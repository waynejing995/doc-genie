---
name: genie-extract
description: >
  Extract document sections as black boxes with inputs, outputs, and attributes.
  Supports PDF, DOCX, Markdown, and code files (Python, JS, TS, Go, Java).
  Use when analyzing specs, parsing requirements, or defining system components.
  Triggers: extract, parse, analyze document, find sections, define components.
---

# Extract Black Boxes

Extract structured black boxes from documents and code files.

## Input Sources

| Type | Formats | Tool |
|------|---------|------|
| Document | PDF, DOCX, Markdown | pdfplumber, python-docx, markdown-it-py |
| Code | Python, JS, TS, Go, Java | ast-grep-py |
| API Spec | OpenAPI, GraphQL | YAML/JSON parser |
| Config | YAML, JSON, TOML | PyYAML |

## Extraction Process

1. Parse file structure (headings, sections, functions, classes)
2. Identify component boundaries
3. Extract inputs (parameters, dependencies, triggers)
4. Extract outputs (results, side effects, artifacts)
5. Extract attributes (constraints, properties, metadata)

## Output Template

**ALWAYS use this exact format:**

```yaml
blackboxes:
  - id: "bb-001"
    name: "Component Name"
    source:
      type: "document" | "code" | "api_spec" | "config"
      file: "path/to/file"
      section: "## Section Title"
      line_range: [start, end]
    
    inputs:
      - name: "input_name"
        type: "data" | "trigger" | "parameter"
        required: true | false
        format: "string" | "number" | "object" | etc.
        description: "What this input is"
    
    outputs:
      - name: "output_name"
        type: "data" | "side_effect" | "artifact"
        format: "string" | "number" | "object" | etc.
        description: "What this output is"
    
    attributes:
      constraints:
        - "Constraint 1"
        - "Constraint 2"
      dependencies:
        - "bb-002"
      properties:
        owner: "team-name"
        status: "draft" | "approved" | "deprecated"
```

## Example Output

```yaml
blackboxes:
  - id: "bb-auth-001"
    name: "User Authentication"
    source:
      type: "document"
      file: "specs/auth.md"
      section: "## 3. Authentication Flow"
      line_range: [45, 120]
    
    inputs:
      - name: "user_credentials"
        type: "data"
        required: true
        format: "object"
        description: "Username and password or OAuth token"
      - name: "auth_request"
        type: "trigger"
        required: true
        format: "http_request"
        description: "POST /api/auth/login"
    
    outputs:
      - name: "jwt_token"
        type: "data"
        required: true
        format: "string"
        description: "24-hour JWT access token"
      - name: "auth_log"
        type: "side_effect"
        required: false
        format: "database_entry"
        description: "Audit log entry"
    
    attributes:
      constraints:
        - "Password minimum 8 characters"
        - "Lock after 5 failed attempts"
        - "Token expires in 24 hours"
      dependencies:
        - "bb-user-db-001"
        - "bb-log-service-001"
      properties:
        owner: "auth-team"
        status: "approved"
```
