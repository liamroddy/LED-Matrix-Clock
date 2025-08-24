from matrix_panel import MatrixPanel
from rgbmatrix import graphics
from datetime import datetime, timedelta
import time
import os
from enum import Enum
from croniter import croniter
import requests
import json
from focal_an_lae import get_focal_an_lae

def get_fact():
    limit = 1
    api_url = 'https://api.api-ninjas.com/v1/facts'
    api_url = 'https://api.api-ninjas.com/v1/facts'
    api_key = os.getenv("FACTS_API_KEY")
    if not api_key:
        return "FACTS_API_KEY environment variable not set! Get from api-ninjas.com"
    response = requests.get(api_url, headers={'X-Api-Key': api_key})
    if response.status_code == requests.codes.ok:
        return json.loads(response.text)[0].get("fact")
    else:
        return ("Error: " + str(response.status_code) + "; reason: " + str(response.text))
        
class Scheduler():
    def __init__(self):
        self.schedule = [
            ["0 * 28 5 *", "Breithla sona duit, a stór <3 <3 <3"], # 28th May, every hour
            ["0 * 25 12 *", "Nollaig shona daoibh!"], # 25th December, every hour
            ["0/15 * * * *", get_focal_an_lae], # every 15 mins (if above does not takes priority)
            ["16 19 * * *", "Angel numbers! <3"],
            ["02 20 * * *", "Angel numbers! <3"],
        ]

        self.event_run_tracker = [None] * len(self.schedule)

        self.rerun_limit_period = timedelta(hours=1)
        self.grace_period = timedelta(hours=1)

    def __is_time_match(self, cron_expr, current_time, last_time_event_ran):
        cron = croniter(cron_expr, current_time)
        prev_time = cron.get_prev(datetime)
        rerun_limited = False

        event_should_execute = (current_time - prev_time) < self.grace_period

        if last_time_event_ran:
            diff = current_time - last_time_event_ran
            if (diff > timedelta(seconds=0) and diff < self.rerun_limit_period):
                rerun_limited = True

        return (event_should_execute) and (not rerun_limited)

    def getEvent(self, current_time):
        for i in range(len(self.schedule)):
            event = self.schedule[i]
            cron_expr = event[0]
            event_content = event[1]

            last_time_event_ran = self.event_run_tracker[i]

            if self.__is_time_match(cron_expr, current_time, last_time_event_ran):
                self.event_run_tracker[i] = current_time
                event_text = ""
                if callable(event[1]):
                    event_text = event_content()
                if isinstance(event_content, str):
                    event_text = event_content
                return event_text + "    •    " + event_text # repeat text in case start missed by reader         
        return None

class EventPhase(Enum):
    START = 1
    MAIN = 2
    END = 3
    OVER = 4

def draw_with_seconds(date, offscreen_canvas, bigFont, font, vertical_offset, text_colour_primary):
    hour = date.strftime("%H")
    minute = date.strftime("%M")
    second = date.strftime("%S")
    X_START = 5

    TEMP = 7

    graphics.DrawText(offscreen_canvas, bigFont, X_START, 32+vertical_offset, text_colour_primary, hour)
    graphics.DrawText(offscreen_canvas, bigFont, X_START+17, 32+vertical_offset, text_colour_primary, ":")
    graphics.DrawText(offscreen_canvas, bigFont, X_START+25, 32+vertical_offset, text_colour_primary, minute)
    graphics.DrawText(offscreen_canvas, font, X_START+46, 32+vertical_offset, text_colour_primary, second)


class Clock(MatrixPanel):
    def __init__(self, *args, **kwargs):
        super(Clock, self).__init__(*args, **kwargs)
        self.parser.add_argument("--cycle_colours", help="Whether or not to cycle colours automatically", default=False)
        self.parser.add_argument("--brightness", help="The brightness of the text if --cycle-colours is True", default=0.5)     
        self.parser.add_argument("--colour_primary", help="The 1st text colour if --cycle-colours and --enable-arrow-keys are False, formatted as 6-digit hexadecimal string (e.g. '7f1200')", default='7f1200')
        self.parser.add_argument("--colour_secondary", help="The 2nd text colour if --cycle-colours and --enable-arrow-keys are False, formatted as 6-digit hexadecimal string (e.g. '7f4800')", default='7f4800')
        self.parser.add_argument("--scriobh_as_gaeilge", help="Set as true to print date in Irish langauge", default=True)
        self.parser.add_argument("--use_seconds", help="Set as true to include seconds in the time display", default=True)

    def get_formatted_date(self, date, scriobh_as_gaeilge):
        # we should be able to to natively get the date in the OS language,
        # however I have had issues with Irish language support on Raspbian/Debian so this is my workaround
        if scriobh_as_gaeilge:
            days = ["Lua", "Mái", "Céa", "Déa", "Aoi", "Sat", "Dom"]
            months = ["Ean", "Fea", "Már", "Aib", "Bea", "Mei", "Iúi", "Lún", "MFó", "DFó", "Sam", "Nol"]
            formatted_date = f"{days[date.weekday()]} {date.day} {months[date.month - 1]}"
        else:
            formatted_date = date.strftime("%a %d %b")
        return formatted_date
    
    def get_color_from_hue(self, hue):
        h = hue / 60.0
        x = 1 - abs(h % 2 - 1)
        if h < 1:
            r, g, b = 1, x, 0
        elif h < 2:
            r, g, b = x, 1, 0
        elif h < 3:
            r, g, b = 0, 1, x
        elif h < 4:
            r, g, b = 0, x, 1
        elif h < 5:
            r, g, b = x, 0, 1
        else:
            r, g, b = 1, 0, x
        return int(r * 255), int(g * 255), int(b * 255)

    def get_colour_from_hue(self, brightness, hue):
        r, g, b = self.get_color_from_hue(hue)
        r = int(r * brightness)
        g = int(g * brightness)
        b = int(b * brightness)
        return graphics.Color(r, g, b)
    
    def get_vertical_offset(self, vertical_offset, vertical_animation_speed, event_phase):
        if event_phase == EventPhase.START:
            return vertical_offset - vertical_animation_speed
        if event_phase == EventPhase.END:
            return vertical_offset + vertical_animation_speed
        return vertical_offset
    
    def get_event_phase(self, vertical_offset, max_vertical_offset, event_phase, scrolling_horizontal_offset, event_text_length):
        if event_phase == EventPhase.START:
            if vertical_offset <= max_vertical_offset:
                return EventPhase.MAIN
            else:
                return EventPhase.START
        if event_phase == EventPhase.END:
            if vertical_offset >= 0:
                return EventPhase.OVER
            else:
                return EventPhase.END
        if event_phase == EventPhase.MAIN:
            if scrolling_horizontal_offset + event_text_length < 0:
                return EventPhase.END
        return EventPhase.MAIN

    def adjust_colours(self):
        return [self.colour_primary_hue, self.colour_secondary_hue]

    def convert_hex_string_to_colour(self, color_string):
        return graphics.Color(int(color_string[0:2], 16), int(color_string[2:4], 16), int(color_string[4:6], 16))

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()

        fonts_dir = "fonts/"
        font = graphics.Font()
        font.LoadFont(os.path.join(fonts_dir, "5x7.bdf"))
        bigFont = graphics.Font()
        bigFont.LoadFont(os.path.join(fonts_dir, "10x20.bdf"))

        brightness = 0.5    
        total_steps = 255
        colour_step_per_refresh = 0.05
        colour_primary_hue = 0
        colour_secondary_hue = 20

        currently_in_event = False
        event_phase = EventPhase.START
        event_text = ""
        vertical_animation_speed = 0.1
        vertical_offset = 0
        max_vertical_offset = -10

        scrolling_horizontal_offset = 64
        event_text_length = 0
        text_scroll_speed = 0.4

        scheduler = Scheduler()

        if not self.args.cycle_colours and self.args.colour_primary and self.args.colour_secondary:
            text_colour_primary = self.convert_hex_string_to_colour(self.args.colour_primary)
            text_colour_secondary = self.convert_hex_string_to_colour(self.args.colour_secondary)

        while True:
            offscreen_canvas.Clear()

            if self.args.cycle_colours:
                colour_primary_hue = (colour_primary_hue + colour_step_per_refresh) % total_steps
                colour_secondary_hue = (colour_secondary_hue + colour_step_per_refresh) % total_steps
                text_colour_primary = self.get_colour_from_hue(brightness, colour_primary_hue)
                text_colour_secondary = self.get_colour_from_hue(brightness, colour_secondary_hue)            
            
            date = datetime.now()

            if not currently_in_event:
                event_text = scheduler.getEvent(date)
                if event_text:
                    currently_in_event = True

            if currently_in_event:
                vertical_offset = self.get_vertical_offset(vertical_offset, vertical_animation_speed, event_phase)
                if event_phase == EventPhase.MAIN:
                    scrolling_horizontal_offset = scrolling_horizontal_offset - text_scroll_speed
                    event_text_length = graphics.DrawText(offscreen_canvas, font, scrolling_horizontal_offset, 55, text_colour_primary, event_text) 
                event_phase = self.get_event_phase(vertical_offset, max_vertical_offset, event_phase, scrolling_horizontal_offset, event_text_length)
                if event_phase == EventPhase.OVER:
                    scrolling_horizontal_offset = 64
                    currently_in_event = False
                    event_phase = EventPhase.START
            
            date_text = self.get_formatted_date(date, self.args.scriobh_as_gaeilge)
            horizontal_offset = 7
            if date.day < 10:
                horizontal_offset = 9
            
            if self.args.use_seconds:
                draw_with_seconds(date, offscreen_canvas, bigFont, font, vertical_offset, text_colour_primary)
            else:
                current_time_string = date.strftime("%H:%M")
                length = graphics.DrawText(offscreen_canvas, bigFont, 7, 32+vertical_offset, text_colour_primary, current_time_string) # length = 50

            length = graphics.DrawText(offscreen_canvas, font, horizontal_offset, 47+vertical_offset, text_colour_secondary, date_text) # length = 45 when date 1 > 10; 50 for 10+ 

            time.sleep(0.00000001)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)


# Main function
if __name__ == "__main__":
    clock = Clock()
    if (not clock.process()):
        clock.print_help()
