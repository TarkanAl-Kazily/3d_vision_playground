import argparse
import os

import wireframe
import myply
import numpy as np

def main(args):
    origin = myply.Vertex(0, 0, 0)

    v1 = np.random.rand(3)
    v2 = np.random.rand(3)
    b1 = v1
    b2 = np.cross(v1, v2)
    b3 = np.cross(b1, b2)
    b1 /= np.linalg.norm(b1)
    b2 /= np.linalg.norm(b2)
    b3 /= np.linalg.norm(b3)
    rot = np.vstack([b1, b2, b3])

    dirs = np.random.randint(3, size=args.n)
    directions = np.vstack([rot[i] for i in dirs])
    rand = (np.random.rand(args.n, 3) - np.array([0.5, 0.5, 0.5])) * 2.0 * args.noise / np.sqrt(3)
    directions += rand
    edges = [myply.Edge(origin, myply.Vertex(d[0], d[1], d[2])) for d in directions]
    edge_labels = [(-1, -1) for d in directions]
    ply = myply.PLYEdge(myply.PLY(None, edges, edge_labels))

    est_rot = ply.add_basis_directions(args.iterations, args.threshold)
    ply.write(args.output)
    ply.filter_basis_directions(args.iterations, args.threshold)
    ply.write(args.output.replace(".ply", "_filtered.ply"))

    print("Actual rot: {}".format(rot))
    print("Est rot: {}".format(est_rot))

    print("R * R': {}".format(rot @ est_rot.transpose()))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=str, help="Output file")
    parser.add_argument('-n', type=int, default=20, help="number of random lines")
    parser.add_argument('--iterations', '-i', type=int, default=20, help="number of iterations")
    parser.add_argument('--threshold', '-t', type=float, default=0.25, help="inlier threshold")
    parser.add_argument('--noise', type=float, default=0.1, help="max magnitude of noise")
    args = parser.parse_args()
    main(args)

