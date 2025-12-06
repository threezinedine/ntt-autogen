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


def test_autogen_with_dependencies(fs: FakeFilesystem) -> None:
    os.makedirs("/project", exist_ok=True)

    with open("/project/base.json.in", "w") as f:
        f.write(
            """
        {
            "base_setting": "{{ BASE_VALUE }}" 
        }
        """
        )

    with open("/project/depedencies.txt", "w") as f:
        f.write("base.json.in\n")

    settings = Settings(
        templates=[
            Template(
                file="base.json.in",
                dependencies=["."],
                extensions=[".txt"],
            )
        ]
    )

    with open("/project/autogen-settings.json", "w") as f:
        f.write(json.dumps(asdict(settings)))

    Autogen(baseDir="/project", BASE_VALUE="base1")

    assert os.path.exists(
        "/project/temp/base.json.in.stamp"
    ), "Stamp file was not created."

    assert os.path.exists(
        "/project/temp/depedencies.txt.stamp"
    ), "Dependency stamp file was not created."

    firstStampTime = os.path.getmtime("/project/temp/base.json.in.stamp")

    time.sleep(0.1)
    with open("/project/depedencies.txt", "w") as f:
        f.write("base.json.in\nadditional_dependency.txt\n")

    Autogen(baseDir="/project", BASE_VALUE="base1")

    secondStampTime = os.path.getmtime("/project/temp/base.json.in.stamp")

    assert (
        firstStampTime < secondStampTime
    ), "Stamp file was not updated after dependency file was modified."

    with open("/project/base.json", "r") as f:
        generated_content = f.read()
        data = json.loads(generated_content)
        assert (
            data["base_setting"] == "base1"
        ), "base_setting was not set correctly after dependency modification."


def test_templates_with_shared_dependencies(fs: FakeFilesystem) -> None:
    os.makedirs("/project", exist_ok=True)

    with open("/project/shared_dep.txt", "w") as f:
        f.write("Shared dependency content")

    template1 = Template(
        file="template1.json.in",
        dependencies=["."],
        extensions=[".txt"],
    )

    template2 = Template(
        file="template2.json.in",
        dependencies=["."],
        extensions=[".txt"],
    )

    with open("/project/template1.json.in", "w") as f:
        f.write(
            """
        {
            "template": "{{ TEMPLATE_NAME }}"
        }
        """
        )

    with open("/project/template2.json.in", "w") as f:
        f.write(
            """
        {
            "template": "{{ TEMPLATE_NAME }}"
        }
        """
        )

    settings = Settings(templates=[template1, template2])

    with open("/project/autogen-settings.json", "w") as f:
        f.write(json.dumps(asdict(settings)))

    Autogen(baseDir="/project", TEMPLATE_NAME="Hello")

    assert os.path.exists(
        "/project/temp/template1.json.in.stamp"
    ), "Stamp file for template1 was not created."

    with open("/project/template1.json", "r") as f:
        generated_content1 = f.read()
        data1 = json.loads(generated_content1)
        assert data1["template"] == "Hello", "Template1 was not generated correctly."

    assert os.path.exists(
        "/project/temp/template2.json.in.stamp"
    ), "Stamp file for template2 was not created."

    with open("/project/template2.json", "r") as f:
        generated_content2 = f.read()
        data2 = json.loads(generated_content2)
        assert data2["template"] == "Hello", "Template2 was not generated correctly."

    time.sleep(0.1)

    Autogen(baseDir="/project", TEMPLATE_NAME="World")

    with open("/project/template1.json", "r") as f:
        generated_content1 = f.read()
        data1 = json.loads(generated_content1)
        assert data1["template"] == "Hello", "Template1 was not regenerated correctly."

    with open("/project/template2.json", "r") as f:
        generated_content2 = f.read()
        data2 = json.loads(generated_content2)
        assert data2["template"] == "Hello", "Template2 was not regenerated correctly."

    time.sleep(0.1)
    with open("/project/shared_dep.txt", "w") as f:
        f.write("Modified shared dependency content")

    Autogen(baseDir="/project", TEMPLATE_NAME="New")

    with open("/project/template1.json", "r") as f:
        generated_content1 = f.read()
        data1 = json.loads(generated_content1)
        assert data1["template"] == "New", "Template1 was not regenerated correctly."

    with open("/project/template2.json", "r") as f:
        generated_content2 = f.read()
        data2 = json.loads(generated_content2)
        assert data2["template"] == "New", "Template2 was not regenerated correctly."
