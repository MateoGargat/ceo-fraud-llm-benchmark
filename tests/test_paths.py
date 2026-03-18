from src.paths import PROJECT_ROOT, PROMPTS_DIR
from importlib import resources
from pathlib import Path
from src.paths import resolve_prompts_dir


def test_project_root_contains_pyproject():
    assert (PROJECT_ROOT / "pyproject.toml").exists()


def test_prompts_dir_contains_system():
    assert (PROMPTS_DIR / "system" / "attacker.md").exists()


def test_prompts_dir_contains_channels():
    assert (PROMPTS_DIR / "channels" / "email.md").exists()


def test_prompts_dir_resolves_from_package_resources():
    expected = Path(__file__).resolve().parent.parent / "src" / "prompts"
    assert PROMPTS_DIR == expected
    assert resolve_prompts_dir() == expected
    assert resources.files("src").joinpath("prompts/system/attacker.md").is_file()
