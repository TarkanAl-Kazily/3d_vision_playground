import wireframe
import utils
import argparse
import json
import os

def save_wireframe_records(proj_dir, w):
    num_images = 0
    for imname in os.listdir(os.path.join(proj_dir, "images")):
        if imname.endswith(".png") or filename.endswith(".jpg"):
            print("Parsing {}...".format(imname))
            rec = w.parse(os.path.join(proj_dir, "images", imname))
            rec.save(os.path.join(proj_dir, "wireframe_recs", "{}.rec".format(imname)))
            num_images += 1
    print("Saved {} wireframe records.".format(num_images))

def load_wireframe_records(proj_dir):
    records = {}
    for fname in os.listdir(os.path.join(proj_dir, "wireframe_recs")):
        if fname.endswith(".npz"):
            print("Loading {}...".format(fname))
            rec = wireframe.WireframeRecord.load(os.path.join(proj_dir, "wireframe_recs", fname))
            records[fname[:-8]] = rec
    print("Loaded {} wireframe records.".format(len(records)))
    return records

def main(args):
    # Filepaths
    config_file = utils.data("wireframe.yaml")
    model_file = utils.data("pretrained_lcnn.pth.tar")

    w = wireframe.Wireframe(config_file, model_file, "")
    if not w.setup():
        print(w.error)
    else:
        print("w is setup successfully")

    save_wireframe_records(args.project_directory, w)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('project_directory', type=str, help="directory storing all image data")
    args = parser.parse_args()
    main(args)

