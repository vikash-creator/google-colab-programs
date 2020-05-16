import glob
import sys
from multiprocessing import Process

# ../../Carla0.9.6/PythonAPI/carla/dist/carla-*%d.%d-%s.egg
# ../carla/dist/carla-*%d.%d-%s.egg
# Verwendung einex expliziten Pfades suboptimal.
# python3 muss jetzt verwendet werden.
try:
    sys.path.append(glob.glob(
        '/opt/carla/PythonAPI/carla/dist/carla-0.9.8-py3.5-linux-x86_64.egg')[0])
except IndexError:
    pass


# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================


import carla
import random
import time
import numpy as np
import cv2

def func1():
    while(True):
        print("hello.......11111111")

def func2():
    while(True):
        print("hello.......22222222")

if __name__=='__main__':
     p1 = Process(target = func1)
     p1.start()
     p2 = Process(target = func2)
     p2.start()