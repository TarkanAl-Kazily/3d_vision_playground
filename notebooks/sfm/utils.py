import sys
sys.path.append('../../OpenSfM')
from opensfm import features
import cv2
import matplotlib.pyplot as plt
import numpy as np

def insert_features(feats, feats_file_path, config):
    """
    Input: 
        feats: Features to add to existing ORB features as a tuple (points, desc, color)
        feats_file_path: where the npz file is stored incl. npz file name
        config: SfM configuration info
    Output:
        saves a new npz file with extra features on it
    """
    fts = features.load_features(feats_file_path, config)

    assert(feats[0].shape[1] == fts[0].shape[1]) # make sure we have the same dimension
    assert(feats[1].shape[1] == fts[1].shape[1]) # make sure we have the same dimension
    assert(feats[2].shape[1] == fts[2].shape[1]) # make sure we have the same dimension

    new_feat_pts = np.vstack((fts[0], feats[0])) # append features together
    new_feat_desc = np.vstack((fts[1], feats[1]))
    new_feat_col = np.vstack((fts[2], feats[2]))

    features.save_features(feats_file_path, new_feat_pts, new_feat_desc, new_feat_col, config) # save features yeaaaaaah boi

def display_features(file_path, filename, config, n_fts):
    """
    Inputs:
        file_path: where the images, features are stored
        config: SfM configuration info
        n_fts: display every n features
    Outputs:
        will display the image along with every n_fts on it
    """
    fts = features.load_features(file_path+"features/"+filename, config)
    points = fts[0]
    img_name = filename[:-13]
    img = cv2.imread(file_path+"images/"+img_name)
    plt.imshow(img)
    denorm_pts = features.denormalized_image_coordinates(points, 1920, 1080)
    for pt_i, (x, y) in enumerate(denorm_pts): 
        if (pt_i % n_fts) == 0:
            plt.scatter(x, y)
    plt.show()