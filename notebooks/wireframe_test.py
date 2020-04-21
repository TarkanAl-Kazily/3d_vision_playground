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



if __name__ == "__main__":
    main()
