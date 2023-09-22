# @author: Yun Yang
# @prerequite: Arnold Renderer
# @description: 
#   This script renders each scene in the background and output the image sequence
from tqdm import tqdm
import threading

import os
import time


class suppress_stdout_stderr(object):
    '''
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).

    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])



if __name__ == "__main__":

    # specify parameter

    RenderingSeetting = os.path.join(os.path.abspath(__file__), "RenderingSetting.json")
    specifyCamera = None
    # how many DRAM you have set it to 8 if you have 16G DRAM
    parallelThreadNum =  8


    dataDir = os.path.dirname(os.path.abspath(__file__))
    dataDir = "C:/Users/87979/Desktop/NerualCloth/codes/VirtualBones/out"
    base = os.path.join(dataDir, "mayaTMP")
    target = os.path.join(dataDir, "outPicture")

    if not os.path.exists(target):
        os.mkdir(target)

    exe = "D:/software/maya/Maya2022/bin/Render.exe"
    imageFormat = "png"
    renderer = "arnold"
    namingConvention = 1

    for root, ds, fs in os.walk(base):
        fsLen = len(fs)
        tasks = range(len(fs))
        subarrays = []
        for i in range(0, len(fs), parallelThreadNum):
            subarray = list(range(i, min(i + parallelThreadNum, len(fs))))
            subarrays.append(subarray)
        
        # create cmds
        cmds = []
        for f in fs:
            scene = os.path.join(base, f)
            saveName = f.split(".")[0]
            cmd = '%s -s 1 -e 1 -r arnold -rd %s -im %s -fnc %d -of %s'\
                   %(exe, target, saveName, namingConvention, imageFormat)
            if RenderingSeetting is not None:
                cmd += ' -rsp %s' % (RenderingSeetting) 
            if specifyCamera is not None:
                cmd += ' -cam %s'% (specifyCamera)
            cmd += ' %s' % (scene)
            cmds.append(cmd)

        def renderingOne(cmd):
            global pbar
            #with suppress_stdout_stderr():
            os.system(cmd)
            pbar.update(1)

        with tqdm(total=len(tasks)) as pbar:
            threads = []
            for arr in subarrays:
                for i in arr:
                    thread = threading.Thread(target=renderingOne, args=(cmds[i],))
                    thread.start()
                    time.sleep(1)
                    threads.append(thread)
                
                for thread in threads:
                    thread.join()

