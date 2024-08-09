import requests
import os

import adb_utils


if __name__ == "__main__":
    if not os.path.exists(adb_utils.ADB_PATH):
        adb_utils.download_adb()

    print(adb_utils.list_devices())
