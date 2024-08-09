import adb_utils
import dir_utils


if __name__ == "__main__":
    files = adb_utils.get_files_to_copy()
    dir_utils.backup_files(files)
