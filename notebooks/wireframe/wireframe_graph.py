#
# graph.py
#
# Class built on existing graph library for wireframe graph representation.
#

import numpy as np
from igraph import Graph

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
        self.disc = 10000
        self.imshape = self.rec.imshape

        self.setup_graph()

    def setup_graph(self):
        # Add vertices to g
        nlines = self.rec.lines_postprocess()
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
