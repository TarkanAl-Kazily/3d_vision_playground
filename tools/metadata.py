# Takes an image taken from your phone and saves it to camera_model_overrides.json
# copy this to the data/{dir}/exif/ directory

import PIL.Image
import PIL.ExifTags
from opensfm import exif
from opensfm import dataset
import argparse
import json

"""
FROM: https://github.com/mapillary/OpenSfM/issues/95
You can set the camera parameters (focal, k1 and k2) manually by creating a camera_models_overrides.json 
file on the dataset folder. The simples way is to rename the automatically generated camera_models.json and edit the values.

You can then run bin/clean path_to_dataset to remove the previous results and then bin/run_all path_to_dataset. 
This time, any cameras defined in camera_models_overrides.json will use the parameters defined on that file as a prior.
"""

def extract_exif(image, data):
    # EXIF data in Image
    d = exif.extract_exif_from_file(data.open_image_file(image))

    # Image Height and Image Width
    if d['width'] <= 0 or not data.config['use_exif_size']:
        d['height'], d['width'] = data.image_size(image)

    d['camera'] = exif.camera_id(d)

    return d

if __name__ == "__main__":
    ap = argparse.ArgumentParser('extract metadata')
    ap.add_argument('dataset', help='file where image to calibrate with is stored')
    ap.add_argument('outdir', help='dataset where image sequence is store, i.e. where you do the reconstruction')
    ap.add_argument('--im_name', type=str, default="calibration.jpg", help='name of the image to use for calibration')
    args = ap.parse_args()
    
    data = dataset.DataSet(args.dataset)
    exif_data = extract_exif(args.im_name, data)

    with open(args.outdir+'camera_models.json') as f:
        camera_model = json.load(f)

    keys = []
    [keys.append(key) for key in camera_model.keys()]
    model_name = keys[0]

    outfile = args.outdir+'camera_models_overrides.json'

    output = {exif_data["camera"]: camera_model[model_name]}

    # output[exif_data["camera"]]["width"] = exif_data["width"]
    # output[exif_data["camera"]]["height"] = exif_data["height"]
    output[exif_data["camera"]]["focal"] = exif_data["focal_ratio"]
    # output[exif_data["camera"]]["projection_type"] = exif_data["projection_type"]

    with open(outfile, 'w') as out:
        json.dump(output, out, indent=4)