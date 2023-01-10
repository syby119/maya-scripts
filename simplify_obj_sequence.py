# @author: Yun Yang
# @description: 
#   This script simplifies all obj files in the specified directory by 
#   + omitting normal information
#   + omitting texture coordinates information
#   Besides, the script can modifiy the output obj to fit the simulation pipeline by
#   + changing the up direction from +y to +z
#   + scale the size for unit transformation


import os


def process_obj(input_file, compress=True, change_up_direction=False, scale=1.0):
    """
    @description: read the obj file and process
    @usage: process_obj("C:/Users/syby119/Desktop/body0000.obj")
    @param input_file: the obj file to be processed
    @param compress: whether to minimize the obj file
    @param change_up_direction: whether to change the up direction from +y to +z
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
                if (change_up_direction):
                    x, y, z = -x, z, y
                if (scale != 1.0):
                    x, y, z = scale * x, scale * y, scale * z
                new_lines.append("v %f %f %f\n" % (x, y, z))
            if line.startswith("f "):
                if compress:
                    new_line = "f"
                    results = line[2: ].split()
                    for result in results:
                        new_line += " " + result.split("/")[0]
                    new_lines.append(new_line + '\n')
                else:
                    new_lines.append(line)
    return new_lines


def save_obj(output_file, new_lines):
    """
    @description: save the obj file
    @usage: save_obj("C:/Users/syby119/Desktop/body0000.obj")
    @param output_file: the obj file to be saved
    """
    with open(output_file, "w+") as fp:
        fp.writelines(new_lines)


if __name__ == '__main__':
    workdir = "C:/Users/syby119/Desktop/body"
    outputdir = "C:/Users/syby119/Desktop/body"

    options = {
        "compress": True,
        "change_up_direction": True,
        "scale": 0.01
    }

    if not os.path.exists(outputdir):
        os.mkdir(outputdir)

    for root, dirs, files in os.walk(workdir):
        for file in files:
            filepath = os.path.join(root, file)
            new_lines = process_obj(
                filepath, 
                options["compress"],
                options["change_up_direction"],
                options["scale"])

            save_obj(os.path.join(outputdir, file), new_lines)
            
            print("save " + file + " to " + outputdir)