# Color Vision

This document covers the biology of color vision and the activities students complete during the color vision day(s): two browser color games that run from a local HTML file on the student's own computer (RGB Codebreaker and the Color Constancy Challenge), a human color discrimination game (a deployed web app with a goggle trainer and a timed group competition), and a robot color discrimination challenge.

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

## Activity 1: RGB Codebreaker (Local HTML Game)

RGB Codebreaker is a color-matching game that students open in a web browser from a local HTML file on their own computer (it is not a deployed web app — there is no server, login, or internet dependency). Students view a target color square, then adjust red, green, and blue sliders to recreate it in a "Your Color" square. It teaches additive color mixing, numerical color representation, and the idea that a machine stores color as numbers while a human perceives color as an experience. This connects directly to the "How Computer Screens Produce Color" concept above.

**What students do:**
- View a target color square, then adjust the R, G, and B sliders to match it.
- Click **Check Match** to get a score.
- Click **Reveal Answer** to see the color's name and exact RGB values.
- Click **Next Round** to advance through the fixed round set; the end screen reports an average score.

**App structure the agent should know:**
- Targets come from fixed round sets, not random colors. There are **Easy** and **Hard** modes set by a teacher toggle.
- Easy mode uses named canonical targets (Red, Green, Blue, Yellow, Cyan, Magenta, Gray, Orange, Brown, Purple). Hard mode uses muted, less-saturated versions of those families.
- Each round starts with sliders reset to middle values. Students must click **Check Match** before **Next Round** will advance. Switching Easy/Hard restarts the round sequence by design.

### What the score means
The score is a **game metric, not a measure of perception**. It reflects how close the student's RGB settings are to the stored target values. A high score means a close numerical match — but numerical similarity and human perceptual similarity are not always the same thing.

**Agent Notes:**
- Use the score as feedback, not as the teaching point. A student can learn something even from a low-scoring round if they notice how channel changes affect the color.
- When students focus only on beating the score, redirect to the pattern of channel contributions: *"Which channel is contributing most strongly here?"* or *"What happened when you raised green but left red high?"*
- Question: *Why is yellow possible if there is no yellow slider?*
  Answer: The screen combines red and green light, and the visual system interprets that pattern as yellow — no separate yellow source is needed.
- Question: *Does a high score mean my eyes were perfect?*
  Answer: No — it means your RGB settings were numerically close to the stored target.
- Question: *Why is gray (or a muted color) harder than red?*
  Answer: Neutral and muted colors require careful balance across all three channels; saturated colors often just need one channel maxed out.

### Troubleshooting RGB Codebreaker
- If the game won't open, the student likely needs to double-click the correct `.html` file so it opens in their browser (it runs locally from the file — there is no web address to visit). The same applies to the Color Constancy Challenge.
- If a student can't advance, check whether they clicked **Check Match** before **Next Round**.
- Duplicate panels, sliders, or target squares point to an outdated or malformed HTML file, not a color-vision concept problem.
- Washed-out or odd colors usually trace to screen brightness, glare, browser zoom, or a projector — not the game. Different displays can shift color slightly across devices.

## Activity 2: Color Constancy Challenge (Local HTML Game)

The Color Constancy Challenge is the second browser game opened from a local HTML file on the student's own computer (again, no server or internet needed). In it, students judge whether two center patches are **physically the same** color or **physically different** when each is shown in a different surrounding context. It teaches that perceived color depends on context, inferred lighting, and brain-level interpretation — not cone signals alone. This builds on the "Color Constancy and Context" concept above.

**Expected game structure (planned classroom version):**
- Two center patches are shown, one in a left context and one in a right context; students answer **Same** or **Different**, then get correctness feedback.
- A **reveal** step then shows the patches again on a neutral background for direct comparison.
- Easy/Hard modes vary how subtle the context manipulation is. Rounds may be "same but looks different" or "different but looks similar."
- *Note: this reflects the planned version. If the shipped app differs, anchor support in the concept, not memorized interface details.*

### Looks vs. physically the same
The core distinction students must grasp:
- **Looks the same / looks different** are perceptual judgments.
- **Physically the same / different** refers to the actual stored patch values.
- Perception and physical stimulus are related but not always identical — that gap is the whole point of the activity.

**Agent Notes:**
- The **reveal step is the teaching moment** — treat it as more important than the score. The point is not whether the student guessed right, but whether they notice how perception changes when misleading context is removed. After a reveal, ask *"What changed?"* rather than just stating the answer.
- Restate the task plainly when students are confused: *"Are the two center patches physically the same color, yes or no?"*
- Question: *If the patches look different, aren't they different?*
  Answer: Not always — surrounding context can change appearance without changing the actual patch values.
- Question: *If they're physically the same, why did my answer feel wrong?*
  Answer: Your visual system was doing a context-sensitive interpretation that usually helps in real life.
- Question: *So is the brain bad at color? Are illusions just tricks?*
  Answer: No — the brain is solving a useful problem (estimating surface color under uncertain lighting). Illusions reveal that normal computation, they aren't gimmicks.

### Troubleshooting the Color Constancy Challenge
- If students keep answering from appearance alone, introduce the looks-vs-physical vocabulary explicitly.
- If the reveal isn't obvious, have them compare only the center patches and ignore the previous background.
- If a projector washes out the effect, try a laptop screen or dimmer room lighting; strong display color casts also change the strength of the illusion.

## Activity 3: Human Color Discrimination

This activity is a **deployed web app** — the human color discrimination game — that groups of at least three students play in a browser at **https://colorvisionapp.up.railway.app** (it runs on a server, so it needs an internet connection; this is unlike the local HTML games in Activities 1 and 2). Each student wears goggles with a red, green, or blue filter and acts as a proxy for one cone class. Together the group works like a three-channel color detector — the same idea as the robot's three filtered sensors in Activity 4.

The app has two modes, reached from buttons on its start page:
- **TRAIN** — a Color Trainer for practicing before the competition.
- **START** — the timed, scored competition.

### Train mode (Color Trainer)
Students choose a color from a dropdown. A large box shows that color, and below it three boxes — one under an image of each pair of goggles (red, green, and blue) — show how that color looks through each filter. This lets the group learn the bright/dark pattern each color produces across the three channels before they compete.

**Agent Notes:**
- Train mode is the safe place to discover that one channel alone is ambiguous (for example, red and yellow both look bright through the red goggle). Encourage students to use it until they can predict the three-goggle pattern for each color.

### Competition mode (the scored game)
The group is presented with a screen showing **9 colored boxes** (primary and secondary colors), with the **name of the target color shown above them**. The goal is for the group to collectively select **all** boxes of that color, communicating how bright each box looks through their goggles.

**How scoring works:**
- There are **10 rounds**. Each round starts at **100 points** and counts down as an audible clock ticks — the faster the group selects all the correct boxes, the more of the 100 points it keeps.
- Selecting a wrongly colored box costs **10 points** and also speeds the clock up, so mistakes are penalized twice over.
- The round total is multiplied by a **difficulty factor** chosen on the start page: **Easy ×1.0, Medium ×1.5, Hard ×2.0** (harder settings also allow less time per screen).
- At the end, the group enters a **team name** and submits its score. Submitted scores appear on a password-protected **instructor dashboard** (link at the bottom of the start page), which lists each team's score for a chosen date. Teachers who want to use the dashboard in class can email vanderdt@ucmail.uc.edu for access.

Students collaborate by communicating how bright each box looks through their goggles. The table below shows how each color appears through each filter:

**Agent Notes:**
- Question: *Why can't one student identify all colors on their own?*
  Answer: One color channel doesn't contain enough information to distinguish many colors — just like a single cone class can't support full color vision on its own.
- The score is a **game metric, not a measure of perception** — it mainly rewards fast, accurate teamwork across the three goggle "channels." If a group fixates on the score, redirect them to the communication: *"What did the blue-goggle student see that the others couldn't?"*

| Actual Color | Goggles That See This as Bright | Goggles That See This as Dark |
|---|---|---|
| Red | Red | Green, Blue |
| Green | Green | Red, Blue |
| Blue | Blue | Red, Green |
| Yellow | Red, Green | Blue |
| Cyan | Green, Blue | Red |
| Magenta | Red, Blue | Green |

### Troubleshooting the color discrimination game
- The game is a web app, so it needs an internet connection and the correct address (https://colorvisionapp.up.railway.app). If it won't load, check connectivity and the URL — there is no local file to open here (unlike the RGB Codebreaker and Color Constancy games in Activities 1–2).
- If a group can't agree on a box, have each goggle-wearer report only **"bright"** or **"dark"** for that box and match the pattern against the table above.
- If scores seem low, remember the clock: both speed and avoiding wrong clicks matter, since wrong clicks lose points *and* speed the timer up. Suggest starting on **Easy** to build confidence.
- The instructor dashboard is password-protected; teachers who want to use it in class can email vanderdt@ucmail.uc.edu for access.

## Activity 4: Robot Color Discrimination

### What the Robot Is Building
In this activity, students give their robot color vision by equipping it with up to three light sensors, each covered by a color filter. The result is essentially a **1-pixel RGB camera**: just like the human eye compares signals across three cone classes to determine color, the robot compares signals across three filtered sensors.

**Agent Notes:**
- Use the "1-pixel RGB camera" framing to help students connect the human goggle game (Activity 3) to this robot activity. The goggles they wore are the same idea as the color filters on the sensors.
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

## Biology–Engineering Connections

| Biology | The two web games |
|---|---|
| The eye builds color from three cone channels | RGB Codebreaker builds any target color from three output channels (additive mixing) |
| Color is represented in the brain as a pattern of activation, not a single "color signal" | Engineering systems store color numerically (RGB values), not as the experience itself |
| Color constancy: the brain estimates surface color despite changing illumination | The Color Constancy Challenge shows context and inferred lighting changing perceived color |
| Perception sometimes diverges from the physical stimulus | Machine vision also struggles when lighting, shadow, or white balance change |

**Agent Notes:**
- Strong bridge sentence: *"RGB Codebreaker shows how machines build color from channels; the Color Constancy Challenge shows that channel values alone don't determine what we perceive."*
- Keep engineering analogies honest — computer vision and human vision overlap usefully but are not identical (consistent with not overclaiming the robot's capabilities elsewhere in this module).
