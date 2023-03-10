# @author: Yun Yang
# @prerequite: Maya 2018
# @description: 
#   This script transforms mixamo fbx to obj sequences
#   One should select the transform that is skined, and run the script


import maya.cmds as cmds
import itertools
import os
import sys


class ObjSequnceConvertor:
    """
    @description: 
        obj sequence convertor
    """
    def __init__(self, skinedTransform):
        self.skinedTransform = skinedTransform
        self.rootJoint = self.__findRootJoint(skinedTransform)
        self.animationRange = self.__findAnimationRange(self.rootJoint)

        print("--------------------------------------------------")
        print(str(sys._getframe().f_lineno), self.rootJoint)
        print(str(sys._getframe().f_lineno), self.animationRange)

    def __del__(self):
        pass

    def __startFromTpose(self, transitionFrames):
        startFrame = self.animationRange["start"] - transitionFrames
        endFrame = self.animationRange["end"]

        # create an animation layer and add all selected joints
        cmds.select(self.rootJoint, hierarchy=True)
        animationLayer = cmds.animLayer("AnimLayer1")
        cmds.setAttr(animationLayer + ".rotationAccumulationMode", 0)
        cmds.setAttr(animationLayer + ".scaleAccumulationMode", 1)
        cmds.animLayer(animationLayer, edit=True, addSelectedObjects=True)

        # lock the base animation layer to prevent wrong operation
        cmds.animLayer("BaseAnimation", edit=True, lock=True)

        # set keyframe at the original start and startFrame of T-pose
        cmds.select(self.rootJoint, hierarchy=True)
        cmds.setKeyframe(animLayer="AnimLayer1",
                         attribute='rotateX',
                         t=self.animationRange["start"])
        cmds.setKeyframe(animLayer="AnimLayer1",
                         attribute='rotateY',
                         t=self.animationRange["start"])
        cmds.setKeyframe(animLayer="AnimLayer1",
                         attribute='rotateZ',
                         t=self.animationRange["start"])
        cmds.setKeyframe(animLayer="AnimLayer1",
                         attribute='rotateX',
                         t=startFrame,
                         value=0)
        cmds.setKeyframe(animLayer="AnimLayer1",
                         attribute='rotateY',
                         t=startFrame,
                         value=0)
        cmds.setKeyframe(animLayer="AnimLayer1",
                         attribute='rotateZ',
                         t=startFrame,
                         value=0)

        self.animationRange["start"] = startFrame

    def __convert(self, exportDir, exportBaseName, digits, startFrame,
                  endFrame, objPerFrame, renumberFrame, startNumber):
        cmds.select(self.skinedTransform)

        if startFrame < 0 or objPerFrame != 1:
            renumberFrame = True

        exportBaseName = exportBaseName.strip()
        if not exportBaseName:
            exportBaseName = self.skinedTransform.strip()

        frames = []
        try:
            frames = itertools.takewhile(
                lambda x: x < endFrame,
                itertools.count(startFrame, 1.0 / objPerFrame))
            if type(frames) != type(list):
                frames = []
                raise Exception("itertools doesn't fully supported")
        except:
            print("itertools doesn't fully supported")

            frame = startFrame
            print(str(sys._getframe().f_lineno), frame)
            print(str(sys._getframe().f_lineno), startFrame)
            print(str(sys._getframe().f_lineno), endFrame)
            while frame < endFrame:
                frames.append(frame)
                frame += 1.0 / objPerFrame

        print(str(sys._getframe().f_lineno), frames)

        # get digits of number to padding zeros
        maxFrame = endFrame
        if renumberFrame:
            maxFrame = startNumber + len(frames)
        minDigitsRequired = len(str(maxFrame))
        if minDigitsRequired > digits:
            digits = minDigitsRequired

        for i in range(len(frames)):
            cmds.currentTime(frames[i])

            index = i
            if renumberFrame:
                index = i + startNumber

            outputPath = exportDir + "/" + exportBaseName + str(index).zfill(
                digits) + ".obj"

            print(outputPath)

            cmds.file(
                outputPath,
                force=True,
                options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1",
                type="OBJexport",
                preserveReferences=True,
                exportSelected=True)

    def __findRootJoint(self, skinedTransform):
        # this will return deformed mesh and original mesh of the fbx
        meshes = cmds.listRelatives(skinedTransform,
                                    children=True,
                                    type="mesh")
        # find the skin cluster connecting to the deformed mesh
        for mesh in meshes:
            skinCluster = cmds.listConnections(mesh,
                                               type="skinCluster",
                                               exactType=True,
                                               destination=False)
            if skinCluster:
                break
        # find all joints connecting to skin cluster node
        joints = cmds.listConnections(skinCluster,
                                      type="joint",
                                      exactType=True,
                                      destination=False)
        # find the root joints that isn't be connected by other joints on the source side
        for joint in joints:
            if not cmds.listConnections(
                    joint, type="joint", exactType=True, destination=False):
                rootJoint = joint
                break

        return rootJoint

    def __findAnimationRange(self, rootJoint):
        startFrame = cmds.findKeyframe("mixamorig:Hips",
                                       hierarchy="both,",
                                       which="first")
        endFrame = cmds.findKeyframe("mixamorig:Hips",
                                     hierarchy="both,",
                                     which="last")

        return {"start": startFrame, "end": endFrame}

    def getAnimationRange(self):
        return self.animationRange

    def run(self,
            exportDir,
            exportBaseName="",
            digits=4,
            startFromTpose=True,
            transitionFrames=30,
            startFrame=0,
            endFrame=-1,
            objPerFrame=8,
            renumberFrame=False,
            startNumber=0):
        # startNumber must be greater than 0
        if startNumber < 0:
            raise Exception("Start number must be nonnegative")
        # digits must be no less than 0
        if digits <= 0:
            raise Exception("Digits must be positive")
        #
        if startFromTpose:
            self.__startFromTpose(transitionFrames)
        # minimize the number of the exported objs
        if startFrame > endFrame:
            startFrame = self.animationRange["start"]
            endFrame = self.animationRange["end"]

        if not os.path.exists(exportDir):
            os.mkdir(exportDir)

        print(str(sys._getframe().f_lineno), startFrame)
        print(str(sys._getframe().f_lineno), endFrame)

        self.__convert(startFrame=startFrame,
                       endFrame=endFrame,
                       objPerFrame=objPerFrame,
                       exportDir=exportDir,
                       exportBaseName=exportBaseName,
                       digits=digits,
                       renumberFrame=renumberFrame,
                       startNumber=startNumber)


if __name__ == "__main__":
    export_dir = "C:/Users/syby119/Desktop/poses"
    export_base_name = "body"
    
    
    objects = cmds.ls(selection=True)
    if len(objects) == 1:
        convertor = ObjSequnceConvertor(objects[0])
        convertor.run(
            exportDir=export_dir, 
            exportBaseName=export_base_name)