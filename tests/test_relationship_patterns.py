"""Tests for relationship_patterns module."""

import pytest

from lib.blackbox_model import BlackBox, BlackBoxInput, BlackBoxOutput, BlackBoxSource
from lib.patterns.relationship_patterns import PatternDetector


class TestPatternDetector:
    def test_detect_data_flow_from_io_match(self):
        boxes = [
            BlackBox(
                id="bb-001",
                name="Auth",
                source=BlackBoxSource(type="document", file="auth.md"),
                outputs=[BlackBoxOutput(name="jwt_token", type="data")],
            ),
            BlackBox(
                id="bb-002",
                name="Gateway",
                source=BlackBoxSource(type="document", file="gateway.md"),
                inputs=[BlackBoxInput(name="jwt_token", type="data")],
            ),
        ]
        detector = PatternDetector()
        rels = detector.detect(boxes)

        data_flows = [r for r in rels if r["type"] == "data_flow"]
        assert len(data_flows) == 1
        assert data_flows[0]["source"] == "bb-001"
        assert data_flows[0]["target"] == "bb-002"

    def test_detect_dependency_from_text(self):
        boxes = [
            BlackBox(
                id="bb-001",
                name="Order Service",
                source=BlackBoxSource(type="document", file="order.md"),
            ),
            BlackBox(
                id="bb-002",
                name="User Service",
                source=BlackBoxSource(type="document", file="user.md"),
            ),
        ]
        boxes[0]._text = "Order Service depends on User Service"

        detector = PatternDetector()
        rels = detector.detect(boxes)

        deps = [r for r in rels if r["type"] == "dependency"]
        assert len(deps) >= 1

    def test_no_self_relationship(self):
        boxes = [
            BlackBox(
                id="bb-001",
                name="Auth",
                source=BlackBoxSource(type="document", file="auth.md"),
                inputs=[{"name": "creds", "type": "data"}],
                outputs=[{"name": "creds", "type": "data"}],
            ),
        ]
        detector = PatternDetector()
        rels = detector.detect(boxes)

        self_rels = [r for r in rels if r["source"] == r["target"]]
        assert len(self_rels) == 0

    def test_detect_multiple_relationships(self):
        boxes = [
            BlackBox(
                id="bb-001",
                name="Auth",
                source=BlackBoxSource(type="document", file="auth.md"),
                outputs=[BlackBoxOutput(name="token", type="data")],
            ),
            BlackBox(
                id="bb-002",
                name="Gateway",
                source=BlackBoxSource(type="document", file="gw.md"),
                inputs=[BlackBoxInput(name="token", type="data")],
                outputs=[BlackBoxOutput(name="request", type="data")],
            ),
            BlackBox(
                id="bb-003",
                name="API",
                source=BlackBoxSource(type="document", file="api.md"),
                inputs=[BlackBoxInput(name="request", type="data")],
            ),
        ]
        detector = PatternDetector()
        rels = detector.detect(boxes)

        assert len(rels) >= 2
