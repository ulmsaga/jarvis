"""Git Clone → 워크트리 격리 관리"""
import shutil
import subprocess
import tempfile
from pathlib import Path
from src.config import settings


def _full_repo(repo: str) -> str:
    return repo if "/" in repo else f"{settings.github_owner}/{repo}"


def clone(repo: str, branch: str = "main") -> Path:
    """GitHub 레포를 격리된 임시 디렉토리에 클론한다."""
    full = _full_repo(repo)
    token = settings.github_token
    clone_url = f"https://{token}@github.com/{full}.git"

    tmp = Path(tempfile.mkdtemp(prefix="jarvis_wt_"))
    subprocess.run(
        ["git", "clone", "--depth=1", "-b", branch, clone_url, str(tmp)],
        check=True,
        capture_output=True,
        text=True,
    )
    return tmp


def cleanup(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
