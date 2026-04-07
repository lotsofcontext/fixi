# Sprint 1 — Critical Path al Demo GlobalMVM

> **Objetivo**: Repo cloneable que GlobalMVM pueda analizar, ejecutar, y verificar end-to-end.
> **Duración estimada**: 5 días focalizados
> **Deliverable**: 2 repos públicos en `lotsofcontext` — [[fixi]] + `fixi-demo-dotnet`
>
> Ver también: [[PLAN|Roadmap completo]], [[BACKLOG|Backlog priorizado]], [[HANDOFF-FROM-HQ|Contexto GlobalMVM]]

---

## Definition of Done

El sprint está completo cuando Joaris puede:
1. `git clone https://github.com/lotsofcontext/fixi-demo-dotnet`
2. `dotnet restore && dotnet build && dotnet test` → observar 4+ tests rojos
3. Leer `docs/CLIENT-FACING.md` en fixi
4. Click-through a `docs/demos/run-01-github.md` y `run-02-ado.md`
5. Ver PRs reales en GitHub/Azure DevOps
6. Leer los módulos `terraform/` con comentarios
7. Volver con preguntas técnicas concretas

---

## Día 1 — Fundamentos y skeleton del demo

**Meta**: skill refs verificados + fixi-demo-dotnet compilando con 3 bugs sembrados + tests fallando.

| # | Tarea | Duración | Resultado |
|---|-------|----------|-----------|
| S1.1 | Auditar `skill/references/classification.md` y `guardrails.md` | 15 min | Confirmado completos (ya lo están, solo verificar) |
| S1.2 | Auditar wiki links — convertir client-facing a formato estándar | 30 min | `diagrams.md` y `CLIENT-FACING.md` renderizan bien en GitHub |
| S1.3 | Crear repo `lotsofcontext/fixi-demo-dotnet` en GitHub | 10 min | Repo público existe |
| S1.4 | Inicializar solution `GMVM.EnergyTracker` con 3 projects | 45 min | `dotnet build` limpio |
| S1.5 | `CalculadoraConsumo.cs` con BUG #1 (DivideByZero `.Days`) | 30 min | Compila, bug sembrado |
| S1.6 | `MedidorService.cs` con PERF #2 (N+1 loop) | 45 min | Compila, query en loop |
| S1.7 | `AdminController.cs` con SECURITY #3 (sin `[Authorize]`) | 20 min | Compila, endpoints abiertos |
| S1.8 | Tests failing para los 3 bugs | 1.5 h | `dotnet test` → 4+ rojos predecibles |

**Punto de control Día 1**: `fixi-demo-dotnet` pusheado con commit inicial. Tests fallan deterministicamente.

---

## Día 2 — Tooling del demo y primer rehearsal

**Meta**: Work items creados + CLAUDE.md + README + primer run de Fixi documentado.

| # | Tarea | Duración | Resultado |
|---|-------|----------|-----------|
| S1.9 | 3 work items markdown en `docs/issues/` | 1 h | WI-101, WI-102, WI-103 formato ADO export |
| S1.10 | `CLAUDE.md` del demo repo (convenciones .NET) | 30 min | Fixi puede leerlo en Paso 0 |
| S1.11 | `README.md` + `README.es.md` del demo repo | 45 min | Walkthrough bilingüe |
| S1.12 | Rehearsal contra WI-101 → `docs/demos/run-01-github.md` | 1.5 h | Transcript completo + PR real creado en GitHub |

**Punto de control Día 2**: 1 PR merged en `fixi-demo-dotnet` via Fixi. Test del bug ahora pasa. Transcript commiteado.

---

## Día 3 — Azure DevOps path

**Meta**: Fixi habla Azure DevOps. Parser + PR creation funcionando.

| # | Tarea | Duración | Resultado |
|---|-------|----------|-----------|
| S1.13 | Agregar Paso 1 handler de ADO URLs al SKILL.md | 45 min | Pattern + comando `az boards work-item show` documentado |
| S1.14 | Agregar Paso 8 rama ADO al SKILL.md | 45 min | `az repos pr create` como alternativa a `gh pr create` |
| — | Configurar ADO sandbox (proyecto throwaway) | 1 h | Org + project + PAT listos |
| — | Mirror `fixi-demo-dotnet` a Azure Repos | 30 min | Código en ambos lados |
| — | Crear WI-102 y WI-103 en ADO (real, no solo markdown) | 30 min | Work items reales para parsear |

**Punto de control Día 3**: Fixi puede leer un work item real de ADO y crear un PR en Azure Repos.

---

## Día 4 — Rehearsal ADO + Terraform

**Meta**: Segundo run documentado + IaC legible.

| # | Tarea | Duración | Resultado |
|---|-------|----------|-----------|
| S1.15 | Rehearsal contra WI-102 y WI-103 → `docs/demos/run-02-ado.md` | 2 h | Transcripts + PRs en Azure Repos |
| S1.16 | Terraform skeleton en `fixi/terraform/` | 2 h | ACI, ACR, managed identity, networking. `terraform validate` limpio |
| — | `terraform/README.md` con diagrama | 30 min | Explicación legible |

**Punto de control Día 4**: `terraform validate` pasa. Dos rehearsals completos documentados.

---

## Día 5 — Polish y ship

**Meta**: Todo conectado, demo shippable.

| # | Tarea | Duración | Resultado |
|---|-------|----------|-----------|
| S1.17 | Polish `CLIENT-FACING.md` con links a runs + Terraform | 1 h | Doc final listo para circular |
| — | Verificar todos los links cross-doc | 30 min | Zero enlaces rotos |
| — | README de fixi apunta a fixi-demo-dotnet | 15 min | Discoverable |
| — | Actualizar descripción GitHub de ambos repos | 15 min | Topics, description |
| — | Final push master a ambos repos | 15 min | Shipped |
| — | Enviar mensaje a Joaris con los links | 15 min | Entregado |

**Punto de control Día 5 (SHIP)**: Mensaje enviado a Joaris con:
- `https://github.com/lotsofcontext/fixi`
- `https://github.com/lotsofcontext/fixi-demo-dotnet`
- Invitación a revisar y volver con preguntas.

---

## Dependencias y blockers conocidos

| Blocker | Owner | Mitigación |
|---------|-------|------------|
| `gh auth login` necesita cuenta de lotsofcontext para editar descripciones | Saul | Login adicional en gh CLI o edit manual vía web |
| ADO sandbox (org + PAT) para Día 3 | Saul | Crear org throwaway gratis |
| `.NET 8 SDK` instalado | Saul | Verificar con `dotnet --version` antes del Día 1 |
| `az` CLI con extensión `azure-devops` | Saul | `az extension add --name azure-devops` |

---

## Riesgos del Sprint

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|------------|
| Test de query counting EF Core resulta flaky | Media | Fallback a `Stopwatch`-based latency assertion |
| Rehearsal de Fixi produce transcripts inconsistentes | Alta | Commitear el primer run bueno, no perseguir perfección |
| ADO sandbox auth bloquea Día 3 | Media | Pedir a GlobalMVM proyecto sandbox si necesario |
| Terraform modules no pasan `validate` por typo | Baja | `terraform validate` es rápido, iterar |
| Wiki links audit revela más archivos de los esperados | Baja | Grep rápido al principio, priorizar client-facing |

---

## Post-sprint (qué sigue)

Al cerrar Sprint 1 con ship exitoso:
1. Esperar respuesta de Joaris (24-72h típicamente)
2. Reunión de aclaración con preguntas técnicas
3. GlobalMVM envía "el chicharrón" — caso de uso concreto
4. Iniciar [[SPRINT-2]] — confidence building y CONFIRM_PLAN mode

Ver [[BACKLOG]] sección "Sprint 2" para el detalle.
