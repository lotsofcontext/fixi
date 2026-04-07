---
id: S1-T16
title: Terraform skeleton en fixi/terraform/
sprint: S1
day: 4
status: pending
priority: P1
type: implementation
tags: [terraform, azure, iac, day-4]
created: 2026-04-07T00:00:00
updated: 2026-04-07T00:00:00
estimated: 2h
actual: ""
owner: claude
blocks: [S1-T17]
blocked_by: []
related_docs: [SPRINT-1, BACKLOG, PLAN]
commits: []
files_touched: []
---

# S1-T16: Terraform skeleton para Azure

> **Sprint**: [[SPRINT-1]] · **Día**: 4 · **Status**: pending
> **Owner**: claude · **Estimated**: 2h

## Contexto

Elkin pidió "demo desplegado con infra-as-code". Tarea PLAN 6.3.

**Importante**: el Terraform NO necesita `apply` exitoso. Solo debe ser **legible y `terraform validate` debe pasar**. Es documentation-grade IaC, no operational.

## Acceptance Criteria

- [ ] Carpeta `fixi/terraform/` creada
- [ ] `main.tf` con providers (azurerm, azuread)
- [ ] `variables.tf` con inputs configurables
- [ ] `outputs.tf` con FQDNs y IDs útiles
- [ ] Módulos para: ACI (Container Instance), ACR (Container Registry), managed identity, VNet básico, Key Vault
- [ ] Comentarios explicativos en español/inglés
- [ ] `terraform/README.md` con diagrama y cómo usar
- [ ] `terraform validate` pasa limpio (sin `apply`)
- [ ] Naming convention Azure (CAF — Cloud Adoption Framework)

## Plan

Estructura modular pero simple. No HCL fancy, prioridad legibilidad.

## Notes & Attempts

[Append durante ejecución]

## Outcome

[Llenar al completar]

## History

- `2026-04-07 00:00` · created (status: pending)
