from pathlib import Path

import pytest
from linkml_runtime.linkml_model import SchemaDefinition
from linkml_runtime.loaders import yaml_loader

from linkml.validator.plugins.pydantic_validation_plugin import PydanticValidationPlugin
from linkml.validator.validation_context import ValidationContext

PERSONINFO_SCHEMA = str(Path(__file__).parent / "input/personinfo.yaml")


@pytest.fixture
def validation_context():
    schema = yaml_loader.load(PERSONINFO_SCHEMA, SchemaDefinition)
    return ValidationContext(schema, "Person")


@pytest.mark.parametrize(
    "instance,valid,skip",
    [
        ({"id": "1", "full_name": "Person One"}, True, False),
        ({"id": "1", "full_name": "Person One", "phone": "1-555-555-5555"}, True, False),
        ({"id": "1", "full_name": "Person One", "not_a_field": "blah"}, False, False),
        ({}, False, False),
        ({"id": "1"}, False, False),
        ({"id": "1", "full_name": "Person One", "aliases": []}, True, False),
        ({"id": "1", "full_name": "Person One", "aliases": ["Person 1"]}, True, False),
        ({"id": "1", "full_name": "Person One", "aliases": "Person 1"}, False, False),
        ({"id": "1", "full_name": ["Person One"]}, False, False),
        ({"id": ["1"], "full_name": "Person One"}, False, False),
        ({"id": "1", "full_name": 1, "age": 100}, True, False),
        ({"id": "1", "full_name": 1, "age": "one hundred"}, False, False),
        ({"full_name": "Person One"}, False, False),
        # TODO
        ({"id": "1", "full_name": "Person One", "phone": "not a number"}, False, True),
        ({"id": "1", "full_name": 1}, False, True),
        ({"id": "1", "full_name": 1, "age": "100"}, False, True),
    ],
)
def test_instance(validation_context, instance, valid, skip):
    if skip:
        pytest.skip()
    plugin = PydanticValidationPlugin()
    results = list(plugin.process(instance, validation_context))
    if valid:
        assert not results
    else:
        assert len(results) == 1
