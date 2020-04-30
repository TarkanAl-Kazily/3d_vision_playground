import cv2, os, subprocess

def video_to_images(inputfile, n, outputdir, rotate=0):
    """
    Takes in an mp4 video and images to a directory named after the video
    Inputs:
        filename: the name of the video (exlude the .mp4)
        n: save every n images - for if you do not want to save every frame
        path_to_video: if the video is not in the home directory
        rotate: number of times to rotate the image by 90 degrees
    Outputs:
        None
    """
    cap = cv2.VideoCapture(inputfile)
    success, img = cap.read()
    if not success:
        print("Failed to read from the capture")
        return

    print("Reading from {}".format(inputfile))
    count = 0
    img_id = 0
    rotateCode = None
    toby = None
    if rotate == 1:
        rotateCode = cv2.ROTATE_90_CLOCKWISE
    if rotate == 2:
        rotateCode = cv2.ROTATE_180
    if rotate == 3:
        rotateCode = cv2.ROTATE_90_COUNTERCLOCKWISE
    if rotate == 4:
        rotateCode = cv2.ROTATE_90_COUNTERCLOCKWISE
        toby = cv2.ROTATE_180

    while success:
        if (count % n == 0):
            output_filename = os.path.join(outputdir, "img_{}.png".format(img_id))
            if rotateCode and not toby:
                img = cv2.rotate(img, rotateCode)
            if rotateCode and toby:
                img = cv2.rotate(img, rotateCode)
                img = cv2.rotate(img, toby)
            cv2.imwrite(output_filename, img)
            img_id += 1

        success, img = cap.read()
        count += 1
    print("Successfully saved {} frames".format(img_id))

class FFMPEGFrames:
    def __init__(self, output):
        self.output = output

    def extract_frames(self, input, fps):
        output = input.split('/')[-1].split('.')[0]

        if not os.path.exists(self.output):
            os.makedirs(self.output)

        query = "ffmpeg -i " + input + " -vf fps=" + str(fps) + " " + self.output + "/output%06d.png"
        response = subprocess.Popen(query, shell=True, stdout=subprocess.PIPE).stdout.read()
        s = str(response).encode('utf-8')
