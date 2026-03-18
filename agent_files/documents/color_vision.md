# Color vision
This document contains information about color vision in humans students in the biology Meets Engineering Program should know to complete activities and to understand how to program a robot with a simple system for discriminating colors.
## Core concepts
### Visible light and color
Visible light is only a narrow part of the electromagnetic spectrum. What we call color depends on the mixture of visible wavelengths reaching the eye or the sensor.

Agent Notes:
+ An object’s color depends on the wavelengths it reflects or emits.
+ Color is not a property of light alone; it is also a property of how a visual system interprets that light.

### Rods and cones in the human eye
The retina contains rod and cone photoreceptor cells. Rods are important for low-light sensitivity and peripheral vision. Cones are used for detail and color vision. 

Humans use three cone classes for color vision.  These cone classes are commonly labeled red, green, and blue because they differ in the wavelengths to which they are most sensitive.

### Color is a pattern across multiple channels

Color vision requires more than sensitivity to certain wavelengths. The brain compares excitation across multiple cone channels and interprets the resulting pattern.

For example, red light stimulates the red-sensitive channel much more than the others, while yellow light stimulates both the red and green channels strongly but the blue channel weakly.

Potential student questions and answers:
+ Question: Why can one student not identify all colors alone?
+ Answer: One color channel does not contain enough information to distinguish many colors
+ Question: Why are secondary colors important?
+ Answer: They make it obvious that different channels must be compared. Yellow, cyan, and magenta each stimulate two channels.

### How computer screens produce of color
A screen can make students perceive yellow even though it is only emitting red and green light. The perceived color depends on the pattern of stimulation across the cone channels, not on the presence of a separate “yellow pixel.”

### Color constancy and context
Perceiving color involves more than comparing signals from the retina. The brain also uses context and estimates of illumination. Because of this, the same surface can appear different under different viewing conditions.

Agent Notes: 
+ Color constancy is the ability to recognize an object as having the same surface color under different lighting conditions.
+ Ambiguous viewing conditions can produce disagreements about color perception, as in famous online image examples.
## Activity 1: human color discrimination
+ In this activity, students play a game in groups of 3. Each student wears goggles with a red, green, or blue filter and acts as a proxy for one cone class.
+ The group are presented with a computer screen on which are shown 9 boxes of different color (primary colors and secondary colors). The name of the target color is shown at the top of the screen. The goal of the game is for the students to collectively select all boxes of the target color.
+ The group must collaborate to decide what color is being viewed. They can do this by communicating to each other how bright each of the boxes look through the 3 different goggles. The table below shows how each color looks through the 3 different goggles. This table, shows, for example, that students can find identify the yellow boxes by noting which boxes look bright to the persons wearing the red and green goggles but dark to the person wearing the blue goggles.
| Actual Color of the Box | Goggles That See This Color as Bright | Goggles That See This Color as Dark |
|-------------------------|---------------------------------------|-------------------------------------|
| Red                     | Red                                   | Green, Blue                          |
| Green                   | Green                                 | Red, Blue                            |
| Blue                    | Blue                                  | Red, Green                           |
| Yellow                  | Red, Green                            | Blue                                 |
| Cyan                    | Green, Blue                           | Red                                  |
| Magenta                 | Red, Blue                             | Green                                |
## Activity 2: robot color discrimination
### General outline of the activity
In this activity, students use the knowledge listed under concepts and the experience from activity 1 to build a robot that can discriminate colors. The basic approach is the following:
+ The robot can be equipped with up to 3 external light detectors. These measure the amount of light that reaches them over a broad spectrum of light.
+ Students are provided with little 3D printed covers which can be placed over the light sensors and into which they can slide reg, green or blue color filters. By placing color filters in front of the sensors, they make them sensitive to a narrow part of the spectrum.
+ By comparing how much light each of the light sensor + color filter receives, the robot can work out the color of the light falling on the sensors:
   - **Red light**: High intensity on the **red-filtered sensor**; low on green and blue.
     - **Green light**: High intensity on the **green-filtered sensor**; low on red and blue.
     - **Blue light**: High intensity on the **blue-filtered sensor**; low on red and green.
     - **Yellow light**: High intensity on **red and green-filtered sensors**; low on blue.
     - **Cyan light**: High intensity on **green and blue-filtered sensors**; low on red.
     - **Magenta light**: High intensity on **red and blue-filtered sensors**; low on green.
     
### Specific goals
Using this approach students could program the robot to complete different challenge. To ensure students are successful at each task they should collect some calbiration data: once they have equipped their robot with the necessary sensors (light sensors with color filters), they should place their robots in the conditions in which they will operate and present them with the different colored LED bars or papers. Systematically moving the robot closer or further away will show them how the values recorded by each color sensor map onto the situations they want to discimininate. This knowlegde can then be used to set thresholds in their programs. 
#### Challenge 1: color mimicking
Students could program the robot to determine the color of an RGB LEDB bar held in front of the robot. Once the robot has determined the color, it could switch on its onboard LEDs to mimic the color. So, if the robot detects yellow light, it could show a yellow color using its LEDs lights.
#### Challenge 2: color approach
Students could place two LED colors bars with different colors in front of the robot. The robot, having essentially one RGB camera pixel, could take two measurements. One after turning slightly left and one after turning slightly right. By comparing the measurements across the three light sensors covered with color filters, the robot could determine whether a preferred color (say green) is at the left or the right.
#### Challenge 3: following a colored trail
For this activity, the students lay down a track of different colored papers. The left of the track has one color and the right side of the track has another color. The robot can be programmed to follow the track by turning left when it detects the right hand color and the other way around.