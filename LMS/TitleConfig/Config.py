from importlib import resources
from typing import Self

import yaml

from LMS.Common.LMS_DataType import LMS_DataType
from LMS.Project.MSBP import MSBP
from LMS.TitleConfig.Definitions.Attributes import AttributeConfig
from LMS.TitleConfig.Definitions.Tags import TagConfig, TagDefinition
from LMS.TitleConfig.Definitions.Value import ValueDefinition

TAG_KEY = "tag_definitions"
ATTR_KEY = "attribute_definitions"


class TitleConfig:
    """Represents a configuration for a specific game/title."""

    # Populate the preset list from the directory
    PRESET_LIST = [
        file.name.removesuffix(".yaml")
        for file in resources.files("LMS.TitleConfig.Presets").iterdir()
        if file.name.endswith(".yaml")
    ]

    def __init__(
        self, attribute_configs: dict[str, AttributeConfig], tag_config: TagConfig
    ):
        self._attribute_configs = attribute_configs
        self._tag_config = tag_config

    @property
    def attribute_configs(self) -> dict[str, AttributeConfig]:
        """The map of attribute config instances."""
        return self._attribute_configs

    @property
    def tag_config(self) -> TagConfig:
        """The loaded tag config instance."""
        return self._tag_config

    @classmethod
    def load_preset(cls, game: str) -> Self:
        """Loads an existing preset from a game."""
        if game.lower() not in [preset.lower() for preset in cls.PRESET_LIST]:
            raise FileNotFoundError(f"Preset '{game}' not found.")

        with resources.open_text("LMS.TitleConfig.Presets", f"{game}.yaml") as f:
            return cls.load_config(f.read())

    @classmethod
    def load_file(self, file_path: str) -> Self:
        """Loads a config from a file.

        :param file_path: the path to the config."""
        with open(file_path, "r") as f:
            return TitleConfig.load_config(f.read())

    @classmethod
    def load_config(cls, content: str | dict) -> Self:
        """Loads the config of a specified game.

        :param content: the config content, as a string or loaded as a dictionary."""
        if isinstance(content, str):
            parsed_content = yaml.safe_load(content)
        else:
            parsed_content = content

        # Load the attribute definitions
        attribute_configs = {}
        for config in parsed_content[ATTR_KEY]:
            definitions = [
                ValueDefinition.from_dict(value_def)
                for value_def in config["definitions"]
            ]
            attribute_configs[config["name"]] = AttributeConfig(
                config["name"], config["description"], definitions
            )

        # Load the tag definitions
        tag_definitions = []
        group_map = parsed_content[TAG_KEY]["groups"]
        for tag_def in parsed_content[TAG_KEY]["tags"]:
            tag_definitions.append(TagDefinition.from_dict(tag_def, group_map))

        tag_config = TagConfig(group_map, tag_definitions)

        return cls(attribute_configs, tag_config)

    @staticmethod
    def generate_file(file_path: str, project: MSBP) -> None:
        with open(file_path, "w+") as f:
            yaml.safe_dump(
                TitleConfig.generate_config(project),
                f,
                default_flow_style=False,
                sort_keys=False,
            )

    @staticmethod
    def generate_config(project: MSBP) -> dict | None:
        """Creates a message config file for the game.

        :param project: a MSBP object."""
        # TODO: Add custom node definitions

        config = {}

        config[TAG_KEY] = {
            "groups": {
                i: group.name for i, group in enumerate(project.tag_groups, start=1)
            },
            "tags": [],
        }

        if project.tag_groups is not None:
            for group_i, group in enumerate(project.tag_groups, start=1):
                for tag_i, info in enumerate(group.tag_definitions):

                    definition = {
                        "name": info.name,
                        "group_index": group_i,
                        "tag_index": tag_i,
                        "description": "",
                        "parameters": [],
                    }

                    for param_info in info.param_info:
                        param_definition = {
                            "name": param_info.name,
                            "description": "",
                            "datatype": param_info.datatype.to_string(),
                        }

                        if param_info.datatype is LMS_DataType.LIST:
                            param_definition["list_items"] = param_info.list_items

                        definition["parameters"].append(param_definition)

                    config[TAG_KEY]["tags"].append(definition)

        config[ATTR_KEY] = []
        if project.attribute_info is not None:

            attr_definitions = []
            for attr_info in project.attribute_info:
                definition = {
                    "name": attr_info.name,
                    "description": "",
                    "datatype": attr_info.datatype.to_string(),
                }
                if attr_info.datatype is LMS_DataType.LIST:
                    definition["list_items"] = attr_info.list_items

                attr_definitions.append(definition)

            # Main attribute entries
            config[ATTR_KEY].append(
                {
                    "name": project.name,
                    "description": "",
                    "definitions": attr_definitions,
                }
            )

        return config
