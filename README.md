# Flapulator
 
Meet the Flapulator, the “form over function” calculator. No more do you have to wait in silence as you calculate. Sit back and enjoy the clacks of a mechanical keyboard, as your display gently clicks its way to the next digit. Questionable accuracy, slow calculation speed, but maximum tactile pleasure.

This was a small passion project which I've been working on for a few evenings and weekends over the last month. I found out one of my favourite Mathematicians/Comedians/Pi-Lovers: Matt Parker was going to be doing a show in my hometown, and he is known for his signing of calculators. Upon discovering this at the start of March I then had four weeks to design and build a novel calculator which offered something no calculator has done before, and thus the Flapulator was born.

The concept was to create the most over-engineered calculator which had an analogue feel, but still with a digital brain. After exploring some ideas with flip dots, I eventually settled on split flaps as my display choice. The clack of big wheels of characters turning in airports has always been a sensory pleasure of mine, so I wondered how tough it would be to build a vastly smaller, but fully functional 3D printed version from scratch. Turns out it was fun and also quite a challenge!

To put in some subtle nods towards Matt and his love of Pi, I also hid Pi throughout the design in a number of places: The obvious being a dedicated Pi button which shows both the actual value of Pi and also Matt's most recently calculated approxomation from Pi. The trigonomic functions also only work in radians to keep everything as close to Pi as possible, and finally all of the angles used when designing the shell, lid and body are either some form of Pi or a derrivative of Pi. And the most the obvious is that of course I used a Raspberry Pi Pico microcontroller to handle all the logic.

# Features

* 6 Digit Split Flap Calculator Display (where the decimal point, or negative sign also require 1 digit)
* Automated Calibration and Homing of Servo motors through Hall sensors
* Handwired Mechanical Keyboard with 24 keys (customisable functions can be written into the code)
* Battery Powered (around 4 hours of calculation time on a full charge)
* Raspberry Pi Pico Controlled (with full custom code available to download as part of this project)
* LED Illumination to keep track of current mathematic operation
* Fully asynchronous operation

# Links
[3D Print Files](https://makerworld.com/en/models/2625039-flapulator-the-world-s-most-tactile-calculator#profileId-2897906)

[Instructables Build Walkthrough](https://www.instructables.com/Flapulator-Pi-Centric-Fully-3D-Printable-and-World)

# References
"keypad.py" is my variation (switching row and column orientation/lookup to match my hardware diode layout) derived from the following repository:
https://github.com/PerfecXX/MicroPython-SimpleKeypad
