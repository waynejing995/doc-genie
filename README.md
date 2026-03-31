# BoxMatrix

> **Box** = Self-contained unit | **Matrix** = Relationship network

A Claude Code plugin for extracting black boxes from code/documents and mapping their relationships.

## Design Philosophy

### The BoxMatrix Concept

Every system is composed of **Boxes** (components) connected in a **Matrix** (relationship network):

```
┌─────────────────────────────────────────────────────────────┐
│                         MATRIX                               │
│  ┌───────┐     ┌───────┐     ┌───────┐     ┌───────┐       │
│  │ Box A │────▶│ Box B │────▶│ Box C │────▶│ Box D │       │
│  └───────┘     └───────┘     └───────┘     └───────┘       │
│      │                           │                           │
│      └───────────────────────────┘                           │
│              (relationship)                                   │
└─────────────────────────────────────────────────────────────┘
```

### Three-Layer Architecture

BoxMatrix uses a three-layer approach for deep understanding:

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Index** | tree-sitter | Fast structural scanning |
| **Detection** | Pattern rules | Identify relationships |
| **Analysis** | AI Skills | Semantic understanding |

**Key insight**: tree-sitter only provides the skeleton. AI Skills provide the semantic understanding - inputs, outputs, constraints, and real data flow.

### The Black Box Abstraction

Each component is modeled as a **Box** with:

```yaml
- id: box-001
  name: UserService
  inputs:
    - name: user_id
      type: str
      description: "User identifier"
  outputs:
    - name: user_data
      type: dict
      description: "User profile data"
  attributes:
    constraints: ["Requires authentication"]
    dependencies: [box-002, box-003]
```

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/boxmatrix.git
cd boxmatrix

# Install dependencies
uv sync

# Install the plugin
claude plugin install .
```

## Usage

### CLI Commands

```bash
# Extract boxes from code
uv run boxmatrix extract lib/ --output .genie/boxes.yaml

# Analyze relationships
uv run boxmatrix relations lib/ --output .genie/relationships.yaml

# Find patterns and insights
uv run boxmatrix insights lib/ --output .genie/insights.yaml

# Generate interactive HTML report
uv run boxmatrix report --format html --output .genie/report.html
```

### Using Skills in Claude Code

The plugin provides four AI-powered skills:

#### 1. bx-extract

Extract black boxes from code or documents.

```
Use the bx-extract skill to extract boxes from lib/config.py
```

**Output**: YAML file with structured boxes including inputs, outputs, and dependencies.

#### 2. bx-relations

Analyze relationships between components.

```
Use the bx-relations skill to analyze relationships between lib/config.py and lib/storage/
```

**Relationship types**:
- `data_flow` - Data moves from A to B
- `dependency` - A depends on B
- `interface` - A calls B's interface
- `constraint` - A constrains B's behavior
- `conflict` - A conflicts with B

#### 3. bx-insights

Discover hidden patterns, conflicts, and implicit relationships.

```
Use the bx-insights skill to find patterns in lib/extractors/
```

**Finds**:
- Design patterns (Strategy, Repository, Observer)
- Anti-patterns (duplication, implicit coupling)
- Missing components
- Optimization opportunities

#### 4. bx-report

Generate interactive HTML reports with visualizations.

```
Use the bx-report skill to generate a full project report
```

**Features**:
- Interactive network graph (vis.js)
- Component distribution charts (Chart.js)
- Searchable tables
- Dark theme

## Project Structure

```
boxmatrix/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── skills/
│   ├── bx-extract/   # Extraction skill
│   ├── bx-relations/ # Relationship analysis
│   ├── bx-insights/  # Pattern detection
│   └── bx-report/    # Report generation
├── agents/
│   ├── extract-worker.md    # Parallel extraction
│   ├── data-flow-agent.md   # Data flow analysis
│   └── ...
├── lib/
│   ├── blackbox_model.py    # Box data model
│   ├── relationship_types.py # Relationship types
│   ├── extractors/          # Code/document extractors
│   └── storage/             # Persistence layer
└── tests/                   # Test suite
```

## Supported Formats

### Code
- Python (AST + tree-sitter)
- JavaScript/TypeScript
- C/C++
- Go, Java, Rust (optional)

### Documents
- PDF
- DOCX
- Markdown

## Development

```bash
# Run tests
uv run pytest tests/ -v

# Run E2E evaluation
uv run python scripts/run_e2e_eval.py

# View report
open .genie/e2e/e2e_report.html
```

## License

MIT

---

**BoxMatrix** - Every system is a matrix of connected boxes.