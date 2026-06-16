# Final Project

This document covers the **final project**, the capstone activity that comes after the sense modules. Unlike the other activity documents it does **not** introduce a new sense or a new biology topic. Instead, students design and build their **own** robot challenge using the senses they have already covered: color vision, touch/whiskers, sonar, olfaction (line following), and sound localization. Students are encouraged to **combine at least two senses** — integrating them is the point of the capstone — though a single sense done really well is still acceptable. The goal is for students to put the whole course together: pick a problem, decide which senses the robot needs, and build the sense → process → decide → act loop themselves.

Because the project is self-selected, there is no single "correct" build and no fixed troubleshooting path. The agent's job here is less about one activity's details and more about **helping students scope a realistic project, choose appropriate senses, and reuse what they already learned**. The companion document **`sensor_toolkit.md`** is the place to look for each sense's reusable parts: what students already built with it, its sensor and mBlock block, calibration, and troubleshooting. Lead with what a student already built — "remember you did obstacle avoidance with sonar? reuse that pattern."

## Core Concepts

### What the Final Project Is
Students invent their own challenge and solve it with the robot. They are encouraged to combine **at least two** senses; a single sense done really well is still acceptable. Examples of the *kind* of thing they might choose (not a required list):

- A robot that **follows a line** (olfaction/line following) but **stops when something is in the way** (sonar) — a delivery robot.
- A robot that **drives toward a color** (color vision) and **announces arrival** by reacting when it is close (sonar).
- A robot that **approaches a sound** (sound localization) and **avoids obstacles** on the way (sonar or whiskers).
- A robot that uses **whiskers** to feel its way along a wall (touch) and **turns at corners**.

**Agent Notes:**
- **There is no single right answer.** The project is open-ended by design — help the student build *their* idea rather than steering them to a "standard" project.
- **Push for at least two senses.** Integrating senses is the point of the capstone, so nudge students toward combining two before they settle on one. A well-executed single-sense project is still acceptable if that's where a student lands — but the default encouragement is "what second sense would make this better?" At the same time, don't push *past* two into piling on sensors the scope can't support (see the five-port limit below) — two senses, well integrated, is the sweet spot.
- **The reusable parts of every sense live in `sensor_toolkit.md`** — for each sense: what students already built, the sensor and its block, calibration, and troubleshooting. For anything sense-specific (which block, how to calibrate, why a reading is noisy), retrieve from there rather than re-deriving it here.
- **The robot may not work perfectly, and that's expected.** As in every module, failure cases are part of the learning experience — don't promise a student's project will work flawlessly.

### The Skills This Project Reuses
The final project rests on everything from earlier modules — there is nothing new to learn first:

- **The basic program structure** (from getting started): initialize, then loop — get sensor data → process → decide → act → repeat.
- **Reading sensors into variables** and **comparing** them to make decisions.
- **Per-sense techniques**: calibrating a sensor, averaging noisy readings, comparing two channels (two color sensors, two ears), thresholds and dead bands.

**Agent Notes:**
- **Start from the program structure.** When a student doesn't know where to begin, walk them through sense → process → decide → act for *their* chosen challenge. It organizes any project, no matter which senses it uses.
- **Point back, don't re-teach.** If a student picks color vision, the calibration and two-sensor comparison they need are in the color-vision section of `sensor_toolkit.md` — send them there, and remind them they already built it.

---

## Designing a Project

A good way to help a student plan, in order:

1. **What should the robot do?** Get a one-sentence goal ("drive toward the green card and stop before it hits the wall").
2. **Which sense(s) does that need?** Map each part of the goal to a sense the student has covered. "Drive toward green" → color vision. "Stop before the wall" → sonar.
3. **What does each sensor tell the robot, and what decision follows?** For each sense: what is read, what it is compared to, and what the robot does as a result.
4. **How do the parts combine?** Decide what takes priority when more than one sense is involved (see *Combining Senses* below).
5. **Build the simplest version first**, then add to it.

**Agent Notes:**
- **Push for a small first version.** The single most common problem with self-selected projects is over-scoping. Get *one* behavior working end-to-end before adding a second sense or a refinement. "What's the smallest version of this that would still be cool?" is a good question.
- **Use the biology bridge.** The course taught biology first for every sense; that scaffolding still applies. "You learned how two ears compare loudness — how will your robot decide which way to turn?"
- **Keep it to senses they've done.** The project draws on the five covered senses. If a student wants a sense or sensor the course didn't cover, gently steer them back to what they have — or suggest they ask their teacher whether it's feasible.

---

## Combining Senses

Combining senses is the main *new* engineering wrinkle in the final project — not a new biology concept, but a build-and-program challenge. Two things to keep in mind:

### Ports and Sensors
The mBot Ranger has **five ports (6–10)**, and any sensor can go in any port (see `robot_details.md`). A project that combines senses needs **one port per external sensor**, so students must plan their wiring:

- A line-follow-and-avoid robot needs a **line-follower sensor** *and* an **ultrasonic (sonar) sensor** — two ports.
- A two-eared sound robot already uses **two** sound sensors; adding another sense uses more ports.
- The **onboard** light, sound, and inertial sensors do **not** use ports 6–10 — but remember the sound-localization activity deliberately uses *external* sound sensors, not the onboard mic.

**Agent Notes:**
- **Five ports is the hard limit.** If a student's plan needs more external sensors than that, help them simplify — drop a sense, or use the onboard sensors where they fit.
- **Each block's port must match the physical port** the sensor is plugged into — the single most common "the sensor does nothing" bug, and it gets more likely with several sensors wired at once. When a combined project misbehaves, check each sensor's port assignment first.
- **Label which sensor is in which port.** With multiple sensors it is easy to lose track; suggest the student write it down before programming.

### Deciding What the Robot Does When Senses Disagree
When a robot uses more than one sense, its program has to decide **which sense wins** at any moment. This is a *decision-logic* problem, not a sensor problem:

- **Priority / override**: one sense interrupts the others. *Follow the line, but if the sonar sees an obstacle closer than 15 cm, stop — the obstacle overrides the line.*
- **Sequence / states**: the robot does one thing, then switches to another. *First approach the sound; once close, switch to avoiding obstacles.*
- **Combine into one decision**: both readings feed a single choice. *Steer by the brighter color sensor unless a whisker is pressed.*

**Agent Notes:**
- **Make the "who wins" rule explicit.** Most combined-sense bugs are really an unclear or missing priority rule — the robot is reading both sensors fine but the program doesn't say which one to act on. Ask: "When the line sensor says go and the sonar says stop, what should the robot do?"
- **Build one sense at a time, then join them.** Get the line-follow working alone, get the obstacle-stop working alone, *then* combine. Debugging two senses at once is much harder.
- **An if-decision usually expresses the priority**: check the high-priority sensor first (the obstacle), and only fall through to the normal behavior (following the line) when it's clear.

---

## Troubleshooting a Self-Selected Project

Because every project is different, troubleshoot by **layer**, the same separation used in every module:

| Layer | Question to ask | Where to look |
| ----- | --------------- | ------------- |
| **Sensing** | Is each sensor reading sensible values that change when expected? | The relevant sense doc + check the **port** matches the block |
| **Decision** | Is the comparison/threshold right? When senses are combined, is the priority rule right? | The student's if-decisions and thresholds |
| **Action** | Are the motors/LEDs doing what the decision asked (right direction, right speed)? | The action blocks; check motor wiring (M1 left, M2 right) |

**Agent Notes:**
- **Isolate before combining.** If a multi-sense robot misbehaves, test each sense on its own — it quickly shows which layer and which sense is the problem.
- **Reuse per-sense troubleshooting.** Noisy sound readings? Average them. Color sensor needs calibrating? Each sense's "Watch for" items are in `sensor_toolkit.md` — the capstone doesn't replace that guidance, it points to it.
- **Over-scope is a "project" problem, not a code problem.** If a student is stuck because the whole thing is too ambitious, the fix is to cut it down to a working core, not to keep debugging the full version.

---

## Common Student Misconceptions

**"A project has to combine lots of senses to be good."**
- **Reality**: aim for **two** well-integrated senses — that's the sweet spot. More senses mostly add wiring and decision-logic difficulty without making the project better, and a single sense done really well is still acceptable.
- **Response**: "Two senses working together is the goal — not as many as possible. What's the one second sense that would make your robot more interesting?"

**"I can just plug in all the sensors I want."**
- **Reality**: there are only five ports (6–10), one per external sensor, and each block's port must match the wiring.
- **Response**: "Let's count the sensors your idea needs — there are five ports. And double-check each block's port matches where it's plugged in."

**"If I add two senses, the robot will just do both at once."**
- **Reality**: the program must decide which sense the robot acts on at any moment — a priority or sequence rule.
- **Response**: "When your two sensors disagree, what should the robot do? Writing that rule down is usually the missing piece."

**"My combined robot is broken."**
- **Reality**: it's almost always one layer — a wrong port, an unclear priority rule, or a flipped motor — not the whole robot.
- **Response**: "Let's test one sense at a time. Which sensor reads correctly on its own, and where does it break when you combine them?"

---

## Senses Available for the Final Project

This recap maps each covered sense to what its robot build does. It replaces the single-sense Biology-Robot Connections table used in the other documents, because the final project can draw on any of these. The reusable detail for every sense — what students already built, the sensor and its block, calibration, and troubleshooting — is in the companion document **`sensor_toolkit.md`**.

| Sense | Biological idea | Robot build (already done) |
| ----- | --------------- | -------------------------- |
| **Color vision** | Comparing color channels (trichromacy) | Filtered light sensors as a 1-pixel color camera; color mimicking / approach-avoid |
| **Touch / whiskers** | Mechanical touch and active whisker sensing | Flex-sensor whisker that detects contact; obstacle avoidance / wall following |
| **Sonar / echolocation** | Pulse-and-echo ranging | Ultrasonic sensor for obstacle avoidance / distance; sonar cane |
| **Olfaction (line following)** | Following a chemical trail | Line-follower sensor tracking a line as an odor-trail analog |
| **Sound localization** | Comparing two ears / turning to scan | External sound sensor(s) in handmade ears; approach a sound source |

**Agent Notes:**
- **Use this table to help a student choose.** If they have a goal but don't know which sense fits, map the goal onto this table.
- **For the details of any sense, go to `sensor_toolkit.md`** — it has the per-sense section with the sensor block, calibration steps, and troubleshooting, framed around the challenge the student already completed.
- **Don't overclaim any of these** — as in the individual modules, each robot build is a simplified *model* of the animal sense, not a replica.
