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
        '/opt/carla-simulator/PythonAPI/carla/dist/carla-0.9.8-py3.5-linux-x86_64.egg')[0])
except IndexError:
    pass

import carla
import random
import time
import numpy as np
import cv2
import matplotlib.pyplot as mplt
import matplotlib.image as mimg
import math

# ===========================================================================================
# variables and constants

runTime = 1
#
# IM_WIDTH = 640
# IM_HEIGHT = 480

IM_WIDTH = 1280
IM_HEIGHT = 720

# IM_WIDTH = 1000
# IM_HEIGHT = 600

last = np.zeros((IM_HEIGHT, IM_WIDTH, 4), dtype=np.uint8)

PERIOD_OF_TIME = 100
start = time.time()

actor_list = []

f_images = []
f_images.append(last)

b_images = []
b_images.append(last)

# ==========================================================================================
# functions

# ----------------------------------------------------------------------------------------
# lane detection functions

def canny(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # blur = cv2.GaussianBlur(gray,(5, 5),0)
    canny = cv2.Canny(gray,50,150)
    return canny

def region_of_interest(image):
    height = image.shape[0]
    width = image.shape[1]
    height_half = round(height/2)
    width_half = round(width/2)
    # polygons = np.array([
    # [(0, height),(width+width_half, height),(500,300)]
    # ])
    # polygons = np.array([
    # [(0, height),(0, height),(width,height),(width,0)]
    # ])
    # polygons = np.array([
    # [(0, height-350),(0, height),(width+500,height),(width,height-350)]
    # ])
    polygons = np.array([
    [(0, height_half+20),(0, height),(width+width_half,height),(width,height_half+20)]
    ])
    # polygons = np.array([
    # [(50, height),(100, height),(670,355)]
    # ])
    mask = np.zeros_like(image)
    cv2.fillPoly(mask,polygons,255)
    masked_image = cv2.bitwise_and(image,mask)
    return masked_image

def display_lines(image, lines):
    line_image = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(line_image,(x1,y1),(x2,y2),(255,0,0),5)
    return line_image

def calculateDistance(x1,y1,x2,y2):
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return dist

def only_lane(lines):
    mod_lines = []
    # left_fit = []
    # middle_fit = []
    # right_fit = []
    i = 0
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        # params = np.polyfit((x1,y1),(x2,y2),1)
        # slope = params[0]
        # y_interest = params[1]
        # x_interest = -(y_interest/slope)
        # parameters = []
        # for param in params:
        #     parameters.append(param)
        # parameters.append(x_interest)
        slope = (y2-y1)/(x2-x1)
        numerator = y2 - y1
        denominator = x2 - x1
        d = calculateDistance(x1, y1, x2, y2)
        if (slope < -0.1 or slope > 0.1) and denominator != 0 and numerator != 0  and d > 300:
            mod_lines.append(line)
            print(slope)
        i = i+1
    Mod_lines = np.array(mod_lines)
    # print(Mod_lines)
    return Mod_lines

def lane_detection(image):
    lane_image = np.copy(image)
    Canny = canny(lane_image)
    cropped_image = region_of_interest(Canny)
    lines = cv2.HoughLinesP(cropped_image, 2, np.pi/180,100, np.array([]),minLineLength=50,maxLineGap=70)
    # print(lines)
    lane_lines = only_lane(lines)
    line_image = display_lines(lane_image,lane_lines)
    combo_image = cv2.addWeighted(lane_image, 0.8, line_image, 1, 1)
    # cv2.namedWindow("result",cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("result", 800,500)
    # cv2.imwrite("../../data/combo_image.png",combo_image)
    # cv2.imshow("result",combo_image)
    # cv2.waitKey(0)
    # mplt.imshow(combo_image)
    # mplt.show()
    return combo_image

# ========================================================================================================
# processing image

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
    lanep_image = lane_detection(i3)
    f_images.append(lanep_image)
    # f_images.append(i3)
    return i3/255.0 # normalize the data

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
    return i3/255.0 # normalize the data


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
# simulation control

try:
    client = carla.Client("localhost", 2000)
    client.set_timeout(5.0)

    world = client.get_world()

    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter("model3")[0]
    print(bp)

    # spawn_point = random.choice(world.get_map().get_spawn_points())
    # vehicle_spawn_point = carla.Transform(carla.Location(x=50, y=4, z=1), carla.Rotation(yaw=0.6))
    vehicle_spawn_point = carla.Transform(carla.Location(x=233, y=-12, z=1), carla.Rotation(yaw=90))

    vehicle = world.spawn_actor(bp, vehicle_spawn_point)
    actor_list.append(vehicle)
    #vehicle.set_autopilot(True)

    vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))

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
