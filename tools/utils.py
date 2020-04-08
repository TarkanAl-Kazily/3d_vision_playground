import cv2, os

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
    if os.path.isdir(filename) == False:
        os.mkdir(filename)
    cap = cv2.VideoCapture(path_to_video+filename+'.mp4')
    success, img = cap.read()
    count = 0
    img_id = 0
    while success:
        if (count % n == 0):
            cv2.imwrite("../"+filename+"/img_{}.png".format(img_id), img)
            img_id += 1

        success, img = cap.read()
        count += 1
    print("Successfully saved {} frames".format(count))