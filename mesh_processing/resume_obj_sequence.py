# @author: Yun Yang
# @description: 
#   This script resumes all simulated obj files by
#   + change the up direction from +z to +y
#   + scale the model size to match the unit


import os


def process_obj(input_file, change_yz=False, scale=1.0):
    """
    @description: read the obj file and process
    @usage: process_obj("C:/Users/syby119/Desktop/cloth0000.obj")
    @param input_file: the obj file to be processed
    @param change_yz: whether to change the up direction from +z to +y
    @param scale: scale rate of the model size
    @return: processed lines
    """
    new_lines = []
    with open(input_file, "r") as fp:
        while True:
            line = fp.readline()
            if not line:
                break
            if line.startswith("v "):
                results = line[2: ].split()
                x, y, z = float(results[0]), float(results[1]), float(results[2])
                if (change_yz):
                    x, y, z = -x, z, y
                if (scale != 1.0):
                    x, y, z = scale * x, scale * y, scale * z
                new_lines.append("v %f %f %f\n" % (x, y, z))
            else:
                new_lines.append(line)
    return new_lines


def save_obj(output_file, new_lines):
    """
    @description: save the obj file
    @usage: save_obj("C:/Users/syby119/Desktop/cloth0000.obj")
    @param output_file: the obj file to be saved
    """
    with open(output_file, "w+") as fp:
        fp.writelines(new_lines)


if __name__ == '__main__':
    workdir = "C:/Users/syby119/Desktop/out-hires"
    outputdir = "C:/Users/syby119/Desktop/resume-cloth"

    options = {
        "change_xy": True,
        "scale": 100
    }

    if not os.path.exists(outputdir):
        os.mkdir(outputdir)

    for root, dirs, files in os.walk(workdir):
        for file in files:
            filepath = os.path.join(root, file)
            new_lines = process_obj(
                filepath, 
                options["change_xy"],
                options["scale"])

            save_obj(os.path.join(outputdir, file), new_lines)
            
            print("save " + file + " to " + outputdir)