#!/usr/bin/env python3
"""Create AgilePlace Feature cards for all 18 ACP spec components.

Cards sync to Jira as Epics via Planview Hub. This populates the new
spec-driven epic board aligned to D0 Discovery.

Usage:
    set -a && source .github/.env && set +a
    python3 scripts/create_spec_epics.py
"""

import json
import os
import ssl
import subprocess
import sys
import time
import yaml
from pathlib import Path

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)


AGILEPLACE_BASE_URL = os.environ["AGILEPLACE_BASE_URL"]
AGILEPLACE_API_TOKEN = os.environ["AGILEPLACE_API_TOKEN"]
AGILEPLACE_BOARD_ID = os.environ["AGILEPLACE_BOARD_ID"]

# Card type: Feature (syncs to Jira Epic)
FEATURE_TYPE_ID = "2446054319"
# Lane: Funnel (Intake & Backlog → Funnel)
FUNNEL_LANE_ID = "2446105393"


def agileplace_api(method, endpoint, payload=None):
    """Call AgilePlace API via curl (avoids SSL issues)."""
    url = f"{AGILEPLACE_BASE_URL}{endpoint}"
    cmd = [
        "curl", "-sk", "-X", method,
        "-H", f"Authorization: Bearer {AGILEPLACE_API_TOKEN}",
        "-H", "Content-Type: application/json",
        url,
    ]
    if payload:
        cmd.extend(["-d", json.dumps(payload)])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: curl failed: {result.stderr}")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  ERROR: Invalid JSON: {result.stdout[:200]}")
        return None


def create_feature_card(title, description, tags):
    """Create a Feature card in AgilePlace Funnel lane."""
    payload = {
        "title": title,
        "description": description,
        "destination": {"boardId": AGILEPLACE_BOARD_ID, "laneId": FUNNEL_LANE_ID},
        "type": {"id": FEATURE_TYPE_ID},
        "priority": "normal",
        "tags": tags,
    }
    return agileplace_api("POST", "/io/card?returnFullRecord=true", payload)


def get_jira_key(card_id, retries=3, delay=3):
    """Poll for the Jira key that gets synced by Planview Hub."""
    for i in range(retries):
        time.sleep(delay)
        card = agileplace_api("GET", f"/io/card/{card_id}")
        if card:
            custom_id = card.get("customId", {})
            jira_key = custom_id.get("value", "")
            if jira_key:
                return jira_key
    return ""


def main():
    specs_dir = Path("specs")
    results = []

    # Load all spec.yaml files
    components = []
    for spec_yaml in sorted(specs_dir.glob("*/*/spec.yaml")):
        with open(spec_yaml) as f:
            data = yaml.safe_load(f)
        data["_dir"] = spec_yaml.parent.relative_to(specs_dir).as_posix()
        components.append(data)

    print(f"Found {len(components)} components\n")

    for comp in components:
        title = f"[D0] {comp['title']}"
        component_name = comp["component"]
        description = (
            f"<p><strong>Component</strong>: {component_name}</p>"
            f"<p><strong>Gate</strong>: D0 — Discovery</p>"
            f"<p><strong>Repo</strong>: {comp.get('repo', '—')}</p>"
            f"<p>{comp.get('description', '')}</p>"
            f"<p><strong>Spec</strong>: <code>acp-product-specs/specs/{comp['_dir']}/</code></p>"
        )
        tags = ["acp", "spec-driven", f"gate:d0", f"component:{component_name}"]

        print(f"Creating: {title}")
        card = create_feature_card(title, description, tags)

        if card and "id" in card:
            card_id = card["id"]
            print(f"  Card ID: {card_id}")

            # Wait for Jira sync
            jira_key = get_jira_key(card_id)
            if jira_key:
                print(f"  Jira Key: {jira_key}")
            else:
                print(f"  Jira Key: (pending sync)")
                jira_key = ""

            results.append({
                "component": component_name,
                "title": comp["title"],
                "card_id": card_id,
                "jira_key": jira_key,
                "spec_dir": comp["_dir"],
            })
        else:
            print(f"  FAILED to create card")
            results.append({
                "component": component_name,
                "title": comp["title"],
                "card_id": "",
                "jira_key": "",
                "spec_dir": comp["_dir"],
            })

        # Small delay to avoid rate limiting
        time.sleep(2)

    # Summary
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"{'Component':<30} {'Card ID':<15} {'Jira Key':<12}")
    print("-" * 60)
    for r in results:
        print(f"{r['component']:<30} {r['card_id']:<15} {r['jira_key'] or '(pending)':<12}")

    # Save mapping
    mapping_file = Path("specs/epic-mapping.json")
    with open(mapping_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nMapping saved to {mapping_file}")


if __name__ == "__main__":
    main()
