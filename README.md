# LED-Matrix-Clock
This is an LED project clock I designed and built using a 64x64 Waveshare LED Matrix Board and a Rasberry Pi Zero 2W.

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

The frame for the clock is a handmade wooden one, with these dimensions:

TODO

Though a 3D print would work well too!

Here is a link to the 64x64 matrix I used: https://www.waveshare.com/wiki/RGB-Matrix-P2-64x64.

## Potential Improvements

* I would recommend using a different microcomputer if building this yourself - I only used a Pi because I had it lying around but it was total overkill performance-wise (it doesn't take much to run a clock!), and this model not having built in GPIO pins meant I had a lot of soldering to do I would have rather avoided!
* Also I handwired the Pi's GPIO pins to the LED board by hand, and didn't find it too difficult - but there is HUB75 adapter HATs available for Raspberry Pi's and other microcomputers if yu can't or don't want to do this yourself.
* Finally I ended up using two separate cables to powe the LED board and Pi seperately - a micro USB for the Pi and a 5v DC barrel jack for the board. Given that both the Pi and board take 5V DC you could definitely use a single cable - maybe a USB cable in that then splits out inside the frame.
