"""File utility functions.

Ported from ServiceLib/Common/FileUtils.cs.
"""

from __future__ import annotations

import gzip
import os
import shutil
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path

from v2rayn.common import logging_config

_tag = "FileUtils"


def byte_array_to_file(file_name: str, content: bytes) -> bool:
    """Write bytes to a file.

    Args:
        file_name: Path to the file
        content: Bytes to write

    Returns:
        True on success, False on failure
    """
    try:
        with open(file_name, "wb") as f:
            f.write(content)
        return True
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return False


def decompress_file_from_bytes(file_name: str, content: bytes) -> None:
    """Decompress gzip bytes and write to file.

    Args:
        file_name: Output file path
        content: Gzip compressed bytes
    """
    try:
        decompressed = gzip.decompress(content)
        with open(file_name, "wb") as f:
            f.write(decompressed)
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)


def decompress_file(file_name: str, to_path: str, to_name: str | None = None) -> None:
    """Decompress a gzip file.

    Args:
        file_name: Source gzip file
        to_path: Destination directory
        to_name: Optional output file name
    """
    try:
        output_path = os.path.join(to_path, to_name) if to_name else to_path
        with gzip.open(file_name, "rb") as f_in:
            with open(output_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)


def decompress_tar_file(file_name: str, to_path: str) -> None:
    """Extract a tar.gz file.

    Args:
        file_name: Source tar.gz file
        to_path: Destination directory
    """
    try:
        with tarfile.open(file_name, "r:gz") as tar:
            tar.extractall(path=to_path, filter="data")
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)


def non_exclusive_read_all_text(path: str, encoding: str = "utf-8") -> str:
    """Read all text from a file without exclusive lock.

    Args:
        path: File path
        encoding: Text encoding

    Returns:
        File content as string
    """
    try:
        with open(path, "r", encoding=encoding) as f:
            return f.read()
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        raise


def zip_extract_to_file(file_name: str, to_path: str, ignored_name: str = "") -> bool:
    """Extract files from a zip archive.

    Args:
        file_name: Source zip file
        to_path: Destination directory
        ignored_name: File name pattern to ignore

    Returns:
        True on success, False on failure
    """
    try:
        with zipfile.ZipFile(file_name, "r") as archive:
            for entry in archive.infolist():
                if entry.file_size == 0:
                    continue
                if ignored_name and ignored_name in entry.filename:
                    continue
                # Extract just the filename (not directory structure)
                base_name = os.path.basename(entry.filename)
                if not base_name:
                    continue
                target_path = os.path.join(to_path, base_name)
                with archive.open(entry) as source, open(target_path, "wb") as target:
                    shutil.copyfileobj(source, target)
        return True
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return False


def get_files_from_zip(file_name: str) -> list[str] | None:
    """Get list of file names from a zip archive.

    Args:
        file_name: Source zip file

    Returns:
        List of file names or None
    """
    if not os.path.exists(file_name):
        return None
    try:
        with zipfile.ZipFile(file_name, "r") as archive:
            return archive.namelist()
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return None


def create_from_directory(source_dir: str, dest_file: str) -> bool:
    """Create a zip archive from a directory.

    Args:
        source_dir: Source directory
        dest_file: Destination zip file path

    Returns:
        True on success, False on failure
    """
    try:
        if os.path.exists(dest_file):
            os.remove(dest_file)
        shutil.make_archive(
            dest_file.rsplit(".", 1)[0],
            "zip",
            source_dir,
        )
        return True
    except Exception as ex:
        logging_config.save_log_ex(_tag, ex)
        return False


def copy_directory(
    source_dir: str,
    destination_dir: str,
    recursive: bool = True,
    overwrite: bool = True,
    ignored_name: str | None = None,
) -> None:
    """Copy a directory tree.

    Args:
        source_dir: Source directory path
        destination_dir: Destination directory path
        recursive: Whether to copy subdirectories
        overwrite: Whether to overwrite existing files
        ignored_name: File name pattern to ignore
    """
    src_path = Path(source_dir)
    if not src_path.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    dst_path = Path(destination_dir)
    dst_path.mkdir(parents=True, exist_ok=True)

    for item in src_path.iterdir():
        if item.is_file():
            if ignored_name and ignored_name in item.name:
                continue
            if item.suffix == item.name:
                continue
            target = dst_path / item.name
            if not overwrite and target.exists():
                continue
            shutil.copy2(str(item), str(target))
        elif item.is_dir() and recursive:
            copy_directory(
                str(item),
                str(dst_path / item.name),
                recursive=True,
                overwrite=overwrite,
                ignored_name=ignored_name,
            )


def delete_expired_files(source_dir: str, dt_line: datetime) -> None:
    """Delete files older than the specified date.

    Args:
        source_dir: Directory to clean
        dt_line: Cutoff date
    """
    try:
        for file_path in Path(source_dir).glob("*"):
            if file_path.is_file():
                creation_time = datetime.fromtimestamp(file_path.stat().st_ctime)
                if creation_time < dt_line:
                    file_path.unlink()
    except Exception:
        pass


async def create_linux_shell_file(file_name: str, contents: str, overwrite: bool) -> str:
    """Create a Linux shell script file.

    Args:
        file_name: Shell script file name
        contents: Script contents
        overwrite: Whether to overwrite existing file

    Returns:
        Full path to the created shell file
    """
    from v2rayn.common.utils import get_bin_config_path, set_linux_chmod

    sh_file_path = get_bin_config_path(file_name)

    if not overwrite and os.path.exists(sh_file_path):
        return sh_file_path

    if os.path.exists(sh_file_path):
        os.remove(sh_file_path)

    with open(sh_file_path, "w", encoding="utf-8") as f:
        f.write(contents)

    await set_linux_chmod(sh_file_path)
    return sh_file_path
