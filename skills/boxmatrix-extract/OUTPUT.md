# Output Template: Black Box Extraction

```yaml
blackboxes:
  - id: "bb-{source}-{number}"
    name: "Component Name"
    source:
      type: "document" | "code" | "api_spec" | "config"
      file: "path/to/file"
      section: "## Section Title"
    
    inputs:
      - name: "input_name"
        type: "data" | "trigger" | "parameter"
        required: true | false
        description: "What this input is"
    
    outputs:
      - name: "output_name"
        type: "data" | "side_effect" | "artifact"
        description: "What this output is"
    
    attributes:
      constraints:
        - "Constraint 1"
      dependencies:
        - "bb-other-001"
      properties:
        owner: "team-name"
```

## ID Convention

- Format: `bb-{source}-{number}`
- Source: abbreviated filename (e.g., "auth-spec.md" → "auth")
- Number: sequential within source (001, 002, ...)

## Subagent Chunk Format

When processing in parallel, each subagent outputs ONE blackbox per chunk:

```yaml
blackboxes:
  - id: "bb-auth-001"
    name: "User Authentication"
    source:
      type: "document"
      file: "auth-spec.md"
      section: "## 3. Authentication"
    inputs:
      - name: "credentials"
        type: "data"
        required: true
    outputs:
      - name: "jwt_token"
        type: "data"
    attributes:
      constraints: ["24h expiry"]
```
