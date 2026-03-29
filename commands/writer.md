---
description: Build or edit a Research Writer AI playbook zip file. Use when the user wants to create, build, generate, export, update, or modify a Writer playbook, workflow, or automation. Triggers on phrases like "make a playbook that...", "create a Writer workflow for...", "build a Writer workflow", "update playbook.zip to...", "edit this playbook to add...", "add a step to playbook.zip", or any request to create or modify an agent/workflow in Writer AI.
argument-hint: <natural language description — or reference an existing .zip to edit it>
allowed-tools: Write, Bash, Read
---

# Writer Playbook Builder

Create a new Research Writer AI playbook, or load and edit an existing one. Output is a `.zip` file for direct import.

## User's Request

$ARGUMENTS

---

## Step 0: Detect Mode

Read `$ARGUMENTS` and determine which mode applies:

**EDIT mode** — if the request references an existing `.zip` file by name or path (e.g., "update playbook1.zip", "edit the New Quote Processing zip", "add a step to my_workflow.zip"). Proceed to **Edit Flow**.

**CREATE mode** — if no existing zip is referenced. Proceed to **Create Flow**.

If `$ARGUMENTS` is empty, ask the user whether they want to create a new playbook or edit an existing one, and what they want to do.

---

## EDIT FLOW

### Edit Phase 1: Load the Existing Playbook

**Step 1A**: Locate the zip file.

Check these locations in order:
1. The exact path or filename given in `$ARGUMENTS`
2. The current working directory (`pwd`)
3. Common subdirectories: `examples/`, `output/`, `playbooks/`

Use Bash to find the file if needed:
```bash
find . -name "*.zip" | head -20
```

If multiple zip files exist and the user was vague, list them and ask which one to edit.

**Step 1B**: Extract and parse the manifest.

```bash
python3 - << 'PYEOF'
import zipfile, json, sys

zip_path = "PATH_TO_ZIP"
with zipfile.ZipFile(zip_path) as z:
    with z.open("manifest.json") as f:
        m = json.load(f)

w = m["workflow"]
print("=== CURRENT PLAYBOOK ===")
print(f"Name: {w['name']}")
print(f"Description: {w.get('description', '')}")
print(f"Variables ({len(w['variables'])}):")
for v in w["variables"]:
    req = "required" if v.get("required") else "optional"
    vtype = v.get("type", "text")
    print(f"  - {v['key']} ({vtype}, {req}): {v.get('description', '')}")
print(f"Connectors ({len(w['connectors'])}): {', '.join(w['connectors'])}")
files = m.get("files", [])
print(f"Files ({len(files)}): {', '.join(f['name'] for f in files) if files else 'none'}")

# Count steps by counting ### headings
import re
steps = re.findall(r'^###\s+\d+', w['template'], re.MULTILINE)
print(f"Template steps: ~{len(steps)}")
print(f"Template length: {len(w['template'])} chars")
PYEOF
```

**Step 1C**: Also read the raw template so you can work with it:
```bash
python3 -c "
import zipfile, json
with zipfile.ZipFile('PATH_TO_ZIP') as z:
    m = json.load(z.open('manifest.json'))
print(m['workflow']['template'])
"
```

### Edit Phase 2: Gather Changes

Display a summary of the loaded playbook to the user, then send **one single message** asking all of the following. Do not ask one at a time:

---

I've loaded **[Playbook Name]**. Here's what it currently contains:

- **Variables ([N]):** [list]
- **Connectors ([N]):** [list]
- **Files ([N]):** [list or "none"]
- **Steps:** ~[N] steps

To apply your changes, I need a few details:

**1. What specifically needs to change?**
Be as precise as possible. For example:
- "Add a new step after step 3 that calls the Weather API to get current conditions"
- "Add a new variable called `Location` (required)"
- "Remove the STOP POINT on step 5 — the connector is now built"
- "Replace the Azure Document Intelligence steps with calls to our new WEATHER_API connector"
- "Update the pricing formula in step 7 to use a flat fee instead of margin percentage"

**2. New connector IDs** (if any)
If your changes involve new connectors, provide their exact IDs as configured in Writer (e.g., `WEATHER_API`). If the connector already exists in the playbook, just reference it by name.

**3. New variables** (if any)
If your changes require new input variables: name (underscores), type (text or file upload), required (yes/no), description.

**4. New workspace files** (if any)
If your changes reference files that already exist in the workspace, provide their exact filenames and paths.

**5. Output filename**
Should I overwrite `[original filename]`, or save as a new file (e.g., `[original-name]_v2.zip`)?

---

Wait for the user's answers before applying changes.

### Edit Phase 3: Apply Changes

Load the full manifest in memory. Apply the requested changes:

**For template changes:**
- Parse the existing template Markdown as a string
- Insert, modify, or remove the relevant sections
- Apply all template rules from the Create flow (connector pattern, stop points, etc.) to any new or modified steps
- Renumber steps if steps were inserted or removed
- Re-run all sync checks (variables, file-vars, connectors, workspace files) against the full updated template

**For variable changes:**
- Add new variable objects to the `variables` array
  - Text inputs: `"type": "text"`
  - File uploads: `"type": "file"`
- Remove variables that are no longer referenced in the template
- Never remove a variable that still has `[w-var](Key)` or `[w-file-var](Key)` references in the template

**For connector changes:**
- Add new connector IDs to the `connectors` array
- Remove connector IDs that are no longer referenced in the template
- Never remove a connector ID that still has `[w-connector](ID)` references in the template

**For workspace file changes:**
- Add new entries to the `files` array: `{"name": "filename.ext", "path": "/exact/path/in/workspace"}`
- Remove entries for files no longer referenced with `[w-file](filename.ext)` in the template

**Metadata preservation:**
- Keep the original `source_workflow_id` and `source_agent_id` from the loaded manifest (these tie the playbook to the original workflow in Writer)
- Update `exported_at` to the current timestamp (fresh export)

### Edit Phase 4: Package

Follow the same packaging steps as the Create flow (Phase 4), with these differences:

- Use the output filename the user chose (overwrite original or new name)
- If overwriting, use the same path as the source zip
- The Python script reads from `/tmp/writer_<slug>_manifest.json` (written by the Write tool) and writes the zip to the chosen output path

```bash
python3 - << 'PYEOF'
import zipfile, json, uuid
from datetime import datetime, timezone

slug = "SLUG"
source_zip = "SOURCE_ZIP_PATH"
output_zip = "OUTPUT_ZIP_PATH"  # same as source if overwriting

with open(f"/tmp/writer_{slug}_manifest.json") as f:
    m = json.load(f)

# Update export timestamp only — preserve original workflow/agent IDs
m["metadata"]["exported_at"] = datetime.now(timezone.utc).isoformat()

with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("manifest.json", json.dumps(m, indent=2, ensure_ascii=False))

print(f"Saved: {output_zip}")
PYEOF
```

### Edit Phase 5: Confirm

Report what changed:

```
Playbook updated: /absolute/path/to/<file>.zip

  Name:       [Playbook Name]
  Variables:  [N] — [list] ([+X added, -Y removed] if changed)
  Connectors: [N] — [list] ([+X added, -Y removed] if changed)
  Files:      [N] — [list] ([+X added, -Y removed] if changed)
  Steps:      [N total] ([M placeholders])

Changes applied:
  - [Brief bullet for each change made]

To import: Research Writer AI > Workflows > Import > Upload ZIP
```

---

## CREATE FLOW

### Create Phase 1: Gather Requirements

Send **one single message** with all clarifying questions — do not ask them one at a time:

---

I need a few details to build your playbook. Please answer all of these in one reply:

**1. Playbook name**
What should this workflow be called? (2–6 words, e.g., "Azure Invoice Processor")

**2. Description**
One to two sentences describing what the playbook does. Use third-person present tense starting with an action verb — e.g., "Processes vendor quote files and creates records in your target system." Writer shows this description in the Playbooks library.

**3. Step-by-step logic**
Describe the sequence of steps this agent should perform. Include:
- What inputs flow in at each step
- Which connector functions get called (and what params they receive)
- Any branching logic (e.g., "if PDF do X, if Excel do Y")
- Any async polling steps (e.g., "wait for result, retry up to 5 times")
- What gets written to a tracking file between steps (for API-heavy workflows)

**4. Input variables**
What values does the user provide at runtime? For each variable provide:
- Name (underscores, no spaces — e.g., `File_URL`)
- Type: **text** (typed value) or **file upload** (user attaches a file)
- Required? (yes/no)
- Short description

**5. Workspace files** (if any)
Are there files that already exist in the workspace that the playbook should reference (e.g., templates, style guides, data files)? If so, provide their exact filenames and paths.

**6. Connector IDs**
What connectors does this workflow use? Provide the **exact IDs** as configured in your Writer instance (e.g., `AZURE_FUNCTIONS_API`, `CALLBACK_API`). If you have a callback/logging connector for status updates, include that too.

If you're using a common service (Gmail, Slack, Google Sheets, etc.), see the standard IDs below — you can use these directly without configuring a custom connector:
- `GMAIL`, `GOOGLE_CALENDAR`, `GOOGLE_SHEETS`, `GOOGLE_DRIVE`
- `SLACK`, `MICROSOFT_OUTLOOK`, `MICROSOFT_TEAMS`
- `SALESFORCE`, `HUBSPOT`, `NOTION`, `AIRTABLE`, `JIRA`, `ASANA`, `TRELLO`

**7. Stop points / placeholders**
Are any steps dependent on connectors not yet built? If so, which steps should be marked **DO NOT EXECUTE** / PLACEHOLDER?

**8. Presentation output?**
Will this playbook produce a slide deck or presentation as its deliverable? (yes/no — affects a feature flag)

---

Wait for the user's answers before continuing.

### Create Phase 2: Build the Template Markdown

Using the answers, construct the full playbook template as a Markdown string. Apply all of these rules:

#### Rule: Phase Naming

- Use numbered headings: `### 1. Phase Title`, `### 2. Next Phase`, etc.
- End with `### Completion`
- **Never** prefix titles with "Phase", "Step", or "Part" (e.g., ❌ "Phase 1: Setup", ✅ "Setup & Planning")
- Each phase should have **3–8 tasks** — not too granular, not too vague

#### Rule: Task Writing Style

- Use imperative voice starting with action verbs: "Fetch", "Extract", "Calculate", "Create", "Send"
- Be specific about outcomes, not implementation internals
- Use natural language in template tasks — write "Search the web for recent trends" not `web_search`. Exception: `WRITER_SEARCH_INTEGRATIONS` and `WRITER_EXECUTE_FUNCTION` are permitted in connector call steps.
- Inline tags (`[w-var]`, `[w-file-var]`, `[w-file]`, `[w-connector]`) go directly in the task sentence

#### Rule: Initialization Step (for API-heavy workflows)

For workflows that make multiple connector/API calls, step 1 should:
1. Create a tracker JSON object (shown as a code block) with an `input` section containing one key per variable and a `results` section
2. Seed all variable values into the tracker using `[w-var](Key)` syntax
3. Save the tracker to `<slug>_tracker.json` in the workspace

Example:
```
### 1. Initialization & Setup

- Create a JSON tracking object with the following structure:

  ```json
  {
      "processingStatus": "",
      "correlationId": "",
      "input": {
          "variableOne": "",
          "variableTwo": 0
      },
      "results": {}
  }
  ```

- Seed these values:
  variableOne: "[w-var](Variable_One)",
  variableTwo: [w-var](Variable_Two)

- Save this JSON object to the workspace as `my_playbook_tracker.json`
```

For simpler workflows (no connector API calls), skip the tracker and begin directly with the first logical phase.

#### Rule: Connector Call Pattern (always two sub-steps, never skip)

Every connector function call must follow this exact two-step pattern:

```
- **CRITICAL**: First search for the [FunctionName] function from the [w-connector](CONNECTOR_ID) tool using WRITER_SEARCH_INTEGRATIONS
- Then execute the found function using WRITER_EXECUTE_FUNCTION with parameters: [describe params]
- Save the result to `<slug>_tracker.json`
```

Never call `WRITER_EXECUTE_FUNCTION` without first calling `WRITER_SEARCH_INTEGRATIONS` for the same function in the same step.

#### Rule: Workspace File References

When the playbook references a file that exists in the workspace, use:
```
- Use [w-file](filename.ext) as the base format for the report
```
Every `[w-file](filename.ext)` reference must have a matching entry in the manifest `files` array.

#### Rule: File Upload Variables

When the user provides a file at runtime (not a pre-existing workspace file), use:
```
- Extract data from [w-file-var](Source_Document)
```
Every `[w-file-var](Key)` reference must have a matching entry in the manifest `variables` array with `"type": "file"`.

#### Rule: Conditional Branching

Use labeled sub-steps for branching:
```
### 3A. [Branch Name]

**Only execute this phase if [condition]**

[instructions...]

### 3B. [Branch Name]

**Only execute this phase if [other condition]**

[instructions...]
```

#### Rule: Async Polling

When a step calls an async API that returns a job URL or status:
```
- Poll for results by calling [function] with the returned URL
- Retry up to 5 times with delays between attempts if status is pending
- Fail with an error message if all retries are exhausted
```

#### Rule: Callback Logging (if callback connector provided)

If the user provided a callback/logging connector, add this at the end of each major step:
```
- Log step completion status via [w-connector](CALLBACK_CONNECTOR_ID) using WRITER_SEARCH_INTEGRATIONS then WRITER_EXECUTE_FUNCTION with the current step name and status from `<slug>_tracker.json`
```

#### Rule: Stop Points for Placeholder Phases (custom extension)

For any step the user marked as not-yet-implemented, use this block before the step:
```
---

## STOP POINT — [Connector Name] Integration Required

**CRITICAL**: The following phase requires [ConnectorName] which is not yet built. Do NOT proceed beyond this point until the integration is complete.

**Required**: [describe what connector/endpoint is needed]

```

Then write the step itself prefixed with:
```
### N. [Step Name] (PLACEHOLDER — Requires [Connector])

**DO NOT EXECUTE — [Connector] not yet available**
```

#### Rule: Completion Phase (always last)

The final `### Completion` phase must:
1. Describe the final deliverable — what the user receives at the end
2. Confirm what success looks like (1–2 tasks maximum)

For API-heavy workflows, also include:
- Final status report via callback connector (if one exists)
- Attach `<slug>_tracker.json` as a deliverable

### Create Phase 3: Assemble the Manifest

Build the manifest object. Before finalizing, perform these cross-checks:

**Variable sync check**:
- Every `[w-var](Key)` token in the template → must have a matching `variables` entry with `"type": "text"` and the same `key`
- Every `[w-file-var](Key)` token in the template → must have a matching `variables` entry with `"type": "file"` and the same `key`
- Add any missing entries

**Connector sync check**: Every `[w-connector](ID)` token used in the template must appear in the `connectors` array. Deduplicate the list.

**Workspace file sync check**: Every `[w-file](filename.ext)` token in the template must have a matching entry in the `files` array: `{"name": "filename.ext", "path": "/path/in/workspace/filename.ext"}`. If the user did not provide an exact path, use the filename as-is and note it in the confirmation output.

**Placeholder connector rule**: If the user did not provide a connector ID for something, use a descriptive placeholder like `YOUR_AZURE_FUNCTIONS_API` and note it in the confirmation output.

**enabled_features rule**: Set `"enabled_features": ["presentation"]` if the playbook's deliverable is a slide deck or presentation. Otherwise leave as `[]`.

Manifest structure:
```json
{
  "format_version": "1.0",
  "workflow": {
    "name": "<Playbook Name — 2-6 words>",
    "description": "<1-2 sentences, third-person present tense, starts with action verb>",
    "status": "active",
    "template": "<full markdown template as a JSON string>",
    "variables": [
      {
        "key": "Variable_Key",
        "type": "text",
        "label": "Variable_Key",
        "required": true,
        "description": "Short description"
      },
      {
        "key": "File_Upload_Key",
        "type": "file",
        "label": "File_Upload_Key",
        "required": true,
        "description": "Short description"
      }
    ],
    "connectors": ["CONNECTOR_ID_1", "CONNECTOR_ID_2"],
    "connector_profiles": null,
    "knowledge_graphs": [],
    "skills": [],
    "enabled_features": [],
    "generation_data": null,
    "custom_instructions": "",
    "voice_id": null,
    "graph": null
  },
  "files": [
    {"name": "filename.ext", "path": "/path/in/workspace/filename.ext"}
  ],
  "skills": [],
  "metadata": {
    "exported_at": "WILL_BE_INJECTED",
    "source_workflow_id": "WILL_BE_INJECTED",
    "source_agent_id": "WILL_BE_INJECTED",
    "source_organization_id": 0
  }
}
```

Notes:
- `exported_at`, `source_workflow_id`, and `source_agent_id` are injected by the packaging script
- `voice_id`: optional UUID — only set if the user specifies a voice profile (requires calling `list_voices` first to get a valid UUID)
- `files`: use `[]` if no workspace files are referenced

### Create Phase 4: Package as Zip

**Step 1**: Get current working directory
```bash
pwd
```

**Step 2**: Build the slug — take the playbook name, lowercase it, replace spaces with underscores, replace `&` with `and`, remove special characters.

**Step 3**: Write the manifest JSON to a temp file using the Write tool:
- Path: `/tmp/writer_<slug>_manifest.json`

**Step 4**: Run the Python packaging script via Bash (substitute actual `SLUG` and `CWD`):

```bash
python3 - << 'PYEOF'
import zipfile, json, uuid
from datetime import datetime, timezone

slug = "SLUG"
cwd = "CWD"

with open(f"/tmp/writer_{slug}_manifest.json") as f:
    m = json.load(f)

m["metadata"]["exported_at"] = datetime.now(timezone.utc).isoformat()
m["metadata"]["source_workflow_id"] = str(uuid.uuid4())
m["metadata"]["source_agent_id"] = str(uuid.uuid4())

out = f"{cwd}/{slug}.zip"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("manifest.json", json.dumps(m, indent=2, ensure_ascii=False))

print(f"Created: {out}")
PYEOF
```

**Step 5**: Verify the zip:
```bash
python3 -c "import zipfile; z=zipfile.ZipFile('CWD/SLUG.zip'); print(z.namelist())"
```

### Create Phase 5: Confirm

```
Playbook zip created: /absolute/path/to/<slug>.zip

  Name:       [Playbook Name]
  Variables:  [N] — [comma-separated list of keys (with type)]
  Connectors: [N] — [comma-separated list of IDs]
  Files:      [N] — [comma-separated list of filenames, or "none"]
  Steps:      [N total] ([M placeholders])

To import: run `/import-playbook [zip-path]` to auto-import into Writer, or manually via Research Writer AI > Workflows > Import > Upload ZIP
```

If any connector IDs were left as placeholders, add:
```
Note: The following connector IDs are placeholders — update them in Writer after import:
  - YOUR_CONNECTOR_ID → [what this connector should be]
```

If any workspace file paths were not confirmed, add:
```
Note: The following workspace file paths were not verified — confirm they exist before running:
  - [filename.ext] → [path used]
```

---

## Important Rules (Both Modes)

- The `template` field in the manifest is a JSON string — write it as normal text in the manifest object; Python's `json.dumps` handles escaping.
- `key` and `label` in each variable must exactly match the string inside `[w-var](...)` or `[w-file-var](...)` tokens.
- Text input variables use `"type": "text"`; file upload variables use `"type": "file"`.
- Connector IDs are case-sensitive — use them exactly as the user provided.
- `connector_profiles` is always `null`.
- `source_organization_id` is always `0` when building from scratch (preserved from original in edit mode).
- Never invent connector IDs. If not provided, use an obvious placeholder and call it out.
- The zip filename should use the slug format (no spaces).
- In edit mode, never generate new `source_workflow_id` or `source_agent_id` — preserve the originals so Writer can match the existing workflow on import.
- Do NOT use "Phase N:", "Step N:", or "Part N:" prefixes in phase headings — just `### N. Phase Name`.
- Use natural language in template tasks — write "Search the web" not `web_search`. Exception: `WRITER_SEARCH_INTEGRATIONS` and `WRITER_EXECUTE_FUNCTION` are permitted in connector call steps for reliability.
- `[w-connector](WRITER_KNOWLEDGE_GRAPH)` is not a valid connector — knowledge graphs auto-attach; write natural search language instead.
