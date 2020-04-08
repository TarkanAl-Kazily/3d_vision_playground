from utils import video_to_images
import argparse

def main():
    parser = argparse.ArgumentParser(description='Save a video frame to a series of images')
    parser.add_argument('--filename', type=str, help='filename of the video, exclude the extension')
    parser.add_argument('--n', type=int, default=1, help='save every n images')
    parser.add_argument('--path', default='', type=str, help='path to video if stored in another directory')

    args = parser.parse_args()

    video_to_images(args.filename, n=args.n, path_to_video=args.path)

if __name__ == "__main__":
    main()


