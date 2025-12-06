import os
from typing import Any
from models import Template
from jinja2 import Template as JinjaTemplate
from utils import (
    logger,
    IsFileModified,
    UpdateFileStamp,
    AllDependenciesFiles,
)


def GenerateTemplate(
    template: Template,
    baseDir: str,
    **kwargs: Any,
) -> tuple[str, list[str]]:
    """
    The tools creating the template files.

    Arguments
    ---------
    template : Template
        The template configuration.

    baseDir: str
        The base directory for resolving relative paths. Defaults to None. If None,
        the current working directory is used.

    Keyword Arguments
    -----------------
    kwargs : dict
        Additional data to pass to the template.
    """
    baseDir = baseDir if baseDir else os.getcwd()
    templatePath = os.path.join(baseDir, template.file)

    allDependencies = []

    if template.dependencies is not None:
        assert (
            template.extensions is not None
        ), f'Template "{template.file}" has dependencies but no extensions specified.'

        allDependencies = AllDependenciesFiles(
            template.dependencies,
            template.extensions,
            baseDir,
        )

        logger.debug(
            'All dependency files for binding "{}": \n{}'.format(
                template.file,
                str(allDependencies)
                .replace(", ", ",\n\t")
                .replace("[", "[\n\t")
                .replace("]", "\n]"),
            )
        )

    if not os.path.exists(templatePath):
        logger.warning(f'Template file "{template.file}" does not exist, skipping...')
        return "", []

    outputFiles = [template.file[:-3]]  # remove .in extension

    if template.outputs is not None:
        outputFiles = template.outputs

    fullOutputPaths = [os.path.join(baseDir, outputFile) for outputFile in outputFiles]

    isAnyDependencyModified = False
    for depFile in allDependencies:
        if IsFileModified(depFile):
            isAnyDependencyModified = True
            break

    if (
        not isAnyDependencyModified
        and not IsFileModified(template.file)
        and all(os.path.exists(fullOutputPath) for fullOutputPath in fullOutputPaths)
    ):
        logger.debug(
            f'Template file "{template.file}" has not been modified, skipping...'
        )
        return "", []

    with open(templatePath, "r") as f:
        templateContent = f.read()
        jinjaTemplate = JinjaTemplate(templateContent)
        renderedContent = jinjaTemplate.render(**kwargs)

    for outputFile, fullOutputPath in zip(outputFiles, fullOutputPaths):
        if template.noReload and os.path.exists(fullOutputPath):
            logger.debug(
                f'Skipping generation of "{outputFile}" from template "{template.file}" as noReload is set and the output file already exists.'
            )
            continue

        os.makedirs(os.path.dirname(fullOutputPath), exist_ok=True)

        with open(fullOutputPath, "w") as f:
            f.write(renderedContent)

        logger.info(f'Generated file "{outputFile}" from template "{template.file}".')

    UpdateFileStamp(template.file)

    return renderedContent, allDependencies
