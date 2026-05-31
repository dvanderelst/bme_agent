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