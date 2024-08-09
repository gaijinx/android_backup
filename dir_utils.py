import hashlib
import os
from typing import Iterable
import adb_utils
from itertools import compress
from tqdm import tqdm
from multiprocessing import Pool

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DIRECTORIES_TO_COPY = [
    "Bluetooth",
    "DCIM",
    "Documents",
    "Download",
    "Movies",
    "Music",
    "Pictures",
    "Recordings",
]
BACKUP_DIR = os.path.join(CURRENT_DIR, "backup")


def get_extensions(file_list: Iterable[str]):
    return {os.path.splitext(file)[1].lower() for file in file_list}


def is_local_file_different(remote_filepath: str):
    local_filepath = get_local_filepath_from_remote(remote_filepath)
    if os.path.exists(local_filepath):
        return md5_local(local_filepath) != md5_remote(remote_filepath)
    return True


def get_local_filepath_from_remote(remote_filepath: str) -> str:
    destination_path = os.path.normpath(
        os.path.join(BACKUP_DIR, remote_filepath.replace("/sdcard/", "", 1))
    )
    return destination_path


def md5_local(file_path: str) -> str:
    # Calculate the MD5 hash of a local file.
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def md5_remote(file_path: str) -> str:
    # Calculate the MD5 hash of a remote file.
    return adb_utils.get_file_md5(file_path)


def backup_file(filepath: str):
    destination_path = get_local_filepath_from_remote(filepath)
    os.makedirs(os.path.abspath(os.path.dirname(destination_path)), exist_ok=True)
    adb_utils.pull_file(filepath, destination_path)


def get_files_to_backup(workers=10) -> Iterable[str]:
    remote_files = adb_utils.get_files_to_copy()
    with Pool(workers) as p:
        files_to_pull_mask = list(tqdm(p.imap(is_local_file_different, remote_files), total=len(remote_files), desc="Comparing files", unit="files"))
    return list(compress(remote_files, files_to_pull_mask))


def backup_files(file_list: Iterable[str], workers=10):
    with Pool(workers) as p:
        list(tqdm(p.imap(backup_file, file_list), total=len(file_list), desc="Copying files", unit="files"))
