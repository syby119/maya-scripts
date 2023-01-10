# @author: Yun Yang
# @prerequite: Arnold Renderer
# @description: 
#   This script renders each scene in the background and output the image sequence


import os

if __name__ == "__main__":
    workDir = os.path.dirname(os.path.abspath(__file__))
    base = os.path.join(workDir, "predict_scenes")
    target = os.path.join(workDir, "predict_pictures")

    if not os.path.exists(target):
        os.mkdir(target)

    exe = "E:/Autodesk/Maya2019/bin/Render.exe"
    imageFormat = "png"
    renderer = "arnold"
    namingConvention = 1

    for root, ds, fs in os.walk(base):
        for f in fs:
            scene = os.path.join(base, f)
            saveName = f.split(".")[0]

            cmd = '"%s" -s 1 -e 1 -r arnold -rd %s -im %s -fnc %d -of %s %s'\
                   %(exe, target, saveName, namingConvention, imageFormat, scene)
            print(cmd)
            os.system(cmd)