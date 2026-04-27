# Write-Up: Daily Reflection Tree — Design Rationale

**Candidate:** DT Fellowship Application
**Assignment:** Role Simulation — DailyReflectionTree
**Date:** April 2026

---

## 1. Why These Questions

The hardest part of this assignment wasn't the code or the JSON schema — it was writing questions that a real person, tired at 7pm, would actually stop and think about rather than click through.

My guiding principle: **each question must name something the employee already felt, without telling them how to feel about it.** A question like "Did you show initiative today?" is useless — it leads the witness. A question like "When something went well, what made it happen?" invites honest self-attribution.

**On Axis 1 (Locus):** I opened with a one-word descriptor of the day — "Productive," "Tough," "Mixed," "Frustrating" — rather than asking directly about agency. This is borrowed from interview technique: start with a low-threat observation question before asking an interpretation question. The descriptor answer also feeds into the interpolation in Q2 ("You said 'Frustrating'..."), which makes the conversation feel personal rather than scripted. The follow-up question — "Was there a moment, even small, where you made a decision that changed something?" — was the hardest to write. I went through six versions. Too leading ("Did you take control?") produces compliance. Too open ("What did you do?") produces defensiveness. The word "even small" does the work: it gives the external-locus employee permission to find *something* while not pressuring them to inflate it.

**On Axis 2 (Orientation):** The key psychological trap I was designing against is that entitlement is invisible to the person holding it (Campbell et al., 2004). People rarely feel entitled; they feel *rightfully frustrated*. So I couldn't ask "Were you entitled today?" I instead asked about a specific interaction (concrete, low-threat), then asked what drove it. Options like "I was hoping it would be noticed" and "I felt obligated" surface entitlement-adjacent motivations without moralising. The alternative branch — "Was there a moment you gave without expectation?" — gives entitlement-oriented employees a chance to find a counter-example, which prevents the tree from being a guilt machine.

**On Axis 3 (Radius):** I wanted to operationalise Maslow's self-transcendence without using that language. "Who were you thinking about?" is better than "Did you think about others?" because it's reconstructive, not evaluative. The options are ordered from narrow (A: myself) to wide (D: the end user), creating a natural spectrum that the employee can place themselves on without knowing the "right answer."

---

## 2. Branching Design — Tradeoffs

The tree uses a **signal tally** system: each option on a question node carries a signal ("axis1:internal" or "axis1:external"). Signals accumulate in state. Decision nodes routing to reflections compare tallies — if internal signals ≥ external, the employee sees the internal-locus reflection.

**Tradeoff 1: Granularity vs. complexity.** I could have created separate branches for every possible answer combination (32 paths through 5 binary questions). I chose to tally signals instead, which collapses many paths into two reflections per axis. This sacrifices some granularity but massively reduces tree maintenance complexity — and prevents the explosion of edge-case paths that would be impossible to review for tone quality.

**Tradeoff 2: Entry-point branching.** For Axis 1, I branch immediately on the opening word ("Productive/Mixed" vs. "Tough/Frustrating") to show different Q2 variants. Someone who described the day as "Productive" would find "When things got difficult, what was your first instinct?" jarring — it doesn't match their stated experience. Matching the early branch to the entry word makes the conversation feel responsive, not canned.

**Tradeoff 3: Bridge nodes.** I deliberated over whether to include bridges at all. They add nodes without gathering data. But they serve a real function: they help the employee mentally close one axis before opening the next. Without a bridge, the shift from "how did you handle it?" to "what did you give?" feels abrupt. The bridges also give the tree's tone a voice — unhurried, curious, not interrogative.

---

## 3. Psychological Sources

- **Rotter (1954) — Locus of Control Scale:** I read the original 29-item scale to understand how Rotter differentiated internal vs. external items. His items are forced-choice between two statements, which influenced my option design — I tried to write options where both poles are defensible, not where one is obviously "correct."
- **Dweck (2006) — Mindset:** Growth vs. fixed mindset is related to but distinct from locus of control. I deliberately kept growth mindset as subtext rather than explicit — the question "Was there a moment you made a decision that changed something?" is implicitly asking about belief in personal agency, which is the locus-growth intersection.
- **Campbell et al. (2004) — Psychological Entitlement Scale:** The six-item PES helped me understand what entitlement looks like in observable behaviours: counting credit, comparing contribution ("they aren't pulling their weight"), focusing on recognition. These fed directly into the Axis 2 option language.
- **Organ (1988) — Organizational Citizenship Behavior:** "Helping someone with something outside your formal responsibility" and "doing something extra without being asked" are direct operationalisations of OCB dimensions (altruism and conscientiousness).
- **Maslow (1969) — Toward a Psychology of Being:** The later Maslow is rarely taught in management contexts. His argument — that self-actualization is not the peak, and that the move from self-referential to other-oriented concern is the final developmental step — is exactly the frame Axis 3 is built on. I wanted the radius questions to surface this without naming it.
- **Batson (2011) — Altruism in Humans:** Batson's distinction between *empathy* (imagining another's feelings) and *perspective-taking* (imagining another's situation) informed the Axis 3 option "A specific colleague who had it harder than me" — which is perspective-taking in action.

---

## 4. What I'd Improve With More Time

**Tighter options on Q3 (Axis 1 follow-up).** "Maybe — I hadn't thought about it that way" is doing a lot of work. It's useful for catching employees who initially framed their day as externally driven but can be nudged toward agency. But it's also the kind of option that thoughtful people always pick because it feels honest. I'd user-test this option with real people to see if it's meaningful or a cop-out.

**A fourth axis.** There's a natural extension here around *time orientation* — was the employee thinking about today's events or connecting them to longer-term trajectories? Someone who sees a hard day as data for the future versus evidence of a permanent problem is experiencing something psychologically meaningful that the current tree doesn't capture.

**Adaptive questioning.** Right now, the same Q3 follows regardless of whether the employee answered Q2 with "I planned for it" or "Someone else made it possible." With more nodes, I'd write Q3 variants that build on the specific Q2 answer, deepening the interpolation. Currently `{A1_OPEN.answer}` is the only interpolation used — the tree could be much more personalised.

**Tone testing.** The reflections are the hardest nodes to write and the easiest to get wrong. A reflection that sounds therapeutic in isolation might sound condescending at 7pm after a brutal day. I'd want to run these through 10-15 real users across different axis profiles before shipping.

---

*"The tree's tone is a wise colleague — not a therapist, not a manager, not a motivational poster."*
*— Assignment brief. I kept that sentence on screen the entire time I was writing.*
