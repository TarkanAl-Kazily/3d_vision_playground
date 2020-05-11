import argparse
import os

import matplotlib.pyplot as plt
import wireframe
import wireframe_run_ply
import myply
import skimage.io

def load_image(imname):
    im = skimage.io.imread(imname)
    if im.ndim == 2:
        im = np.repeat(im[:, :, None], 3, 2)
    im = im[:, :, :3]
    return im

class ArgSet():

    def __init__(self):
        pass

class Match():

    def __init__(self, ply, labels):
        self.ply = ply
        self.labels = labels

    def plot_matches(self, proj_dir, initial_lines, batch=3):
        linenums = [l[1] for l in self.labels]
        imnums = [l[0] for l in self.labels]
        images = ["img_{}.png".format(l[0]) for l in self.labels]
        idx = 0
        while len(images[idx:]) >= batch:
            fig, axes = plt.subplots(1, batch)
            for i in range(batch):
                im = load_image(os.path.join(proj_dir, "images", images[idx + i]))
                axes[i].imshow(im)
                l = initial_lines[imnums[idx + i]][linenums[idx + i]]
                axes[i].plot([l[0, 0], l[1, 0]], [l[0, 1], l[1, 1]], c='r', linewidth=2)
            plt.gca().xaxis.set_major_locator(plt.NullLocator())
            plt.gca().yaxis.set_major_locator(plt.NullLocator())
            plt.show()
            plt.close()
            idx += batch

        if len(images[idx:]) == 0:
            return

        batch = len(images[idx:])
        fig, axes = plt.subplots(1, batch)
        for i in range(batch):
            im = load_image(os.path.join(proj_dir, "images", images[idx + i]))
            l = initial_lines[imnums[idx + i]][linenums[idx + i]]
            if batch == 1:
                axes.imshow(im)
                axes.plot([l[0, 0], l[1, 0]], [l[0, 1], l[1, 1]], c='r', linewidth=2)
            else:
                axes[i].imshow(im)
                axes[i].plot([l[0, 0], l[1, 0]], [l[0, 1], l[1, 1]], c='r', linewidth=2)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.show()
        plt.close()

def main(args):

    w_args = ArgSet()
    w_args.project_directory = args.project_directory
    w_args.recompute = False
    w_args.color_inliers = True
    w_args.l_thresh = 0.25
    w_args.reconstruction = 0

    wpcs = wireframe_run_ply.main(w_args)

    # list of (imname, imline, ply) objects from all wpcs
    all_plys = []
    all_initial_lines = {}
    for wpc in wpcs:
        all_plys += wpc.get_plys()
        all_initial_lines[wpc.imnum] = wpc.initial_lines


    merged = myply.PLY(None, None, None)
    for imname, imline, ply in all_plys:
        merged.combine(ply)

    filtered_by_distance = merged.get_nearby_lines(tol=args.tol, min_group=args.min_group)
    combined = myply.PLY(None, None, None)
    matches = []
    count = 0
    for p in filtered_by_distance:
        e = myply.PLYEdge(p)
        fname = "complex_{}.ply".format(count)
        e.write(os.path.join(args.project_directory, "wireframe_ply", fname))
        e.combine_edges()
        combined.combine(e)
        fname = "simplified_{}.ply".format(count)
        count += 1
        print("Showing matches for {}".format(fname))
        e.write(os.path.join(args.project_directory, "wireframe_ply", fname))
        matches.append(Match(e, p.edge_labels))
        matches[-1].plot_matches(args.project_directory, all_initial_lines)

    combined.write(os.path.join(args.project_directory, "wireframe_simplified.ply"))
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('project_directory', type=str, help="directory storing all OpenSfM data")
    parser.add_argument('--tol', type=float, default=0.2, help="Distance tolerance for grouping lines")
    parser.add_argument('--min_group', type=int, default=3, help="Minimum number of distance based matches for inclusion")
    args = parser.parse_args()
    main(args)

