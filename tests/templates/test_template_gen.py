import json
from dataclasses import asdict
from pyfakefs.fake_filesystem import FakeFilesystem
from ntt_autogen import Autogen, Settings, Template


def test_auto_generate_config(fs: FakeFilesystem) -> None:
    fs.makedir("/project")  # type: ignore

    settings = Settings(templates=[Template(file="config.json.in")])

    with open("project/autogen-settings.json", "w") as f:
        f.write(json.dumps(asdict(settings)))

    fs.create_file(  # type: ignore
        "/project/config.json.in",
        contents=json.dumps((asdict(settings))),
    )

    Autogen(baseDir="/project")  # type: ignore

    assert fs.exists("/project/config.json"), "Config file was not generated."  # type: ignore
