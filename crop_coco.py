import json
from PIL import Image, ImageDraw
import numpy as np

with open('00073new.json') as f:
    coco_data = json.load(f)

image = Image.open('00073.jpg')


intext_polygon = None
for annotation in coco_data['annotations']:
    if annotation['category_id'] == 7:  # Category ID = "Intext"
        intext_polygon = annotation['segmentation'][0]
        break

if intext_polygon is None:
    raise ValueError("No polygon found for the 'Intext' category.")

polygon = [(intext_polygon[i], intext_polygon[i + 1]) for i in range(0, len(intext_polygon), 2)]

# Create a mask
mask = Image.new('L', image.size, 0)
ImageDraw.Draw(mask).polygon(polygon, outline=1, fill=1)
mask = np.array(mask)

# Create a new image 
new_image = Image.new('RGBA', image.size)
new_image.paste(image, (0, 0), mask=Image.fromarray(mask * 255))

# Crop the image to the bounding box of the polygon
bbox = mask.nonzero()
bbox = (min(bbox[1]), min(bbox[0]), max(bbox[1]), max(bbox[0]))
cropped_image = new_image.crop(bbox)


cropped_image.save('cropped_image.png')

