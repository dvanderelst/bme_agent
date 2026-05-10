# Issues — Punch List

The original 38-item punch list from the May-2026 step-back review was worked through to close-out — 32 fixed in code, 6 closed by documented decision in `ResearchPlan.md`. Resolution detail for those lives in the git log; search commit messages for "issue N" or by file path. The items below are the ones that survive: two deferred by explicit decision and one marked out-of-scope for this document. Kept here so they don't get forgotten.

Status: `[ ]` = open / deferred, `[~]` = out of scope for this repo's docs.

---

## Chatbot (`agent/`)

- [ ] **5. No prompt caching; documents re-attached every turn.** *(deferred — see note below)*
  *Where:* `agent/anthropic_lib/conversation_management.py:60-75, 103-112`
  *Why:* Biggest single cost lever not pulled. With ~N docs in the registry, every turn re-attaches all of them; cost scales linearly with conversation length.
  *Fix:* Move documents from the latest user message into the `system` parameter (which accepts a list of content blocks) and put `cache_control: {"type": "ephemeral"}` on the last system block.
  *Note (2026-05-09):* The naive fix — `cache_control` on the last doc block in the user message — does **not** produce cache hits in our setup. Anthropic's cache requires an exact prefix match up to the breakpoint, and our user message sits at the end of a `messages` list that grows two entries per turn (one user + one assistant). The doc blocks therefore shift position every turn and the cached prefix is never re-matched; we'd pay the 1.25× write cost without the 0.1× read benefit. The only way to cache the docs is to put them somewhere positionally stable across turns, which means the `system` parameter. That works mechanically but changes Anthropic's framing — system content is "background context" rather than "primary source material" (per the comment currently in `_build_messages`). Deferred because response quality is the higher priority right now; the cost saving (~90% on cached input tokens after the first turn, within the 5-minute ephemeral TTL) is a future-when-we-care-about-cost win.

---

## Survey (`research/`)

- [ ] **19. Passcode form has no brute-force protection.** *(deferred — see note)*
  *Where:* `research/pages/2_Tasks.py:55-79`
  *Why:* 0.5s sleep slows but doesn't stop a logged-in student. A 4-digit numeric passcode = ~83 min worst case. No per-user/IP counter, no lockout.
  *Fix:* Small failed-attempts table + lockout; use `hmac.compare_digest` for the comparison.
  *Note (2026-05-09):* Deferred. The threat model is "a logged-in student spamming the restart form to brute-force the instructor passcode" — implausible in a 24-student classroom where (a) the instructor is physically present, (b) the student has nothing to gain from a successful restart that they couldn't get by asking the instructor directly, and (c) any successful brute-force is logged in `rubric_responses` with a username and timestamp. Revisit if the survey gets used outside a supervised setting.

---

## Research plan (`ResearchPlan.md`)

- [~] **34. No IRB/consent, data-sharing, dropout, or pre-registration plan.** *(out of scope for ResearchPlan.md)*
  *Where:* (missing throughout)
  *Why:* Identifiable usernames in chatbot/observation logs and AI-judged answers — not optional. Reviewers will block on this.
  *Fix:* Add §Ethics and §Pre-registration sections.
  *Resolution (2026-05-09):* Acknowledged as needed but not in scope for `ResearchPlan.md`, which is the study-design document. IRB / consent / data-sharing / pre-registration live in separate documents managed outside this repo.
