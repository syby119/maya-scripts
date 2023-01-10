# @author: Yun Yang
# @prerequite: Maya 2022
# @description: 
#   This script seperates the obj models to multiple connected parts.
#   The seperation will be done for each file in the given directory

import os
import maya.cmds as cmds


def seperate_obj(input_filepath:str, output_dir:str, padding=3):
    """
    @description: 
        read the obj file and seperate the model into sereral connected parts
        if C:/Users/syby119/Desktop/cloth0000.obj file consists 3 different clothes,
        then the obj will be seperated into
        + C:/Users/syby119/Desktop/cloth0000_000.obj
        + C:/Users/syby119/Desktop/cloth0000_001.obj
        + C:/Users/syby119/Desktop/cloth0000_002.obj
    @usage: process_obj("C:/Users/syby119/Desktop/cloth0000.obj")
    @param input_filepath: the full path of the obj file to be seperated
    @param output_dir: output directory of the result
    @param padding: zero padding for seperated parts 
    """
    cmds.file(new=True, force=True)
    cmds.file(input_filepath, i=True)
    
    mesh_shape = cmds.ls(exactType="mesh")
    results = cmds.polySeparate(mesh_shape, constructionHistory=True)
    
    for index in range(len(results) - 1):
        cmds.select(results[index])
        input_name = os.path.splitext(os.path.basename(input_filepath))[0]
        output_filename = input_name + str(index).zfill(padding) + ".obj"
        cmds.file(
            os.path.join(output_dir, output_filename),
            options="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1",
            type="OBJexport",
            preserveReferences=True,
            exportSelected=True,
            force=True)
            
        print(output_filename)


if __name__ == "__main__":
    input_dir = "C:/Users/syby119/Desktop/resume-cloth"
    output_dir = "C:/Users/syby119/Desktop/seperate-cloth"

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for (root, dirs, files) in os.walk(input_dir):
        for file in files:
            if not file.endswith(".obj"):
                continue
            
            seperate_obj(os.path.join(root, file), output_dir)