import cv2
import numpy as np
import matplotlib.pyplot as mplt
import math

def canny(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # blur = cv2.GaussianBlur(gray,(5, 5),0)
    canny = cv2.Canny(gray,50,150)
    return canny

def region_of_interest(image):
    height = image.shape[0]
    width = image.shape[1]
    # polygons = np.array([
    # [(0, height),(width+1100, height),(670,355)]
    # ])
    # polygons = np.array([
    # [(0, height),(0, height),(width,height),(width,0)]
    # ])
    polygons = np.array([
    [(0, height-350),(0, height),(width+500,height),(width,height-350)]
    ])
    # polygons = np.array([
    # [(50, height),(100, height),(670,355)]
    # ])
    # polygons = np.array([
    # [(0, 350),(0, 450),(1280,450),(1280,350)]
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
        if (slope < -0.1 or slope > 0.1) and denominator != 0 and numerator != 0 and d > 100:
            mod_lines.append(line)
            print(slope)
        i = i+1
    Mod_lines = np.array(mod_lines)
    # print(Mod_lines)
    return Mod_lines


image = cv2.imread('../../data/images/sim_test.png')
lane_image = np.copy(image)
canny = canny(lane_image)
cropped_image = region_of_interest(canny)
lines = cv2.HoughLinesP(cropped_image, 2, np.pi/180,100, np.array([]),minLineLength=40,maxLineGap=70)
# print(lines)
lane_lines = only_lane(lines)
line_image = display_lines(lane_image,lane_lines)
combo_image = cv2.addWeighted(lane_image, 0.8, line_image, 1, 1)
# cv2.namedWindow("result",cv2.WINDOW_NORMAL)
# cv2.resizeWindow("result", 800,500)
cv2.imwrite("../../data/combo_image.png",combo_image)
cv2.imshow("result",combo_image)
cv2.waitKey(0)
# mplt.imshow(combo_image)
# mplt.show()
