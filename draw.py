# Ce script permet de dessiner des polygones sur une image à partir d'un fichier ALTO.
# L'output est une image avec les polygones dessinés avec une couleur différent pour chaque catégorie de polygonne : default, text, Title, Intext, Commentary, Numbering, SteleArea.
# Ce script a été créee sur mesure pour les fichiers ALTO créés à partir du fichier COCO JSON créé via makesense.ai. 

# Installer : pip install pillow lxml

import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
import random
from lxml import etree

def parse_alto_xml(alto_file):
    tree = etree.parse(alto_file)
    root = tree.getroot()
    
    namespaces = {
        'alto': 'http://www.loc.gov/standards/alto/ns-v3#'
    }
    
    # Parse categories 
    category_colors = {}
    tags = root.find('alto:Tags', namespaces)
    for tag in tags.findall('alto:OtherTag', namespaces):
        category_id = tag.get('ID')
        category_label = tag.get('LABEL')
        # Donner une couleur différente à chaque catégorie
        category_colors[category_id] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # Parse polygons
    polygons = []
    for shape in root.findall('.//alto:Shape', namespaces):
        polygon = shape.find('alto:Polygon', namespaces)
        points = polygon.get('POINTS').split()
        points = [(int(points[i]), int(points[i + 1])) for i in range(0, len(points), 2)]
        parent = shape.getparent()
        while parent is not None and parent.tag != '{http://www.loc.gov/standards/alto/ns-v3#}TextBlock':
            parent = parent.getparent()
        if parent is None:
            continue  
        tagrefs = parent.get('TAGREFS')
        polygons.append((points, category_colors.get(tagrefs, (255, 255, 255))))
    
    return polygons

def draw_polygons(image_file, polygons, output_file, thickness=3):
    # Open an image file
    with Image.open(image_file) as im:
        draw = ImageDraw.Draw(im)
        # Draw each polygon with increased thickness
        for points, color in polygons:
            for i in range(len(points)):
                start_point = points[i]
                end_point = points[(i + 1) % len(points)]
                draw.line([start_point, end_point], fill=color, width=thickness)
        # Save the image with polygons
        im.save(output_file)


alto_file = '00073new.xml'
image_file = '00073.jpg'


output_file = 'output_avec_Polygones.jpg'


polygons = parse_alto_xml(alto_file)

# Call la fonction 
draw_polygons(image_file, polygons, output_file, thickness=5)
