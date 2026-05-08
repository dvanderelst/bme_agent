# ChatBot Educational Research

# Outstanding tasks

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

# Design overview

## The ideal design

With two factors — chatbot order (on→off vs. off→on) and task order (T1→T2 vs. T2→T1) — there are four combinations, and students would ideally be split into four independent groups:

| Group 1        | Group 2        | Group 3        | Group 4        |
| -------------- | -------------- | -------------- | -------------- |
| T1/ChatBot on  | T2/ChatBot on  | T1/ChatBot off | T2/ChatBot off |
| T2/ChatBot off | T1/ChatBot off | T2/ChatBot on  | T1/ChatBot on  |

This is impractical because the chatbot toggle and task assignment occur at the class level: 24 students in one room cannot run different conditions simultaneously.

## Latin-square reversal across two days

> 💡 Students will have had experience with the chatbot before we roll out the design below. This gives them some time to get used to using it. We will also have data on their chatbot usage prior to the start of our experimental protocol.

We split the class in half and run two modules on two days, flipping which chatbot state comes first across days. Within each day, the two halves of the class complete the tasks in opposite order, so the task order is counterbalanced with respect to chatbot state.

| Slot | Day                        | Chatbot | Half A task    | Half B task    |
| ---- | -------------------------- | ------- | -------------- | -------------- |
| 1    | Day 1 (Color vision)       | on      | Mimic Color    | Approach Color |
| 2    | Day 1 (Color vision)       | off     | Approach Color | Mimic Color    |
| 3    | Day 2 (Sound localization) | off     | Kinesis        | Taxis          |
| 4    | Day 2 (Sound localization) | on      | Taxis          | Kinesis        |

Reading the chatbot column top to bottom gives the manipulation vector [1, 0, 0, 1]. Each task slot ends with an assessment.

## Identification argument

Across the two days, the chatbot manipulation, read in temporal order of slots, is the vector **[1, 0, 0, 1]**. The design above controls for confounds orthogonal to this (e.g., overall experience, which rises monotonically). However, interactions between day and slot are not controlled for. In general, any effect that follows a pattern across the 4 slots that is correlated with the chatbot manipulation vector can be a confound.  

# Assessment

We will assess whether the chatbot improves (1) production and (2) learning and understanding.  

| Construct  | Scored by                 | Scored from               |
| ---------- | ------------------------- | ------------------------- |
| Production | Instructor / AI           | Code + robot photo        |
| Learning   | AI (pairwise comparisons) | Student's written answers |

### Methodological safeguards

- Students answer probes without chatbot access.
- Scoring of production rubrics should be blinded to condition and day.

### Scoring plan

- **Production rubrics.** Each item 0–3: absent/rudimentary/partial/clearly present.
- **Learning rubrics.** Pairwise comparison of anonymized answers. Adaptive Comparative Judgment (ACJ) to pick informative pairs — stable ranking in ~10–15×N comparisons rather than full pairwise. Multiple rounds / multiple AI models as judges; aggregate via Bradley-Terry to get interval scores.

### Analysis plan

Two Bayesian mixed models, same predictors, different outcomes:

- **Production:** `sum score (0–15) ~ chatbot + day + position + task + (1|student)`
- **Learning:** `z-scored BT score ~ chatbot + day + position + task + (1|student) + (1|question)`

## Sound localization

### Production rubric: Taxis

1. Does the robot have two ears with clearly different acoustic axes
2. Does the code compare the loudness at the left and right ears
3. Does the rotation sign match the sign of the IID
4. Is there a mechanism for noise handling
5. Is there a mechanism for stopping at the goal

### Production rubric: Kinesis

1. Does the robot have a single directional ear
2. Does the robot compare the measurements between rotations
3. Does the rotation sign match the loudness difference sign
4. Is there a mechanism for noise handling
5. Is there a mechanism for stopping at the goal

### Learning rubric: Kinesis

**Q1**

[Image: Robot with one bare microphone (no external ear). Two speakers: speaker 1 at 0° (straight ahead), speaker 2 at 45°.]

We play sound from speakers 1 and 2 in succession. What do you predict the sensor readings will be when we play the different speakers? Explain.

**Q2**

[Image: Single speaker fixed at 45°. Three panels showing the robot at different body orientations — panel 1: robot faces 0°; panel 2: robot faces 45°; panel 3: robot faces 90°. The external ear is mounted along the robot's forward axis in all panels, so it rotates with the body.]

What do you predict the sensor readings will be at each of the three orientations? Explain.

**Q3**

[Image: Robot with one microphone with an external ear, fixed at 45° relative to the body. Two speakers: speaker 1 at 0°, speaker 2 at 45°.]

We play sound from speakers 1 and 2 in succession. What do you predict the sensor readings will be when we play the different speakers? Explain.

**Q4**

[Image: Two consecutive panels of the robot with a single directional ear. Panel 1: ear pointing at 0°, reading = 3. The robot rotates clockwise. Panel 2: ear pointing at 45°, reading = 7. The speaker's position is not shown.]

Based on these two readings, where do you think the speaker is, and which way should the robot rotate next? Explain.

### Learning rubric: Taxis

*To be designed — parallel scaffold to kinesis but built on simultaneous (two-eared) rather than sequential comparison.*

## Color vision

### Production rubric: Mimic Color

1. Are at least two sensors with different color filters used
2. Does the robot produce the correct output color for a given input color
3. Does the code use ratios or normalization to make the response intensity-invariant
4. Is there a mechanism for noise handling (averaging, thresholding)
5. Can the robot mimic more than two distinct colors (requires combining channels, not just thresholding each independently)

### Production rubric: Approach Color

1. Are at least two sensors with different color filters used
2. Does the robot compare measurements between rotations to decide which way to turn
3. Does the code use ratios or normalization to make the discrimination intensity-invariant
4. Is there a mechanism for noise handling (averaging, thresholding)
5. Can the robot handle multiple different distractor colors, not just one specific one (requires identifying the target by template matching, not by single-channel comparison)

### Learning rubric: Mimic and Approach Color

1. Why can't the robot distinguish colors without the color filters on the sensors?
2. What would happen if one filter were removed (that sensor exposed to all wavelengths)?
3. Animal eyes differ in the number of color channels (cones), the wavelengths they respond to, and the shape of the eye. Pick one of these differences and design a robot experiment that would test why it matters.
4. Animals exhibit many color-vision behaviors that aren't yet present in your robot. Pick one such behavior and explain how you would add it to the robot, and what advantage it would give.