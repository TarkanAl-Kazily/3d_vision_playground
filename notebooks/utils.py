import cv2
import numpy as np

# For portable filepath operations
import os.path

# For unix style file expansion
import glob

# Workspace constants

# Relative directory for data (containing saved parameters, images, etc)
DATA_DIRECTORY = "../data/"

# Workspace utility functions

def load_image(img_name, grayscale=False):
    """
    Given the name of an image in the data directory, load and return that image.
    Image will have data type char8 ranging from 0 to 255
    """
    flags = cv2.IMREAD_COLOR
    if grayscale:
        flags = cv2.IMREAD_GRAYSCALE
    img_path = os.path.join(DATA_DIRECTORY, img_name)
    return cv2.imread(img_path, flags)

def convert_image_c2f(image):
    """
    Given an image construct and return a corresponding image with float data values between 0 and 1
    """
    new_image = image.astype(np.float32)
    new_image /= 255.0
    return new_image

def convert_image_f2c(image):
    """
    Given an image construct and return a corresponding image with char data values between 0 and 255
    """
    image *= 255.0
    new_image = image.astype(np.uint8)
    image /= 255.0
    return new_image

def glob_data(string):
    """
    Given a glob string, glob the files in the data directory
    """
    path = os.path.join(DATA_DIRECTORY, string)
    return glob.glob(path)

def numpy_save(filename, array):
    """
    Saves array to the given filename in the data directory
    """
    path = os.path.join(DATA_DIRECTORY, filename)
    np.save(path, array)
    
def numpy_load(filename):
    """
    Loads a numpy array from the given filename in the data directory
    """
    path = os.path.join(DATA_DIRECTORY, filename)
    return np.load(path)