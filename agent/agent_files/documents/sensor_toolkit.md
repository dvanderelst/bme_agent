# Sensor Toolkit & Prior Activities — Final Project Reference

This document is a **quick reference for the final project**, the self-selected capstone. It is not a new sense — it gathers, for each sense students have already covered, the parts that are reusable when they build their own robot challenge: a one-line biology reminder, **what they already built** with that sense, the sensor and its mBlock block, how to reuse it, and what to watch for.

Use it two ways:
1. **As a "you've done this before" scaffold.** When a student picks a sense for their project, connect it to the challenge they already completed: *"You built obstacle avoidance with sonar already — remember reading the distance and turning away when it dropped below ~30 cm? Your project can reuse that same pattern."* Pointing students back to working code and ideas they own is the fastest way to get them started.
2. **As a compact sensor reference.** Each section has the exact block, value meanings, calibration steps, and the top troubleshooting items — enough to help with a project without re-loading every full sense document.

This is paired with `final_project.md`, which covers scoping a project, the design process, and combining several senses (the five-port limit and the "which sense wins" priority rule). The hands-on **biology** activities from the original modules (the goggle game, termite observation, two-point discrimination test, etc.) are intentionally left out — they don't transfer to a robot build. For the deepest per-sense detail, the full module documents still exist.

**Agent Notes:**
- **Lead with what they already built.** The single most useful move on capstone day is reminding a student of the working pattern they produced in the relevant module, then helping them adapt it — not teaching the sense from scratch.
- **Don't overclaim any robot build** — each is a simplified *model* of the animal sense (the line sensor isn't really smelling; the mBot sonar isn't a bat). Keep that honesty.
- **Separate the layers when debugging** any project: is the **sensor** reading sensibly? is the **decision** (comparison/threshold) right? is the **motor action** right? Most "it's broken" reports are one layer, not the whole robot.

---

### Color Vision
**Biology in one line:** Color comes from comparing signals across multiple light-sensitive channels — just as the brain compares cone classes, the robot compares readings across filtered sensors to identify a color.

**What you already built:** A **dichromatic robot** (two filtered light sensors, like a dog's two-cone vision) for two challenges — **Color Mimicking** (read the color of an LED bar held in front and switch the onboard LEDs to match) and **Approach / Avoid** (turn left and sample, turn right and sample, then steer toward one color and away from another). Core pattern in both: **sense → compare sensor readings against calibration thresholds → decide which color → act** (set LEDs or steer). Key insight: no single filtered sensor can identify a color alone — you must read multiple channels and compare.

**Sensor & blocks:** External mBot Ranger light sensors fitted with 3D-printed covers and color-filter slides, read with the mBlock light-sensor block (returns a numeric value). There are no universal values — range depends on lighting and filter color, so calibration sets each build's thresholds. Default wiring: two sensors on external ports (e.g. green + blue filters); optional third sensor with a red filter for trichromatic (RGB). The sensor responds to roughly **480–1000 nm**, so deep blue/violet sits near the edge of sensitivity.

**Reusing it:** Calibrate before programming, every time: (1) attach the filtered sensors, (2) place the robot in the real operating conditions (same lighting and distance), (3) present each color one at a time and record each sensor's value, (4) use those recorded values as thresholds. For the Approach/Avoid pattern, store the first sample in a variable before taking the second.

**Watch for:**
- Misidentified colors → usually missing/wrong calibration. "What values did your sensors give during calibration, and are your thresholds based on those?"
- Trying to identify a color from one channel — it's ambiguous (red and yellow both read high through a red filter); read all sensors together.
- Dichromatic limits: some color pairs are genuinely indistinguishable with two sensors (e.g. red vs. no light both read low-low). Not a bug — pick more-distinguishable colors or add a third filter.

**Agent Notes:**
- The standard build is **two** sensors. Ask how many filters the student is actually using before helping with thresholds or logic.
- The two-channel pattern table (green+blue: Green = High/Low, Blue = Low/High, Cyan = High/High, Red = Low/Low) and the three-channel RGB table are in `color_vision.md` and can be shared with students reasoning about which colors their setup can distinguish.

---

### Touch & Whiskers
**Biology in one line:** Animals like rats actively sweep whiskers (vibrissae) through space — the shaft bends on contact and the deformation is sensed at the follicle base, not the tip.

**What you already built:** A **whisker robot using flex sensors** for one of two challenges — obstacle avoidance (drive around without bumping, using left and right whiskers) or wall following (keep one whisker lightly touching a wall with a continuous feedback loop). Both use the same pattern: read the whisker value → compare to a threshold → decide contact state (bent / not bent) → steer the motors. The robot gathers information by moving and triggering contact — **active sensing**, the same strategy animals use.

**Sensor & blocks:** Use the **`light sensor [dropdown] light intensity`** block, selecting the whisker's port (any of **ports 6–10**) in the dropdown. The flex sensor has a nominal flat resistance of ~10 kΩ. Values **decrease** when the whisker bends (bending does not raise the number). Left and right whiskers are read separately, each with its own threshold.

**Reusing it:**
1. Read resting values with no contact (left and right separately).
2. Gently bend each whisker as during contact; note the lower values.
3. Pick a threshold between resting and bent for each whisker — left and right need not match.
4. Run slowly first — easier to debug, less likely to damage sensors.
5. Tune: reacts too late → raise sensitivity (threshold closer to resting); reacts constantly → lower it, or check the whisker sits neutral at rest.
6. Condition: `< threshold` means "bent/contact", `> threshold` means "not bent" (because bending lowers the value).

**Watch for:**
- Value doesn't change at all → wrong port in the block, loose cable, or damaged sensor. Match the dropdown to the physical port; reseat; bend by hand to confirm.
- Value changes but robot does nothing → threshold not crossed, or the if-check sits outside the loop. Read live values vs. threshold; confirm the check is inside the loop.
- Reacts constantly without contact → threshold too close to resting, whisker pre-bent at mount, or cable noise. Recalibrate and remount neutral.
- Stops working after handling → flex sensors bend one way only; inspect for a crease and replace if damaged.

**Agent Notes:**
- Ask which challenge the student did (obstacle avoidance vs. wall following) before giving logic or calibration advice — whisker count and threshold logic differ.
- Reusable core: measure resting, measure bent, pick a number between, use `< threshold` as the contact condition.
- Wall following adds a feedback loop; if it oscillates, reduce speed or soften the turn response rather than re-calibrating the sensor.

---

### Sonar (Ultrasonic)
**Biology in one line:** Animals like bats emit sound pulses and read the returning echoes to judge distance — the ultrasonic sensor does the same.

**What you already built:** Three things — measuring the sensor's **directionality** (mapping its cone of detection), observing the **sound-mirror problem** on smooth angled surfaces, and an **obstacle-avoidance robot** using two ultrasonic sensors to compare left/right distance and decide which way to turn. Also a **sonar cane** (robot on a PVC pipe) that signals distance by beep duration. Core pattern: **sense** (read distance) → **process** (apply the 1.25 correction, compare to threshold) → **decide** (which side is constrained / is something too close?) → **act** (turn, beep, drive). Obstacle avoidance used a ~30 cm safe-distance threshold.

**Sensor & blocks:** The ultrasonic sensor has two cylinders — emitter (**T**) and receiver (**R**). Plug into any of **ports 6–10** and select the matching port in the block. Returns distance in **centimeters**. When it detects nothing it returns exactly **400 cm** (not a real reading). Apply a **1.25 correction factor** (multiply readings by 1.25) for the sensor's systematic underestimation. The sonar cane converted distance to meters and set beep duration as `b = 0.49 - 0.4 × distance`, clipped to 0–0.25 s.

**Reusing it:** The sensor is directional — most sensitive straight ahead, range drops off-axis (~240 cm at 0°, ~190 cm at 20°, ~120 cm at 30° for a ~10 cm object). Always apply the 1.25 correction. Use a distance threshold and act when a reading crosses it (~30 cm worked at normal speed). Two sensors give left/right comparison for choosing a turn direction — the same principle as two ears. For continuous proximity feedback, the beep-duration encoding from the cane transfers.

**Watch for:**
- Smooth angled surfaces reflect sound away ("sound-mirror") → sensor reports 400 cm though a wall is there; use rougher surfaces or face it straight on.
- A constant 400 cm means *no echo received*, not "object is 4 m away."
- Smaller/softer targets return weaker echoes and shorter detection range than large hard surfaces.
- Several robots running at once can interfere — test one at a time.

**Agent Notes:**
- "It's not working" → ask "what value does the sensor show now?" and "what happens with your hand in front of it?" — separates sensing from logic/motor.
- The 1.25 correction and the ~30 cm threshold from the obstacle-avoidance build are directly reusable; remind students they already have working code for this pattern.

---

### Olfaction (Line Following)
**Biology in one line:** Animals like termites follow chemical trails by comparing the odor on their left vs. right and steering toward the stronger side — the robot copies that logic, but its line-follower sensor reads reflected light from a dark line, **not** actual chemicals.

**What you already built:** A **line-following robot** as an odor-trail analog, using the same sense→process→decide→act loop: read line position (sense) → compare left/right detectors (process) → choose a steering direction (decide) → drive motors (act). The hard part was corners, gaps, and intersections. Key hints from that build: tune speed first when behavior is wrong (too fast → overshoots corners/gaps); add an explicit rule for value 3 (line lost), simplest being brief forward continuation; add an explicit rule for intersections since value 0 is ambiguous at a crossing.

**Sensor & blocks:** The **line follower sensor** plugs into any of **ports 6–10** (match the port in the block). Useful blocks: `line follower sensor [port] value`, `move forward at power [slot]%`, `turn left/right at power [slot]%`, `left wheel at [slot]%, right wheel at [slot]%`, `if/else`, variables and comparisons. Value meanings:

| Value | Interpretation | Typical action |
|-------|----------------|----------------|
| 0 | Centered on the line (both detectors on line) | Drive forward |
| 1 | Veering right (left detector on line) | Turn left to correct |
| 2 | Veering left (right detector on line) | Turn right to correct |
| 3 | Line lost (neither detector on line) | Search, slow, or briefly continue forward |

**Reusing it:** Ensure good contrast (dark line on a light surface). The transferable technique is the compare-and-correct loop: continuously read the sensor, steer toward the side detecting the line, and have an explicit strategy for value 3. Brief forward continuation is the simplest gap strategy. For any new challenge, map the required behavior onto these four values.

**Watch for:**
- Value 3 (line lost) with no handling → robot freezes or behaves unpredictably; always add an explicit rule.
- Speed too high → overshoots corners/gaps before it can correct; reduce motor power first.
- Value 0 at intersections is ambiguous (reads "centered" the same on a crossing) → add a branch (e.g. always go straight) if the challenge has crossings.
- Wrong port in the block → garbage readings; confirm the block's port matches the physical port.

**Agent Notes:**
- The robot is not literally smelling — frame it as "a line-follower sensor standing in for an olfactory sensor; the line is a proxy for a chemical trail."
- The loop structure transfers directly: a new challenge just needs new rules wired into the same four-value loop.

---

### Sound Localization
**Biology in one line:** Animals locate sound by comparing loudness between two ears and by rotating the head/ears to scan — the external ear (pinna) shapes incoming sound so each ear is more sensitive in some directions.

**What you already built:** A robot that **approaches a speaker playing a pulsed noise**, in one of two builds. The **one-eared** robot rotates to sample directions — measure, turn a little, measure again, reverse whenever the sound gets quieter — homing on the loudest heading before creeping forward. The **two-eared** robot mounts two directional ears angled outward and steers by comparing left vs. right at the same instant, turning toward the louder ear. Both needed a **handmade external ear** (paper cone, clay, cardboard) to make the sensor directional, and the two-eared build matched its sensors with a correction factor. Reusable: the stop-measure-move rhythm, the comparison logic, and the ear design.

**Sensor & blocks:** Use the `sound sensor [port] loudness` block — available out of the box, no extension; higher number = louder. It measures **total loudness only** — no frequency, no timing — and is **omnidirectional** on its own. Always use an **external** sound sensor plugged into a port (**6–10**), embedded in a handmade ear; **never** the onboard mic (it can't be placed inside an ear). One external sensor for a one-eared build, two for a two-eared build.

**Reusing it:**
1. **Make the ear directional first** — build a physical ear (cone/clay/cardboard; bigger is better, ~10–20 cm) and run a calibration test: place the speaker at several positions around the robot at a fixed distance and record the averaged reading at each. It should peak when the ear faces the source and fall off to the sides/behind; if not, rebuild before writing approach code.
2. **Average** noisy/pulsed measurements — a single read can fall in a silent gap; take several per position and average before deciding.
3. **Compare, don't threshold** — absolute loudness drifts; use "louder than last time" (one-eared, across turns) or "louder left vs. right" (two-eared, same instant).
4. **Match two sensors** (two-eared only): with the speaker straight ahead, take averaged `L_avg` and `R_avg`, then multiply one sensor's reading by `L_avg / R_avg` so equal sound gives equal corrected readings.
5. Use a **stop-measure-move** rhythm — measuring while moving smears the readings.

**Watch for:**
- Reading barely changes as the robot rotates → the ear isn't directional enough; make it bigger, deeper, or denser.
- Absolute loudness drifts with distance, room, and battery → always compare readings, never test against a fixed number.
- Two same-model sensors differ in sensitivity → unequal left/right readings with a centered speaker are expected; equalize with the correction factor (two-eared only).

**Agent Notes:**
- Ask how many ears the student's project robot uses before giving build-specific advice — the core comparison step differs (across turns vs. left-vs-right).
- The one-eared pattern (compare across successive turns, reverse when quieter) and the two-eared pattern (compare left vs. right at the same instant) are the reusable skeletons — help the student pick which fits their new challenge.
- Calibration (the directionality test) is not optional; most "won't approach" problems trace to a non-directional ear. Ask for the table of readings at different angles to diagnose.
- Cross-module callback: "compare, don't threshold" is the same lesson as color vision — worth naming if the student did that module.
