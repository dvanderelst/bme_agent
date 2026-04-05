# Olfaction and Odor-Guided Behavior

This document covers the biology of olfaction and the two main investigations students complete: observing termite trail-following behavior, and building a robot that imitates that behavior using a line sensor as a substitute for an olfactory sensor. A central theme is that olfaction is not just about detecting chemicals — it is about using chemical information to guide movement and make decisions.

## Core Concepts

### What is Olfaction?
Olfaction is the sense of smell. The basic mechanism is that chemical molecules in the environment bind to receptor proteins on sensory cells. The module uses a **lock-and-key analogy**: odor molecules are like keys, receptors are like locks — different keys fit different locks better than others.

**Agent Notes:**
- **Lock-and-key caveat**: The analogy is useful but not perfectly literal — a single odor can stimulate multiple receptors, and a single receptor can respond to multiple odors
- **Odors are mixtures**: Most natural odors are not single chemicals but complex mixtures
- **Concentration matters**: Behavior depends not just on what chemical is present but how much of it there is

### Biological Diversity of Olfaction
Different animals have different numbers of odor receptor types. The module compares humans, mice, dogs, and fruit flies as examples of this diversity. In humans, olfactory sensory cells are located in the olfactory epithelium high in the nasal cavity, feeding into the olfactory bulb. In insects, the key sensory structures are the antennae and maxillary palps, which carry different types of sensilla (small sensory hairs).

**Agent Notes:**
- **Simple comparison**: Humans smell primarily through the nose; insects smell strongly through structures on their head, especially antennae
- **Why olfaction matters in nature**: In insects, olfaction is linked to food finding, mate recognition, predator avoidance, navigation, pollination, agriculture, and disease transmission
- **Why olfaction matters in humans**: Food choice, hazard detection, flavor and fragrance industries

### Trail Following vs. Plume Following
Two distinct behaviors must be kept separate:

- **Trail following**: An animal follows a chemical cue physically laid down on a surface (like a line of pheromones on the ground). The cue is where you walk, not where you sniff.
- **Plume following**: An animal tracks an odor carried through air from a distant source, using the spatial structure of the concentration gradient to navigate.

**Agent Notes:**
- **The classroom activities are about trail following**, not plume following — keep this distinction clear if students ask about "smelling" the source from a distance
- **Key difference**: In trail following the signal is on the surface; in plume following the signal is in the air and changes with air currents

### The Robot Substitute: Line Sensor as Odor Analog
The robot used in this module does **not** have a real chemical or gas sensor. Instead, a **line follower sensor** is used as a simplified stand-in for an olfactory sensor. The dark line on the floor acts as a proxy for a chemical trail. The robot's task — staying on the line by comparing left and right sensor inputs — mirrors the logic a trail-following animal uses when sampling a pheromone trail.

**Agent Notes:**
- **Critical framing**: The robot is not literally smelling. It is imitating the *logic* of odor-guided trail following with a substitute signal
- **Do not say "the robot smells"**: Correct phrasing: "the robot uses a light sensor as a stand-in for an olfactory sensor" or "the line acts as a proxy for a chemical trail"
- **The biomimetic idea**: Biology provides the guidance logic (compare left vs. right, steer toward the signal, search when lost); the robot provides an engineered version of the same control problem

---

## Activity 1: Termite Trail Following

### Why Termites?
Termites show easy-to-observe trail-following behavior, making them excellent classroom organisms for thinking about how simple local sensory rules can produce directed movement. Worker termites (the relevant caste for this activity) follow trails of pheromones during foraging.

**Agent Notes:**
- **Use worker termites**: Workers are the trail-following caste. Other castes in the container may not follow trails — if students observe mixed behavior, this is likely why
- **The pen ink connection**: The module uses Bic ballpoint pen ink to draw trails. Some ballpoint inks contain **2-phenoxyethanol**, a compound that can mimic a termite trail-following pheromone. The termites respond to the chemical, not the visible line
- **Pen variability**: Not every Bic pen or termite species will perform equally well — avoid claiming it always works perfectly. If nothing happens, check the pen brand and termite condition

### Termite Care and Handling
Termites are sourced from Carolina Biological. Keep them in a covered container away from direct sunlight, with moist cardboard or paper towels (and optionally untreated rotting wood). Handle with a soft brush, not fingers. Do not let them dry out or sit on hot, bright surfaces.

**Agent Notes:**
- **Variability is normal**: Individual termites vary in behavior — not every termite in a trial will follow the trail
- **Stressed or dry termites behave poorly**: If behavior is weak across all termites, check that they are moist and have been handled gently

### What the Termites Are Detecting
Students often assume termites follow the visible ink line using vision. The module's key point is **chemical guidance**, not visual guidance. Termites use chemoreceptors on their antennae to detect trail pheromones; the ink acts as a chemical mimic of those pheromones.

**Agent Notes:**
- **Redirect visual explanations**: If a student says "the termite sees the line," steer toward: "What sensory structures do insects use to detect chemicals? Could the termite be responding to something in the ink rather than its color?"
- **Chemical mimic framing**: The pen line is a stand-in for a trail pheromone, not a natural termite trail — describe it as a chemical analog or mimic

### The Four Trail Investigations

Students complete four investigations, each probing a different aspect of trail-following behavior:

| **Investigation** | **What students draw** | **What they observe** | **What it reveals** |
|---|---|---|---|
| General observations | Straight line and/or large circle | Whether path is straight or wavy; how far termites leave trail before correcting | Suggests the local sampling rules termites use |
| Curved paths | Circles of ~9 cm and ~3 cm radius | How many termites complete 1/4 and 1/2 of the circle | Shows limits of following a continuously curving trail |
| Corners | Bends of ~30°, 60°, and 90° | How many of 5 termites pass the bend | Shows how abrupt turns challenge a local guidance rule |
| Intersections and gaps | Figure-8 or crossing paths; circles with increasing gap widths | Choices at 30° and 90° intersections; widest gap crossed | Shows ambiguity at branch points and failure when signal disappears |

### Interpreting Termite Behavior

**Agent Notes:**
- **Wavy path**: Suggests the termite is sampling and repeatedly correcting, not locking rigidly onto the line — expected and normal
- **Gentle curves**: Easier because the direction changes gradually
- **Sharp corners**: Hard because the termite may overshoot before it has enough information to correct
- **Intersections**: Hard because two plausible directions are present simultaneously
- **Gaps**: Hard because there is no surface cue — success depends on whether momentum and local searching can reacquire the trail on the other side
- **Present as candidate interpretations**: These observations are evidence for behavioral rules, not proof of a complete neural mechanism

### Candidate Algorithm for Termite Trail Following
The module asks students to infer what rules termites appear to use. A strong student-level candidate algorithm:

```
Termite trail-following rule:
1. Move forward while the trail cue is detected near the head/antennae
2. Continuously sample the cue on the left and right sides
3. If cue is stronger on one side → turn slightly toward that side
4. If cue disappears → search locally until trail is found again
5. At intersections → continue straight, or choose smallest required turn,
   or choose the branch with the strongest cue
```

**Agent Notes:**
- **Help students propose rules from their observations**: Ask "what rule would produce the behavior you saw?"
- **Don't claim completeness**: The classroom activity reveals plausible rules, not the full neural mechanism

---

## Activity 2: Robot Trail Following

### Setup
The mBot uses a **line follower sensor** (typically in port 2) to follow a dark line on a light surface. The sensor has two light detectors (left and right) that report whether each side is over the dark line or not. The robot imitates termite trail-following logic by comparing the two sensor values and steering toward the line.

### Sensor Values and Meaning

| **Sensor Value** | **Interpretation** | **Typical Action** |
|---|---|---|
| 1 | Centered on the line | Drive forward |
| 2 | Veering left (right detector on line) | Turn right to correct |
| 3 | Veering right (left detector on line) | Turn left to correct |
| 4 | Line lost (neither detector on line) | Search, slow down, or briefly continue forward |

### Programming Logic

```
Robot trail-following logic:
1. Read line follower sensor value
2. If value = 1 → drive forward
3. If value = 2 → turn right (correct left drift)
4. If value = 3 → turn left (correct right drift)
5. If value = 4 → apply gap strategy (continue briefly, slow search, or stop)
6. Repeat continuously
```

**Agent Notes:**
- **Relevant mBlock blocks**: `line follower sensor [port] value`, `move forward at power [slot]%`, `turn left/right at power [slot]%`, `left wheel at [slot]%, right wheel at [slot]%`, `if/else`, variables and comparison blocks
- **Speed matters**: Too fast → overshoots corners and gaps; too slow → works but may be unstable. Suggest tuning speed first when behavior is wrong
- **Gap strategy**: The sensor returns 4 when the line is lost. The robot needs explicit code for this — brief forward continuation is the simplest approach

### Challenges that Mirror Termite Behavior

| **Challenge** | **Why it's hard** | **Suggested fix** |
|---|---|---|
| Sharp corners | Robot moves too fast to detect and correct in time | Reduce speed; increase turn response |
| Gaps | Sensor reads 4, no guidance signal | Add brief forward continuation, or small search sweep |
| Intersections | Sensor may read 1 (centered) on a crossing, masking the branch | Add explicit branch rule in code (e.g., always go straight) |

**Agent Notes:**
- **Connect to termite observations**: These robot failures mirror what students saw with the termites — the same ambiguous situations (gaps, corners, intersections) cause both animal and robot to struggle
- **When a student's robot fails at gaps**: Ask "what does the sensor read when there's no line? What should the robot do with that value?"
- **When a student's robot fails at intersections**: Ask "does your code have a rule for what to do when it sees value 1 at a crossing? The robot can't tell a straight stretch from an intersection center"

---

## Common Student Misconceptions

**"The termites are following the line because they can see it"**
- **Reality**: Termites respond to a chemical in the ink, not the visible color
- **Response**: "What sensory structures do termites use to detect their environment? Could the ink contain something chemical rather than visual that the termite detects?"

**"The robot is smelling the trail"**
- **Reality**: The robot uses a light sensor, not a chemical sensor
- **Response**: "The robot is imitating the *logic* of smell-guided movement — comparing left and right inputs and steering toward the signal — but the sensor is detecting light, not chemicals"

**"Trail following and plume following are the same thing"**
- **Reality**: Trail following means the cue is on the surface; plume following means tracking odor through air
- **Response**: "In this module, the termite is following a cue that's physically laid down on the paper — like following painted footprints rather than sniffing for a smell in the air"

**"The termite algorithm must be complicated to produce that behavior"**
- **Reality**: Complex-looking behavior can emerge from a small set of simple local rules
- **Response**: "The candidate rule is just: detect the cue, compare left vs. right, steer toward the stronger side, search if lost. That's it — no map, no memory of the whole path"

---

## Biology-Robot Connections

| **Biological Concept** | **Robot Implementation** | **Teaching Connection** |
|---|---|---|
| Trail pheromone on surface | Dark line on floor | "Both are surface-laid cues the agent follows" |
| Chemoreceptors on antennae (left/right) | Line follower sensor (left/right detector) | "Both compare left and right input to decide which way to steer" |
| Repeated small steering corrections | Short motor adjustments in a loop | "Both accumulate small corrections to stay on path" |
| Wavy path from sampling | Slight oscillation around line center | "Both weave slightly because they're correcting, not locked on" |
| Failure at sharp corners | Robot overshoots at high speed | "Both struggle when the trail changes direction faster than they can correct" |
| Failure at gaps | Sensor reads 4, no signal | "Both fail when the cue disappears and need a search strategy" |
| Failure at intersections | Sensor reads 1 at crossing, ambiguous | "Both face ambiguity when two plausible paths are present" |
| Trail following ≠ plume following | Line following ≠ gradient climbing | "Following a surface path is a different problem from tracking a diffusing source" |
