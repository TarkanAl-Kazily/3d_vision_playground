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
    w_args.score_thresh = 0.95
    w_args.device = args.device

    wpcs, records = wireframe_run_ply.main(w_args)
    record_dict = {}
    for r in records.values():
        record_dict[r.imnum] = r

    all_images = {}
    # list of (imname, imnum, ply) objects from all wpcs
    all_plys = []
    # dict from (imnum, linenum) -> ply
    plys_by_im_line = {}
    all_initial_lines = {}
    for wpc in wpcs:
        for imnum, imline, ply in wpc.get_plys():
            if all_images.get(imnum, None) is None:
                all_images[imnum] = load_image(os.path.join(args.project_directory, "images", "img_{}.png".format(imnum)))
            plys_by_im_line[(imnum, imline)] = ply
        all_plys += wpc.get_plys()
        all_initial_lines[wpc.imnum] = wpc.initial_lines


    merged = myply.PLY(None, None, None)
    for imname, imline, ply in all_plys:
        merged.combine(ply)

    merged.write(os.path.join(args.project_directory, "merged_wireframe.ply"))
    print("Wrote merged_wireframe.ply...")

    manhattan = myply.PLYEdge(merged)
    manhattan.assert_basis_directions(1000, 0.2)
    manhattan.write(os.path.join(args.project_directory, "manhattan_wireframe.ply"))
    print("Wrote manhattan_wireframe.ply...")

    filtered_by_distance = merged.get_nearby_lines(tol=args.tol, min_group=args.min_group)
    combined = myply.PLY(None, None, None)
    matches = []
    count = 0
    for p in filtered_by_distance:
        print("Combining filtered line {}...".format(count))
        e = myply.PLYEdge(myply.PLY(None, None, None))
        for label in p.edge_labels:
            e.combine(plys_by_im_line[label])

        fname = "complex_{}.ply".format(count)
        e.write(os.path.join(args.project_directory, "wireframe_ply", fname))
        e.combine_edges_with_ransac(20, w_args.l_thresh)
        e.remove_all_vertices()
        combined.combine(e)
        fname = "simplified_{}.ply".format(count)
        count += 1
        print("Showing matches for {}".format(fname))
        e.write(os.path.join(args.project_directory, "wireframe_ply", fname))
        matches.append(Match(e, p.edge_labels))
        if args.plot:
            matches[-1].plot_matches(args.project_directory, all_initial_lines)

    combined.write(os.path.join(args.project_directory, "wireframe_simplified.ply"))

    # Each match stores the edge e and the labels (imnum, imname) for that edge in each image
    # Adjacencies goes from index in matches -> list of groups of matches
    # group matches all correspond to a single intersection point
    adjacencies = {}

    # for ei, m in enumerate(matches):
    #     # Find all other matches incident with this one
    #     adjacencies[ei] = []
    #     for imnum, linenum in m.labels:
    #         g = wireframe.WireframeGraph(record_dict[imnum], threshold=w_args.score_thresh)
    #         intersecting_linenums = g.get_intersecting_lines(linenum)
    #         for group in intersecting_linenums:
    #             group_matches = []
    #             if args.plot:
    #                 g.plot_graph(g.g, all_images[imnum], highlight=[linenum])
    #                 g.plot_graph(g.g, all_images[imnum], highlight=group)
    #             for other_linenum in group:
    #                 label = (imnum, other_linenum)
    #                 for other_ei, other_m in enumerate(matches):
    #                     if (label in other_m.labels):
    #                         group_matches.append(other_ei)
    #             adjacencies[ei].append(group_matches)

    # With adjacencies add a vertex that is the closest intersection point for all the adjacent edges
    # count = 0
    # vertex_plys = []
    # for ei in adjacencies:
    #     groups = adjacencies[ei]
    #     base_match = matches[ei]
    #     for group in groups:
    #         vertex_ply = myply.PLYEdge(base_match.ply)
    #         for other_ei in group:
    #             vertex_ply.combine(matches[other_ei].ply)
    #         intersection_pt = vertex_ply.closest_intersection_pt()
    #         vertex_ply.add_vertices([myply.Vertex(intersection_pt[0], intersection_pt[1], intersection_pt[2])])
    #         vertex_ply.write(os.path.join(args.project_directory, "wireframe_ply", "group_{}.ply".format(count)))
    #         count += 1
    #         vertex_ply.remove_all_edges()
    #         vertex_plys.append(vertex_ply)

    # intersection_pts = myply.PLY(None, None, None)
    # for ply in vertex_plys:
    #     intersection_pts.combine(ply)

    # intersection_pts.write(os.path.join(args.project_directory, "wireframe_ply", "intersection_pts.ply"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('project_directory', type=str, help="directory storing all OpenSfM data")
    parser.add_argument('--tol', type=float, default=0.2, help="Distance tolerance for grouping lines")
    parser.add_argument('--min_group', type=int, default=3, help="Minimum number of distance based matches for inclusion")
    parser.add_argument('--plot', action='store_true', help="Plot matches")
    parser.add_argument('--device', type=str, default='', help="GPU Devices")
    args = parser.parse_args()
    main(args)

