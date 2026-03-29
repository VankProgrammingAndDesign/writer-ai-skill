# Writer AI Skill for Claude Code

Two Claude Code skills for building and importing Writer AI playbooks. `writer.md` generates playbook `.zip` files from natural language descriptions. `import-playbook.md` pushes them into Writer Agent without opening a browser.

## Prerequisites

- Claude Code installed
- Writer AI account with Research Writer access
- Python 3 (required for `import-playbook` only)

## Installation

```bash
git clone https://github.com/VankProgrammingAndDesign/writer-ai-skill.git
cp writer-ai-skill/commands/writer.md ~/.claude/commands/
cp writer-ai-skill/commands/import-playbook.md ~/.claude/commands/   # optional
```

See [CLAUDE-CODE-INSTALL.md](CLAUDE-CODE-INSTALL.md) for the full walkthrough, or [INSTALL.md](INSTALL.md) for the detailed guide with Windows steps and troubleshooting.

## Usage

| Skill | Trigger | What it does |
|---|---|---|
| `/writer` | `/writer build a playbook that...` | Generates a playbook `.zip` from your description |
| `/writer` (edit) | `/writer update my_playbook.zip to add...` | Loads and edits an existing playbook |
| `/import-playbook` | `/import-playbook my_playbook.zip` | Imports the zip into Writer Agent |

## Example Prompts

**Build a new playbook:**
> `/writer build a playbook that searches the web for competitor pricing and outputs a summary table`

**Add a step to an existing playbook:**
> `/writer update invoice_processor.zip to add an email notification step after the data extraction phase`

**Import after building:**
> `/import-playbook invoice_processor.zip`

**Edit and re-import:**
> `/writer update quote_builder.zip to replace the PLACEHOLDER step, the AZURE_API connector is now live`

## How It Works

### CREATE vs EDIT mode

The `/writer` skill detects which mode to use based on your prompt:
- Reference an existing `.zip` file → EDIT mode: loads the zip, parses the manifest, applies changes
- No zip reference → CREATE mode: gathers requirements, builds the template, packages a new zip

### Manifest format

Writer playbooks are `.zip` files containing a single `manifest.json`. The manifest defines the workflow name, description, a Markdown template with inline variable/connector tags, and arrays for variables, connectors, and workspace file references.

### Connector pattern

Every connector call in a playbook template requires two sub-steps: a `WRITER_SEARCH_INTEGRATIONS` call to locate the function, followed by a `WRITER_EXECUTE_FUNCTION` call to run it. The skill enforces this pattern automatically.

### Token script

`import-playbook` retrieves your Writer session token from your browser's cookie store (Edge or Chrome). You must be logged into `app.writer.com` for the token extraction to work. See [INSTALL.md](INSTALL.md) for setup details.

## Configuration (import-playbook)

Before using `/import-playbook`, edit `~/.claude/commands/import-playbook.md` and replace three placeholders:

| Placeholder | Replace with |
|---|---|
| `YOUR_ORG_ID` | Your Writer organization ID. Find it at Settings > API |
| `YOUR_TEAM_ID` | Your Writer team ID. Visible in the URL when logged in |
| `/path/to/get_writer_token.py` | Absolute path to `get_writer_token.py` from this repo |

## License

MIT
