import importlib.resources as pkg_resources
import os
from typing import Self

import yaml

from LMS.Config.Definitions.Attributes import AttributeConfig
from LMS.Config.Definitions.Tags import TagConfig, TagDefinition
from LMS.Config.Definitions.Value import ValueDefinition
from LMS.Field.LMS_DataType import LMS_DataType
from LMS.Project.MSBP import MSBP


class TitleConfig:
    """Represents a configuration for a specific game/title."""

    # Populate the preset list from the directory
    PRESET_LIST = [
        name.removesuffix(".yaml") for name in pkg_resources.contents("LMS.Config.Presets") if name.endswith(".yaml")
    ]

    def __init__(self, attribute_configs: dict[str, AttributeConfig], tag_config: TagConfig):
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
        """Loads an existing preset from the package."""
        if game not in cls.PRESET_LIST:
            raise FileNotFoundError(f"Preset '{game}' not found.")

        with pkg_resources.open_text("LMS.Config.Presets", f"{game}.yaml") as f:
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

        group_map = {0: "System"}
        tag_config = []

        # Add the System tag definitions to the config
        with open(r"LMS\Message\Tag\System.yaml", "r") as f:
            system_tags = yaml.safe_load(f)
            tag_config = system_tags

        # Combine with the rest of the cofnig
        group_map |= parsed_content["tag_definitions"]["groups"]
        for tag_def in parsed_content["tag_definitions"]["tags"]:
            tag_config.append(tag_def)

        # Load tag definitions
        tag_definitions = []
        for tag_def in tag_config:
            tag_name = tag_def["name"]
            group_index, tag_index = tag_def["group_index"], tag_def["tag_index"]
            group_name = group_map[group_index]
            tag_description = tag_def["description"]

            group_name = group_map[group_index]

            parameters = None
            if "parameters" in tag_def:
                parameters = []
                for param_def in tag_def["parameters"]:
                    param_name = param_def["name"]
                    param_description = param_def["description"]
                    datatype = LMS_DataType.from_string(param_def["datatype"])
                    list_items = param_def.get("list_items")
                    parameters.append(ValueDefinition(param_name, param_description, datatype, list_items))

            tag_definitions.append(
                TagDefinition(
                    group_name,
                    group_index,
                    tag_name,
                    tag_index,
                    tag_description,
                    parameters,
                )
            )

        tag_config = TagConfig(group_map, tag_definitions)

        # Load the attribute definitions
        attribute_config = {}
        for structure in parsed_content["attributes"]:
            structure_name = structure["name"]

            definitions = []
            for info in structure["definitions"]:
                name, description = info["name"], info["description"]
                datatype = LMS_DataType.from_string(info["datatype"])
                list_items = info.get("list_items")

                definition = ValueDefinition(name, description, datatype, list_items)
                definitions.append(definition)

            structure = AttributeConfig(structure_name, structure["description"], definitions)
            attribute_config[structure_name] = structure

        return cls(attribute_config, tag_config)

    @staticmethod
    def generate_file(file_path: str, project: MSBP) -> None:
        with open(file_path, "w+") as f:
            yaml.safe_dump(
                TitleConfig.generate_profile(project),
                f,
                default_flow_style=False,
                sort_keys=False,
            )

    @staticmethod
    def generate_config(project: MSBP) -> dict | None:
        """Creates a message config file for the game.

        :param project: a MSBP object."""
        # TODO: Add custom node definitions

        tag_key = "tag_definitions"
        attr_key = "attributes"

        config = {}
        # Source files may be a path to a non-existent directory.
        # These files were generated from the source machine from the actual libMS tool
        # Shorten the filename with basname and replace the extension with .msbt for lookup later when reading a MSBT
        config[tag_key] = {
            "groups": {i + 1: group.name for i, group in enumerate(project.tag_groups[1:])},
            "tags": [],
        }

        # Slice to exclude System group
        for group_i, group in enumerate(project.tag_groups[1:], start=1):
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

                config[tag_key]["tags"].append(definition)

        # Set main attribute entries as the definitions from the MSBP
        # Since most games use one MSBP these act the primary definitions
        config[attr_key] = []

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
        config[attr_key].append(
            {
                "name": project.name,
                "description": "",
                "definitions": attr_definitions,
            }
        )

        return config
