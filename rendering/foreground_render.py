# @author: Yun Yang
# @prerequite: Maya 2022
# @description: 
#   This script render the scene sequences in foreground in Maya.
#   Before rendering start, one need to provide
#   + a human scene containing
#       + the character with animation
#       + the camera for rendering
#       + proper lighting
#   + the cloth scene sequence
#   The rendered images can be .png or .tif format


import os
import time
import maya.cmds as cmds
import maya.mel as mel


class ArnoldRenderer:
    """
    @description: The encapsulation class for the Arnold Renderer
    """
    def __init__(self):
        # init arnold nodes if it's not in the scene graph 
        mel.eval("cmdArnoldMtoARenderView")
        mel.eval("RenderViewWindow")
        
        self.driver = "defaultArnoldDriver"
        self.options = "defaultArnoldRenderOptions"
             
        self.antialising_samples           = cmds.getAttr("%s.AASamples" % self.options)
        self.diffuse_samples               = cmds.getAttr("%s.GIDiffuseSamples" % self.options)
        self.specular_samples              = cmds.getAttr("%s.GISpecularSamples" % self.options)
        self.subsurface_scattering_samples = cmds.getAttr("%s.GISssSamples" % self.options)
        self.transmission_samples          = cmds.getAttr("%s.GITransmissionSamples" % self.options)
        self.volume_indirect_samples       = cmds.getAttr("%s.GIVolumeSamples" % self.options)
        
        self.width = cmds.getAttr("defaultResolution.width")
        self.height = cmds.getAttr("defaultResolution.height")
        
        self.image_format = cmds.getAttr("%s.aiTranslator" % self.driver)
        
        self.camera = None
        
        self.version = cmds.getAttr("%s.version" % self.options)
        
        cmds.setAttr("defaultRenderGlobals.outFormatControl", 1)
        cmds.setAttr("defaultArnoldDriver.colorManagement", 1)
        
        
    def set_camera(self, camera:str):
        self.camera = camera
        
        
    def set_image_size(self, width:int, height:int):
        self.width = width
        self.height = height
        
        
    def set_image_format(self, format:str):
        cmds.setAttr("%s.ai_translator" % self.driver, format, type="string")
        cmds.setAttr("%s.unpremultAlpha" % self.driver, 1)
        self.image_format = format
        
    
    def set_antialising_samples(self, samples:int):
        cmds.setAttr("%s.AASamples" % self.options, samples)
        self.antialising_samples = samples
    
    
    def set_diffuse_samples(self, samples:int):
        cmds.setAttr("%s.GIDiffuseSamples" % self.options, samples)
        self.diffuse_samples = samples
        
        
    def set_specular_samples(self, samples:int):
        cmds.setAttr("%s.GISpecularSamples" % self.options, samples)
        self.specular_samples = samples
        
        
    def set_subsurface_scattering_samples(self, samples:int):
        cmds.setAttr("%s.GISssSamples" % self.options, samples)
        self.subsurface_scattering_samples = samples
    
    
    def set_transmission_samples(self, samples:int):
        cmds.setAttr("%s.GITransmissionSamples" % self.options, samples)
        self.transmission_samples = samples
        
        
    def set_volume_indirect_samples(self, samples:int):
        cmds.setAttr("%s.GIVolumeSamples" % self.options, samples)
        self.volume_indirect_samples = samples


    def set_fps(self, fps:str):
        cmds.currentUnit(time=fps)
        
    
    def render(self, frame:int, filepath:str):
        cmds.currentTime(frame)
        cmds.setAttr("%s.prefix" % self.driver, filepath, type="string")
        cmds.arnoldRender(width=self.width, height=self.height, camera=self.camera)
                
        # rename the output file from xxx.fmt_1 to xxx.fmt
        if os.path.exists(filepath):
            os.remove(filepath)
        os.rename(filepath + "_1", filepath)
        
        
    def renderInRenderView(self, frame: int, filepath:str):
        cmds.currentTime(frame)
        mel.eval("renderWindowRenderCamera redoPreviousRender renderView " + self.camera)
        
        if os.path.exists(filepath):
            os.remove(filepath)
        
        cmdline_filepath = filepath.replace("\\", "/")
        cmdline_format = self.image_format.upper()
        mel.eval('renderWindowSaveImageCallback renderView "' + cmdline_filepath + '" ' + cmdline_format)
        
        
    def print_settings(self):
        print("===== Render Info =====")
        print("+ arnold version: %s" % (self.version))
        print("+ image resolution: %s x %s" % (self.width, self.height))
        print("+ camera: %s" % (self.camera))
        print("+ samples")
        print("  + antialising:           ", self.antialising_samples)
        print("  + diffuse:               ", self.diffuse_samples)
        print("  + specular:              ", self.specular_samples)
        print("  + subsurface scattering: ", self.subsurface_scattering_samples)
        print("  + transmission:          ", self.transmission_samples)
        print("  + volume indirect:       ", self.volume_indirect_samples)


if __name__ == "__main__":    
    # import human scene
    # we assume that 
    # + the human has its own material
    # + the lights for rendering has already exist
    # + the camera for rendering has already exist
    character_filepath = "C:/Users/syby119/Desktop/human_scene.mb"
    cmds.file(character_filepath, open=True, force=True)
    
    # get clothes file paths
    clothes_dir = "C:/Users/syby119/Desktop/cloth"
    clothes_filepaths = []
    for (root, dirs, files) in os.walk(clothes_dir):
        for filename in files:
            clothes_filepaths.append(os.path.join(root, filename))
    
    renderer = ArnoldRenderer()
    
    # render options
    renderer.set_camera("renderCamera")
    renderer.set_antialising_samples(4)
    renderer.set_diffuse_samples(3)
    renderer.set_specular_samples(3)
    renderer.set_subsurface_scattering_samples(3)
    renderer.set_transmission_samples(3)
    renderer.set_volume_indirect_samples(3)
    
    # output options
    output_dir = "C:/Users/syby119/Desktop/save-zhijiang"
    image_base_name = "image"
    image_format = "tif"
    # image_format = "png"
    image_width = 540
    image_height = 960
    image_start_index = 30
    image_zero_padding = 4
    fps = "30fps"

    # create the output directory
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    renderer.set_image_size(image_width, image_height)
    renderer.set_image_format(image_format)
    renderer.set_fps(fps)
        
    # render process
    start_frame, end_frame = 264, 265
    end_frame = min(end_frame, start_frame + len(clothes_filepaths) - 1)

    renderer.print_settings()
    
    for frame in range(start_frame, end_frame + 1):
        start_time = time.time()
        
        # import cloth
        # we assume that
        # + the cloth has its own material
        namespace = "cloth_scene" + str(frame - start_frame)
        cmds.file(clothes_filepaths[frame - start_frame], i=True, namespace=namespace)
        
        #render
        filename = image_base_name + str(frame + image_start_index).zfill(image_zero_padding) + "." + image_format
        filepath = os.path.join(output_dir, filename)
        renderer.render(frame, filepath)
        # renderer.renderInRenderView(frame, filepath)
        
        print(filepath)
        
        # clear objects in the cloth
        cloth_scene_objects = []
        for object in cmds.ls("%s:*" % namespace):
            cloth_scene_objects.append(object)
        for object in cmds.ls("%s:*:*" % namespace):
            cloth_scene_objects.append(object)
        for object in cloth_scene_objects:
            try:
                cmds.delete(object)
            except:
                pass
        
        duration = time.time() - start_time
        print("time for frame %d: %f s, remaining time: %f s" % (frame, duration, duration * (end_frame - frame)))