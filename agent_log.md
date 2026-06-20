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


Wed Jun  3 02:01:44 PM EDT 2026

+ Fixed the line-follower sensor value range in the knowledge-base docs: it was documented as returning 1–4, but the mBot sensor actually returns 0–3. Corrected across all three docs that reference it: `olfaction.md` (value table + trail-following pseudocode), `robot_details.md` (Line Sensor section), and `programming_blocks.md` (line-follower block table + comparison examples).
+ The value->action mapping is now: 0 = both detectors on line / centered -> drive forward; 1 = left detector on line / veering right -> turn left; 2 = right detector on line / veering left -> turn right; 3 = both off line / lost -> search or stop. (Note: this swapped the meaning of values 1 and 2 vs. a naive renumber of the old 1–4 table — confirmed correct mapping with Dieter.)
+ Left untouched: references to the four physical ports (1–4), which are unrelated to the sensor return value.
+ TODO / not yet deployed: these are the on-disk markdown sources. They reach students only after re-running `script_configure_agents.py` (re-uploads Anthropic file IDs + reloads the Mistral library). Until then the live agent still serves the old 1–4 text.


Wed Jun  3 02:14:46 PM EDT 2026

+ Corrected the documented robot model in the knowledge base: docs said "mBot" (4 ports, 1–4) but the program actually uses the **mBot Ranger** (5 ports: 6, 7, 8, 9, 10). Renamed the product to "mBot Ranger" in `robot_details.md`, `sonar.md`, `olfaction.md`, `touch_whiskers.md` (programming_blocks.md / getting_started.md never named the product).
+ Fixed the mBlock device-selection guidance in `robot_details.md`: select `mBot Ranger`, NOT the plain `mBot`. (mBot2 is never used in this program, so it is not mentioned anywhere in the docs.)
+ Port numbers updated everywhere 1–4 -> 6–10 (five ports). Per Dieter: any sensor can go on any port; the rule students must follow is selecting the matching port in the software block. So I removed hard per-sensor port assignments (sonar=port1, line=port2, whiskers=port3/4) in favor of "any of ports 6–10, match it in the block." Concrete code examples standardized on port6.
+ Judgment calls (flagged to Dieter): (a) rewrote the robot_details.md port-capability table so all five ports accept any sensor and dropped the color-label column — the old per-port restriction (Gray-only on 3/4) contradicted "any sensor on any port," and I could not verify the Ranger color labels; (b) onboard-sensors list in robot_details.md updated to the Ranger's set — added 3-axis gyroscope (already used in getting_started.md's tilt challenge), sound sensor, and temperature sensor; corrected "2 RGB LEDs" → "programmable RGB LEDs" and gave the onboard light sensor its 0–1000 range. (Earlier in this session it was left as the basic-mBot set; Dieter then asked to update it.)
+ Fixed `getting_started.md`: it listed the sonar (ultrasonic) sensor among the robot's *onboard* features. Per Dieter the sonar is NOT onboard — it's an external sensor plugged into a port (6–10). Reworded so the onboard list is RGB LEDs / light sensor / gyroscope, with the sonar called out as external.
+ Also updated `manifest.toml`: robot_details title "mBot Robot — …" → "mBot Ranger — …" and its description ("connect the mBot" → "connect the mBot Ranger"), since the manifest title/description is baked into the uploaded content blocks.
+ DEPLOYED: ran `script_configure_agents.py` (via `.venv/bin/python` — system/miniforge python lacks `toml`). It rewrote the Anthropic file IDs in `file_registry.json` and reloaded the Mistral library. NOTE: the script only loads the **current day's activity doc + the always-on reference docs** — today that's `olfaction.md`, `robot_details.md`, `programming_blocks.md`, `faculty_and_staff.md`. So the fixes are LIVE only in those. Edits to `sonar.md`, `touch_whiskers.md`, and `getting_started.md` are committed-to-disk but will not reach students until those activities become the daily topic and the script re-runs then.
+ ACTION REQUIRED: `anthropic_lib/file_registry.json` was rewritten with new file IDs (old IDs deleted from the Anthropic workspace). It must be committed and pushed or the deployed app will reference dead file IDs.


Wed Jun  3 03:27:48 PM EDT 2026

+ Document technical-review pass. Found and fixed issues the earlier sweeps missed:
  - olfaction.md Biology-Robot table: stale line-sensor values "reads 4"->3 (gap/lost) and "reads 1"->0 (intersection/centered). These were LIVE (olfaction is the active day).
  - robot_details.md whisker section: "Attach to ports 3 or 4" -> "any of ports 6–10" (missed earlier because the sweep regex did not catch the plural "ports"; this section contradicted the port table rewritten two sections above). Also LIVE.
  - touch_whiskers.md obstacle-avoidance pseudocode: step 2 comparison was inverted ("both < threshold -> forward"); since bending lowers the value, < threshold = bent, so it said "both bent -> forward" AND duplicated step 5's condition with the opposite action. Rewrote the block with correct comparisons + else-if ordering (neither bent -> forward; both bent -> reverse; single -> turn away).
  - touch_whiskers.md obstacle table: wheel-speed notes were inverted for differential drive ("turn right (slow left, speed right)" actually turns left). Fixed to "turn right (speed left, slow right)" / "turn left (speed right, slow left)". (Dieter confirmed M1=left/M2=right is the wiring students are instructed to use, so this fix is correct.)
  - touch_whiskers.md wall-following: "If value above resting" -> "at/near resting" (value cannot exceed resting since bending only lowers it).
  - sonar.md: dolphin range "0–150 kHz" -> "roughly 0.2–150 kHz" (0 kHz not physical).
+ Reviewed color_vision.md and faculty_and_staff.md: no technical issues.
+ touch_whiskers.md is not in the current (olfaction) active set, so its fixes are on-disk only until that activity day; olfaction.md and robot_details.md fixes require a configure re-run to go live.


Wed Jun  3 04:42:41 PM EDT 2026

+ Extended the color vision knowledge base with the two web-based color games from Color_Vision_Games_Knowledge_Base.docx (dropped into the project root). Added to color_vision.md as **Activity 3: RGB Codebreaker** (additive mixing / RGB sliders / score-is-a-game-metric, Easy-Hard modes, Check-Match-before-Next, reveal shows name+RGB) and **Activity 4: Color Constancy Challenge** (same/different physical-vs-perceptual judgment, reveal-on-neutral-background as the teaching moment). Plus a new Biology–Engineering Connections table covering both games.
+ Condensed the docx into the repo house style (concise sections + embedded Agent Notes Q&A + troubleshooting inside each activity) rather than pasting the ~2,500-word verbose chatbot-guidance prose verbatim. Decision (confirmed with Dieter): integrate into the existing color_vision.md as one module rather than a separate doc; condense rather than keep all detail.
+ Flagged in the doc: the Color Constancy Challenge section reflects the *planned* classroom version of the game; if the shipped app differs, support should anchor on the concept, not interface details (the docx itself carried this caveat).
+ Updated manifest.toml color_vision description to mention both web games (title/description are baked into the uploaded content blocks). NOT YET DEPLOYED: script_configure_agents.py not run — color_vision is not the current daily topic (olfaction is), so these edits are on-disk only until the color vision activity day, when the configure script re-runs and picks them up.


Wed Jun  3 04:47:46 PM EDT 2026

+ Reordered color_vision.md activities (Dieter's call): the two web games now come FIRST as Activity 1 (RGB Codebreaker) and Activity 2 (Color Constancy Challenge), followed by Activity 3 (Human Color Discrimination, the goggle game) and Activity 4 (Robot Color Discrimination). Web games are the gentler familiarization step, so they precede the hands-on goggle/robot work. Also reordered the intro sentence to match and fixed the '1-pixel RGB camera' cross-reference in the robot section (was 'connection between Activity 1 and Activity 2'; now names the human goggle game as Activity 3). Still on-disk only — not deployed (color vision is not the current daily topic).


Wed Jun  3 04:54:17 PM EDT 2026

+ Correction (Dieter): the two color games (RGB Codebreaker, Color Constancy Challenge) run from a LOCAL HTML file on each student's own computer — NOT a deployed web app (no server, login, or internet). Updated color_vision.md: headings '(Web Game)' -> '(Local HTML Game)', intro + each activity's opening line now say 'browser game opened from a local HTML file', and added a troubleshooting bullet (double-click the correct .html file; there is no web address). Still on-disk only — color vision is not the current daily topic.


Wed Jun  3 08:03:32 PM EDT 2026

+ Updated the Color Vision knowledge base to match the rewritten ColorVisionApp (NiceGUI + Postgres) now deployed on Railway at https://colorvisionapp.up.railway.app. This single app is the **human color discrimination goggle game** = Activity 3 in color_vision.md (NOT the two local-HTML games in Activities 1–2; Dieter clarified that distinction). It replaced two older Anvil apps (a separate trainer + competition).
+ color_vision.md Activity 3 (Human Color Discrimination) rewritten from a generic "computer screen" description into the deployed web app: noted it needs internet (unlike Activities 1–2's local HTML), documented the TRAIN (Color Trainer) and competition modes, the scoring (10 rounds, 100 pts/round decaying with an audible clock, -10 per wrong box which also speeds the clock up, round total × difficulty multiplier Easy ×1.0 / Medium ×1.5 / Hard ×2.0), team-name submission + password-protected instructor dashboard (teachers email vanderdt@ucmail.uc.edu for access), plus a new "Troubleshooting the color discrimination game" subsection and a score-is-a-game-metric agent note. Updated the doc intro line and the manifest.toml color_vision description accordingly. Activities 1, 2, 4 left untouched.
+ NOT DEPLOYED: color vision is not the current daily topic (olfaction is), so script_configure_agents.py was not run — these color_vision.md / manifest.toml edits are on-disk only until the color vision activity day, when the configure script re-runs and picks them up.


Wed Jun  3 08:46:04 PM EDT 2026

+ Document technical-review pass (Dieter requested a re-check for outstanding errors after the earlier mBot→Ranger and line-sensor fixes). Confirmed the prior fixes are now consistent across robot_details.md, olfaction.md, programming_blocks.md (robot model, ports 6–10, line-sensor 0–3 encoding, whisker logic). Found and fixed five items, all confirmed with Dieter:
  - LED COUNT: getting_started Challenge 3 ("N = distance/10 LEDs, all on >120cm") implied ~12 addressable LEDs, but programming_blocks LED blocks only listed all/left/right (the BASIC mBot's 2-LED block). Dieter confirmed the Ranger's Me Auriga has a ring of 12 individually-addressable RGB LEDs on top (web-confirmed: LEDs 1–12). Documented the 12-LED ring in robot_details onboard outputs; corrected all four LED blocks in programming_blocks (shows-color ×2, RGB, turn-off) from "all/left/right" to "all (whole ring) or position 1–12"; added a ring note to the Challenge 3 agent note and the getting_started onboard-features line.
  - SOUND SENSOR onboard vs external: robot_details called it onboard while programming_blocks treated it as a port sensor. Per Dieter: there IS an onboard sound sensor, but the sound-localization activity uses TWO external plugged-in sensors (one per side) to compare left/right. Clarified this in robot_details (onboard list + Sound Sensor spec) and the programming_blocks sound block.
  - OLFACTION sensor wording: olfaction.md twice called the trail sensor a "light sensor"; it is the LINE FOLLOWER sensor used as an analogy for an olfactory sensor (the rest of the doc already said so). Fixed both the framing note and the "robot is smelling" misconception.
  - GYROSCOPE: getting_started/robot_details said a "3-axis gyroscope measures tilt." A gyro measures angular rate; absolute tilt needs the accelerometer. Reworded to "inertial sensor (gyroscope + accelerometer)" in robot_details onboard list, getting_started onboard line, and Challenge 4 + its agent note.
+ LINE FOLLOWER (#4) double-check: Makeblock support pages block the fetcher (403), but search confirms each probe reads 0=black / 1=white, two probes. That verifies our ENDPOINTS (value 0 = both on black = centered; value 3 = both on white = lost). The 1-vs-2 single-sided bit-order could NOT be independently confirmed from accessible pages — it is internally consistent and the steering logic is self-consistent, but worth a 30-second on-robot confirmation that value 1 (left probe on line) → turn left is the real hardware mapping.
+ RESIDUAL / not changed: (a) programming_blocks LED dropdown labels were updated by inference from the confirmed 12-LED hardware — exact mBlock dropdown text should be eyeballed in the IDE. (b) No gyro/tilt READ block is documented in programming_blocks, yet getting_started Challenge 4 uses one — optional gap to fill with the real block name. (c) Line-sensor 1-vs-2 mapping (above).
+ NOT DEPLOYED: script_configure_agents.py not re-run. olfaction.md (current daily topic) + robot_details.md + programming_blocks.md are in the always-on/active set, so they go LIVE on the next configure run; getting_started.md is on-disk only until its activity day.


Wed Jun  3 08:52:52 PM EDT 2026

+ Follow-up to the review pass (Dieter supplied the exact mBlock blocks). Corrected programming_blocks.md LED blocks to match the real Ranger IDE blocks (screenshot-confirmed): replaced the invented `LED [all/left/right] shows color` / `turn off LED` entries with the actual blocks — `all lights up with color [color]`, `turn on [N] light with color [color]`, `turn on [N] light with color [color] for [secs] secs`, and `turn on [N] light with color red/green/blue` — where `[N]` is a typed LED number 1–12 on the 12-LED ring (no all/left/right dropdown). Noted there is no dedicated off block (set color to black). Added a ring-intro line.
+ Added the previously-missing gyro block to programming_blocks.md: `onboard gyro [X/Y/Z] angle` (degrees, onboard, no port) with the note that X/Y are tilt and Z is heading. Pointed getting_started Challenge 4 at this exact block.
+ This closes the two residual flags from the prior entry (LED dropdown labels; missing gyro/tilt block). Still on-disk only; same deploy note as above (robot_details.md + programming_blocks.md are always-on, so they go live on the next configure run).


Wed Jun  3 09:06:28 PM EDT 2026

+ Aligned color_vision.md Activity 4 (Robot Color Discrimination) with the "Color vision robot" Google Slides deck Dieter is presenting tomorrow (reviewed all 21 slides). Decisions confirmed with Dieter:
  - DICHROMATIC DEFAULT: the deck builds a 2-sensor (green+blue) robot framed as "dichromatic, just like a dog," not the doc's old trichromatic "1-pixel RGB camera / three filtered sensors." Rewrote "What the Robot Is Building" + "How It Works" to lead with the 2-sensor dichromatic build (dog analogy), and replaced the RGB-only High/Low table with a green/blue dichromatic example table (showing the ambiguities: red≈no-light, yellow≈green). Kept the full 3-channel RGB table as an OPTIONAL extension ("if a group adds a red sensor") since the deck lets students add filters for harder colors (slide 16 RGB wheel). Agent notes now say "don't assume three sensors — ask how many filters."
  - WAVELENGTH: added the deck's spec that the light sensor responds to ~480–1000 nm (deep blue is at the edge → some colors harder).
  - TWO CHALLENGES THIS SESSION: deck runs exactly two challenges (Group A = Mimicking, Group B = Approach/Avoid). Added a banner before the challenges and a blockquote on Challenge 3 (Following a Colored Trail) marking it NOT part of the current session (kept for reference; agent shouldn't propose it).
  - APPROACH/AVOID: renamed doc "Challenge 2: Color Approach" → "Approach / Avoid" and added the avoid half (approach one color AND turn away from another, e.g. green vs yellow), plus the deck's "robot has one eye → turn, sample, compare" framing (the program logic already matched).
  - Updated manifest.toml color_vision description (was "1-pixel RGB camera challenge") to reflect the dichromatic-default framing.
+ Cross-check result: the deck and the doc agree on the core method (filters make sensors wavelength-selective; compare filtered channels; mimic with onboard LEDs; approach via turn-measure-compare). The mismatches were all in the doc and are now fixed.
+ NOT DEPLOYED: script_configure_agents.py not re-run. color_vision becomes the daily topic tomorrow; these edits go live when the configure script runs for the color-vision day. (Did NOT change the Notion deck — Dieter owns that; this was a one-way doc alignment to the deck.)


Wed Jun  3 09:22:51 PM EDT 2026

+ Tightened the research app (research/, the Streamlit "Check Your Understanding" app on Railway) ahead of the color-vision day, per Dieter:
  - REBRAND "Survey" → "Check Your Understanding" (Dieter's call from a few options; friendlier than "Comprehension questions", avoids sounding research-y). Updated all user-visible titles/messages: login title "BmE — Check Your Understanding" (app.py), intro title, the DB-unavailable and no-access errors, and the completion "...questions" line. Did NOT rename the page .py files (1_Intro/2_Tasks/3_Survey) — the sidebar is hidden via CSS so filenames aren't user-visible, and renaming would mean rewriting every st.switch_page target (breakage risk for no user benefit).
  - LINGO "tasks" → "Challenges" to match the presentation: every student-facing string ("Pick the challenge you just completed", "Back to challenge list", the already-started/-completed notices, the restart note placeholder, the stale-tab warnings, and the Q5 chatbot questions). Internal identifiers (TASKS list, task keys, enter_survey, question yaml filenames) left unchanged.
  - REMOVED the data-use placeholder paragraph on the intro page ("Placeholder text — ... how the data will be used ...") per Dieter; kept the real "pick the challenge, answer five questions" instructions.
  - SCROLL-TO-TOP: added research/ui_helpers.py with scroll_to_top(view_key=None) — injects a tiny components.html script that scrolls the main container to the top. Called on each page; keyed by view (login / intro / tasks:<selected> / survey:<task>:<attempt>:<question>) so it fires when the visible page/question changes but NOT on in-place reruns like a form validation error (which would otherwise yank a student away from where they were typing). Fixes students landing scrolled-down after clicking a button below the fold.
+ Verified: all five files ast-parse, and ui_helpers imports cleanly under the repo venv with streamlit. Did NOT do a full interactive run (needs the Railway Postgres + a browser).
+ DEPLOY NOTE: the research app deploys from Railway (research/start.sh); these changes go live when committed and pushed (Railway auto-deploys). Not pushed yet.


Wed Jun  3 09:26:43 PM EDT 2026

+ Scheduling deviation from ResearchPlan.md (recorded here only — the plan is intentionally LEFT AS THE ORIGINAL PLAN, not edited). The plan's "Slot schedule" (§ Latin-square reversal across two days) runs the four slots two-per-day over two days: Day 1 (Color vision) = slot 1 (chatbot on) + slot 2 (off); Day 2 (Sound localization) = slot 3 (off) + slot 4 (on). We have now decided to run **each slot on its own separate day** — one task/slot per day, four days total — instead of two slots per day.
+ Expected to be immaterial to the analysis (Dieter's read, and consistent with the plan's own notes): `day` is perfectly collinear with `task` in this design and is already dropped from the models in favor of `task`, and the chatbot order across slots — the vector [1, 0, 0, 1] — is unchanged. The main practical differences: the "second-task-of-the-day" within-day position effect becomes moot (each day now has a single task), and any carryover between adjacent slots now spans a day boundary rather than happening within a day (the on→off / off→on slot ordering is preserved either way). No app or data-schema change needed — responses are keyed by task/attempt, independent of calendar day.


Wed Jun  3 09:34:50 PM EDT 2026

+ Research app: renamed the "approach" challenge's display label "Approach Color" → "Approach / Avoid" so it matches the slides and color_vision.md (final cross-artifact consistency check before the color-vision day). Changed in pages/2_Tasks.py (TASKS label) and questions/approach.yaml (title). The task KEY stays "approach" — display-only change, so existing/future DB rows are unaffected. (Dieter confirmed RESTART_PASSCODE is set on Railway, and fixed the deck title-slide "robots"→"robot" himself.)


Wed Jun  3 09:40:01 PM EDT 2026

+ DEPLOYED the agent for the color-vision day: set daily_modules=["color_vision.md"] in script_configure_agents.py and ran it (via .venv/bin/python).
+ First run hit a TRANSIENT Mistral 500 (Internal Server Error) on the 4th library upload (color_vision.md) — left the Mistral library partial (3 of 4 docs, no description/reassign) and never reached the Anthropic section. Re-ran immediately; the second run completed cleanly: Mistral library cleared + all 4 docs re-uploaded + description updated; Anthropic deleted the old olfaction-day file set and uploaded the new 4, rewriting anthropic_lib/file_registry.json.
+ Loaded doc set is now: robot_details.md, programming_blocks.md, faculty_and_staff.md (always-on) + color_vision.md (daily). olfaction/getting_started/sonar/touch_whiskers are no longer loaded. All the recent color-vision/robot doc fixes are therefore now live on both backends.
+ Also refreshed activity_descriptions/color_vision.md (was stale — "1-pixel RGB camera"); it now describes the dichromatic-default robot (two filtered sensors, like a dog), the games, and the two challenges (Color Mimicking, Approach/Avoid). The script injected it into the "Today's Activity" block of bme_agent_instructions.md.
+ ACTION REQUIRED (Dieter is pushing): commit + push anthropic_lib/file_registry.json — the old Anthropic file IDs were deleted from the workspace, so production points at dead IDs until the new registry is pushed and Railway redeploys. (Mistral side is live API state, already updated — no push needed for it.)


Thu Jun  4 05:17:20 PM EDT 2026

+ Chat: moderation now classifies only the student's typed caption, not the assembled `content` (caption + `📎 <filename>` markers). Screenshot filenames often embed dates (phone camera naming) and were getting false-flagged as PII, blocking legitimate uploads. Image content was already excluded from moderation by design; this just stops the filename string from being classified too. Chat history, the model call, and DB logging still use the full `content` (with markers) — only the moderator input changed. One-line edit in `agent/pages/1_Chat.py` (commit cf9856a). Deploys to Railway on push.


Fri Jun  5 10:45:49 AM EDT 2026

+ CHATBOT TURNED OFF for all students (Dieter, this slot). Set `enabled` = false for every row in students.ods and re-ran `script_configure_students.py` (TRUNCATE + re-sync). Login to the chatbot now shows "Sorry, you don't have access to the chatbot at this moment."
+ NOTE: `enabled` is a SHARED access gate — it also blocks the research/survey app ("Check Your Understanding"). The survey is not being presented during this slot, so that is fine.
+ Also updated the Google Slides for today.
+ ACTION REQUIRED — RE-ENABLE BEFORE THE SURVEY: set `enabled` back to true (or blank) in students.ods and re-run `script_configure_students.py`. If this is skipped, students stay locked out of BOTH the chatbot and the survey.


Fri Jun  5 02:26:13 PM EDT 2026

+ RE-ENABLED all student accounts ahead of the survey (Dieter). Set `enabled` back to true in students.ods and re-ran `script_configure_students.py` (TRUNCATE + re-sync). Chatbot and the research/survey app ("Check Your Understanding") are both accessible again. Closes the ACTION REQUIRED from the earlier chatbot-off entry today.

Wed Jun 10 13:08

Set the instructions to sonar. Ran agent conf. and pushed.

Wed Jun 10 08:48 PM EDT 2026

+ Research app (the "Check Your Understanding" survey, research/pages/3_Survey.py): EXPANDED Q5 — did not replace the existing widgets. Q5 now has three parts:
  1. Chatbot-use questions (unchanged): used-chatbot Yes/No, usefulness 1–5, specifics, comments.
  2. NEW — student self-rating on the production rubric. Five items, per task, mirroring the instructor/AI production rubric in ResearchPlan.md 1:1 (same items, same order) so self-rating vs. actual score becomes its own study output. Items live in a new PRODUCTION_SELF_RATING dict keyed by task (mimic/approach/taxis/kinesis), student-facing wording, on a 0–3 scale (Not at all / Barely / Partly / Yes, clearly) mapping to the rubric's absent/rudimentary/partial/clearly present. Each item is a required horizontal st.radio with index=None (submit rejected if any is None) — follows the file's "distinguish answered from didn't-touch" design rule. Stored in answer_json["self_rating"] as a 5-element list in rubric order.
  3. NEW — outstanding-problems free-text prompt ("anything you couldn't get working, or are still unsure about"). Empty stored as None. answer_json["outstanding"].
+ Closes the "Finalize Q5 items" outstanding task. Updated ResearchPlan.md §Learning rubric design (Q5 now documented as deployed, three parts) and ticked the Outstanding-tasks checkbox.
+ Verified: file AST-parses under the repo venv; the four PRODUCTION_SELF_RATING keys match the four questions/*.yaml task keys and each has exactly 5 items. No interactive run (needs Railway Postgres + browser).
+ DEPLOY NOTE: research app deploys from Railway on push (research/start.sh) — not committed/pushed yet. answer_json gains two new keys (self_rating, outstanding); no DB schema change (Q5 already stored a JSON blob).


Wed Jun 10 09:05 PM EDT 2026

+ Research app: relabeled the two sound-localization challenges in the task picker (Dieter). "Kinesis Sound Localization" -> "One Ear", "Taxis Sound Localization" -> "Two Ears". Display-only: changed the TASKS label in research/pages/2_Tasks.py and the title in questions/kinesis.yaml + questions/taxis.yaml. Task KEYS (kinesis/taxis) unchanged, so VALID_TASKS, the DB CHECK constraints, PRODUCTION_SELF_RATING, and existing/future rows are unaffected (same pattern as the earlier Approach Color -> Approach / Avoid rename). ResearchPlan.md keeps the formal construct names Kinesis/Taxis. Deploys on push.


Wed Jun 10 10:15 PM EDT 2026

+ PREP (NOT DEPLOYED): built the sound-localization knowledge for the agent ahead of the sound-localization days, against Dieter's draft + the just-edited "Sound localization robot" Google Slides + the kinesis/taxis rubrics in ResearchPlan.md.
  - NEW agent/agent_files/documents/sound_localization.md — full RAG doc (house format). Covers: loudness-only/phasic/omnidirectional sound sensor; external-ear solution (bigger ears = more directional; encourage 10–20 cm, not tiny); systematic directionality calibration (semi-quiet spot, fixed distance, several azimuths, write down readings, compare to expected pattern — agent should ask the student for their numbers); the one-eared (rotate-sample-compare) and two-eared (compare L vs R) approach algorithms straight from the slides; averaging + stepwise stop-measure-move motion; optional stop-at-target. Internal note tells the agent NOT to say "kinesis"/"taxis" and to ask how many ears a student is building.
  - NEW agent/agent_files/activity_descriptions/sound_localization.md — the "Today's Activity" injection.
  - manifest.toml — added [sound_localization] entry.
  - FIXED factual errors in the always-on docs (robot_details.md, programming_blocks.md): removed the wrong "the activity uses two sensors / you cannot localize with a single sensor" claims (they'd have told the one-eared group their task is impossible), and removed the wrong "sound sensor needs the Light Sound extension" claim (it's available out of the box). Both now describe the one-ear and two-ear builds correctly and "never the onboard mic."
  - robot_details.md — added general guidance on using the 12-LED ring as program-state feedback (color/specific LEDs per branch/step/decision) as a debugging aid for any activity.
+ STILL LIVE: sonar.md remains the daily module (daily_modules unchanged) — students are still finishing sonar. None of the above reaches the agent until script_configure_agents.py is run with daily_modules=["sound_localization.md"] for the sound-localization day (the chatbot-ON day; the first sound day is chatbot-off). Committed + pushed to git as source only; no configure run, so production behavior is unchanged.

Thurday June 11 12:55 EDT 2026

Deactivated the accounts as the first sound-localization day is chatbot-off.
Also set the topic to sound localization
Thursday June 11 2026 (later)

+ Knowledge-base wording fix (Dieter): in agent/agent_files/documents/touch_whiskers.md, named the mBlock block explicitly in the two spots that referred to it generically as "the light sensor block" (Hardware Setup intro + the "Use the light sensor block" Agent Note). Both now use the exact label `light sensor [dropdown] light intensity` to match how it is documented in programming_blocks.md (line 109). Content/meaning unchanged — still ports 6–10, still "bending decreases the value." Source-only edit; does not reach the agent until a configure run.

+ Knowledge-base addition (Dieter): added a "The Three Challenges (students choose)" subsection at the top of Activity 2 in agent/agent_files/documents/touch_whiskers.md, sourced from the current "Whisker Robot" Google Slides deck (the one preceding the activity, modified 2026-06-12). Documents that students PICK among three challenges (1: obstacle avoidance / ≥2 whiskers; 2: wall following / 1 whisker; 3: more whiskers / open-ended extension) with no required order. Agent Notes tell the agent to ask which challenge first and tailor help, and frame Challenge 3 as an open-ended extension tied to whisker arrays + the sensor-count tradeoff. The obstacle-avoidance and wall-following LOGIC was already in the doc; this adds the choice framing + the standalone Challenge 3. Source-only edit; does not reach the agent until a configure run.

+ Reframed the whisker-challenges subsection in touch_whiskers.md (Dieter): now TWO challenges (1: obstacle avoidance, 2: wall following) plus "more whiskers" as an open-ended EXTENSION that applies to either challenge, rather than three standalone challenges. Matches Dieter's intended deck reframing. NOTE: the live "Whisker Robot" Google Slides deck still showed the old three-separate-challenges layout when checked (2026-06-12) — Dieter said he'll rephrase the slides; doc was updated ahead of that. Still source-only; no configure run.

+ Sound-localization doc — sensor matching (Dieter): added coverage for two-eared robots whose two sound sensors don't read equally for the same sound (intrinsic sensitivity variation, present even with no/identical ears; ears add more mismatch). agent/agent_files/documents/sound_localization.md now has: (a) a new "## Match the Two Sensors (Two-Eared Robots Only)" section before Challenge A — explains the symptom (drifts to one side at center), and the fix (measure averaged L_avg/R_avg under the same sound, compute a correction factor, multiply/divide one sensor in the program so equal sound -> equal corrected readings, then compare corrected values; one-eared robots don't need this since the offset cancels); (b) a Challenge B agent note pointing to it; (c) two new Challenge B troubleshooting rows; (d) a new misconception ("my two sensors should read the same"). Source-only; no configure run.

+ Ran script_configure_agents.py (daily_modules=["sound_localization.md"]). Pushed the updated knowledge base — including today's sound_localization.md edits (two-eared sensor-matching / gain-equalization content) — to BOTH backends. Mistral library cleared + re-uploaded (live immediately). Anthropic Files API: old 4 files deleted, 4 re-uploaded, anthropic_lib/file_registry.json rewritten with new IDs. Today's Activity instructions section unchanged (already sound localization from the June 11 run). touch_whiskers.md edits (challenge reframe, light-sensor block name, decreasing-value wording) are NOT deployed — touch_whiskers is not in daily_modules/shared_documents, so it ships only when its day is configured. ACTION NEEDED: commit + push anthropic_lib/file_registry.json so production's Anthropic backend references the new file IDs (old ones already deleted from the Anthropic workspace).


Sun 14 Jun 2026 12:31:01 PM EDT (Claude)

+ Added a new activity to the agent's knowledge base: **final_project** — the self-selected capstone. Students design their own robot challenge using any one, or any combination, of the senses already covered (color vision, touch/whiskers, sonar, olfaction/line following, sound localization).
  - New knowledge doc `agent/agent_files/documents/final_project.md` (cross-cutting, no new biology — recaps the five senses, gives a scope/design process, covers combining senses across the 5 ports + writing a "which sense wins" priority rule, and ends with a senses-available recap table instead of a single-sense Biology-Robot Connections table).
  - New activity description `agent/agent_files/activity_descriptions/final_project.md` (the "Today's Activity" blurb).
  - Manifest entry `[final_project]` added to `agent/agent_files/documents/manifest.toml`.
  - Updated the stale "Available modules" comment in `script_configure_agents.py`.
+ NOT deployed: `daily_modules` is unchanged (still sound_localization) and `script_configure_agents.py` has not been re-run, so the new doc is available to set as a future activity but is not yet uploaded to Mistral/Anthropic. To deploy: set `daily_modules = ["final_project.md"]`, run the script, then commit/push `file_registry.json`.

  Update (same day): reworked how the final project loads its sense knowledge.
  Rather than loading all five full sense docs on capstone day, added a single
  companion reference `agent/agent_files/documents/sensor_toolkit.md` that, per
  sense, gives: a one-line biology hook, **what students already built** with it
  (so the agent can say "remember you did obstacle avoidance with sonar? reuse
  that pattern"), the sensor + exact mBlock block + value meanings, calibration/
  reuse steps, and the top troubleshooting items. The hands-on *biology*
  activities (goggle game, termite observation, two-point discrimination) were
  dropped — they don't transfer to a robot build. Built by extracting from each
  sense doc; manifest entry `[sensor_toolkit]` added. `final_project.md` now
  points at `sensor_toolkit.md` instead of the five individual docs.
  Capstone-day deploy is therefore: daily_modules = ["final_project.md",
  "sensor_toolkit.md"] (2 docs, not 6). Still NOT deployed.


Tues 14:15 PM EDT 2026 (Dieter)

Updated to final project


Sat Jun 20 01:25:43 PM EDT 2026 (Claude)

End-of-program data export. Program has ended; downloaded all 7 Postgres tables to `collected_data/database/` via new script `script_export_collected_data.py` (read-only against the DB; re-runnable). Three parts:
+ `raw/` — full-fidelity master copy WITH names + password hashes + the 71 attachment image files. Stays inside the encrypted folder; never shared.
+ `anonymized/` — shareable pseudonymized copies. Each login string -> stable pseudonym (S01..S30), same person same id across ALL tables (linkage preserved). Dropped: password_hash, students.full_name, student_settings.full_name (group A/B kept), attachment image bytes (metadata kept). Free-text scrubbed of roster names -> [NAME]. Verified 0 name leaks in this set.
+ `identity_key/pseudonym_map.csv` — pseudonym<->username<->full_name lookup + redaction_report.json. This is the recoverable key the data-retention promise requires (kept, not destroyed, so deletion-on-request stays honourable). Never leaves the encrypted folder unless IRB approves.
Pseudonymization, not anonymization, per the 2026-06-01 commitment. collected_data/ is gitignored.
Still TODO (Dieter): (1) encrypt the whole collected_data folder with TrueCrypt; (2) remove the data from the Railway server now that the local copy exists (the post-program server-deletion half of the policy).
