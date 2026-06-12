# Sound Localization

This document covers the biology of sound localization and the robot activity in which students get an mBot to **approach a sound source** (a speaker playing a pulsed noise). The core engineering problem is that the robot's sound sensor measures only *loudness* and is *omnidirectional* — on its own it cannot tell where a sound comes from. Students solve this the way animals do: by giving the sensor a directional **external ear**, then steering by comparing loudness. Two builds run in parallel — a **one-eared** robot and a **two-eared** robot — and students swap builds on the second day.

**Internal note for the agent (do NOT use these words with students):** the one-eared task is *kinesis* and the two-eared task is *taxis*. These terms are intentionally hidden from students. Use plain language — "one-eared robot", "two-eared robot". Because the agent is not told which build a given student has, **ask how many ears they are building** before giving build-specific advice.

## Core Concepts

### How Animals Localize Sound
Animals find the direction of a sound mainly by comparing the two ears: a sound off to one side is a little louder at the nearer ear (and arrives slightly sooner). The external ear (pinna) shapes incoming sound so the ear is more sensitive in some directions than others, and many animals turn the head or ears to scan. Owls, cats, and many mammals are good examples.

**Agent Notes:**
- **Two cues in biology**: interaural *level* (loudness) differences and *timing* differences. Our robot can use **only loudness** — the sensor gives no precise timing.
- **Pinna = directionality**: the external ear is what makes a single ear directional; without it, an ear is roughly equally sensitive in all directions.
- **Scanning**: animals relying on one ear (or wanting a better fix) move the head/ears — the one-eared robot does the same by rotating.
- **Don't overclaim**: the mBot's single loudness sensor is far cruder than an animal's ear — this is a model, not a replica.

### The Makeblock Sound Sensor
The sound sensor measures the **total amount of sound** (loudness) reaching it. It does **not** separate frequencies and gives **no precise timing** — just "how loud, right now," as a number where higher = louder.

**Agent Notes:**
- **Block**: `sound sensor [port] loudness` — available **out of the box, no extension needed**. Higher number = louder. See programming_blocks.md.
- **External sensor only**: the activity always uses an **external** sound sensor plugged into a port (6–10) and embedded in a handmade ear. Students must **not** use the board's onboard mic — it can't be put inside an ear. One external sensor for the one-eared build, two for the two-eared build.
- **No frequency, no timing**: students cannot use pitch or arrival-time differences — only loudness.

### Problem 1: The Sensor Is Phasic
For a *constant* sound the sensor stops responding — it reacts to the onset, then settles back toward baseline within about a second. A steady tone is therefore useless; the source must **change in loudness over time**.

**Agent Notes:**
- **Use the pulsed clip**: students play a repeating **noise-burst** sound (bursts separated by silence). Class clip: https://tinyurl.com/3ahsnr6n. Music can also work because its level varies.
- **Consequence for code**: because the sound pulses on and off, a single instantaneous read can land in a silent gap and look quiet even when the ear points right at the speaker. This is why averaging matters (below).

### Problem 2: The Sensor Is Omnidirectional
On its own the sensor responds the **same regardless of direction**. It can tell you a sound is loud, but not where it is. Making the reading depend on direction is the whole point of the activity.

**Agent Notes:**
- A bare sensor cannot steer the robot — point it any way and the reading barely changes.
- If a student's robot can't find the source, first check whether the sensor's reading actually changes with direction at all.

### The Solution: Build a Directional External Ear
Putting the sensor inside an **external ear** — a rolled paper cone, a clay "ear," cardboard, any material — makes its response **depend on direction**: loudest when the ear points at the source, weaker off to the side, weakest behind. This directional shaping is what makes localization possible.

It's hard to predict from an ear's shape exactly how directional it will be — which is why students have to **test** it rather than assume. But one rule of thumb holds: **all else equal, a bigger ear is more directional.**

**Agent Notes:**
- **Materials**: modeling clay, a paper/cardboard cone — anything that funnels or blocks sound asymmetrically. The sensor should sit **inside** the ear, not poke out of it.
- **Go big**: students often build tiny ears just a few cm across — these are usually too small to be directional. Encourage **much larger** ears — 10, 15, even 20 cm in diameter is completely reasonable. When a student's test shows weak directionality, "make the ear bigger" is the first thing to try.
- **Shape is hard to predict**: don't promise a given shape will work — the directionality test is what settles it. This is exactly why calibration matters.
- **Imperative**: if the ear isn't actually directional, the robot cannot work. Calibration (below) is **not optional**.
- **One ear vs. two**: one directional ear localizes by **rotating and comparing across turns**; two directional ears (angled outward, each "listening" to its own side) localize by **comparing left vs. right** at the same instant.

### Intensity Is the Only Cue — So Compare, Don't Threshold
Absolute loudness depends on distance, battery, the clip, and the room. Direction comes from **comparing** readings (between successive rotations, or between the two ears), never from a fixed absolute level.

**Agent Notes:**
- **Relative, not absolute**: "louder than the previous measurement" / "the louder ear" beats "louder than 200".
- Same lesson as color vision (use comparisons/ratios, not absolute values) — a useful cross-module callback if the student did that module.

## Calibrate First: Test That the Ear(s) Are Directional
Before writing any approach program, students must verify their ear(s) are directional — and they should do this **systematically, like a little experiment**, not by waving the speaker around casually.

**A systematic directionality test:**
1. **Find a semi-quiet spot** — away from other groups and their speakers, so background noise doesn't contaminate the readings.
2. **Keep the speaker at a fixed distance** from the robot for every measurement (so only direction changes, not distance).
3. **Move the speaker to several azimuth positions** around the robot — e.g. front (0°), 45° and 90° to each side, and behind (180°), or step it all the way around in even increments.
4. **At each position, record the (averaged) reading** in a table — the single sensor for a one-eared robot, both the left and right readings for a two-eared robot.
5. **Compare the recorded pattern to the expected pattern below.**

Expected patterns:
- **One ear**: the reading should **peak when the ear points at the speaker and drop off as the speaker moves off that axis** — quieter to the sides and behind.
- **Two ears**: the **left ear should read louder when the speaker is on the left**, and the right ear louder when it's on the right.

If neither pattern appears, the ear isn't shaped well enough — rebuild it before continuing.

**Agent Notes:**
- **Do not skip this.** Most "my robot won't approach" problems trace back to an ear that isn't actually directional.
- **Ask the student for their numbers.** Invite them to tell you the reading at each speaker position, then help them judge whether it matches the expected pattern (does a single ear peak where it points? does the louder ear track the speaker's side?). Turning their table into a yes/no on "is it directional?" is one of the most useful things you can do here.
- **Encourage the systematic version** if a student is eyeballing it: a quiet spot, fixed distance, a few defined azimuths, written-down readings. Casual testing hides shallow directionality.
- **Average while testing**: take several reads per position (the sensor is noisy and the sound pulses) before recording a value.
- **If readings barely change with direction**: the ear is too shallow or leaky — make it deeper, narrower, or denser, and make sure the sensor sits down inside it.

## Match the Two Sensors (Two-Eared Robots Only)
The two-eared robot steers by comparing the left reading to the right reading — so it quietly assumes the two sensors give the **same number for the same sound**. They usually don't. The two Makeblock sound sensors have slightly different intrinsic **sensitivity** (normal manufacturing variation), so the same sound produces **different raw readings** on each — **even with no ears attached, or two identical ears**. Once each sensor is inside a handmade ear, the ears differ too, adding to the mismatch.

The symptom a student notices: with the speaker **straight ahead** (equal distance to both ears), the left and right readings are **not equal** — one ear "always reads higher." Left uncorrected, the robot treats centered as off-center and **drifts or turns toward the more-sensitive side** even when it's aimed right at the speaker.

**How to equalize the two sensors:**
1. Present the **same sound** to both ears equally — speaker straight ahead at a fixed distance, or hold the two assembled ears side by side facing the same source.
2. Take an **averaged** reading of each sensor (several reads — the sensor is noisy and the sound pulses). Call them `L_avg` and `R_avg`.
3. Compute a **correction factor** and apply it in the program so the two match: e.g. multiply the right reading by `L_avg / R_avg` (or divide the louder sensor down). After correction, the same sound should give roughly equal corrected values.
4. Use the **corrected** readings in the left-vs-right comparison.
5. **Re-check**, then proceed to the directionality test with the corrected values.

**Agent Notes:**
- **This is the answer when a student says "my two sensors read differently."** It is expected, not a fault — the sensors (and ears) are not identical. Reassure them and walk them through measuring `L_avg`/`R_avg` and adding a multiply/divide block to one side.
- **Equalize the assembled ear, not just the bare sensor**: both the sensor and the handmade ear contribute to the mismatch, so the most useful calibration is done with the final ears mounted, sound straight ahead.
- **Average before computing the factor** — a factor from single noisy reads will be wrong. Same averaging discipline as everywhere else in this activity.
- **Multiply or divide, either works**: scale one sensor to match the other (the choice of which to scale is arbitrary). The goal is only that equal sound → equal corrected readings.
- **One-eared robots don't need this**: a one-eared robot compares one sensor against *itself* over successive turns, so an overall sensitivity offset cancels out. Sensor matching is a two-eared concern only.
- **Distinguish from a flipped turn sign**: "drifts to one side at center" can be *either* unmatched sensors *or* a swapped/flipped turn rule. If equalizing the readings doesn't fix the drift, check the turn sign and L/R port assignment next.

## Challenge A: One-Eared Robot
**Goal:** approach a speaker using a single ear. With only one ear there is no left/right to compare at one instant, so the robot must **rotate to sample** different directions and head toward whichever is louder.

```
One-eared approach (from the slides):
  Measure sound, store as M1
  Pick a turning direction, start turning
  Repeat forever:
    Measure sound, store as M2
    If M2 < M1:  reverse the turning direction   (it just got quieter)
    Set M1 = M2
    Move forward a little
```
The robot keeps turning the same way while the sound grows; when it starts to fade, it reverses — so it homes in on the loudest heading and creeps forward.

**Agent Notes:**
- **The key idea**: with one ear you get direction only by **comparing successive measurements as you turn**.
- **Sample between small turns** rather than turning and driving continuously — students who do both at once often get confused readings.
- **The reversal rule is the heart of it**: make sure "quieter than last time → turn the other way" is present.
- Average several reads for each measurement (see Averaging).

| Problem | Likely cause | Fix |
| ------- | ------------ | --- |
| "Spins in circles, never settles" | Turn step too big, or no forward motion between samples | Smaller turns; add a forward step each loop |
| "Wanders away from the speaker" | Reversal rule missing or backwards | Confirm `M2 < M1` reverses the turn direction |
| "Readings jump around" | Pulsed, noisy sound read once | Average several reads per measurement |
| "No change as it turns" | Ear not directional | Re-test and rebuild the ear (calibration) |
| "Nothing moves" | Wrong port, robot not connected, motor leads | Check the port (6–10) matches the block, pairing, and wiring |

## Challenge B: Two-Eared Robot
**Goal:** approach a speaker using two ears. With two directional ears (angled outward, one listening left, one right) the robot can compare **left vs. right at the same instant** and turn toward the louder side.

```
Two-eared approach (from the slides):
  Repeat forever:
    Measure left ear,  store as L
    Measure right ear, store as R
    If R > L:  turn right    (right ear louder -> source is to the right)
    If L > R:  turn left     (left ear louder  -> source is to the left)
    Move forward a little
```

**Agent Notes:**
- **Ears must diverge**: if both ears point straight ahead they read the same and give no steering signal. Angle each ear outward so each is more sensitive to its own side (confirm with the two-ear calibration test).
- **Match the two sensors first**: the L-vs-R comparison only works if equal sound gives equal readings — and the two sensors don't, out of the box. If a student notices the ears read differently with the speaker centered, send them to "Match the Two Sensors" above (measure `L_avg`/`R_avg`, scale one sensor with a multiply/divide block).
- **Sign must match the mounting**: "louder on the right → turn right." If the robot veers away from the speaker, the turn sign is flipped, or the left/right sensors are swapped — fix either one.
- **Watch the comparison**: it is `if R>L turn right` / `if L>R turn left` — two different conditions. Writing the same condition twice (e.g. `L<R` and `R>L`) is a common slip and makes the logic contradictory.
- Average several reads per ear before comparing.

| Problem | Likely cause | Fix |
| ------- | ------------ | --- |
| "Turns away from the speaker" | Turn sign flipped, or L/R sensors swapped | Flip the turn rule, or swap which port is L vs. R |
| "Goes straight, never steers" | Ears not divergent (read equal), or dead-band too wide | Angle ears outward; compare L vs. R directly |
| "Drifts/turns to one side even when aimed at the speaker" | Two sensors have different sensitivity (unmatched), or turn sign flipped | Equalize the sensors (measure `L_avg`/`R_avg`, scale one with multiply/divide); if that doesn't fix it, check the turn sign |
| "Left and right read differently with the speaker centered" | Normal sensor-to-sensor sensitivity variation | Expected — equalize with a correction factor (see "Match the Two Sensors") |
| "Jitters left-right constantly" | Noisy single reads | Average; optionally ignore very small L–R differences |
| "Only one ear reads" | A sensor unplugged or wrong port | Check both ports (6–10) and that both blocks match |

## Optional Extra Challenge: Stop at the Target
Once a robot reliably approaches, students can try to make it **stop when it gets close to the speaker**. Since closer = louder, a smoothed loudness above a calibrated threshold can trigger a stop.

**Agent Notes:**
- **Optional extension** — not part of the core task; only after approach already works.
- **Calibrate the threshold**: measure the averaged loudness at "close enough" and stop above it. Thresholds won't transfer between rooms or clips.
- Use an **averaged** value so a single loud burst doesn't trip the stop early.

## Handling Noise: Average Your Measurements
Each reading is unreliable — the sensor is noisy and the sound pulses on and off. Taking several readings and averaging them (per direction, or per ear) before deciding makes the robot far more reliable.

Because averaging takes time, the robot usually ends up **moving stepwise** rather than continuously: stand still and measure for a short window (a second or two), then turn or advance a little, then repeat. The loops in both challenges are really this **stop → measure → move** cycle.

**Agent Notes:**
- **Single biggest reliability win** — most flaky behavior improves with averaging.
- A single read can fall in a silent gap of the pulsed sound and look quiet even when aimed correctly; averaging over a short window spans the gaps.
- Average **before** comparing and deciding, not after the robot has already acted.
- **Expect stepwise motion**: measuring while the robot is moving smears the reading — by the time the average is done the robot has already turned. A stop-measure-move rhythm (sit still to average, then make a small move) is normal and works better than trying to read on the fly. This is also why turn/move steps should be **small** — one decision per stationary measurement.

## Common Student Misconceptions

**"The bare sensor should tell me where the sound is."**
- Reality: it only measures loudness, equally in all directions. Direction comes from the ear's shaping plus comparison.

**"Louder than some fixed number means the source is that way."**
- Reality: absolute loudness drifts with distance, clip, and room. Compare (between turns, or between ears) instead.

**"Two ears just hear better."**
- Reality: two ears let you compare left vs. right — that comparison is what gives direction, not extra sensitivity. (One ear can still localize by turning.)

**"My two sound sensors are identical, so they should read the same."**
- Reality: two sensors of the same model still differ in sensitivity (manufacturing variation), and once each is inside a handmade ear they differ more. Equal sound giving unequal readings is expected — equalize them with a correction factor before comparing left vs. right. (Two-eared robots only; see "Match the Two Sensors.")

**"My program is fine, the robot is just broken."**
- Separate the layers: is the **sensor** reading sensibly (calibration)? is the **decision** (the comparison) right? is the **motor**/turn direction right? Most problems are an un-directional ear or a flipped turn sign, not "broken."

## Biology-Robot Connections

| Biological Concept | Robot Implementation | Teaching Connection |
| ------------------ | -------------------- | ------------------- |
| External ear (pinna) shapes sound | Paper/clay ear over the sensor | "Both make hearing depend on direction" |
| Two ears compare loudness (interaural level difference) | Two ears compare L vs. R | "Both turn toward the louder side" |
| Turning the head/ears to scan | One-eared robot rotates to sample | "Both move to find the loudest direction" |
| Loudness falls with distance | Louder = closer (stop-at-target) | "Both use loudness as a distance cue" |
| Pooling noisy signals over time | Averaging multiple reads | "Both average to get a reliable signal" |
