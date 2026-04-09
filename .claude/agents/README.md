# GlobalMVM Simulation Agents

> **Que es esto**: un equipo de 8 agentes subagent de Claude Code que simulan al equipo tecnico de GlobalMVM basandose en comportamiento observado en la reunion real del 2026-04-06.
>
> **Fuente del corpus**: transcripcion de la reunion (speaker diarization via NotebookLM) guardada en `Z:\consultoria-x\clientes\globalmvm\TRANSCRIPT-REUNION-2026-04-06.md`. Cada agente tiene quotes textuales del transcript.

---

## Los 8 agentes

| Slug | Persona | Rol | Status en reunion 2026-04-06 |
|------|---------|-----|------------------------------|
| `globalmvm-elkin-ceo` | Elkin "Kin" Medina | CEO / Sponsor | Asistio (llego tarde) |
| `globalmvm-joaris-architect` | Joaris Angulo Quiroz | Arquitecto / Champion Fixi | Organizo la reunion |
| `globalmvm-jefferson-hyperautomation` | Jefferson Acevedo | Lider Hiperautomatizacion | **Dio el prompt original** |
| `globalmvm-liset-data-ai` | Liset (Liseth Campo Arcos) | Lider Datos+IA / Centro de Aceleracion | Asistio |
| `globalmvm-john-bairo-architect` | John Bairo Gomez | Arquitecto / Scale+Adopcion | Asistio |
| `globalmvm-jenny-product-owner` | Jenny Pedraza | PO Energy Suite (15y) | Asistio, hablo poco |
| `globalmvm-victor-operations` | Victor Orrego | Dir Operaciones | **NO asistio — origino el caso** |
| `globalmvm-carlos-regression-prevention` | Carlos Caicedo | Dev Senior / Regression Prevention | **NO asistio — mencionado por Liset** |

Los ultimos dos (Victor y Carlos) son **personalidades parciales** — se construyen con lo que otros dijeron sobre ellos. Sus simulaciones son mas incompletas y deben actualizarse cuando hayan interacciones reales.

---

## 4 casos de uso

### 1. Pre-pitch dry-run (paralelo)
Antes de entregar un deliverable al cliente, lanzar los 8 agentes en paralelo para que cada uno critique desde su angulo. Se consolidan hallazgos y se corrigen antes de la entrega real.

```python
# Ejemplo de invocacion conceptual (via Task tool)
Task(subagent_type="globalmvm-joaris-architect",
     prompt="Revisa Fixi PoC. Califica el nivel de IA (1-4)...")
Task(subagent_type="globalmvm-jefferson-hyperautomation",
     prompt="Audita Fixi contra tu prompt original...")
# ...los 8 en la misma llamada, sin esperar
```

Output del dry-run del Sprint 3: [`docs/planning/dry-run-report.md`](../../docs/planning/dry-run-report.md).

### 2. Generacion de FAQ defensivo
Cada agente da las 10 preguntas mas dificiles que haria. Se consolida ~80 preguntas → deduplicar → top 20 por dificultad → armar respuestas defensivas.

```python
Task(subagent_type="globalmvm-john-bairo-architect",
     prompt="Dame las 10 preguntas mas dificiles que harias sobre Fixi. Ordenalas por dificultad.")
```

Output del Sprint 3: [`docs/planning/faq-defensivo.md`](../../docs/planning/faq-defensivo.md).

### 3. Roleplay de objeciones (interactivo)
Saul practica respuestas contra un agente en conversacion turn-by-turn.

```python
Task(subagent_type="globalmvm-jefferson-hyperautomation",
     prompt="Roleplay: Saul te acaba de mostrar Fixi en vivo. Reacciona como en la reunion real — una pregunta a la vez, espera mi respuesta antes de la siguiente.")
```

### 4. Anticipacion de dinamica politica
Simular como un agente reaccionaria a un escenario con el resto del equipo.

```python
Task(subagent_type="globalmvm-elkin-ceo",
     prompt="Escenario: Joaris dijo 'estamos alineados', Jefferson pidio mas minimalismo, John Bairo pregunto por matriz de decision. Como cerrarias la decision tu como CEO?")
```

---

## Reglas de uso

### NUNCA
- **NUNCA** usar estos agentes para generar comunicaciones directas al cliente ("Jefferson dijo que..."). Solo para dry-runs y validacion interna.
- **NUNCA** dejar que un agente invente quotes que no esten en su perfil. Cada perfil tiene quotes textuales del transcript — son su ancla.
- **NUNCA** tratarlos como verdad absoluta sobre las personas reales. Son simulaciones desde **una** reunion.

### SIEMPRE
- Actualizar el perfil correspondiente despues de cada interaccion real con GlobalMVM. Nuevas frases, nuevos temas, correcciones al perfil → commit al repo.
- Cuando se usen para dry-run, consolidar hallazgos en `docs/planning/` (no dejar outputs como scratch).
- Correr los 8 en paralelo siempre que sea posible — son independientes.

---

## Advertencias

1. **No son las personas reales**. Son aproximaciones basadas en UNA reunion. Pueden fallar en temas que no estaban en ese contexto.
2. **Victor y Carlos** tienen personalidad parcial (no asistieron). Calificar su output como "opinion inferida".
3. **Menos blockchain, mas AI practica**. Feedback clave de la reunion: el tono debe ser AI consulting, no web3 consulting. Cuando un agente roleplay se vaya a blockchain sin necesidad, marcarlo como ruido.

---

## Archivos fuente en consultoria-x (lecturas obligatorias antes de editar)

| Archivo | Contenido |
|---------|-----------|
| `Z:\consultoria-x\clientes\globalmvm\TRANSCRIPT-REUNION-2026-04-06.md` | Transcript completo con speaker diarization |
| `Z:\consultoria-x\clientes\globalmvm\AGENTS-GLOBALMVM-TEAM.md` | Version extendida de los perfiles con mas contexto |
| `Z:\consultoria-x\clientes\globalmvm\HANDOFF-FIX-ISSUE-AGENT.md` | Handoff original post-reunion |
| `Z:\consultoria-x\clientes\globalmvm\HANDOFF-FIXI-SPRINT3-SIMULATION-AGENTS.md` | Handoff de este Sprint 3 (la fuente de este README) |

---

*Sprint 3 — 2026-04-08*
