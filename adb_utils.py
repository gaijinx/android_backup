import os
import subprocess
from typing import Iterable
import zipfile

import requests

from dir_utils import CURRENT_DIR, DIRECTORIES_TO_COPY

ADB_PATH = os.path.join(CURRENT_DIR, "platform-tools", "adb.exe")


def download_adb():
    print("Downloading adb")
    platform_tools = requests.get(
        "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    )
    zip_file_path = os.path.join(CURRENT_DIR, "platform-tools-latest-windows.zip")
    print("Unzipping")
    with open(zip_file_path, "wb") as f:
        f.write(platform_tools.content)
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(CURRENT_DIR)
    os.remove(zip_file_path)


def call_adb(command: Iterable[str]):
    try:
        output = subprocess.check_output([ADB_PATH] + command, stderr=subprocess.PIPE)
    except Exception as e:
        output = e.output
    output = output.decode("utf-8")
    return output


def list_devices():
    return call_adb(["devices"])


def get_files_to_copy():
    files = []
    for directory in DIRECTORIES_TO_COPY:
        dir_files = call_adb(["shell", "find", f"/sdcard/{directory}", "-type f"])
        dir_files = [i for i in dir_files.split("\r\n") if i]
        files.extend(dir_files)
        print(f"Directory: {directory}, files: {len(dir_files)}")
        print(dir_files[:10])
    return files


def pull_file(filepath: str, destination: str):
    call_adb(["pull", filepath, destination])


def get_file_md5(file_path: str) -> str:
    return call_adb(["shell", "md5sum", f'"{file_path}"']).split()[0]
