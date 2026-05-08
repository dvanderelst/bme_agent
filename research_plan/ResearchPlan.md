# ChatBot Educational Research

# Outstanding tasks

*Personal to-do list — chatbot-code and study-design items I want to tackle. Collaborators can skip this section.*

- [x] Ensure the settings are logged.
- [x] Sign in to the chatbot
- [x] Way to disable chatbot
- [x] Enable task awareness in chatbot (subject dependent) and student name aware —> Not really needed
- [ ] Digitize surveys → task aware?
- [ ] Note/talk about observations
- [ ] Better questions
- [ ] Consider the decline in data quality.
- [x] Show name at top

# Research question

Does access to an AI chatbot during a robotics programming task improve students' ability to solve the task? We distinguish two possible effects:

- **Performance** — students accomplish more when the chatbot is available in real time.
- **Learning** — students internalize understanding that persists after the chatbot is removed.

The two are not the same, and that is the point. The chatbot could plausibly produce *better robots without better understanding*: students might implement what the chatbot suggests, end up with programs that work, and have little grasp of why. The reverse is also possible — students forced to think hard about the chatbot's suggestions could end up understanding the material better even when the produced artifact is no different. Measuring only one of the two would miss this dissociation. We therefore measure both, treat them as separate constructs, and let the contrast between them be one of the study's main outputs.

# Study design

Below, I first sketch the ideal design — what we would run if practicalities allowed — and then the design we actually adopt. The latter is not confound-free, but it is constructed to be robust against the confounds most likely to matter in a class of this size and structure.

## The ideal design

Ideally we would split the class into four independent groups and counterbalance two factors across them: **chatbot order** (on→off vs. off→on) and **task order** (T1→T2 vs. T2→T1). Crossing these two factors produces four condition sequences, one per group, so that every student does both tasks under both chatbot states, but the two orderings are decoupled across the class:

| Group 1        | Group 2        | Group 3        | Group 4        |
| -------------- | -------------- | -------------- | -------------- |
| T1/ChatBot on  | T2/ChatBot on  | T1/ChatBot off | T2/ChatBot off |
| T2/ChatBot off | T1/ChatBot off | T2/ChatBot on  | T1/ChatBot on  |

This is impractical because the chatbot toggle and task assignment both occur at the class level: 24 students in one room cannot run different conditions simultaneously. The design adopted below is the closest counterbalanced approximation we can run inside that constraint.

## Latin-square reversal across two days

Two structural facts force the shape of this design. The chatbot has to be on or off for the whole room at any given moment, so chatbot can only vary *across* slots, not within. And the course already runs two modules on two separate days (color vision, then sound localization), each with two distinct tasks — giving us four natural slots, two per day.

Within those constraints we adopt the following layout. We split the class in half and flip which chatbot state comes first across days; within each day, the two halves complete the tasks in opposite order. Every student then experiences both chatbot states and both tasks per module, and task order is counterbalanced with respect to chatbot state.

**Slot schedule.**

| Slot | Day                        | Chatbot | Half A task    | Half B task    |
| ---- | -------------------------- | ------- | -------------- | -------------- |
| 1    | Day 1 (Color vision)       | on      | Mimic Color    | Approach Color |
| 2    | Day 1 (Color vision)       | off     | Approach Color | Mimic Color    |
| 3    | Day 2 (Sound localization) | off     | Kinesis        | Taxis          |
| 4    | Day 2 (Sound localization) | on      | Taxis          | Kinesis        |

Each slot in the schedule ends with two pieces of data collection. For the production rubric we collect each student's robot program and a photo of their robot. For the learning rubric, students answer the rubric questions for that slot's task via an online survey, without chatbot access.

**What this layout buys us.** Reading the chatbot column top to bottom, the chatbot manipulation in temporal order of slots is the vector **[1, 0, 0, 1]**. Any confound whose 4-slot pattern is orthogonal to this vector cancels in the chatbot contrast. Concretely, that includes:

- Monotonic time-on-robot effects (pattern [1, 2, 3, 4]) — students get better with practice across slots.
- Within-day position effects that repeat across days (pattern [1, 0, 1, 0]) — e.g., students always perform a bit worse on the second task of the day.
- Uniform day-level shifts (pattern [0, 0, 1, 1]) — e.g., a Day-2 mood or fatigue effect.

Equivalently, anything that decomposes additively into `day + within-day position` washes out.

**What it does not fix.** Day × position interactions — effects whose 4-slot pattern correlates with [1, 0, 0, 1] — do not cancel. The most plausible such interaction is **asymmetric carryover**: chatbot-imparted knowledge persisting from chatbot-on into chatbot-off (Day 1: attenuates the chatbot effect) versus generic practice carrying from chatbot-off into chatbot-on (Day 2: inflates the chatbot effect). If these two carryovers are roughly equal, they cancel; if not, residual bias remains.

**Diagnostic.** We report the Day 1 and Day 2 chatbot effects separately before pooling. Close agreement is consistent with small or symmetric carryover. Divergence is the fingerprint of asymmetric carryover, and the pooled estimate should be read with that bias in mind.

## Design notes

Students will have had experience with the chatbot before we roll out the design below. This gives them some time to get used to using it. We will also have data on their chatbot usage prior to the start of our experimental protocol.

# Assessment

We will assess whether the chatbot improves (1) production and (2) learning and understanding.  

| Construct  | Scored by                 | Scored from               |
| ---------- | ------------------------- | ------------------------- |
| Production | Instructor / AI           | Code + robot photo        |
| Learning   | AI (pairwise comparisons) | Student's written answers |

### Methodological safeguards

- Students answer the learning rubric questions without chatbot access, in both conditions. Otherwise the learning track collapses into another performance measurement.
- Scoring of production rubrics should be blinded to condition and day.

### Learning rubric design

The current image-based scaffolded format is a deliberate move away from two alternatives. Earlier versions used generic open-ended prompts (e.g., "explain how the robot decides which way to turn"), which gave students too much room for shallow handwaving. The image plus concrete numerical setup pins down the situation and forces a specific prediction.

Multiple-choice was also considered and rejected. MC would require designing distractor options that anticipate every interesting wrong answer — work the image-based scaffolding does without losing the depth signal that open-ended responses preserve.

### Scoring plan

- **Production rubrics.** Each item 0–3: absent/rudimentary/partial/clearly present.
- **Learning rubrics.** Pairwise comparison of anonymized answers. Adaptive Comparative Judgment (ACJ) to pick informative pairs — stable ranking in ~10–15×N comparisons rather than full pairwise. Multiple rounds / multiple AI models as judges; aggregate via Bradley-Terry to get interval scores.

### Analysis plan

Two Bayesian mixed models, same predictors, different outcomes:

- **Production:** `sum score (0–15) ~ chatbot + day + position + task + (1|student)`
- **Learning:** `z-scored BT score ~ chatbot + day + position + task + (1|student) + (1|question)`

Reporting is in estimation terms — point estimates with credible intervals — not null-hypothesis testing. We do not threshold on p-values. The dissociation between the chatbot's production and learning effects is reported as a posterior contrast across the two models, with its own credible interval.

## Color vision assessment tools

### Production rubric: Mimic Color

*Scored from each student's robot program plus a photo of their robot, collected at the end of the slot in which they performed Mimic Color. Items rated 0–3 (absent / rudimentary / partial / clearly present); maximum 15.*

1. Are at least two sensors with different color filters used
2. Does the robot produce the correct output color for a given input color
3. Does the code use ratios or normalization to make the response intensity-invariant
4. Is there a mechanism for noise handling (averaging, thresholding)
5. Can the robot mimic more than two distinct colors (requires combining channels, not just thresholding each independently)

### Production rubric: Approach Color

*Scored from each student's robot program plus a photo of their robot, collected at the end of the slot in which they performed Approach Color. Items rated 0–3; maximum 15.*

1. Are at least two sensors with different color filters used
2. Does the robot compare measurements between rotations to decide which way to turn
3. Does the code use ratios or normalization to make the discrimination intensity-invariant
4. Is there a mechanism for noise handling (averaging, thresholding)
5. Can the robot handle multiple different distractor colors, not just one specific one (requires identifying the target by template matching, not by single-channel comparison)

### Learning rubric: Mimic and Approach Color

*Single shared rubric covering concepts from both color tasks. Delivered as an online survey at the end of Day 1; no chatbot access during the survey.*

1. Why can't the robot distinguish colors without the color filters on the sensors?
2. What would happen if one filter were removed (that sensor exposed to all wavelengths)?
3. Animal eyes differ in the number of color channels (cones), the wavelengths they respond to, and the shape of the eye. Pick one of these differences and design a robot experiment that would test why it matters.
4. Animals exhibit many color-vision behaviors that aren't yet present in your robot. Pick one such behavior and explain how you would add it to the robot, and what advantage it would give.

## Sound localization assessment tools

### Production rubric: Taxis

*Scored from each student's robot program plus a photo of their robot, collected at the end of the slot in which they performed Taxis. Items rated 0–3; maximum 15.*

1. Does the robot have two ears with clearly different acoustic axes
2. Does the code compare the loudness at the left and right ears
3. Does the rotation sign match the sign of the IID
4. Is there a mechanism for noise handling
5. Is there a mechanism for stopping at the goal

### Production rubric: Kinesis

*Scored from each student's robot program plus a photo of their robot, collected at the end of the slot in which they performed Kinesis. Items rated 0–3; maximum 15.*

1. Does the robot have a single directional ear
2. Does the robot compare the measurements between rotations
3. Does the rotation sign match the loudness difference sign
4. Is there a mechanism for noise handling
5. Is there a mechanism for stopping at the goal

### Learning rubric: Kinesis

*Delivered as an online survey at the end of the slot in which the student performed Kinesis. No chatbot access during the survey. The four questions form a scaffold: each builds on what the previous one established, with the student reconstructing the kinesis algorithm by Q4. To measure whether each step is reached on its own, every question appears on a separate page and students cannot revisit earlier ones — otherwise later questions, which reveal setup information, would let them backfill earlier answers in hindsight.*

**Q1**

<u>Image:</u> Robot with one bare sound sensor. Two speakers at equal distance: speaker 1 at 0°, speaker 2 at 45°.

![Robot with one bare sound sensor. Two speakers at equal distance: speaker 1 at 0°, speaker 2 at 45°.](images/q1_kinesis.png)

<u>Question text:</u> The robot is equipped with one sound sensor. We play sound from speakers 1 and 2 in succession. What do you predict the sensor readings will be when we play the different speakers? Explain.

**Q2**

<u>Image:</u> Single speaker fixed at 45°. Three panels showing the robot at different body orientations — panel 1: robot faces 0°; panel 2: robot faces 45°; panel 3: robot faces 90°. The robot has one external ear, mounted at the center of the body and left/right symmetric. The ear points along the robot's forward axis and rotates with the body.

![Three panels showing the robot at body orientations 0°, 45°, and 90°, with a single speaker fixed at compass 45° in all three. The ear is mounted at the front of the robot and rotates with the body.](images/q2_kinesis.png)

<u>Question text:</u> The robot is equipped with one sound sensor in an external ear. What do you predict the sensor readings will be at each of the three orientations? Explain.

**Q3**

<u>Image:</u> Robot with one external ear mounted at the front-center but tilted 45° from the body's forward axis (not pointing forward). The robot's body faces 0°, so the ear points at 45° absolute. Two speakers: speaker 1 at 0° (in front of the body), speaker 2 at 45° (in front of the ear).

![Robot facing east with an external ear mounted at the front-center but tilted 45° from the body's forward axis. Speaker 1 lies in the body's forward direction (east); speaker 2 lies in the ear's pointing direction (SE), at the same distance.](images/q3_kinesis.png)

<u>Question text:</u> The robot is equipped with one sound sensor in an external ear. We play sound from speakers 1 and 2 in succession. Which speaker gives the louder reading? Explain — does the answer depend on where the body is facing, or where the ear is pointing?

**Q4**

<u>Image:</u> Two consecutive panels of the robot with a single directional ear. Panel 1: ear pointing at 0°, reading = 126. The robot rotates clockwise. Panel 2: ear pointing at 45°, reading = 233. The speaker's position is not shown.

![Two panels showing the robot with a forward-mounted directional ear. Situation 1: ear at 0° (north), reading = 126. Situation 2: robot rotated 45° clockwise, ear at 45°, reading = 233. The speaker is not shown.](images/q4_kinesis.png)

<u>Question text:</u> The robot is equipped with one sound sensor in an external ear. Based on these two readings, where do you think the speaker is? Explain.

### Learning rubric: Taxis

*To be designed — parallel scaffold to kinesis but built on simultaneous (two-eared) rather than sequential comparison.*