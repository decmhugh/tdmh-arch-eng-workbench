# Jira ADF Formatting Guide — Creating Tickets via API

> Reference for creating well-formatted Jira tickets via the REST API v3.
> Covers ADF (Atlassian Document Format) for descriptions, acceptance criteria,
> and comments. All examples use the EACPP project conventions.

---

## API Basics

**Always use the v3 REST API** for creating and updating issues. The v2 API accepts
plain text or wiki markup but does not support interactive checkboxes or rich formatting.

```bash
# Create issue
curl -s -u "$JIRA_USER_EMAIL:$JIRA_API_TOKEN" \
  -X POST "$JIRA_BASE_URL/rest/api/3/issue" \
  -H "Content-Type: application/json" \
  -d @payload.json

# Search (new endpoint — old /rest/api/2/search is removed)
curl -s -u "$JIRA_USER_EMAIL:$JIRA_API_TOKEN" \
  -X POST "$JIRA_BASE_URL/rest/api/3/search/jql" \
  -H "Content-Type: application/json" \
  -d '{"jql": "project = EACPP AND issuetype = Sub-task", "maxResults": 50}'
```

**SSL Note**: On macOS, Python `urllib`/`requests` may fail with SSL cert errors.
Use `subprocess.run(["curl", ...])` as a workaround.

---

## EACPP Field Reference

| Field | API Path | Format | Notes |
|-------|----------|--------|-------|
| Project | `fields.project.key` | `"EACPP"` | |
| Issue Type | `fields.issuetype.name` | `"Sub-task"` | EACPP only has Epic, Sub-task, Risk |
| Parent (Epic) | `fields.parent.key` | `"EACPP-37"` | For Sub-tasks — NOT `customfield_10014` |
| Summary | `fields.summary` | Plain string | Imperative verb + what + context |
| Description | `fields.description` | **ADF JSON** | See structure below |
| Acceptance Criteria | `fields.customfield_10029` | **ADF JSON** | Must use taskList for checkboxes |
| Priority | `fields.priority.name` | `"Urgent"`, `"High"`, `"Medium"`, `"Low"` | |
| Labels | `fields.labels` | Array of strings | Include `epic:{component}` label |
| Team | `fields.customfield_10001` | `"7b8c4032-..."` | Plain string ID, NOT object |
| Story Points | `fields.customfield_10016` | Number | Optional — teams often point during refinement |

---

## ADF Document Structure

Every ADF field is a JSON document with this outer shell:

```json
{
  "version": 1,
  "type": "doc",
  "content": [
    // block-level nodes go here
  ]
}
```

### Block Node Types

| Node | Purpose | Example |
|------|---------|---------|
| `heading` | Section headers (h1–h6) | Context, Scope, Technical Approach |
| `paragraph` | Body text | Any prose |
| `bulletList` | Unordered list | Scope items, file lists |
| `orderedList` | Numbered list | Steps, sequences |
| `taskList` | Interactive checkboxes | **Acceptance criteria only** |
| `table` | Data tables | Files affected, endpoint summary |
| `codeBlock` | Fenced code | File paths, code references, CLI commands |
| `rule` | Horizontal divider | Section breaks |
| `blockquote` | Callout/quote | Important notes |

### Inline Mark Types

Marks are applied to text nodes inside paragraphs:

| Mark | Purpose | JSON |
|------|---------|------|
| `strong` | **Bold** | `{"type": "text", "text": "bold", "marks": [{"type": "strong"}]}` |
| `em` | *Italic* | `{"type": "text", "text": "italic", "marks": [{"type": "em"}]}` |
| `code` | `inline code` | `{"type": "text", "text": "code", "marks": [{"type": "code"}]}` |
| `link` | [Hyperlink] | `{"type": "text", "text": "link text", "marks": [{"type": "link", "attrs": {"href": "https://..."}}]}` |
| `strike` | ~~Strikethrough~~ | `{"type": "text", "text": "deleted", "marks": [{"type": "strike"}]}` |

---

## Description Field — Full Structure

The description must follow the team agreement structure: Context → Scope → Out of Scope → Technical Approach → Files Affected.

### Complete Example

```json
{
  "version": 1,
  "type": "doc",
  "content": [
    {
      "type": "heading",
      "attrs": {"level": 2},
      "content": [{"type": "text", "text": "Context"}]
    },
    {
      "type": "paragraph",
      "content": [
        {"type": "text", "text": "The agent registry ("},
        {"type": "text", "text": "acp-agent-registry", "marks": [{"type": "code"}]},
        {"type": "text", "text": ") needs a lifecycle state machine to enforce valid transitions between agent states (pending_review → approved → active → suspended → decommissioned)."}
      ]
    },
    {
      "type": "paragraph",
      "content": [
        {"type": "text", "text": "Parent Epic: "},
        {"type": "text", "text": "EACPP-37", "marks": [{"type": "link", "attrs": {"href": "https://sunlife.atlassian.net/browse/EACPP-37"}}]}
      ]
    },
    {
      "type": "heading",
      "attrs": {"level": 2},
      "content": [{"type": "text", "text": "Scope"}]
    },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [{"type": "paragraph", "content": [
            {"type": "text", "text": "Implement state machine with valid transitions in "},
            {"type": "text", "text": "acp_agent_registry/models.py", "marks": [{"type": "code"}]}
          ]}]
        },
        {
          "type": "listItem",
          "content": [{"type": "paragraph", "content": [
            {"type": "text", "text": "Add "},
            {"type": "text", "text": "POST /agents/{id}/transition", "marks": [{"type": "code"}]},
            {"type": "text", "text": " endpoint"}
          ]}]
        },
        {
          "type": "listItem",
          "content": [{"type": "paragraph", "content": [
            {"type": "text", "text": "Reject invalid state transitions with 409 Conflict"}
          ]}]
        }
      ]
    },
    {
      "type": "heading",
      "attrs": {"level": 2},
      "content": [{"type": "text", "text": "Out of Scope"}]
    },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [{"type": "paragraph", "content": [
            {"type": "text", "text": "Kill switch cascade (separate ticket)"}
          ]}]
        },
        {
          "type": "listItem",
          "content": [{"type": "paragraph", "content": [
            {"type": "text", "text": "UI updates for state visualization"}
          ]}]
        }
      ]
    },
    {
      "type": "heading",
      "attrs": {"level": 2},
      "content": [{"type": "text", "text": "Technical Approach"}]
    },
    {
      "type": "orderedList",
      "attrs": {"order": 1},
      "content": [
        {
          "type": "listItem",
          "content": [{"type": "paragraph", "content": [
            {"type": "text", "text": "Define an enum of valid states and a transition matrix as a dict"}
          ]}]
        },
        {
          "type": "listItem",
          "content": [{"type": "paragraph", "content": [
            {"type": "text", "text": "Add a "},
            {"type": "text", "text": "transition()", "marks": [{"type": "code"}]},
            {"type": "text", "text": " method on the Agent model that validates against the matrix"}
          ]}]
        },
        {
          "type": "listItem",
          "content": [{"type": "paragraph", "content": [
            {"type": "text", "text": "Emit a domain event ("},
            {"type": "text", "text": "AgentStateChanged", "marks": [{"type": "code"}]},
            {"type": "text", "text": ") on successful transition"}
          ]}]
        }
      ]
    },
    {
      "type": "heading",
      "attrs": {"level": 2},
      "content": [{"type": "text", "text": "Files Affected"}]
    },
    {
      "type": "table",
      "attrs": {"isNumberColumnEnabled": false, "layout": "default"},
      "content": [
        {
          "type": "tableRow",
          "content": [
            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "File"}]}]},
            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Change"}]}]},
            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Reason"}]}]}
          ]
        },
        {
          "type": "tableRow",
          "content": [
            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "src/acp_agent_registry/models.py", "marks": [{"type": "code"}]}]}]},
            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Modify"}]}]},
            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Add state enum and transition matrix"}]}]}
          ]
        },
        {
          "type": "tableRow",
          "content": [
            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "src/acp_agent_registry/routes.py", "marks": [{"type": "code"}]}]}]},
            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Modify"}]}]},
            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Add POST /agents/{id}/transition endpoint"}]}]}
          ]
        },
        {
          "type": "tableRow",
          "content": [
            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "tests/unit/test_lifecycle.py", "marks": [{"type": "code"}]}]}]},
            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "New"}]}]},
            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Unit tests for state machine transitions"}]}]}
          ]
        }
      ]
    }
  ]
}
```

---

## Acceptance Criteria — Interactive Checkboxes

The AC field (`customfield_10029`) **must** use `taskList` nodes. This renders interactive
checkboxes that team members can check off directly in the Jira UI.

### Rules

1. **Do NOT include an "Acceptance Criteria" heading** — the field label already provides it
2. Each item is a `taskItem` with `state: "TODO"` (unchecked)
3. Each `taskItem` needs a unique `localId` (use sequential IDs like `ac-1`, `ac-2`)
4. Use Gherkin format: **Given** / **When** / **Then** (bold the keywords)
5. No nested lists — keep each criterion a single clear statement
6. Support inline marks: `strong`, `code`, `link`

### Complete Example with Gherkin Format

```json
{
  "version": 1,
  "type": "doc",
  "content": [
    {
      "type": "taskList",
      "attrs": {"localId": "ac-list-1"},
      "content": [
        {
          "type": "taskItem",
          "attrs": {"localId": "ac-1", "state": "TODO"},
          "content": [
            {"type": "text", "text": "Given ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": "an agent in "},
            {"type": "text", "text": "approved", "marks": [{"type": "code"}]},
            {"type": "text", "text": " state, "},
            {"type": "text", "text": "When ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": "POST /agents/{id}/transition is called with "},
            {"type": "text", "text": "{\"target_state\": \"active\"}", "marks": [{"type": "code"}]},
            {"type": "text", "text": ", "},
            {"type": "text", "text": "Then ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": "the agent transitions to "},
            {"type": "text", "text": "active", "marks": [{"type": "code"}]},
            {"type": "text", "text": " and a 200 response is returned"}
          ]
        },
        {
          "type": "taskItem",
          "attrs": {"localId": "ac-2", "state": "TODO"},
          "content": [
            {"type": "text", "text": "Given ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": "an agent in "},
            {"type": "text", "text": "pending_review", "marks": [{"type": "code"}]},
            {"type": "text", "text": " state, "},
            {"type": "text", "text": "When ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": "transition to "},
            {"type": "text", "text": "active", "marks": [{"type": "code"}]},
            {"type": "text", "text": " is attempted, "},
            {"type": "text", "text": "Then ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": "a 409 Conflict is returned with the list of valid transitions"}
          ]
        },
        {
          "type": "taskItem",
          "attrs": {"localId": "ac-3", "state": "TODO"},
          "content": [
            {"type": "text", "text": "Given ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": "a successful state transition, "},
            {"type": "text", "text": "When ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": "the transition completes, "},
            {"type": "text", "text": "Then ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": "an "},
            {"type": "text", "text": "AgentStateChanged", "marks": [{"type": "code"}]},
            {"type": "text", "text": " domain event is emitted with old_state, new_state, and timestamp"}
          ]
        },
        {
          "type": "taskItem",
          "attrs": {"localId": "ac-4", "state": "TODO"},
          "content": [
            {"type": "text", "text": "Unit tests pass with ≥90% coverage on the state machine module"}
          ]
        }
      ]
    }
  ]
}
```

---

## Code Blocks in ADF

Use `codeBlock` for file paths, CLI commands, code snippets, and API examples:

```json
{
  "type": "codeBlock",
  "attrs": {"language": "python"},
  "content": [
    {"type": "text", "text": "class AgentState(str, Enum):\n    PENDING_REVIEW = \"pending_review\"\n    APPROVED = \"approved\"\n    ACTIVE = \"active\"\n    SUSPENDED = \"suspended\"\n    DECOMMISSIONED = \"decommissioned\""}
  ]
}
```

Supported `language` values: `python`, `bash`, `json`, `yaml`, `sql`, `javascript`,
`typescript`, `terraform`, `dockerfile`, `text`.

For inline code references (file paths, function names), use the `code` mark on text:

```json
{"type": "text", "text": "acp_agent_registry/models.py", "marks": [{"type": "code"}]}
```

---

## Python Helper — Build ADF

Use these helper functions to construct ADF payloads without hand-writing JSON:

```python
import json
import uuid

def adf_doc(*blocks):
    """Wrap blocks in an ADF document."""
    return {"version": 1, "type": "doc", "content": list(blocks)}

def adf_heading(text, level=2):
    """Create a heading block."""
    return {"type": "heading", "attrs": {"level": level},
            "content": [{"type": "text", "text": text}]}

def adf_paragraph(*inlines):
    """Create a paragraph with inline nodes."""
    return {"type": "paragraph", "content": list(inlines)}

def adf_text(text, bold=False, italic=False, code=False, link=None):
    """Create an inline text node with optional marks."""
    node = {"type": "text", "text": text}
    marks = []
    if bold:
        marks.append({"type": "strong"})
    if italic:
        marks.append({"type": "em"})
    if code:
        marks.append({"type": "code"})
    if link:
        marks.append({"type": "link", "attrs": {"href": link}})
    if marks:
        node["marks"] = marks
    return node

def adf_bullet_list(*items):
    """Create a bullet list from strings or inline node lists."""
    li = []
    for item in items:
        if isinstance(item, str):
            content = [adf_text(item)]
        else:
            content = item
        li.append({"type": "listItem", "content": [{"type": "paragraph", "content": content}]})
    return {"type": "bulletList", "content": li}

def adf_code_block(text, language="python"):
    """Create a fenced code block."""
    return {"type": "codeBlock", "attrs": {"language": language},
            "content": [{"type": "text", "text": text}]}

def adf_table(headers, rows):
    """Create a table. headers and rows are lists of strings."""
    header_row = {"type": "tableRow", "content": [
        {"type": "tableHeader", "content": [adf_paragraph(adf_text(h))]}
        for h in headers
    ]}
    data_rows = [{"type": "tableRow", "content": [
        {"type": "tableCell", "content": [adf_paragraph(adf_text(cell))]}
        for cell in row
    ]} for row in rows]
    return {"type": "table", "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
            "content": [header_row] + data_rows}

def adf_task_list(*items):
    """Create a taskList for acceptance criteria.
    items: list of strings or lists of inline nodes.
    """
    tasks = []
    for i, item in enumerate(items, 1):
        if isinstance(item, str):
            content = [adf_text(item)]
        else:
            content = item
        tasks.append({
            "type": "taskItem",
            "attrs": {"localId": f"ac-{i}", "state": "TODO"},
            "content": content
        })
    return {"type": "taskList", "attrs": {"localId": str(uuid.uuid4())[:8]},
            "content": tasks}

def adf_gherkin_ac(given, when, then):
    """Create a Gherkin-formatted acceptance criterion with bold keywords."""
    return [
        adf_text("Given ", bold=True), adf_text(given + ", "),
        adf_text("When ", bold=True), adf_text(when + ", "),
        adf_text("Then ", bold=True), adf_text(then),
    ]
```

### Usage Example

```python
description = adf_doc(
    adf_heading("Context"),
    adf_paragraph(
        adf_text("The agent registry ("),
        adf_text("acp-agent-registry", code=True),
        adf_text(") needs a lifecycle state machine.")
    ),
    adf_heading("Scope"),
    adf_bullet_list(
        [adf_text("Implement state enum in "), adf_text("models.py", code=True)],
        [adf_text("Add "), adf_text("POST /agents/{id}/transition", code=True), adf_text(" endpoint")],
        "Reject invalid transitions with 409 Conflict",
    ),
    adf_heading("Technical Approach"),
    adf_code_block(
        'VALID_TRANSITIONS = {\n'
        '    "pending_review": ["approved", "rejected"],\n'
        '    "approved": ["active", "suspended"],\n'
        '}',
        language="python"
    ),
    adf_heading("Files Affected"),
    adf_table(
        ["File", "Change", "Reason"],
        [
            ["src/acp_agent_registry/models.py", "Modify", "Add state enum"],
            ["src/acp_agent_registry/routes.py", "Modify", "Add transition endpoint"],
            ["tests/unit/test_lifecycle.py", "New", "State machine tests"],
        ]
    ),
)

acceptance_criteria = adf_doc(
    adf_task_list(
        adf_gherkin_ac(
            "an agent in approved state",
            "POST /agents/{id}/transition with target=active",
            "agent transitions to active with 200 response"
        ),
        adf_gherkin_ac(
            "an agent in pending_review state",
            "transition to active is attempted",
            "409 Conflict returned with valid transitions"
        ),
        "Unit tests pass with ≥90% coverage on the state machine module",
    )
)

payload = {
    "fields": {
        "project": {"key": "EACPP"},
        "issuetype": {"name": "Sub-task"},
        "parent": {"key": "EACPP-37"},
        "summary": "Implement lifecycle state machine for agent registry",
        "description": description,
        "customfield_10029": acceptance_criteria,
        "labels": ["epic:agent-registry", "lifecycle", "state-machine"],
        "priority": {"name": "High"},
    }
}
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| AC in description field | AC goes in `customfield_10029` only — never in description |
| AC heading in AC field | Don't add "Acceptance Criteria" heading — field label provides it |
| Plain text AC (no checkboxes) | Use `taskList`/`taskItem` nodes, not `bulletList` |
| `customfield_10014` for parent | EACPP Sub-tasks use `parent.key`, not `customfield_10014` |
| Team field as object | `customfield_10001` takes a plain string ID, not `{"id": "..."}` |
| Using v2 API | Always use v3 (`/rest/api/3/issue`) for ADF support |
| Search via old endpoint | `/rest/api/2/search` is gone — use `POST /rest/api/3/search/jql` |
| Inline code as plain text | Wrap file paths and function names in `code` marks |
| Missing `epic:` label | Every sub-task needs `epic:{component}` for board visibility |

---

## Issue Link Direction (Blocks)

When creating dependency links, the direction is **counterintuitive**:

```json
{
  "type": {"name": "Blocks"},
  "inwardIssue": {"key": "EACPP-100"},
  "outwardIssue": {"key": "EACPP-101"}
}
```

This means **EACPP-100 blocks EACPP-101**:
- `inwardIssue` = the **blocker**
- `outwardIssue` = the **blocked** ticket

---

## Adding Comments (ADF)

```python
comment_payload = {
    "body": adf_doc(
        adf_paragraph(
            adf_text("Implementation complete. PR: "),
            adf_text("#42", link="https://bitbucket.sunlifecorp.com/..."),
        ),
        adf_bullet_list(
            "State machine with 5 states and validated transitions",
            "93% test coverage on lifecycle module",
            "Deployed to dev — verified via /agents/{id}/transition endpoint",
        ),
    )
}
# POST /rest/api/3/issue/EACPP-84/comment
```
