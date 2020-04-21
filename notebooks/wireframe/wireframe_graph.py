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
    """
    def __init__(self, record, name=None):
        """
        Arguments:
        record -- a wireframe record object
        name -- (optional) name for graph
        """
        self.rec = record
        self.g = Graph()
        self.g["name"] = name if name else ""

        # disc specifies how many cells to consider vertices in
        self.disc = 1000

        self.setup_graph()

    def setup_graph(self):
        # Add vertices to g
        all_pts = self.rec.lines().reshape((self.rec.num_lines * 2, 2))
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
        for i in range(self.rec.num_lines):
            l = self.rec.lines()[i]
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
        arr = (pts * self.disc).astype(int)
        for i, j in arr:
            result.append((i, j))
        return result
