import imgaug as ia
import imgaug.augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
import cv2
import xml.etree.ElementTree as ET

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def read_image(img_path):
    '''
    Reads from image path and returns it numerically.
    '''
    return cv2.cvtColor(cv2.imread(img_path, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

def write_image(path, img):
    '''
    Writes an image to path.
    '''
    cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

def get_bounding_boxes(annotation_path):
    '''
    Reads from annotation and returns bounding boxes.
    '''
    boxes = []
    for tag in ET.parse(annotation_path).getroot().findall('object'):
        x1, y1, x2, y2 = [int(v.text) for v in tag.find('bndbox')]
        boxes.append(BoundingBox(x1=x1, x2=x2, y1=y1, y2=y2, label=tag.find('name').text))
    return boxes

def show_annotated_image(image_path=None, image=None, annotation_path=None, boxes=None, ripe_color=GREEN, unripe_color=BLUE):
    '''
    Reads from image and annotation paths and returns an annotated image.
    Pass in either the image path or preread image.
    Pass in either the annotation path or precomputed bounding boxes.
    '''
    if image_path:
        image = read_image(image_path)
    elif not image.any():
        raise(ValueError('image_path or image required'))
    
    if annotation_path:
        boxes = get_bounding_boxes(annotation_path)
    elif not boxes:
        raise(ValueError('annotation_path or bounding boxes required.'))
    
    for b in boxes.bounding_boxes:
        image = b.draw_on_image(
            image,
            size=2,
            color=ripe_color if b.label == 'ripe_strawberry' else unripe_color
        )
    print("Ripe RGB: {}, Unripe RGB: {}".format(ripe_color, unripe_color))
    ia.imshow(image)

def get_training_annotation(image_path, img_boxes):
    '''
    Generates the line for training example.
    '''
    return '\n'.join('{},{},{},{},{},{}'.format(
            image_path,
            b.x1_int,
            b.y1_int,
            b.x2_int,
            b.y2_int,
            b.label
        ) for b in img_boxes.bounding_boxes)
