# @author: Yun Yang
# @prerequite: Maya 2018
# @description: 
#   This script assemble scenes for background rendering.
#   It initializes the following object with scene_config.json
#   + cloth materials
#   + camera
#   + lights
#   + ground
#   Then it assembles scenes for each frame by
#   + import the body obj file
#   + import the cloth obj file
#   + assign new material to the cloth
#   + move camera if needed
#   + save the result
#   + clean up the imported models
#   The result will be .mb files for each frame


from __future__ import print_function
import maya.cmds as cmds
import maya.mel as mel
import os
import json


def createRampNodeAsTexture(ramp):
    """
    @description:
        create ramp node with a image file
    @param ramp: image file path
    @return ramp node in Maya
    """
    rampNode = cmds.shadingNode("ramp", asTexture=True, isColorManaged=True)
    place2dTextureNode = cmds.shadingNode("place2dTexture", asUtility=True)
    cmds.connectAttr("%s.%s"%(place2dTextureNode, "outUV"), "%s.%s"%(rampNode, "uvCoord"))
    cmds.connectAttr("%s.%s"%(place2dTextureNode, "outUvFilterSize"), "%s.%s"%(rampNode, "uvFilterSize"))
    return rampNode


def createFileNodeAsTexture(srcImage):
    # create a file node in maya
    fileNode = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
    cmds.setAttr("%s.%s"%(fileNode, "fileTextureName"), srcImage, type="string")
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


def createLambertMaterial(config):
    """
    @description:
        create lambert material node in Maya by the config
    @param config: config dict for the material including the following optional field
        + color: [double, double, double]
        + transparency: [double, double, double]
        + ambientColor: [double, double, double]
        + bumpMapping: filepath
        + diffuse: double
        + translucence: double
        + translucenceDepth: double
        + translucenceFocus: double
    @return: lambert material
    """
    shader = cmds.shadingNode("lambert", asShader=True)
    if config.get("color"):
        color = config["color"]
        cmds.setAttr("%s.%s"%(shader, "color"), color[0], color[1], color[2], type="double3")
    if config.get("transparency"):
        cmds.setAttr("%s.%s"%(shader, "transparency"), *config["transparency"], type="double3")
    if config.get("ambientColor"):
        cmds.setAttr("%s.%s"%(shader, "ambientColor"), *config["ambientColor"], type="double3")
    if config.get("incandescence"):
        cmds.setAttr("%s.%s"%(shader, "incandescence"), *config["incandescence"], type="double3")
    if config.get("bumpMapping"):
        bumpMappingFileNode = createFileNodeAsTexture(config["bumpMapping"])
        bump2dNode = cmds.shadingNode("bump2d", asTexture=True)
        cmds.setAttr("%s.%s"%(bump2dNode, "aiFlipG"), False)
        cmds.setAttr("%s.%s"%(bump2dNode, "aiFlipR"), False)
        cmds.setAttr("%s.%s"%(bump2dNode, "bumpInterp"), 1)
        # connect nodes
        cmds.connectAttr("%s.%s"%(bumpMappingFileNode, "outAlpha"), "%s.%s"%(bump2dNode, "bumpValue"))
        cmds.connectAttr("%s.%s"%(bump2dNode, "outNormal"), "%s.%s"%(shader, "normalCamera"))
    if config.get("diffuse"):
        cmds.setAttr("%s.%s"%(shader, "diffuse"), config["diffuse"])
    if config.get("translucence"):
        cmds.setAttr("%s.%s"%(shader, "translucence"), config["translucence"])
    if config.get("translucenceDepth"):
        cmds.setAttr("%s.%s"%(shader, "translucenceDepth"), config["translucenceDepth"])
    if config.get("translucenceFocus"):
        cmds.setAttr("%s.%s"%(shader, "translucenceFocus"), config["translucenceFocus"])

    return shader


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
                baseColorFileNode = createFileNodeAsTexture(base["color"])
                cmds.connectAttr("%s.%s"%(baseColorFileNode, "outColor"), "%s.%s"%(shader, "baseColor"))
        if base.get("diffuseRoughness"):
            cmds.setAttr("%s.%s"%(shader, "diffuseRoughness"), base["diffuseRoughness"])
        if base.get("metalness"):
            if isinstance(base["metalness"], float) or isinstance(base["metalness"], int):
                cmds.setAttr("%s.%s"%(shader, "metalness"), base["metalness"])
            else:
                metalnessFileNode = createFileNodeAsTexture(base["metalness"])
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
                specularRoughnessFileNode = createFileNodeAsTexture(specular["roughness"])
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
                transmissionColorFileNode = createFileNodeAsTexture(transmission["color"])
                cmds.connectAttr("%s.%s"%(transmissionColorFileNode, "outColor"), "%s.%s"%(shader, "transmissionColor"))
        if transmission.get("depth"):
            cmds.setAttr("%s.%s"%(shader, "transmissionDepth"), transmission["depth"])
        if transmission.get("scatter"):
            if isinstance(transmission["scatter"], tuple) or isinstance(transmission["scatter"], list):
                cmds.setAttr("%s.%s"%(shader, "transmissionScatter"), *transmission["scatter"], type="double3")
            else:
                transmissionScatterFileNode = createFileNodeAsTexture(transmission["scatter"])
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
                subsurfaceColorFileNode = createFileNodeAsTexture(subsurface["color"])
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
            geometryBumpMappingFileNode = createFileNodeAsTexture(geometry["bumpMapping"])
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


if __name__ == "__main__":
    config_path = "E:/cloth_render/andy_tshirt/scene_config.json"

    cmds.file(new=True, force=True)

    print("\n################### Config ###################")
    # get configuration from file
    with open(config_path, "r") as f:
        config = json.load(f)
        print(json.dumps(config, indent=2))

    print("\n############# Prepare Utilities ##############")
    # create ground to cast shadow for reality
    if (config.get("ground")):
        print("create ground")
        ground, _ = cmds.polyPlane(name="ground", height=10e9, width=10e9)
        # rotate
        cmds.setAttr("%s.%s"%(ground, "rotate"), *config["ground"].get("rotate", [0.0, 0.0, 0.0]), type="double3")
        # translate
        cmds.setAttr("%s.%s"%(ground, "translate"), *config["ground"].get("translate", [0.0, 0.0, 0.0]), type="double3")
        # material
        groundMtl = config["ground"].get("material")
        if groundMtl and groundMtl.get("type"):
            if groundMtl["type"] == "aiStandardSurface":
                groundMtl = createAiStandardSurfaceMaterial(groundMtl)
                assignMaterial(ground, groundMtl)
            elif groundMtl["type"] == "lambert":
                groundMtl = createLambertMaterial(groundMtl)
                assignMaterial(ground, groundMtl)
            
    # create a camera for render
    print("create camera")
    camera, cameraShape = cmds.camera(name="mainCamera")
    if config["camera"].get("focalLength"):
        cmds.setAttr("%s.%s"%(cameraShape, "focalLength"), config["camera"]["focalLength"])
    if config["camera"].get("translate"):
        cmds.setAttr("%s.%s"%(camera, "translate"), *config["camera"]["translate"], type="double3")
    if config["camera"].get("rotate"):
        cmds.setAttr("%s.%s"%(camera, "rotate"), *config["camera"]["rotate"], type="double3")

    for cam in cmds.ls(type="camera"):
        if cam != cameraShape:
            cmds.setAttr("%s.%s"%(cam, "renderable"), False)
    cmds.setAttr("%s.%s"%(cameraShape, "renderable"), True)

    # create arnold lights
    print("create lights")
    lights = []
    for i in range(len(config["lights"])):
        if config["lights"][i]["type"] == "areaLight":
            lightShape = cmds.createNode("aiAreaLight")
        elif config["lights"][i]["type"] == "skyDomeLight":
            lightShape = cmds.createNode("aiSkyDomeLight")
        else:
            print("warning: unsupported light shape")
            continue

        light = cmds.listRelatives(lightShape, parent=True)[0]

        if config["lights"][i].get("translate"):
            cmds.setAttr("%s.%s"%(light, "translate"), *config["lights"][i]["translate"], type="double3")
        if config["lights"][i].get("rotate"):
            cmds.setAttr("%s.%s"%(light, "rotate"), *config["lights"][i]["rotate"], type="double3")
        if config["lights"][i].get("scale"):
            cmds.setAttr("%s.%s"%(light, "scale"), *config["lights"][i]["scale"], type="double3")
        if config["lights"][i].get("intensity"):
            cmds.setAttr("%s.%s"%(lightShape, "intensity"), config["lights"][i]["intensity"])
        if config["lights"][i].get("exposure"):
            cmds.setAttr("%s.%s"%(lightShape, "exposure"), config["lights"][i]["exposure"])
        if config["lights"][i].get("color"):
            if isinstance(config["lights"][i]["color"], list) or isinstance(config["lights"][i]["color"], tuple):
                cmds.setAttr("%s.%s"%(lightShape, "color"), *config["lights"][i]["color"], type="double3")
            else:
                if config["lights"][i]["color"] == "ramp":
                    node = createRampNodeAsTexture(config["lights"][i]["color"])
                else:
                    node = createFileNodeAsTexture(config["lights"][i]["color"])
                cmds.connectAttr("%s.%s"%(node, "outColor"), "%s.%s"%(lightShape, "color"))
                    
        cmds.sets(light, forceElement="defaultLightSet")

        lights.append(light)

    # create material for clothes
    if config.get("clothes"):
        clothMtls = []
        print("create materials for clothes")
        for i in range(len(config["clothes"])):
            if config["clothes"][i]["material"]["type"] == "aiStandardSurface":
                clothMtl = createAiStandardSurfaceMaterial(config["clothes"][i]["material"])
            elif config["clothes"][i]["material"]["type"] == "lambert":
                clothMtl = createLambertMaterial(config["clothes"][i]["material"])
            else:
                clothMtl = createLambertMaterial()
            clothMtls.append(clothMtl)

    # create material for obstacles
    if config.get("obstacles"):
        obstacleMtls = []
        print("create materials for obstacles")
        for i in range(len(config["obstacles"])):
            if config["obstacles"][i]["material"]["type"] == "aiStandardSurface":
                obstacleMtl = createAiStandardSurfaceMaterial(config["obstacles"][i]["material"])
            elif config["obstacles"][i]["material"]["type"] == "lambert":
                obstacleMtl = createLambertMaterial(config["obstacles"][i]["material"])
            else:
                obstacleMtl = createLambertMaterial()
            obstacleMtls.append(obstacleMtl)

    # initialize for render settings
    mel.eval('unifiedRenderGlobalsWindow')
    mel.eval('workspaceControl -e -vis 0 unifiedRenderGlobalsWindow')
    # cmds.colorManagementPrefs(e=True, outputTransformEnabled=True)
    # cmds.colorManagementPrefs(e=True, outputTransformName='sRGB gamma')
    # mel.eval('savePrefsChanges')

    print("\n############# Assembling Scenes ##############")
    # create directory for result if needed
    if not os.path.exists(config["setting"]["result"]):
        print(config["setting"]["result"])
        os.mkdir(config["setting"]["result"])

    startFrame, endFrame = 100000000, -1

    # find prefix and suffix for obstacles
    if config.get("obstacles"):
        obstaclePrefixes = []
        obstacleSuffixes = []
        for i in range(len(config["obstacles"])):
            filenames = os.listdir(config["obstacles"][i]["path"])
            obstaclePrefix = filenames[0]
            obstacleSuffix = filenames[0]
            for name in filenames:
                common = ""
                for j in range(min(len(obstaclePrefix), len(name))): 
                    if obstaclePrefix[j] == name[j]:
                        common += obstaclePrefix[j]
                    else:
                        break
                obstaclePrefix = common

                common = ""
                for j in range(-1, -min(len(obstacleSuffix), len(name)) - 1, -1):
                    if obstacleSuffix[j] == name[j]:
                        common = obstacleSuffix[j] + common
                    else:
                        break
                obstacleSuffix = common
            obstaclePrefixes.append(obstaclePrefix)
            obstacleSuffixes.append(obstacleSuffix)
            print("obstacle prefix: ", obstaclePrefix, " suffix: ", obstacleSuffix)

            for name in filenames:
                frame = int(name[len(obstaclePrefixes[i]): -len(obstacleSuffixes[i])])
                startFrame = min(startFrame, frame)
                endFrame = max(endFrame, frame)

    # find prefix and suffix for clothes
    if config.get("clothes"):
        clothPrefixes = []
        clothSuffixes = []
        for i in range(len(config["clothes"])):
            filenames = os.listdir(config["clothes"][i]["path"])
            clothPrefix = filenames[0]
            clothSuffix = filenames[0]
            for name in filenames:
                common = ""
                for j in range(min(len(clothPrefix), len(name))): 
                    if clothPrefix[j] == name[j]:
                        common += clothPrefix[j]
                    else:
                        break
                clothPrefix = common

                common = ""
                for j in range(-1, -min(len(clothSuffix), len(name)) -1, -1):
                    if clothSuffix[j] == name[j]:
                        common = clothSuffix[j] + common
                    else:
                        break
                clothSuffix = common

            clothPrefixes.append(clothPrefix)
            clothSuffixes.append(clothSuffix)
            print("cloth prefix: ", clothPrefix, " suffix: ", clothSuffix)
            for name in filenames:
                frame = int(name[len(clothPrefixes[i]): -len(clothSuffixes[i])])
                startFrame = min(startFrame, frame)
                endFrame = max(endFrame, frame)


    step = 1
    if config.get("setting"):
        step = config["setting"].get("step", 1)

    print("start frame: ", startFrame, " end frame: ", endFrame, "step: ", step)

    cmds.setAttr("defaultArnoldDriver.colorManagement", 1)
    cmds.setAttr("defaultRenderGlobals.imageFormat", 32)

    if config.get("setting"):
        if cmds.ls("defaultArnoldRenderOptions") and config["setting"].get("sample"):
            cmds.setAttr("defaultArnoldRenderOptions.AASamples", config["setting"]["sample"].get("camera", 4))
            cmds.setAttr("defaultArnoldRenderOptions.GIDiffuseSamples", config["setting"]["sample"].get("diffuse", 3))
            cmds.setAttr("defaultArnoldRenderOptions.GISpecularSamples", config["setting"]["sample"].get("specular", 2))
            cmds.setAttr("defaultArnoldRenderOptions.GITransmissionSamples", config["setting"]["sample"].get("transmission", 2))
            cmds.setAttr("defaultArnoldRenderOptions.GISssSamples", config["setting"]["sample"].get("sss", 2))
            cmds.setAttr("defaultArnoldRenderOptions.GIVolumeSamples", config["setting"]["sample"].get("volumeIndirect", 2))

        if config["setting"].get("resolution"):
            cmds.setAttr("defaultResolution.width", config["setting"]["resolution"]["width"])
            cmds.setAttr("defaultResolution.height", config["setting"]["resolution"]["height"])
            cmds.setAttr("defaultResolution.pixelAspect", 1.0)
            cmds.setAttr("defaultResolution.deviceAspectRatio", 1.0 * config["setting"]["resolution"]["width"] / config["setting"]["resolution"]["height"])

    for frame in range(startFrame, endFrame + 1, step):
        # delete cloth and pose object
        allObjects = cmds.ls(long=True, transforms=True)
        for obj in allObjects:
            if cmds.listRelatives(obj, children = True, type = "mesh"):
                if obj.find(ground) == -1:
                    cmds.delete(obj)

        # import cloth obj
        if config.get("clothes"):
            for i in range(len(config["clothes"])):
                fmt = r"%s" + r"%0" + "%dd"%(config["clothes"][i]["padding"]) + r"%s"
                clothPath = os.path.join(config["clothes"][i]["path"], fmt%(clothPrefixes[i], frame, clothSuffixes[i]))
                print(clothPath)
                cmds.file(clothPath, i=True, namespace="cloth_%d_%d"%(frame, i))
                cmds.select("cloth_%d_%d:*"%(frame, i))
                cloth, clothShape = cmds.ls(sl=True)
                assignMaterial(cloth, clothMtls[i])
                if config["clothes"][i]["subdivision"]:
                    cmds.setAttr("%s.%s"%(clothShape, "aiSubdivType"), 1)
                    cmds.setAttr("%s.%s"%(clothShape, "aiSubdivIterations"), 2)
                
        # import obstacle obj
        if config.get("obstacles"):
            for i in range(len(config["obstacles"])):
                fmt = r"%s" + r"%0" + "%dd"%(config["obstacles"][i]["padding"]) + r"%s"
                obstaclePath = os.path.join(config["obstacles"][i]["path"], fmt%(obstaclePrefixes[i], frame, obstacleSuffixes[i]))
                print(obstaclePath)
                cmds.file(obstaclePath, i=True, namespace="obstacle_%d_%d"%(frame, i))
                cmds.select("obstacle_%d_%d:*"%(frame, i))
                obstacle, obstacleShape = cmds.ls(sl=True)
                assignMaterial(obstacle, obstacleMtls[i])
                if config["obstacles"][i]["material"]["type"] == "lambert":
                    transparency = config["obstacles"][i]["material"].get("transparency", [0.0, 0.0, 0.0])
                    if transparency != [0.0, 0.0, 0.0]:
                        cmds.setAttr("%s.%s"%(obstacleShape, "aiOpaque"), 0)
                if config["obstacles"][i]["subdivision"]:
                    cmds.setAttr("%s.%s"%(obstacleShape, "aiSubdivType"), 1)
                    cmds.setAttr("%s.%s"%(obstacleShape, "aiSubdivIterations"), 2)

        mel.eval('hyperShadePanelMenuCommand(`getFocusedHypershade`, "deleteUnusedNodes")')
        
        # set camera attributes
        if config["camera"].get("followObstacle") and config["camera"]["followObstacle"] == True:
            cameraPos = cmds.getAttr("%s.%s"%(obstacle, "center"))
            for i in range(3):
                cameraPos[i] += config["camera"]["translate"][i]
            cmds.setAttr("%s.%s"%(camera, "translate"), *cameraPos[0], type="double3")
            cmds.setAttr("%s.%s"%(cameraShape, "displayCameraNearClip"), True)
            cmds.setAttr("%s.%s"%(cameraShape, "displayCameraFarClip"), True)
            cmds.setAttr("%s.%s"%(cameraShape, "displayCameraFrustum"), True)

        # set light positions
        for i in range(len(lights)):
            if config["lights"][i].get("followObstacle") and config["lights"][i]["followObstacle"] == True:
                lightTranslate = cmds.getAttr("%s.%s"%(obstacle, "center"))
                for j in range(3):
                    lightTranslate[j] += config["lights"][i]["translate"][j]
                cmds.setAttr("%s.%s"%(lights[i], "translate"), *lightTranslate, type="double3")

        # save scene as i.mb
        filename = os.path.join(config["setting"]["result"], "%04d.mb"%(int)((frame - startFrame) / step))
        cmds.file(rename=filename)
        cmds.file(save=True)
        print("save scene: ", filename)