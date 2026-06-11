import logging
import pathlib

import streamlit as st
import yaml

from shared_lib.auth import lookup_student
from rubric_db import TOTAL_QUESTIONS, get_attempt_note, get_progress, record_answer
from ui_helpers import scroll_to_top

st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

# --- Guards ------------------------------------------------------------------
if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

# Re-verify the student is still active (see 1_Intro.py for rationale).
fresh_student = lookup_student(
    st.session_state.get("database_url"), st.session_state.get("student_id")
)
if fresh_student is None or not fresh_student.get("enabled", True):
    for k in list(st.session_state.keys()):
        st.session_state.pop(k, None)
    st.error("Your account is no longer active. Please contact an instructor.")
    st.stop()
st.session_state.student = fresh_student

required_keys = ("task", "task_label", "attempt")
if not all(k in st.session_state for k in required_keys):
    st.switch_page("pages/2_Tasks.py")

task = st.session_state.task
task_label = st.session_state.task_label
attempt = st.session_state.attempt
username = st.session_state.student["username"]
database_url = st.session_state.database_url

# --- Question source ---------------------------------------------------------
QUESTIONS_DIR = pathlib.Path(__file__).resolve().parent.parent / "questions"
with open(QUESTIONS_DIR / f"{task}.yaml") as f:
    task_data = yaml.safe_load(f)

# Per-task production-rubric items for the Q5 student self-rating. These mirror
# the instructor-/AI-scored production rubric in ResearchPlan.md 1:1 — same
# five items, same order — so each student's self-rating can be contrasted
# item-for-item with the actual production score (that contrast is itself a
# study output). Keep in sync with the "Production rubric: <task>" blocks in
# ResearchPlan.md; the wording here is the student-facing paraphrase.
PRODUCTION_SELF_RATING = {
    "mimic": [
        "My robot uses at least two sensors with different color filters.",
        "My robot produces the correct output color for a given input color.",
        "My code uses ratios or normalization so the response doesn't depend "
        "on overall brightness.",
        "My code handles noise (e.g. averaging or thresholding).",
        "My robot can mimic more than two distinct colors (combining "
        "channels, not just thresholding each one).",
    ],
    "approach": [
        "My robot uses at least two sensors with different color filters.",
        "My robot compares measurements between rotations to decide which "
        "way to turn.",
        "My code uses ratios or normalization so the discrimination doesn't "
        "depend on overall brightness.",
        "My code handles noise (e.g. averaging or thresholding).",
        "My robot can handle several different distractor colors, not just "
        "one specific one.",
    ],
    "taxis": [
        "My robot has two ears pointing in clearly different directions.",
        "My code compares the loudness at the left and right ears.",
        "My robot turns in the direction the louder ear indicates.",
        "My code handles noise (e.g. averaging or thresholding).",
        "My robot stops when it reaches the goal.",
    ],
    "kinesis": [
        "My robot has a single directional ear.",
        "My robot compares the measurements between rotations.",
        "My robot turns in the direction the louder measurement indicates.",
        "My code handles noise (e.g. averaging or thresholding).",
        "My robot stops when it reaches the goal.",
    ],
}

# 0–3 self-rating scale, mirroring the instructor rubric's
# absent / rudimentary / partial / clearly present, in student-facing words.
SELF_RATING_OPTIONS = [0, 1, 2, 3]
SELF_RATING_LABELS = {
    0: "0 — Not at all",
    1: "1 — Barely",
    2: "2 — Partly",
    3: "3 — Yes, clearly",
}

# --- Derive current question from the DB ------------------------------------
# The DB is the source of truth; session state only carries (task, attempt).
# Refreshing the page or coming back from a tab close still works.
progress = get_progress(database_url, username, task)

# If the DB is ahead of the attempt we have in session state, this tab is
# stale — most likely another tab (or the instructor on a shared screen)
# restarted the same task with the passcode. Refuse to render the form
# rather than silently rewriting the attempt number on submit, which would
# park the typed text under the wrong (attempt, question_no) row.
if progress["attempt"] > attempt:
    st.warning(
        "This challenge was advanced in another tab or window — possibly a "
        "restart with the instructor passcode. Reload to pick up where "
        "it stands now. Anything you started typing here will not be saved."
    )
    if st.button("Reload", type="primary"):
        for k in ("task", "task_label", "attempt", "restart_note"):
            st.session_state.pop(k, None)
        st.switch_page("pages/2_Tasks.py")
    st.stop()

if progress["attempt"] < attempt:
    current_question = 1  # No rows for this attempt yet
else:
    current_question = progress["last_question"] + 1

# A restart writes the same instructor note onto every row of the new
# attempt. Prefer the value carried in session state (set by 2_Tasks.py
# when restart was authorized); fall back to whatever's on disk so a
# refresh mid-attempt doesn't drop the note.
restart_note = st.session_state.get("restart_note")
if not restart_note and attempt > 1:
    # Fallback chain for recovering the note after session_state has been
    # dropped (tab close + reopen, etc.):
    #   1. progress["note"] reads MAX(note) FILTER (WHERE question_no = 1)
    #      from rubric_responses — works once any answer for this attempt
    #      has been written.
    #   2. rubric_attempts holds the note from the moment the restart was
    #      authorized, before Q1 was answered — covers the tab-close-
    #      between-authorization-and-Q1 case.
    restart_note = progress.get("note") or get_attempt_note(
        database_url, username, task, attempt
    )

# Reset scroll whenever the visible question (or the completion screen)
# changes. Keyed so an in-place rerun — e.g. a validation error — leaves the
# student where they were typing instead of jumping to the top.
scroll_to_top(f"survey:{task}:{attempt}:{current_question}")

# --- Completion screen -------------------------------------------------------
if current_question > TOTAL_QUESTIONS:
    st.title("Thank you")
    st.success(
        f"You've completed the **{task_label}** questions (attempt {attempt})."
    )
    st.caption("Your answers are saved.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to challenges", use_container_width=True):
            for k in ("task", "task_label", "attempt", "restart_note"):
                st.session_state.pop(k, None)
            st.switch_page("pages/2_Tasks.py")
    with col2:
        if st.button("Log out", use_container_width=True):
            for k in list(st.session_state.keys()):
                st.session_state.pop(k, None)
            st.switch_page("app.py")
    st.stop()

# --- Header ------------------------------------------------------------------
st.progress(
    current_question / TOTAL_QUESTIONS,
    text=f"Question {current_question} of {TOTAL_QUESTIONS}",
)
st.title(task_label)
st.caption(
    "Answer each question as best you can. Once submitted, you can't return "
    "to a previous question."
)

# --- Q1–Q4: free-text answer ------------------------------------------------
if 1 <= current_question <= 4:
    q = task_data["questions"][current_question - 1]

    img_path = (QUESTIONS_DIR.parent / q["image"]).resolve()
    if not img_path.exists():
        # The student can't meaningfully answer a figure-grounded question
        # without seeing the figure. Halt with an instructor-actionable
        # message rather than letting them submit blind.
        logging.error(
            "Survey image missing for %s Q%d: %s",
            task, current_question, img_path,
        )
        st.error(
            "The image for this question is missing. Please ask an "
            "instructor to look at the deployment."
        )
        st.stop()
    st.image(str(img_path))

    st.markdown(q["text"])

    with st.form(f"q{current_question}_form", clear_on_submit=True):
        answer = st.text_area(
            "Your answer",
            height=200,
            key=f"answer_q{current_question}",
            placeholder="Type your answer here...",
        )
        submitted = st.form_submit_button("Submit and continue", type="primary")
        if submitted:
            if not answer.strip():
                st.error("Please write an answer before submitting.")
            else:
                # Re-check progress at submit time. Closes the race window
                # between page render and form submit — if another tab moved
                # this task forward between the render and now, the form's
                # captured (attempt, current_question) is stale and we
                # mustn't write under those keys.
                live = get_progress(database_url, username, task)
                if live["attempt"] > attempt:
                    expected_q = None  # stale tab
                elif live["attempt"] == attempt:
                    expected_q = live["last_question"] + 1
                else:
                    expected_q = 1  # fresh attempt; no rows yet
                if expected_q != current_question:
                    st.error(
                        "This challenge changed in another tab while you were "
                        "answering. Reload the page to continue."
                    )
                else:
                    result = record_answer(
                        database_url,
                        username,
                        task,
                        attempt,
                        current_question,
                        answer_text=answer.strip(),
                        note=restart_note,
                    )
                    if result["ok"]:
                        st.toast(f"Q{current_question} saved", icon="✅")
                        st.rerun()
                    elif result.get("reason") == "duplicate":
                        st.error(
                            "Looks like this answer was already saved "
                            "(probably from another tab). Reload the page "
                            "to continue."
                        )
                    else:
                        st.error(
                            "Could not save your answer — please try again. "
                            "If this keeps happening, ask an instructor."
                        )

# --- Q5: structured wrap-up --------------------------------------------------
#
# DESIGN PRINCIPLE for every Q5 widget — read this before adding or
# replacing fields below.
#
# Each input must distinguish a real answer from "didn't touch". A
# student who clicks straight through Q5 must not look in the data like
# they actively answered with whatever value was the widget's default.
#
# Concrete rules:
#   - st.radio / st.selectbox: pass `index=None` so nothing is preselected;
#     reject the submit if the value is still None and the question is
#     required.
#   - Avoid st.slider for ordinal ratings — sliders default to a midpoint
#     that looks indistinguishable from a deliberate neutral answer. Use
#     a horizontal `st.radio` over a small integer range instead. If a
#     slider really is needed, pair it with a separate "didn't rate"
#     checkbox.
#   - Free-text (st.text_area / st.text_input): an empty string IS the
#     "didn't touch" answer — store it as None on submit so that's explicit.
#
# Q5 has three parts: (1) the chatbot-use questions, (2) the student's
# self-rating on this task's production rubric — the same five items the
# instructor/AI scorer uses, so self- vs. actual score becomes its own
# output (see PRODUCTION_SELF_RATING above), and (3) an outstanding-problems
# prompt. Any widget added later must follow the same rules so the analysis
# layer can tell skipped questions from neutral answers.
#
elif current_question == 5:
    st.markdown(
        "A few short questions to finish up the challenge you just did."
    )

    with st.form("q5_form", clear_on_submit=True):
        used_chatbot = st.radio(
            "Did you use the chatbot for this challenge?",
            options=["Yes", "No"],
            index=None,
            horizontal=True,
            key="q5_used_chatbot",
        )
        usefulness = st.radio(
            "If yes — how useful was the chatbot? "
            "(1 = not useful, 5 = very useful. Leave blank if you didn't use it.)",
            options=[1, 2, 3, 4, 5],
            index=None,
            horizontal=True,
            key="q5_usefulness",
        )
        specifics = st.text_area(
            "If yes — anything specific that helped or didn't?",
            height=100,
            key="q5_specifics",
        )
        comments = st.text_area(
            "Any other comments about the challenge?",
            height=100,
            key="q5_comments",
        )

        # (2) Self-rating on this task's production rubric. Same five items
        # the instructor/AI scorer uses; the contrast between this and the
        # actual score is a study output. Required, on the 0–3 scale, with
        # index=None so a click-through can't masquerade as a real rating.
        st.divider()
        rubric_items = PRODUCTION_SELF_RATING.get(task, [])
        self_ratings = []
        if rubric_items:
            st.markdown(
                "**How well does your own robot do each of these?** "
                "This is your own view of your robot — separate from how it "
                "will be scored."
            )
            for i, item in enumerate(rubric_items):
                self_ratings.append(
                    st.radio(
                        item,
                        options=SELF_RATING_OPTIONS,
                        index=None,
                        horizontal=True,
                        format_func=lambda v: SELF_RATING_LABELS[v],
                        key=f"q5_self_rating_{i}",
                    )
                )

        # (3) Outstanding-problems prompt. Free text — empty stored as None.
        st.divider()
        outstanding = st.text_area(
            "Is there anything you couldn't get working, or are still unsure "
            "about?",
            height=100,
            key="q5_outstanding",
        )
        submitted = st.form_submit_button("Submit and finish", type="primary")
        if submitted:
            if used_chatbot is None:
                st.error(
                    "Please answer whether you used the chatbot for this challenge."
                )
            elif used_chatbot == "Yes" and usefulness is None:
                st.error(
                    "You said you used the chatbot — please rate how useful it was."
                )
            elif any(r is None for r in self_ratings):
                st.error(
                    "Please rate your own robot on each of the items above."
                )
            else:
                # Re-check progress at submit time (same race-protection
                # logic as the Q1–Q4 path).
                live = get_progress(database_url, username, task)
                if live["attempt"] > attempt:
                    expected_q = None
                elif live["attempt"] == attempt:
                    expected_q = live["last_question"] + 1
                else:
                    expected_q = 1
                if expected_q != 5:
                    st.error(
                        "This challenge changed in another tab while you were "
                        "answering. Reload the page to continue."
                    )
                else:
                    used_chatbot_bool = used_chatbot == "Yes"
                    answer_json = {
                        "used_chatbot": used_chatbot_bool,
                        "usefulness": usefulness if used_chatbot_bool else None,
                        "specifics": specifics.strip() or None,
                        "comments": comments.strip() or None,
                        # Per-item self-rating on this task's production
                        # rubric, in the order of PRODUCTION_SELF_RATING[task]
                        # (so it lines up with the instructor rubric). Empty
                        # list if the task has no rubric defined.
                        "self_rating": self_ratings,
                        "outstanding": outstanding.strip() or None,
                    }
                    result = record_answer(
                        database_url,
                        username,
                        task,
                        attempt,
                        5,
                        answer_json=answer_json,
                        note=restart_note,
                    )
                    if result["ok"]:
                        st.toast("Q5 saved", icon="✅")
                        st.rerun()
                    elif result.get("reason") == "duplicate":
                        st.error(
                            "Looks like Q5 was already saved (probably from "
                            "another tab). Reload the page to continue."
                        )
                    else:
                        st.error(
                            "Could not save your answers — please try again. "
                            "If this keeps happening, ask an instructor."
                        )
