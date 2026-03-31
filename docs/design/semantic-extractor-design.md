# Semantic Code Extractor Design

## Problem Statement

Current tree-sitter extractor only provides structural skeleton:
- Function/class names
- Line numbers  
- Basic parameter names

But lacks semantic content:
- Real input types and meanings
- Output types and purposes
- Docstring metadata
- Data flow between components
- Attribute descriptions

## Architecture Proposal

### Layer 1: Index Layer (tree-sitter)
**Purpose**: Fast structural scanning
**Output**: Skeleton with locations

```yaml
- name: GenieConfig
  type: class
  line: 42
  methods:
    - name: __init__
      line: 45
    - name: depth
      line: 73
      decorators: [@property]
```

### Layer 2: Semantic Layer (Python AST + Type Analysis)
**Purpose**: Extract rich metadata
**Input**: Index + Source code content
**Output**: Enriched black boxes

```yaml
- name: GenieConfig.__init__
  type: method
  line: 45
  inputs:
    - name: project_root
      type: str
      default: "."
      description: "Root path for project config"
  outputs:
    - type: None
      description: "Initializes config object"
  attributes:
    - self._project_root: Path
    - self._config: dict[str, Any]
  docstring: "Initialize config with project root path"
```

### Layer 3: AI Analysis Layer (Skills)
**Purpose**: Full semantic understanding
**Input**: Enriched black boxes + Context
**Output**: Relationships, patterns, insights

## Implementation Approach

### Python AST-based Semantic Extraction

Use Python's ast module to extract:
- Type annotations from signatures
- Docstrings (Google/NumPy/Sphinx style)
- Variable assignments in class __init__
- Decorator semantics
- Return type inference

### Integration with Existing Pipeline

```
Source Code
    ↓
tree-sitter (Index) → Skeleton: {name, line, type}
    ↓
AST Enricher → Enriched: {inputs, outputs, types, docs}
    ↓
Pattern Detector → Hints: {potential_data_flow, dependencies}
    ↓
AI Skill → Final: {relationships, semantic_box}
```

## Next Steps

1. Create `lib/extractors/semantic_enricher.py`
2. Add type annotation extraction
3. Add docstring parsing
4. Integrate with CLI pipeline
