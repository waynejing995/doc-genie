from dataclasses import dataclass, field
from typing import Any


@dataclass
class BlackBoxInput:
    name: str
    type: str
    required: bool = True
    description: str = ""
    format: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "type": self.type, "required": self.required}
        if self.description:
            d["description"] = self.description
        if self.format:
            d["format"] = self.format
        return d


@dataclass
class BlackBoxOutput:
    name: str
    type: str
    description: str = ""
    format: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "type": self.type}
        if self.description:
            d["description"] = self.description
        if self.format:
            d["format"] = self.format
        return d


@dataclass
class BlackBoxSource:
    type: str
    file: str
    section: str | None = None
    line_range: tuple[int, int] | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"type": self.type, "file": self.file}
        if self.section:
            d["section"] = self.section
        if self.line_range:
            d["line_range"] = list(self.line_range)
        return d


@dataclass
class BlackBoxAttributes:
    constraints: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "constraints": self.constraints,
            "dependencies": self.dependencies,
            "properties": self.properties,
        }


@dataclass
class BlackBox:
    id: str
    name: str
    source: BlackBoxSource
    inputs: list[BlackBoxInput] = field(default_factory=list)
    outputs: list[BlackBoxOutput] = field(default_factory=list)
    attributes: BlackBoxAttributes = field(default_factory=BlackBoxAttributes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source.to_dict(),
            "inputs": [i.to_dict() for i in self.inputs],
            "outputs": [o.to_dict() for o in self.outputs],
            "attributes": self.attributes.to_dict(),
        }

    def to_yaml(self) -> str:
        import yaml

        return yaml.dump(
            {"blackboxes": [self.to_dict()]}, allow_unicode=True, default_flow_style=False
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BlackBox":
        source = BlackBoxSource(**data["source"])
        inputs = [BlackBoxInput(**i) for i in data.get("inputs", [])]
        outputs = [BlackBoxOutput(**o) for o in data.get("outputs", [])]
        attrs_data = data.get("attributes", {})
        attrs = BlackBoxAttributes(**attrs_data)
        return cls(
            id=data["id"],
            name=data["name"],
            source=source,
            inputs=inputs,
            outputs=outputs,
            attributes=attrs,
        )
