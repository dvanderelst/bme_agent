# Color Vision

This document covers the biology of color vision and the two activities students complete during the color vision day(s): a human color discrimination game and a robot color discrimination challenge.

## Core Concepts

### Visible Light and Color
Visible light is only a narrow part of the electromagnetic spectrum. What we call color depends on the mixture of visible wavelengths reaching the eye or the sensor.

**Agent Notes:**
- An object's color depends on the wavelengths it reflects or emits.
- Color is not a property of light alone; it is also a property of how a visual system interprets that light.

### Rods and Cones in the Human Eye
The retina contains rod and cone photoreceptor cells. Rods are important for low-light sensitivity and peripheral vision. Cones are used for detail and color vision.

Humans use three cone classes for color vision. These cone classes are commonly labeled red, green, and blue because they differ in the wavelengths to which they are most sensitive.

### Color Is a Pattern Across Multiple Channels
Color vision requires more than sensitivity to certain wavelengths. The brain compares excitation across multiple cone channels and interprets the resulting pattern.

For example, red light stimulates the red-sensitive channel much more than the others, while yellow light stimulates both the red and green channels strongly but the blue channel weakly.

**Agent Notes:**
- Question: *Why are secondary colors important?*
  Answer: They make it obvious that different channels must be compared — yellow, cyan, and magenta each stimulate two channels.

### How Computer Screens Produce Color
A screen can make students perceive yellow even though it is only emitting red and green light. The perceived color depends on the pattern of stimulation across the cone channels, not on the presence of a separate "yellow pixel."

### Color Constancy and Context
Perceiving color involves more than comparing signals from the retina. The brain also uses context and estimates of illumination. Because of this, the same surface can appear different under different viewing conditions.

**Agent Notes:**
- Color constancy is the ability to recognize an object as having the same surface color under different lighting conditions.
- Ambiguous viewing conditions can produce disagreements about color perception, as in famous online image examples (e.g., the blue/gold dress).

## Activity 1: Human Color Discrimination

In this activity, students play a game in groups of 3. Each student wears goggles with a red, green, or blue filter and acts as a proxy for one cone class.

The group is presented with a computer screen showing 9 colored boxes (primary and secondary colors). The name of the target color is shown at the top. The goal is for the group to collectively select all boxes of that color.

Students collaborate by communicating how bright each box looks through their goggles. The table below shows how each color appears through each filter:

**Agent Notes:**
- Question: *Why can't one student identify all colors on their own?*
  Answer: One color channel doesn't contain enough information to distinguish many colors — just like a single cone class can't support full color vision on its own.

| Actual Color | Goggles That See This as Bright | Goggles That See This as Dark |
|---|---|---|
| Red | Red | Green, Blue |
| Green | Green | Red, Blue |
| Blue | Blue | Red, Green |
| Yellow | Red, Green | Blue |
| Cyan | Green, Blue | Red |
| Magenta | Red, Blue | Green |

## Activity 2: Robot Color Discrimination

### What the Robot Is Building
In this activity, students give their robot color vision by equipping it with up to three light sensors, each covered by a color filter. The result is essentially a **1-pixel RGB camera**: just like the human eye compares signals across three cone classes to determine color, the robot compares signals across three filtered sensors.

**Agent Notes:**
- Use the "1-pixel RGB camera" framing to help students understand the connection between Activity 1 and Activity 2. The goggles they wore are the same idea as the color filters on the sensors.
- Each filtered sensor acts like one cone class: it only responds strongly to its own color of light.

### How It Works
- The robot is equipped with up to 3 external light sensors.
- Students fit 3D-printed covers over the sensors and slide in red, green, or blue color filters, making each sensor sensitive to a narrow part of the spectrum.
- By comparing the readings across the three filtered sensors, the robot can determine the color of the light falling on them:

| Light Color | Red Sensor | Green Sensor | Blue Sensor |
|---|---|---|---|
| Red | High | Low | Low |
| Green | Low | High | Low |
| Blue | Low | Low | High |
| Yellow | High | High | Low |
| Cyan | Low | High | High |
| Magenta | High | Low | High |

### Step 0: Calibrate Before Programming

Before writing any program, students should take calibration measurements. This step saves a lot of time and guesswork.

**How to calibrate:**
1. Attach the color-filtered sensors to the robot.
2. Place the robot in the actual conditions it will operate in (same lighting, same distance from the colored object).
3. Present each color to the robot one at a time and note down the values each sensor returns.
4. From these measurements, students can see exactly what values correspond to each color — and use those values to set thresholds in their programs.

**Agent Notes:**
- If a student is struggling with their thresholds, ask: *"Did you take calibration measurements first? What values did your sensors give for each color?"*
- Calibration values will differ between robots and lighting conditions — there are no universal "correct" values.
- Encourage students to write down their calibration table before they start programming.

### Challenge 1: Color Mimicking
The robot determines the color of an LED bar held in front of it and switches on its onboard LEDs to match. For example, if it detects yellow, it lights up yellow.

**Program logic:**
1. Read the three filtered sensor values.
2. Compare them against calibration thresholds to identify the color.
3. Set the onboard LEDs to the matching color using the RGB LED block.
4. Repeat in a loop.

**Agent Notes:**
- The most common problem is wrong or missing calibration. If the robot misidentifies colors, ask: *"What values did your sensors give during calibration? Are your thresholds based on those?"*
- Remind students that the robot needs to check all three sensors together — no single sensor is enough to identify all colors.

### Challenge 2: Color Approach
Two LED bars of different colors are placed in front of the robot. The robot identifies which side holds its preferred color (chosen by the student) and moves toward it.

**Program logic:**
1. Turn slightly left, read and store the three sensor values in variables.
2. Turn slightly right, read and store the three sensor values in variables.
3. Compare the stored values to determine which side is showing the preferred color.
4. Move toward that side.

**Agent Notes:**
- Students must store sensor readings in variables — they can't take both measurements at the same time. Ask: *"Are you saving the first measurement in a variable before taking the second one?"*
- The preferred color is the student's choice — calibration must be done for that specific color under the actual lighting conditions.
- If the robot can't tell which side is brighter, the two LED bars may be too far apart or the turn angle too small.

### Challenge 3: Following a Colored Trail
Students lay down a track of two differently colored papers — one color on the left side, one on the right. The robot follows the track by turning left when it detects the color of the right-side paper, and turning right when it detects the color of the left-side paper.

**Program logic:**
1. In a forever loop, read the three filtered sensor values.
2. If the readings match the right-side color, turn left.
3. If the readings match the left-side color, turn right.

**Agent Notes:**
- Again, calibration is critical — students should measure the sensor values for both paper colors before programming.
- If the robot overshoots, suggest reducing motor power or turn duration.
- Students need to choose two colors that are clearly distinguishable by the sensors (e.g., red and green rather than red and orange).
