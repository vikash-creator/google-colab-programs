# ===========================================================================================
# importing packages

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

import carla
import random
import time
import numpy as np
import cv2
import matplotlib.pyplot as mplt
import matplotlib.image as mimg

# ===========================================================================================
# variables and constants

runTime = 1

IM_WIDTH = 480
IM_HEIGHT = 300

# IM_WIDTH = 1280
# IM_HEIGHT = 720

last = np.zeros((IM_HEIGHT, IM_WIDTH, 4), dtype=np.uint8)

PERIOD_OF_TIME = 50
start = time.time()

actor_list = []

f_images = []
f_images.append(last)

b_images = []
b_images.append(last)

# ==========================================================================================
# functions

def process_f_img(image, l_images):
    i = np.array(image.raw_data)
    # print(i.shape)
    i2 = i.reshape((IM_HEIGHT, IM_WIDTH, 4)) #rgba, a for alpha (opacity)
    i3 = i2[:, :, :3] # /255.0 # entire height, entire width, only rgb (no alpha)
    # print(i3[1 , 1, :])
    #import pdb; pdb.set_trace()
    # cv2.imshow("image", i3)
    # cv2.waitKey(111)
    # print(image.frame)
    f_images.append(i3)
    return #i3/255.0 # normalize the data

def process_b_img(image, l_images):
    i = np.array(image.raw_data)
    # print(i.shape)
    i2 = i.reshape((IM_HEIGHT, IM_WIDTH, 4)) #rgba, a for alpha (opacity)
    image = i2[:, :, :3] # /255.0 # entire height, entire width, only rgb (no alpha)
    # print(image[1 , 1, :])
    #import pdb; pdb.set_trace()
    # cv2.imshow("image", image)
    # cv2.waitKey(111)
    # print(image.frame)
    b_images.append(image)
    return #i3/255.0 # normalize the data


# def show(l_images):
#     while(True):
#         cv2.imshow('image', l_images[-1])
#         cv2.waitKey(16)
#         # time.sleep(0.125)

def show():
    while(True):
        cv2.imshow('f_image', f_images[-1])
        cv2.waitKey(16)
        # cv2.imshow('b_image', b_images[-1])
        # cv2.waitKey(16)
        print(carla.Actor.get_location(actor_list[0]))
        time.sleep(0.100)
        if time.time() > start + PERIOD_OF_TIME :
            sys.exit()


# ======================================================================================

try:
    client = carla.Client("localhost", 2000)
    client.set_timeout(5.0)

    world = client.get_world()

    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter("model3")[0]
    print(bp)

    # spawn_point = random.choice(world.get_map().get_spawn_points())
    vehicle_spawn_point = carla.Transform(carla.Location(x=50, y=5, z=1), carla.Rotation(yaw=0.0))
    # spawn_point = carla.Transform(carla.Location(x=233, y=-12, z=1), carla.Rotation(yaw=-90))

    vehicle = world.spawn_actor(bp, vehicle_spawn_point)
    actor_list.append(vehicle)
    vehicle.set_autopilot(True)

    # vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))

    cam_bp = blueprint_library.find("sensor.camera.rgb")
    cam_bp.set_attribute("image_size_x",  format(IM_WIDTH))
    cam_bp.set_attribute("image_size_y",  format(IM_HEIGHT))
    cam_bp.set_attribute("fov", "90")

    fcam_spawn_point = carla.Transform(carla.Location(x=0.9, z=1.5),carla.Rotation(yaw=0.0))
    bcam_spawn_point = carla.Transform(carla.Location(x=-1.6, z=1.5),carla.Rotation(yaw=180.0))
    # spawn_point = carla.Transform(carla.Location(x=2.5, z=0.7))

    fcam = world.spawn_actor(cam_bp, fcam_spawn_point, attach_to=vehicle)
    actor_list.append(fcam)

    fcam.listen(lambda f_data: process_f_img(f_data,f_images))

    # bcam = world.spawn_actor(cam_bp, bcam_spawn_point, attach_to=vehicle)
    # actor_list.append(bcam)

    # bcam.listen(lambda b_data: process_b_img(b_data,b_images))

    if __name__=='__main__':
        Process(target = show()).start()

    # time.sleep(runTime)

    fcam.stop()


finally:
    for actor in actor_list:
        actor.destroy()
    print("All cleaned up!")


    # blueprint.set_attribute("image_size_x",  format(IM_WIDTH))
    # blueprint.set_attribute("image_size_y",  format(IM_HEIGHT))
