#
# graph.py
#
# Class built on existing graph library for wireframe graph representation.
#

import numpy as np
from igraph import Graph

import matplotlib as mpl
import matplotlib.pyplot as plt
from collections.abc import Iterable

# Plotting settings
PLTOPTS = {"color": "#33FFFF", "s": 15, "edgecolors": "none", "zorder": 5}
cmap = plt.get_cmap("jet")
norm = mpl.colors.Normalize(vmin=0.9, vmax=1.0)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])

def c(x):
    return sm.to_rgba(x)

class WireframeGraph():
    """
    WireframeGraph

    A graph representation to access detected wireframe information

    Attributes:
    rec -- reference to the backing wireframe record
    g -- the igraph Graph object
    disc -- the discretization factor used
    t -- threshold level
    """
    def __init__(self, record, threshold=0.95, name=None):
        """
        Arguments:
        record -- a wireframe record object
        threshold -- score threshold value to add lines to graph (default 0.95)
        name -- (optional) name for graph
        """
        self.rec = record
        self.t = threshold
        self.g = Graph()
        if name:
            self.g["name"] = name

        # disc specifies how many cells to consider vertices in
        self.disc = 100
        self.imshape = self.rec.imshape
        self.imnum = self.rec.imnum

        self.setup_graph()

    def setup_graph(self):
        # Add vertices to g
        nlines, nscores = self.rec.postprocess(self.t)
        all_pts = nlines.reshape((len(nlines) * 2, 2))
        idxs = self.point_to_vertex(all_pts)
        # Map for lookup vertex num -> (x, y)
        idx_list = list(set(idxs))
        # Map for reverse lookup (x, y) -> vertex num
        idx_map = {}
        for i in range(len(idx_list)):
            idx_map[idx_list[i]] = i
        self.g.add_vertices(len(idx_list))
        self.g.vs["idx"] = idx_list

        # Add edges to g
        edges = []
        for l in nlines:
            idxs = self.point_to_vertex(l)
            edges.append((idx_map[idxs[0]], idx_map[idxs[1]]))
        self.g.add_edges(edges)
        self.g.es["score"] = nscores

    def point_to_vertex(self, pts):
        """
        Returns the (i, j) indices that correspond to the discretized location of pt

        Arguments:
        pts -- numpy float array [num_pts, 2] or [2]

        Returns:
        idxs -- list [num_pts] of int tuples [2]
        """
        result = []
        arr = ((pts * self.disc) / self.imshape[:2]).astype(int)
        for i, j in arr:
            result.append((i, j))
        return result

    def vertex_to_point(self, vertices):
        """
        Returns the (x, y) cell coords that correspond to a discretized vertex

        Arguments:
        vertices -- list of tuples [num_pts, 2]

        Returns:
        pts -- numpy float array [num_pts, 2]
        """
        num_pts = len(vertices)
        result = np.zeros((num_pts, 2))
        for i, v in enumerate(vertices):
            result[i] = (np.array(v) * self.imshape[:2]) / self.disc
        return result

    def plot_graph(self, graph, im, highlight=[]):
        print("Plotting graph:\n{}\n".format(graph))
        plt.gca().set_axis_off()
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.margins(0, 0)
        for i, edge in enumerate(graph.es):
            s = graph.es["score"][edge.index]
            vs = [graph.vs["idx"][edge.source], graph.vs["idx"][edge.target]]
            pts = self.vertex_to_point(vs)
            plt.plot([pts[0, 1], pts[1, 1]], [pts[0, 0], pts[1, 0]], c='b' if i in highlight else 'r', linewidth=2)
            plt.scatter(pts[0, 1], pts[0, 0], **PLTOPTS)
            plt.scatter(pts[1, 1], pts[1, 0], **PLTOPTS)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.imshow(im)
        plt.show()
        plt.close()

    def connected_subgraphs(self):
        return self.g.components().subgraphs()

    def get_intersecting_lines(self, linenum, close=0.05):
        edge = self.g.es[linenum]
        line = np.array([self.g.vs["idx"][edge.source], self.g.vs["idx"][edge.target]])
        result = []
        points = []
        for i, l in enumerate(self.g.es):
            if i == linenum:
                continue
            other_line = np.array([self.g.vs["idx"][l.source], self.g.vs["idx"][l.target]])
            intersect, p = intersect_2d(line, other_line)
            if not intersect:
                continue
            if not points:
                points.append[p]
                result.append([other_line])
            else:
                for group, prev_p in enumerate(points):
                    if np.linalg.norm(p - prev_p) < close:
                        result[group].append(other_line)
                        break

        return result

###############################################################
# Utility functions
###############################################################

def intersect_2d(l1, l2):
    """
    Arguments:
    l1, l2 -- numpy arrays of shape [2, 2]
    """
    print(l1, l2)
    d1 = l1[1] - l1[0]
    d2 = l2[1] - l2[0]

    # See https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Using_homogeneous_coordinates
    U1 = np.array([-d1[1], d1[0], d1[1] * l1[0, 0] - d1[0] * l1[0, 1]])
    U2 = np.array([-d2[1], d2[0], d2[1] * l2[0, 0] - d2[0] * l2[0, 1]])
    P = np.cross(U1, U2)
    if np.isclose(P[2], 0):
        return False, None

    p = np.array([P[0] / P[2], P[1] / P[2]])
    print("p: {}".format(p))
    # Check that p lies between each endpoint
    if np.dot(p - l1[0], d1) < 0:
        return False, None
    if np.dot(l1[1] - p, d1) < 0:
        return False, None
    if np.dot(p - l2[0], d2) < 0:
        return False, None
    if np.dot(l2[1] - p, d2) < 0:
        return False, None

    return True, p


