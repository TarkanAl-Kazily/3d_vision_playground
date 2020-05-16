import sys
sys.path.append('../../OpenSfM')
from opensfm import features, types
import cv2, json, csv
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.transform import Rotation as R

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

def get_camera_poses(file_path):
    filename = file_path+'undistorted/reconstruction.json'
    camera_poses = {}
    with open(filename) as json_file:
        data = json.load(json_file)
        data = data[0]
        for shot in data['shots'].keys():
            img_data = data['shots'][shot]
            cam_pose = types.Pose(img_data['rotation'], img_data['translation'])
            g = cam_pose.get_Rt()
            camera_poses[shot] = np.vstack((g, np.array([0, 0, 0, 1])))
    return camera_poses

def load_3d_features(file_path):
    """
        Outputs a nested dictionary where the primary keys are each of the images and the secondary keys are 
        for the feature ID's. track ID's and the 3D co-ordinates of each point in space. This allows for correlation
        between each 3D point and it's corresponding point in the image plane.
    """
    tracks_file = file_path+'undistorted/tracks.csv'
    constr_file = file_path+'undistorted/reconstruction.json'

    # Load JSON reconstruction info
    json_data = None
    with open(constr_file) as json_file:
        json_data = json.load(json_file)[0]
    
    # Setup matches dictionary
    matches = {}
    for shot in json_data['shots'].keys():
        matches[shot] = {}
        matches[shot]['feat_ids'] = []
        matches[shot]['coords'] = []
        matches[shot]['track_ids'] = []
    
    # Iterate over tracks to get track_id and feature_id
    with open(tracks_file) as csvfile:
        reader = csv.reader(csvfile, delimiter='\n')
        progress = 0
        no_matches = 0
        for line in reader:
            for item in line:
                entries = item.split()
                if len(entries) > 1: # not using the file header
                    im, track_id, feat_id, x, y, idk, r, g, b = entries
                    try:
                        coords = json_data['points'][track_id]['coordinates']
                        matches[im]['feat_ids'] = np.append(matches[im]['feat_ids'], feat_id)
                        matches[im]['coords'] = np.append(matches[im]['coords'], coords)
                        matches[im]['track_ids'] = np.append(matches[im]['track_ids'], track_id)
                    except:
                        no_matches += 1
                    progress += 1
                    if progress % 100 == 0:
                        print('.', end='')
        print("\n{} matches not found, {} matches found".format(no_matches, progress-no_matches))
    return matches
            