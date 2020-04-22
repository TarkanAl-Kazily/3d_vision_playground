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
        self.g["name"] = name if name else ""

        # disc specifies how many cells to consider vertices in
        self.disc = 100
        self.imshape = self.rec.imshape

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

    def plot_graph(self, graph, im):
        print("Plotting graph:\n{}\n".format(graph))
        plt.gca().set_axis_off()
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.margins(0, 0)
        for i, edge in enumerate(graph.es):
            s = graph.es["score"][edge.index]
            vs = [graph.vs["idx"][edge.source], graph.vs["idx"][edge.target]]
            pts = self.vertex_to_point(vs)
            plt.plot([pts[0, 1], pts[1, 1]], [pts[0, 0], pts[1, 0]], c=c(s), linewidth=2, zorder=s)
            plt.scatter(pts[0, 1], pts[0, 0], **PLTOPTS)
            plt.scatter(pts[1, 1], pts[1, 0], **PLTOPTS)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.imshow(im)
        plt.show()
        plt.close()

    def connected_subgraphs(self):
        return self.g.components().subgraphs()
