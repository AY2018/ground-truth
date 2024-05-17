# Ce script permet de passer d'un fichier ALTO crée par le modèle 47 à un fichier COCO JSON que l'on peut utiliser sur makesense.ai pour corriger les polygones.
# Il ne prend pas en compte les baselines, mais seulement les coordonées des polygones. 

import xml.etree.ElementTree as ET
import json
import os

# Load and parse the XML file
tree = ET.parse('00073.xml')
root = tree.getroot()


ns = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}

# COCO JSON structure
coco_json = {
    "info": {"description": "my-project-name"},
    "images": [],
    "annotations": [],
    "categories": [
        {"id": 1, "name": "default"},
        {"id": 2, "name": "text"},
        {"id": 3, "name": "Title"},
        {"id": 4, "name": "SteleArea"},
        {"id": 5, "name": "Commentary"},
        {"id": 6, "name": "Numbering"},
        {"id": 7, "name": "Intext"}
    ]
}

# Function to extract coordinates from the polygon points
def extract_coordinates(polygon):
    return [float(coord) for point in polygon.split() for coord in point.split(',')]

# ID counters
image_id = 1
annotation_id = 1

# Add image info to COCO JSON
image_info = {
    "id": image_id,
    "width": 3840,
    "height": 4900,
    "file_name": "00073.jpg"
}
coco_json["images"].append(image_info)

# Extract polygons from the XML and add to annotations
for textline in root.findall('.//alto:TextLine', ns):
    for polygon in textline.findall('.//alto:Polygon', ns):
        points = polygon.get('POINTS')
        segmentation = extract_coordinates(points)
        bbox = [
            min(segmentation[::2]),  # min x
            min(segmentation[1::2]),  # min y
            max(segmentation[::2]) - min(segmentation[::2]),  # width
            max(segmentation[1::2]) - min(segmentation[1::2])  # height
        ]
        area = bbox[2] * bbox[3]

        annotation = {
            "id": annotation_id,
            "iscrowd": 0,
            "image_id": image_id,
            "category_id": 2,
            "segmentation": [segmentation],
            "bbox": bbox,
            "area": area
        }

        coco_json["annotations"].append(annotation)
        annotation_id += 1

# Increment the image ID for the next image
image_id += 1

# Save the COCO JSON to a file
with open('coco_format.json', 'w') as json_file:
    json.dump(coco_json, json_file, indent=4)

