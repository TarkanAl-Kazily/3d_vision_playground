import cv2, os, subprocess

def video_to_images(filename, n=1, path_to_video=''):
    """
    Takes in an mp4 video and images to a directory named after the video
    Inputs:
        filename: the name of the video (exlude the .mp4)
        n: save every n images - for if you do not want to save every frame
        path_to_video: if the video is not in the home directory
    Outputs:
        None
    """
    if os.path.isdir("../data/"+filename) == False:
        os.mkdir("../data/"+filename)
    if os.path.isdir("../data/"+filename+"/images/") == False:
        os.mkdir("../data/"+filename+"/images/")
    cap = cv2.VideoCapture(path_to_video+filename+'.mp4')
    success, img = cap.read()
    count = 0
    img_id = 0
    while success:
        if (count % n == 0):
            cv2.imwrite("../data/"+filename+"/images/img_{}.png".format(img_id), img)
            img_id += 1

        success, img = cap.read()
        count += 1
    print("Successfully saved {} frames".format(count))

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