# Terraform Infrastructure Audit Report -- Fixi

**Fecha:** 2026-04-10  
**Proyecto:** Fixi -- Autonomous Issue Resolution Agent  
**Cliente:** GlobalMVM (sector energetico colombiano)  
**Metodologia:** 5 agentes expertos en paralelo (PM, HR, Azure Architect AZ-305/500/400, Terraform Expert HashiCorp Certified, DevOps/Security Engineer AZ-400/500)

---

## Resumen Ejecutivo

La infraestructura Terraform de Fixi presenta un nivel de calidad en el codigo HCL que los cinco expertos calificaron independientemente como "senior/staff-level" -- algo poco comun en auditorias de este tipo. El naming sigue rigurosamente el Cloud Adoption Framework de Azure, la modularizacion esta bien delimitada, los comentarios explican el "por que" detras de cada decision (no solo el "que"), y el modelo de identidad con User-Assigned Managed Identity (UAMI) y least-privilege scoping es la decision arquitectural correcta. ACI como plataforma de computo es la eleccion adecuada para un agente de largo ciclo tipo worker-queue.

Sin embargo, la auditoria identifico **3 hallazgos tipo BLOCKER** que impiden que `terraform apply` complete exitosamente en un entorno limpio, **9 hallazgos CRITICAL** que bloquean cualquier despliegue en produccion, y multiples gaps de seguridad y compliance que deben cerrarse antes de operar con datos reales de GlobalMVM. Adicionalmente, se detecto un desacople entre las variables declaradas en el modulo `container_instance` y las que el modulo root le pasa, lo que constituye un error de validacion que Terraform deberia atrapar en `plan`.

La estimacion consolidada de los cinco expertos es de **3 a 4 semanas** para llevar esta infraestructura de "demo funcional" a "produccion-ready" con un equipo de 2 ingenieros dedicados mas un consultor de redes por 60 horas.

---

## Hallazgos Consolidados

### BLOCKERS (3) -- El apply no funciona

Estos hallazgos impiden que `terraform plan` o `terraform apply` completen exitosamente en un entorno nuevo (sin state previo). Son la maxima prioridad.

| ID | Hallazgo | Archivo | Consenso |
|----|----------|---------|----------|
| BLK-01 | **Data source chicken-and-egg:** `data "azurerm_key_vault"` en el modulo `container_instance` intenta leer un Key Vault por nombre durante plan-time, pero ese KV todavia no existe en el primer apply. Los data sources se evaluan en la fase `plan`, no en la fase `apply`, por lo que Terraform aborta con un error "Key Vault not found". La solucion es pasar el `key_vault_id` como variable del modulo (que ya esta declarada en `variables.tf` pero no se usa) en vez de derivarlo via regex del URI del secret. | `modules/container_instance/main.tf:70-73` | 5/5 expertos |
| BLK-02 | **URIs EXAMPLE en tfvars:** los archivos `dev.tfvars` y `prod.tfvars` contienen URIs con el literal `EXAMPLE` (ej: `kv-fixi-dev-EXAMPLE`). La regex en la linea 67 del modulo ACI extrae ese nombre y lo pasa al data source, que busca un vault llamado `kv-fixi-dev-EXAMPLE` -- un recurso que no existe ni existira (el nombre real tiene un sufijo aleatorio generado por `random_string`). Este hallazgo se acopla con BLK-01: incluso si se resuelve el chicken-and-egg, los URIs de ejemplo garantizan el fallo. | `environments/dev.tfvars:39-41`, `environments/prod.tfvars:40-42` | 4/5 expertos |
| BLK-03 | **RBAC propagation delay:** Azure RBAC tarda entre 5 y 15 minutos en propagarse completamente. El modulo `key_vault` usa `depends_on` entre el role assignment de Secrets Officer y los secrets placeholder, lo cual garantiza orden de ejecucion pero NO garantiza propagacion. En la practica, los primeros `azurerm_key_vault_secret` fallan con HTTP 403 "Caller is not authorized" de forma intermitente -- a veces pasan, a veces no, dependiendo de la velocidad de propagacion de Azure AD en ese momento. | `modules/key_vault/main.tf:94-122` | 3/5 expertos |

**Hallazgo adicional relacionado con Blockers:** El modulo `container_instance` declara tres variables (`key_vault_id`, `managed_identity_client_id`, `environment`) en su `variables.tf` (lineas 52-65) que el root `main.tf` nunca pasa en el bloque `module "container_instance"`. Simultaneamente, el root module pasa `anthropic_api_key_secret_id`, `ado_pat_secret_id`, y `github_pat_secret_id` que no estan declaradas en el `variables.tf` del modulo hijo. Esto deberia causar errores de validacion en `terraform validate`.

---

### CRITICAL (9) -- Bloquean produccion

Estos hallazgos no impiden que el `apply` complete (asumiendo blockers resueltos), pero representan riesgos inaceptables para un entorno de produccion con datos reales.

| ID | Hallazgo | Archivo | Consenso |
|----|----------|---------|----------|
| CRT-01 | **Backend remoto COMENTADO:** el bloque `backend "azurerm"` en `versions.tf:44-65` esta intencional y explicitamente comentado. Esto significa que el state de Terraform se almacena localmente en `terraform.tfstate` -- sin encryption at rest, sin locking (dos operadores pueden hacer `apply` simultaneamente y corromper el state), y sin versionamiento (no hay rollback si un apply destruye recursos). Para un cliente del sector energetico con requisitos de compliance, esto es inaceptable. | `versions.tf:44-65` | 5/5 |
| CRT-02 | **Secrets en state plaintext:** los data sources `azurerm_key_vault_secret` en el modulo `container_instance` (lineas 39-52) leen los valores reales de los secrets del Key Vault. Terraform almacena estos valores en el state file sin encryption. Cualquiera con acceso al archivo `terraform.tfstate` local obtiene las API keys de Anthropic, el PAT de Azure DevOps, y el PAT de GitHub en texto plano. | `modules/container_instance/main.tf:39-52` | 4/5 |
| CRT-03 | **Key Vault con acceso publico:** `public_network_access_enabled = true` y `network_acls.default_action = "Allow"` significan que el Key Vault es accesible desde cualquier IP en internet. Si un atacante obtiene un token de Azure AD con `Key Vault Secrets User` scope (ej: via un service principal comprometido), puede leer todos los secrets del vault remotamente. La mitigacion es `default_action = "Deny"` con private endpoint y/o IP rules. | `modules/key_vault/main.tf:46-51` | 5/5 |
| CRT-04 | **ACR con acceso publico:** el Container Registry usa SKU Basic sin private endpoints. Basic SKU no soporta private endpoints -- es una limitacion de Azure. Esto significa que cualquiera con credenciales AcrPull puede hacer pull de la imagen de Fixi desde cualquier red. Para produccion, se requiere SKU Premium con private endpoint dentro del VNet. | `modules/container_registry/main.tf:24` | 4/5 |
| CRT-05 | **Zero pipeline CI/CD:** no existe ningun archivo `azure-pipelines.yml`, `.github/workflows/*.yml`, ni ningun otro mecanismo de integracion continua o despliegue continuo. Esto significa que los deploys se hacen manualmente desde laptops de desarrolladores, sin audit trail, sin revisiones de pares, y sin separacion de deberes. | N/A | 5/5 |
| CRT-06 | **Zero alertas y monitoring:** el workspace de Log Analytics recibe logs del container, pero no hay `azurerm_monitor_metric_alert`, `azurerm_monitor_action_group`, ni dashboards configurados. Si Fixi se cae, se queda sin memoria, o entra en un restart loop, nadie se entera hasta que un usuario reporta que el agente no responde. | N/A | 5/5 |
| CRT-07 | **Zero tests de infraestructura:** no existen archivos `.tftest.hcl` (native TF tests desde v1.6), ni tests de Terratest, ni integracion con Checkov, tflint, o tfsec. No hay forma automatizada de verificar que un cambio en la configuracion no rompe algo. | N/A | 4/5 |
| CRT-08 | **Egress sin control:** el NSG depende de la regla por defecto `AllowInternetOutBound` (priority 65001) para todo el trafico saliente. Esto esta documentado en los comentarios del modulo de networking (lineas 55-66) como una decision consciente, pero sigue siendo un riesgo: si la imagen de Fixi es comprometida, puede exfiltrar datos a cualquier destino en internet sin restriccion. La mitigacion es un Azure Firewall o egress NSG rules con Service Tags. | `modules/networking/main.tf:55-66` | 4/5 |
| CRT-09 | **Secrets con "REPLACE_ME" inyectados al container:** el modulo `key_vault` crea placeholders con el valor literal `"REPLACE_ME"` (linea 98). Si un operador ejecuta `terraform apply` sin haber sobrescrito estos secrets out-of-band, el modulo `container_instance` lee `"REPLACE_ME"` como si fuera el API key real y lo inyecta como `ANTHROPIC_API_KEY`. Fixi arranca, intenta llamar a la API de Anthropic con `"REPLACE_ME"`, recibe un 401, y entra en restart loop perpetuo por la politica `OnFailure`. | `modules/key_vault/main.tf:98` + `modules/container_instance/main.tf:148-152` | 3/5 |

---

### HIGH (8)

Hallazgos que no bloquean el deploy pero generan problemas operacionales significativos.

| ID | Hallazgo | Archivo | Consenso |
|----|----------|---------|----------|
| HGH-01 | **`timestamp()` en tags causa drift permanente:** `locals.tf:57` usa `formatdate("YYYY-MM-DD", timestamp())` en el tag `last_applied`. La funcion `timestamp()` retorna un valor diferente en cada ejecucion de `terraform plan`, lo que genera un diff en TODOS los recursos con tags en cada plan -- incluso cuando no hay cambios reales. Esto contamina el output de `plan`, dificulta code review, y en equipos grandes genera "alert fatigue" donde los operadores ignoran los diffs porque siempre hay ruido. | `locals.tf:57` | 5/5 |
| HGH-02 | **Sin liveness ni readiness probes:** el bloque `container` (lineas 123-153) no define health checks. ACI soporta liveness y readiness probes via HTTP, TCP, o exec. Sin ellos, un container que este corriendo pero en estado zombie (proceso vivo pero sin procesar trabajo) nunca sera reiniciado automaticamente. | `modules/container_instance/main.tf:123-153` | 4/5 |
| HGH-03 | **Terraform Secrets Officer "temporal" que es permanente:** el comentario en la linea 70 dice "Temporary Terraform grant", pero `azurerm_role_assignment.terraform_secrets_officer` es un recurso gestionado por Terraform. Si alguien lo elimina manualmente, el siguiente `apply` lo recrea. Es decir, la intencion documentada ("revocar despues del primer apply") contradice la realidad del state: Terraform lo mantiene indefinidamente. | `modules/key_vault/main.tf:65-71` | 4/5 |
| HGH-04 | **Sin pre-commit hooks para IaC:** no hay configuracion de pre-commit (`.pre-commit-config.yaml`) con hooks para `terraform fmt`, `terraform validate`, `tflint`, o `tfsec`/`trivy`. Esto permite que codigo HCL mal formateado, con errores de validacion, o con vulnerabilidades conocidas llegue al repositorio sin deteccion. | N/A | 3/5 |
| HGH-05 | **`depends_on` excesivo en container_instance:** el bloque `depends_on` en `main.tf:233-239` lista cinco dependencias explicitas. Terraform ya infiere la mayoria de estas dependencias de las referencias a outputs de modulos. El `depends_on` explicito a nivel de modulo tiene un efecto colateral no obvio: desactiva el paralelismo de Terraform para TODO el modulo (no solo el recurso), forzando evaluacion secuencial de todos los data sources y recursos dentro de el. | `main.tf:233-239` | 2/5 |
| HGH-06 | **Sin plan de Disaster Recovery:** toda la infraestructura esta en una sola region (`eastus2`), sin replicacion, sin backup del state, sin runbooks de recuperacion. Si la region sufre un outage (evento raro pero documentado en Azure), Fixi queda completamente offline sin procedimiento de failover. | N/A | 3/5 |
| HGH-07 | **Sin Microsoft Defender for Cloud:** no hay habilitacion de Defender for Cloud para los recursos desplegados. Defender provee deteccion de amenazas, evaluacion de vulnerabilidades, y recomendaciones de seguridad especificas para Key Vault, ACR, y networking. Para un cliente del sector energetico con estrictos requisitos de compliance, esto deberia estar habilitado. | N/A | 2/5 |
| HGH-08 | **No usa check blocks ni terraform test:** Terraform 1.5 introdujo `check` blocks para invariantes post-apply y Terraform 1.6 introdujo `terraform test` con archivos `.tftest.hcl`. Dado que el proyecto ya requiere `>= 1.6.0`, estas features estan disponibles pero no se aprovechan. | N/A | 2/5 |

---

### MEDIUM (9)

Hallazgos que representan riesgo moderado o deuda tecnica que deberia resolverse antes de escalar.

| ID | Hallazgo | Archivo | Consenso |
|----|----------|---------|----------|
| MED-01 | **Secret URIs expuestas como environment_variables no-secure:** las lineas 142-145 del modulo ACI pasan los URIs de los secrets (`ANTHROPIC_API_KEY_SECRET`, `ADO_PAT_SECRET`, `GITHUB_PAT_SECRET`) como variables de entorno normales (no `secure_environment_variables`). Aunque los URIs no son los valores de los secrets, si revelan los nombres del vault y de los secrets -- informacion util para un atacante que ya tenga acceso parcial al entorno de Azure. | `modules/container_instance/main.tf:142-145` | 4/5 |
| MED-02 | **`AZURE_CLIENT_ID = ""` como placeholder peligroso:** la linea 141 pone un string vacio como `AZURE_CLIENT_ID`. ACI con UAMI no inyecta automaticamente el client ID; la aplicacion debe usar `DefaultAzureCredential` con el client ID explicito para seleccionar la identidad correcta. Un string vacio puede causar que `DefaultAzureCredential` intente la cadena completa (environment -> managed identity -> CLI) y falle de formas inesperadas. El root module deberia pasar `module.managed_identity.client_id` aqui (la variable `managed_identity_client_id` ya esta declarada en el modulo pero no se usa). | `modules/container_instance/main.tf:141` | 4/5 |
| MED-03 | **Log Analytics workspace_key en transito y en state:** `main.tf:229` pasa `primary_shared_key` del workspace al modulo ACI. Esta shared key es un secret (permite escribir logs al workspace desde cualquier lugar) y queda almacenada en el state de Terraform en texto plano. La mitigacion seria usar autenticacion basada en identidad para diagnostics cuando ACI lo soporte. | `main.tf:229` | 3/5 |
| MED-04 | **Faltan validaciones en variables criticas:** `location`, `vnet_address_space`, `aci_subnet_prefix`, y `container_image` no tienen bloques de `validation`. Un typo en `location` (ej: `eastus22`) no se detecta hasta el apply, y un CIDR invalido en `aci_subnet_prefix` puede causar errores confusos de Azure. | `variables.tf` | 2/5 |
| MED-05 | **Sin proceso de secret rotation documentado:** no hay runbook, script, ni documentacion sobre como rotar los secrets del Key Vault. La nota en `key_vault/main.tf` dice "overwrite via `az keyvault secret set`" pero no menciona que despues hay que hacer `terraform apply` para que ACI recoja el nuevo valor (porque los data sources cachean el valor hasta el proximo apply). | N/A | 4/5 |
| MED-06 | **Doble bloque `locals` en el modulo container_instance:** las lineas 65-68 y 75-77 definen dos bloques `locals` separados. Terraform lo permite sintacticamente, pero es confuso para mantenimiento y puede causar errores de merge. Se recomienda consolidar en un solo bloque. | `modules/container_instance/main.tf:65-77` | 1/5 |
| MED-07 | **Sin `staging.tfvars`:** la variable `environment` acepta `"staging"` como valor valido (validacion en `variables.tf:34`), pero no existe ningun archivo `environments/staging.tfvars`. Esto sugiere un environment fantasma: la validacion lo permite pero no hay configuracion preparada para usarlo. | N/A | 2/5 |
| MED-08 | **ACR Basic sin geo-replicacion ni content trust:** el SKU Basic es apropiado para el MVP pero no soporta geo-replicacion (necesaria para DR) ni Docker Content Trust (necesario para validar la integridad de las imagenes). | N/A | 2/5 |
| MED-09 | **Data sources de KV secrets dentro del modulo ACI acoplan al formato de URI:** el modulo container_instance parsea internamente el URI del secret (via regex) para extraer el nombre del vault y luego busca el vault y los secrets por nombre. Esto acopla fuertemente el modulo al formato de URI de Azure Public Cloud y falla silenciosamente con Azure Government (`vault.usgovcloudapi.net`) o Azure China (`vault.azure.cn`). Ademas, el root module ya tiene acceso al `key_vault_id` via el output del modulo `key_vault` -- la indirecion via URI es innecesaria. | `modules/container_instance/main.tf:39-52, 65-77` | 2/5 |

---

### LOW (12)

Hallazgos menores que representan deuda tecnica o mejoras de calidad. No bloquean nada pero deberian resolverse eventualmente.

| ID | Hallazgo | Archivo | Consenso |
|----|----------|---------|----------|
| LOW-01 | **Provider `azuread` declarado pero nunca usado:** `versions.tf:33-36` declara el provider `azuread ~> 2.50` pero ningun recurso ni data source lo referencia. Terraform lo descarga en `init` y lo incluye en el lock file innecesariamente. | `versions.tf:33-36` | 4/5 |
| LOW-02 | **Variable `location_short` declarada pero nunca referenciada:** `variables.tf:44-48` declara `location_short` con default `"eus2"` pero no aparece en `locals.tf` ni en ningun otro archivo. Es codigo muerto. | `variables.tf:44-48` | 2/5 |
| LOW-03 | **Sin `azurerm_management_lock` en recursos criticos:** el resource group y el Key Vault no tienen locks `CanNotDelete`. Un `terraform destroy` accidental (o un operador con permisos excesivos) puede eliminar todo el entorno de produccion sin confirmacion adicional. | `main.tf:72-77` | 3/5 |
| LOW-04 | **Nombres de recursos al borde del limite:** el Key Vault usa `substr(..., 0, 24)` para respetar el limite de 24 caracteres de Azure. Esto funciona, pero si el sufijo aleatorio genera nombres que colisionan con vaults eliminados (soft-deleted), el apply falla con un error opaco. | `locals.tf:39` | 1/5 |
| LOW-05 | **Regex fragil para parsear vault name de URI:** la regex `https://([^.]+)\\.vault\\.azure\\.net` en la linea 67 del modulo ACI asume Azure Public Cloud. Falla con Azure Government (`.vault.usgovcloudapi.net`), Azure China (`.vault.azure.cn`), y Azure Germany (legacy). | `modules/container_instance/main.tf:67` | 2/5 |
| LOW-06 | **`FIXI_ENV` usa `aci_name` en vez de environment flag:** la linea 139 setea `FIXI_ENV = var.aci_name`, lo que produce valores como `aci-fixi-dev-eastus2` en vez de simplemente `dev`. Si la aplicacion usa `FIXI_ENV` para feature flags o branching logico, el valor complejo puede causar comparaciones inesperadas. La variable `environment` ya esta declarada en el modulo pero no se pasa desde el root. | `modules/container_instance/main.tf:139` | 1/5 |
| LOW-07 | **Secrets duplicados: URIs en env_vars y valores en secure_env_vars:** el container recibe tanto el URI del secret (en `environment_variables`, lineas 142-144) como el valor real del secret (en `secure_environment_variables`, lineas 148-151). Dependiendo de como Fixi lea su configuracion, podria ignorar los valores reales y intentar fetch via SDK usando los URIs -- o viceversa. Esta ambiguedad deberia resolverse eligiendo una estrategia unica. | `modules/container_instance/main.tf:138-152` | 2/5 |
| LOW-08 | **Sin `versions.tf` en modulos hijos:** ningun modulo hijo (`container_instance`, `container_registry`, `key_vault`, `managed_identity`, `networking`) tiene su propio `versions.tf` con `required_providers`. Esto funciona porque heredan del root, pero es una mala practica si alguien quiere reusar un modulo de forma independiente o publicarlo en un registry. | N/A | 1/5 |
| LOW-09 | **Lock file solo tiene hashes para una plataforma:** `.terraform.lock.hcl` fue generado en una sola plataforma. Si un operador ejecuta `terraform init` en Linux, macOS, o en un CI runner con arquitectura diferente, los hashes no van a coincidir y Terraform pedira `init -upgrade`, lo que puede cambiar versiones inesperadamente. | `.terraform.lock.hcl` | 1/5 |
| LOW-10 | **Sin `prevent_destroy` lifecycle en ACR:** el Container Registry no tiene `lifecycle { prevent_destroy = true }`. Si un `terraform destroy` o un refactor elimina accidentalmente el modulo ACR, se pierden todas las imagenes almacenadas sin confirmacion adicional. | `modules/container_registry/main.tf` | 1/5 |
| LOW-11 | **Provider azurerm sin `subscription_id` explicito:** `main.tf:38-49` no especifica `subscription_id` en el bloque del provider. Terraform usa la suscripcion del contexto de `az login` o del service principal, lo que funciona bien para un solo desarrollador pero es fragil en equipos: un operador logueado en la suscripcion equivocada despliega en el entorno incorrecto sin advertencia. | `main.tf:38-49` | 1/5 |
| LOW-12 | **`required_version = ">= 1.6.0"` sin limite superior:** esta restriccion permite que Terraform 2.0 (cuando salga) ejecute este codigo, pero las versiones mayores suelen traer breaking changes. Se recomienda `>= 1.6.0, < 2.0.0` para evitar sorpresas. | `versions.tf:25` | 1/5 |

---

## Compliance Gaps

Evaluacion contra estandares relevantes para un cliente del sector energetico colombiano.

| Estandar | Control | Gap | Severidad |
|----------|---------|-----|-----------|
| ISO 27001 | A.13.1.1 Network Controls | Egress completamente abierto. No hay Azure Firewall ni NSG rules de egress. Un container comprometido puede exfiltrar datos a cualquier destino. | CRITICAL |
| ISO 27001 | A.12.4.1 Event Logging | Key Vault no tiene diagnostic settings configurados. No hay registro de quien accede a que secrets ni cuando. | HIGH |
| ISO 27001 | A.9.2.3 Privileged Access Management | El role "Key Vault Secrets Officer" para el Terraform runner es permanente en el state, contradiciendo la intencion documentada de temporalidad. | HIGH |
| SOC2 | CC6.1 Logical Access | No hay pipeline CI/CD con aprobaciones. Los deploys se pueden ejecutar desde cualquier laptop sin revisiones de pares ni audit trail. | CRITICAL |
| SOC2 | CC6.6 External Communication Restrictions | Sin restriccion de trafico saliente. Todos los servicios externos son accesibles desde el container sin filtrado. | HIGH |
| SOC2 | CC7.2 Monitoring of System Components | Log Analytics recibe logs pero no hay alertas, action groups, ni dashboards. Las anomalias no generan notificaciones. | HIGH |
| CIS Azure | 5.1.1 Diagnostic Settings | State local sin encryption ni control de acceso. Secrets en plaintext accesibles a cualquiera con acceso al filesystem del operador. | CRITICAL |
| CIS Azure | 8.5 Key Vault Access | Key Vault con `public_network_access_enabled = true` y `default_action = "Allow"`. Accesible desde cualquier IP. | HIGH |
| CIS Azure | 9.3 Container Registry Access | ACR con acceso publico. SKU Basic no soporta private endpoints. | HIGH |
| Regulacion Colombiana (SIC) | Proteccion de Datos Personales | Si Fixi procesa tickets que contienen datos personales de empleados o clientes de GlobalMVM, los secrets del state local representan un vector de fuga de datos personales sujeto a la Ley 1581 de 2012. | CRITICAL |

---

## Well-Architected Framework Assessment

Evaluacion contra los cinco pilares del Microsoft Azure Well-Architected Framework.

| Pilar | Score | Notas |
|-------|-------|-------|
| **Reliability** | 4/10 | Politica de restart `OnFailure` esta bien, pero no hay health checks (liveness/readiness), no hay Availability Zones, no hay DR plan, no hay management locks en recursos criticos, y un solo container instance sin redundancia significa que cualquier fallo es un outage total. |
| **Security** | 6/10 | Lo positivo: UAMI con least privilege (AcrPull + KV Secrets User scoped), RBAC authorization en Key Vault, admin deshabilitado en ACR, inbound deny-all en NSG, soft-delete con purge protection. Lo negativo: ACR y KV publicos, egress sin control, secrets en state plaintext, Secrets Officer permanente, sin Defender for Cloud. |
| **Cost Optimization** | 8/10 | Sizing diferenciado por entorno (0.5 CPU / 1 GB en dev, 2 CPU / 4 GB en prod), Basic SKU para ACR apropiado en MVP, Log Analytics con retencion minima en dev (30 dias) y extendida en prod (90 dias). ACI es la opcion mas economica para este tipo de workload (vs. AKS o App Service). |
| **Operational Excellence** | 3/10 | Logs se envian a Log Analytics (bien), pero no hay alertas, no hay dashboards, no hay runbooks de operacion, no hay CI/CD, no hay tests de infraestructura, no hay pre-commit hooks, y `timestamp()` en tags genera ruido en cada plan. La documentacion inline en HCL es excelente, pero no compensa la falta de automatizacion operacional. |
| **Performance Efficiency** | 7/10 | ACI es la opcion correcta para un worker que procesa una cola. El sizing es razonable. No hay overprovisioning evidente. El unico gap es la ausencia de metricas de performance (CPU/memory usage) con alertas de threshold para detectar cuando escalar. |

**Score ponderado global: 5.6/10** -- Aceptable para demo, insuficiente para produccion.

---

## Recomendaciones de Contratacion (HR)

Basado en los hallazgos de la auditoria y el timeline estimado de remediacion, los expertos recomiendan los siguientes perfiles de contratacion.

### Perfiles requeridos

| Perfil | Prioridad | Costo estimado/mes USD | Justificacion |
|--------|-----------|------------------------|---------------|
| **Senior Cloud Security Engineer** (AZ-500, SC-100) | P0 -- contratacion inmediata | ~$5,500 | Responsable de cerrar CRT-03, CRT-04, CRT-08, HGH-03, HGH-07, y todos los gaps de compliance. Configura private endpoints, Azure Firewall o NSG egress rules, Defender for Cloud, y diagnostic settings en Key Vault. Establece el baseline de seguridad para produccion. |
| **DevOps Engineer -- IaC & CI/CD** (AZ-400, Terraform Associate) | P1 -- esta semana | ~$3,500 | Responsable de CRT-01, CRT-05, CRT-06, CRT-07, HGH-01, HGH-04, HGH-08. Configura backend remoto con Azure Storage, pipeline de CI/CD con plan/apply automatizados, alertas con action groups, tests con `.tftest.hcl` o Terratest, y pre-commit hooks con tflint + tfsec. |
| **Azure Network Engineer -- consultor 60h** (AZ-700) | P2 -- este mes | ~$4,800 pago unico | Responsable de disenar e implementar la topologia de red de produccion: Azure Firewall con egress filtering por FQDN, private endpoints para KV y ACR, DNS private zones, validacion de CIDRs para peering futuro con redes on-prem de GlobalMVM, y documentacion de la arquitectura de red. |

### Perfiles que NO necesitamos

| Perfil | Razon |
|--------|-------|
| Azure Solutions Architect | La arquitectura general ya es correcta. UAMI, ACI, modularizacion -- todo esta bien disenado. No necesitamos a alguien que redisene desde cero. |
| Terraform Expert dedicado | La calidad del HCL ya esta en el percentil 90+. Los hallazgos son de configuracion y operaciones, no de calidad de codigo. |
| DBA / Data Engineer | No hay base de datos en esta arquitectura. Fixi interactua con APIs externas (Azure DevOps, GitHub, Anthropic). |
| Kubernetes Engineer | ACI es la eleccion correcta para este workload. Migrar a AKS introduciria complejidad innecesaria para un agente single-container. |

### Presupuesto

| Concepto | Monto |
|----------|-------|
| Primer mes (incluye consultor de redes) | ~$13,800 USD |
| Recurrente mensual (Security + DevOps) | ~$9,000 USD |
| Costo total estimado hasta produccion-ready (4 semanas) | ~$13,800 USD |

---

## Timeline Estimado

Plan de remediacion de 4 semanas asumiendo los perfiles recomendados ya contratados.

| Semana | Foco | Items | Responsable |
|--------|------|-------|-------------|
| **Semana 1** | Blockers + Backend remoto | BLK-01 (refactorizar data sources a variables directas), BLK-02 (eliminar URIs EXAMPLE, documentar proceso de bootstrap), BLK-03 (agregar `time_sleep` o provisioner de validacion post-RBAC), CRT-01 (habilitar backend remoto con Azure Storage), HGH-01 (reemplazar `timestamp()` con variable de CI/CD) | DevOps Engineer |
| **Semana 2** | Seguridad + CI/CD | CRT-03 (KV private endpoint + `default_action = "Deny"`), CRT-04 (ACR Premium + private endpoint), CRT-05 (pipeline CI/CD con plan/apply/approval gates), CRT-08 (Azure Firewall o NSG egress rules), HGH-03 (lifecycle block o flag para Secrets Officer), HGH-04 (pre-commit hooks: fmt, validate, tflint, tfsec) | Security Engineer + DevOps |
| **Semana 3** | Monitoring + Testing | CRT-06 (metric alerts + action groups para CPU, memory, restart count), CRT-07 (`.tftest.hcl` para cada modulo + Checkov scan en CI), HGH-02 (liveness/readiness probes HTTP o TCP), HGH-08 (check blocks para invariantes post-apply) | DevOps Engineer |
| **Semana 4** | Hardening + DR | HGH-06 (plan de DR con replicacion de state y runbook de failover a otra region), HGH-07 (Defender for Cloud), MEDs (validaciones de variables, secret rotation runbook, staging.tfvars, consolidar locals), LOWs (limpiar provider azuread, variable location_short, agregar locks y prevent_destroy, fijar version constraint) | Security + Network Consultant |

**Nota:** las semanas 1 y 2 son criticas. Sin resolver los blockers y el backend remoto, no tiene sentido avanzar con el resto. El trabajo de redes (Semana 2-4) puede ejecutarse en paralelo con el de monitoring y testing (Semana 3).

---

## Reconocimiento Positivo

Los 5 expertos coincidieron independientemente en los siguientes puntos positivos. Es importante documentarlos porque representan decisiones de diseno que deben preservarse durante la remediacion.

1. **Calidad del HCL nivel senior/staff.** La estructura, el formato, y la legibilidad del codigo estan por encima de lo que se ve en la mayoria de proyectos de infraestructura. No hay recursos sueltos, no hay bloques desordenados, no hay "TODOs" abandonados sin contexto.

2. **Comentarios inline excepcionales.** Cada bloque de codigo tiene un comentario que explica el "por que" de la decision, no solo el "que" hace. Ejemplos: la explicacion de por que `admin_enabled = false` en ACR, por que UAMI en vez de system-assigned, por que `purge_protection_enabled = true` no se puede desactivar. Esto reduce drasticamente el bus-factor del proyecto.

3. **Naming sigue CAF correctamente.** Los nombres de recursos usan las abreviaciones oficiales del Cloud Adoption Framework (`rg-`, `vnet-`, `snet-`, `nsg-`, `aci-`, `log-`, `id-`, `kv-`, `acr`). Esto facilita la navegacion en el portal de Azure y la correlacion con alertas.

4. **Modelo de identidad correcto.** User-Assigned Managed Identity con scoping de least privilege (AcrPull solo en el ACR, KV Secrets User solo en el vault) es exactamente lo que recomienda Microsoft. La decision de usar UAMI en vez de SAMI evita el chicken-and-egg de RBAC y permite que la identidad sobreviva a rebuilds del container.

5. **ACI es la eleccion arquitectural correcta.** Para un agente single-container que procesa una cola, ACI es mas simple, mas barato, y mas facil de operar que AKS, App Service, o Azure Functions (Durable). No hay overengineering.

6. **Modularizacion permite evolucion sin reescribir.** Cada componente (networking, ACR, KV, MI, ACI) esta en su propio modulo con inputs/outputs bien definidos. Agregar un segundo container, cambiar de ACI a AKS, o agregar un Application Gateway se puede hacer sin tocar los modulos existentes.

7. **No hay overengineering.** No hay modules anidados tres niveles, no hay workspaces innecesarios, no hay abstracciones que no justifiquen su complejidad. El codigo es directo y honesto sobre lo que hace.

---

## Veredicto Final

**Para demo/MVP: APROBADO con reservas.**

El codigo es lo suficientemente solido para una demostracion controlada donde el operador resuelva manualmente los 3 blockers (usar variables directas en vez de data sources, reemplazar URIs EXAMPLE con valores reales post-bootstrap, y manejar el delay de RBAC). En un entorno de demo, los riesgos de seguridad (KV publico, egress abierto, state local) son aceptables porque no hay datos reales en juego.

**Para produccion GlobalMVM: REQUIERE 3-4 semanas de remediacion.**

La infraestructura es un esqueleto excelente -- bien comentado, bien estructurado, bien nombrado -- que necesita las capas que separan "demo que funciona" de "produccion que cumple con los estandares de un cliente del sector energetico colombiano": backend remoto con encryption y locking, pipeline CI/CD con approval gates, alertas y dashboards operacionales, private endpoints para KV y ACR, egress filtering, Defender for Cloud, tests automatizados, y procesos documentados de secret rotation y disaster recovery.

La buena noticia es que la base es solida. No hay que reescribir nada. Hay que agregar las capas de seguridad, operaciones, y compliance encima de una arquitectura que ya esta correcta.

---

*Documento generado como parte del Sprint de auditoria de infraestructura del proyecto Fixi.*  
*Los hallazgos representan el consenso de 5 agentes expertos evaluando independientemente el mismo codebase.*
