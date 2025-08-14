from importlib import resources

import yaml

from lms.common.lms_datatype import LMS_DataType
from lms.project.msbp import MSBP
from lms.titleconfig.definitions.attribute import AttributeConfig
from lms.titleconfig.definitions.tags import TagConfig, TagDefinition
from lms.titleconfig.definitions.value import ValueDefinition


class TitleConfig:
    """Represents a configuration for a specific title."""

    TAG_KEY = "tag_definitions"
    ATTR_KEY = "attribute_definitions"

    PRESET_LIST = [
        file.name.removesuffix(".yaml")
        for file in resources.files("lms.titleconfig.presets").iterdir()
    ]

    def __init__(
        self,
        game: str | None,
        attribute_configs: dict[str, AttributeConfig] | None = None,
        tag_config: TagConfig | None = None,
    ):
        self._game = game
        self._attribute_configs = attribute_configs
        self._tag_config = tag_config

    @property
    def game(self) -> str | None:
        """The name of the game for the titleconfig."""
        return self._game

    @property
    def attribute_configs(self) -> dict[str, AttributeConfig] | None:
        """The map of attribute config instances."""
        return self._attribute_configs

    @property
    def tag_config(self) -> TagConfig | None:
        """The loaded tag config instance."""
        return self._tag_config

    @classmethod
    def load_preset(cls, game: str):
        """
        Loads an existing preset from a game.

        :param game: the game preset.

        The list of presets are found with `TitleConfig.preset_list`.
        """
        preset_map = {preset.lower(): preset for preset in cls.PRESET_LIST}

        if game.lower() not in preset_map:
            raise FileNotFoundError(f"Preset '{game}' not found.")

        actual_name = preset_map[game.lower()]

        with resources.open_text("lms.titleconfig.presets", f"{actual_name}.yaml") as f:
            return cls.load_config(f.read())

    @classmethod
    def load_file(cls, file_path: str):
        """
        Loads a config from a file.

        :param file_path: the path to the config.
        """
        with open(file_path, "r") as f:
            return TitleConfig.load_config(f.read())

    @classmethod
    def load_config(cls, content: str | dict):
        """
        Loads the config of a specified game.

        :param content: the config content, as a string or loaded as a dictionary.
        """

        if isinstance(content, str):
            parsed_content = yaml.safe_load(content)
        else:
            parsed_content = content

        game = parsed_content.get("game")

        attribute_configs = {}
        for config in parsed_content[cls.ATTR_KEY]:
            definitions = [
                ValueDefinition.from_dict(value_def)
                for value_def in config["definitions"]
            ]
            attribute_configs[config["name"]] = AttributeConfig(
                config["name"], config["description"], definitions
            )

        tag_definitions = []
        group_map = parsed_content[cls.TAG_KEY]["groups"]

        for tag_def in parsed_content[cls.TAG_KEY]["tags"]:
            tag_definitions.append(TagDefinition.from_dict(tag_def, group_map))

        tag_config = TagConfig(group_map, tag_definitions)

        return cls(game, attribute_configs, tag_config)

    @staticmethod
    def generate_file(file_path: str, game: str, project: MSBP) -> None:
        """
        Generates a title config file for a specific game.

        :param file_path: the path to the yaml file.
        :param game: the name of the game to create the config for.
        :param project: a MSBP object.
        """
        with open(file_path, "w+") as f:
            yaml.safe_dump(
                TitleConfig.generate_config(game, project),
                f,
                default_flow_style=False,
                sort_keys=False,
            )

    @staticmethod
    def generate_config(game: str, project: MSBP) -> dict | None:
        """
        Generates a title config file for the specified game.

        :param game: the name of the game to create the config for.
        :param project: a MSBP object.
        """
        config = {}
        config["game"] = game

        if project.tag_groups is not None:
            config[TitleConfig.TAG_KEY] = {
                "groups": {group.id: group.name for group in project.tag_groups},
                "tags": [],
            }

            for group in project.tag_groups:
                for i, tag_def in enumerate(group.tag_definitions):

                    definition = {
                        "name": tag_def.name,
                        "group_id": group.id,
                        "tag_index": i,
                        "description": "",
                        "parameters": None if not tag_def.parameter_definitions else [],
                    }

                    if definition["parameters"] is None:
                        continue

                    for param_def in tag_def.parameter_definitions:
                        param_definition: dict[str, str | list] = {
                            "name": param_def.name,
                            "description": "",
                            "datatype": param_def.datatype.to_string(),
                        }

                        if param_def.datatype is LMS_DataType.LIST:
                            param_definition["list_items"] = param_def.list_items

                        definition["parameters"].append(param_definition)

                    config[TitleConfig.TAG_KEY]["tags"].append(definition)

        config[TitleConfig.ATTR_KEY] = []
        if project.attribute_info is not None:

            attr_definitions = []
            for attr_def in project.attribute_info:
                definition = {
                    "name": attr_def.name,
                    "description": "",
                    "datatype": attr_def.datatype.to_string(),
                }
                if attr_def.datatype is LMS_DataType.LIST:
                    definition["list_items"] = attr_def.list_items

                attr_definitions.append(definition)

            # Main attribute entries
            config[TitleConfig.ATTR_KEY].append(
                {
                    "name": project.name,
                    "description": "",
                    "definitions": attr_definitions,
                }
            )

        return config
