import cv2
import numpy as np
from matplotlib import pyplot as plt
#------------------------------------------------------------------------------------------------------------------------------------------------------------#
#functions
#------------------------------------------------------------------------------------------------------------------------------------------------------------#

def preprocessImage(image):
    #resize
    height, width, ch = image.shape
    resized = cv2.resize(image, [int(width/2), int(height/2)])

    #Grayscale conversion
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    return gray

def segmentBreast(preprocessedImage):
    #Increasing the contrast values
    highContrast = adjustContrastAndBrightness(contrast=3, brightness=0, image=preprocessedImage)

    #Apllying Gaussian Blur
    blur = cv2.GaussianBlur(highContrast, (3,3), 0)

    #Otsu Threshold
    val, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    #Dilation
    kernel = np.ones((15,15), np.uint8)
    dilation = cv2.dilate(thresh, kernel, iterations=1)

    #Create breast mask
    contours, hierarchy= cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    biggestContour = max(contours, key = cv2.contourArea)
    breastMask = cv2.drawContours(np.zeros(preprocessedImage.shape, np.uint8), [biggestContour], -1, 255, -1)

    #Breast removal
    result = cv2.bitwise_and(preprocessedImage, preprocessedImage, mask=breastMask)

    return result, breastMask

def adjustContrastAndBrightness(contrast, brightness, image):
    imgContrast = np.zeros(image.shape, image.dtype)
    for x in range(imgContrast.shape[0]):
        for y in range(imgContrast.shape[1]):
            imgContrast[y,x] = np.clip(contrast*image[y,x] + brightness, 0, 255)
    return imgContrast

def threshold(image, threshValue):
    equalizedHist = cv2.equalizeHist(image)
    #abnormality thresholding
    val, thresh = cv2.threshold(equalizedHist, threshValue, 255, cv2.THRESH_BINARY)

    return thresh

def openingMorphology(image, kernel):
    erodedImage = erode(image, kernel, 2)
    dilatedImage = dilate(erodedImage, kernel, 2)

    return dilatedImage

def dilate(image, KernelLenght, it):
    #Dilation
    kernel = np.ones((KernelLenght,KernelLenght), np.uint8)
    dilation = cv2.dilate(image, kernel, iterations=it)

    return dilation

def erode(image, KernelLenght, it):
    #Dilation
    kernel = np.ones((KernelLenght,KernelLenght), np.uint8)
    erode = cv2.erode(image, kernel, iterations=it)

    return erode

def dilateBreast(preprocessedImage, mask):
    #Breast removal
    result = cv2.bitwise_and(preprocessedImage, preprocessedImage, mask=mask)

    return result

def segmentAbnormality(inputImage, binaryImage, color):
    #Canny to identify edges
    canny = cv2.Canny(binaryImage, 0, 255)

    #Resize to original Image size
    cannyResized = cv2.resize(canny, [1024, 1024])

    #Create Canny Edges mask
    cannyBGR = cv2.cvtColor(cannyResized, cv2.COLOR_GRAY2BGR)       #convert to bgr
    cannyBGR *= np.array(color, np.uint8)                       

    finalImage = cv2.addWeighted(inputImage, 1.0, cannyBGR, 1.0, 0, 0)
    finalImage = cv2.cvtColor(finalImage, cv2.COLOR_BGR2RGB)
    return finalImage, cannyResized

def calculateMetrics(edges, image):
    img = image.copy()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #Find contours
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    results = []
    for index, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        (x,y), radius = cv2.minEnclosingCircle(cnt)
        print("Objeto %d: Area: %d px*px | Center: ( %d, %d) | Radius: %d" %(index, area, x, image.shape[1]-y, radius))
        #Write results
        r = [str(index), str(int(area)), str(int(x)), str(int(y)), str(int(radius))]

        results.append(r)

        #Draw circles and write detection index
        cv2.circle (img,(int(x),int(y)),int(radius),(210,30,0),2)
        cv2.putText(img, str(index), (int(x),int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (210,30,0), 2)
    return img, results

#------------------------------------------------------------------------
#                           Other functions
#------------------------------------------------------------------------

def showImages(images, titles, rows, columns):
    fig = plt.gcf()
    fig.set_size_inches(18,12)
    for i in range(rows*columns):
        plt.subplot(rows, columns, i + 1)
        plt.imshow(cv2.cvtColor(images[i], cv2.COLOR_BGR2RGB), cmap = 'gray')
        plt.title(titles[i])
        plt.xticks([]),plt.yticks([])
    plt.show()

def writeResults(filePath, imageName, edges):
    #opening the file
    file = open(file=filePath, mode='a')

    file.write("\nIMAGEM:"+ imageName)
    #Find contours
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for index, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        (x,y), radius = cv2.minEnclosingCircle(cnt)
        file.write("\n\t\tObjeto %d: Area: %d px*px | Center: (%d, %d) | Radius: %d" %(index, area, x, 1024-y, radius))

    file.close()

def processImage(path, savePath, filename, inputFileFormat, exportFormat):
    #------------------- Acquisition Step --------------------------
   
    img = cv2.imread(path+filename+inputFileFormat)

    #----------------- Pre Processing Step--------------------------

    preprocessedImage = preprocessImage(img.copy())

    #------------------- Segmentation Step -------------------------

    segmentedBreastImage, mask = segmentBreast(preprocessedImage)

    #------------------- Feature Extraction Step -------------------
    
    thresholdedImage = threshold(segmentedBreastImage, 220)
    openingMorphImage = openingMorphology(thresholdedImage, 5)
    
    #---------- 4 - INTERPRETAÇÃO -----------------------------------

    final, edges = segmentAbnormality(img, openingMorphImage, (0,1,1))
    cv2.imwrite(savePath+filename+exportFormat, final)
    writeResults(savePath+"results.txt", filename, edges)

def processAllMiasImages(path, savePath):
    for i in range(1,323):
        filename = "mdb00"
        inputType = ".pgm"
        exportType = ".jpg"
        if i < 10:
            filename = "mdb00" + str(i)
        elif i < 100:
            filename = "mdb0" +  str(i) 
        else: 
            filename = "mdb" +  str(i) 
        processImage(path, savePath, filename, inputType, exportType)

#processAllMiasImages("mias_database/", "results/")
#processImage("mias_database/", "results/", "mdb184", ".pgm", ".png")



