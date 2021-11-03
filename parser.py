import argparse
import os

parser = argparse.ArgumentParser(description='Process VEDAI image labels.')
parser.add_argument('--label_directory', dest='label_directory', type=str, help='directory of file containing vedia labels')
parser.add_argument('--output_location', dest='output_location', type=str, help='sum the integers (default: find the max)')
parser.add_argument('--image_file_suffix', dest='image_file_suffix', type=str, help='suffix of the images for which one is processing the labels ie .jpg')

args = parser.parse_args()

object_map = {1: "Car", 2: "Truck", 23: "Ship", 4: "Tractor", \
5: "Camping Car", 9: "Van", 10: "Vehicle", 11: "Pick-Up", 31: "Plane", \
7: "other", 8: "Other"}

class Image:
    def __init__(self, image_name, image_suffix, object_map, image_size):
        self.image_file_name = image_name+image_suffix
        self.image_name = image_name
        self.image_size = image_size
        
        self.object_labels = []
    
    def save_xml(self, output_directory):
        folder_name = output_directory.split("//")[-1]
        output_string = "<annotation><folder>" + folder_name +\
        "</folder><filename>" + str(self.image_file_name) + "</filename><path>" + os.path.join(output_directory, str(self.image_file_name)) + \
        "</path><source><database>Unknown</database></source><size><width>" + str(self.image_size) + "</width><height>" + \
        str(self.image_size) + "</height><depth>3</depth></size><segmented>0</segmented>"
        for object_label in self.object_labels:
            output_string = output_string + object_label.create_xml_text()
        output_string = output_string + "</annotation>"
        save_name = os.path.join(output_directory, "{}.xml".format(self.image_name))
        text_file = open(save_name, "w")
        _ = text_file.write(output_string)
        text_file.close()
    
    def add_object_label(self, row):
        self.object_labels.append(Object_label(row, object_map))

class Object_label:
    def __init__(self, row, object_map):
        image_id, _, _, _, x_1, x_2, x_3, x_4, y_1, y_2, y_3, y_4, object_id, _, _ = row.split(" ")
        
        self.ymax = max(y_1, y_2, y_3, y_4)
        self.ymin = min(y_1, y_2, y_3, y_4)
        self.xmax = max(x_1, x_2, x_3, x_4)
        self.xmin = min(x_1, x_2, x_3, x_4)
        
        self.object_name = object_map[int(object_id)]
        
    def create_xml_text(self):
        return "<object><name>" + str(self.object_name) + "</name><pose>Unspecified</pose><truncated>0</truncated><difficult>0</difficult>" +\
        "<bndbox><xmin>" + str(self.xmin)  + "</xmin><ymin>" + str(self.ymin) + "</ymin><xmax>" + str(self.xmax) + "</xmax><ymax>" + str(self.ymax) +\
        "</ymax></bndbox></object>"

# run through the items in the VEDAI label file
image_cache = None
for row in open(args.label_directory, "r"):
    image_name = row.split(" ")[0]
    if image_cache==None:
        image_cache = Image(image_name=image_name,\
                            image_suffix=args.image_file_suffix,\
                            object_map=object_map,\
                            image_size=512)
    else:
        if image_cache.image_name!=image_name:
            image_cache = Image(image_name=image_name,\
                                image_suffix=args.image_file_suffix,\
                                object_map=object_map,\
                                image_size=512)
    image_cache.add_object_label(row)
    image_cache.save_xml(args.output_location)