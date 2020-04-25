#
# merge_ply.py
#
# Recursively merges all ply files in a given directory
#

import argparse
import os

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

            print(len(self.edges))
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

def main(args):
    ply_parser = PLYParser(args.directory)
    ply_parser.merge(args.output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, help="directory storing the ply files")
    parser.add_argument('--output', '-o', type=str, help="output filename", default="all_merged.ply")
    args = parser.parse_args()
    main(args)

