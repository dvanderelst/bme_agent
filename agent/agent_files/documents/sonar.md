# Sonar and Echolocation

This document covers the biology of echolocation and the sonar activities students complete: measuring sensor directionality, observing the sound-mirror problem, building obstacle-avoidance robots, and creating sonar canes. A central theme is the parallel between biological echolocation (bats, whales) and engineering sonar — both emit sound pulses and interpret the returning echoes, but differ in the richness of information they extract and how they process it.

## Core Concepts

### What is Echolocation?
Echolocation is a biological process where animals emit sound pulses and analyze the returning echoes to understand their environment. Bats and toothed whales are primary examples.

**Agent Notes:**
- **Key difference**: Sonar (engineering term) vs Echolocation (biological term)
- **Basic principle**: Pulse-and-echo sensing - emit sound, wait for echo, interpret returning signal
- **Distance calculation**: Echo delay ÷ 2 = object distance (sound travels to object AND back)

### How Distance is Calculated
Sound travels at approximately 343 meters per second in air. The total travel distance is speed × time, but since the pulse goes to the object and returns, the actual object distance is half the total travel distance.

**Agent Notes:**
- **Classroom approximation**: 1 millisecond of echo delay ≈ 17 cm of object distance
- **Why divide by 2?** The sound makes a round trip (to object and back)
- **Common mistake**: Students often forget to divide by 2

### The mBot Ultrasonic Sensor
The sensor has two metal cylinders: one emitter (marked T) and one receiver (marked R). It emits ultrasonic pulses at around 40 kHz — inaudible to humans — and returns distance in centimeters in mBlock. It uses the first strong echo it receives, not a detailed waveform.

**Agent Notes:**
- **Common misconception**: Students often think the sensor is seeing like a camera — it is not; it sends out sound and listens
- **Output unit**: Distance in centimeters (not raw time delay)
- **First-echo behavior**: The sensor reports distance to the nearest detectable object, not a map of everything ahead
- **Bias**: The sensor systematically underestimates distance; multiply readings by 1.25 to compensate
- **40 kHz and animals**: The sensor's 40 kHz emission is inaudible to humans but detectable by many animals — rats hear up to ~40 kHz, bats and dolphins well beyond it. Good discussion point for the biology connection

### Animals vs. Robots
While echolocating animals can extract rich information (location, movement, target properties), the mBot ultrasonic sensor primarily functions as a distance meter. A key difference is that animals use **broad-spectrum sounds** — bats sweep from roughly 25–100+ kHz, dolphins from 0–150 kHz — while the mBot emits a single narrow frequency (~40 kHz). This broad spectrum is part of what makes animal echolocation so much more powerful.

**Agent Notes:**
- **Animal examples**: Bats, sperm whales, oilbirds, cave-dwelling swiftlets
- **Not all bats echolocate**: Only microbats (e.g. Little Brown Bat, Big Brown Bat) echolocate; megabats (fruit bats, flying foxes) rely on vision and smell
- **Not all whales echolocate**: Only toothed whales (dolphins, sperm whales, orcas, belugas) echolocate; baleen whales (humpback, blue, fin) do not
- **Robot limitation**: mBot mainly uses sonar for distance estimation, not detailed mapping
- **Important distinction**: "The mBot sensor is useful but not bat-level echolocation"
- **Broad vs. narrow spectrum**: Animals use broad-spectrum calls; the mBot uses a single ~40 kHz frequency — this is one reason animal sonar extracts richer information
- **Real-world engineering uses**: Parking sensors, drones, occupancy detectors, fish finders, seafloor mapping, submarine sensing

### Sensor Directionality
The ultrasonic sensor is most sensitive straight ahead and less sensitive at angles. This creates a directional detection pattern.

**Agent Notes:**
- **Practical range**: For a ~10 cm object: ~240 cm straight ahead, ~190 cm at 20° off-axis, ~120 cm at 30° off-axis — range drops sharply with angle
- **Thin targets**: Smaller or softer objects will have shorter range than the figures above
- **Asymmetry is normal**: Directional patterns don't need to be perfectly symmetric
- **Key concept**: Both emitter and receiver are directional, so the whole sensor is directional

### The Sound-Mirror Problem
Smooth, angled surfaces can reflect sound away from the receiver, making objects effectively invisible to the sensor.

**Agent Notes:**
- **Student-friendly analogy**: "A smooth angled wall acts like a mirror for sound"
- **Solution**: Use rougher surfaces or change approach angle
- **Why this matters**: Explains many "my robot drove into a wall" moments

## Activity 1: Understanding the Sensor

### Measuring Directionality
Students measure how the sensor's detection range varies with angle.

**Setup:**
- Sonar sensor in port 1
- Line follower can be omitted
- LEDs provide feedback (green = detected, red = not detected)

**Procedure:**
1. Move an object around in front of the robot
2. Mark boundaries where object is just barely detected
3. Create a directional detection pattern

**Agent Notes:**
- **Expected outcome**: Directional pattern, not a perfect circle
- **No-detection value**: The sensor returns exactly 400 cm when it detects nothing — if a student sees a constant 400, the sensor is not picking up an echo, not measuring 4 meters
- **Body interference**: The student's own body returns stronger echoes than most test objects — remind them to keep their body out of the detection zone while moving the test object
- **Troubleshooting**: If no detection:
  - Is the sensor properly connected to the correct port?
  - Is the mBot paired and connected in mBlock?
  - Try a larger or harder object (soft surfaces absorb more sound)
- **Question**: *"Why isn't the detection range the same in all directions?"*
  **Answer**: "The sensor is directional - it's most sensitive straight ahead"

### Observing the Sound-Mirror Problem
Students compare detection of smooth walls at different angles.

**Key Lesson:**
- Straight-on: Easy detection
- Angled: May be invisible due to sound reflection

**Agent Notes:**
- **Common misunderstanding**: "Sonar is unreliable"
- **Correction**: "Echo return depends strongly on geometry and surface properties"
- **Real-world connection**: Explains why bats change head position to get better echoes

## Activity 2: Obstacle-Avoidance Robot

### Two-Sensor Setup
Uses two ultrasonic sensors (typically left on port 1, right on port 2) for spatial awareness.

**How It Works:**
1. Continuously read both sensors
2. Apply 1.25 correction factor (sensor underestimates distance)
3. Identify the smaller reading (more constrained side)
4. Decide if a turn is needed

**Agent Notes:**
- **Safe distance**: ~30 cm (adjust based on speed and arena)
- **Single vs dual sensors**: One sensor detects "something ahead", two sensors allow left/right comparison
- **Turn direction**: Must match sensor mounting - test empirically

### Programming Logic

```
Single-sensor rule: If ultrasonic reading < threshold → nearby object ahead

Two-sensor obstacle avoidance:
1. Read left_distance and right_distance
2. Apply correction: distance × 1.25
3. Set min_distance = smaller of the two
4. If min_distance > safe_distance → drive forward
5. If min_distance < safe_distance → turn away from constrained side
6. Repeat continuously
```

**Agent Notes:**
- **Common problem**: "My robot turns the wrong way"
  **Solution**: Test with obstacle clearly on one side, check which sensor gives smaller value, flip turn rule if needed
- **Bias correction**: Multiply readings by 1.25 as shown in example programs

### Troubleshooting Guide

| **Problem** | **Likely Cause** | **Solution** |
|-------------|------------------|--------------|
| "It doesn't see the wall" | Wall smooth and angled, or outside detection cone | Face wall straight on, use rougher surface |
| "It saw that cup but not this skinny thing" | Smaller targets return weaker echoes | Explain that range depends on target size and reflectivity, not just distance |
| "Readings seem too small" | Not using 1.25 correction factor | Add multiplication by 1.25 in code |
| "Robot turns wrong way" | Turn rule reversed for sensor mounting | Test with clear obstacle, flip logic if needed |
| "Works alone but not with others" | Sensor interference from multiple robots | Space robots apart, test one at a time |
| "Should work from 4 meters" | Confusing manufacturer max with classroom reality | Explain practical range is much shorter |
| "Program runs but nothing moves correctly" | Wrong ports, mBot not connected, or swapped motor leads | Check mBot was paired and added in mBlock; verify sensor ports and motor wiring |

**Agent Notes (Arena Setup):**
- **Use complex objects**: Toys, irregular objects with multiple surfaces return strong echoes from many angles — smooth walls cause the mirror effect and make poor arena boundaries
- **Cup height**: If using plastic cups as obstacles, they must be tall enough to reach the sensor's height on the robot — otherwise the sensor will literally overlook them
- **First diagnostic question**: "What values is your sensor showing right now?"
- **Second diagnostic question**: "What happens when you put your hand directly in front of it?"
- **Key insight**: Most problems fall into one of three categories: sensor placement, code logic, or unrealistic expectations about range
- **Separate three layers**: When a student reports wrong behavior, distinguish sensing (are the values correct?), decision logic (is the comparison right?), and motor action (is the robot turning the right way?) — students often conflate these
- **Unknown behavior**: Ask whether they are using one sensor or two, which ports the sensors are in, and whether they copied the example program or modified it
- **Block reference**: For specific block usage, see programming_blocks.md

## Activity 3: Sonar Cane

### Purpose
Detects overhanging obstacles that a sweeping cane might miss, using auditory feedback.

### Physical Setup
The robot is mounted on a 1/2-inch PVC pipe. Students can attach 1 or more sonar sensors anywhere on the pipe using 3D-printed brackets or Lego-compatible blocks. The device looks horizontally for overhanging obstacles while the user's physical cane sweeps the floor.

### How It Works
- Distance → auditory feedback via robot speaker using **beep duration** (not pitch)
- Closer obstacles → **longer** beeps; further obstacles → shorter beeps
- Beyond ~1.2 m → silence (no beep)
- Below ~0.6 m → maximum beep duration + brief motor activation for vibrational feedback

**Agent Notes:**
- **Feedback is duration-based**: The example program encodes distance as beep length using `b = 0.49 - 0.4 × distance` (in meters), clipped to 0–0.25 seconds — do NOT describe it as pitch-based
- **Safety feature**: At very close distances, motors briefly activate to give vibrational feedback in addition to the beep
- **Testing**: Use overhanging obstacles (e.g. cardboard held at head height) — the physical cane handles floor obstacles, sonar handles what the cane misses
- **Real-world connection**: Similar to electronic travel aids for visually impaired

### Programming Structure

```
Sonar cane logic:
1. Read ultrasonic distance, apply 1.25 correction, convert to meters
2. Calculate beep duration: b = 0.49 - 0.4 × distance
3. If b ≤ 0 (distance > ~1.2m) → silence
4. If b > 0.25 (distance < ~0.6m) → beep for 0.25s + brief motor activation
5. Otherwise → beep for b seconds
6. Repeat in loop
```

**Agent Notes:**
- **Calibration needed**: Test frequency mapping in actual conditions
- **User testing**: Have students test while blindfolded to experience the feedback



## Common Student Misconceptions

**"Sonar should detect everything like a camera"**
- **Reality**: Sonar is directional and has limited range
- **Response**: "Remember how bats move their heads to scan? The robot sensor works similarly - it only 'sees' in one direction at a time"

**"The 4-meter range should work in class"**
- **Reality**: Manufacturer specs are best-case; classroom conditions reduce range
- **Response**: "In perfect conditions with large targets, yes. But in our classroom with smaller objects, the practical range is much shorter"

**"If one sensor works, two should be twice as good"**
- **Reality**: Two sensors enable comparison, not just better detection
- **Response**: "Think about your two ears - they don't just hear better, they help you tell which direction sound comes from"

## Biology-Robot Connections

| **Biological Concept** | **Robot Implementation** | **Teaching Connection** |
|------------------------|--------------------------|-------------------------|
| Bat echolocation pulses | Ultrasonic sensor pulses | "Both send out sound and listen for echoes" |
| Two ears for localization | Two sensors for comparison | "Both compare left/right to determine direction" |
| Bat head movement | Robot turning | "Both change orientation to scan environment" |
| Echo delay processing | Distance calculation | "Both use time delay to calculate distance" |
| Sound mirror effect | Smooth surface reflection | "Both can 'lose' echoes from angled surfaces" |
| Broad-spectrum calls (25–150 kHz) | Single frequency (~40 kHz) | "Animals sweep many frequencies; the robot uses just one — part of why animal sonar is richer" |

