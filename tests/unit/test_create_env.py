import os
from pathlib import Path
from venv import create
from unittest.mock import patch
import os
from pathlib import Path

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, "../"))

from scripts.create_env import create_env, create_env_if_not_already_created


# Checks that an existing env file is detected
def test_create_env_file_already_there(monkeypatch, capfd):
    # Arrange
    monkeypatch.setattr(Path, "exists", lambda _: True)
    env_file = ".env"

    # Act
    create_env_if_not_already_created(env_file=env_file)

    out, err = capfd.readouterr()
    # Assert
    assert out == f"{env_file} already exists!\n"
    assert err == ""


# Checks that the function determining whether an env file exists works correctly
def test_create_env_file_not_yet_created(monkeypatch, mocker, capfd):
    # Arrange
    monkeypatch.setattr(Path, "exists", lambda _: False)
    create_env = mocker.patch("scripts.create_env.create_env", autospec=True)
    env_file = ".env"

    # Act
    create_env_if_not_already_created(env_file=env_file)

    # Assert
    create_env.assert_called_once_with(Path(env_file))

    out, err = capfd.readouterr()
    assert out == ""
    assert err == ""


# Checks that the function to create an env file works correctly
def test_create_env(monkeypatch, capfd):
    # Arrange
    monkeypatch.setattr(Path, "write_text", lambda _, x: True)
    monkeypatch.setattr(Path, "chmod", lambda _, x: True)
    env_file = ".env"

    # Act
    create_env(env_file=Path(env_file))

    out, err = capfd.readouterr()
    # Assert
    assert out == f"Created {env_file}\n"
    assert err == ""
