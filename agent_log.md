# Agent Log

This document will be used to track changes and manipulations to the agent/chatbot as it is deployed throughout the program.
Entries here can be in free format. And both Claude and Dieter are allowed to write to this document.


Sun 31 May 2026 01:42:35 PM EDT

+ Changed to new mistral moderation model
+ Set up the 25 students I found in the onedrive folder (usernames: first name, lowercase; passwords: animal + number)
+ Created an activity description "getting_started.md" and set this for tomorrow's start of the program
+ Reset (but backed up) the existing database tables
+ Split the students into two groups A and B as a way to assign students to different challenges in the research part of the program

Sun 31 May 2026 — additional notes (Claude)

Details on the above that matter for interpreting day-1 behaviour:
+ Moderation: the model change was to `mistral-moderation-2603`, and we also enabled its new `jailbreaking` category (the old model didn't have it). Tested against benign + adversarial prompts: real jailbreaks flag, normal student phrasings ("ignore the line sensor", "kill the stuck program", etc.) pass.
+ Moderation `pii` category stays ON. This means a message containing a name/email/phone/address gets blocked — including a student self-introduction like "Hi, I'm Breanna". Worth watching on day 1.
+ The `students.enabled` flag was being read as text, so disabling a student silently did nothing; fixed to coerce to a real boolean. Disabling a student now actually blocks login.
+ The roster has 27 rows, not 25: the `teacher` and `ttest` accounts are still live for instructor use / spot-checking.
+ Two students named Benjamin were disambiguated as `benjaminm` (Moore) and `benjamino` (Ormsby) — so usernames are first-name-lowercase except for that pair.


Mon 01 Jun 2026 07:17:13 AM EDT

+ Decided on the long-term data storage approach for student chatbot data, as of today:
  - While the program runs, data stays on the secure Railway server (only Dieter has access).
  - After the program ends, the data is removed from the server and kept only as a local copy, with identifying information stored separately from the conversations AND encrypted (so the identity file is unreadable without the key — separation + encryption are two independent locks). TODO when building the post-program export: actually encrypt that identity file — it's now a promise made to students on the slide.
  - This is pseudonymization, not anonymization: the login→student key is filed apart and access-controlled but NOT destroyed, so the "you can ask to delete your data at any point" promise stays honourable. (Destroying the key would silently break that promise.)
  - Exact retention duration is intentionally left unspecified — the commitment is the process, not a number.
+ We are putting this in front of the students later today, as part of the ChatBmE explainer slide deck (covers how the chatbot works and how their data is handled).


Mon 01 Jun 2026 02:19:44 PM EDT

+ Re-synced the students table from the updated `students.ods` (TRUNCATE + reinsert). Roster went from 25 → 24 students (26 rows incl. `teacher`/`ttest`):
  - Removed (4): `diya` (Venkataragavan), `rebekah` (Stiever), `sophie` (Qiao), and the old `kesia` login.
  - Added (3): `keysia` (was `kesia` — first-name spelling was a typo, so the login changed too: kesia → keysia), `logan` (Stiever), `stuti` (Koloagi).
  - Corrected in place: `mario`'s full name was a typo, fixed Ynga Durand → Agustin (same login, same student).
+ Group split is now A=12 / B=12 (test accounts `teacher`/`ttest` stay group X). Columns unchanged; `teacher`/`ttest` untouched.
+ No real student data existed yet (program day 1), so the kesia→keysia login change and the removals carry no data loss.
Tue 02 Jun 2026 08:14:14 PM EDT

+ Switched the agent's daily topic from `getting_started.md` to `olfaction.md` (day 2): re-ran `script_configure_agents.py`, which rewrote the Anthropic file IDs (`file_registry.json`), reloaded the Mistral library, and replaced the "Today's Activity" block in `bme_agent_instructions.md` with the olfaction activity description.
+ Fixed a path bug in `script_configure_agents.py`: it assumed CWD was `agent/` (relative `agent_files/...` paths and config_manager's `.streamlit/secrets.toml` load both broke when run from the repo root). It now `chdir`s into `agent/` before the imports, so it runs from anywhere. Side effect: the run log now lands in `agent/logs/`.
