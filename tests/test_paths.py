from src.paths import PROJECT_ROOT, PROMPTS_DIR


def test_project_root_contains_pyproject():
    assert (PROJECT_ROOT / "pyproject.toml").exists()


def test_prompts_dir_contains_system():
    assert (PROMPTS_DIR / "system" / "attacker.md").exists()


def test_prompts_dir_contains_channels():
    assert (PROMPTS_DIR / "channels" / "email.md").exists()
