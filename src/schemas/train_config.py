from __future__ import annotations

from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

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

    @model_validator(mode="after")
    def _require_params_for_agent(self) -> Self:
        if self.agent_type == "q_learning" and self.q_params is None:
            msg = "q_params must be provided for q_learning"
            raise ValueError(msg)
        if self.epsilon_params is None:
            msg = "epsilon_params must be provided"
            raise ValueError(msg)
        return self
