"""Tests for fixi_agent.prompts — system prompt loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from fixi_agent.prompts import (
    _apply_autonomous_transforms,
    estimate_tokens,
    load_system_prompt,
)

# Resolve the repo root (agent/tests/unit/ → repo root)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SKILL_DIR = REPO_ROOT / "skill"


class TestLoadSystemPrompt:
    """Integration tests for the full loader."""

    def test_loads_successfully(self) -> None:
        prompt = load_system_prompt(skill_dir=SKILL_DIR)
        assert len(prompt) > 1000
        assert isinstance(prompt, str)

    def test_has_autonomous_preamble(self) -> None:
        prompt = load_system_prompt(skill_dir=SKILL_DIR)
        assert "Autonomous Agent Mode" in prompt

    def test_has_classification_annex(self) -> None:
        prompt = load_system_prompt(skill_dir=SKILL_DIR)
        assert "Anexo: Clasificacion de Issues" in prompt

    def test_has_guardrails_annex(self) -> None:
        prompt = load_system_prompt(skill_dir=SKILL_DIR)
        assert "Anexo: Guardrails de Seguridad" in prompt

    def test_no_esperar_confirmacion(self) -> None:
        """Approval gates must be stripped for autonomous mode."""
        prompt = load_system_prompt(skill_dir=SKILL_DIR)
        assert "Esperar confirmacion del usuario" not in prompt

    def test_paso_0_pre_validated(self) -> None:
        """Paso 0 pwd check must be replaced with pre-validated no-op."""
        prompt = load_system_prompt(skill_dir=SKILL_DIR)
        assert "Contexto Pre-validado" in prompt

    def test_full_auto_default(self) -> None:
        """Default autonomy must be FULL_AUTO, not GUIDED."""
        prompt = load_system_prompt(skill_dir=SKILL_DIR)
        assert "FULL_AUTO** (modo autonomo)" in prompt

    def test_has_gap_a_validaciones_basicas(self) -> None:
        """Gap A: Paso 7 must be 'Ejecutar Validaciones Basicas'."""
        prompt = load_system_prompt(skill_dir=SKILL_DIR)
        assert "Ejecutar Validaciones Basicas" in prompt

    def test_has_gap_b_pr_sections(self) -> None:
        """Gap B: PR template must have the 3 named sections from Cap 8."""
        prompt = load_system_prompt(skill_dir=SKILL_DIR)
        assert "## Descripcion tecnica" in prompt
        assert "## Cambios realizados" in prompt
        assert "## Posibles impactos" in prompt

    def test_has_validaciones_ejecutadas(self) -> None:
        """PR template must have a Validaciones ejecutadas section."""
        prompt = load_system_prompt(skill_dir=SKILL_DIR)
        assert "## Validaciones ejecutadas" in prompt

    def test_has_pre_existentes_disclaimer(self) -> None:
        """PR template must include pre-existentes disclaimer."""
        prompt = load_system_prompt(skill_dir=SKILL_DIR)
        assert "pre-existentes" in prompt

    def test_no_yaml_frontmatter(self) -> None:
        """YAML frontmatter must be stripped."""
        prompt = load_system_prompt(skill_dir=SKILL_DIR)
        assert not prompt.startswith("---\n")

    def test_token_estimate_reasonable(self) -> None:
        """Total system prompt should be under 15K tokens."""
        prompt = load_system_prompt(skill_dir=SKILL_DIR)
        tokens = estimate_tokens(prompt)
        assert tokens < 15_000, f"Prompt too large: {tokens} tokens"
        assert tokens > 1_000, f"Prompt too small: {tokens} tokens"


class TestTrackingModes:
    """Tests for the tracking_mode parameter."""

    def test_mode_none_skips_paso_9(self) -> None:
        prompt = load_system_prompt(skill_dir=SKILL_DIR, tracking_mode="none")
        assert "tracking_mode=none" in prompt
        assert "tasks.json" not in prompt

    def test_mode_client_skips_mission_control(self) -> None:
        prompt = load_system_prompt(skill_dir=SKILL_DIR, tracking_mode="client")
        assert "tracking_mode=client" in prompt
        assert "ACTIVO.md" in prompt

    def test_mode_hq_has_full_triple_write(self) -> None:
        prompt = load_system_prompt(skill_dir=SKILL_DIR, tracking_mode="hq")
        assert "ACTIVO.md" in prompt
        assert "tasks.json" in prompt
        assert "activity-log.json" in prompt

    def test_invalid_mode_raises(self) -> None:
        with pytest.raises(ValueError, match="tracking_mode must be"):
            load_system_prompt(skill_dir=SKILL_DIR, tracking_mode="invalid")


class TestErrorHandling:
    """Tests for missing files and bad inputs."""

    def test_missing_skill_dir_raises(self) -> None:
        with pytest.raises(FileNotFoundError, match="Required file not found"):
            load_system_prompt(skill_dir=Path("/nonexistent/path"))

    def test_missing_skill_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="SKILL.md"):
            load_system_prompt(skill_dir=tmp_path)


class TestTransformations:
    """Unit tests for individual transforms."""

    SAMPLE_SKILL = """\
---
name: fix-issue
description: test
---

# Fix Issue

**Autonomia default: GUIDED** (aprobacion en cada paso).

## Paso 0: Verificacion de Contexto (SAFETY GATE)

Verificar pwd.
Esperar confirmacion del usuario.

## Paso 1: Parsear

Content.
Esperar confirmacion del usuario antes de continuar.

## Paso 3: Autonomia

El usuario puede cambiar nivel en cualquier momento: "sigue en auto".

## Paso 9: Tracking (TRIPLE-WRITE)

### A. ACTIVO.md

Write activo.

### B. Mission Control

Write tasks.json, activity-log.json, inbox.json.

### C. Output final

Done.

## Paso 10: Cleanup
"""

    def test_strips_frontmatter(self) -> None:
        result = _apply_autonomous_transforms(self.SAMPLE_SKILL, "client")
        assert "---\nname: fix-issue" not in result

    def test_replaces_paso_0(self) -> None:
        result = _apply_autonomous_transforms(self.SAMPLE_SKILL, "client")
        assert "Contexto Pre-validado" in result
        assert "Verificar pwd" not in result

    def test_strips_esperar_confirmacion(self) -> None:
        result = _apply_autonomous_transforms(self.SAMPLE_SKILL, "client")
        assert "Esperar confirmacion del usuario" not in result
        assert "Proceder inmediatamente" in result

    def test_replaces_autonomy_narrative(self) -> None:
        result = _apply_autonomous_transforms(self.SAMPLE_SKILL, "client")
        assert "El usuario puede cambiar nivel" not in result
        assert "FULL_AUTO" in result

    def test_inverts_default_to_full_auto(self) -> None:
        result = _apply_autonomous_transforms(self.SAMPLE_SKILL, "client")
        assert "FULL_AUTO** (modo autonomo)" in result

    def test_tracking_none_strips_paso_9(self) -> None:
        result = _apply_autonomous_transforms(self.SAMPLE_SKILL, "none")
        assert "TRIPLE-WRITE" not in result
        assert "tracking_mode=none" in result

    def test_tracking_client_skips_mission_control(self) -> None:
        result = _apply_autonomous_transforms(self.SAMPLE_SKILL, "client")
        assert "ACTIVO.md" in result
        assert "Omitido" in result
        assert "tracking_mode=client" in result

    def test_tracking_hq_preserves_everything(self) -> None:
        result = _apply_autonomous_transforms(self.SAMPLE_SKILL, "hq")
        assert "ACTIVO.md" in result
        assert "Mission Control" in result
        assert "tasks.json" in result


class TestEstimateTokens:
    def test_basic_estimate(self) -> None:
        assert estimate_tokens("Hello world! This is a test.") == 7  # 28 chars / 4

    def test_empty_string(self) -> None:
        assert estimate_tokens("") == 0
