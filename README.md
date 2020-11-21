# sh1107g
MicroPython driver for the Seeed GROVE OLED display 1.12" v2.2

It is based on the MicroPython `FrameBuffer` class; it also limits the I2C bus usage by updating only the modified parts of the display.

### Usage

Move the `sh1107g.py` file where your project can import it; instantiate the `sh1107g.SH1107G` class providing a `I2C` bus object. Draw using the `FrameBuffer` methods, and remember to call `.update()` or `.update_all()` to update the image on the display.

### Running the example

The `example_main.py` contains a working main file for MicroPython; be sure to properly set the pins for I2C bus; I used a ESP32 board. It shows an animated analogue clock.

![analogue clock](/images/example.jpg)


