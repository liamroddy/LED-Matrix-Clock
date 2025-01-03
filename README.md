# LED-Matrix-Clock
This is an LED project clock I designed and built using a [64x64 Waveshare LED Matrix Board](https://www.waveshare.com/wiki/RGB-Matrix-P2-64x64) and a [Rasberry Pi Zero 2W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/).

TODO videos and pics

## Notifications

I designed the clock to have a notifiation system - you can configure a cron-scheduled message to appear based on whatever schedule you please. An example I have included is a Merry Christmas message that appears every hour on the hour on the 25th of December, as well as a daily 7pm and 9pm interesting fact being fetched from an online API:

```
self.schedule = [
    ["0 19,21,14 * * *", get_fact], # At 7 PM (19:00) and 9 PM (21:00) daily
    ["0 * 25 12 *", "Nollaig shona daoibh!"]
]
```

## The Clock Frame

The frame I used for the clock is a handmade wooden one (Though a 3D print would work well too!), with these dimensions:

![Single pieece measurements](https://github.com/user-attachments/assets/7c90024d-37b1-48ec-9fd2-56598d344bb5)

All of these measuremnts can be tweaked to your needs and wood at hand (I simply used 12mm x 46mm wood because that's what I picked up from Woodies!)
The only measurement you really need to have down right is the internal measurment of the frame - must be 128mm x 128mm to fit the LED board!

![Full frame measurements](https://github.com/user-attachments/assets/1a2238c4-b12b-450b-a9a1-b11a8034c7db)
Note that the bottom piece has a hole drilled in it for passing cables inside the frame!

## Potential Improvements

* I would recommend using a different microcomputer if building this yourself - I only used a Pi because I had it lying around but it was total overkill performance-wise (it doesn't take much to run a clock!), and this model not having built in GPIO pins meant I had a lot of soldering to do I would have rather avoided!
* On the topic of power amangement - it mighrt be possible to make this battery powered with a low power microprocessor. Although the Waveshare board is rated for 5v 3A that is at peak (e.g. when showing a full field of white pixels at 100% brigthness) it consumes far less energy in less demanding scenarios. For reference I usually run the clock at 50% brightness - unless it's in direct sunlight this is plenty bright - and most of the pixels are compeltely off all the time.
* I handwired the Pi's GPIO pins to the LED board by hand, and didn't find it too difficult - but there is HUB75 adapter HATs available for Raspberry Pi's and other microcomputers if yu can't or don't want to do this yourself.
* Finally I ended up using two separate cables to powe the LED board and Pi seperately - a micro USB for the Pi and a 5v DC barrel jack for the board. Given that both the Pi and board take 5V DC you could definitely use a single cable - maybe a USB cable in that then splits out inside the frame.
