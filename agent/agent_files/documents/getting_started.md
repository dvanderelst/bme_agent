# Getting Started with the Robot

This document covers the very first activity students complete: building, pairing, and programming the robot before any of the biology modules begin. Unlike the other activity documents, this one has no biology component — its goal is simply to get every student to a working, connected robot and to write a few first programs. The animal-behavior modules that follow all build on the skills introduced here: connecting to the robot, the basic program structure, reading sensors, and using variables.

The activity has four steps: (1) build the robot, (2) pair the dongle, (3) start programming in mBlock, and (4) write two simple first programs. It ends with a set of optional challenges that use the robot's sonar and gyroscope.

## Core Concepts

### The Robot and mBlock
The robot is programmed with **mBlock**, a block-based coding tool similar to Scratch — students drag and drop blocks rather than typing code. mBlock runs in a web browser or as an installed app. The robot connects to the computer wirelessly through a small USB **dongle** rather than a cable.

**Agent Notes:**
- **Block-based, no typing**: students snap blocks together. If a student has used Scratch, the interface will feel familiar.
- **Wireless via dongle**: the link between computer and robot is the dongle, not a USB cable to the robot itself. This is a frequent source of confusion — see the pairing section.
- **The robot has several onboard features** used in this activity even before any external sensors are attached: programmable RGB LEDs, a light-intensity sensor, and a 3-axis gyroscope. The **sonar (ultrasonic) distance sensor** used in the challenges is *not* onboard — it is an external sensor plugged into one of the ports (6–10).

### The Basic Program Structure
A central idea introduced here, and reused in every later module, is the standard shape of a robot program:

1. **Initialization** — set things up once at the start.
2. **Main loop** (repeats over and over):
   - **Get data from sensors**
   - **Process the data**
   - **Decide what to do**
   - **Move the robot** (or otherwise act)
3. **Stop / break the loop**

**Agent Notes:**
- **This structure is the backbone of every module** — sense, process, decide, act, repeat. When a student is stuck on a later activity, walking through these stages is a good way to locate where their program is going wrong.
- **The main loop is what makes the robot responsive**: reading the sensor once isn't enough; the robot has to keep sensing and re-deciding inside a loop.

### Variables
A **variable** is a labeled container that stores data (a number, text, etc.) so the program can use it later. The activity introduces variables by having students read the light sensor and store its value in a variable, then make a decision based on that stored value.

**Agent Notes:**
- **Plain framing**: "a variable is a labeled box you put a value in, so you can use that value later." The slides explicitly reassure students this is easier than it sounds.
- **Why it matters here**: storing the sensor reading in a variable is what lets the program compare it (e.g., "is the light value less than 500?") and decide what to do.

---

## Step 1: Building the Robot

Students assemble the robot following the printed build manual. To make building easier, the kit **simplifies the screws**: instead of the three screw types in the original manual, only **two are provided — short screws and long screws** — plus two **screws for the wheels** and a few **nuts**.

**Agent Notes:**
- **Two screw types, not three**: if a student is confused because the manual shows three screw types, explain that the kit deliberately replaces them with just short and long screws (plus the wheel screws and nuts).
- **Follow the manual carefully**: the deck makes a strong recommendation about the build (watch/follow the build guide carefully). A carefully built robot avoids problems later — most "it won't move" issues trace back to a loose connection or a misbuilt step.
- **Don't over-specify build steps you can't see**: point students to the printed manual for the exact mechanical order rather than improvising part-by-part instructions.

---

## Step 2: Pairing the Dongle

To use the robot wirelessly, students pair it with the **dongle** once. (It only needs to be done again if the pair somehow becomes unpaired.)

**Pairing procedure:**
1. **Switch off** the robot.
2. **Plug the dongle** into a USB port on the computer.
3. **Press and hold the button on the dongle** until its LED starts **flashing rapidly**.
4. **Switch on** the robot.
5. **Wait** until the LED on **both** the dongle and the robot stops flashing and stays **solid blue**.

**Agent Notes:**
- **Solid blue on both = paired.** Rapid flashing on the dongle means it's in pairing mode and waiting; slow flashing means it lost the connection.
- **Order matters**: dongle into pairing mode (button held until rapid flash) *before* switching the robot on.
- **One-time step**: pairing persists — students don't redo it every session, only if they unpair.

### Testing the Pairing
Two quick tests confirm the pair is working:

- **Test 1**: With the dongle in the computer, **switch off the robot**. After a few seconds the dongle should start **flashing slowly** (it lost the connection). Switching the robot back on should return the dongle to **solid blue**.
- **Test 2**: With the robot on, **unplug the dongle**. After a few seconds the robot's blue LED should start **flashing** (it lost the connection).

If the dongle reacts to the robot being switched on/off, and the robot reacts to the dongle being unplugged, the pair is good.

**Agent Notes:**
- **Use these tests to diagnose connection problems**: if neither device reacts to the other, they aren't actually paired — redo Step 2.
- **Label the robot and the dongle**: the deck recommends labeling each robot and its matching dongle, so pairs don't get mixed up between students.

---

## Step 3: Start Programming

Once built and paired, students open mBlock, add the robot as a device, and connect.

**The robot's blocks** are organized into categories:
- **Onboard LEDs**
- **Moving / motors**
- **Getting values from sensors**
- **Events** (blocks triggered by something happening)
- **Program flow** (if, repeat, …)
- **Math / comparisons**
- **Variables**

**Agent Notes:**
- **Add the device, then connect**: mBlock has to know which robot it's talking to (add the device) before a connection can be made. If the robot's blocks aren't showing up, the device probably hasn't been added.
- **If "connect" fails**: check that the dongle is plugged in, the robot is switched on, and the pair tested good (Step 2) — the wireless link runs through the dongle.
- **Map block categories to the program structure**: sensor blocks for "get data," math/comparison and variables for "process/decide," moving blocks for "act," and program-flow blocks (if/repeat) to build the main loop.

---

## Step 4: Two Simple First Programs

### Program 1 — Blink the Onboard LEDs
Write a program that **continuously turns the onboard LEDs on for one second, then off for one second**, over and over. The LED color and brightness can be changed in the LED block.

**Agent Notes:**
- **This is the "hello world" of the robot** — it confirms the connection works and introduces a repeating loop.
- **Needs a loop**: "on for a second, off for a second, over and over" means the on/off blocks go inside a repeat/forever loop with one-second waits.

### Program 2 — Blink When It Gets Dark
The robot has an **onboard light-intensity sensor** that returns a value from **0 to 1000** depending on how much light falls on it. Write a program that **briefly blinks the LEDs whenever the light sensor reads less than 500**.

In other words, do this over and over:
1. Read the onboard light sensor and **store the result in a variable**.
2. **If** the light value is less than 500, **blink the LEDs briefly**.

**Agent Notes:**
- **This program introduces variables and an if-decision** — it's the first time students sense → store → decide → act, the full main-loop pattern in miniature.
- **Map it to the program structure**: read sensor (get data) → store in variable (process) → compare to 500 (decide) → blink (act) → repeat (main loop).
- **Testing tip**: cover the sensor with a hand or cup it in shadow to drop the reading below 500 and trigger the blink. If it never blinks, check the threshold comparison and that the variable is being updated inside the loop.

---

## Challenges

These optional challenges extend the first programs using the robot's **sonar (ultrasonic) distance sensor** and **gyroscope**. They preview the sense-process-decide-act pattern that the animal-behavior modules rely on.

### Challenge 1 — Drive and Stop
Drive forward until the **sonar measures a distance smaller than 15 cm**, then **stop**.

### Challenge 2 — Maintain a Fixed Distance
Keep the robot a fixed distance from an obstacle:
- If the obstacle **moves away**, drive **forward** until the distance is **smaller than 20 cm**.
- If the obstacle **moves toward** the robot, drive **backward** until the distance is **larger than 15 cm**.

### Challenge 3 — LED Distance Indicator
Use the LEDs to display the distance measured by the sonar. The number **N** of LEDs turned on is:

```
N = distance / 10
```
- If the distance is **less than 10 cm**, **no** LEDs are on.
- If the distance is **greater than 120 cm**, **all** LEDs are on.

### Challenge 4 — Use the Robot as a Level
The robot has an **onboard 3-axis gyroscope** that measures the robot's tilt around the **X and Y axes** relative to horizontal. Write a program that uses the LEDs to indicate when the robot is **level** (e.g., all LEDs green when level). Optionally, use different colors or numbers of LEDs to show the **direction and amount of tilt** (e.g., more blue LEDs the further it's rotated around the Y axis).

**Agent Notes:**
- **All four follow sense → decide → act**: read sonar/gyroscope, compare to a threshold, then drive or set LEDs. Point students back to the basic program structure when they're stuck.
- **Challenge 2 needs two thresholds (20 cm and 15 cm)**: the gap between them (15–20 cm) is a "do nothing" dead band that keeps the robot from jittering forward and backward. If a student's robot oscillates constantly, this dead band is usually the missing piece.
- **Challenge 3 is integer LED steps**: N = distance/10 means the count jumps by whole LEDs; the <10 cm and >120 cm rules are the floor (0 LEDs) and ceiling (all LEDs).
- **Challenge 4 uses tilt, not distance**: the gyroscope reports angle around X and Y; "level" means both angles are near zero. Encourage students to first just turn LEDs green when level before adding direction-of-tilt color logic.
- **Sonar caveats apply** (from the robot hardware reference): the ultrasonic sensor is most reliable for objects roughly in front of it and within its working range; smooth angled surfaces can reflect sound away and give odd readings.

---

## Common Student Misconceptions

**"The robot connects to the computer with a cable"**
- **Reality**: the connection is wireless, through the USB dongle. The robot is paired to the dongle once in Step 2.
- **Response**: "The dongle is the wireless link. Is it plugged in, is the robot on, and do both show solid blue? That's what 'connected' means here."

**"Both LEDs are solid blue isn't important / any LED state is fine"**
- **Reality**: solid blue on both dongle and robot is the signal that pairing succeeded; flashing means pairing mode or a lost connection.
- **Response**: "Check the LED colors — rapid flash on the dongle is pairing mode, slow flash means it lost the robot, solid blue on both means you're paired."

**"Reading the light sensor once is enough"**
- **Reality**: to keep reacting, the read-and-decide has to be inside the main loop.
- **Response**: "Is your sensor read inside the repeat loop? If it only reads once at the top, the robot won't notice the light changing."

**"There must be three kinds of screws like the manual shows"**
- **Reality**: the kit simplifies this to two screw types (short and long) plus wheel screws and nuts.
- **Response**: "The kit swapped the manual's three screw types for just short and long screws — use those, plus the wheel screws and nuts."

---

## Note on Biology

Unlike the other activity documents, this one has **no biology component** — it exists to get every student to a working, connected robot and comfortable with the basics of mBlock. There is therefore no Biology-Robot Connections table here.

What carries forward into the animal-behavior modules: pairing/connecting the robot, the basic program structure (sense → process → decide → act in a main loop), reading sensors, using variables and if-decisions, and the sonar challenges. In the later modules the robot is programmed to **mimic, approach, avoid, and navigate** like different animals, bringing biology and engineering together.

**Agent Notes:**
- **This is the foundation for every later module** — if a student struggles later with connecting, the program structure, or reading a sensor into a variable, it's worth revisiting the skills from this activity.
- **Point forward**: once a student has a working robot and both first programs running, frame the onboard sensors and the program structure they just learned as the tools the upcoming animal activities will build on.
