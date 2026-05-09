# ChatBot Educational Research — handoff context

This document hands off the design state of an educational research study so a fresh Claude session can pick up without rebuilding context.



---

## 1. What we are studying

We are running an educational research study on whether an AI chatbot, deployed in a biorobotics course, helps students. We distinguish two effects:

- **Performance** — students accomplish more *while the chatbot is available*.
- **Learning** — students internalize understanding that *persists after the chatbot is removed*.

The interesting scientific question is the dissociation between the two: it is possible for the chatbot to help with production (good code is produced) without teaching (the student doesn't actually understand the code). Reporting both effects with uncertainty lets us characterize the chatbot's pedagogical role.

The course context: ~24 undergraduate students, two robotics modules — color vision (Day 1) and sound localization (Day 2). Each module has two tasks (color: Mimic and Approach; sound: kinesis and taxis). The chatbot is a two-agent Mistral backend; details aren't relevant for the design.

## 2. Experimental design

### The constraint

Whole-class chatbot toggle. Cannot have different students in the same room with chatbot on/off simultaneously. So the manipulation is at the class level.

### The adopted design — Latin-square reversal across two days

Class is split in half (Half A, Half B). Within each day, the two halves do the two tasks in opposite order. Across days, the chatbot order is reversed.

| Slot | Day                        | Chatbot | Half A task    | Half B task    |
| ---- | -------------------------- | ------- | -------------- | -------------- |
| 1    | Day 1 (Color vision)       | on      | Mimic Color    | Approach Color |
| 2    | Day 1 (Color vision)       | off     | Approach Color | Mimic Color    |
| 3    | Day 2 (Sound localization) | off     | Kinesis        | Taxis          |
| 4    | Day 2 (Sound localization) | on      | Taxis          | Kinesis        |

Each slot ends with an assessment (both production rubric on the artifact + learning probe answered by the student).

### Identification argument

Read in temporal slot order, the chatbot manipulation is the vector **[1, 0, 0, 1]**.

- **Cancels:** any confound whose 4-slot pattern is orthogonal to [1,0,0,1]. This includes monotonic time-on-robot (1,2,3,4), within-day position effects that repeat across days (1,0,1,0), and uniform day-level shifts (0,0,1,1). Equivalently, anything that decomposes additively into `day + within-day position` washes out.
- **Does NOT cancel:** Day × position interactions. The most likely such interaction is **asymmetric carryover** — chatbot-imparted knowledge persisting from chatbot-on to chatbot-off (Day 1 effect attenuation), and generic practice from chatbot-off to chatbot-on (Day 2 effect inflation). If these are roughly equal, they cancel; if not, residual bias remains.
- **Diagnostic:** report Day 1 and Day 2 chatbot effects separately before pooling. Close agreement → small or symmetric carryover. Divergence → the fingerprint of asymmetric carryover, and pooled estimate is biased.

## 3. Assessment structure

Two tracks per slot, targeting different constructs:

| Track      | What it measures                  | Scored by                 | Scored from               |
| ---------- | --------------------------------- | ------------------------- | ------------------------- |
| Production | Chatbot-aided production quality  | Instructor / AI           | Code + robot photo        |
| Learning   | Student's persisted understanding | AI (pairwise comparisons) | Student's written answers |

Critical: **probes are answered without chatbot access in both conditions.** Otherwise the learning track becomes another assistance measurement.

## 4. Rubrics — current state

### Production rubrics

Each item scored 0–3: absent / rudimentary / partial / clearly present. Max 15 per rubric.

The four production rubrics are designed in parallel structure: items 1–2 capture hardware/setup, items 3–4 capture algorithmic reasoning, item 5 captures behavioral sophistication. They are listed in detail on the Notion page.

**Sound — Taxis:** ears with divergent acoustic axes; left/right comparison; rotation sign matches IID sign; noise handling; stopping at goal.

**Sound — Kinesis:** single directional ear; comparison between rotations; rotation sign matches loudness difference sign; noise handling; stopping at goal.

**Color — Mimic:** ≥2 sensors with different filters; correct output color for input color; intensity-invariance via ratios/normalization; noise handling; ability to mimic >2 distinct colors (requires combining channels).

**Color — Approach:** ≥2 sensors with different filters; comparison between rotations to decide direction (klinotaxis structure, since the robot can only fit one "cone cell" of multiple sensors); intensity-invariance; noise handling; ability to handle multiple distractor colors (template matching, not single-channel comparison).

### Learning rubrics — sound

Originally a single shared rubric with 4 generic open-ended questions. Recently undoubled and redesigned into image-based scaffolded prediction questions.

**Kinesis — DONE.** Four image-based prediction questions forming a scaffold from "bare microphone gives no directional info" through "directional ear has a tuning curve" to "the rotation that increased the signal points toward the source." Each question is a separate page; no going back.

**Taxis — TO BE DESIGNED.** Should follow a parallel scaffold but built on simultaneous (two-eared, single-moment) rather than sequential (one ear, multiple rotations) comparison. Suggested arc: bare mics → mics-with-pinnae give IID → IID across source positions → decision rule from L vs R. This is the next concrete task.

### Learning rubrics — color

Currently 4 generic open-ended questions in the older style. **Probably worth redesigning in the same image-based scaffold style we used for kinesis** — but we deferred this to focus on sound. Open question: do we redesign these too, or leave them as-is?

## 5. Scoring plan

**Production rubrics:** sum of 5 items per slot → 0–15 score per slot per student.

**Learning rubrics:** the open-ended responses are too noisy for direct numeric scoring. Plan:

1. Anonymize all responses (strip condition, day, student name).
2. Use **Adaptive Comparative Judgement (ACJ)** to pick informative pairs of responses for a given question and have AI judges (multiple models, multiple rounds) decide which is better.
3. Aggregate the pairwise judgments via **Bradley-Terry** (or Elo) to produce an interval-level score per response.
4. Z-score within question to align scales across the four learning questions per module.

ACJ is the educational-assessment branch of active ranking — picks pairs that maximally reduce uncertainty, gets stable rankings in ~10–15×N comparisons rather than full pairwise (which would be O(N²)).

## 6. Analysis plan

Bayesian mixed models, two of them, same predictor structure:

**Production model:**

sum_score (0–15) ~ chatbot + day + position + task + (1|student)

**Learning model:**

z_BT_score ~ chatbot + day + position + task + (1|student) + (1|question)

Where `position` is within-day position (slot 1 vs slot 2 within a day, i.e., 0/1 — not the across-day temporal index, which would be redundant with day + within-day-position).

**Dissociation:** derived from the posterior difference of the chatbot effect across the two models. Since both models are fitted on the same students, this is a within-subject contrast.

**Carryover diagnostic:** same models fit with `chatbot × day` interaction, examined separately.

**Reporting philosophy:** estimation, not NHST. The PI explicitly does not want p < 0.05 framing — wants effect sizes with credible intervals, and characterization of the dissociation (which can be small, large, positive, negative, or zero — all informative). Use weakly informative priors (e.g., Normal(0,1) on standardized coefficients).

**Power/precision concern:** with N=24, intervals will be informative for medium-large effects (d > ~0.6) and noisy for small ones. Worth a simulation before running. The dissociation interval will be wider than either main-effect interval.

## 7. Methodological safeguards (on Notion page)

- Probes answered without chatbot access regardless of condition.
- Production scoring blinded to condition and day (randomized IDs, key sealed).

(Prior versions of the page had longer safeguards lists; the PI trimmed them on the grounds that the rest is self-evident to colleagues.)

## 8. Working style / collaborator preferences

These matter for future Claude sessions.

- **The PI (Dieter) wants estimation, not hypothesis testing.** Avoid p-values and binary verdicts. Frame outcomes as point estimates with credible intervals. He specifically dislikes p < 0.05 framing.
- **Notion page wants telegraph-style.** A callout at the top says "Keep sentences and text on this page brief and telegraph-style. Ask me before editing." Respect both. The detailed prose belongs in chat; the page wants compact summary form.
- **He pushes back on imprecise wording and unsupported claims.** Several questions on the page were rewritten because their initial phrasing was vague or because the wording let students give shallow answers. Take this as a feature — when he challenges something, the answer is usually that the wording or the framing needs sharpening.
- **He likes scaffolded conceptual progression in question design.** The kinesis learning rubric was deliberately built so each question builds on the previous one's setup, so by Q4 the student has reconstructed the algorithm from first principles. The "no going back" structure of the assessment supports this.
- **Quantitative literacy is high.** Don't dumb down statistical concepts. Bradley-Terry, ACJ, mixed models, posterior contrasts — all fair game.
- **Direct, economical communication.** No throat-clearing. Targeted edits, not wholesale rewrites. When he asks for an MD or a new section, give the actual artifact, not a meta-discussion of what the artifact will contain.

## 9. Outstanding work

In rough priority order:

1. **Design the taxis learning rubric** following the parallel-but-simultaneous scaffold (see §4 above). Image-based prediction questions, four questions, parallel arc to kinesis.
2. **Decide whether to redesign the color learning rubrics** in the same image-based scaffold style. Currently they're in the older generic open-ended format.
3. **Power simulation** with plausible effect sizes to estimate credible interval widths on the chatbot effect (each track) and the dissociation.
4. **Image generation** — the kinesis questions reference specific schematic robot images that don't exist yet. Rough hand-drawn or simple diagrams suffice; they need to be created before deployment.
5. **A few minor items on the Notion page's "Outstanding tasks" checklist** (digitize surveys, observation notes, etc.) — these are operational rather than design issues.

## 10. Don't-redo list (decisions that are settled)

- Whole-class toggle constraint accepts the within-subject Latin-square reversal design. Don't relitigate alternatives like between-class designs or single-day designs.
- Rubrics scored by AI (with human spot-checks) is preferred to rater pairs — the PI is happy with AI scoring as the primary and dislikes IRR-by-multiple-humans as a heavy lift for limited gain.
- Production rubric items dropped: a separate "ports/wiring correctness" item was removed (students who get this wrong will fail everything else anyway), and a "stopping/holding the matched color" item was removed from Mimic (the robot doesn't need to move there).
- Learning rubric questions are open-ended (with image-based scaffolding) rather than multiple choice. Briefly considered MC, decided that the image and concrete setup do enough scaffolding to prevent shallow answers, and the open format preserves the depth signal.
- Each learning probe question goes on a separate page; students cannot go back to revise.

---

When picking up this work, fetch the Notion page first for the current state, then refer back to this doc for context on why things are the way they are.
