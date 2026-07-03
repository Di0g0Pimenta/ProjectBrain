from projectbrain.core.config import settings


def test_settings_loaded() -> None:
    assert settings.app_name == "ProjectBrain"