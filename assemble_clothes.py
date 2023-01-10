# @author: Yun Yang
# @prerequite: Maya 2022
# @description: 
#   This script process cloth models by
#   + assemble different parts of the cloth with the same frame index into one cloth file
#   + create materials for each cloth parts
#   + save the result as .mb file
# The above process works for each cloth part obj in the specified directory


import os
import re
import maya.cmds as cmds


def create_texture_file_node(image_filepath:str):
    """
    @description: 
        create texture file node in Maya from the image file 
    @usage: create_texture_file_node("C:/Users/syby119/Desktop/img.png")
    @param image_filepath: the full path of the image file
    @return: maya texture file node
    """
    fileNode = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
    cmds.setAttr("%s.%s"%(fileNode, "fileTextureName"), image_filepath, type="string")
    place2dTextureNode = cmds.shadingNode("place2dTexture", asUtility=True)
    attributes = ["coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV", 
                  "stagger", "wrapU", "wrapV", "repeatUV", "offset", "rotateUV", "noiseUV", 
                  "vertexUvOne", "vertexUvTwo", "vertexUvThree", 
                  "vertexCameraOne", "outUV", "outUvFilterSize"]
    for attr in attributes:
        attrOut = attr
        attrIn = attr
        if attr.startswith("out"):
            attrIn = attr[3:5].lower() + attr[5:]
        cmds.connectAttr("%s.%s"%(place2dTextureNode, attrOut), "%s.%s"%(fileNode, attrIn), force=True)
    
    return fileNode


def createAiStandardSurfaceMaterial(config):
    """
    @description:
        create aiStandardSurface material node in Maya by the config
    @param config: config dict for the material including the following optional field
        + base
            + weight: double
            + color: [double, double, double] / filepath
            + diffuseRoughness: double
            + metalness: double / filepath
        + specular
            + weight: double
            + color: [double, double, double] / filepath
            + roughness: double / filepath
            + IOR: double
            + anisotropy: double
            + rotation: double
        + transmission
            + weight: double
            + color: [double, double, double] / filepath
            + depth: double
            + scatter: [double, double, double] / filepath
            + scatterAnisotropy: double
            + dispersionAbbe: double
            + extraRoughness: double
        + subsurface
            + weight: double
            + color: [double, double, double] / filepath
            + radius: double
            + scale: double
        + geometry
            + thinWalled: double
            + opacity: double
            + bumpMapping: filepath
            + anisotropyTangent: [double, double, double]
    @return: aiStandardSurface material
    """
    # create aiStandardSurface
    shader = cmds.shadingNode("aiStandardSurface", asShader=True)
    # base
    if config.get("base"):
        base = config["base"]
        if base.get("weight"):
            cmds.setAttr("%s.%s"%(shader, "base"), base["weight"])
        if base.get("color"):
            if isinstance(base["color"], tuple) or isinstance(base["color"], list):
                cmds.setAttr("%s.%s"%(shader, "baseColor"), *base["color"], type="double3")
            else:
                baseColorFileNode = create_texture_file_node(base["color"])
                cmds.connectAttr("%s.%s"%(baseColorFileNode, "outColor"), "%s.%s"%(shader, "baseColor"))
        if base.get("diffuseRoughness"):
            cmds.setAttr("%s.%s"%(shader, "diffuseRoughness"), base["diffuseRoughness"])
        if base.get("metalness"):
            if isinstance(base["metalness"], float) or isinstance(base["metalness"], int):
                cmds.setAttr("%s.%s"%(shader, "metalness"), base["metalness"])
            else:
                metalnessFileNode = create_texture_file_node(base["metalness"])
                cmds.setAttr("%s.%s"%(metalnessFileNode, "colorSpace"), "Raw", type="string")
                cmds.setAttr("%s.%s"%(metalnessFileNode, "alphaIsLuminance"), True)
                cmds.connectAttr("%s.%s"%(metalnessFileNode, "outAlpha"), "%s.%s"%(shader, "metalness"))
    # specular
    if config.get("specular"):
        specular = config["specular"]
        if specular.get("weight"):
            cmds.setAttr("%s.%s"%(shader, "specular"), specular["weight"])
        if specular.get("color"):
            cmds.setAttr("%s.%s"%(shader, "specularColor"), *specular["color"], type="double3")
        if specular.get("roughness"):
            if isinstance(specular["roughness"], float) or isinstance(specular["roughness"], int):
                cmds.setAttr("%s.%s"%(shader, "specularRoughness"), specular["roughness"])
            else:
                specularRoughnessFileNode = create_texture_file_node(specular["roughness"])
                cmds.setAttr("%s.%s"%(specularRoughnessFileNode, "colorSpace"), "Raw", type="string")
                cmds.setAttr("%s.%s"%(specularRoughnessFileNode, "alphaIsLuminance"), True)
                cmds.connectAttr("%s.%s"%(specularRoughnessFileNode, "outAlpha"), "%s.%s"%(shader, "specularRoughness"))
        if specular.get("IOR"):
            cmds.setAttr("%s.%s"%(shader, "specularIOR"), specular["IOR"])
        if specular.get("anisotropy"):
            cmds.setAttr("%s.%s"%(shader, "specularAnisotropy"), specular["anisotropy"])
        if specular.get("rotation"):
            cmds.setAttr("%s.%s"%(shader, "specularRotation"), specular["rotation"])
    # transmission
    if config.get("transmission"):
        transmission = config["transmission"]
        if transmission.get("weight"):
            cmds.setAttr("%s.%s"%(shader, "transmission"), transmission["weight"])
        if transmission.get("color"):
            transmissionColor = transmission["color"]
            if isinstance(transmission["color"], tuple) or isinstance(transmission["color"], list):
                cmds.setAttr("%s.%s"%(shader, "transmissionColor"), *transmission["color"], type="double3")
            else:
                transmissionColorFileNode = create_texture_file_node(transmission["color"])
                cmds.connectAttr("%s.%s"%(transmissionColorFileNode, "outColor"), "%s.%s"%(shader, "transmissionColor"))
        if transmission.get("depth"):
            cmds.setAttr("%s.%s"%(shader, "transmissionDepth"), transmission["depth"])
        if transmission.get("scatter"):
            if isinstance(transmission["scatter"], tuple) or isinstance(transmission["scatter"], list):
                cmds.setAttr("%s.%s"%(shader, "transmissionScatter"), *transmission["scatter"], type="double3")
            else:
                transmissionScatterFileNode = create_texture_file_node(transmission["scatter"])
                cmds.connectAttr("%s.%s"%(transmissionScatterFileNode, "outColor"), "%s.%s"%(shader, "transmissionScatter"))
        if transmission.get("scatterAnisotropy"):
            cmds.setAttr("%s.%s"%(shader, "transmissionScatterAnisotropy"), transmission["scatterAnisotropy"])
        if transmission.get("dispersionAbbe"):
            cmds.setAttr("%s.%s"%(shader, "transmissionDispersion"), transmission["dispersionAbbe"])
        if transmission.get("extraRoughness"):
            cmds.setAttr("%s.%s"%(shader, "transmissionExtraRoughness"), transmission["extraRoughness"])
    # subsurface
    if config.get("subsurface"):
        subsurface = config["subsurface"]
        if subsurface.get("weight"):
            cmds.setAttr("%s.%s"%(shader, "subsurface"), subsurface["weight"])
        if subsurface.get("color"):
            if isinstance(subsurface["color"], tuple) or isinstance(subsurface["color"], list):
                cmds.setAttr("%s.%s"%(shader, "subsurfaceColor"), *subsurface["color"], type="double3")
            else:
                subsurfaceColorFileNode = create_texture_file_node(subsurface["color"])
                cmds.connectAttr("%s.%s"%(subsurfaceColorFileNode, "outColor"), "%s.%s"%(shader, "subsurfaceColor"))
        if subsurface.get("radius"):
            cmds.setAttr("%s.%s"%(shader, "subsurfaceRadius"), *subsurface["radius"], type="double3")
        if subsurface.get("scale"):
            cmds.setAttr("%s.%s"%(shader, "subsurfaceScale"), subsurface["scale"])
    # geometry
    if config.get("geometry"):
        geometry = config["geometry"]
        if geometry.get("thinWalled"):
            cmds.setAttr("%s.%s"%(shader, "thinWalled"), geometry["thinWalled"])
        if geometry.get("opacity"):
            cmds.setAttr("%s.%s"%(shader, "opacity"), *geometry["opacity"], type="double3")
        if geometry.get("bumpMapping"):
            geometryBumpMappingFileNode = create_texture_file_node(geometry["bumpMapping"])
            bump2dNode = cmds.shadingNode("bump2d", asTexture=True)
            cmds.setAttr("%s.%s"%(bump2dNode, "aiFlipG"), False)
            cmds.setAttr("%s.%s"%(bump2dNode, "aiFlipR"), False)
            cmds.setAttr("%s.%s"%(bump2dNode, "bumpInterp"), 1)
            cmds.connectAttr("%s.%s"%(geometryBumpMappingFileNode, "outAlpha"), "%s.%s"%(bump2dNode, "bumpValue"))
            cmds.connectAttr("%s.%s"%(bump2dNode, "outNormal"), "%s.%s"%(shader, "normalCamera"))
        if geometry.get("anisotropyTangent"):
            cmds.setAttr("%s.%s"%(shader, "tangent"), *geometry["anisotropyTangent"], type="double3")

    return shader


def assignMaterial(obj: str, material: str):
    """
    @description:
        assign the material to the object
    @param obj: object name
    @param material: material node name
    """
    cmds.select(obj)
    cmds.hyperShade(assign=material)
    cmds.select(cl=True)
    
    
def process_cloth(input_dir:str, filename:str, material:str):
    """
    @description:
        import the cloth obj file and assign materials to it
    @param input_dir: directory of the cloth
    @param file: cloth file name
    @param material: material node name
    """
    namespace = filename.split(".")[0]
    cmds.file(os.path.join(input_dir, filename), i=True, namespace=namespace)
    
    clothShape = cmds.ls("%s:*" % namespace, exactType="mesh")[0]
    cloth = cmds.listRelatives(clothShape, parent=True)
        
    assignMaterial(cloth, material)
    cmds.setAttr("%s.%s"%(clothShape, "aiSubdivType"), 1)
    cmds.setAttr("%s.%s"%(clothShape, "aiSubdivIterations"), 2)


def get_meta_info(input_dir:str):
    """
    @description: 
        get meta info of the file in the input directory
        format of the cloth file is assumed to be
        [prefix_str][frame_number][_][part_number].obj
        the digits of frame_number and part_number in different file must be the same 
        + cloth021_01.obj
        + cloth021_01.obj
        + cloth021.obj
        + 021_01.obj
        + 021.obj
    @usage get_meta_info("C:/Users/syby119/Desktop/clothes")
    @param input_dir: input directory containing multiple cloth files
    @return: meta info of the cloth file including
        + start_frame
        + end_frame
        + parts
        + format string
    """
    start_frame, end_frame = 9999999, -9999999
    parts = 0
    for (root, dirs, files) in os.walk(input_dir):
        for file in files:
            ret = file.split("_")
            frame_number_start_index = re.search(r"\d", file).start()
            prefix_str = file[:frame_number_start_index]
            if len(ret) == 2:
                frame_str = ret[0][frame_number_start_index:]
                part_str = ret[1].split(".")[0]
                frame = int(frame_str)
                part = int(part_str) + 1
                format = prefix_str + "%0" + str(len(frame_str)) + "d_%0" + str(len(part_str)) + "d.obj"
            elif len(ret) == 1:
                frame_str = file.split(".")[0][frame_number_start_index:]
                frame = int(frame_str)
                part = 0
                format = prefix_str + "%0" + str(len(frame_str)) + "d.obj"
            else:
                raise ValueError("parse file format failure")
            
            parts = max(parts, part)
            start_frame = min(start_frame, frame)
            end_frame = max(end_frame, frame)
            
    return {
        "start_frame": start_frame,
        "end_frame": end_frame,
        "parts": parts,
        "format": format
    }


if __name__ == "__main__":
    input_dir = "C:/Users/syby119/Desktop/resume-cloth"
    output_dir = "C:/Users/syby119/Desktop/cloth"

    mtl_configs = {
        "red": {
            "base": {
                "weight": 1.0,
                "color": [0.237, 0.036, 0.011],
                "diffuseRoughness": 0.5,
                "metalness": 0.0
            },
            "specular": {
                "weight": 1.0,
                "color": [1.0, 1.0, 1.0],
                "roughness": 0.9, 
            }
        }, 
        "texture": {
            "base": {
                "weight": 1.0,
                "color": "C:/Users/syby119/Desktop/cloth_tex.png",
                "diffuseRoughness": 0.6,
                "metalness": 0.0
            },
            "specular": {
                "weight": 1.0,
                "color": [1.0, 1.0, 1.0],
                "roughness": 0.8, 
            }
        }
    }
    
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    cmds.file(new=True, force=True)
    
    cloth_materials = [
        # createAiStandardSurfaceMaterial(mtl_configs["red"]),
        createAiStandardSurfaceMaterial(mtl_configs["texture"])
    ]
    
    
    meta_info = get_meta_info(input_dir)
    print(meta_info)
    
    padding_digits = max(4, len(str(meta_info["end_frame"] - meta_info["start_frame"] + 1)))
    output_format = "cloth%0" + str(padding_digits) + "d.mb" 
    
    for frame in range(meta_info["start_frame"], meta_info["end_frame"] + 1):
        allObjects = cmds.ls(long=True, transforms=True)
        for obj in allObjects:
            if cmds.listRelatives(obj, children = True, type = "mesh"):
                cmds.delete(obj)
    
        if meta_info["parts"] == 0:
            filename = meta_info["format"] % (frame)
            process_cloth(input_dir, filename, cloth_materials[0])
            print(os.path.join(input_dir, filename))
        else: 
            for part in range(meta_info["parts"]):
                filename = meta_info["format"] % (frame, part)
                process_cloth(input_dir, filename, cloth_materials[part])
                print(os.path.join(input_dir, filename))
                
        filename = os.path.join(output_dir, output_format % (frame - meta_info["start_frame"]))
        cmds.file(rename=filename)
        cmds.file(save=True)
        print("save scene: ", filename)