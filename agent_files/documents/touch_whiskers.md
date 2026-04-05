# Touch, Whiskers, and Mechanical Whisker Sensing

This document covers the biology of touch and whisker sensing, and the two main student activities: a two-point discrimination test of human tactile acuity, and a robot that uses flex sensors as mechanical whiskers for obstacle avoidance and wall following. A central theme is **active sensing** — animals and robots that move their sensors to gather information, rather than waiting passively for contact.

## Core Concepts

### Touch Is Not One Sense
Human skin contains multiple receptor types that differ in what kind of stimulus they emphasize and how precisely they localize it. Two organizing dimensions matter:
- **Dynamics**: phasic receptors respond strongly to *change* (onset, offset, vibration); tonic receptors continue signaling during *sustained* contact.
- **Receptive field size**: small fields give finer spatial resolution; large fields give coarser, broader coverage.

**Agent Notes:**
- **"Slow adapting" does not mean slow to start**: A tonic receptor can respond quickly at touch onset and still keep signaling — "slow adapting" refers to its sustained response, not a delayed one
- **Key insight for students**: No single receptor does everything — different types specialize for different aspects of touch

### The Four Main Receptor Types

| **Receptor** | **Dynamics** | **Field / Depth** | **Best student takeaway** |
|---|---|---|---|
| Merkel disk | Tonic | Small / shallow | Fine spatial detail, edges, sustained touch — why we can read Braille or feel shape |
| Meissner corpuscle | Phasic | Small / shallow | Light flutter and motion across skin; detects touch changes and low-frequency vibration |
| Pacinian corpuscle | Very phasic | Large / deep | High-frequency vibration and brief pressure changes; extremely sensitive to vibration |
| Ruffini ending | Tonic | Large / deep | Skin stretch and lateral deformation; useful for sensing hand shape and sustained deformation |

**Agent Notes:**
- **Small field + tonic = fine spatial detail** (Merkel): best for two-point discrimination tasks
- **Small field + phasic = motion detection** (Meissner): best for detecting sliding or flutter
- **Large field + very phasic = vibration** (Pacinian): responds to brief, high-frequency inputs
- **Large field + tonic = stretch** (Ruffini): tracks deformation over a larger skin region

### Two-Point Discrimination
The two-point discrimination task asks whether two simultaneous touches can be perceived as separate or blur together as one. The smallest spacing that still feels like two points is the **threshold** for that body site. Lower threshold = greater spatial acuity.

Body regions with denser receptors and smaller receptive fields (fingertips, lips) perform better than regions with sparser, larger-field receptors (back, calf).

**Agent Notes:**
- **What it measures**: Spatial acuity of touch — how close two stimuli can be before they are no longer distinguishable
- **Why fingertips beat the back**: More receptors per area, smaller receptive fields, and more cortical brain area devoted to processing (as shown by the homunculus)
- **"Better" means finer resolution, not stronger feeling**: Correct students who interpret lower threshold as "more intense" sensation
- **Homunculus connection**: Sensitive body regions have disproportionately large cortical representation — the homunculus is not body-proportional because touch is not uniform

### Animal Whiskers (Vibrissae)
Whiskers are specialized tactile hairs — stiffer, thicker at the base, and more tapered than ordinary fur. The whisker shaft acts as a flexible lever: it contacts the object, bends, and the mechanical deformation is detected by receptors in the **follicle at the base**. The tip touches; the base senses.

Many animals actively move their whiskers — **whisking** — to scan nearby space rather than waiting passively for contact. Arrays of whiskers give richer spatial information than a single whisker because different whiskers bend in different ways, providing a spatial pattern rather than a single yes/no signal.

**Agent Notes:**
- **Sensing is at the base, not the tip**: "A whisker works like a flexible lever — when the tip hits something, the base senses how it bent"
- **Active sensing**: Whisking is analogous to moving fingertips across a surface to feel texture — the animal moves the sensor, not just the object
- **What whiskers are used for**: Near-field navigation, object localization, wall following, texture discrimination, judging gap width, orienting in low-light conditions (species-dependent)
- **Whisker array**: Multiple whiskers give a spatial pattern of contact — richer than one sensor
- **Antennae analogy**: Antennae in insects can serve whisker-like tactile roles (touch and movement sensing) even though they are anatomically different from mammalian vibrissae — a useful analogy but not the same structure

---

## Activity 1: Two-Point Discrimination

### Procedure
A tester applies two points to the skin simultaneously. The subject (eyes closed) says whether they feel one or two points. Spacing starts large and decreases. The smallest spacing that still feels like two points is recorded as the threshold for that body site. Students compare multiple body regions and enter results into the Brainmapper tool to generate a cortical homunculus.

**Setup:**
- Eyes closed throughout (removes visual bias)
- Both points applied at exactly the same time (sequential application can be mistaken for motion)
- Start at a large spacing and decrease (makes the task easier to understand early in the trial)
- Use gentle, consistent pressure (different pressure can change the answer)
- Compare at least two or three body regions (fingertip, palm, forearm, back, etc.)

**Agent Notes:**
- **Brainmapper**: Results can be entered at brainmapper.org/experiment to visualize the cortical homunculus
- **Technique errors to watch for**:
  - Points not applied simultaneously → subject may use timing differences instead of spatial ones
  - Inconsistent pressure across trials → artificially shifts the threshold
  - Testing slightly different spots each time → receptor density varies even within a body region
  - Sharp or uncomfortable touch → switches the task from discrimination to pain
- **Expected result**: Fingertips and facial regions are usually more sensitive (lower threshold) than back, calf, or upper arm — though exact rankings vary by person and technique

### Interpreting Results
**Agent Notes:**
- **Lower threshold = greater spatial acuity**: More receptors, smaller receptive fields at that site
- **Homunculus distortion**: The brain devotes more cortical space to regions with finer touch acuity — fingertips are enormous on the homunculus, the back is tiny
- **Individual variation**: Results vary between people; variation within a class is expected and not a sign of experimental error

---

## Activity 2: Robot Whisker Sensing

### Hardware Setup
The mBot uses **flex sensors** as mechanical whiskers. The flex sensor has a nominal flat resistance of ~10 kΩ that increases when bent. In this module's implementation, whiskers are read through the **light sensor block** on **port 3 or port 4** in mBlock.

**Agent Notes:**
- **Value drops when bent**: In this module's wiring and code, the displayed value in mBlock *decreases* when the whisker bends — this is counterintuitive but correct for this setup. Trust the measured mBlock values, not the assumption that more bend = bigger number
- **Use the light sensor block**: Not the sonar or line sensor block — read port 3 or 4 with the light sensor block
- **One-direction bending only**: Flex sensors can be damaged by bending in the wrong direction or by creasing — emphasize this during mounting

### Safe Handling and Mounting
- Bend only in the intended direction — bending the wrong way can damage the sensor
- Do not crease or sharply fold the sensor
- Mount so the whisker is free to flex; do not tape over the active bending region
- Ensure the connector is fully seated and strain-relieved so the sensor does not wiggle at the plug
- **Always verify that values change** before writing behavior code — gently bend the whisker by hand and watch the mBlock reading

### Calibration Workflow

| **Step** | **What to do** |
|---|---|
| 1. Read resting values | With no contact, note left and right whisker values separately |
| 2. Read bent values | Gently bend each whisker as it would during contact; note the changed values |
| 3. Choose thresholds | Pick a threshold between resting and bent for each whisker — left and right thresholds don't need to match |
| 4. Test at low speed | Run the robot slowly first; logic errors are easier to catch and less likely to damage the sensor |
| 5. Refine from behavior | If robot reacts too late → raise sensitivity; if it reacts constantly → lower sensitivity or improve mounting |

### Obstacle Avoidance Logic
Contact on one side should bias movement away from that side — the direct biomimetic link to whisker behavior.

| **Condition** | **Action** |
|---|---|
| Neither whisker bent | Drive forward |
| Left whisker bent | Turn right (slow left, speed right) |
| Right whisker bent | Turn left (slow right, speed left) |
| Both whiskers bent | Back up briefly, then turn to escape |

```
Obstacle avoidance logic:
1. Read left_whisker and right_whisker values
2. If left_whisker < threshold AND right_whisker < threshold → forward
3. If left_whisker < threshold → turn right
4. If right_whisker < threshold → turn left
5. If both < threshold → reverse briefly, then turn
6. Repeat continuously
```

**Agent Notes:**
- **Thresholds are empirical**: Measure resting and bent values first, then pick a value between them — do not guess in advance
- **Separate variables for left and right**: Makes the logic transparent and easier to debug
- **Start slow**: Slow robots are easier to debug and less likely to damage the sensors

### Wall Following Logic
Keep one whisker just barely contacting the wall. If contact is lost, turn slightly toward the wall. If the whisker bends too much, turn slightly away. This creates a feedback loop rather than a one-time reaction — closer to how animals use whiskers for wall following.

```
Wall-following logic (right wall):
1. Read right whisker value
2. If value above resting (contact lost) → turn slightly right toward wall
3. If value below threshold (too much bend) → turn slightly left away from wall
4. Otherwise → drive forward
5. Repeat continuously
```

**Agent Notes:**
- **Wall following oscillates**: Usually means turn response is too strong or speed is too high — reduce speed, soften the turn, or add a short delay between corrections
- **More whiskers = better coverage**: Students can extend the design by adding more sensors; animals benefit from arrays of whiskers for the same reason — but more sensors means more calibration and code complexity

### Troubleshooting Guide

| **Problem** | **Likely Cause** | **What to try** |
|---|---|---|
| Whisker value does not change at all | Wrong port, wrong block, loose cable, or damaged sensor | Check block reads port 3 or 4; reseat cable; gently bend sensor by hand to confirm it works |
| Value changes but robot does nothing | Threshold not crossed, or condition not inside the running loop | Print/read values, compare to threshold, verify the if-statement is inside the loop |
| Robot reacts constantly without contact | Threshold too close to resting value, bent mounting, or cable noise | Recalibrate resting values; remount whisker so it sits neutral when not contacting anything |
| Robot turns the wrong way | Left/right logic reversed, or motors wired opposite to expectations | Swap turn logic in code first; if movement directions are globally wrong, check M1/M2 wiring |
| Sensor stops working after handling | Bent in the wrong direction or creased | Inspect for damage; replace if needed; reinforce one-direction bending rule |
| Wall following oscillates | Turn response too strong or speed too high | Reduce speed, soften turn strength, or add a brief delay between corrections |

---

## Common Student Misconceptions

**"Better touch sensitivity means feeling things more intensely"**
- **Reality**: In the two-point task, better sensitivity means finer spatial resolution — distinguishing nearby points as separate, not feeling them more strongly
- **Response**: "Lower threshold means the brain can tell two nearby touches apart — it's about precision, not intensity"

**"Whiskers feel at the tip"**
- **Reality**: The tip contacts the object, but sensing happens at the follicle at the base where the shaft bends
- **Response**: "Think of the whisker like a flexible lever — the tip touches the object, but the base is where the sensor is"

**"Antennae are basically whiskers"**
- **Reality**: Not anatomically — vibrissae and antennae are very different structures — but they can serve similar tactile roles in behavior
- **Response**: "They're built differently, but in some insects, antennae do provide touch information in a similar way to how whiskers work for mammals"

**"The robot's whisker value goes up when it bends more"**
- **Reality**: In this module's wiring, the value displayed in mBlock *decreases* when the flex sensor bends
- **Response**: "In this setup, bending decreases the value — trust what you measure in mBlock, not what you'd expect from the sensor alone"

**"Tonic means slow to respond"**
- **Reality**: Tonic (slow-adapting) means the receptor keeps signaling during sustained contact — it can respond fast at onset, it just doesn't stop
- **Response**: "Slow-adapting describes how long the receptor keeps firing, not how quickly it starts"

---

## Biology-Robot Connections

| **Biological Concept** | **Robot Implementation** | **Teaching Connection** |
|---|---|---|
| Whisker shaft bends on contact | Flex sensor bends on contact | "Both convert physical deflection into a signal" |
| Sensing at the follicle (base) | Resistance change read at the connector end | "Both detect bending at the anchor point, not the tip" |
| Left/right whisker comparison | Left/right sensor threshold comparison | "Both compare input from two sides to decide which way to turn" |
| Turn away from contact side | Motor logic: contact on left → turn right | "Same rule: steer away from the obstacle that touched you" |
| Wall following by whisker contact | Wall following by whisker threshold loop | "Both maintain just enough contact to stay near the surface" |
| Whisker array (multiple whiskers) | Multiple flex sensors | "More sensors → better spatial coverage, same engineering tradeoff" |
| Active sensing / whisking | Robot moving through space to trigger contact | "Both gather information by moving the sensor, not waiting passively" |
| Small receptive field = fine acuity | More whiskers = finer spatial resolution | "More sensors, spaced closer, give a finer 'picture' of nearby space" |
