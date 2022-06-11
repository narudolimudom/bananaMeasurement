import cv2
import numpy as np
import math
import matplotlib.pyplot as plt

def readImage(img_path):
    try:
        return cv2.imread(img_path)
    except:
        print('Error invalid path or image file')

def fitLinesOnCoor(coordinates, image):
    points = []
    x_min, x_max = image.shape[1], 0
    for point in coordinates: 
        points.append(tuple(point[0]))
    x,y = zip(*points)
# How degree affect to polynomial equations.
    z = np.polyfit(x,y,7)
    f = np.poly1d(z)
    x_new = np.linspace(0, image.shape[1],image.shape[0])
    y_new = f(x_new)
    extension = list(zip(x_new, y_new))
    return extension

def getContours(binary_img):
    return cv2.findContours(binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

def findLargestContour(contours):
    return contours[get_biggest_n_contours(contours)]

def drawContourImg(contours, image):
    color, thickness, result = (255,0,0), 1, image.copy()
    cv2.drawContours(result, contours, 0, color, thickness)
    return result

def showImage(title, image):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def get_biggest_n_contours(contours):
    current = 0
    temp = contours[current]
    max_index = 0
    for j in contours:
        if cv2.arcLength(j, True) > cv2.arcLength(temp, True):
            temp = contours[current]
            max_index = current
        current+=1
    return max_index
    
def getPreparedImg(image, threshold):
    mask_size = (5,5)
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    removed_noise_img = cv2.blur(gray_img, mask_size)
    ret, binary_img = cv2.threshold(removed_noise_img, threshold, 255,0)
    # contour filling
    contours, _ = cv2.findContours(binary_img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    temp_binary = np.zeros_like(binary_img)
    largest_contour = get_biggest_n_contours(contours)
    cv2.drawContours(temp_binary,contours,largest_contour,255, cv2.FILLED)
    if ret:
        return removed_noise_img, temp_binary, contours, largest_contour
    else:
        print('Error occurs')

def removeSkelNoise(skeleton_img):
    return cv2.morphologyEx(skeleton_img, cv2.MORPH_OPEN, (1,1))

def getSkeleton(binary_img, gray_img):
    mask_size = (3,3)
    size = np.size(gray_img)
    skel = np.zeros_like(gray_img)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, mask_size)
    done = False

    while(not done):
        eroded = cv2.erode(binary_img, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(binary_img, temp)
        skel = cv2.bitwise_or(skel, temp)
        binary_img = eroded.copy()

        zeros = size - cv2.countNonZero(binary_img)
        if zeros==size:
            done = True

    return skel

def fillSKelHoles(skeleton_img,binary_img,original_img):
    container = np.zeros(skeleton_img.shape, np.uint8)
    height, width = skeleton_img.shape
    temp = None
    is_endpoint = False
    prev_slope = None
    # for ripeness
    count_r = 0
    sumR = 0
    sumG = 0
    sumB = 0
    ripeness = 'None'
    for i in range(width):
        count = 0
        for j in range(height):
            if binary_img[j,i] == 255:
                sumR += original_img[j,i][2]
                sumG += original_img[j,i][1]
                sumB += original_img[j,i][0]
                count_r += 1
            if skeleton_img[j,i] == 255:
                if is_endpoint:
                    cv2.line(container, temp, (i,j), (255,255,255), 1)
                    prev_slope = findSlope(temp, (i,j))
                    is_endpoint = False
                count += 1
                temp = (i,j)
                break
        if count == 0 and temp is not(None):
            is_endpoint = True
        else:
            is_endpoint = False
    avgR = sumR / count_r
    avgG = sumG / count_r
    avgB = sumB / count_r
    
    
    filled_skel = cv2.bitwise_or(skeleton_img,container)
    enhanced_filled_skel = cv2.dilate(filled_skel, np.ones((2,2), np.uint8), iterations=1)
    return enhanced_filled_skel

def getPerpCoord(aX, aY, bX, bY, length):
    vX = bX-aX
    vY = bY-aY
    if(vX == 0 or vY == 0):
        return 0, 0, 0, 0
    mag = math.sqrt(vX*vX + vY*vY)
    vX = vX / mag
    vY = vY / mag
    temp = vX
    vX = 0-vY
    vY = temp
    cX = bX + vX * length
    cY = bY + vY * length
    dX = bX - vX * length
    dY = bY - vY * length
    return int(cX), int(cY), int(dX), int(dY)

def findSlope(coor_1,coor_2):
    return (coor_2[1] - coor_1[1]) / (coor_2[0] - coor_1[0])

def findDistance(a,b): 
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)