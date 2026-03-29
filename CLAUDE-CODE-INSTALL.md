# Claude Code Install Guide

Self-contained setup for the Writer AI skill in Claude Code. All commands are here with no external links required.

## Prerequisites

Check that these are installed before starting.

**Claude Code:**
```bash
claude --version
```
If not installed, follow the [Claude Code installation guide](https://docs.anthropic.com/en/docs/claude-code).

**Python 3** (required for `import-playbook` only):
```bash
python3 --version
```

**Git:**
```bash
git --version
```

---

## Step 1: Clone the repository

```bash
git clone https://github.com/VankProgrammingAndDesign/writer-ai-skill.git
```

---

## Step 2: Copy skills to Claude Code

**macOS / Linux:**
```bash
cp writer-ai-skill/commands/writer.md ~/.claude/commands/
```

For `import-playbook` (optional, only needed if you want auto-import):
```bash
cp writer-ai-skill/commands/import-playbook.md ~/.claude/commands/
cp writer-ai-skill/commands/get_writer_token.py /path/to/your/scripts/get_writer_token.py
```

**Windows (PowerShell):**
```powershell
Copy-Item writer-ai-skill\commands\writer.md "$env:USERPROFILE\.claude\commands\"
Copy-Item writer-ai-skill\commands\import-playbook.md "$env:USERPROFILE\.claude\commands\"
Copy-Item writer-ai-skill\commands\get_writer_token.py "C:\path\to\your\scripts\"
```

---

## Step 3: Install the token script dependency (import-playbook only)

```bash
pip install browser_cookie3
```

---

## Step 4: Configure import-playbook (if installed)

Open `~/.claude/commands/import-playbook.md` and replace the three placeholders:

**YOUR_ORG_ID**: find this in Writer at Settings > API > Organization ID.

**YOUR_TEAM_ID**: visible in the URL when you are logged in:
```
app.writer.com/organization/123456/team/789012/...
                             ^^^^^^       ^^^^^^
                             ORG_ID       TEAM_ID
```

**/path/to/get_writer_token.py**: the absolute path where you copied `get_writer_token.py` in Step 2.

Example of the completed Step 2 command block:
```bash
TOKEN=$(python3 /Users/yourname/scripts/get_writer_token.py) && \
curl -s -X POST \
  "https://app.writer.com/api/writer-agent/organization/123456/team/789012/workflows/import" \
  -H "Cookie: qToken=$TOKEN" \
  -F "file=@ZIP_ABSOLUTE_PATH"
```

---

## Step 5: Verify

Open a new Claude Code session:
```bash
claude
```

Type `/writer` and press Enter. Claude should respond asking for playbook details.

For `import-playbook`, make sure you are logged into `app.writer.com` in Edge or Chrome, then try:
```
/import-playbook my_playbook.zip
```

---

## Quick Fixes

**`/writer` skill not found**
The file is not in the commands folder. Run:
```bash
ls ~/.claude/commands/
```
Copy `writer.md` there if it is missing.

**`/import-playbook` returns 401**
Your Writer session token expired. Log back into `app.writer.com` in your browser, then re-run the import.

**`qToken not found` error from get_writer_token.py**
You are not logged in at `app.writer.com`, or the script is looking at the wrong browser. Open `get_writer_token.py` and change `browser_cookie3.edge` to `browser_cookie3.chrome` if you use Chrome.

**Wrong org ID or team ID**
If import succeeds but the playbook appears in the wrong team, re-check both IDs in `~/.claude/commands/import-playbook.md`.
