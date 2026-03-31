"""Tests for blackbox_model module."""

import pytest

from lib.blackbox_model import (
    BlackBox,
    BlackBoxAttributes,
    BlackBoxInput,
    BlackBoxOutput,
    BlackBoxSource,
)


class TestBlackBoxInput:
    def test_create_input(self):
        inp = BlackBoxInput(
            name="user_id", type="data", required=True, description="User identifier"
        )
        assert inp.name == "user_id"
        assert inp.type == "data"
        assert inp.required is True

    def test_input_to_dict(self):
        inp = BlackBoxInput(name="token", type="data", required=False, format="string")
        d = inp.to_dict()
        assert d["name"] == "token"
        assert d["type"] == "data"
        assert d["required"] is False
        assert d["format"] == "string"


class TestBlackBoxOutput:
    def test_create_output(self):
        out = BlackBoxOutput(name="result", type="data", description="Operation result")
        assert out.name == "result"
        assert out.type == "data"

    def test_output_to_dict(self):
        out = BlackBoxOutput(name="token", type="data", format="jwt")
        d = out.to_dict()
        assert d["name"] == "token"
        assert d["format"] == "jwt"


class TestBlackBoxSource:
    def test_create_source(self):
        src = BlackBoxSource(type="document", file="spec.md", section="## Auth")
        assert src.type == "document"
        assert src.file == "spec.md"

    def test_source_to_dict(self):
        src = BlackBoxSource(type="code", file="auth.py", line_range=(10, 50))
        d = src.to_dict()
        assert d["type"] == "code"
        assert d["line_range"] == [10, 50]


class TestBlackBoxAttributes:
    def test_create_attributes(self):
        attrs = BlackBoxAttributes(
            constraints=["24h expiry"],
            dependencies=["bb-002"],
            properties={"owner": "auth-team"},
        )
        assert len(attrs.constraints) == 1
        assert "bb-002" in attrs.dependencies

    def test_attributes_to_dict(self):
        attrs = BlackBoxAttributes(constraints=["max 100"])
        d = attrs.to_dict()
        assert d["constraints"] == ["max 100"]
        assert d["dependencies"] == []


class TestBlackBox:
    def test_create_blackbox(self):
        bb = BlackBox(
            id="bb-auth-001",
            name="User Auth",
            source=BlackBoxSource(type="document", file="auth.md"),
            inputs=[BlackBoxInput(name="creds", type="data")],
            outputs=[BlackBoxOutput(name="token", type="data")],
            attributes=BlackBoxAttributes(constraints=["24h"]),
        )
        assert bb.id == "bb-auth-001"
        assert bb.name == "User Auth"
        assert len(bb.inputs) == 1
        assert len(bb.outputs) == 1

    def test_blackbox_to_dict(self):
        bb = BlackBox(
            id="bb-001",
            name="Test",
            source=BlackBoxSource(type="document", file="test.md"),
        )
        d = bb.to_dict()
        assert d["id"] == "bb-001"
        assert d["name"] == "Test"
        assert d["inputs"] == []
        assert d["outputs"] == []

    def test_blackbox_to_yaml(self):
        bb = BlackBox(
            id="bb-001",
            name="Test",
            source=BlackBoxSource(type="document", file="test.md"),
        )
        yaml_str = bb.to_yaml()
        assert "bb-001" in yaml_str
        assert "Test" in yaml_str

    def test_blackbox_from_dict(self):
        data = {
            "id": "bb-001",
            "name": "Auth",
            "source": {"type": "document", "file": "auth.md", "section": "## Auth"},
            "inputs": [{"name": "creds", "type": "data", "required": True}],
            "outputs": [{"name": "token", "type": "data"}],
            "attributes": {"constraints": ["24h"], "dependencies": [], "properties": {}},
        }
        bb = BlackBox.from_dict(data)
        assert bb.id == "bb-001"
        assert bb.name == "Auth"
        assert bb.inputs[0].name == "creds"
        assert bb.attributes.constraints[0] == "24h"
