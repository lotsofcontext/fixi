# HANDOFF: Fixi — Continuar Desarrollo

## Contexto
Fixi es un agente autonomo de resolucion de issues que fue presentado como proof of concept a GlobalMVM (software house de 30 anos, 300+ devs, Medellin, sector energia, 99% Azure).

En la reunion del 6 de abril 2026, el equipo gerencial de GlobalMVM pidio explicitamente este agente. El prompt exacto vino de Jefferson Acevedo (lider de hiperautomatizacion):

> "Actua como un agente de automatizacion de desarrollo de software encargado de gestionar tickets y requerimientos. Debes conectarte a fuentes de conocimiento disponibles como repositorios de codigo, sistemas de tickets y documentacion tecnica para analizar cada solicitud. Clasifica y prioriza el ticket segun su tipo (bug, mejora, nueva funcionalidad), valida el codigo fuente existente relacionado, propone y aplica ajustes siguiendo buenas practicas de desarrollo y estandares definidos, crea automaticamente una nueva rama con una nomenclatura adecuada, realiza los cambios necesarios en el codigo, ejecuta validaciones basicas, genera el commit con un mensaje claro y estructurado, y deja creado el Pull Request listo para aprobacion incluyendo descripcion tecnica, cambios realizados y posibles impactos. No debes inventar informacion, si faltan datos debes indicarlo claramente y detener el flujo."

## Que ya existe en este repo

- `skill/SKILL.md` — Workflow de 10 pasos (518 lineas)
- `skill/references/classification.md` — Taxonomia de 7 tipos de issues
- `skill/references/guardrails.md` — 13 reglas de seguridad
- `docs/PLAN.md` — Roadmap de 5 fases, 36 tareas
- `docs/SPEC.md` — Especificacion tecnica completa (2,356 lineas)

## Que hay que hacer AHORA (deliverable para GlobalMVM)

### Prioridad 1: Demo funcional end-to-end
Elkin (CEO) pidio: "demo desplegado con infra-as-code en un repositorio que ellos puedan analizar".

1. Crear un repo de ejemplo con bugs intencionales (2-3 issues pre-creados)
2. Ejecutar Fixi contra esos issues y grabar/documentar el resultado
3. El flujo completo debe ser visible: issue → branch → fix → tests → PR

### Prioridad 2: Diagramas Mermaid
Joaris (champion tecnico) pidio diagramas que su equipo pueda VER y PROBAR:
- Flujo principal (issue → PR)
- Arbol de clasificacion
- Niveles de autonomia (GUIDED / CONFIRM_PLAN / FULL_AUTO)
- Flujo de tracking (triple-write)

### Prioridad 3: Documento client-facing
Un README o doc que GlobalMVM pueda circular internamente:
- Lenguaje de negocio, no jerga interna
- ROI: "cuanto tiempo ahorra por ticket"
- Seguridad: "nunca inventa info, siempre branch, siempre PR para revision humana"
- Stack agnostic: funciona con .NET, Java, Python, Angular

### Prioridad 4: Adaptacion Azure DevOps
GlobalMVM es 99% Azure. Necesitan:
- Parsers para Azure DevOps Work Items (no solo GitHub Issues)
- Branch naming compatible con Azure Repos
- PR creation via `az repos pr create` (no solo `gh pr create`)
- CI/CD: Azure Pipelines triggers

## Lo que GlobalMVM QUIERE VER (critico)

- Flujo end-to-end DEMOSTRABLE, no solo documentos
- Que se pueda ejecutar y ver la operacion
- Que sea AGNOSTICO al proyecto y tecnologia
- Que no afecte codigo previo (rama espejo, PR para validacion humana)
- Conectores a diferentes fuentes (Azure DevOps, S3, blob storage, DBs)

## Compromisos de Saul con GlobalMVM

1. Enviar demo desplegado con infra-as-code en un repositorio que ellos puedan analizar
2. Incluir diagramas (Mermaid), especificaciones, todo documentado
3. Ellos envian "el chicharron" — caso de uso concreto mas detallado
4. Reunion de aclaracion despues de la entrega

## Personas clave en GlobalMVM

- **Joaris Angulo** — Champion tecnico, quiere "ingenieria y confiabilidad", quiere monetizar la solucion para multiples clientes
- **Jefferson Acevedo** — Hiperautomatizacion, dio el prompt, quiere PoC minimalista, comparo con Power Platform
- **Liset** — Datos+AI, transversal, conoce deuda tecnica
- **John Bairo Gomez** — Arquitectura, preocupado por adopcion y resistencia de devs
- **Elkin Medina** — CEO, quiere acelerar entregas

## Para empezar en esta sesion

1. Lee CLAUDE.md para las reglas del proyecto
2. Lee skill/SKILL.md para entender el workflow actual
3. Empieza por los diagramas Mermaid (Prioridad 2) — son rapidos y dan contexto visual
4. Luego crea el repo de demo (Prioridad 1) con issues de ejemplo
