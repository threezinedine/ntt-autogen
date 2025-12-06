import os
import time
import json
from dataclasses import asdict
from pyfakefs.fake_filesystem import FakeFilesystem
from ntt_autogen import Autogen, Settings, Template


def test_auto_generate_config(fs: FakeFilesystem) -> None:
    os.makedirs("/project", exist_ok=True)

    settings = Settings(templates=[Template(file="config.json.in")])

    with open("/project/autogen-settings.json", "w") as f:
        f.write(json.dumps(asdict(settings)))

    configContent = """{
        "setting1": "{{ VALUE }}",
        "setting2": "value2"
    }"""

    with open("/project/config.json.in", "w") as f:
        f.write(configContent)

    Autogen(baseDir="/project", VALUE="value1")

    assert os.path.exists("/project/config.json"), "Config file was not generated."

    with open("/project/config.json", "r") as f:
        generated_config = f.read()
        data = json.loads(generated_config)
        assert data["setting1"] == "value1", "setting1 was not set correctly."

    assert os.path.exists(
        "/project/temp/config.json.in.stamp"
    ), "Stamp file was not created."


def test_auto_generate_setting_file(fs: FakeFilesystem) -> None:
    fs.makedir("/project")  # type: ignore

    assert not os.path.exists(
        "/project/autogen-settings.json"
    ), "Setting file should not exist yet."

    Autogen(baseDir="/project")

    assert os.path.exists(
        "/project/autogen-settings.json"
    ), "Setting file was not generated."

    with open("/project/autogen-settings.json", "r") as f:
        settings = json.load(f)
        assert "templates" in settings, "Default settings not set correctly."
        assert "bindings" in settings, "Default settings not set correctly."


def test_skip_unchanged_template(fs: FakeFilesystem) -> None:
    os.makedirs("/project", exist_ok=True)

    content = """
    {
        "setting1": "{{ VALUE }}",
    }
    """

    with open("/project/template.json.in", "w") as f:
        f.write(content)

    settings = Settings(templates=[Template(file="template.json.in")])
    with open("/project/autogen-settings.json", "w") as f:
        f.write(json.dumps(asdict(settings)))

    Autogen(baseDir="/project", VALUE="initial")

    firstStampTime = os.path.getmtime("/project/temp/template.json.in.stamp")

    Autogen(baseDir="/project", VALUE="initial")

    secondStampTime = os.path.getmtime("/project/temp/template.json.in.stamp")

    assert (
        firstStampTime == secondStampTime
    ), "Stamp file was updated despite no changes to the template."


def test_auto_generate_template_if_source_changed(fs: FakeFilesystem) -> None:
    os.makedirs("/project", exist_ok=True)

    content = """
    {
        "setting1": "{{ VALUE }}"
    }
    """

    with open("/project/template.json.in", "w") as f:
        f.write(content)

    settings = Settings(templates=[Template(file="template.json.in")])
    with open("/project/autogen-settings.json", "w") as f:
        f.write(json.dumps(asdict(settings)))

    Autogen(baseDir="/project", VALUE="initial")

    firstStampTime = os.path.getmtime("/project/temp/template.json.in.stamp")

    time.sleep(0.1)
    with open("/project/template.json.in", "w") as f:
        f.write(
            """
        {
            "setting1": "{{ VALUE }}",
            "setting2": "new_value"
        }
        """
        )

    Autogen(baseDir="/project", VALUE="initial")

    secondStampTime = os.path.getmtime("/project/temp/template.json.in.stamp")

    with open("/project/template.json", "r") as f:
        generated_content = f.read()
        print(generated_content)
        data = json.loads(generated_content)
        assert (
            data["setting1"] == "initial"
        ), "setting1 was not set correctly after modification."
        assert (
            data["setting2"] == "new_value"
        ), "New setting2 was not added after modification."

    assert (
        firstStampTime < secondStampTime
    ), "Stamp file was not updated after the template was modified."
