import helper as hp
import cv2
import numpy as np
import timeit
import time
import os
from PyQt5.QtCore import (QThread, Qt, pyqtSignal)
from PyQt5.QtGui import (QPixmap, QImage)

def image_process(real_image,copy_image):
    pass
class ProcessWorker(QThread):
    sizeNumber = pyqtSignal(int)
    length = pyqtSignal(float)
    diameter = pyqtSignal(float)
    timeUsed = pyqtSignal(float)
    changePixmap = pyqtSignal(QImage)
    def __init__(self,parent):
        QThread.__init__(self, parent=parent)   
        self.banana_image = cv2.imread('defaultImage.png')
        self.frequency = 10
        self.hasVisual = False
        self.calibration_value = 57.89 # 72.16 for scale percent = 50
        self.threshold_value = 80 # 80
        self.font_text = cv2.FONT_HERSHEY_SIMPLEX
        self.text_line = cv2.LINE_AA
        self.white_color = (255,255,255)
        self.red_color = (0,0,255)
        self.blue_color = (255,0,0)
        self.object_detected = False

    def run(self):
        while True:
            print('start')
            try:
                self.main_func()
                
            except:
                print('error')
                
    def main_func(self):
        #+ filename
        # Start mearsuring time
        start = timeit.default_timer()
        # Get input image from camera or files
        # hp.showImage('title',banana_image)
        # Input image was too big so resize it before doing the process for better runtime
        scale_percent = 40 # percent of original size
        w = int(self.banana_image.shape[1] * scale_percent / 100)
        h = int(self.banana_image.shape[0] * scale_percent / 100)
        dim = (w, h)
        # Result of resizing the image
        self.banana_image = cv2.resize(self.banana_image, dim, interpolation=cv2.INTER_NEAREST)
        # Prepare the image for other process
        gray_image, binary_image, banana_contours, largest_contour = hp.getPreparedImg(self.banana_image, self.threshold_value)
        # cv2.imshow('title', binary_image)
        # cv2.waitKey(0)
        temp_contour = np.zeros_like(binary_image)
        cv2.drawContours(temp_contour, banana_contours, largest_contour, (255,255,255), 2)
        # Find skeleton of the image for calculating width
        skeleton_image = hp.getSkeleton(binary_image, gray_image)
        # Remove some noise that caused from skeletonization process
        removed_noise = hp.removeSkelNoise(skeleton_image)
        # Enhance the skeleton image
        filled_skeleton = hp.fillSKelHoles(removed_noise, binary_image, self.banana_image)
        # Find skeleton's contour and the largest one
        skeleton_contours, _ = hp.getContours(filled_skeleton)
        largest_skeleton_contour = hp.findLargestContour(skeleton_contours)
        # hp.showImage('test', cv2.drawContours(np.zeros_like(filled_skeleton), skeleton_contours, hp.get_biggest_n_contours(skeleton_contours), (255,255,255), 1))
        # We can't directly use the skeleton from the image so fit it with some polynomial equations and use its coordinates instead
        extension = hp.fitLinesOnCoor(largest_skeleton_contour, gray_image)
        # This part just for visualize how polynomial equation fit with skeleton of an image

        temp_image = self.banana_image.copy()
        for point in range(len(extension)-1):
            title = 'Fit line with poylynomial equation'
            a = tuple(np.array(extension[point], int))
            b = tuple(np.array(extension[point+1], int))
            cv2.line(temp_image, a, b, self.blue_color, 1)
            if self.hasVisual:
                rgbImage = cv2.cvtColor(temp_image, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(760, 430)
                self.changePixmap.emit(p)

        # Start finding the longest width of the banana
        # Fix this later bruh.
        max_diamter = 0
        max_diamter_coor = []
        total_width = []
        perp_lines = []
        for point in range(len(extension)-self.frequency):
            # Prepare some instance of an image for the process
            title = 'Draw perpendicular line on banana'
            temp_image = self.banana_image.copy()
            container = np.zeros_like(gray_image)
            # Sampling and calculating the midpoint
            x_midpoint = int((extension[point][0] + extension[point+self.frequency][0])/2)
            y_midpoint = int((extension[point][1] + extension[point+self.frequency][1])/2)
            # Draw the previous perpendicular line
            # version 2.0
            isInside = cv2.pointPolygonTest(banana_contours[largest_contour],(x_midpoint,y_midpoint),True)
            if isInside >= 0:
                # Calculate the perpendicular line
                x1, y1, x2, y2 = hp.getPerpCoord(extension[point+10][0],extension[point+10][1], x_midpoint, y_midpoint, length=90)
                cv2.line(container, (x1, y1), (x2, y2), self.white_color, 1)
                # Bitwise for removing the exceed part
                perp_line = cv2.bitwise_and(container, binary_image)
                # Get contour from the previous line
                perp_contours, _ = hp.getContours(perp_line)
                cv2.drawContours(temp_image, perp_contours, 0, self.red_color, 1)
                if self.hasVisual:
                    rgbImage = cv2.cvtColor(temp_image, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(760, 430)
                    self.changePixmap.emit(p)
                # If exists then get the info
                if len(perp_contours) > 0:
                    length = cv2.arcLength(perp_contours[0], False)
                    perp_lines.append([length, perp_contours])
                    if length > max_diamter:
                        max_diamter = length
                        max_diamter_coor = perp_contours
                    total_width.append(length)

        # Calculate the average diameter for removing head and tail purpose
        average_width, std = np.average(total_width), np.std(total_width)
        count_flag = 0
        for line in perp_lines:
            if line[0] < 0.84*(average_width - std):
                if count_flag < 1:
                    cv2.drawContours(self.banana_image, line[1], 0, self.red_color, 2)
                count_flag = 0
            else:
                count_flag+=1
        # Find the longest length of the banana 
        # I'm too lazy to describe this part so..
        colors = self.blue_color
        flag = False
        temp_coor = []
        max_length = 0
        max_length_coor = []
        for i in banana_contours[largest_contour]:
            title = 'Find the longest part'
            check = self.banana_image.copy()
            x, y = i[0][0], i[0][1]
            if all(check[y,x] == self.red_color):
                # I found some error with this part caused by empty list []. I can't really figured out how come is it
                # so instead handle it with try catch exception might work
                try:
                    length = cv2.arcLength(np.array([temp_coor]), False)
                    if length > max_length:
                        max_length = length
                        max_length_coor = temp_coor
                    if flag:
                        colors = self.red_color
                    else:
                        colors = self.blue_color
                    temp_coor = []
                    flag = not(flag)
                except:
                    pass
            temp_coor.append(i[0])
            cv2.circle(check, (x,y), 2, colors, 2)
        # End all of the process. show time that we used
        tempimage = np.zeros_like(binary_image)
        cv2.polylines(tempimage, np.array([max_length_coor]), False, (255,255,255), 4)
        cnt_len, _ = cv2.findContours(tempimage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        max_length = cv2.arcLength(cnt_len[0], False)
        stop = timeit.default_timer()
        # Visualization part for showing how's the result
        width_info = 'Diameter: ' + '{:.2f} cm.'.format(max_diamter/self.calibration_value)
        length_info = 'Length: ' + '{:.2f} cm.'.format(max_length/self.calibration_value)
        cv2.putText(self.banana_image, width_info, (20,50), self.font_text, 0.7, self.white_color, 2, self.text_line)
        cv2.putText(self.banana_image, length_info, (20,100), self.font_text, 0.7, self.white_color, 2, self.text_line)
        if self.object_detected:
            cv2.putText(self.banana_image, 'Two or more objects were detected', (20,150), self.font_text, 0.8, self.white_color, 2, self.text_line)
        cv2.polylines(self.banana_image, np.array([max_length_coor]), False, self.blue_color, 3)
        cv2.drawContours(self.banana_image, max_diamter_coor, 0, (0,255,0), 3)
        rgbImage = cv2.cvtColor(self.banana_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w
        convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(760, 430)
        self.changePixmap.emit(p)
        self.length.emit(max_length/self.calibration_value)
        self.diameter.emit(max_diamter/self.calibration_value)
        self.timeUsed.emit(stop - start)
        self.getSizeNumber(max_diamter/self.calibration_value,max_length/self.calibration_value)


    def getSizeNumber(self, diameter, length):
        if diameter > 4.6:
            self.sizeNumber.emit(1)
        elif diameter > 4.3 and diameter < 4.6: 
            self.sizeNumber.emit(2)
        elif diameter > 4.0 and diameter < 4.3:
            self.sizeNumber.emit(3)
        elif diameter > 3.6 and diameter < 4.0:
            self.sizeNumber.emit(4)
        elif diameter > 3.3 and diameter < 3.6:
            self.sizeNumber.emit(5)
        elif diameter > 3.0 and diameter < 3.3:
            self.sizeNumber.emit(6)
        elif diameter > 2.8 and diameter < 3.0:
            self.sizeNumber.emit(7)
        else: 
            self.sizeNumber.emit(0)
    

