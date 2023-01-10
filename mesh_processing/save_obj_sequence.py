# @author: Yun Yang
# @prerequesite: Maya 2022
# @description: 
#   This script saves Maya scene to obj sequence
#   Generally, it is used to transform character fbx to obj sequence

import maya.cmds as cmds
import maya.mel as mel
import os


def make_directory(output_dir: str):
    """
    @description: 
        make a new directory if the specified directory doesn't exist
    @param output_dir: output directory
    """
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)


def get_fps() -> float:
    """
    @description: 
        get frame per second of the timeline
    @return: frame per second
    """
    return mel.eval('currentTimeUnitToFPS')


def set_fps(fps: str):
    """
    @description: 
        set frame per second of the timeline
    @param fps: frame per second, which is corresponding to Maya playback speed options
    """
    cmds.currentUnit(time=fps)


def save_objs(
    output_dir:str, output_prefix:str, digits:int, 
    start_frame:int, end_frame:int, save_pre_frame:int,
    compress:bool):
    """
    @description: 
        save the scene as the obj file sequence
    @usage: 
        save_obj("C:/User/syby119/Desktop", "body", 4, 0, 4, 2, true)
        the follow file will be saved:
        + C:/User/syby119/Desktop/body0000.obj
        + C:/User/syby119/Desktop/body0002.obj
        + C:/User/syby119/Desktop/body0004.obj
    @param output_dir: output directory of the obj file
    @param output_prefix: obj file prefix
    @param digits: padding digits
    @param start_frame: start frame
    @param end_frame: end frame
    @param save_pre_frame: step of the frame
    @param compress: whether to compress the obj file
    """
    cmds.select(all=True)
    
    index = 0
    for frame in range(start_frame, end_frame + 1):
        for i in range(save_per_frame):
            cmds.currentTime(frame + i / save_pre_frame)
            filename = output_prefix + str(index).zfill(digits) + ".obj"
            output_path = os.path.join(output_dir, filename)

            options = "groups=1;ptgroups=1;"
            if compress:
                options += "materials=0;smooting=0;normals=0;"
            else:
                options = "materials=1;smooting=1;normals=1"

            cmds.file(
                output_path,
                force=True,
                options=options,
                type="OBJexport",
                preserveReferences=True,
                exportSelected=True)
            
            index += 1
            
            print(output_path)


if __name__ == "__main__":
    # timeline options
    fps = "30fps"
    start_frame, end_frame = -30, 410
    save_per_frame = 1
    
    # output options
    output_dir = "C:/Users/syby119/Desktop/body"
    output_prefix = "body"
    digits = 4
    
    # compress options
    compress = False
    
    make_directory(output_dir)
    set_fps(fps)
    save_objs(
        output_dir, output_prefix, digits, 
        start_frame, end_frame, save_per_frame, 
        compress)