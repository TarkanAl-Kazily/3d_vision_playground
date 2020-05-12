import wireframe
import utils
import argparse
import json
import os

def setup_project_data(proj_dir):
    images = os.listdir(os.path.join(proj_dir, "images"))
    with open(os.path.join(proj_dir, "reconstruction.meshed.json"), 'r') as f:
        reconstruction = json.load(f)
    return images, reconstruction

def main(args):
    try:
        images, reconstruction = setup_project_data(args.project_directory)
    except Exception as e:
        print("An exception occurred while trying to load project data: {}".format(e))
        return

    # Filepaths
    config_file = utils.data("wireframe.yaml")
    model_file = utils.data("pretrained_lcnn.pth.tar")

    w = wireframe.Wireframe(config_file, model_file, args.device)
    if not w.setup():
        print(w.error)
    else:
        print("w is setup successfully")

    records = wireframe.project.generate_wireframe_records(args.project_directory, w, force=args.recompute)

    if args.reconstruction >= 0:
        reconstruction = [reconstruction[args.reconstruction]]

    wpcs = []

    for r in reconstruction:
        for imname, iminfo in r['shots'].items():
            print("Processing {}...".format(imname))
            wpc = wireframe.WireframePointCloud(args.project_directory,
                    imname,
                    records[imname],
                    iminfo,
                    r['cameras'],
                    line_inlier_thresh=args.l_thresh,
                    color_inliers=args.color_inliers,
                    threshold=args.score_thresh)
            wpcs.append(wpc)
            wpc.write_line_point_clouds()

    return wpcs, records


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('project_directory', type=str, help="directory storing all OpenSfM data")
    parser.add_argument('--l_thresh', type=float, default=0.25, help="Threshold value for RANSAC line fitting")
    parser.add_argument('--score_thresh', type=float, default=0.95, help="Score threshold for wireframe detection")
    parser.add_argument('--color_inliers', action="store_true", help="Use a fixed coloring scheme and indicate inliers a different color")
    parser.add_argument('--reconstruction', '-r', type=int, default=-1, help="which reconstruction to generate plys with")
    parser.add_argument('--recompute', action="store_true", help="force recomputing wireframe records")
    parser.add_argument('--device', type=str, default='', help="GPU Devices")
    args = parser.parse_args()
    main(args)

