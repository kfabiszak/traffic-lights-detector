# Krzysztof Fabiszak 122553
# Mateusz Głowacki 122555

import numpy as np
import cv2
from PIL import Image

passesRank = 0.6*0.6
imageCounter = 0

loaded = 0

def adjust_gamma(image, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def loadImage(name):
    image = cv2.imread('images/' + name + '.png')
    return image

def JPG2PNG(name):
    im = Image.open('images/'+name+'.jpg')
    im.save('images/'+name+'.png')

def transformImage(image):
    gammaImage = adjust_gamma(image, 0.8)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(gammaImage, cv2.COLOR_BGR2HSV)

    edged = cv2.Canny(gray, 50, 150)
    circles = cv2.HoughCircles(edged, cv2.HOUGH_GRADIENT, 1, 10, param1=100, param2=25, minRadius=5, maxRadius=25)
    circles = np.uint16(np.around(circles))
    return circles, hsv

def difColor(color1, color2):
    treshH = 20
    return (abs(color1[0] - color2[0]) < treshH)

def colorTestGreenHSV(imgDetected, x, y, r):
    size = int(r * 0.6)
    size2 = int(size / 2)
    passes = 0
    centerColor = imgDetected[y, x]
    lower_green = [40, 100, 100]
    higher_green = [100, 255, 255]

    for j in range(0, size2):
        color = imgDetected[y, x - j]
        if color[0] > lower_green[0] and color[0] < higher_green[0]\
                and color[1] >= lower_green[1] and color[1] <= higher_green[1]\
                and color[2] >= lower_green[2] and color[2] <= higher_green[2]:
            passes += 0.7 + 0.3*difColor(centerColor, color)
    for k in range(0, size2):
        color = imgDetected[y, x + k]
        if color[0] > lower_green[0] and color[0] < higher_green[0]\
                and color[1] >= lower_green[1] and color[1] <= higher_green[1]\
                and color[2] >= lower_green[2] and color[2] <= higher_green[2]:
            passes += 0.7 + 0.3*difColor(centerColor, color)
    print('passes GreenTest: ', passes, '/', size, '/ hsv: ', imgDetected[y, x])
    #print(color)
    return passes

def colorTestRedHSV(imgDetected, x, y, r):
    size = int(r * 0.6)
    size2 = int(size / 2)
    passes = 0
    centerColor = imgDetected[y, x]
    higher_red = [40, 255, 255]
    lower_red = [130, 50, 180]

    for j in range(0, size2):
        color = imgDetected[y - j, x]
        if (color[0] > lower_red[0] or color[0] < higher_red[0])\
                and color[1] >= lower_red[1] and color[1] <= higher_red[1]\
                and color[2] >= lower_red[2] and color[2] <= higher_red[2]:
            passes += 1# + 0.3 * difColor(centerColor, color)
    for k in range(0, size2):
        color = imgDetected[y + k, x]
        if (color[0] > lower_red[0] or color[0] < higher_red[0])\
                and color[1] >= lower_red[1] and color[1] <= higher_red[1]\
                and color[2] >= lower_red[2] and color[2] <= higher_red[2]:
            passes += 1# + 0.3 * difColor(centerColor, color)
    print('passes RedTest: ', passes, '/', size, '/ hsv: ', imgDetected[y, x])
    return passes

def detectLights(name):
    image = loadImage(name)

    circles, hsv = transformImage(image)

    for n, i in enumerate(circles[0, :]):
        print('nr ', n)
        #cv2.circle(image, (i[0], i[1]), i[2], (0, 255, 0), 2), 10
        passesGreen = colorTestGreenHSV(hsv, i[0], i[1], i[2])
        passesRed = colorTestRedHSV(hsv, i[0], i[1], i[2])

        #cv2.putText(image, '%d' % n, (i[0], i[1] + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 0), 2, 2)


        if passesGreen >= passesRed and passesGreen > i[2] * passesRank:
            print(i[1], i[0])
            cv2.circle(image, (i[0], i[1]), i[2], (0, 0, 255), 2)
            cv2.putText(image, 'DRIVE', (i[0], i[1]), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 255, 255), 2, 2)
        if passesGreen < passesRed and passesRed > i[2] * passesRank:
            print(i[1], i[0])
            cv2.circle(image, (i[0], i[1]), i[2], (255, 0, 0), 2)
            cv2.putText(image, 'STOP', (i[0], i[1]), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 255, 255), 2, 2)
    return image

def interaction(imageNumber, loaded):
    loaded = 1
    image = detectLights('t%d' % imageNumber)
    cv2.namedWindow('Traffic Lights', cv2.WINDOW_NORMAL)
    cv2.imshow("Traffic Lights", image)
    print('Image ', imageNumber)
    return loaded

def start(loaded):
    image = cv2.imread('images/t0.png')
    cv2.imshow('Traffic Lights', image)
    loaded = 1
    return loaded

#JPG2PNG('t51') //konwersja JPG do PNG

while True:
    k = cv2.waitKey(100)
    if imageCounter == 0:
        loaded = start(loaded)
    if loaded == 0:
        loaded = interaction(imageCounter, loaded)
    if k == 2424832 and imageCounter > 0:
        loaded = 0
        imageCounter -= 1
    if k == 2555904 and imageCounter < 53:
        loaded = 0
        imageCounter += 1
