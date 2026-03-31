"""Tests for relationship_types module."""

import pytest

from lib.relationship_types import Relationship, RelationshipCategory, RelationshipType


class TestRelationshipType:
    def test_data_flow(self):
        assert RelationshipType.DATA_FLOW.value == "data_flow"

    def test_dependency(self):
        assert RelationshipType.DEPENDENCY.value == "dependency"

    def test_interface(self):
        assert RelationshipType.INTERFACE.value == "interface"

    def test_conflict(self):
        assert RelationshipType.CONFLICT.value == "conflict"


class TestRelationshipCategory:
    def test_data_category(self):
        assert RelationshipCategory.DATA.value == "data"

    def test_control_category(self):
        assert RelationshipCategory.CONTROL.value == "control"


class TestRelationship:
    def test_create_relationship(self):
        rel = Relationship(
            source_id="bb-001",
            target_id="bb-002",
            type=RelationshipType.DATA_FLOW,
            category=RelationshipCategory.DATA,
            evidence="Auth outputs token to Gateway",
        )
        assert rel.source_id == "bb-001"
        assert rel.target_id == "bb-002"
        assert rel.type == RelationshipType.DATA_FLOW

    def test_relationship_to_dict(self):
        rel = Relationship(
            source_id="bb-001",
            target_id="bb-002",
            type=RelationshipType.DEPENDENCY,
            category=RelationshipCategory.CONTROL,
            confidence=0.9,
            evidence="Auth requires DB",
        )
        d = rel.to_dict()
        assert d["source"] == "bb-001"
        assert d["target"] == "bb-002"
        assert d["type"] == "dependency"
        assert d["confidence"] == 0.9

    def test_relationship_from_dict(self):
        data = {
            "source": "bb-001",
            "target": "bb-002",
            "type": "data_flow",
            "confidence": 0.85,
            "evidence": "Test evidence",
        }
        rel = Relationship.from_dict(data)
        assert rel.source_id == "bb-001"
        assert rel.type == RelationshipType.DATA_FLOW

    def test_relationship_to_yaml(self):
        rel = Relationship(
            source_id="bb-001",
            target_id="bb-002",
            type=RelationshipType.INTERFACE,
            category=RelationshipCategory.INTERACTION,
        )
        yaml_str = rel.to_yaml()
        assert "bb-001" in yaml_str
        assert "interface" in yaml_str
