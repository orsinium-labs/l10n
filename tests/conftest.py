from pathlib import Path
import pytest


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    root = tmp_path / 'project-test'
    root.mkdir()
    (root / 'pyproject.toml').write_text('')
    (root / 'project_test').mkdir()
    (root / 'project_test' / '__init__.py').write_text('')
    return root


@pytest.fixture
def source_path(project_root: Path) -> Path:
    path = (project_root / 'project_test' / 'core.py')
    path.write_text('')
    return path
