from matrix_panel import MatrixPanel
from rgbmatrix import graphics
from datetime import datetime, timedelta
import time
import os
from enum import Enum
from scheduler import Scheduler
from schedule import schedule

class EventPhase(Enum):
    START = 1
    MAIN = 2
    END = 3
    OVER = 4

# ── Scrolling digit animation constants ──────────────────────────────────
SCROLL_DURATION_FRAMES = 22        # how many frames the scroll animation lasts (same for both font sizes)
SCROLL_DIGIT_STAGGER_FRAMES = 16    # frame delay between each digit position (right-to-left cascade)
SCROLL_DIGIT_GAP_PX = 2            # pixel gap between outgoing and incoming digit during scroll
SCROLL_EASE_POWER = 2.0            # easing exponent: 1.0 = linear, 2.0 = ease-out quadratic, 3.0 = cubic

def ease_out(t, power=SCROLL_EASE_POWER):
    """Attempt ease-out: fast start, slow finish. t in [0,1] -> [0,1]"""
    return 1.0 - (1.0 - t) ** power

# Digit position definitions: (x, font_key)
# font_key: 'big' for 10x20, 'small' for 5x7
DIGIT_POSITIONS = [
    # index 0: hours tens
    {"x": 5,  "font": "big"},
    # index 1: hours units
    {"x": 15, "font": "big"},
    # index 2: minutes tens
    {"x": 30, "font": "big"},
    # index 3: minutes units
    {"x": 40, "font": "big"},
    # index 4: seconds tens
    {"x": 51, "font": "small"},
    # index 5: seconds units
    {"x": 56, "font": "small"},
]

# Font metrics
FONT_HEIGHT = {"big": 20, "small": 7}
FONT_ASCENT = {"big": 16, "small": 6}
FONT_DESCENT = {"big": 4, "small": 1}
FONT_WIDTH = {"big": 10, "small": 5}

# Mask box overshoot: extra pixels above/below to ensure clean clipping
MASK_OVERSHOOT = 4

# The baseline y for the time display (before vertical_offset)
TIME_BASELINE_Y = 32

# Colon position
COLON_X = 22


class DigitScroller:
    """Tracks per-digit animation state for the scrolling effect.

    Each digit position has three pieces of state:
      - display_char: the character currently shown (the "old" digit during animation)
      - target_char:  the character we're animating towards (None if idle)
      - anim_frame:   current frame of the animation (None if idle)
      - stagger_wait: frames to wait before animation begins
    """

    def __init__(self):
        self.display_char = [None] * 6   # what's currently rendered / the "from" digit
        self.target_char = [None] * 6    # what we're scrolling towards
        self.anim_frame = [None] * 6     # None = idle, 0..N = animating
        self.stagger_wait = [0] * 6

    def update(self, digits):
        """
        digits: list of 6 single-char strings for current HH MM SS.
        Call once per frame.
        """
        # First frame: just adopt the digits, no animation
        if self.display_char[0] is None:
            for i in range(6):
                self.display_char[i] = digits[i]
            return

        # Detect which digits just changed (only if not already animating)
        changed_indices = []
        for i in range(6):
            if self.anim_frame[i] is None and digits[i] != self.display_char[i]:
                changed_indices.append(i)

        # Kick off animations with right-to-left stagger
        if changed_indices:
            max_idx = max(changed_indices)
            for i in changed_indices:
                self.target_char[i] = digits[i]
                self.stagger_wait[i] = (max_idx - i) * SCROLL_DIGIT_STAGGER_FRAMES
                self.anim_frame[i] = 0

        # Advance all active animations
        for i in range(6):
            if self.anim_frame[i] is None:
                continue

            if self.stagger_wait[i] > 0:
                self.stagger_wait[i] -= 1
                continue

            self.anim_frame[i] += 1

            if self.anim_frame[i] >= SCROLL_DURATION_FRAMES:
                # Animation done — adopt the new digit
                self.display_char[i] = self.target_char[i]
                self.target_char[i] = None
                self.anim_frame[i] = None

    def get_draw_info(self, i):
        """
        Returns (old_char, new_char, y_offset) for digit position i.
        - Static digit: (None, char, 0)
        - Waiting for stagger: (None, old_char, 0)  — holds old digit in place
        - Animating: (old_char, new_char, pixel_offset)
        """
        # Not animating — just show current display char
        if self.anim_frame[i] is None:
            return None, self.display_char[i], 0

        # Waiting for stagger to expire — hold old digit
        if self.stagger_wait[i] > 0:
            return None, self.display_char[i], 0

        # Actively animating
        font_key = DIGIT_POSITIONS[i]["font"]
        height = FONT_HEIGHT[font_key]
        total_travel = height + SCROLL_DIGIT_GAP_PX

        t = self.anim_frame[i] / max(SCROLL_DURATION_FRAMES - 1, 1)
        t = min(t, 1.0)
        eased = ease_out(t)
        y_offset = eased * total_travel

        return self.display_char[i], self.target_char[i], y_offset



def draw_scrolling_time(date, offscreen_canvas, bigFont, smallFont, vertical_offset, text_colour_primary, scroller):
    """Draw the time with scrolling digit animation. Returns nothing; draws directly."""
    hour = date.strftime("%H")
    minute = date.strftime("%M")
    second = date.strftime("%S")
    digits = [hour[0], hour[1], minute[0], minute[1], second[0], second[1]]

    scroller.update(digits)

    base_y = TIME_BASELINE_Y + vertical_offset

    # Draw each digit (possibly animating)
    for i in range(6):
        pos = DIGIT_POSITIONS[i]
        x = pos["x"]
        font_key = pos["font"]
        font = bigFont if font_key == "big" else smallFont
        height = FONT_HEIGHT[font_key]

        old_char, new_char, y_off = scroller.get_draw_info(i)

        if old_char is None:
            # Static digit — just draw it
            graphics.DrawText(offscreen_canvas, font, x, base_y, text_colour_primary, new_char)
        else:
            # Animating: draw old digit scrolling up, new digit entering from below
            # old digit y: base_y - y_off (moves upward)
            old_y = base_y - int(round(y_off))
            # new digit y: base_y + (total_travel - y_off) = starts below, ends at base_y
            total_travel = height + SCROLL_DIGIT_GAP_PX
            new_y = base_y + int(round(total_travel - y_off))

            graphics.DrawText(offscreen_canvas, font, x, old_y, text_colour_primary, old_char)
            graphics.DrawText(offscreen_canvas, font, x, new_y, text_colour_primary, new_char)

    # Draw the colon (static, no animation)
    graphics.DrawText(offscreen_canvas, bigFont, COLON_X, base_y, text_colour_primary, ":")

    # ── Per-digit masking boxes ──────────────────────────────────────────
    # Each digit gets its own black rectangles above and below, sized to
    # that digit's font metrics. This ensures the small seconds font gets
    # clipped at its own ascent/descent, not the big font's.
    black = graphics.Color(0, 0, 0)

    for i in range(6):
        pos = DIGIT_POSITIONS[i]
        x = pos["x"]
        font_key = pos["font"]
        ascent = FONT_ASCENT[font_key]
        descent = FONT_DESCENT[font_key]
        width = FONT_WIDTH[font_key]

        # Visible region for this digit
        digit_top = int(base_y) - ascent
        digit_bottom = int(base_y) + descent - 1

        # Top mask: from row 0 down to just above the visible region
        for row in range(0, digit_top):
            graphics.DrawLine(offscreen_canvas, x, row, x + width - 1, row, black)

        # Bottom mask: from just below visible region down far enough to cover scroll travel
        height = FONT_HEIGHT[font_key]
        mask_bottom_extent = digit_bottom + 1 + height + SCROLL_DIGIT_GAP_PX + MASK_OVERSHOOT
        for row in range(digit_bottom + 1, mask_bottom_extent + 1):
            graphics.DrawLine(offscreen_canvas, x, row, x + width - 1, row, black)


class Clock(MatrixPanel):
    def __init__(self, *args, **kwargs):
        super(Clock, self).__init__(*args, **kwargs)
        self.parser.add_argument("--cycle-colours", help="Whether or not to cycle colours automatically", default=False)
        self.parser.add_argument("--brightness", help="The brightness of the text if --cycle-colours is True", default=0.5)     
        self.parser.add_argument("--colour-primary", help="The 1st text colour if --cycle-colours and --enable-arrow-keys are False, formatted as 6-digit hexadecimal string (e.g. '7f1200')", default='7f1200')
        self.parser.add_argument("--colour-secondary", help="The 2nd text colour if --cycle-colours and --enable-arrow-keys are False, formatted as 6-digit hexadecimal string (e.g. '7f4800')", default='7f4800')
        self.parser.add_argument("--scriobh-as-gaeilge", help="Set as true to print date in Irish language", default=True)
        self.parser.add_argument("--use-seconds", help="Set as true to include seconds in the time display", default=True)
        self.parser.add_argument("--time-override", help="Start the clock at a custom time for testing, e.g. '23:59:55'", default=None, type=str)

    def get_formatted_date(self, date, scriobh_as_gaeilge):
        if scriobh_as_gaeilge:
            days = ["Lua", "Mái", "Céa", "Déa", "Aoi", "Sat", "Dom"]
            months = ["Ean", "Fea", "Már", "Aib", "Bea", "Mei", "Iúi", "Lún", "MFó", "DFó", "Sam", "Nol"]
            formatted_date = f"{date.day} {days[date.weekday()]} {months[date.month - 1]}"
        else:
            formatted_date = date.strftime("%d %a %b")
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

        scheduler = Scheduler(schedule)
        scroller = DigitScroller()

        # Compute a fixed offset if --time_override was given
        time_offset = timedelta()
        if self.args.time_override:
            parts = self.args.time_override.split(":")
            override_time = datetime.now().replace(
                hour=int(parts[0]),
                minute=int(parts[1]),
                second=int(parts[2]) if len(parts) > 2 else 0,
                microsecond=0,
            )
            time_offset = override_time - datetime.now()

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
            
            date = datetime.now() + time_offset

            if not currently_in_event:
                event_text = scheduler.getEvent(date)
                if event_text:
                    currently_in_event = True

            if currently_in_event:
                vertical_offset = self.get_vertical_offset(vertical_offset, vertical_animation_speed, event_phase)
                if event_phase == EventPhase.MAIN:
                    scrolling_horizontal_offset = scrolling_horizontal_offset - text_scroll_speed
                event_phase = self.get_event_phase(vertical_offset, max_vertical_offset, event_phase, scrolling_horizontal_offset, event_text_length)
                if event_phase == EventPhase.OVER:
                    scrolling_horizontal_offset = 64
                    currently_in_event = False
                    event_phase = EventPhase.START
            
            date_text = self.get_formatted_date(date, self.args.scriobh_as_gaeilge)
            horizontal_offset = 7
            if date.day < 10:
                horizontal_offset = 9
            
            # ── Draw order: clock digits + masks, then date, then event text ──
            if self.args.use_seconds:
                draw_scrolling_time(date, offscreen_canvas, bigFont, font, vertical_offset, text_colour_primary, scroller)
            else:
                current_time_string = date.strftime("%H:%M")
                graphics.DrawText(offscreen_canvas, bigFont, 7, 32+vertical_offset, text_colour_primary, current_time_string)

            graphics.DrawText(offscreen_canvas, font, horizontal_offset, 47+vertical_offset, text_colour_secondary, date_text)

            # Event scrolling text drawn last so it's not clipped by digit masks
            if currently_in_event and event_phase == EventPhase.MAIN:
                event_text_length = graphics.DrawText(offscreen_canvas, font, scrolling_horizontal_offset, 55, text_colour_primary, event_text)

            time.sleep(0.00000001) # 10ns
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas) 

# Main function
if __name__ == "__main__":
    clock = Clock()
    if (not clock.process()):
        clock.print_help()
