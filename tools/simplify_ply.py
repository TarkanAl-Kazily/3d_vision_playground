#
# merge_ply.py
#
# Recursively merges all ply files in a given directory
#

import argparse
import os

import numpy as np

class Vertex():

    def __init__(self, x, y, z):
        self.pt = np.array([x, y, z])

class Edge():
    def __init__(self, u, v):
        self.line = np.vstack((u.pt, v.pt))

    def direction(self):
        return (self.line[1] - self.line[0]) / (np.linalg.norm(self.line[1] - self.line[0]))

    def parallel2(self, other, tol=0.1):
        return np.linalg.norm(np.cross(self.direction(), other.direction())) < tol

    def parallel(self, other):
        return (np.allclose(self.direction(), other.direction(), atol=0.1) or
                np.allclose(self.direction(), other.direction(), atol=0.1))

    def distance(self, point):
        return np.linalg.norm(np.cross(self.direction(), point - self.line[0]))

    def close(self, other, tol=0.5, num_pts=10):
        pts = np.linspace(self.line[0], self.line[1], num=num_pts)
        for p in pts:
            if other.distance(p) > tol:
                return False
        return True

class PLY():

    def __init__(self, vertices, edges):
        self.vertices = vertices if vertices else []
        self.edges = edges if edges else []
        self.header = ["ply\n",
                  "format ascii 1.0\n",
                  "element vertex {}\n".format(len(self.vertices) + 2 * len(self.edges)),
                  "property float x\n",
                  "property float y\n",
                  "property float z\n",
                  "property uchar red\n",
                  "property uchar green\n",
                  "property uchar blue\n",
                  "element edge {}\n".format(len(self.edges)),
                  "property int vertex1\n",
                  "property int vertex2\n",
                  "property uchar red\n",
                  "property uchar green\n",
                  "property uchar blue\n",
                  "end_header\n"]

    def get_parallel_lines(self, tol=0.1, min_group=10):
        all_lines = self.edges.copy()
        plys = []
        while len(all_lines) > 0:
            e0 = all_lines.pop(0)
            index = 0
            line_set = [e0]
            while index < len(all_lines):
                if e0.parallel2(all_lines[index], tol=tol):
                    line_set.append(all_lines.pop(index))
                else:
                    index += 1
            if len(line_set) > min_group:
                print("Found {} parallel lines".format(len(line_set)))
                plys.append(PLY(None, line_set))
        return plys

    def get_nearby_lines(self, tol=0.5, min_group=5):
        # Filters lines based on minimum distance
        all_lines = self.edges.copy()
        plys = []
        while len(all_lines) > 0:
            e0 = all_lines.pop(0)
            index = 0
            line_set = [e0]
            while index < len(all_lines):
                if e0.close(all_lines[index], tol=tol):
                    line_set.append(all_lines.pop(index))
                else:
                    index += 1
            if len(line_set) > min_group:
                print("Found {} close lines".format(len(line_set)))
                plys.append(PLY(None, line_set))
        return plys

    def write(self, filename):
        with open(filename, 'w') as f:
            f.writelines(self.header)
            f.writelines(self.write_elements())

    def write_elements(self):
        for v in self.vertices:
            yield "{} {} {} 255 255 255\n".format(v.pt[0], v.pt[1], v.pt[2])

        for e in self.edges:
            yield "{} {} {} 255 255 255\n".format(e.line[0, 0], e.line[0, 1], e.line[0, 2])
            yield "{} {} {} 255 255 255\n".format(e.line[1, 0], e.line[1, 1], e.line[1, 2])

        i = len(self.vertices)
        for e in self.edges:
            yield "{} {} 255 255 255\n".format(i, i+1)
            i += 2

class PLYLoader():

    def __init__(self):
        pass

    def load(self, filename):
        vertices = []
        edges = []
        num_vertices = 0
        num_edges = 0
        with open(filename, 'r') as f:
            in_header = True
            while in_header:
                words = f.readline().split()
                if words[0] == "end_header":
                    in_header = False
                if words[0] != "element":
                    continue

                if words[1] == "vertex":
                    num_vertices = int(words[2])
                if words[1] == "edge":
                    num_edges = int(words[2])

            if num_vertices + num_edges == 0:
                # No elements found - OK
                print("No vertices or edges")
                return

            # No longer in the header region
            for l in f:
                if num_vertices > 0:
                    words = l.split()
                    vertex = Vertex(float(words[0]), float(words[1]), float(words[2]))
                    vertices.append(vertex)
                    num_vertices -= 1
                elif num_edges > 0:
                    words = l.split()
                    edge = Edge(vertices[int(words[0])], vertices[int(words[1])])
                    edges.append(edge)
                    num_edges -= 1
                else:
                    raise Exception("We don't deal with faces")

        return PLY(vertices, edges)

def main(args):
    ply_loader = PLYLoader()
    ply = ply_loader.load(args.filename)
    print("Loaded {} total edges".format(len(ply.edges)))
    if args.filter == "parallel":
        ply_set = ply.get_parallel_lines(tol=args.tol)
        index = 0
        for ply in ply_set:
            ply.write(os.path.join(args.output, "parallel_{}.ply".format(index)))
            index += 1
    if args.filter == "close":
        ply_set = ply.get_nearby_lines(tol=args.tol)
        index = 0
        for ply in ply_set:
            ply.write(os.path.join(args.output, "close_{}.ply".format(index)))
            index += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help="ply file to load")
    parser.add_argument('--output', '-o', type=str, help="output directory", default=".")
    parser.add_argument('--filter', choices=['parallel', 'close'], help="filter operation")
    parser.add_argument('--tol', type=float, default=0.1, help="tolerance amount")
    parser.add_argument('--min_group', type=int, default=5, help="minumum number of elements in output PLY files")
    args = parser.parse_args()
    main(args)

