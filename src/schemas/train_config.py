from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

AGENT_TYPES = Literal["mc_first_visit", "q_learning"]


class QParams(BaseModel):
    """Pydantic model for Q-learning hyperparameters."""

    alpha: float
    gamma: float


class EpsilonParams(BaseModel):
    """Pydantic model for epsilon schedule parameters."""

    epsilon_start: float
    epsilon_min: float
    epsilon_decay: float


class EvaluationConfig(BaseModel):
    """Pydantic model for evaluation parameters with sensible defaults."""

    matches: int = Field(default=200)
    target_points: int = Field(default=40)
    seed: int = Field(default=123)
    output_dir: str | None = Field(default=None)


class TrainingConfig(BaseModel):
    """Pydantic model for full training configuration."""

    episodes: int
    seed: int
    out: str
    agent_type: AGENT_TYPES
    q_params: QParams | None = None
    epsilon_params: EpsilonParams | None = None
    evaluation: EvaluationConfig | None = None
