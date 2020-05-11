import argparse
import os

import wireframe_run_ply
import myply

class ArgSet():

    def __init__(self):
        pass

def main(args):

    w_args = ArgSet()
    w_args.project_directory = args.project_directory
    w_args.recompute = False
    w_args.color_inliers = True
    w_args.l_thresh = 0.25
    w_args.reconstruction = 0

    wireframe_run_ply.main(w_args)

    ply_merger = myply.PLYParser(os.path.join(args.project_directory, "wireframe_ply"))
    ply_merger.merge(os.path.join(args.project_directory, "wireframe_merged.ply"))

    ply_loader = myply.PLYLoader()
    merged = ply_loader.load(os.path.join(args.project_directory, "wireframe_merged.ply"))

    filtered_by_distance = merged.get_nearby_lines(tol=args.tol, min_group=args.min_group)
    combined = myply.PLY(None, None)
    for p in filtered_by_distance:
        e = myply.PLYEdge(p)
        e.combine_edges()
        combined.combine(e)

    combined.write(os.path.join(args.project_directory, "wireframe_simplified.ply"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('project_directory', type=str, help="directory storing all OpenSfM data")
    parser.add_argument('--tol', type=float, default=0.2, help="Distance tolerance for grouping lines")
    parser.add_argument('--min_group', type=int, default=3, help="Minimum number of distance based matches for inclusion")
    args = parser.parse_args()
    main(args)

