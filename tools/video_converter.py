from utils import video_to_images
import argparse

def main():
    parser = argparse.ArgumentParser(description='Save a video frame to a series of images')
    parser.add_argument('inputfile', type=str, help='filename of input video')
    parser.add_argument('--n', type=int, default=1, help='save every n images')
    parser.add_argument('--outputdir', default='./', type=str, help='directory to store output files to')

    args = parser.parse_args()

    video_to_images(args.inputfile, args.n, args.outputdir)

# Credit to https://github.com/alibugra/frame-extraction for the better frame extraction code that preserves metadata

if __name__ == "__main__":
    main()
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-i", "--input", required=True)
    # ap.add_argument("-fname", "--filename", required=True)
    # ap.add_argument("-f", "--fps", required=True)
    # args = vars(ap.parse_args())

    # input = args["input"]
    # fps = args["fps"]

    # f = FFMPEGFrames("../data/"+args["filename"]+"/images/")
    # f.extract_frames(input, fps)


