#
# merge_ply.py
#
# Recursively merges all ply files in a given directory
# Different ply files are given different (solid) colors

import argparse
import os

class ParsePlyError(Exception):
    def __init__(self, message):
        self.message = message

def parse_ply_fp(fp, element, num_props):
    num_prior_elements = 0
    num_elements = 0
    for l in fp:
        words = l.split()
        if words[0] == "element":
            break

    in_header = True
    prop_count = 0
    while in_header:
        # At start of loop the current line (in words) is an element line
        if words[1] == element:
            if prop_count != 0:
                raise ParsePlyError("Multiple element regions defined for type!")
            num_elements = int(words[2])
            # Iterate to next element tag, counting property tags
            for l in fp:
                words = l.split()
                if words[0] == "end_header":
                    in_header = False
                    break
                if words[0] == "element":
                    break
                if words[0] == "property":
                    prop_count += 1
            if prop_count != num_props:
                raise ParsePlyError("Incorrect number of properties!")
        else:
            if num_elements == 0:
                num_prior_elements += int(words[2])
            # Iterate to next element tag
            for l in fp:
                words = l.split()
                if words[0] == "end_header":
                    in_header = False
                    break
                if words[0] == "element":
                    break

    if num_elements == 0:
        # No elements found - OK
        return

    # No longer in the header region
    for l in fp:
        words = l.split()
        if words[0] == "comment":
            continue
        if num_prior_elements > 0:
            num_prior_elements -= 1
            continue
        if num_elements > 0:
            num_elements -= 1
            yield l



def parse_ply_files(directory, element, num_props):
    """
    Generator parsing ply files in a directory (recursively) for the given element type
    Arguments:
    directory -- the directory to search through
    element -- the element type ['vertex', 'edge']
    num_props -- number of properties the element is expected to have.
    A ParsePlyError exception is raised if not all ply file element definitions equal this number
    """
    directories = [directory]
    while len(directories) > 0:
        d = directories.pop()
        with os.scandir(d) as it:
            for dirent in it:
                if dirent.is_dir():
                    directories.append(dirent.path)
                if dirent.is_file() and dirent.name[-4:] == ".ply":
                    with open(dirent.path, 'r') as fp:
                        yield parse_ply_fp(fp, element, num_props)

def main(args):
    directory = args.directory
    with open(args.output, 'w') as f:
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
                  "end_header\n"]
        f.writelines(header)

        gen1 = parse_ply_files(directory, "vertex", 6)
        total_elements = 0
        for gen2 in gen1:
            for l in gen2:
                total_elements += 1
                f.write(l)

        f.seek(len(header[0]) + len(header[1]) + len(header[2]))
        f.write("{}\ncomment space".format(total_elements))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, help="directory storing the ply files")
    parser.add_argument('--output', '-o', type=str, help="output filename", default="all_merged.ply")
    args = parser.parse_args()
    main(args)

