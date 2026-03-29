# FAQ

---

## Writer AI Basics

**What is Writer AI / Research Writer?**
Writer AI is an enterprise LLM platform. Research Writer is the agent workflow product. It lets you build reusable automations called playbooks that run inside Writer's agent environment, with access to connectors, knowledge graphs, and workspace files.

**What is a playbook?**
A playbook is a reusable agent workflow. It has a Markdown template that defines the steps, a set of input variables the user fills in at runtime, and an optional set of connectors (integrations with external APIs or services). Playbooks are distributed as `.zip` files containing a `manifest.json`.

**Do I need a paid Writer account?**
Yes. Research Writer access is required. Check with your organization's Writer admin if you are unsure whether your account includes it.

**What are connectors?**
Connectors are integrations configured in your Writer instance that give the agent access to external APIs or services. Writer includes built-in connectors for Gmail, Slack, Google Sheets, Salesforce, and others. Custom connectors point to your own APIs. Connector IDs are case-sensitive strings like `GMAIL` or `AZURE_FUNCTIONS_API`.

---

## Skills and Claude Code

**What is a Claude Code skill?**
A skill is a Markdown file in `~/.claude/commands/`. When you type `/skill-name` in a Claude Code session, Claude loads that file and follows its instructions. Skills give Claude a repeatable, structured way to perform complex tasks.

**Do both skills need to be installed?**
No. `writer.md` works on its own. It builds and edits playbook zips without importing them. `import-playbook.md` is optional. Install it if you want auto-import via the command line.

**Does this work with Claude Desktop?**
No. Claude Desktop does not support custom skills. These skills require the Claude Code CLI.

**Can I use these skills in any Claude Code project?**
Yes. Files in `~/.claude/commands/` are available in every Claude Code session regardless of working directory.

---

## Configuration

**Where do I find my org ID and team ID?**
Org ID: Settings > API > Organization ID in the Writer web app.
Team ID: visible in the URL when you are logged in. Pattern: `app.writer.com/organization/{ORG_ID}/team/{TEAM_ID}/...`

**What is the token script?**
`get_writer_token.py` reads your Writer session cookie (`qToken`) from your browser's local cookie store using the `browser_cookie3` library. You must be logged into `app.writer.com` in Edge or Chrome for it to work. No credentials are stored or transmitted. The script only reads the cookie from your local machine.

**Do I need to write the token script myself?**
No. The script is included in `commands/get_writer_token.py`. Copy it to a permanent location and reference that path in `import-playbook.md`.

**Can I use an API key instead of the token script?**
Writer's playbook import endpoint uses session cookie auth, not API keys. The token script is the supported approach for command-line import.

**The token script uses Edge. I use Chrome.**
Open `get_writer_token.py` and change `browser_cookie3.edge(...)` to `browser_cookie3.chrome(...)`.

---

## Building Playbooks

**What is CREATE vs EDIT mode?**
The `/writer` skill reads your prompt and picks a mode automatically. If you reference an existing `.zip` file, it opens that file, parses the manifest, and applies your changes (EDIT). If you do not reference a zip, it gathers requirements and builds a new one (CREATE).

**What connector IDs do I use?**
Use the exact IDs as configured in your Writer instance. Find them at Settings > Integrations. Common built-in IDs: `GMAIL`, `SLACK`, `GOOGLE_SHEETS`, `SALESFORCE`, `HUBSPOT`, `NOTION`, `JIRA`. Custom connectors have whatever ID your Writer admin set.

**What is the SEARCH then EXECUTE pattern?**
Every connector call in a playbook template requires two sub-steps: first a `WRITER_SEARCH_INTEGRATIONS` call to find the function, then a `WRITER_EXECUTE_FUNCTION` call to run it. Skipping the search step causes reliability issues in Writer Agent. The `/writer` skill enforces this pattern automatically.

**Can I add stop points for connectors not yet built?**
Yes. During requirements gathering, tell the skill which steps depend on connectors that are not ready. The skill marks those steps as `PLACEHOLDER - DO NOT EXECUTE` with a stop point block above them. Remove the stop point and `PLACEHOLDER` prefix once the connector is live by running `/writer update my_playbook.zip to remove the STOP POINT on step 4, the connector is now built`.

**What file formats can I reference in a playbook?**
Two types: workspace files (files already uploaded to your Writer workspace, referenced with `[w-file](filename.ext)`) and file upload variables (files the user attaches at runtime, referenced with `[w-file-var](Variable_Key)`). Provide exact filenames and workspace paths for workspace files. The skill cannot look these up for you.

**How many steps should a playbook have?**
Each phase should contain 3–8 tasks. A well-structured playbook typically has 4–8 phases. Very small playbooks (1–2 phases) do not benefit much from the playbook format. Very large ones (15+ phases) are hard for Writer Agent to execute reliably.

---

## Importing

**What does `/import-playbook` do exactly?**
It reads the zip path you provide, extracts your Writer session token from your browser's cookie store, and calls the Writer import API with a single `curl` command. On success, it prints the playbook name, ID, and a link to open it in Writer.

**Can I import without the skill?**
Yes. In Writer, go to Research Writer AI > Workflows > Import > Upload ZIP. The skill automates this step.

**The import returns 401.**
Your session token expired. Log back into `app.writer.com` in your browser and re-run the import.

**The import returns 400 with "corrupted".**
The zip file is not valid. Verify it:
```bash
python3 -c "import zipfile; zipfile.ZipFile('my_playbook.zip').namelist()"
```
If this errors, the zip was not built correctly. Re-run `/writer` to regenerate it.

**The import succeeded but the playbook does not appear in Writer.**
Check that the team ID in `import-playbook.md` matches the team where you are looking. Playbooks go to the specific team referenced in the import URL.
