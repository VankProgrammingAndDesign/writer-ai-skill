# Installation Guide

Step-by-step setup for the Writer AI skill with Claude Code.

## Prerequisites

Check that you have the required tools before starting.

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

**Writer AI access:**
- A Writer AI account with Research Writer enabled
- Your organization ID (find it at Settings > API)
- Your team ID (visible in the URL when logged in)

---

## Step 1: Clone the repository

```bash
git clone https://github.com/VankProgrammingAndDesign/writer-ai-skill.git
cd writer-ai-skill
```

---

## Step 2: Create the Claude Code commands folder (if it does not exist)

**macOS / Linux:**
```bash
mkdir -p ~/.claude/commands
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\commands"
```

---

## Step 3: Copy the skills

**writer.md only** (no import needed):

**macOS / Linux:**
```bash
cp commands/writer.md ~/.claude/commands/
```

**Windows (PowerShell):**
```powershell
Copy-Item commands\writer.md "$env:USERPROFILE\.claude\commands\"
```

**Both skills** (writer + import-playbook):

**macOS / Linux:**
```bash
cp commands/writer.md ~/.claude/commands/
cp commands/import-playbook.md ~/.claude/commands/
```

**Windows (PowerShell):**
```powershell
Copy-Item commands\writer.md "$env:USERPROFILE\.claude\commands\"
Copy-Item commands\import-playbook.md "$env:USERPROFILE\.claude\commands\"
```

---

## Step 4: Set up the token script (import-playbook only)

The `import-playbook` skill uses `get_writer_token.py` to read your Writer session token from your browser's cookie store. Copy it to a permanent location:

**macOS / Linux:**
```bash
cp commands/get_writer_token.py ~/scripts/get_writer_token.py
```

Or any other permanent path. You will reference it in Step 5.

Install the dependency:
```bash
pip install browser_cookie3
```

---

## Step 5: Configure import-playbook (import-playbook only)

Open `~/.claude/commands/import-playbook.md` in a text editor. Find and replace three placeholders:

**YOUR_ORG_ID**
Your Writer organization ID. Find it at: Settings > API > Organization ID.

**YOUR_TEAM_ID**
Your Writer team ID. Find it in the URL when you are logged in:
```
https://app.writer.com/organization/123456/team/789012/writer-agent/...
                                     ^^^^^^       ^^^^^^
                                     ORG_ID       TEAM_ID
```

**/path/to/get_writer_token.py**
The absolute path to where you copied `get_writer_token.py` in Step 4. Example: `/Users/yourname/scripts/get_writer_token.py`

After editing, the Step 2 command block in `import-playbook.md` should look like:
```bash
TOKEN=$(python3 /Users/yourname/scripts/get_writer_token.py) && \
curl -s -X POST \
  "https://app.writer.com/api/writer-agent/organization/123456/team/789012/workflows/import" \
  -H "Cookie: qToken=$TOKEN" \
  -F "file=@ZIP_ABSOLUTE_PATH"
```

---

## Step 6: Verify

Open a new Claude Code session:
```bash
claude
```

For the writer skill, type `/writer`. Claude should respond asking for playbook details.

For import-playbook, make sure you are logged into `app.writer.com` in Edge or Chrome, then run:
```
/import-playbook my_playbook.zip
```

---

## Troubleshooting

**`/writer` skill not found**
The file is not in the right folder. Check:
```bash
ls ~/.claude/commands/
```
Copy `writer.md` there if it is missing.

**`qToken not found` from get_writer_token.py**
You are not logged into `app.writer.com`, or the script is using the wrong browser. Open `get_writer_token.py` and change `browser_cookie3.edge` to `browser_cookie3.chrome` if you use Chrome.

**`ModuleNotFoundError: No module named 'browser_cookie3'`**
Run `pip install browser_cookie3` and try again. If you use a virtual environment, make sure it is active when running the script.

**Import returns 401**
Your Writer session token expired. Log back into `app.writer.com` in your browser, then re-run the import.

**Import returns 403**
The org ID or team ID in `import-playbook.md` does not match your Writer account. Re-check both values at Settings > API.

**Windows: path to get_writer_token.py**
Use forward slashes or escape backslashes in the path inside `import-playbook.md`. Example:
```
C:/Users/yourname/scripts/get_writer_token.py
```

**Skills not appearing after copying**
Claude Code loads skills from `~/.claude/commands/` (macOS/Linux) or `%USERPROFILE%\.claude\commands\` (Windows). Confirm the files landed in the correct location. No restart is needed. Skills load per session.
