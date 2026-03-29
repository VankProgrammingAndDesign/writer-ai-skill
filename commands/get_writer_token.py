#!/usr/bin/env python3
"""Extract Writer qToken from browser cookies. Run when token expires.

Requires the user to be logged into app.writer.com in Edge or Chrome.

Usage:
    python3 get_writer_token.py

To use Chrome instead of Edge, replace browser_cookie3.edge with browser_cookie3.chrome.
"""
import browser_cookie3
import sys

# Change to browser_cookie3.chrome(...) if using Chrome
cj = browser_cookie3.edge(domain_name='app.writer.com')

for c in cj:
    if c.name == 'qToken' and 'writer.com' in c.domain:
        print(c.value)
        sys.exit(0)

print(
    "ERROR: qToken not found — make sure you're logged into app.writer.com in Edge",
    file=sys.stderr
)
sys.exit(1)
