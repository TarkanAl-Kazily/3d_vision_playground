import wireframe
import utils
import argparse

def main(args):
    # Filepaths
    config_file = utils.data("wireframe.yaml")
    model_file = utils.data("pretrained_lcnn.pth.tar")

    w = wireframe.Wireframe(config_file, model_file, "")
    if not w.setup():
        print(w.error)
    else:
        print("w is setup successfully")

    # Controls how small the minimum connected component can be
    desired_edges = 2

    for imname in args.image:
        im, g, subgraphs = w.get_filtered_subgraphs(imname, desired_edges)
        g.plot_graph(g.g, im)
        print("\n\nFound {} subgraphs".format(len(subgraphs)))

        for s in subgraphs:
            print("\n\n===================\n\n")
            g.plot_graph(s, im)

        print("\n\nReduced subgraphs to {} graphs".format(len(subgraphs)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('image', nargs='+')
    args = parser.parse_args()
    main(args)
