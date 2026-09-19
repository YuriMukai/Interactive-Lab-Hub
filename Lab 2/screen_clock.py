import time
import os
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont, ImageOps
import adafruit_rgb_display.st7789 as st7789

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.D5) 
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
comic_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22
)
small_comic_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10
)
caption_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14
)
welcome_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
)
clock_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12
)

# The photo is a local stand-in for the picture received through LINE.
script_dir = os.path.dirname(os.path.abspath(__file__))


def load_photo(*filenames):
    for filename in filenames:
        photo_path = os.path.join(script_dir, filename)
        if os.path.exists(photo_path):
            return Image.open(photo_path).convert("RGB")
    return None


dog_photo = load_photo("dog_running.jpeg", "dog.jpg", "dog.jpg.JPG")
dog_food_photo = dog_photo
loaded_food_photo = load_photo("dog_food.jpg", "dog_food.jpg.jpeg")
if loaded_food_photo:
    dog_food_photo = loaded_food_photo
dog_idle_photo = load_photo("dog_idle.jpg")

# The buttons are active-low when using the PiTFT pull-ups.
button_a = digitalio.DigitalInOut(board.D23)
button_b = digitalio.DigitalInOut(board.D24)
button_a.switch_to_input(pull=digitalio.Pull.UP)
button_b.switch_to_input(pull=digitalio.Pull.UP)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

active_event = None
event_started_at = 0.0
event_duration = 5
previous_night_invitation = False
previous_morning_invitation = False


def draw_photo_scene(photo_to_show):
    draw.rectangle((0, 0, width, height), fill=(245, 240, 220))
    caption = "A photo arrived from Japan!"
    caption_box = draw.textbbox((0, 0), caption, font=caption_font)
    caption_x = (width - (caption_box[2] - caption_box[0])) // 2
    draw.text((caption_x, 3), caption, font=caption_font, fill="black")

    photo_area_top = 28
    if photo_to_show:
        photo = photo_to_show.copy()
        photo.thumbnail((width, height - photo_area_top))
        photo_x = (width - photo.width) // 2
        photo_y = photo_area_top + (height - photo_area_top - photo.height) // 2
        image.paste(photo, (photo_x, photo_y))
    else:
        draw.text((width // 2, height // 2), "DOG", font=comic_font, fill="black", anchor="mm")


def draw_comic_scene(event):
    if event == "night":
        draw.rectangle((0, 0, width, height), fill=(15, 35, 75))
        greeting_lines = ("GOOD NIGHT,", "AMERICA!")
        for line_index, line in enumerate(greeting_lines):
            line_box = draw.textbbox((0, 0), line, font=comic_font)
            line_x = (width - (line_box[2] - line_box[0])) // 2
            line_y = 8 + line_index * 25
            draw.text((line_x, line_y), line, font=comic_font, fill="white")
            line_center_y = line_y + (line_box[3] - line_box[1]) // 2
            draw.line(
                (line_x - 3, line_center_y, line_x + line_box[2] - line_box[0] + 3, line_center_y),
                fill="white",
                width=3,
            )
        draw.multiline_text(
            (width // 2, 95),
            "Welcome to the\ncity that never\nsleeps!",
            font=welcome_font,
            fill="white",
            anchor="mm",
            align="center",
            spacing=1,
        )
    else:
        draw.rectangle((0, 0, width, height), fill=(255, 220, 90))
        draw.multiline_text(
            (width // 2, height // 2),
            "GOOD MORNING,\nAMERICA!",
            font=comic_font,
            fill="black",
            anchor="mm",
            align="center",
            spacing=2,
        )


def draw_dog_icon(icon_y, symbol):
    dog_color = "#A1887F"
    draw.ellipse((5, icon_y + 8, 23, icon_y + 22), fill=dog_color)
    draw.ellipse((20, icon_y + 5, 34, icon_y + 18), fill=dog_color)
    draw.polygon(
        [(21, icon_y + 7), (21, icon_y + 1), (27, icon_y + 6)],
        fill=dog_color,
    )
    draw.ellipse((30, icon_y + 10, 32, icon_y + 12), fill="black")
    draw.line((8, icon_y + 21, 8, icon_y + 27), fill=dog_color, width=3)
    draw.line((19, icon_y + 21, 19, icon_y + 27), fill=dog_color, width=3)
    draw.line((5, icon_y + 11, 1, icon_y + 5), fill=dog_color, width=3)

    if symbol == "sun":
        draw.ellipse((34, icon_y + 3, 43, icon_y + 12), fill="#E8A317")
        for ray_start, ray_end in (
            ((38, icon_y + 1), (38, icon_y - 3)),
            ((38, icon_y + 14), (38, icon_y + 18)),
            ((32, icon_y + 7), (28, icon_y + 7)),
            ((44, icon_y + 7), (48, icon_y + 7)),
        ):
            draw.line((ray_start, ray_end), fill="#E8A317", width=2)
    else:
        draw.ellipse((34, icon_y + 2, 45, icon_y + 14), fill="#F4E7B2")
        draw.ellipse((38, icon_y, 47, icon_y + 10), fill=(200, 235, 240))


def draw_clock_scene():
    background_color = (200, 235, 240)
    text_color = "#A1887F"
    content_left = 48
    content_width = width - content_left - 3
    draw.rectangle((0, 0, width, height), fill=background_color)

    draw_dog_icon(3, "sun")
    draw_dog_icon(80, "moon")

    new_york_time = datetime.now(ZoneInfo("America/New_York")).strftime("%H:%M")
    japan_time = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%H:%M")
    for clock_text, clock_y in (
        (f"NY     {new_york_time}", 0),
        (f"Japan  {japan_time}", 17),
    ):
        text_box = draw.textbbox((0, 0), clock_text, font=clock_font)
        text_x = content_left + (content_width - (text_box[2] - text_box[0])) // 2
        draw.text((text_x, clock_y), clock_text, font=clock_font, fill=text_color)

    if dog_idle_photo:
        photo_frame = (content_left, 40, width - 3, height - 2)
        photo = dog_idle_photo.copy()
        photo.thumbnail(
            (content_width, photo_frame[3] - photo_frame[1]),
            Image.Resampling.LANCZOS,
        )
        photo_x = photo_frame[0] + (content_width - photo.width) // 2
        photo_y = photo_frame[1] + (photo_frame[3] - photo_frame[1] - photo.height) // 2
        image.paste(photo, (photo_x, photo_y))


while True:
    night_invitation = button_a.value == False
    morning_invitation = button_b.value == False
    night_pressed = night_invitation and not previous_night_invitation
    morning_pressed = morning_invitation and not previous_morning_invitation

    if night_pressed or morning_pressed:
        # A button press stands in for receiving a LINE photo.
        active_event = "night" if night_pressed else "morning"
        event_started_at = time.monotonic()

    if active_event is not None:
        photo_to_show = dog_photo if active_event == "night" else dog_food_photo
        elapsed = time.monotonic() - event_started_at
        if elapsed >= event_duration:
            active_event = None
            draw_clock_scene()
        elif elapsed < 1:
            draw_photo_scene(photo_to_show)
        else:
            draw_comic_scene(active_event)
    else:
        active_event = None
        draw_clock_scene()

    previous_night_invitation = night_invitation
    previous_morning_invitation = morning_invitation

    # Display image.
    disp.image(image, rotation)
    time.sleep(0.1)
