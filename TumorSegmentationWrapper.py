import cv2
import DigitalImageProcessing as dpi


class TumorSegmentationWrapper():
    def __init__(self, inputImage = None):
        self.inputImage = inputImage
        self.preprocessedImage = None
        self.breastMask = None
        self.outputBreastSegmentation = None
        self.constrastBrightnessTumorSegmentation = None
        self.tumorThreshold = None
        self.morphologyOperations = None
        self.edges = None
        self.outputTumorSegmentation = None
        self.enumeratedOutput = None

    def loadInputImageFromPath(self, path):
        self.inputImage = cv2.imread(path)
        self.preprocessedImage = dpi.preprocessImage(self.inputImage)

    def segmentBreast(self):
        output, mask = dpi.segmentBreast(self.preprocessedImage)
        self.outputBreastSegmentation = output
        self.breastMask = mask

    def applyContrastBrightness(self, contrast, brightness):
        """ Adjust contrast and brightness levels in a image."""
        output = dpi.adjustContrastAndBrightness(contrast, brightness, self.outputBreastSegmentation)
        self.constrastBrightnessTumorSegmentation = output

    def applyThreshold(self,thresh):
        output = dpi.threshold(self.constrastBrightnessTumorSegmentation, thresh)
        self.tumorThreshold = output

    def applyDilate(self, kernel):
        mask = dpi.dilate(self.breastMask, kernel, 1)
        self.outputBreastSegmentation = dpi.dilateBreast(self.preprocessedImage, mask)

    def applyOpeningMorphology(self, kernel):
        output = dpi.openingMorphology(self.tumorThreshold, kernel)
        self.morphologyOperations = output

    def applyAbnormalityMask(self, op):
        color = None
        if op == 0:
            color = (1,0,0)
        elif op == 1:
            color = (0,1,0)
        elif op == 2:
            color = (0,0,1)
        elif op == 3:
            color = (1,1,0)
        elif op == 4:
            color = (0,1,1)
        elif op == 5:
            color = (1,0,1)
        output, edges = dpi.segmentAbnormality(self.inputImage, self.morphologyOperations, color)
        img, results = dpi.calculateMetrics(edges, self.inputImage)
        self.outputTumorSegmentation = output
        self.enumeratedOutput = img
        self.textResults = results
        self.edges = edges

    def saveFile(self, path):
        cv2.imwrite(path, cv2.cvtColor(self.outputTumorSegmentation, cv2.COLOR_RGB2BGR))
