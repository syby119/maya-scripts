# @author: Yun Yang
# @prerequite: OpenCV
# @description: 
#   This script transforms the given image sequence to a video.
#   The image format of the image sequence can be .png or .tif



import os
import cv2
import random

if __name__ == "__main__":
    workDir = os.path.dirname(os.path.abspath(__file__))
    
    workDir = "C:/Users/87979/Desktop/NerualCloth/codes/VirtualBones/out"
    base = os.path.join(workDir, "outPicture")
    target = workDir

    if not os.path.exists(target):
        os.mkdir(target)

    videoName = os.path.join(target, "final.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 30
    videoWriter = None

    for root, ds, fs in os.walk(base):
        # random.shuffle (fs)
        for f in fs:
            if videoWriter == None:
                pngShape = cv2.imread(os.path.join(base, f)).shape
                resolution = (pngShape[1], pngShape[0])
                videoWriter = cv2.VideoWriter(videoName, fourcc, fps, resolution)
            imgName = os.path.join(base, f)
            frame = cv2.imread(imgName)
            videoWriter.write(frame)
    print("----------------video saved------------------")
    videoWriter.release()