# Daily Reflection Tree — README

## What This Is

A fully deterministic, end-of-day employee reflection tool built as a decision tree. The tree walks an employee through a structured conversation across three psychological axes. No LLM is called at runtime — the intelligence is encoded in the tree structure itself.

**Built for:** DT Fellowship Role Simulation Assignment

---

## Repository Structure

```
/tree/
  reflection-tree.json     ← Part A: full tree data (27 nodes)
  tree-diagram.md          ← Part A: Mermaid visual + node map table

/agent/
  agent.py                 ← Part B: Python CLI runner

/transcripts/
  persona-1-transcript.md  ← Victor / Contribution / Altrocentric path
  persona-2-transcript.md  ← Victim / Entitlement / Self-Centric path

write-up.md                ← Part A: design rationale (2 pages)
README.md                  ← this file
```

---

## Reading the Tree (Part A)

Open `tree/reflection-tree.json`. Each node in the `"nodes"` array has:

| Field | Purpose |
|-------|---------|
| `id` | Unique node identifier |
| `type` | Node behaviour: `start`, `question`, `decision`, `reflection`, `bridge`, `summary`, `end` |
| `axis` | Which psychological axis this node belongs to (1, 2, 3, or null) |
| `text` | What the employee sees. `{NODE_ID.answer}` is replaced with their earlier answer. |
| `options` | Fixed choices for question nodes. Each option has a `label`, `value`, and optional `signal`. |
| `routes` | Routing rules for decision nodes. Evaluated in order; first match wins. |
| `next` | Default next node ID for non-decision nodes. |
| `signal` | Not used on question nodes directly — signals are on each *option* instead. |

### Node Types

| Type | Employee sees? | Auto-advances? |
|------|---------------|---------------|
| `start` | Welcome text | After Enter |
| `question` | Question + options | After selection |
| `decision` | Nothing | Immediately (invisible) |
| `reflection` | Reframe/insight text | After Enter |
| `bridge` | Transition statement | After Enter |
| `summary` | Personalised end-of-session synthesis | After Enter |
| `end` | Closing message | Session ends |

### Signal Tallying

Each question option can carry a `signal` like `"axis1:internal"`. The agent increments a tally:

```
state.axes.axis1.internal += 1
```

Decision nodes routing to reflections use `axis1.dominant == internal` — meaning whichever pole has the higher tally wins.

### Tracing a Path Manually

Example — an employee who describes their day as "Tough":

1. `START` → auto-advance to `A1_OPEN`
2. `A1_OPEN` → employee picks "Tough" → advance to `A1_D1`
3. `A1_D1` → condition `A1_OPEN.answer IN [Tough, Frustrating]` matches → go to `A1_Q_LOW`
4. `A1_Q_LOW` → employee picks option C or D (external) → signal `axis1:external` recorded
5. `A1_Q_AGENCY_FOLLOWUP` → employee picks D → signal `axis1:external` recorded (tally: external=2, internal=0)
6. `A1_D2` → `axis1.dominant == external` → go to `A1_R_EXT`
7. ...and so on through Axis 2 and Axis 3

---

## Running the Agent (Part B)

**Requirements:** Python 3.10+ (no external libraries)

```bash
# From the repo root:
python agent/agent.py

# Or specify the tree path explicitly:
python agent/agent.py --tree tree/reflection-tree.json
```

The agent:
1. Loads `reflection-tree.json` from disk (not hardcoded)
2. Walks the tree node-by-node
3. At `question` nodes: prints options, waits for numbered input, records answer + signal
4. At `decision` nodes: evaluates routing conditions silently, jumps to target
5. At `reflection`/`bridge` nodes: prints text, waits for Enter
6. At `summary`: builds personalised text from accumulated axis tallies, prints signal breakdown
7. At `end`: closes session

---

## The Three Axes

| Axis | Spectrum | Core Psychology |
|------|---------|----------------|
| 1 — Locus | Victim ↔ Victor | Rotter (1954) Locus of Control; Dweck (2006) Growth Mindset |
| 2 — Orientation | Entitlement ↔ Contribution | Campbell et al. (2004) Psychological Entitlement; Organ (1988) OCB |
| 3 — Radius | Self-Centric ↔ Altrocentric | Maslow (1969) Self-Transcendence; Batson (2011) Perspective-Taking |

---

## Node Count Verification

| Requirement | Minimum | This Tree |
|------------|---------|----------|
| Total nodes | 25+ | **27** |
| Question nodes | 8+ | **10** |
| Decision nodes | 4+ | **6** |
| Reflection nodes | 4+ | **6** |
| Bridge nodes | 2+ | **2** |
| Summary nodes | 1+ | **1** |
| Axes covered | All 3 | **All 3** |
| Options per question | 3–5 | **4 each** |
