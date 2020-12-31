import cv2
import numpy as np
from collections import deque



def setValues(x):
    print("none")

cv2.namedWindow("Color Pointer")
cv2.createTrackbar("Upper Hue", "Color Pointer", 153, 180, setValues)
cv2.createTrackbar("Upper Saturation", "Color Pointer", 255, 0, setValues)
cv2.createTrackbar("Upper Value", "Color Pointer", 255, 0, setValues)
cv2.createTrackbar("Lower Hue", "Color Pointer", 64, 180, setValues)
cv2.createTrackbar("Lower Saturation", "Color Pointer", 72, 0, setValues)
cv2.createTrackbar("Lower Value", "Color Pointer", 49, 255, setValues)


cpoints = [deque(maxlen=1024)]


blue_index = 0


kernel = np.ones((5, 5), np.uint8)

colors = [(255, 255, 0)]
colorIndex = 0


paintWindow = np.zeros((471, 636, 3)) + 255

cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)


cap = cv2.VideoCapture(0)


while True:

    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    u_hue = cv2.getTrackbarPos("Upper Hue", "Color Pointer")
    u_saturation = cv2.getTrackbarPos("Upper Saturation", "Color Pointer")
    u_value = cv2.getTrackbarPos("Upper Value", "Color Pointer")
    l_hue = cv2.getTrackbarPos("Lower Hue", "Color Pointer")
    l_saturation = cv2.getTrackbarPos("Lower Saturation", "Color Pointer")
    l_value = cv2.getTrackbarPos("Lower Value", "Color Pointer")
    Upper_hsv = np.array([u_hue, u_saturation, u_value])
    Lower_hsv = np.array([l_hue, l_saturation, l_value])


    Mask = cv2.inRange(hsv, Lower_hsv, Upper_hsv)
    Mask = cv2.erode(Mask, kernel, iterations=1)
    Mask = cv2.morphologyEx(Mask, cv2.MORPH_OPEN, kernel)
    Mask = cv2.dilate(Mask, kernel, iterations=1)


    cnts, _ = cv2.findContours(Mask.copy(), cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_SIMPLE)
    center = None

    if len(cnts) > 0:

        cnt = sorted(cnts, key=cv2.contourArea, reverse=True)[0]

        ((x, y), radius) = cv2.minEnclosingCircle(cnt)

        cv2.circle(frame, (int(x), int(y)), int(radius), (0, 0, 255), 2)

        M = cv2.moments(cnt)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))


        if center[1] <= 65:
            if 40 <= center[0] <= 140:
                cpoints = [deque(maxlen=512)]

                blue_index = 0

                paintWindow[67:, :, :] = 255
            elif 160 <= center[0] <= 255:
                colorIndex = 0

        else:
            if colorIndex == 0:
                cpoints[blue_index].appendleft(center)

    else:
        cpoints.append(deque(maxlen=512))
        blue_index += 1

    points = [cpoints]
    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1, len(points[i][j])):
                if points[i][j][k - 1] is None or points[i][j][k] is None:
                    continue
                cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)

    cv2.imshow("Tracking window", frame)


    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()