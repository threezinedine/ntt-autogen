SETTING_FILE = "autogen-settings.json"
import os
import json
from typing import Any

from .binding import GenerateBindings
from .template_gen import GenerateTemplate
from .utils import UpdateFileStamp
from .models import Settings
from dataclasses import asdict
from dacite import from_dict


class Autogen:
    """
    Autogen is a complete tools for auto tracking and generating code bindings and templates
        based on C/C++ header files and user-defined settings.

    Arguments
    ---------
        tempFolder: str, optional
            The temporary folder to store intermediate files. Defaults to "temp".
            The folder is the relative path from the `baseDir` if `baseDir` is provided
            or the current working directory otherwise.

        baseDir: str, optional
            The base directory for resolving relative paths. Defaults to None. If None,
            the current working directory is used.
    """

    def __init__(
        self,
        tempFolder: str = "temp",
        baseDir: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._baseDir = baseDir if baseDir else os.getcwd()
        self._tempFolder = tempFolder

        # create setting files if not exist
        settingFile = os.path.join(self._baseDir, SETTING_FILE)

        if not os.path.exists(settingFile):
            settings = Settings()
            with open(settingFile, "w", encoding="utf-8") as f:
                json.dump(asdict(settings), f, indent=4)

        assert os.path.exists(
            settingFile
        ), f'Setting file "{SETTING_FILE}" does not exist.'

        dependencies: set[str] = set()
        with open(settingFile, "r", encoding="utf-8") as f:
            settings = from_dict(data_class=Settings, data=json.load(f))

        for template in settings.templates:
            _, deps = GenerateTemplate(
                template,
                self._baseDir,
                tempFolder=self._tempFolder,
                **kwargs,
            )
            for dep in deps:
                dependencies.add(dep)

        for binding in settings.bindings:
            _, deps = GenerateBindings(
                binding,
                self._baseDir,
                tempFolder=self._tempFolder,
                systemData=kwargs,
            )
            for dep in deps:
                dependencies.add(dep)

        for dependency in dependencies:
            UpdateFileStamp(dependency, self._baseDir, self._tempFolder)
