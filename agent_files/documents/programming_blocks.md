# Intro
This document provides an overview of the blocks available to students in the mBlock interface.
+ The top-level titles are the block categories as they appear in the mBlock user interface. For example, there are **Action** and a **Control** categories.
+ The second-level titles in this document are the exact names by which each block is listed in the user interface. For example, there is block **move forward at power [] % for [] secs** and a block **Stop Moving**.
+ In the names of blocks, `[slot]` signifies a slot into which other blocks (including variable blocks) can be inserted or values can be entered. The string `[dropdown]` denotes that the slot is a dropdown menu with specific values from which the student can select.
# Action Blocks
## `move forward at power [slot]% for [slot] secs`
- **Description:** Moves the robot forward at a specified power (0-100%) for a set duration (in seconds).
## `move backward at power [slot]% for [slot] secs`
- **Description:** Moves the robot backward at a specified power (0-100%) for a set duration (in seconds).
## `turn left at power [slot]% for [slot] secs`
- **Description:** Turns the robot left at a specified power (0-100%) for a set duration (in seconds).
## `turn right at power [slot]% for [slot] secs`
- **Description:** Turns the robot right at a specified power (0-100%) for a set duration (in seconds).
## `move forward [slot] at power [slot]%`
- **Description:** Moves the robot forward continuously at a specified power (0-100%) until stopped manually or by another block.
- **Agent Notes:**
  - Remind students to use the *"stop moving"* block to halt the robot.
  - Useful for open-ended movement (e.g., until a sensor detects something).

## `left wheel turns at power [slot]%, right wheel at power [slot]%`
- **Description:** Controls each wheel independently with separate power levels (0-100%).
- **Agent Notes:**
  - Great for custom turns or correcting drift.
  - Example: Left wheel at 30%, right wheel at 70% = gentle right curve.

## `stop moving`
- **Description:** Stops all motor movement immediately.
- **Agent Notes:**
  - Essential for ending continuous movement.
  - If a student's robot won't stop, check if this block is missing.

# Show Blocks

## `LED [dropdown] shows color [color] for [slot] secs`
- **Description:** Displays a specified color on all LEDs for a set duration (in seconds).
- **Dropdown Options:** `all`, `left`, `right` - allows targeting specific LEDs
- **Agent Notes:**
  - Use color picker or enter RGB values for custom colors
  - Duration controls how long the color is displayed before turning off
  - **Status Feedback Idea:** Use different colors to indicate program states or steps

## `LED [dropdown] shows color [color]`
- **Description:** Displays a specified color on all LEDs continuously until changed or turned off.
- **Agent Notes:**
  - Remember to use a "turn off LED" block or this will persist
  - Great for status indicators (e.g., red = error, green = ready)
  - **Dropdown Options:** `all`, `left`, `right` - allows targeting specific LEDs
  - **Sensory Feedback Idea:** Use left/right LEDs to indicate:
    - Which sound sensor detected louder noise
    - Which ultrasonic sensor detected an obstacle first
    - Turn direction (left LED for left turns, right LED for right turns)

## `turn on [dropdown] light with color red [slot] green [slot] blue [slot]`
- **Description:** Controls all LEDs using individual RGB values (0-255 for each color channel).
- **Agent Notes:**
  - Standard RGB color model: (255,0,0)=red, (0,255,0)=green, (0,0,255)=blue
  - Example: (128,128,128) creates a medium gray color
  - Values outside 0-255 range will be clamped
  - **Advanced Feedback Idea:** Use RGB gradients to show sensor intensity:
    - Bright red (255,0,0) = object very close
    - Dim red (100,0,0) = object far away
    - Green (0,255,0) = safe distance

## `play note [dropdown] for [slot] beats`
- **Description:** Plays a musical note from the dropdown selection for a specified duration in beats.
- **Agent Notes:**
  - Note dropdown includes standard musical notes (C4, D4, E4, etc.)
  - Beat duration: 1 beat = quarter note, 0.5 beat = eighth note
  - Combine with "wait" blocks for rhythmic patterns
  - **Status Feedback Idea:** Create auditory progress indicators:
    - Low note (C4) = program starting
    - Medium note (G4) = halfway through task
    - High note (C5) = task completed
    - Scale up/down to indicate increasing/decreasing values

## `play sound at frequency of [slot] Hz for [slot] secs`
- **Description:** Plays a tone at a specified frequency (in Hz) for a set duration (in seconds).
- **Agent Notes:**
  - Human hearing range: typically 20-20,000 Hz
  - Common frequencies: 440Hz=A4, 261.63Hz=C4, 523.25Hz=C5
  - Frequencies below 20Hz may not produce audible sound
  - Useful for creating custom sound effects and alarms
  - **Sensory Feedback Ideas:**
    - Continuous tone = system operational
    - Intermittent beeps = waiting for input
    - Fast beeping = error condition
    - Frequency changes = proximity alerts (higher pitch = closer object)
    - Different frequencies for left vs. right sensor triggers

## `turn off LED [dropdown]`
- **Description:** Turns off the specified LED(s).
- **Agent Notes:**
  - Essential for ending persistent LED displays
  - **Dropdown Options:** `all`, `left`, `right` - allows targeting specific LEDs
  - Use after "show color" blocks that don't have automatic timeout
  - **Example:** Create flashing effects by alternating "show color" and "turn off LED" blocks

# Sensing Blocks

## `light sensor [dropdown] light intensity`
- **Description:** Measures the ambient light intensity using a light sensor. The slot in the block is a dropdown menu that can take either take the value `Onboard Sensor` to read out the onboard light sensor or `port3` or `port4` to read out an external light sensor attached to these ports.  
- **Output:** Returns a value where higher numbers = brighter light.
- **Agent Notes:**
  - **Whisker Sensor Compatibility:** The custom whisker sensor uses the same blocks as the light sensor
  - **Whisker Behavior:** Bending the whisker reduces the light sensor value (more bend = lower value)
  - **Port Selection:** Whisker sensors must be connected to port 3 or 4
  - **Example Usage:**
    ```
    if light sensor port3 light intensity < 20 then
      # Whisker is bent - obstacle detected
      turn right at power 50% for 0.5 secs
    ```
  - **Troubleshooting:** If whisker readings seem reversed, check the physical connection and orientation

## `ultrasonic sensor [dropdown] distance`
- **Description:** Measures distance (in cm) to objects using the ultrasonic sensor plugged into one of the ports (1, 2, 3, or 4). The sensor from which the distance is measured is selected by choosing a port from the dropdown menu.
- **Output:** Distance in centimeters (e.g., 10 = 10 cm away).
- **Agent Notes:**
  - If readings seem off, ask:
    - *"Is the sensor facing the object straight-on?"* (Directional!)
    - *"Is the object smooth/angled?"* (May reflect sound away).
  - Tip: Use with *"if distance < 10"* to avoid obstacles.

## `line follower sensor [dropdown] value`
- **Description:** Reads the line sensor’s position. The port to which the sensor is connected should be selected from the dropdown menu (the sensor can be attached to ports 1, 2, 3, or 4).
- **Output:** The way this sensor operates is covered in the document `technological_details_robot.md`

# Light & Sound Blocks (Extension Required)

**Important: These blocks require installing the "Light Sound" extension**

To access these blocks:
1. Click the **+ button** at the bottom of the block category section
2. Select **"Light Sound" extension** from the list
3. A new **"Light Sound" category** will appear with these blocks

## `sound sensor [dropdown] loudness`
- **Description:** Measures sound intensity using the sound sensor plugged into the specified port.
- **Output:** Returns a value where higher numbers = louder sounds.
- **Agent Notes:**
  - **Extension Required:** Students must install the "Light Sound" extension first
  - Sensor has transient response - reacts strongly to sudden sounds then returns to baseline
  - Useful for detecting claps, snaps, or other abrupt noises
  - For continuous sound monitoring, may need to implement averaging
  - **Troubleshooting:** If block is missing, check if extension is installed
  - **Example Usage:**
    ```
    if sound sensor port3 loudness > 50 then
      play note C4 for 0.5 beats
    ```

# Operator Blocks

## `when on-board button [dropdown]?`
- **Description:** Checks the current state of the onboard button and returns true/false.
- **Dropdown Options:** `pressed` or `released`
- **Output:** Returns true if the button matches the selected state, false otherwise.
- **Agent Notes:**
  - Functions as an operator block (hexagonal shape) despite being in Sensing category
  - Use in control blocks for conditional execution
  - **Example 1:** `if when on-board button pressed? then move forward`
  - **Example 2:** `wait until when on-board button released?`
  - **Real-time Check:** Evaluates button state at the moment the block is executed
  - **Common Uses:** Start/stop programs, trigger specific actions, create interactive programs

## `[slot] + [slot]`
- **Description:** Performs addition on two numbers.

## `[slot] - [slot]`
- **Description:** Performs subtraction on two numbers.

## `[slot] + [slot]`
- **Description:** Performs multiplication on two numbers.

## `[slot] / [slot]`
- **Description:** Performs division on two numbers.

## `pick random [slot] to [slot]`
- **Description:** Picks a random number between two values.
- **Use Case:** Random robot behaviors (e.g., *"turn left random 1-3 seconds"*).

## `[slot] > [slot]`
- **Description:** Checks if the first value is greater than the second value.

## `[slot] < [slot]`
- **Description:** Checks if the first value is less than the second value.

## `[slot] = [slot]`
- **Description:** Checks if the first value is equal to the second value.

## `[slot] and [slot]`
- **Description:** Returns true if both conditions are true.

## `[slot] or [slot]`
- **Description:** Returns true if either condition is true.

## `not [slot]`
- **Description:** Reverses a condition.

# Variables in mBlock

## Creating Variables
- **Steps:**
  1. Click *"Make a Variable"* in the Variables menu.
  2. Name the variable (e.g., *"counter"*).
  3. The variable will appear as a block with its name.
  4. Creating at least one variable gives access to the following blocks:

## Variable Blocks

## `set [variable] to [slot]`
- **Description:** Assigns a value to the variable. The slot can be a sensor block to store a sensor's value in a variable. It can also be a combination of operator blocks. 

## `change [variable] by [slot]`
- **Description:** Increments or decrements the variable by a specified amount. The slot is typically filled with a manually typed value.
- **Example:** `change counter by 1`

# Control Blocks

## `when green flag clicked`
- **Description:** The entry point of the program. All actions start here when the green flag is clicked in the mBlock interface.
- **Agent Notes:**
  - If a student says, *"My program doesn’t start!"*, check:
    - Is this block missing?
    - Are other blocks attached to it?
  - **Critical:** Without this block, the program won’t run.
## `wait [slot] seconds`
- **Description:** Pauses the program. Use for timed actions (e.g., *"Wait 1 second before turning"*).

## `forever`
- **Description:** Repeats enclosed blocks indefinitely. Ideal for continuous tasks like sensor monitoring.

## `if [slot] then`
- **Description:** Executes blocks if the condition is true (e.g., *"If distance < 10 cm, stop"*). v

## `if [slot] then else`
- **Description:** Chooses between two actions based on a condition. The slot is typically filled with one or more of the operator blocks and a variable block to create a condition to check.

## `while [slot] repeat`
- **Description:** Repeats while the condition is true. The slot is typically filled with one or more of the operator blocks and a variable block to create a condition to check.

## `repeat until [slot]`
- **Description:** Repeats until the condition becomes true (opposite of *"while"*). The slot is typically filled with one or more of the operator blocks and a variable block to create a condition to check.

## `repeat [slot]`
- **Description:** Repeats blocks a fixed number of times (e.g., *"Repeat 5 times: beep and turn"*).

## `count with [i] from [slot] to [slot] by step [slot] repeat`
- **Description:** Counts from a start to end value, updating a variable.
- **Tip:** Use for numbered sequences (e.g., LED patterns).

## `break`
- **Description:** Exits the current loop immediately.
- **Analogy:** *"Like hitting an emergency stop button."*

## `wait until [slot]`
- **Description:** Pauses until the condition is true (e.g., *"Wait until button clicked"*). The slot is typically filled with one or more of the operator blocks and a variable block to create a condition to check.