"""Build and Falcon-sign the prediction application."""

from hashlib import sha256
import pickle
from pathlib import Path
import shutil
import subprocess
import sys
from falcon_python import Falcon512


def combine_pmos(
    pmos: dict[str, bytes],
    app_directory: str | Path | None = None,
) -> dict[str, Path]:
    """Bundle PMOs, build the Windows app, and sign its executable.

    The signature is made over the executable's SHA-256 digest. A new Falcon
    key pair is generated for each build. The public verification key and
    detached signature are written alongside the executable.
    """
    if not pmos:
        raise ValueError("At least one PMO is required")

    verification_key, signing_private_key = Falcon512.generate_keypair()

    app_path = (
        Path(app_directory)
        if app_directory is not None
        else Path(__file__).resolve().parent / "app"
    )
    app_path.mkdir(parents=True, exist_ok=True)
    bundle_path = app_path / "models.pkl"
    bundle_path.write_bytes(pickle.dumps(pmos, protocol=pickle.HIGHEST_PROTOCOL))

    executable_path = _build_executable(app_path, bundle_path)
    digest = sha256(executable_path.read_bytes()).digest()
    signature = Falcon512.detached_sign(signing_private_key, digest)

    hash_path = executable_path.with_suffix(".sha256")
    signature_path = executable_path.with_suffix(".sig")
    verification_path = executable_path.with_suffix(".pub")
    hash_path.write_text(digest.hex().upper() + "\n", encoding="ascii")
    signature_path.write_bytes(signature)
    verification_path.write_bytes(verification_key)

    return {
        "bundle": bundle_path,
        "executable": executable_path,
        "hash": hash_path,
        "signature": signature_path,
        "verification_key": verification_path,
    }


def _build_executable(app_path: Path, bundle_path: Path) -> Path:
    app_source = app_path / "app.py"
    if not app_source.is_file():
        raise FileNotFoundError(f"Application source not found: {app_source}")

    dist_path = app_path / "dist"
    work_path = app_path / "build"
    spec_path = app_path / "StockPredictor.spec"
    shutil.rmtree(dist_path, ignore_errors=True)
    shutil.rmtree(work_path, ignore_errors=True)
    spec_path.unlink(missing_ok=True)

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        "StockPredictor",
        "--distpath",
        str(dist_path),
        "--workpath",
        str(work_path),
        "--specpath",
        str(app_path),
        "--add-data",
        f"{bundle_path}{';'}.",
        str(app_source),
    ]
    subprocess.run(command, check=True, cwd=app_path)
    executable_path = dist_path / "StockPredictor.exe"
    if not executable_path.is_file():
        raise FileNotFoundError(f"PyInstaller did not create {executable_path}")

    shutil.rmtree(work_path, ignore_errors=True)
    spec_path.unlink(missing_ok=True)
    return executable_path
