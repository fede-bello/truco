from unittest.mock import MagicMock, patch

import pytest

from schemas.train_config import EvaluationConfig, TrainingConfig
from utils.config_loader import _load_and_validate_yaml, get_evaluation_params, load_agent_config


@patch("utils.config_loader.Path.exists")
@patch("utils.config_loader.Path.open")
@patch("utils.config_loader.yaml.safe_load")
def test_load_and_validate_yaml_success(mock_yaml_load, mock_open, mock_exists):
    mock_exists.return_value = True
    mock_yaml_load.return_value = {"key": "value"}

    result = _load_and_validate_yaml("dummy.yaml")
    assert result == {"key": "value"}


@patch("utils.config_loader.Path.exists")
def test_load_and_validate_yaml_not_found(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        _load_and_validate_yaml("missing.yaml")


@patch("utils.config_loader.Path.exists")
@patch("utils.config_loader.Path.open")
@patch("utils.config_loader.yaml.safe_load")
def test_load_and_validate_yaml_not_dict(mock_yaml_load, mock_open, mock_exists):
    mock_exists.return_value = True
    mock_yaml_load.return_value = ["not", "a", "dict"]

    with pytest.raises(TypeError, match="Config file must contain a mapping"):
        _load_and_validate_yaml("invalid.yaml")


@patch("utils.config_loader._load_and_validate_yaml")
def test_load_agent_config(mock_load_yaml):
    raw_config = {
        "episodes": 100,
        "seed": 42,
        "agent_type": "q_learning",
        "out": "models/",
        "q_params": {"alpha": 0.1, "gamma": 0.9},
    }
    mock_load_yaml.return_value = raw_config

    config = load_agent_config("dummy.yaml")
    assert isinstance(config, TrainingConfig)
    assert config.episodes == 100
    assert config.agent_type == "q_learning"


def test_get_evaluation_params_success():
    eval_config = EvaluationConfig(matches=100)
    config = MagicMock(spec=TrainingConfig)
    config.evaluation = eval_config

    result = get_evaluation_params(config)
    assert result == eval_config


def test_get_evaluation_params_missing():
    config = MagicMock(spec=TrainingConfig)
    config.evaluation = None

    with pytest.raises(ValueError, match="Evaluation config is required"):
        get_evaluation_params(config)
