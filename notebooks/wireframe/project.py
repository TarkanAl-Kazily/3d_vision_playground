#
# wireframe_project.py
#
# Utilities for dealing with a project directory
#

import wireframe.wireframe_record
import numpy as np
import os

DIR_IMAGES = "images"
DIR_RECS = "wireframe_recs"

def setup_project_data(proj_dir):
    images = os.listdir(os.path.join(proj_dir, DIR_IMAGES))
    with open(os.path.join(proj_dir, "reconstruction.meshed.json"), 'r') as f:
        reconstruction = json.load(f)
    return images, reconstruction

def save_wireframe_records(proj_dir, w):
    num_images = 0
    for imname in os.listdir(os.path.join(proj_dir, DIR_IMAGES)):
        if imname.endswith(".png") or filename.endswith(".jpg"):
            print("Parsing {}...".format(imname))
            rec = w.parse(os.path.join(proj_dir, DIR_IMAGES, imname))
            rec.save(os.path.join(proj_dir, DIR_RECS, "{}.rec".format(imname)))
            num_images += 1
    print("Saved {} wireframe records.".format(num_images))

def load_wireframe_records(proj_dir):
    records = {}
    for fname in os.listdir(os.path.join(proj_dir, DIR_RECS)):
        if fname.endswith(".npz"):
            print("Loading {}...".format(fname))
            rec = wireframe.WireframeRecord.load(os.path.join(proj_dir, DIR_RECS, fname))
            records[fname[:-8]] = rec
    print("Loaded {} wireframe records.".format(len(records)))
    return records

def generate_wireframe_records(proj_dir, w, force=False):
    records = {}
    for imname in os.listdir(os.path.join(proj_dir, DIR_IMAGES)):
        if imname.endswith(".png") or filename.endswith(".jpg"):
            if force or not os.path.isfile(os.path.join(proj_dir, DIR_RECS, "{}.rec.npz".format(imname))):
                print("Generating rec for {}".format(imname))
                rec = w.parse(os.path.join(proj_dir, DIR_IMAGES, imname))
                rec.save(os.path.join(proj_dir, DIR_RECS, "{}.rec".format(imname)))
                records[imname] = rec
            else:
                print("Loading rec for {}".format(imname))
                rec = wireframe.wireframe_record.WireframeRecord.load(os.path.join(proj_dir, DIR_RECS, "{}.rec.npz".format(imname)))
                records[imname] = rec
    print("Got {} wireframe records".format(len(records)))
    return records
