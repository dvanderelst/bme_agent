# Pickup notes

The project has grown well past the original RAG chatbot. As of 2026-05-10 it's a full research-study setup with two deployed apps and a study-design document. Use this as the on-ramp when coming back to it.

## What's in the repo now

- **`agent/`** — deployed chatbot Streamlit app (Anthropic + Mistral backends, bcrypt auth against Postgres `students` table, RAG via `agent/agent_files/documents/` + `manifest.toml`).
- **`research/`** — deployed survey Streamlit app for the learning rubric (login → intro → task picker → Q1–Q4 free-text + Q5 structured wrap-up, restart with instructor passcode). Shares the same Postgres and student auth as the chatbot.
- **`shared_lib/`** — auth, login throttle, Postgres logging, used by both apps.
- **`figures/`** — figure-generation pipeline for the rubric question images. Renders to `figures/images/*.png`.
- **`ResearchPlan.md`** at repo root — the study-design document. Read this first to understand the *why* of everything.
- **`ISSUES.md`** at repo root — small running punch list. The big May-2026 review was worked through to close-out; resolutions live in git log.
- **`readme.md`** — project docs for running locally and understanding the code.

Two services on one Railway project, each with its own `start.sh` + `railway.toml`; locally run via `dev_agent.sh` / `dev_research.sh`.

When picking up, read the Outstanding-tasks section at the top of `ResearchPlan.md` (study-design TODOs) and the surviving items in `ISSUES.md` (deferred / out-of-scope), in that order. Then `git log --oneline -30` to see what was last touched.

## Open threads worth knowing about

Not exhaustive — `ResearchPlan.md` Outstanding tasks and `ISSUES.md` cover the rest.

- **Q5 finalization.** The survey's wrap-up question (Q5) is still a placeholder set. Plan calls for adding student self-rating on the production rubric (same 5 items as the instructor/AI rubric, so the contrast between self- and instructor-rating becomes its own output) plus an outstanding-problems prompt. Edit in `research/pages/3_Survey.py` and update the matching §Learning rubric design block in `ResearchPlan.md`. The design comment block at the top of the Q5 branch in `3_Survey.py` lays out the "every widget must distinguish answered from didn't-touch" rule — follow it when picking widgets.
- **Observer-log app.** Third Streamlit service to capture instructor-interaction observations during slots. Reuses the same auth and Postgres. Discussed in `ResearchPlan.md` §Interaction assessment but not built yet.
- **Observer protocol** (granularity + topic coding) — pre-Day-1 decision to settle with collaborators. Plan currently lists three granularity options and three topic-coding options.
- **Prompt caching for Anthropic** (issue 5 in `ISSUES.md`) — deferred. Fix would require moving docs from the user message into the `system` parameter to keep them positionally stable, which changes Anthropic's "primary source vs background context" framing. Deferred while response quality is the priority.

## Stances that aren't obvious from the code alone

- **Bayesian for pragmatic reasons, not philosophy.** Priors are weakly informative defaults (`normal(0, 1)` on standardized coefficients), chosen for sensibility not knowledge. The Bayesian framing buys small-N regularization (mixed models at N=24 often won't converge frequentist) and easy posterior contrasts for the production-vs-learning dissociation. Frequentist mixed models + bootstrap would be a defensible alternative.
- **Estimation, not significance.** No p-thresholding. No formal power analysis — the position is "if the chatbot's effect is large enough to matter pedagogically, it'll be visible across 48 chatbot-on / 48 chatbot-off measurements; if not, 'no clear effect' is itself an informative answer."
- **Production rubric is theoretical, not behavioural.** Scored from code reading (does the code, in principle, implement the rubric item) rather than from runtime success (which depends on lighting, tuning, etc.). Q5 self-rating captures behavioural / self-perception separately.
- **Day = task at the design level.** Mimic/Approach are Day 1; Kinesis/Taxis are Day 2. The model uses `task` only; `day` would be perfectly collinear and rank-deficient. The "Note on day vs task" paragraph in `ResearchPlan.md` §Analysis plan spells this out.
- **`half` is a fixed-effect indicator, not `(1|half)`.** n=2 clusters doesn't admit a variance estimate.
- **Fail open over dead-end UX.** Moderation API errors retry once then fail open with a warning rather than dead-ending students; the LLM has its own training-level guardrails as a second line of defense. Documented in `readme.md` under `### moderation.py`.
- **"Independence" of LLM judges in ACJ is conditional and partial.** Per-judge random effects absorb systematic per-judge bias; shared bias across the whole judge pool (training-data overlap) survives and is acknowledged as a limitation rather than modelled away. Mitigation: judge diversity across training lineages (via OpenRouter, Anthropic + OpenAI + Mistral + DeepSeek/Qwen + ...) and reporting inter-judge agreement as a precision diagnostic.

## Tooling reminders

- **Both apps run locally** with `bash dev_agent.sh` (port 8501) / `bash dev_research.sh` (port 8502). They source `.env` at the repo root for `DATABASE_URL` and friends.
- **Anthropic-side knobs** (model, max_tokens, max_history_messages) live in `agent/anthropic_lib/config.toml`. Mistral's equivalents live on the Mistral console (server-side Agent resource — agent owns its own `completion_args`).
- **`RESTART_PASSCODE`** is the survey's instructor passcode for restarting an attempt. Set in Railway env vars for the survey service. Empty = restart disabled.
- **Anthropic file registry** at `agent/anthropic_lib/file_registry.json` is tracked in git so production carries the same `file_id`s as local. Re-running `script_configure_agents.py` updates it; commit and push afterward, then Railway redeploy invalidates the validate-registry cache.

## Why these things might not be in the repo

Some of the rationale here (the Bayesian-for-pragmatic-reasons argument, the centered-vs-uncentered discussion that drove the "uncorrelated" rephrasing in §"What this layout buys us", the LLM-judge-independence philosophical point) lived as conversation but only its conclusion landed in `ResearchPlan.md`. If a reviewer ever pushes back on one of those calls, the git log around 2026-05-09 / 2026-05-10 has the working-out.
