from dataclasses import dataclass
from enum import Enum
from typing import Any


class RelationshipCategory(Enum):
    DATA = "data"
    CONTROL = "control"
    STRUCTURE = "structure"
    INTERACTION = "interaction"
    CONSTRAINT = "constraint"
    ISSUE = "issue"
    MONITORING = "monitoring"


class RelationshipType(Enum):
    DATA_FLOW = "data_flow"
    TRANSFORM = "transform"
    AGGREGATE = "aggregate"
    CACHE = "cache"
    DEPENDENCY = "dependency"
    SEQUENCE = "sequence"
    PREEMPT = "preempt"
    ROUTING = "routing"
    COMPOSITION = "composition"
    EXTENSION = "extension"
    VERSION = "version"
    ALTERNATIVE = "alternative"
    INTERFACE = "interface"
    NOTIFICATION = "notification"
    DELEGATION = "delegation"
    SYNCHRONIZATION = "synchronization"
    CONSTRAINT = "constraint"
    VALIDATION = "validation"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate_limit"
    CONFLICT = "conflict"
    REPLICATION = "replication"
    OVERRIDE = "override"
    FALLBACK = "fallback"
    MONITORING = "monitoring"


@dataclass
class Relationship:
    source_id: str
    target_id: str
    type: RelationshipType
    category: RelationshipCategory
    confidence: float = 1.0
    evidence: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.type.value,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }

    def to_yaml(self) -> str:
        import yaml

        return yaml.dump(self.to_dict(), allow_unicode=True, default_flow_style=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Relationship":
        return cls(
            source_id=data["source"],
            target_id=data["target"],
            type=RelationshipType(data["type"]),
            category=RelationshipCategory.DATA,
            confidence=data.get("confidence", 1.0),
            evidence=data.get("evidence", ""),
        )
