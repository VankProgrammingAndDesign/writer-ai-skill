---
description: Auto-import a Writer playbook zip into Writer Agent via Edge browser. Use when the user wants to import a .zip playbook file into Writer, or after creating a playbook with the writer skill.
argument-hint: <path-to-playbook.zip>
allowed-tools: Bash
---

# Import Writer Playbook

Imports a playbook ZIP into Writer Agent using a single curl command — no browser tools needed.

## Configuration required before use

Edit this file and replace:
- `YOUR_ORG_ID` — your Writer organization ID (Settings > API > Organization ID)
- `YOUR_TEAM_ID` — your Writer team ID (visible in the URL when logged in: `app.writer.com/organization/{ORG_ID}/team/{TEAM_ID}/...`)
- `/path/to/get_writer_token.py` — absolute path to your Writer token retrieval script

## Zip File to Import

$ARGUMENTS

---

## Step 1: Resolve the zip path

If `$ARGUMENTS` is empty or not a `.zip` file, find zips and ask:
```bash
find . -name "*.zip" | head -20
```

Resolve the absolute path:
```bash
realpath "$ZIP_PATH"
```

---

## Step 2: Get auth token and import in one command

```bash
TOKEN=$(python3 /path/to/get_writer_token.py) && \
curl -s -X POST \
  "https://app.writer.com/api/writer-agent/organization/YOUR_ORG_ID/team/YOUR_TEAM_ID/workflows/import" \
  -H "Cookie: qToken=$TOKEN" \
  -F "file=@ZIP_ABSOLUTE_PATH"
```

---

## Step 3: Handle the result

Parse the JSON response:

- **`"name"` present + `"id"` present** → success. Report:
  ```
  Imported: <name>
    ID: <id>
    → https://app.writer.com/organization/YOUR_ORG_ID/team/YOUR_TEAM_ID/writer-agent/playbooks
  ```

- **`"code": "UNAUTHORIZED"` or HTTP 401/403** → token expired. Refresh it:
  ```bash
  python3 /path/to/get_writer_token.py > ~/.writer_token
  ```
  Then re-run Step 2.

- **`"corrupted"` or 400** → zip file issue. Verify the file with:
  ```bash
  python3 -c "import zipfile; zipfile.ZipFile('ZIP_PATH').namelist()"
  ```

- **Any other error** → show full response to user.
