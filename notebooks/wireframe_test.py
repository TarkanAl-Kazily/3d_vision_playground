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

    imname = utils.data("PurnurOffice/IMG_0863.jpg")
    rec = w.parse(imname)

    g = wireframe.WireframeGraph(rec)

    # Get the strong connected components of the graph
    components = g.g.components()
    subgraphs = components.subgraphs()

    print("\n\nFound {} subgraphs".format(len(subgraphs)))

    i = 0
    while i < len(subgraphs):
        if subgraphs[i].ecount() == 1:
            subgraphs.pop(i)
        else:
            i += 1

    for s in subgraphs:
        print("\n\n===================\n\n")
        print(s.vs["idx"])

    print("\n\nReduced subgraphs to {} graphs".format(len(subgraphs)))

if __name__ == "__main__":
    main()
