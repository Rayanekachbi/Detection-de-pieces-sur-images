import numpy as np
import matplotlib.pylab as plt
import cv2

#source : https://www.youtube.com/watch?v=_Coth4YESzk
def fetchNprocess(img : str):
    norm = 500 # For the rescale.

    image = cv2.imread(img) # Fetch the image.
    scale = adaptiveScale(norm, image)
    image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA) # Rescale the image to be smaller and closest to the norm.

    hlsImage = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HLS) # Convert the image to a gray scale image.
    imageH, imageL, imageS = cv2.split(hlsImage)

    imageS = cv2.GaussianBlur(imageS, (9, 9), 1)
    imageS = cv2.medianBlur(imageS, 9)

    clahe = cv2.createCLAHE(clipLimit=3)
    imageS = np.clip(clahe.apply(imageS), 50, 255).astype(np.uint8)

    circle = cv2.HoughCircles(imageS, cv2.HOUGH_GRADIENT, 1, int(norm/10), param1=120, param2=40, minRadius=int(norm/20), maxRadius=int(norm/1))

    circles_list = []
    if circle is not None:
        circles = np.uint16(np.around(circle)) # Create the circles in the form of a vector.

        for i in circles[0,:]:
            x, y, r = i # x is the center, y is the other end of the radius, r is the radius
            circles_list.append((x, y, r))
            # (BRG)
            cv2.circle(image, (x,y), r, (255,0,0), 2) # Create the circle around the center with an r radius (Blue) with a thickness of 2.
            cv2.circle(image, (x,y), 2, (0,255,255), 3) # Create the center of the circle (Yellow) with a thickness of 3.

    return image, circles_list

# This function will rescale the image to the norm size.
def adaptiveScale(norm : int, image) -> float:
    return norm / image.shape[1]

# This function is for the param1 and param2 of the HoughCircle.
def getParameter(param2 : int, factor : int) -> tuple[int, int]:
    return (param2, param2 * factor)