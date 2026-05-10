# Issues — Punch List

Captured during a step-back review of the chatbot, the survey, and `ResearchPlan.md`. Numbered globally so we can refer to "issue 7" without ambiguity. Within each artifact, items are severity-ordered (High → Medium → Low). Status `[ ]` = open, `[x]` = done.

File:line citations are from the review and have not all been re-verified — confirm before editing if anything looks off.

---

## Chatbot (`agent/`)

### High severity

- [x] **1. Raw API errors leak to students.**
  *Where:* `agent/pages/1_Chat.py:286-290`
  *Why:* Exception strings are rendered as Markdown in the chat. SDK errors can carry stack traces, internal IDs, or even keys.
  *Fix:* Catch and show a generic message; log the real one.

- [x] **2. Failed assistant turns persist into history and get re-sent.**
  *Where:* `agent/pages/1_Chat.py:286-290` (same block)
  *Why:* On exception, the error string is appended with `role: assistant` and re-rendered every rerun, plus re-sent to the model on the next turn (Anthropic).
  *Fix:* Don't append on failure; show the error transiently.

- [x] **3. Mistral `conversation_id` can drift on partial failure.**
  *Where:* `agent/pages/1_Chat.py:223-229`
  *Why:* If the call raises mid-flight, `SESSION_CONVERSATION_ID` may not update; on retry the same prompt may be sent against `None` or a stale id, producing duplicate or context-mismatched server-side conversations.
  *Fix:* Update `conversation_id` only on confirmed success; clear local state on failure.

- [x] **4. Moderation failure leaves a dead-end.**
  *Where:* `agent/pages/1_Chat.py:84-96, 171-180`
  *Why:* A transient moderation API blip flips `SESSION_MODERATION_ERROR` until full chat restart. On flaky wifi this means a forced reset for every dropped moderation call.
  *Fix:* Clear the flag on the next successful turn; treat moderation API errors as soft (retry once, fail open with a logged warning) rather than hard.

- [ ] **5. No prompt caching; documents re-attached every turn.** *(deferred — see note below)*
  *Where:* `agent/anthropic_lib/conversation_management.py:60-75, 103-112`
  *Why:* Biggest single cost lever not pulled. With ~N docs in the registry, every turn re-attaches all of them; cost scales linearly with conversation length.
  *Fix:* Move documents from the latest user message into the `system` parameter (which accepts a list of content blocks) and put `cache_control: {"type": "ephemeral"}` on the last system block.
  *Note (2026-05-09):* The naive fix — `cache_control` on the last doc block in the user message — does **not** produce cache hits in our setup. Anthropic's cache requires an exact prefix match up to the breakpoint, and our user message sits at the end of a `messages` list that grows two entries per turn (one user + one assistant). The doc blocks therefore shift position every turn and the cached prefix is never re-matched; we'd pay the 1.25× write cost without the 0.1× read benefit. The only way to cache the docs is to put them somewhere positionally stable across turns, which means the `system` parameter. That works mechanically but changes Anthropic's framing — system content is "background context" rather than "primary source material" (per the comment currently in `_build_messages`). Deferred because response quality is the higher priority right now; the cost saving (~90% on cached input tokens after the first turn, within the 5-minute ephemeral TTL) is a future-when-we-care-about-cost win.

- [x] **6. `max_tokens=1024` truncates Sonnet 4.6 mid-answer often.**
  *Where:* `agent/anthropic_lib/config.toml`
  *Why:* Sonnet 4.6 with rich source documents will frequently hit the cap. Students see cut-off responses with no signal.
  *Fix:* Bump to 4096+; surface `stop_reason == "max_tokens"` in the UI.

### Medium severity

- [x] **7. Login throttle is per-attempt, not per-user/IP.**
  *Where:* `agent/app.py:36-53`
  *Why:* `FAILED_LOGIN_DELAY_SECONDS = 0.5` slows a single attempt; no per-username counter or lockout. With 24 known usernames a public deployment invites grinding.
  *Fix:* Add a small `failed_logins` table keyed by `(username, ip)` with rolling lockout.

- [x] **8. Disabled student keeps access mid-session.**
  *Where:* `agent/pages/1_Chat.py:60-61`
  *Why:* Auth gate is `session_state.authenticated` only; no re-check of `enabled`. An instructor disabling a student takes effect only on next login.
  *Fix:* Re-fetch the student row on a hot path (e.g. before each LLM call) and `st.stop()` if `enabled` is False.

- [x] **9. Empty file registry fails silently.**
  *Where:* `agent/anthropic_lib/conversation_management.py:50-57`
  *Why:* If the registry is empty, the model still answers (without docs) and the student gets generic answers with no indication the RAG layer is broken.
  *Fix:* At minimum surface to diagnostics users; consider failing closed when registry is unexpectedly empty.

- [x] **10. `_build_document_blocks` doesn't validate `file_id`s.**
  *Where:* `agent/anthropic_lib/conversation_management.py:54-57`
  *Why:* If a `file_id` has been deleted from the Anthropic workspace, every subsequent message 400s — currently leaks via issue 1.
  *Fix:* Validate at startup or catch the specific error and degrade gracefully.

- [x] **11. `get_postgres_client` re-runs CREATE/ALTER on every page render.**
  *Where:* `agent/app.py:27`, `agent/pages/1_Chat.py:73`
  *Why:* Idempotent but adds latency and DB churn (~24 students × N reruns/min).
  *Fix:* Wrap in `@st.cache_resource`.

### Low severity

- [ ] **12. Unbounded conversation history sent on every turn.**
  *Where:* `agent/pages/1_Chat.py:219`, `agent/anthropic_lib/conversation_management.py:69`
  *Why:* Long sessions hit the `max_tokens=1024` output cap (issue 6) plus growing input cost; eventually context limits.
  *Fix:* Add a sliding window or summarization.

- [ ] **13. `student_settings` dict mutation across `Json()` calls.**
  *Where:* `agent/pages/1_Chat.py:141-145`
  *Why:* Same dict object is passed to every `log_*` call; in-place mutation could affect any pending writes. Low risk in practice.
  *Fix:* `dict(student_settings)` per call.

- [ ] **14. Feedback Submit button is double-clickable.**
  *Where:* `agent/pages/1_Chat.py:307-323`
  *Why:* On a slow Postgres write, fast double-click can log twice.
  *Fix:* Disable the button after first click or check for in-flight state.

- [ ] **15. Leftover `print()`s in `mistral_lib/conversation_management.py`.**
  *Where:* `agent/mistral_lib/conversation_management.py:182-193`
  *Why:* Module was written for scripting; `print()` calls and emojis are dead in production but indicate it hasn't been hardened.
  *Fix:* Replace with `logging`.

---

## Survey (`research/`)

### High severity

- [x] **16. Cross-tab restart silently rewrites attempt number.**
  *Where:* `research/pages/3_Survey.py:33-41`
  *Why:* Tab A on Q3 of attempt 1; Tab B restarts → attempt 2. Tab A's next submit silently upgrades `attempt` to 2 in-place; the textarea contents land on the wrong (attempt, question_no) row.
  *Fix:* If `progress["attempt"] != session_state.attempt`, abort the form, show "this task was restarted in another tab; reload" and force a rerun.

- [x] **17. `q5_used_chatbot` defaults to "Yes".**
  *Where:* `research/pages/3_Survey.py:132-137`
  *Why:* `st.radio` defaults to the first option, so any student who clicks straight through Q5 records `used_chatbot=true`. Pollutes the headline join `answer_json->>'used_chatbot'`.
  *Fix:* Pass `index=None`; reject submit if still None.

- [x] **18. Q5 `usefulness` slider stores `3` (middle) as if it were a real answer.**
  *Where:* `research/pages/3_Survey.py:138-145, 161`
  *Why:* Default value=3 is stored verbatim when `used_chatbot=True`. Middle-of-range looks like a deliberate neutral rating.
  *Fix:* Add a separate "I didn't rate it" option, or use a 0/None sentinel and a "no rating" radio.

- [ ] **19. Passcode form has no brute-force protection.** *(deferred — see note)*
  *Where:* `research/pages/2_Tasks.py:55-79`
  *Why:* 0.5s sleep slows but doesn't stop a logged-in student. A 4-digit numeric passcode = ~83 min worst case. No per-user/IP counter, no lockout.
  *Fix:* Small failed-attempts table + lockout; use `hmac.compare_digest` for the comparison.
  *Note (2026-05-09):* Deferred. The threat model is "a logged-in student spamming the restart form to brute-force the instructor passcode" — implausible in a 24-student classroom where (a) the instructor is physically present, (b) the student has nothing to gain from a successful restart that they couldn't get by asking the instructor directly, and (c) any successful brute-force is logged in `rubric_responses` with a username and timestamp. Revisit if the survey gets used outside a supervised setting.

### Medium severity

- [x] **20. Restart-allocation race.**
  *Where:* `research/rubric_db.py:90-93`
  *Why:* `next_attempt_number` reads `max+1` outside any transaction; two near-simultaneous restarts can both decide on the same N+1 then collide on the UNIQUE constraint at Q1.
  *Fix:* Allocate atomically — e.g. `INSERT ... ON CONFLICT DO NOTHING RETURNING attempt`, bump and retry on miss.

- [x] **21. `completed` is computed from `MAX(question_no)`, not `COUNT(*)`.**
  *Where:* `research/rubric_db.py:63-87`
  *Why:* If rows ever land non-contiguously (multi-tab race; future code change), `{1, 3, 5}` shows as completed and Q2/Q4 silently absent.
  *Fix:* `COUNT(*) = TOTAL_QUESTIONS` for completion; base the next-question pointer on the smallest gap.

- [x] **22. `note` denormalization relies on `MAX(note)`.**
  *Where:* `research/rubric_db.py:68`
  *Why:* Works only because every row of an attempt currently has the same value. Fragile if a future code change writes per-question notes.
  *Fix:* Pull the note from `question_no = 1` only, or move it to a per-attempt table.

- [x] **23. Image-not-found falls through to a still-submittable form.**
  *Where:* `research/pages/3_Survey.py:87-90`
  *Why:* A path typo silently degrades to a yellow warning while answers continue saving. If figures move or get renamed, students answer questions they can't see.
  *Fix:* Disable submit (or `st.stop()`) when the image is missing; log the failure to Postgres.

- [x] **24. `record_answer` collapses three error classes into one user-visible message.**
  *Where:* `research/rubric_db.py:96-137`
  *Why:* UNIQUE collision, transient connection errors, and malformed JSON all surface as "Could not save your answer." Hides actionable cases (e.g. "another tab already saved this").
  *Fix:* Branch on SQLSTATE; surface duplicates differently.

### Low severity

- [ ] **25. Tab-close mid-restart-attempt strips `restart_note` until Q1 is in the DB.**
  *Where:* `research/pages/3_Survey.py:47-49`
  *Why:* Fallback `progress.get("note")` only works once Q1 is written. Restart → land on Q1 → close tab → log back in → Q1 is recorded with `note=NULL`; later rows inherit NULL.
  *Fix:* Persist the note to a small `rubric_attempts` table at restart-authorization time.

- [ ] **26. `mimic.yaml` Q4 content question.**
  *Where:* `research/questions/mimic.yaml`
  *Why:* The prompt mentions "two candidate LEDs" but the figure shows three filters (R/G/B). Worth a sanity check that the figure matches the prompt.
  *Fix:* Verify with the original rubric design and update either prompt or figure.

---

## Research plan (`ResearchPlan.md`)

### High severity

- [ ] **27. Power isn't quantified.**
  *Where:* §Analysis plan
  *Why:* N=24 × 4 slots × three Bayesian models with four fixed effects + random intercepts will give credible intervals so wide that null and large effects are indistinguishable.
  *Fix:* Run a prior-predictive / SBC power analysis; state the smallest effect the design can resolve.

- [x] **28. `task` is collinear with `day` — model is rank-deficient.**
  *Where:* §Analysis plan, line 108 (`chatbot + day + position + task + (1|student)`)
  *Why:* Mimic/Approach happen only on Day 1; Kinesis/Taxis only on Day 2. `day` is a deterministic function of `task`.
  *Fix:* Drop `day`, or recode `task` as the within-day task (2 levels) nested in day.
  *Resolution (2026-05-10):* Dropped `day` from all three model formulas; kept `task` as the more granular label. Added a "Note on `day` vs `task`" paragraph directly under the formulas explaining the equivalence — design-level prose still uses "day" freely (it's the natural way to talk about the schedule), the model uses `task`. The note concentrates the rationale in one place so a future reader of the formulas doesn't unwittingly add `day` back.

- [x] **29. The [1, 0, 0, 1] orthogonality argument needs to be stated in centered form.**
  *Where:* §"What this layout buys us"
  *Why:* The doc mixes uncentered and centered reasoning. Day×chatbot interaction aliases perfectly with the chatbot main effect at the room level — should be flagged explicitly, not folded into the asymmetric-carryover caveat.
  *Fix:* Restate the contrast in centered/sum-coded form; explicitly acknowledge day×chatbot is unidentifiable from the main effect at the room level.
  *Resolution (2026-05-10):* Substituted "orthogonal to" → "uncorrelated with (zero sample covariance)" in the cancellation argument. The original "orthogonal" wording was technically ambiguous — a reader computing a raw dot product on the listed vectors gets a non-zero number, even though the design-level cancellation property does hold (covariance is what matters, and covariance is invariant to centering and to coding choice). "Uncorrelated" is the same condition stated in language that's intuitively clear and matches what a regression actually does. The day×chatbot identifiability concern raised by the reviewer is now moot since `day` was dropped from the model under issue 28.

- [x] **30. Half (cluster) is unmodeled.**
  *Where:* §Analysis plan
  *Why:* Halves A/B share within-slot task order, so task order is a half-level treatment with n=2 clusters. Without `(1|half)` or a half fixed effect, between-half variance is mis-attributed to students.
  *Fix:* Add half as a random or fixed effect; acknowledge n=2 limits identifiability.
  *Resolution (2026-05-10):* Added `half` as a fixed-effect indicator to all three model formulas. Did not use `(1|half)` because n=2 clusters doesn't admit a variance estimate. Added a "Note on `half`" paragraph in §Analysis plan explaining why we use a fixed effect (absorbs the mean shift between halves) and noting the residual limitation: the pooled chatbot main effect is robust to between-half differences by Latin-square construction, but task-specific chatbot contrasts are not.

- [x] **31. Q5 isn't in the plan.**
  *Where:* §Learning rubric design
  *Why:* The deployed survey has a Q5 structured JSON wrap-up, but the plan only describes Q1–Q4. ACJ scoring is specified over "answers" without saying whether Q5 is included.
  *Fix:* State explicitly how Q5 enters the BT score (or doesn't); add a description of its current placeholder fields and noted-as-TBD status.
  *Resolution (2026-05-09):* Added a "Q5 — structured per-task wrap-up" paragraph to §Learning rubric design listing the current placeholder fields and candidate additional items (student self-rating on the production rubric; outstanding-problems prompt). Stated that Q5 is descriptive only — not BT-aggregated. Pointed at the design-comment block in `research/pages/3_Survey.py` for the "answered vs untouched" rule.

- [ ] **32. No priors or likelihoods specified.**
  *Where:* §Analysis plan
  *Why:* "Bayesian mixed model" is not runnable without priors, link functions, or standardization. Production score is a sum of five 0–3 ordinal items — Gaussian will misbehave at floor/ceiling.
  *Fix:* Specify priors, likelihoods (cumulative ordinal or beta-binomial for production), and predictor coding (centered/sum-coded).

### Medium severity

- [x] **33. No baseline confounders collected.**
  *Where:* (missing throughout)
  *Why:* Prior programming experience, prior chatbot familiarity, native language are obvious moderators of both production and learning, and of differential chatbot benefit.
  *Fix:* Add a one-time baseline survey before Day 1.
  *Resolution (2026-05-09):* Already addressed by the BME program's existing pre-program surveys, one of which explicitly asks about prior experience with and use of chatbots. Added a bullet to §Methodological safeguards noting that pre-program survey fields are available as covariates / moderators in the analysis models if desired.

- [~] **34. No IRB/consent, data-sharing, dropout, or pre-registration plan.** *(out of scope for ResearchPlan.md)*
  *Where:* (missing throughout)
  *Why:* Identifiable usernames in chatbot/observation logs and AI-judged answers — not optional. Reviewers will block on this.
  *Fix:* Add §Ethics and §Pre-registration sections.
  *Resolution (2026-05-09):* Acknowledged as needed but not in scope for `ResearchPlan.md`, which is the study-design document. IRB / consent / data-sharing / pre-registration live in separate documents managed outside this repo.

- [ ] **35. Exclusion / partial-data rules undefined.**
  *Where:* (missing throughout)
  *Why:* A student absent on Day 2 breaks Latin-square balance. What's the ITT vs per-protocol rule and minimum-data threshold?
  *Fix:* Pre-specify before Day 1.

- [ ] **36. AI-judge non-independence in ACJ.**
  *Where:* §Scoring plan
  *Why:* Multiple LLM judges treated as independent raters in BT — but if all are LLMs trained on overlapping data, judgements are correlated, deflating BT standard errors.
  *Fix:* Report inter-judge agreement; consider a hierarchical BT with judge random effect.

### Low severity

- [x] **37. Production-rubric blinding is asserted but not operationalized.**
  *Where:* §Methodological safeguards
  *Why:* Robot photos visibly differ between color-vision and sound-localization tasks; condition (chatbot on/off) may leak through code style/comments.
  *Fix:* Describe the blinding procedure (file scrub, ID-only labels).
  *Resolution (2026-05-09):* Added a "Note on production-rubric blinding" block to §Methodological safeguards. Two leakage-reducing features of the current setup are flagged (block-based code → no free-text comments to scrub and muted stylistic variation; direct rubric items → little room for inference-driven bias). Residual channels named for the eventual operational procedure: file metadata/timestamps (cross-referenceable with the slot schedule), and incidental contents of robot photos.

- [x] **38. Mimic items 2 and 5 need behavioral verification, not just code reading.**
  *Where:* §Production rubric: Mimic Color
  *Why:* "Does the robot produce the correct output color" and "can the robot mimic more than two distinct colors" require running the code, not inspecting it.
  *Fix:* Specify whether the scorer runs the code or judges from inspection.
  *Resolution (2026-05-09):* Production rubric is intentionally **theoretical** — does the code, in principle, implement the rubric item — rather than behavioural. Whether the robot actually completes the task at the moment of the photo depends on parameter tuning, lighting, distance, and exact setup, none of which we want to penalise. Clarified this in §Scoring plan. Behavioural / self-perception data is captured separately via Q5 — added "student self-rating on the production rubric" as a candidate Q5 item, plus an outstanding-problems prompt; the contrast between self-rating and the actual production score is itself a substantive output.
