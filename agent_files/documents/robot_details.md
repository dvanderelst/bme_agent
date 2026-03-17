# mBot Robot Technical Documentation

## Overview

The **mBot by Makeblock** is a 2-wheeled, differentially driven robot programmed using **mBlock**, a Scratch-based drag-and-drop interface. Students can use mBlock [online](https://ide.mblock.cc/) or via installed software.

- **Key Feature:** Designed for beginners; ideal for modeling biological behaviors with sensors
- **Programming Environment:** Visual drag-and-drop interface with optional Python/Arduino code view

## Hardware Specifications

### Ports and Sensors

The mBot has **four ports** (1–4), each with color-coded labels indicating compatible sensors:

| Port | Compatible Labels | Sensors |
| --- | --- | --- |
| 1 | Yellow, Blue, White | Ultrasonic (yellow), Line (blue) |
| 2 | Yellow, Blue, White | Ultrasonic (yellow), Line (blue) |
| 3 | Yellow, Blue, White, Gray | Ultrasonic (yellow), Sound (gray), Light (gray), Whisker (custom, gray) |
| 4 | Yellow, Blue, White, Gray | Ultrasonic (yellow), Sound (gray), Light (gray), Whisker (custom, gray) |

**Troubleshooting Tips:**
- If a sensor isn’t working, check:
  - Is it plugged into a compatible port?
  - Is the cable fully seated?
- **Whisker sensor location:** Ports 3 or 4

### Onboard Sensors and Outputs

Even without external sensors, the mBot has built-in features:

1. **Ambient light sensor** (measures room brightness)
2. **Speaker** (plays tones/melodies)
3. **2 RGB LEDs** (color and brightness can be programmed)
4. **Button** (can trigger programs)

**Analogy for Students:**
- *“The onboard light sensor is like a simple ‘eye’ that detects brightness—no colors, just how much light there is!”*

### Motors and Movement

- **Motor Ports:** M1 (left motor), M2 (right motor)
- **Common Issue:** Robot moves backward/turns the wrong direction

**Motor Cable Troubleshooting:**
1. Turn off the robot and unplug the power
2. Check motor cables:
   - Left motor → **M1**
   - Right motor → **M2**
3. Swap cables if misconnected
4. Reconnect the power and test

**Agent Tip:** If a student says *“My robot spins in circles!”*, suspect **swapped motor cables**.

## Connection and Setup

**Important: Three Essential Steps for mBlock Operation**

Before you can program your mBot in mBlock, **three things must be completed in this exact order**:

1. **Pair the Dongle and Robot** (Hardware Connection) ✅
   - Establishes the wireless link between computer and robot
   - Only needs to be done once per robot/dongle pair

2. **Add the Robot to mBlock** (Software Configuration) ✅  
   - Makes mBlock aware of your specific mBot model
   - Unlocks robot-specific programming blocks

3. **Connect in mBlock** (Session Establishment) ✅
   - Creates an active communication session
   - Must be done each time you start working with the robot

**Troubleshooting Tip:** If your robot isn't responding in mBlock, check these three steps in order. Most connection issues occur because one of these steps was missed or not completed properly.

**Connection Workflow:**
```
Pair Dongle → Add to mBlock → Connect → Ready to Program
```

### Step 1: Pairing the Dongle and Robot

**✅ Step 1 of 3: Establish Hardware Connection**

**Pairing Process (do once per robot):**
1. Unplug the robot from USB (if connected)
2. Turn off the robot
3. Plug the dongle into the computer’s USB port
4. **Press and hold** the dongle button until its LED flashes rapidly
5. Turn on the robot
6. Wait for **solid blue LED** on both dongle and robot

**Testing the Pairing:**
- **Test 1:** Turn robot off → dongle LED should flash slowly (lost connection)
- **Test 2:** Unplug dongle → robot’s blue LED should flash (lost connection)

**Classroom Tips:**
- **Prevent cross-pairing:** Label dongle/robot pairs
- **Prevent accidental unpairing:** Cover dongle button with a label

**✅ Pairing Complete!** Next: [Step 2: Add the Robot to mBlock](#step-2-adding-the-robot-to-mblock)

### Step 2: Adding the Robot to mBlock

**✅ Step 2 of 3: Configure Software**

**Steps to add mBot to mBlock:**
1. Open mBlock and look at the **`Devices` area** (bottom-left corner)
2. If mBot is **not listed**:
   - Click the **`Add (+)` button** in the `Devices` area
   - Select **`mBot`** (not `mBot2`)
   - Click **`OK`**
3. The mBot will now appear in the `Devices` area

**Troubleshooting:**
- *“I don’t see the motor blocks!”* → Ask: *“Did you add the mBot in the Devices area?”*
- Show them where to find the **`Add (+)` button**

**✅ Robot Added!** Next: [Step 3: Connect in mBlock](#step-3-connecting-in-mblock)

### Step 3: Connecting in mBlock

**✅ Step 3 of 3: Establish Communication Session**

**Connection Steps:**
1. Plug the dongle into the computer
2. Turn on the robot
3. In mBlock:
   - Click `Connect` → Select `USB` (even though it uses Bluetooth)
   - Ensure the port is auto-filled (if not, **mLink may not be installed**)
4. Click `Connect`

**Connection Troubleshooting:**
- *“mBlock can’t find the robot”* → Ask:
  *“Is the dongle plugged in? Is the robot on? Did you install mLink?”*

**✅ Connection Complete!** Your robot is now ready for programming.

**Avoid These Common Mistakes:**
- ❌ Skipping pairing and going straight to mBlock connection
- ❌ Forgetting to add the robot to mBlock after pairing  
- ❌ Trying to connect before turning on the robot
- ❌ Using `mBot2` instead of `mBot` in the device selection

## Sensor Technical Specifications

### Light Sensor

- **Type:** Analog (measures overall light intensity)
- **Output:** Higher values = more intense light
- **Limitations:** Does **not** distinguish colors/wavelengths

**Student Questions:**
- *“Why doesn’t the robot see colors?”* → 
  *“This sensor measures brightness, not color—like a light meter, not a camera.”*
- **Color experiments:** Use RGB filters with the light sensor to simulate cone cells

### Sound Sensor

- **Type:** Analog (measures sound intensity)
- **Behavior Characteristics:**
  - **Transient response:** Reacts strongly to sound onset, then returns to baseline (~1 sec)
  - **Frequency response:** Flat in auditory range (~20Hz–20kHz)
  - **Directionality:** Approximately omnidirectional

**Student Questions:**
- *“The sensor stops responding after a second!”* → 
  *“It’s designed to notice new sounds, not constant noise—like how you jump at a sudden clap but ignore background hum.”*
- **Sound localization:** Use two sensors (e.g., “ears”) and compare intensity

### Line Sensor

- **Components:** 2 IR LED/receiver pairs (left and right)
- **Output:** Returns a **number (1–4)** based on surface reflectivity:

| Value | Left Pair | Right Pair | Interpretation | Action for Line-Following |
| --- | --- | --- | --- | --- |
| 1 | Low | Low | Centered on line | Continue straight |
| 2 | High | Low | Veering left | Turn right |
| 3 | Low | High | Veering right | Turn left |
| 4 | High | High | Lost (no line) | Search or stop |

**Line Following Tips:**
- *“Robot keeps turning left?”* → Check if right sensor (Value 3) is over the line
- *“Value 4?”* → Robot lost the line—try slowing down or recalibrating

### Ultrasonic Sensor

- **Output:** Distance in centimeters
- **Technical Characteristics:**
  - **Directional:** Most sensitive to objects straight ahead
  - **Acoustic Mirror Effect:** Smooth, angled surfaces may reflect sound away
  - **Pinging Rhythm:** Sensors ping constantly; software returns most recent measurement

**Troubleshooting:**
- *“Sensor misses obstacles!”* → Ask:
  *“Is the object directly in front? Smooth or angled surfaces can ‘hide’ from sonar.”*
- **Multiple Sensors:** Nearby robots may interfere (same pinging rhythm)
  - **Solution:** Space robots apart or use other sensors (e.g., whiskers)

### Whisker Sensor (Custom)

- **Type:** Analog (uses flex sensors to detect bending/pressure)
- **Behavior:** Mimics mechanosensation (e.g., rodent whiskers or insect antennae)
- **Output:** Higher values = more bending/pressure

**Usage Tips:**
- **Port Assignment:** Attach to ports 3 or 4
- **Analogy:** *“The robot can detect touches—like a rat feeling walls in the dark!”*
- **Troubleshooting:** Ensure whiskers are securely attached and not obstructed