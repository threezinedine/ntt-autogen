import os
import shutil


def GetStampFilePath(
    filePath: str,
    baseDir: str,
) -> str:
    """
    Get the path to the stamp file for a given file.

    Args:
        filePath (str): The path to the original file (relative to the base directory).
        baseDir (str): The base directory for resolving relative paths.

    Returns:
        str: The path to the corresponding stamp file.
    """

    return os.path.join(baseDir, "autogen", "temp", f"{filePath}.stamp")


def IsFileModified(filePath: str, baseDir: str) -> bool:
    """
    Check if a file has been modified based on its cache.

    Args:
        filePath (str): The path to the file to check (relative to the base directory).
        baseDir (str): The base directory for resolving relative paths.

    Returns:
        bool: True if the file has been modified, False otherwise.
    """

    fullFilePath = os.path.join(baseDir, filePath)
    stampFilePath = GetStampFilePath(filePath, baseDir)

    if not os.path.exists(fullFilePath):
        raise FileNotFoundError(f"File '{fullFilePath}' does not exist.")

    if not os.path.exists(stampFilePath):
        return True

    if os.path.getmtime(fullFilePath) > os.path.getmtime(stampFilePath):
        return True

    return False


def UpdateFileStamp(filePath: str, baseDir: str) -> None:
    """
    Update the stamp file for a given file to reflect its current modification time.

    Args:
        filePath (str): The path to the original file (relative to the base directory).
        baseDir (str): The base directory for resolving relative paths.
    """

    stampFilePath = GetStampFilePath(filePath, baseDir)

    os.makedirs(os.path.dirname(stampFilePath), exist_ok=True)
    with open(stampFilePath, "w") as file:
        file.write("")


def ClearCache(baseDir: str) -> None:
    """
    Clear all cached stamp files.

    Args:
        baseDir (str): The base directory for resolving relative paths.
    """

    tempDir = os.path.join(baseDir, "autogen", "temp")
    shutil.rmtree(tempDir, ignore_errors=True)
