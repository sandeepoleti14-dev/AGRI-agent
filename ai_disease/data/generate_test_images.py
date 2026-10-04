"""
Test image generator for paddy disease vision validation.
Creates visual synthetic sample images with specific color distributions,
morphological lesions, and test scenario signatures.
"""

import os
from PIL import Image, ImageDraw, ImageFilter


IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(IMAGES_DIR, exist_ok=True)


def create_healthy_leaf():
    img = Image.new("RGB", (400, 400), color=(34, 139, 34)) # Forest green
    draw = ImageDraw.Draw(img)
    # Draw leaf blade structure
    draw.polygon([(200, 20), (280, 200), (220, 380), (180, 380), (120, 200)], fill=(46, 160, 46), outline=(30, 110, 30))
    # Leaf vein
    draw.line([(200, 30), (200, 370)], fill=(80, 180, 80), width=3)
    path = os.path.join(IMAGES_DIR, "healthy_paddy.jpg")
    img.save(path)
    return path


def create_rice_blast():
    img = Image.new("RGB", (400, 400), color=(50, 140, 50))
    draw = ImageDraw.Draw(img)
    # Leaf blade
    draw.polygon([(200, 20), (280, 200), (220, 380), (180, 380), (120, 200)], fill=(46, 150, 46))
    # Spindle / diamond shaped lesions with gray center and reddish-brown borders
    for y in [100, 180, 260]:
        # outer border
        draw.polygon([(200, y-30), (235, y), (200, y+30), (165, y)], fill=(139, 35, 35))
        # inner grey center
        draw.polygon([(200, y-18), (222, y), (200, y+18), (178, y)], fill=(210, 210, 210))
    path = os.path.join(IMAGES_DIR, "rice_blast.jpg")
    img.save(path)
    return path


def create_sheath_blight():
    img = Image.new("RGB", (400, 400), color=(60, 130, 50))
    draw = ImageDraw.Draw(img)
    # Lower sheath stem near water
    draw.rectangle([140, 40, 260, 380], fill=(70, 140, 60))
    # Water line at bottom
    draw.rectangle([0, 340, 400, 400], fill=(80, 110, 130))
    # Banded, snake-skin-like greenish-gray oval lesions with dark borders
    draw.ellipse([150, 180, 250, 270], fill=(180, 185, 170), outline=(90, 50, 20), width=4)
    draw.ellipse([160, 250, 240, 330], fill=(170, 180, 160), outline=(80, 40, 15), width=4)
    path = os.path.join(IMAGES_DIR, "sheath_blight.jpg")
    img.save(path)
    return path


def create_bacterial_leaf_blight():
    img = Image.new("RGB", (400, 400), color=(40, 120, 40))
    draw = ImageDraw.Draw(img)
    # Leaf blade
    draw.polygon([(200, 20), (300, 200), (240, 380), (160, 380), (100, 200)], fill=(45, 135, 45))
    # Marginal wavy yellow/straw-colored necrosis along leaf edge
    draw.polygon([(200, 20), (300, 200), (280, 230), (250, 180), (220, 100)], fill=(225, 205, 80))
    draw.polygon([(100, 200), (200, 20), (170, 110), (130, 190)], fill=(230, 215, 90))
    # Bleached white areas
    draw.ellipse([240, 150, 270, 190], fill=(245, 245, 220))
    path = os.path.join(IMAGES_DIR, "bacterial_leaf_blight.jpg")
    img.save(path)
    return path


def create_brown_spot():
    img = Image.new("RGB", (400, 400), color=(48, 140, 48))
    draw = ImageDraw.Draw(img)
    # Leaf blade
    draw.polygon([(200, 20), (280, 200), (220, 380), (180, 380), (120, 200)], fill=(46, 145, 46))
    # Small circular sesame-seed-like dark brown spots with yellow halos
    spots = [(170, 110), (220, 140), (190, 180), (210, 230), (180, 270), (200, 320)]
    for sx, sy in spots:
        # Yellow halo
        draw.ellipse([sx-14, sy-14, sx+14, sy+14], fill=(210, 195, 60))
        # Dark brown center
        draw.ellipse([sx-8, sy-8, sx+8, sy+8], fill=(90, 40, 10))
    path = os.path.join(IMAGES_DIR, "brown_spot.jpg")
    img.save(path)
    return path


def create_false_smut():
    img = Image.new("RGB", (400, 400), color=(180, 180, 140))
    draw = ImageDraw.Draw(img)
    # Panicle stalk
    draw.line([(200, 40), (200, 360)], fill=(120, 120, 70), width=4)
    # Velvety orange/green spore balls on grains
    balls = [
        (170, 100, (230, 130, 20)), # Orange ball
        (225, 140, (220, 110, 15)),
        (175, 190, (40, 80, 30)),   # Olive-green ball
        (220, 240, (30, 65, 25)),   # Dark green ball
        (185, 290, (25, 55, 20))
    ]
    for bx, by, col in balls:
        draw.ellipse([bx-25, by-25, bx+25, by+25], fill=col, outline=(20, 40, 15), width=2)
    path = os.path.join(IMAGES_DIR, "false_smut.jpg")
    img.save(path)
    return path


def create_unclear_blur():
    # Extremely blurred image
    img = Image.new("RGB", (400, 400), color=(80, 120, 80))
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 300, 300], fill=(120, 150, 100))
    # Apply severe Gaussian Blur
    for _ in range(5):
        img = img.filter(ImageFilter.GaussianBlur(radius=25))
    path = os.path.join(IMAGES_DIR, "unclear_blur.jpg")
    img.save(path)
    return path


def create_low_quality_dark():
    # Under-exposed / nearly black image
    img = Image.new("RGB", (400, 400), color=(5, 8, 5))
    path = os.path.join(IMAGES_DIR, "low_quality_dark.jpg")
    img.save(path)
    return path


def create_unrelated_car():
    # Non-agricultural object (blue car on gray asphalt)
    img = Image.new("RGB", (400, 400), color=(120, 120, 120))
    draw = ImageDraw.Draw(img)
    # Blue car body
    draw.rectangle([80, 180, 320, 280], fill=(30, 60, 220))
    draw.rectangle([130, 120, 270, 180], fill=(30, 60, 220))
    # Wheels
    draw.ellipse([110, 260, 160, 310], fill=(20, 20, 20))
    draw.ellipse([240, 260, 290, 310], fill=(20, 20, 20))
    path = os.path.join(IMAGES_DIR, "unrelated_car.jpg")
    img.save(path)
    return path


def create_multiple_symptoms():
    # Leaf displaying both spindle spots (blast) and yellow marginal blight (BLB)
    img = Image.new("RGB", (400, 400), color=(40, 120, 40))
    draw = ImageDraw.Draw(img)
    # Leaf
    draw.polygon([(200, 20), (300, 200), (240, 380), (160, 380), (100, 200)], fill=(45, 135, 45))
    # Marginal yellow BLB border
    draw.polygon([(200, 20), (300, 200), (270, 230), (220, 100)], fill=(225, 205, 80))
    # Spindle blast spots in center
    draw.polygon([(200, 150), (225, 175), (200, 200), (175, 175)], fill=(139, 35, 35))
    draw.polygon([(200, 160), (215, 175), (200, 190), (185, 175)], fill=(210, 210, 210))
    path = os.path.join(IMAGES_DIR, "multiple_symptoms.jpg")
    img.save(path)
    return path


def generate_all_images():
    funcs = [
        create_healthy_leaf,
        create_rice_blast,
        create_sheath_blight,
        create_bacterial_leaf_blight,
        create_brown_spot,
        create_false_smut,
        create_unclear_blur,
        create_low_quality_dark,
        create_unrelated_car,
        create_multiple_symptoms
    ]
    for fn in funcs:
        p = fn()
        print(f"Created sample image: {p}")


if __name__ == "__main__":
    generate_all_images()
