"""Tests for stackdiff.config_loader."""

import json
import textwrap
from pathlib import Path

import pytest

from stackdiff.config_loader import (
    ConfigLoadError,
    load_config,
    load_dotenv_file,
    load_json_file,
)


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def test_load_dotenv_basic(tmp_dir):
    env_file = tmp_dir / ".env"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\n# comment\n\nAPP_ENV=staging\n")
    result = load_dotenv_file(env_file)
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "staging"}


def test_load_dotenv_quoted_values(tmp_dir):
    env_file = tmp_dir / ".env"
    env_file.write_text('SECRET="my secret value"\nTOKEN=\'abc123\'\n')
    result = load_dotenv_file(env_file)
    assert result["SECRET"] == "my secret value"
    assert result["TOKEN"] == "abc123"


def test_load_json_file(tmp_dir):
    cfg = {"region": "us-east-1", "replicas": 3}
    json_file = tmp_dir / "config.json"
    json_file.write_text(json.dumps(cfg))
    assert load_json_file(json_file) == cfg


def test_load_config_auto_detect_json(tmp_dir):
    cfg = {"env": "prod"}
    p = tmp_dir / "stack.json"
    p.write_text(json.dumps(cfg))
    assert load_config(p) == cfg


def test_load_config_auto_detect_env(tmp_dir):
    p = tmp_dir / ".env.staging"
    p.write_text("STAGE=staging\n")
    result = load_config(p)
    assert result["STAGE"] == "staging"


def test_load_config_missing_file(tmp_dir):
    with pytest.raises(ConfigLoadError, match="not found"):
        load_config(tmp_dir / "nonexistent.json")


def test_load_config_unsupported_format(tmp_dir):
    p = tmp_dir / "config.toml"
    p.write_text("[section]\nkey = 'value'\n")
    with pytest.raises(ConfigLoadError, match="Unsupported"):
        load_config(p)
