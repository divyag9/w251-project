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

def augment(image, img_boxes):
    '''
    Applies the below augmentation.  Returns augmented (image, bounding boxes).
    '''
    return iaa.Sequential([
        # Flip 50% of the time
        iaa.Fliplr(0.5),
        iaa.Flipud(0.5),
        # Change brightness to between 50-150%
        # Apply them per channel 20% of the time (changes the color)
        iaa.Multiply((0.5, 1.5), per_channel=0.2),
        # Strengthen or weaken the contrast in each image.
        iaa.ContrastNormalization((.5, 1.5)),
        # Apply Gaussian blur randomly.
        # Sigma=5 is blurry but definitely still discernable.
        iaa.GaussianBlur(sigma=(0, 5)),
        # Apply Gaussian noise randomly
        # Apply it per channel 20% of the time (changes the color)
        iaa.AdditiveGaussianNoise(scale=(0, 0.1*255), per_channel=0.2),
        # Translate, scale, rotate, and shear randomly.
        # Keep rotate and shear low in training.  They don't play well with bounding boxes.
        # But it should be safe to apply them to test data.
        iaa.Affine(
            translate_percent={"x": (-0.2, 0.2), "y": (-0.2, 0.2)},
            scale=(0.8, 1.0),
            rotate=(-5, 5),
            shear=(-5, 5)
        )
    # Apply augmentations in random order.
    ], random_order=True)(image=image, bounding_boxes=img_boxes)

def fancy_augment(image, img_boxes):
    '''
    Same as augment but applies the fancy one I found at
    https://imgaug.readthedocs.io/en/latest/source/examples_basics.html#heavy-augmentations
    '''
    # Sometimes(0.5, ...) applies the given augmenter in 50% of all cases,
    # e.g. Sometimes(0.5, GaussianBlur(0.3)) would blur roughly every second
    # image.
    sometimes = lambda aug: iaa.Sometimes(0.5, aug)

    return iaa.Sequential(
        [
            #
            # Apply the following augmenters to most images.
            #
            iaa.Fliplr(0.5), # horizontally flip 50% of all images
            iaa.Flipud(0.2), # vertically flip 20% of all images
            # Crop some of the images by 0-10% of their height/width
            sometimes(iaa.Crop(percent=(0, 0.1))),
            # Apply affine transformations to some of the images
            # - scale to 80-120% of image height/width (each axis independently)
            # - translate by -20 to +20 relative to height/width (per axis)
            # - rotate by -5 to +5 degrees
            # - shear by -2 to +2 degrees
            # - order: use nearest neighbour or bilinear interpolation (fast)
            # - mode: use any available mode to fill newly created pixels
            #         see API or scikit-image for which modes are available
            # - cval: if the mode is constant, then use a random brightness
            #         for the newly created pixels (e.g. sometimes black,
            #         sometimes white)
            sometimes(iaa.Affine(
                scale={"x": (0.8, 1.2), "y": (0.8, 1.2)},
                translate_percent={"x": (-0.2, 0.2), "y": (-0.2, 0.2)},
                rotate=(-5, 5),
                shear=(-2, 2),
                order=[0, 1],
                cval=(0, 255),
                mode=ia.ALL
            )),
            # Execute 0 to 5 of the following (less important) augmenters per
            # image. Don't execute all of them, as that would often be way too
            # strong.
            iaa.SomeOf((0, 5),
                [
                    # Convert some images into their superpixel representation,
                    # sample between 20 and 200 superpixels per image, but do
                    # not replace all superpixels with their average, only
                    # some of them (p_replace).
                    sometimes(
                        iaa.Superpixels(
                            p_replace=(0, 1.0),
                            n_segments=(20, 200)
                        )
                    ),
                    # Blur each image with varying strength using
                    # gaussian blur (sigma between 0 and 3.0),
                    # average/uniform blur (kernel size between 2x2 and 7x7)
                    # median blur (kernel size between 3x3 and 11x11).
                    iaa.OneOf([
                        iaa.GaussianBlur((0, 3.0)),
                        iaa.AverageBlur(k=(2, 7)),
                        iaa.MedianBlur(k=(3, 11)),
                    ]),
                    # Sharpen each image, overlay the result with the original
                    # image using an alpha between 0 (no sharpening) and 1
                    # (full sharpening effect).
                    iaa.Sharpen(alpha=(0, 1.0), lightness=(0.75, 1.5)),
                    # Same as sharpen, but for an embossing effect.
                    iaa.Emboss(alpha=(0, 1.0), strength=(0, 2.0)),
                    # Search in some images either for all edges or for
                    # directed edges. These edges are then marked in a black
                    # and white image and overlayed with the original image
                    # using an alpha of 0 to 0.7.
                    sometimes(iaa.OneOf([
                        iaa.EdgeDetect(alpha=(0, 0.7)),
                        iaa.DirectedEdgeDetect(
                            alpha=(0, 0.7), direction=(0.0, 1.0)
                        ),
                    ])),
                    # Add gaussian noise to some images.
                    # In 50% of these cases, the noise is randomly sampled per
                    # channel and pixel.
                    # In the other 50% of all cases it is sampled once per
                    # pixel (i.e. brightness change).
                    iaa.AdditiveGaussianNoise(
                        loc=0, scale=(0.0, 0.05*255), per_channel=0.5
                    ),
                    # Either drop randomly 1 to 10% of all pixels (i.e. set
                    # them to black) or drop them on an image with 2-5% percent
                    # of the original size, leading to large dropped
                    # rectangles.
                    iaa.OneOf([
                        iaa.Dropout((0.01, 0.1), per_channel=0.5),
                        iaa.CoarseDropout(
                            (0.03, 0.15), size_percent=(0.02, 0.05),
                            per_channel=0.2
                        ),
                    ]),
                    # Invert each image's channel with 5% probability.
                    # This sets each pixel value v to 255-v.
                    iaa.Invert(0.05, per_channel=True), # invert color channels
                    # Add a value of -10 to 10 to each pixel.
                    iaa.Add((-10, 10), per_channel=0.5),
                    # Change brightness of images (50-150% of original value).
                    iaa.Multiply((0.5, 1.5), per_channel=0.5),
                    # Improve or worsen the contrast of images.
                    iaa.ContrastNormalization((0.5, 2.0), per_channel=0.5),
                    # Convert each image to grayscale and then overlay the
                    # result with the original with random alpha. I.e. remove
                    # colors with varying strengths.
                    iaa.Grayscale(alpha=(0.0, 1.0)),
                    # In some images move pixels locally around (with random
                    # strengths).
                    sometimes(
                        iaa.ElasticTransformation(alpha=(0.5, 3.5), sigma=0.25)
                    ),
                    # In some images distort local areas with varying strength.
                    sometimes(iaa.PiecewiseAffine(scale=(0.01, 0.05)))
                ],
                # do all of the above augmentations in random order
                random_order=True
            )
        ],
        # do all of the above augmentations in random order
        random_order=True
    )(image=image, bounding_boxes=img_boxes)

def show_annotated_image(
    image_path=None,
    image=None,
    annotation_path=None,
    boxes=None,
    ripe_color=BLUE,
    unripe_color=GREEN):
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
        boxes = BoundingBoxesOnImage(get_bounding_boxes(annotation_path), shape=image.shape)
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

def get_training_annotations(image_path, img_boxes):
    '''
    Generates the line for training example.
    '''
    return ['{},{},{},{},{},{}'.format(
            image_path,
            b.x1_int,
            b.y1_int,
            b.x2_int,
            b.y2_int,
            b.label
        ) for b in img_boxes.bounding_boxes]
