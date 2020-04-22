import wireframe
import utils

def main():
    # Filepaths
    config_file = utils.data("wireframe.yaml")
    model_file = utils.data("pretrained_lcnn.pth.tar")

    w = wireframe.Wireframe(config_file, model_file, "")
    if not w.setup():
        print(w.error)
    else:
        print("w is setup successfully")

    imname = utils.data("Door/IMG_0917.jpg")
    im = w.load_image(imname)
    rec = w.parse(imname)

    g = wireframe.WireframeGraph(rec)
    g.plot_graph(g.g, im)

    # Get the strong connected components of the graph
    subgraphs = g.connected_subgraphs()

    print("\n\nFound {} subgraphs".format(len(subgraphs)))

    # Controls how small the minimum connected component can be
    desired_edges = 2

    i = 0
    while i < len(subgraphs):
        if subgraphs[i].ecount() < desired_edges:
            subgraphs.pop(i)
        else:
            i += 1

    for s in subgraphs:
        print("\n\n===================\n\n")
        g.plot_graph(s, im)

    print("\n\nReduced subgraphs to {} graphs".format(len(subgraphs)))

if __name__ == "__main__":
    main()
