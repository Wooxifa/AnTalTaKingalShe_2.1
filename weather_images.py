"""
Weather image generation module for Telegram Travel Bot.
This module creates weather visualizations using PIL (Pillow).
"""

import io
import datetime
from PIL import Image, ImageDraw, ImageFont

# Weather symbol mapping (using text-based symbols that work well with PIL)
WEATHER_SYMBOLS = {
    'clear': 'SUN',
    'sun': 'SUN',
    'sunny': 'SUN',
    'clear sky': 'SUN',
    'cloud': 'CLOUD',
    'clouds': 'CLOUD',
    'cloudy': 'CLOUD',
    'partly cloudy': 'P.CLOUD',
    'few clouds': 'P.CLOUD',
    'rain': 'RAIN',
    'rainy': 'RAIN',
    'shower': 'RAIN',
    'drizzle': 'DRIZZLE',
    'snow': 'SNOW',
    'snowy': 'SNOW',
    'mist': 'MIST',
    'fog': 'FOG',
    'haze': 'HAZE',
    'thunder': 'STORM',
    'storm': 'STORM',
    'lightning': 'STORM'
}

# Background color mapping for weather conditions
WEATHER_COLORS = {
    'clear': (135, 206, 235),  # Sky blue
    'clouds': (169, 169, 169),  # Light gray
    'rain': (105, 105, 105),  # Dark gray
    'snow': (220, 220, 220),  # Off-white
    'mist': (192, 192, 192),  # Silver
    'thunder': (47, 79, 79)  # Dark slate gray
}


def get_weather_type(description):
    """Determine weather type from description for icon selection."""
    description = description.lower()

    # First check for exact matches
    if description in WEATHER_SYMBOLS:
        return description

    # Then check for partial matches
    for keyword in WEATHER_SYMBOLS:
        if keyword in description:
            return keyword

    return 'clouds'  # Default to clouds if no match


def get_symbol_for_weather(description):
    """Get text symbol for weather description."""
    weather_type = get_weather_type(description)
    return WEATHER_SYMBOLS.get(weather_type, 'CLOUD')


def get_background_color(description):
    """Get background color for weather description."""
    weather_type = get_weather_type(description)

    # Map to main categories
    if 'clear' in weather_type or 'sun' in weather_type:
        category = 'clear'
    elif 'rain' in weather_type or 'shower' in weather_type or 'drizzle' in weather_type:
        category = 'rain'
    elif 'snow' in weather_type:
        category = 'snow'
    elif 'mist' in weather_type or 'fog' in weather_type or 'haze' in weather_type:
        category = 'mist'
    elif 'thunder' in weather_type or 'storm' in weather_type or 'lightning' in weather_type:
        category = 'thunder'
    else:
        category = 'clouds'

    return WEATHER_COLORS.get(category, (169, 169, 169))  # Default to light gray


def draw_sun(draw, x, y, size):
    """Draw a simple sun icon"""
    # Draw circle
    draw.ellipse((x-size, y-size, x+size, y+size), fill=(255, 215, 0), outline=(255, 165, 0))

    # Draw rays
    ray_length = size * 0.6
    positions = [
        (x, y-size*1.5), (x+size*1.1, y-size*1.1),  # top, top-right
        (x+size*1.5, y), (x+size*1.1, y+size*1.1),  # right, bottom-right
        (x, y+size*1.5), (x-size*1.1, y+size*1.1),  # bottom, bottom-left
        (x-size*1.5, y), (x-size*1.1, y-size*1.1)   # left, top-left
    ]

    for px, py in positions:
        draw.line([(x, y), (px, py)], fill=(255, 165, 0), width=3)


def draw_cloud(draw, x, y, size):
    """Draw a simple cloud icon"""
    # Draw multiple overlapping circles to form a cloud
    cloud_color = (240, 240, 240)
    draw.ellipse((x-size, y-size*0.3, x, y+size*0.7), fill=cloud_color)
    draw.ellipse((x-size*0.5, y-size*0.5, x+size*0.5, y+size*0.5), fill=cloud_color)
    draw.ellipse((x-size*0.2, y-size*0.3, x+size*0.8, y+size*0.7), fill=cloud_color)


def draw_partly_cloudy(draw, x, y, size):
    """Draw a sun partially covered by cloud"""
    # Draw sun (smaller and offset)
    sun_x, sun_y = x-size*0.4, y-size*0.3
    sun_size = size * 0.6
    draw_sun(draw, sun_x, sun_y, sun_size)

    # Draw cloud (offset to partially cover sun)
    cloud_x, cloud_y = x+size*0.2, y+size*0.2
    draw_cloud(draw, cloud_x, cloud_y, size)


def draw_rain(draw, x, y, size):
    """Draw a cloud with rain drops"""
    # Draw cloud
    draw_cloud(draw, x, y-size*0.3, size)

    # Draw rain drops
    drop_color = (30, 144, 255)  # Dodger blue
    drops = [(x-size*0.7, y+size*0.5), (x-size*0.3, y+size*0.7),
             (x+size*0.1, y+size*0.6), (x+size*0.5, y+size*0.5)]

    for dx, dy in drops:
        # Draw tear-shaped drops
        draw.line([(dx, dy-size*0.2), (dx, dy+size*0.2)], fill=drop_color, width=3)
        draw.ellipse((dx-size*0.1, dy+size*0.1, dx+size*0.1, dy+size*0.3), fill=drop_color)


def draw_snow(draw, x, y, size):
    """Draw a cloud with snowflakes"""
    # Draw cloud
    draw_cloud(draw, x, y-size*0.3, size)

    # Draw snowflakes
    flake_color = (255, 255, 255)
    flakes = [(x-size*0.7, y+size*0.5), (x-size*0.3, y+size*0.7),
              (x+size*0.1, y+size*0.6), (x+size*0.5, y+size*0.5)]

    for fx, fy in flakes:
        flake_size = size * 0.1
        # Draw a simple snowflake (asterisk)
        draw.line([(fx-flake_size, fy), (fx+flake_size, fy)], fill=flake_color, width=2)
        draw.line([(fx, fy-flake_size), (fx, fy+flake_size)], fill=flake_color, width=2)
        draw.line([(fx-flake_size*0.7, fy-flake_size*0.7), (fx+flake_size*0.7, fy+flake_size*0.7)], fill=flake_color, width=2)
        draw.line([(fx-flake_size*0.7, fy+flake_size*0.7), (fx+flake_size*0.7, fy-flake_size*0.7)], fill=flake_color, width=2)


def draw_fog(draw, x, y, size):
    """Draw fog/mist lines"""
    fog_color = (220, 220, 220)
    line_width = 3
    line_spacing = size * 0.25
    line_lengths = [size*1.6, size*1.2, size*1.8, size*1.0]

    for i in range(4):
        y_pos = y + i * line_spacing - size*0.5
        line_length = line_lengths[i % len(line_lengths)]
        x_start = x - line_length/2
        draw.line([(x_start, y_pos), (x_start + line_length, y_pos)], fill=fog_color, width=line_width)


def draw_storm(draw, x, y, size):
    """Draw a cloud with lightning bolt"""
    # Draw darker cloud
    cloud_color = (100, 100, 100)
    draw.ellipse((x-size, y-size*0.3, x, y+size*0.7), fill=cloud_color)
    draw.ellipse((x-size*0.5, y-size*0.5, x+size*0.5, y+size*0.5), fill=cloud_color)
    draw.ellipse((x-size*0.2, y-size*0.3, x+size*0.8, y+size*0.7), fill=cloud_color)

    # Draw lightning bolt
    bolt_color = (255, 255, 0)  # Yellow
    bolt_points = [
        (x, y+size*0.3),
        (x-size*0.3, y+size*0.8),
        (x-size*0.1, y+size*0.7),
        (x-size*0.4, y+size*1.3)
    ]
    draw.line(bolt_points, fill=bolt_color, width=3)


def draw_weather_icon(draw, weather_type, x, y, size):
    """Draw the appropriate weather icon based on weather type"""
    weather_type = weather_type.lower()

    if 'clear' in weather_type or 'sun' in weather_type:
        draw_sun(draw, x, y, size)
    elif 'partly' in weather_type or 'few' in weather_type:
        draw_partly_cloudy(draw, x, y, size)
    elif 'rain' in weather_type or 'shower' in weather_type or 'drizzle' in weather_type:
        draw_rain(draw, x, y, size)
    elif 'snow' in weather_type:
        draw_snow(draw, x, y, size)
    elif 'mist' in weather_type or 'fog' in weather_type or 'haze' in weather_type:
        draw_fog(draw, x, y, size)
    elif 'thunder' in weather_type or 'storm' in weather_type or 'lightning' in weather_type:
        draw_storm(draw, x, y, size)
    else:
        # Default to cloud
        draw_cloud(draw, x, y, size)


def create_weather_image(location, description, temp, date=None):
    """Create weather visualization using PIL."""
    # Set current date if not provided
    if date is None:
        date = datetime.datetime.now().strftime("%B %d, %Y")

    # Image dimensions
    width, height = 500, 300

    # Get background color based on weather
    bg_color = get_background_color(description)

    # Create a new image with the background color
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # Try to load fonts - use default if not available
    try:
        # For Windows
        title_font = ImageFont.truetype("arial.ttf", 32)
        large_font = ImageFont.truetype("arial.ttf", 48)
        medium_font = ImageFont.truetype("arial.ttf", 24)
        small_font = ImageFont.truetype("arial.ttf", 18)
    except IOError:
        try:
            # For Linux
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            large_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            medium_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except IOError:
            # Fall back to default
            title_font = ImageFont.load_default()
            large_font = ImageFont.load_default()
            medium_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

    # Draw gradient for the upper part of the image
    for y in range(height // 2):
        # Create a gradient effect
        opacity = int(150 - y * 0.6)  # Decreasing opacity as y increases
        if opacity > 0:
            # Draw a semi-transparent line
            color = (255, 255, 255, min(opacity, 255))
            draw.line([(0, y), (width, y)], fill=color)

    # Draw weather icon in the upper part
    icon_x, icon_y = width // 2, height // 4
    icon_size = 50
    draw_weather_icon(draw, description, icon_x, icon_y, icon_size)

    # Draw a white info box at the bottom
    overlay_height = 130
    draw.rectangle([(0, height - overlay_height), (width, height)], fill=(255, 255, 255))

    # Draw location in larger font
    draw.text((20, height - overlay_height + 15), location, font=title_font, fill=(0, 0, 0))

    # Draw description
    draw.text((20, height - overlay_height + 60), description, font=medium_font, fill=(50, 50, 50))

    # Draw temperature in large font
    temp_text = f"{temp}°C"
    # Get text dimensions using the appropriate method
    if hasattr(draw, 'textbbox'):
        # For newer Pillow versions (>=8.0.0)
        bbox = draw.textbbox((0, 0), temp_text, font=large_font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    elif hasattr(draw, 'textsize'):
        # For older Pillow versions (<8.0.0)
        w, h = draw.textsize(temp_text, font=large_font)
    else:
        # Fallback if neither method is available
        w, h = large_font.getsize(temp_text) if hasattr(large_font, 'getsize') else (120, 48)

    draw.text((width - w - 30, height - overlay_height + 30), temp_text, font=large_font, fill=(0, 0, 0))

    # Draw date
    draw.text((20, height - 30), date, font=small_font, fill=(50, 50, 50))

    # Draw "Powered by TravelBot"
    powered_by_text = "Powered by TravelBot"
    if hasattr(draw, 'textbbox'):
        bbox = draw.textbbox((0, 0), powered_by_text, font=small_font)
        w_powered = bbox[2] - bbox[0]
    elif hasattr(draw, 'textsize'):
        w_powered, _ = draw.textsize(powered_by_text, font=small_font)
    else:
        w_powered = small_font.getsize(powered_by_text)[0] if hasattr(small_font, 'getsize') else 150

    draw.text((width - w_powered - 20, height - 30), powered_by_text, font=small_font, fill=(100, 100, 100))

    # Save image to a BytesIO object
    bio = io.BytesIO()
    image.save(bio, 'PNG')
    bio.seek(0)

    return bio