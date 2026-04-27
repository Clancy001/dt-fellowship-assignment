#!/usr/bin/env python3
"""
Daily Reflection Tree — CLI Agent
Walks reflection-tree.json deterministically. No LLM calls at runtime.

Usage:
    python agent.py
    python agent.py --tree ../tree/reflection-tree.json

The agent:
  - Loads the tree from the JSON data file (not hardcoded)
  - Walks each node by type
  - Branches deterministically based on answers and accumulated signals
  - Interpolates earlier answers into reflection/question text
  - Produces a personalised summary at the end
"""

import json
import sys
import os
import textwrap
from pathlib import Path

# ── Utilities ──────────────────────────────────────────────────────────────────

WIDTH = 60

def hr():
    print("\n" + "─" * WIDTH + "\n")

def wrap(text, indent=0):
    prefix = " " * indent
    for line in text.split("\n"):
        if line.strip() == "":
            print()
        else:
            for wrapped in textwrap.wrap(line, WIDTH - indent):
                print(prefix + wrapped)

def header(title):
    print("\n" + "═" * WIDTH)
    print(f"  {title}")
    print("═" * WIDTH + "\n")

# ── Tree Loading ───────────────────────────────────────────────────────────────

def load_tree(filepath: Path) -> dict:
    """Load the JSON tree and index nodes by id."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {node["id"]: node for node in data["nodes"]}

# ── State Management ───────────────────────────────────────────────────────────

def apply_signal(signal: str, state: dict):
    """Tally a signal into state. Format: 'axis1:internal'"""
    if not signal:
        return
    parts = signal.split(":")
    if len(parts) == 2:
        axis_key, pole = parts
        axes = state.setdefault("axes", {})
        axis = axes.setdefault(axis_key, {})
        axis[pole] = axis.get(pole, 0) + 1

def get_dominant(axis_key: str, state: dict) -> str | None:
    """Return the dominant pole for a given axis, or None if no signals."""
    axis_data = state.get("axes", {}).get(axis_key, {})
    if not axis_data:
        return None
    return max(axis_data, key=axis_data.get)

# ── Condition Evaluation ───────────────────────────────────────────────────────

def evaluate_condition(condition: str, state: dict) -> bool:
    """
    Evaluate a routing condition string against current state.
    Supported formats:
      "NODE_ID.answer IN [Val1, Val2]"
      "NODE_ID.answer == Val"
      "axisN.dominant == pole"
    """
    cond = condition.strip()

    # axis1.dominant == internal
    if ".dominant ==" in cond:
        left, right = cond.split(".dominant ==")
        axis_key = left.strip()
        expected = right.strip()
        return get_dominant(axis_key, state) == expected

    # A1_OPEN.answer IN [Productive, Mixed]
    if ".answer IN" in cond:
        left, right = cond.split(".answer IN")
        node_id = left.strip()
        values_str = right.strip().strip("[]")
        values = [v.strip() for v in values_str.split(",")]
        answer = state.get("answers", {}).get(node_id, "")
        return answer in values

    # A3_OPEN.answer == A
    if ".answer ==" in cond:
        left, right = cond.split(".answer ==")
        node_id = left.strip()
        expected = right.strip()
        answer = state.get("answers", {}).get(node_id, "")
        return answer == expected

    return False

# ── Text Interpolation ─────────────────────────────────────────────────────────

def interpolate(text: str, state: dict) -> str:
    """Replace {NODE_ID.answer} placeholders with stored answers."""
    if not text:
        return text
    for node_id, answer_value in state.get("answers", {}).items():
        # Store display label, not raw value
        placeholder = "{" + node_id + ".answer}"
        display = state.get("answer_labels", {}).get(node_id, answer_value)
        text = text.replace(placeholder, display)
    return text

# ── Summary Builder ────────────────────────────────────────────────────────────

def build_summary(node: dict, state: dict) -> str:
    template = node["template"]
    labels   = node["labels"]

    def pick(axis_key, options):
        dominant = get_dominant(axis_key, state)
        if dominant is None:
            dominant = list(options.keys())[0]
        return options.get(dominant, "")

    text = template
    text = text.replace("{axis1_label}", pick("axis1", labels["axis1"]))
    text = text.replace("{axis2_label}", pick("axis2", labels["axis2"]))
    text = text.replace("{axis3_label}", pick("axis3", labels["axis3"]))
    return text

# ── Node Handlers ──────────────────────────────────────────────────────────────

def handle_start(node: dict, state: dict) -> str:
    wrap(node["text"])
    input("\n  [Press Enter to begin...]")
    hr()
    return node.get("next")

def handle_question(node: dict, state: dict) -> str:
    text = interpolate(node["text"], state)

    # Print axis label if present
    if node.get("axis"):
        axis_names = {
            1: "AXIS 1 — LOCUS",
            2: "AXIS 2 — ORIENTATION",
            3: "AXIS 3 — RADIUS"
        }
        print(f"[ {axis_names.get(node['axis'], '')} ]\n")

    wrap(text)
    print()

    options = node["options"]
    for i, opt in enumerate(options, 1):
        wrap(f"{i}. {opt['label']}", indent=3)

    while True:
        try:
            raw = input(f"\n  Your choice (1–{len(options)}): ").strip()
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                selected = options[idx]
                node_id = node["id"]
                state.setdefault("answers", {})[node_id] = selected["value"]
                state.setdefault("answer_labels", {})[node_id] = selected["label"]
                if selected.get("signal"):
                    apply_signal(selected["signal"], state)
                print(f"\n  ✓ Noted: {selected['label']}")
                break
            else:
                print(f"  Please enter a number between 1 and {len(options)}.")
        except (ValueError, KeyboardInterrupt):
            print(f"  Please enter a number between 1 and {len(options)}.")

    hr()
    return node.get("next")

def handle_decision(node: dict, state: dict) -> str:
    for route in node.get("routes", []):
        if evaluate_condition(route["condition"], state):
            return route["target"]
    # Fallback: return first route target if no condition matches
    routes = node.get("routes", [])
    return routes[0]["target"] if routes else None

def handle_reflection(node: dict, state: dict) -> str:
    text = interpolate(node["text"], state)
    print("  💭\n")
    wrap(text, indent=2)
    input("\n  [Press Enter to continue...]")
    hr()
    return node.get("next")

def handle_bridge(node: dict, state: dict) -> str:
    print("  →  ", end="")
    wrap(node["text"])
    input("\n  [Press Enter...]")
    hr()
    return node.get("next")

def handle_summary(node: dict, state: dict) -> str:
    print("  ─── YOUR REFLECTION SUMMARY ───\n")
    text = build_summary(node, state)
    wrap(text, indent=2)

    # Print tally (for transparency / debugging)
    print("\n  ─── Signal Tallies ───")
    for axis_key, poles in state.get("axes", {}).items():
        dominant = get_dominant(axis_key, state)
        tally_str = "  |  ".join(f"{p}: {n}" for p, n in poles.items())
        print(f"  {axis_key}: {tally_str}  →  dominant: {dominant}")

    input("\n  [Press Enter to finish...]")
    hr()
    return node.get("next")

def handle_end(node: dict, state: dict) -> str:
    wrap(node["text"])
    print("\n" + "═" * WIDTH + "\n")
    return None

# ── Main Loop ──────────────────────────────────────────────────────────────────

HANDLERS = {
    "start":      handle_start,
    "question":   handle_question,
    "decision":   handle_decision,
    "reflection": handle_reflection,
    "bridge":     handle_bridge,
    "summary":    handle_summary,
    "end":        handle_end,
}

def run_tree(tree: dict):
    state = {"answers": {}, "answer_labels": {}, "axes": {}}
    current_id = "START"

    header("DAILY REFLECTION TREE")

    while current_id:
        node = tree.get(current_id)
        if not node:
            print(f"[Error] Node '{current_id}' not found in tree.")
            break

        handler = HANDLERS.get(node["type"])
        if not handler:
            print(f"[Error] Unknown node type '{node['type']}' at '{current_id}'.")
            break

        current_id = handler(node, state)

# ── Entry Point ────────────────────────────────────────────────────────────────

def main():
    # Resolve tree file path
    if len(sys.argv) > 1 and sys.argv[1] != "--tree":
        tree_path = Path(sys.argv[1])
    elif "--tree" in sys.argv:
        idx = sys.argv.index("--tree")
        tree_path = Path(sys.argv[idx + 1])
    else:
        # Default: look one level up in /tree/
        script_dir = Path(__file__).parent
        tree_path  = script_dir.parent / "tree" / "reflection-tree.json"

    if not tree_path.exists():
        print(f"[Error] Tree file not found: {tree_path}")
        print("Usage: python agent.py [--tree path/to/reflection-tree.json]")
        sys.exit(1)

    tree = load_tree(tree_path)
    run_tree(tree)

if __name__ == "__main__":
    main()
