# Ce Script permet de passer d'un fichier JSON COCO à un fichier XML ALTO. 

# Ce script a été créé sur mesure pour les fichiers json COCO qui sont créés via makesense.ai avec les labels : default, text, Title, Intext, Commentary, Numbering, SteleArea. Il ne marchera pour d'autres fichiers json COCO avec des labels différents. 


import json
import xml.etree.ElementTree as ET

def create_alto(coco_json, output_file):

    with open(coco_json) as f:
        data = json.load(f)
    
    # Root + Description
    root = ET.Element("alto")
    root.set("xmlns", "http://www.loc.gov/standards/alto/ns-v3#")
    root.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xsi:schemaLocation", "http://www.loc.gov/standards/alto/ns-v3# http://www.loc.gov/standards/alto/v3/alto.xsd")
    
    
    description = ET.SubElement(root, "Description")
    ET.SubElement(description, "MeasurementUnit").text = "pixel"
    source_image_information = ET.SubElement(description, "sourceImageInformation")
    file_name = data['images'][0]['file_name']
    ET.SubElement(source_image_information, "fileName").text = file_name
    
    # Tags
    tags = ET.SubElement(root, "Tags")
    category_to_tagref = {category['name']: f"TYPE_{category['id']}" for category in data['categories']}
    for category_name, tag_id in category_to_tagref.items():
        other_tag = ET.SubElement(tags, "OtherTag")
        other_tag.set("ID", tag_id)
        other_tag.set("LABEL", category_name)
    
    # Layout
    layout = ET.SubElement(root, "Layout")
    page = ET.SubElement(layout, "Page")
    page.set("ID", "Page1")
    page.set("PHYSICAL_IMG_NR", "1")
    page.set("HEIGHT", str(data['images'][0]['height']))
    page.set("WIDTH", str(data['images'][0]['width']))
    
    print_space = ET.SubElement(page, "PrintSpace")
    print_space.set("HEIGHT", str(data['images'][0]['height']))
    print_space.set("WIDTH", str(data['images'][0]['width']))
    
    block_counter = 1

    # Helper functions
    def ensure_valid_bbox(bbox):
        return [int(round(x)) if x is not None else 0 for x in bbox]

    def convert_points(points):
        return " ".join([f"{int(round(x))} {int(round(y))}" for x, y in zip(points[::2], points[1::2])])

    def create_text_block(parent, bbox, points, tagref, block_counter):
        text_block = ET.SubElement(parent, "TextBlock")
        text_block.set("ID", f"block_{block_counter}")
        text_block.set("HPOS", str(bbox[0]))
        text_block.set("VPOS", str(bbox[1]))
        text_block.set("WIDTH", str(bbox[2]))
        text_block.set("HEIGHT", str(bbox[3]))
        if tagref:
            text_block.set("TAGREFS", tagref)
        
        shape = ET.SubElement(text_block, "Shape")
        polygon = ET.SubElement(shape, "Polygon")
        polygon.set("POINTS", points)

        return text_block, block_counter + 1

    def create_text_line(parent, bbox, points):
        text_line = ET.SubElement(parent, "TextLine")
        text_line.set("HPOS", str(bbox[0]))
        text_line.set("VPOS", str(bbox[1]))
        text_line.set("WIDTH", str(bbox[2]))
        text_line.set("HEIGHT", str(bbox[3]))

        shape = ET.SubElement(text_line, "Shape")
        polygon = ET.SubElement(shape, "Polygon")
        polygon.set("POINTS", points)

        string = ET.SubElement(text_line, "String")
        string.set("CONTENT", "")
    
    # Créer les éléments XML pour chaque annotation
    for ann in data['annotations']:
        category_name = next(cat['name'] for cat in data['categories'] if cat['id'] == ann['category_id'])
        points = convert_points(ann['segmentation'][0])
        bbox = ensure_valid_bbox(ann['bbox'])

        if category_name == "SteleArea":
            shape = ET.SubElement(print_space, "Shape")
            polygon = ET.SubElement(shape, "Polygon")
            polygon.set("POINTS", points)
            
            for sub_category in ["Numbering", "Commentary", "Title", "Intext"]:
                text_block, block_counter = create_text_block(print_space, bbox, points, category_to_tagref[sub_category], block_counter)
                if sub_category in ["Title", "Intext"]:
                    create_text_line(text_block, bbox, points)
        else:
            text_block, block_counter = create_text_block(print_space, bbox, points, category_to_tagref[category_name], block_counter)
            if category_name in ["Title", "Intext"]:
                create_text_line(text_block, bbox, points)
    
    # Write the XML to file
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="UTF-8", xml_declaration=True)


create_alto("00073new.json", "00073new.xml")
