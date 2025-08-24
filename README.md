# LED-Matrix-Clock
This is an LED project clock I designed and built using a [64x64 Waveshare LED Matrix Board](https://www.waveshare.com/wiki/RGB-Matrix-P2-64x64) and a [Rasberry Pi Zero 2W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/).

![clock_photo_2](https://github.com/user-attachments/assets/1fda8e05-2f49-4832-a840-9ac678925f6e)
Here's a video showing the clock from a few different angles: https://streamable.com/xzsfap

My little smartphone camera doesn't do the LED board justice though - it's a lovely display with no visible flicker, very bright pixels (they're at 50% brightness in the picture and video), great colour saturation, and infinite contrast ratio (much like an OLED screen a black pixel is simply turned off).
The amber and yellow text colours in the pic and video looks lovely and warm in person.

## Notifications

I designed the clock to have a notifiation system with a "slide-up-and-reveal" animation - you can configure a cron-scheduled message to appear based on whatever schedule you please. An example I have included is a Merry Christmas message that appears every hour on the hour on the 25th of December, as well as a daily 7pm and 9pm interesting fact being fetched from an online API:

```
self.schedule = [
    ["0 19,21,14 * * *", get_fact], # At 7 PM (19:00) and 9 PM (21:00) daily
    ["0 * 25 12 *", "Nollaig shona daoibh!"]
]
```

Here is a video showing the notifcation display (plus a fun fact!):
https://streamable.com/2s8azb?src=player-page-share

## The Code

I wrote the clock script in Python. For details on building and running a whole variety of sample programs I'd follow hzeller's wonderful guide: 
https://github.com/hzeller/rpi-rgb-led-matrix

But for this clock project you install the `rgbmatrix` library you should be able to directly execute `main.py`.
You may also wish to do what I did for my clock and have a shell script set up to run the clock program automatically when the Pi boots up.

## The Hardware

### The Clock Frame

The frame I used for the clock is a handmade wooden one (though a 3D print would work well too!) with these dimensions:

![Single pieece measurements](https://github.com/user-attachments/assets/7c90024d-37b1-48ec-9fd2-56598d344bb5)

All of these measurements can be tweaked to your desire and wood at hand (I simply used 12mm x 46mm wood because that's what I picked up from Woodies!)
The only measurement you really need to have down right is the internal measurment of the frame - must be 128mm x 128mm to fit the LED board!

![Full frame measurements](https://github.com/user-attachments/assets/1a2238c4-b12b-450b-a9a1-b11a8034c7db)
Note that the bottom piece has a 30mm diamter hole drilled in it for passing cables inside the frame!

I used pine wood and sloppily applied a dark stain after to give it a rough, aged look.

### LED Board and Pi

Physically the Pi is in a slim case for shielding, which is then attached to the rear of the LED board in the most professional way possible - superglue to attach and hotglue to hold securely in place. To make the clock a little slimmer (I used 46mm depth wooden frame with the led board recessed roughly 3mm, so internal frame depth was fairly limited) I removed the LED board's HUB75 output (not needed for this project) with a pair of pliers and atatched the Pi case directly to the exposed board area. The LED board is held into the frame with screwed in corner brackets.

The ribbon cable that is included with the Waveshare board for connecting the board to a device was far too long so I doubled it over itself and cable tied it in place.
The barrel jack to VH4 adaptor included also had far too much loose cable for this clock frame interior, but a bit of wire splicing sorted that out.

Finally I used hooks and string to make the clock wall mountable.

Here's a rear view of the clock, which is exactly as horrifically messy as any good hobbyist electronic project should be:

![interior_shot](https://github.com/user-attachments/assets/7ae81486-1323-4d8f-8c46-6d386603446a)

Ignore the extra hotglue blobs near the edges, they were from a previous project i did with this board, and i really should have removed them properl

## Potential Improvements

* I would recommend using a different microcomputer if building this yourself - I only used a Pi because I had it lying around but it was total overkill performance-wise (it doesn't take much to run a clock!), and this model not having built in GPIO pins meant I had a lot of soldering to do I would have rather avoided!
* On the topic of power amangement - it mighrt be possible to make this battery powered with a low power microprocessor. Although the Waveshare board is rated for 5v 3A that is at peak (e.g. when showing a full field of white pixels at 100% brigthness) it consumes far less energy in less demanding scenarios. For reference I usually run the clock at 50% brightness - unless it's in direct sunlight this is plenty bright - and most of the pixels are compeltely off all the time.
* I handwired the Pi's GPIO pins to the LED board by hand, and didn't find it too difficult - but there is HUB75 adapter HATs available for Raspberry Pi's and other microcomputers if yu can't or don't want to do this yourself.
* Finally I ended up using two separate cables to powe the LED board and Pi seperately - a micro USB for the Pi and a 5v DC barrel jack for the board. Given that both the Pi and board take 5V DC you could definitely use a single cable - maybe a USB cable in that then splits out inside the frame.

## Future Plans

I intend to develop the clock code further, adding:
* Weather display with custom designed icons.
* Custom fonts for prettier output
