from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml

from logging_config import get_logger
from schemas.train_config import EvaluationConfig, TrainingConfig

logger = get_logger(__name__)


def _load_and_validate_yaml(path: str) -> dict[str, Any]:
    """Load and validate YAML configuration file.

    Args:
        path: Path to YAML configuration file.

    Returns:
        Raw configuration dictionary.

    Raises:
        FileNotFoundError: If configuration file doesn't exist.
        TypeError: If configuration file doesn't contain a mapping.
    """
    logger.info("Loading config from path: %s", path)
    p = Path(path)
    if not p.exists():
        msg = f"Config file not found: {path}"
        logger.error(msg)
        raise FileNotFoundError(msg)
    with p.open("r", encoding="utf-8") as f:
        raw_obj = yaml.safe_load(f)
    if not isinstance(raw_obj, dict):
        msg = "Config file must contain a mapping at the top level"
        logger.error(msg)
        raise TypeError(msg)
    return cast("dict[str, Any]", raw_obj)


def load_agent_config(path: str) -> TrainingConfig:
    """Load agent configuration from a YAML file using Pydantic validation."""
    raw = _load_and_validate_yaml(path)
    model = TrainingConfig.model_validate(raw)
    return model


def get_evaluation_params(config: TrainingConfig) -> EvaluationConfig:
    """Return normalized evaluation parameters with sensible defaults.

    Args:
        config: Loaded training config with optional `evaluation` section.

    Returns:
        A tuple (matches, target_points, seed, output_dir).
    """
    eval_raw = config.evaluation
    if eval_raw is None:
        msg = "Evaluation config is required"
        logger.error(msg)
        raise ValueError(msg)

    return eval_raw
