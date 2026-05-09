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

- [ ] **5. No prompt caching; documents re-attached every turn.**
  *Where:* `agent/anthropic_lib/conversation_management.py:60-75, 103-112`
  *Why:* Biggest single cost lever not pulled. With ~N docs in the registry, every turn re-attaches all of them; cost and latency scale linearly with conversation length.
  *Fix:* Add `cache_control: {"type": "ephemeral"}` to system + last document block; consider attaching docs only on the first user turn.

- [ ] **6. `max_tokens=1024` truncates Sonnet 4.6 mid-answer often.**
  *Where:* `agent/anthropic_lib/config.toml`
  *Why:* Sonnet 4.6 with rich source documents will frequently hit the cap. Students see cut-off responses with no signal.
  *Fix:* Bump to 4096+; surface `stop_reason == "max_tokens"` in the UI.

### Medium severity

- [ ] **7. Login throttle is per-attempt, not per-user/IP.**
  *Where:* `agent/app.py:36-53`
  *Why:* `FAILED_LOGIN_DELAY_SECONDS = 0.5` slows a single attempt; no per-username counter or lockout. With 24 known usernames a public deployment invites grinding.
  *Fix:* Add a small `failed_logins` table keyed by `(username, ip)` with rolling lockout.

- [ ] **8. Disabled student keeps access mid-session.**
  *Where:* `agent/pages/1_Chat.py:60-61`
  *Why:* Auth gate is `session_state.authenticated` only; no re-check of `enabled`. An instructor disabling a student takes effect only on next login.
  *Fix:* Re-fetch the student row on a hot path (e.g. before each LLM call) and `st.stop()` if `enabled` is False.

- [ ] **9. Empty file registry fails silently.**
  *Where:* `agent/anthropic_lib/conversation_management.py:50-57`
  *Why:* If the registry is empty, the model still answers (without docs) and the student gets generic answers with no indication the RAG layer is broken.
  *Fix:* At minimum surface to diagnostics users; consider failing closed when registry is unexpectedly empty.

- [ ] **10. `_build_document_blocks` doesn't validate `file_id`s.**
  *Where:* `agent/anthropic_lib/conversation_management.py:54-57`
  *Why:* If a `file_id` has been deleted from the Anthropic workspace, every subsequent message 400s — currently leaks via issue 1.
  *Fix:* Validate at startup or catch the specific error and degrade gracefully.

- [ ] **11. `get_postgres_client` re-runs CREATE/ALTER on every page render.**
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

- [ ] **16. Cross-tab restart silently rewrites attempt number.**
  *Where:* `research/pages/3_Survey.py:33-41`
  *Why:* Tab A on Q3 of attempt 1; Tab B restarts → attempt 2. Tab A's next submit silently upgrades `attempt` to 2 in-place; the textarea contents land on the wrong (attempt, question_no) row.
  *Fix:* If `progress["attempt"] != session_state.attempt`, abort the form, show "this task was restarted in another tab; reload" and force a rerun.

- [ ] **17. `q5_used_chatbot` defaults to "Yes".**
  *Where:* `research/pages/3_Survey.py:132-137`
  *Why:* `st.radio` defaults to the first option, so any student who clicks straight through Q5 records `used_chatbot=true`. Pollutes the headline join `answer_json->>'used_chatbot'`.
  *Fix:* Pass `index=None`; reject submit if still None.

- [ ] **18. Q5 `usefulness` slider stores `3` (middle) as if it were a real answer.**
  *Where:* `research/pages/3_Survey.py:138-145, 161`
  *Why:* Default value=3 is stored verbatim when `used_chatbot=True`. Middle-of-range looks like a deliberate neutral rating.
  *Fix:* Add a separate "I didn't rate it" option, or use a 0/None sentinel and a "no rating" radio.

- [ ] **19. Passcode form has no brute-force protection.**
  *Where:* `research/pages/2_Tasks.py:55-79`
  *Why:* 0.5s sleep slows but doesn't stop a logged-in student. A 4-digit numeric passcode = ~83 min worst case. No per-user/IP counter, no lockout.
  *Fix:* Small failed-attempts table + lockout; use `hmac.compare_digest` for the comparison.

### Medium severity

- [ ] **20. Restart-allocation race.**
  *Where:* `research/rubric_db.py:90-93`
  *Why:* `next_attempt_number` reads `max+1` outside any transaction; two near-simultaneous restarts can both decide on the same N+1 then collide on the UNIQUE constraint at Q1.
  *Fix:* Allocate atomically — e.g. `INSERT ... ON CONFLICT DO NOTHING RETURNING attempt`, bump and retry on miss.

- [ ] **21. `completed` is computed from `MAX(question_no)`, not `COUNT(*)`.**
  *Where:* `research/rubric_db.py:63-87`
  *Why:* If rows ever land non-contiguously (multi-tab race; future code change), `{1, 3, 5}` shows as completed and Q2/Q4 silently absent.
  *Fix:* `COUNT(*) = TOTAL_QUESTIONS` for completion; base the next-question pointer on the smallest gap.

- [ ] **22. `note` denormalization relies on `MAX(note)`.**
  *Where:* `research/rubric_db.py:68`
  *Why:* Works only because every row of an attempt currently has the same value. Fragile if a future code change writes per-question notes.
  *Fix:* Pull the note from `question_no = 1` only, or move it to a per-attempt table.

- [ ] **23. Image-not-found falls through to a still-submittable form.**
  *Where:* `research/pages/3_Survey.py:87-90`
  *Why:* A path typo silently degrades to a yellow warning while answers continue saving. If figures move or get renamed, students answer questions they can't see.
  *Fix:* Disable submit (or `st.stop()`) when the image is missing; log the failure to Postgres.

- [ ] **24. `record_answer` collapses three error classes into one user-visible message.**
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

- [ ] **28. `task` is collinear with `day` — model is rank-deficient.**
  *Where:* §Analysis plan, line 108 (`chatbot + day + position + task + (1|student)`)
  *Why:* Mimic/Approach happen only on Day 1; Kinesis/Taxis only on Day 2. `day` is a deterministic function of `task`.
  *Fix:* Drop `day`, or recode `task` as the within-day task (2 levels) nested in day.

- [ ] **29. The [1, 0, 0, 1] orthogonality argument needs to be stated in centered form.**
  *Where:* §"What this layout buys us"
  *Why:* The doc mixes uncentered and centered reasoning. Day×chatbot interaction aliases perfectly with the chatbot main effect at the room level — should be flagged explicitly, not folded into the asymmetric-carryover caveat.
  *Fix:* Restate the contrast in centered/sum-coded form; explicitly acknowledge day×chatbot is unidentifiable from the main effect at the room level.

- [ ] **30. Half (cluster) is unmodeled.**
  *Where:* §Analysis plan
  *Why:* Halves A/B share within-slot task order, so task order is a half-level treatment with n=2 clusters. Without `(1|half)` or a half fixed effect, between-half variance is mis-attributed to students.
  *Fix:* Add half as a random or fixed effect; acknowledge n=2 limits identifiability.

- [ ] **31. Q5 isn't in the plan.**
  *Where:* §Learning rubric design
  *Why:* The deployed survey has a Q5 structured JSON wrap-up, but the plan only describes Q1–Q4. ACJ scoring is specified over "answers" without saying whether Q5 is included.
  *Fix:* State explicitly how Q5 enters the BT score (or doesn't); add a description of its current placeholder fields and noted-as-TBD status.

- [ ] **32. No priors or likelihoods specified.**
  *Where:* §Analysis plan
  *Why:* "Bayesian mixed model" is not runnable without priors, link functions, or standardization. Production score is a sum of five 0–3 ordinal items — Gaussian will misbehave at floor/ceiling.
  *Fix:* Specify priors, likelihoods (cumulative ordinal or beta-binomial for production), and predictor coding (centered/sum-coded).

### Medium severity

- [ ] **33. No baseline confounders collected.**
  *Where:* (missing throughout)
  *Why:* Prior programming experience, prior chatbot familiarity, native language are obvious moderators of both production and learning, and of differential chatbot benefit.
  *Fix:* Add a one-time baseline survey before Day 1.

- [ ] **34. No IRB/consent, data-sharing, dropout, or pre-registration plan.**
  *Where:* (missing throughout)
  *Why:* Identifiable usernames in chatbot/observation logs and AI-judged answers — not optional. Reviewers will block on this.
  *Fix:* Add §Ethics and §Pre-registration sections.

- [ ] **35. Exclusion / partial-data rules undefined.**
  *Where:* (missing throughout)
  *Why:* A student absent on Day 2 breaks Latin-square balance. What's the ITT vs per-protocol rule and minimum-data threshold?
  *Fix:* Pre-specify before Day 1.

- [ ] **36. AI-judge non-independence in ACJ.**
  *Where:* §Scoring plan
  *Why:* Multiple LLM judges treated as independent raters in BT — but if all are LLMs trained on overlapping data, judgements are correlated, deflating BT standard errors.
  *Fix:* Report inter-judge agreement; consider a hierarchical BT with judge random effect.

### Low severity

- [ ] **37. Production-rubric blinding is asserted but not operationalized.**
  *Where:* §Methodological safeguards
  *Why:* Robot photos visibly differ between color-vision and sound-localization tasks; condition (chatbot on/off) may leak through code style/comments.
  *Fix:* Describe the blinding procedure (file scrub, ID-only labels).

- [ ] **38. Mimic items 2 and 5 need behavioral verification, not just code reading.**
  *Where:* §Production rubric: Mimic Color
  *Why:* "Does the robot produce the correct output color" and "can the robot mimic more than two distinct colors" require running the code, not inspecting it.
  *Fix:* Specify whether the scorer runs the code or judges from inspection.
