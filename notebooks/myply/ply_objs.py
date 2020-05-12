import os
import numpy as np

import wireframe.wireframe_ransac

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

        pts = np.linspace(other.line[0], other.line[1], num=num_pts)
        for p in pts:
            if self.distance(p) > tol:
                return False
        return True

class PLY():

    def __init__(self, vertices, edges, edge_labels):
        self.vertices = vertices if vertices else []
        self.edges = edges if edges else []
        # list of tuples giving image num, line num
        self.edge_labels = edge_labels if (edges and edge_labels) else []
        self.update_header()

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
        labels = self.edge_labels.copy()
        plys = []
        while len(all_lines) > 0:
            e0 = all_lines.pop(0)
            index = 0
            line_set = [e0]
            label_set = [labels.pop(0)]
            while index < len(all_lines):
                if e0.close(all_lines[index], tol=tol):
                    line_set.append(all_lines.pop(index))
                    label_set.append(labels.pop(index))
                else:
                    index += 1
            if len(line_set) > min_group:
                print("Found {} close lines".format(len(line_set)))
                plys.append(PLY(None, line_set, label_set))
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
        for e, label in zip(self.edges, self.edge_labels):
            yield "{} {} 255 255 255 {} {}\n".format(i, i+1, label[0], label[1])
            i += 2

    def combine(self, other):
        self.vertices += other.vertices
        self.edges += other.edges
        self.edge_labels += other.edge_labels
        self.update_header()

    def add_vertices(self, vertices):
        self.vertices += vertices
        self.update_header()

    def update_header(self):
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
                  "property int label1\n",
                  "property int label2\n",
                  "end_header\n"]

    def remove_all_vertices(self):
        self.vertices = []
        self.update_header()

    def remove_all_edges(self):
        self.edges = []
        self.edge_labels = []
        self.update_header()

    def remove_some_vertices(self, keep_every):
        new_vertices = []
        for i, v in enumerate(self.vertices):
            if i % keep_every == 0:
                new_vertices.append(v)
        self.vertices = new_vertices
        self.update_header()

    def enforce_bounding_box(self, c1, c2):
        min_x = min(c1[0], c2[0])
        min_y = min(c1[1], c2[1])
        min_z = min(c1[2], c2[2])
        max_x = max(c1[0], c2[0])
        max_y = max(c1[1], c2[1])
        max_z = max(c1[2], c2[2])
        i = 0
        while i < len(self.vertices):
            v = self.vertices[i]
            if ((v.pt[0] < min_x or v.pt[1] < min_y or v.pt[2] < min_z) or 
                    (v.pt[0] > max_x or v.pt[1] > max_y or v.pt[2] > max_z)):
                self.vertices.pop(i)
                continue
            i += 1

        i = 0
        while i < len(self.edges):
            l = self.edges[i].line
            v = l[0]
            if ((v[0] < min_x or v[1] < min_y or v[2] < min_z) or 
                    (v[0] > max_x or v[1] > max_y or v[2] > max_z)):
                self.edges.pop(i)
                continue
            v = l[1]
            if ((v[0] < min_x or v[1] < min_y or v[2] < min_z) or 
                    (v[0] > max_x or v[1] > max_y or v[2] > max_z)):
                self.edges.pop(i)
                continue
            i += 1
        self.update_header()

class PLYEdge(PLY):

    def __init__(self, ply):
        super().__init__(ply.vertices.copy(), ply.edges.copy(), ply.edge_labels.copy())

    def combine_edges(self):
        """
        Combines all edges into a single edge to approximate all edges.
        """
        avg_direction = self.edges[0].direction()
        for e in self.edges[1:]:
            avg_direction += e.direction() * np.dot(e.direction(), avg_direction) / np.abs(np.dot(e.direction(), avg_direction))
        avg_direction /= np.linalg.norm(avg_direction)
        avg_pt = self.closest_intersection_pt()
        min_param = 10000
        max_param = -10000
        for e in self.edges:
            param1 = np.dot(avg_direction, e.line[0] - avg_pt)
            param2 = np.dot(avg_direction, e.line[1] - avg_pt)
            min_param = min(min_param, param1, param2)
            max_param = max(max_param, param1, param2)
        p1 = avg_pt + avg_direction * min_param
        p2 = avg_pt + avg_direction * max_param
        self.vertices = []
        self.edges = [Edge(Vertex(p1[0], p1[1], p1[2]), Vertex(p2[0], p2[1], p2[2]))]
        self.edge_labels = [(-1, -1)]
        self.update_header()

    def closest_intersection_pt(self):
        # See wikipedia: https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#In_more_than_two_dimensions

        A = np.zeros((3, 3))
        b = np.zeros(3)
        for e in self.edges:
            A += np.eye(3) - np.outer(e.direction(), e.direction())
            b += np.matmul(np.eye(3) - np.outer(e.direction(), e.direction()), e.line[0])

        res, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
        return res

    def combine_edges_with_ransac(self, iterations, inlier_thresh):
        fitter = wireframe.wireframe_ransac.Line3DRANSAC(iterations, inlier_thresh, None)
        line, n_inliers = fitter.ransac(np.array([v.pt for v in self.vertices]))
        self.edges = [Edge(Vertex(line[0, 0], line[0, 1], line[0, 2]), Vertex(line[1, 0], line[1, 1], line[1, 2]))]
        self.edge_labels = [(-1, -1)]
        self.update_header()

class PLYLoader():

    def __init__(self):
        pass

    def load(self, filename):
        vertices = []
        edges = []
        edge_labels = []
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
                    if len(words) == 7:
                        edge_labels.append((int(words[5]), int(words[6])))
                    else:
                        edge_labels.append((-1, -1))
                    num_edges -= 1
                else:
                    raise Exception("We don't deal with faces")

        return PLY(vertices, edges, edge_labels)

class PLYParser():

    def __init__(self, directory):
        # Vertices will be all the vertex lines in all the ply files
        self.total_vertices = 0
        # Edges will be the (derived) relevant line defining edges in all the ply files
        self.edges = []
        self.directory = directory

    def merge(self, output):
        directories = [self.directory]
        header = ["ply\n",
                  "format ascii 1.0\n",
                  "element vertex ",
                  # Blank space to put in the number of elements at the end
                  "                                                     \n",
                  "property float x\n",
                  "property float y\n",
                  "property float z\n",
                  "property uchar red\n",
                  "property uchar green\n",
                  "property uchar blue\n",
                  "element edge ",
                  # Blank space to put in the number of elements at the end
                  "                                                     \n",
                  "property int vertex1\n",
                  "property int vertex2\n",
                  "property uchar red\n",
                  "property uchar green\n",
                  "property uchar blue\n",
                  "end_header\n"]

        with open(output, 'w') as out:
            out.writelines(header)

            while len(directories) > 0:
                d = directories.pop()
                with os.scandir(d) as it:
                    for dirent in it:
                        if dirent.is_dir():
                            directories.append(dirent.path)
                        if dirent.is_file() and dirent.name[-4:] == ".ply":
                            with open(dirent.path, 'r') as fp:
                                # Write all the vertex lines as soon as possible
                                out.writelines(self.parse_ply_fp(fp))

            self.total_edges = len(self.edges)
            out.writelines(self.edges)

            vertex_start_pos = 0
            for h in header[:3]:
                vertex_start_pos += len(h)
            out.seek(vertex_start_pos)
            out.write("{}\ncomment space".format(self.total_vertices))

            edge_start_pos = 0
            for h in header[:11]:
                edge_start_pos += len(h)
            out.seek(edge_start_pos)
            out.write("{}\ncomment space".format(self.total_edges))


    def parse_ply_fp(self, fp):
        """
        Yields all the vertex lines, adds the edge lines to internal datastructure
        """
        num_vertices = 0
        num_edges = 0


        in_header = True
        while in_header:
            words = fp.readline().split()
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
            return

        vertices_start = self.total_vertices
        # No longer in the header region
        for l in fp:
            if num_vertices > 0:
                yield l
                self.total_vertices += 1
                num_vertices -= 1 
            elif num_edges > 0:
                words = l.split()
                u, v = int(words[0]), int(words[1])
                r, g, b = words[2], words[3], words[4]
                self.edges.append("{} {} {} {} {}\n".format(u + vertices_start, v + vertices_start, r, g, b))
                num_edges -= 1
            else:
                raise Exception("Shouldn't happen")
