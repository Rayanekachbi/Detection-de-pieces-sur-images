import numpy as np
import matplotlib.pylab as plt
import cv2

def fetchNprocess(imgStr : str, show = False):
    image = cv2.imread(imgStr)

    factor = round(getFactor(image, 1200), 2)
    image = cv2.resize(image, (0,0), fx=factor, fy=factor)
    
    prImage = processImage(image)
    image, circles_list = doWatershed(prImage, image, show)
    
    return image, circles_list

def getFactor(image, factor : int) -> float:
    imageHeight = image.shape[0]
    imageWidth = image.shape[1]

    factor = min(factor / imageHeight, factor / imageWidth)
    return factor

def processImage(image):
    ### Les valeurs des blurs, adaptiveThreshold, etc... on été trouvé en faisant plusieurs combinaisons sur base de test ###
    prImage = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    _, prImage, _ = cv2.split(prImage)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    prImage = clahe.apply(prImage)

    prImage = cv2.medianBlur(prImage, 7)
    prImage = cv2.GaussianBlur(prImage, (15, 15), 0)

    prImage = cv2.adaptiveThreshold(prImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, blockSize=101, C=4)
    prImage = fillHoles(prImage)

    open_ker  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    close_ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))

    prImage = cv2.morphologyEx(prImage, cv2.MORPH_OPEN,  open_ker,  iterations=1)
    prImage = cv2.morphologyEx(prImage, cv2.MORPH_CLOSE, close_ker, iterations=1)

    return prImage

def fillHoles(binary):
    ### CODE POUR COMBLER LES TROUS DES CONTOURS PAR CLAUDE
    result = binary.copy()
    contours = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    hierarchy = contours[1]
    contours  = contours[0]
    
    if hierarchy is None:
        return binary
    for i, h in enumerate(hierarchy[0]):
        if h[3] != -1:
            cv2.drawContours(result, contours, i, 255, -1)
    ###
    return result

def doWatershed(prImage, dfImage, show):
    height, width = dfImage.shape[0:2]
    l_height, l_width = int(height * (5/100)), int(width * (5/100))
    min_one = int(min(l_height, l_width) * 12/100)

    min_area = l_height * l_width
    minCircularity = 0.75
    distance = cv2.distanceTransform(prImage, cv2.DIST_L2, 5)

    ### DEMANDE D'AIDE DE MAXIMA LOCAL ET NON GLOBAL PAR CLAUDE
    ### En revanche, les valeurs tels que 0.15, (23, 23), 0.70, sont des valeurs ajustées en fonction de la visualisation ci-dessous
    zones = cv2.threshold(distance, 0.15 * distance.max(), 255, 0)[1]
    zones = np.uint8(zones)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (23, 23))
    local_dil = cv2.dilate(distance, kernel)
    sure_foreground_lcl = np.uint8((distance == local_dil) & (zones == 255))
    sure_foreground_str = np.uint8(cv2.threshold(distance, 0.70 * distance.max(), 255, 0)[1])
    sure_foreground = np.uint8(cv2.bitwise_or(sure_foreground_str, sure_foreground_lcl))
    ###

    sure_background = cv2.dilate(prImage, np.ones((min_one, min_one), np.uint8), iterations=3)

    unknown = cv2.subtract(sure_background, sure_foreground)

    marker = cv2.connectedComponents(sure_foreground)[1]
    marker += 1
    marker[unknown == 255] = 0

    if (show):
        ### AFFICHAGE DES DIFFERENTES IMAGES DE WATERSHED AFIN DE POUVOIR FAIRE DU TUNNING
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes[0, 0].imshow(prImage, cmap='gray')
        axes[0, 0].set_title('Masque binaire')
        axes[0, 1].imshow(distance, cmap='jet')
        axes[0, 1].set_title('Distance transform')
        axes[0, 2].imshow(sure_foreground, cmap='gray')
        axes[0, 2].set_title('Sure foreground')
        axes[1, 0].imshow(sure_background, cmap='gray')
        axes[1, 0].set_title('Sure background')
        axes[1, 1].imshow(unknown, cmap='gray')
        axes[1, 1].set_title('Unknown')
        axes[1, 2].imshow(marker, cmap='jet')  # jet pour distinguer les labels
        axes[1, 2].set_title('Markers')
        for ax in axes.flat:
            ax.axis('off')
        plt.tight_layout()
        plt.show()
        ###

    marker = cv2.watershed(dfImage, marker)

    if (show):
        ### AFFICHAGE DES RESULTATS, CODE PAR CLAUDE
        watershed_viz = np.zeros((height, width, 3), dtype=np.uint8)

        for label in np.unique(marker):
            if label <= 1:
                continue
            color = np.random.randint(0, 255, 3).tolist()
            watershed_viz[marker == label] = color
        
        watershed_viz[marker == -1] = [255, 0, 0]
        
        plt.imshow(watershed_viz)
        plt.title('Régions Watershed')
        plt.axis('off')
        plt.show()
        ###
        
    circles_list = []
    
    for label in np.unique(marker):
        if (label > 1):
            region = np.uint8(marker == label) * 255
            area = np.sum(region > 0)
    
            if (area > min_area):
                contour = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]
                ### HULL PROPOSEE PAR CLAUDE EN GUISE D'AMELIORATION POUR LES FORMES CIRCULAIRE
                hull = cv2.convexHull(contour[0])
                ###
                perimeter = cv2.arcLength(hull, True)
                circularity = 4 * np.pi * area / (perimeter ** 2)
    
                if (circularity >= minCircularity):
                    (x, y), radius = cv2.minEnclosingCircle(hull)
                    cv2.circle(dfImage, (int(x), int(y)), int(radius), (255,0,0), 3)
                    circles_list.append((int(x), int(y), int(radius)))
    return dfImage, circles_list