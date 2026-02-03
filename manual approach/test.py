# create_test_pattern.py
import numpy as np
from PIL import Image, ImageDraw

# Smart object dimensions from your psd-tools output
W, H = 789, 643

# Create test pattern with known points
img = Image.new('RGB', (W, H), 'white')
draw = ImageDraw.Draw(img)

# Draw grid and numbered points
grid_size = 50
points = []

for x in range(0, W, grid_size):
    for y in range(0, H, grid_size):
        # Store point location
        points.append((x, y))
        # Draw cross marker
        draw.line([(x-5, y), (x+5, y)], fill='red', width=2)
        draw.line([(x, y-5), (x, y+5)], fill='red', width=2)
        # Label
        draw.text((x+7, y+7), f"({x},{y})", fill='black')

print(f"Created test pattern with {len(points)} control points")
print(f"Top-left: (0,0), Bottom-right: ({W-1},{H-1})")
img.save('test_pattern.png')