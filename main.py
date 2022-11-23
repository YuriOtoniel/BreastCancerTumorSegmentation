from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk
import cv2
import imutils
import os
import TumorSegmentationWrapper as tsw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

window = Tk()

#additional function to convert millimeters to points
def mm2pt(mm):
    return mm/0.352777

class application():
    def __init__(self):
        self.window = window
        self.dpi = tsw.TumorSegmentationWrapper()
        self.screen()
        self.frames()
        self.components()
        self.reset()
        window.mainloop()
    
    def screen(self):
        self.window.title("SEGMENTAÇÃO EM MAMOGRAFIAS")
        self.window.configure(background= '#282A36')
        self.window.geometry("1024x768")
        self.window.resizable(True, True)
        self.window.minsize(width=1024, height=768)
        self.window.state("zoomed")
                
    def frames(self):
        #Input Image Area
        self.frame1 = Frame(self.window, bd = 4, bg = '#282A36')
        self.frame1.place(relx= 0.01 , rely=0.01, relwidth= 0.38,relheight= 0.98)

        #Output Image Area
        self.frame2 = Frame(self.window, bd=4, bg='#282A36')
        self.frame2.place(relx=0.40, rely=0.01, relwidth=0.38, relheight=0.98)

        #Navigation Area
        self.frame3 = Frame(self.window, bd=4, bg='#282A36',
                            highlightbackground='#44475a', highlightthickness=3)
        self.frame3.place(relx=0.79, rely=0.01, relwidth=0.20, relheight=0.98)

    def disableAllButtons(self):
        self.bt_segmentBreast.config(state="disabled", bg="#44475a")
        self.bt_dilate.config(state="disabled", bg="#44475a")
        self.bt_skipContrastBrightness.config(state="disabled", bg="#44475a")
        self.bt_applyContrastBrightness.config(state="disabled", bg="#44475a")
        self.bt_applyThresh.config(state="disabled", bg="#44475a")
        self.bt_applyOpnMorph.config(state="disabled", bg="#44475a")
        self.bt_segmentTumor.config(state="disabled", bg="#44475a")
        self.bt_saveTumorSegmentation.config(state="disabled", bg="#44475a")
        self.bt_generateReport.config(state="disabled", bg="#44475a")

    def showImage(self, image, label):
        lb_width = label.winfo_width()
        lb_height = label.winfo_height()
        image = imutils.resize(image, height= lb_height)

        image = imutils.resize(image, width=lb_width)
        im = Image.fromarray(image)
        img = ImageTk.PhotoImage(image=im)

        label.configure(image=img)
        label.image = img

    def openImage(self):
        path_image = filedialog.askopenfilename(filetypes= [
            (".jpg", ".jpg" ),
            (".jpeg", ".jpeg"),
            (".png", ".png")
        ])
        if len(path_image) > 0:
            self.disableAllButtons()

            #New empty object
            self.dpi = tsw.TumorSegmentationWrapper()

            #Loading image
            self.dpi.loadInputImageFromPath(path=path_image)
            self.showImage(self.dpi.inputImage, self.lb_inputImage)

            #Activate next button
            self.bt_segmentBreast.config(state="normal", bg= "#50fa7b")

            #Reset output label
            self.lb_outputImage.image = None

    def segmentBreast(self):
        #button activation logic
        self.disableAllButtons()
        self.bt_segmentBreast.config(state="normal", bg= "#50fa7b")

        #Add Loading label until the operation ends
        self.lbLoading = Label(self.frame2, text="Loading... Please Wait", fg="#ff5555", bg="#282A36")
        self.lbLoading.place(relx=0, rely=0, relheight=0.99, relwidth=0.99, anchor="nw")
        self.window.update()

        #processing
        self.dpi.segmentBreast()

        #Remove Loading label and show image
        self.lbLoading.place_forget()
        self.showImage(self.dpi.outputBreastSegmentation, self.lb_outputImage)

        #activate next button
        self.bt_dilate.config(state="normal", bg= "#50fa7b")

    def showDilate(self):
        #button logic
        self.disableAllButtons()
        self.bt_segmentBreast.config(state="normal", bg= "#50fa7b")
        self.bt_dilate.config(state="normal", bg= "#50fa7b")

        kernel = self.sc_dilate.get()
        
        #Add Loading label until the operation ends
        self.lbLoading = Label(self.frame2, text="Loading... Please Wait", fg="#ff5555", bg="#282A36")
        self.lbLoading.place(relx=0, rely=0, relheight=0.99, relwidth=0.99, anchor="nw")
        self.window.update()

        self.dpi.applyDilate(kernel)

        #Remove Loading and show image
        self.lbLoading.place_forget()
        self.showImage(self.dpi.outputBreastSegmentation, self.lb_outputImage)
        self.bt_skipContrastBrightness.config(state="normal", bg="#ffb86c")
        self.bt_applyContrastBrightness.config(state="normal", bg= "#50fa7b")

    def showOpeningMorphology(self):
        #button logic
        self.disableAllButtons()
        self.bt_segmentBreast.config(state="normal", bg= "#50fa7b")
        self.bt_dilate.config(state="normal", bg= "#50fa7b")
        self.bt_skipContrastBrightness.config(state="normal", bg="#ffb86c")
        self.bt_applyContrastBrightness.config(state="normal", bg= "#50fa7b")
        self.bt_applyThresh.config(state="normal", bg= "#50fa7b")
        self.bt_applyOpnMorph.config(state="normal", bg= "#50fa7b")

        kernel = self.sc_opnMorph.get()
        
        #Add Loading label until the operation ends
        self.lbLoading = Label(self.frame2, text="Loading... Please Wait", fg="#ff5555", bg="#282A36")
        self.lbLoading.place(relx=0, rely=0, relheight=0.99, relwidth=0.99, anchor="nw")
        self.window.update()

        self.dpi.applyOpeningMorphology(kernel)

        #Remove Loading label and show image
        self.lbLoading.place_forget()
        self.showImage(self.dpi.morphologyOperations, self.lb_outputImage)

        #Activate next button
        self.bt_segmentTumor.config(state="normal", bg= "#50fa7b")

    def showConstrastAndBrigtness(self):
        #button logic
        self.disableAllButtons()
        self.bt_segmentBreast.config(state="normal", bg= "#50fa7b")
        self.bt_dilate.config(state="normal", bg= "#50fa7b")
        self.bt_skipContrastBrightness.config(state="normal", bg="#ffb86c")
        self.bt_applyContrastBrightness.config(state="normal", bg= "#50fa7b")

        contrast = self.sc_contrast.get()
        brightness = self.sc_brightness.get()

        #Add Loading label until the operation ends
        self.lbLoading = Label(self.frame2, text="Loading... Please Wait", fg="#ff5555", bg="#282A36")
        self.lbLoading.place(relx=0, rely=0, relheight=0.99, relwidth=0.99, anchor="nw")
        self.window.update()

        self.dpi.applyContrastBrightness(contrast, brightness)

        #Remove Loading and show image
        self.lbLoading.place_forget()
        self.showImage(self.dpi.constrastBrightnessTumorSegmentation, self.lb_outputImage)
        self.bt_applyThresh.config(state="normal", bg= "#50fa7b")

    def showThreshold(self):
        #button logic
        self.disableAllButtons()
        self.bt_segmentBreast.config(state="normal", bg= "#50fa7b")
        self.bt_dilate.config(state="normal", bg= "#50fa7b")
        self.bt_skipContrastBrightness.config(state="normal", bg="#ffb86c")
        self.bt_applyContrastBrightness.config(state="normal", bg= "#50fa7b")
        self.bt_applyThresh.config(state="normal", bg= "#50fa7b")

        threshValue = self.sc_threshold.get()

        #Add Loading label until the operation ends
        self.lbLoading = Label(self.frame2, text="Loading... Please Wait", fg="#ff5555", bg="#282A36")
        self.lbLoading.place(relx=0, rely=0, relheight=0.99, relwidth=0.99, anchor="nw")
        self.window.update()

        self.dpi.applyThreshold(threshValue)

        #Remove Loading and show image
        self.lbLoading.place_forget()
        self.showImage(self.dpi.tumorThreshold, self.lb_outputImage)
        self.bt_applyOpnMorph.config(state="normal", bg= "#50fa7b")
    
    def segmentAbnormality(self):
        self.disableAllButtons()
        self.bt_segmentBreast.config(state="normal", bg= "#50fa7b")
        self.bt_dilate.config(state="normal", bg= "#50fa7b")
        self.bt_skipContrastBrightness.config(state="normal", bg="#ffb86c")
        self.bt_applyContrastBrightness.config(state="normal", bg= "#50fa7b")
        self.bt_applyThresh.config(state="normal", bg= "#50fa7b")
        self.bt_applyOpnMorph.config(state="normal", bg= "#50fa7b")
        self.bt_segmentTumor.config(state="normal", bg= "#50fa7b")

        #Add Loading label until the operation ends
        self.lbLoading = Label(self.frame2, text="Loading... Please Wait", fg="#ff5555", bg="#282A36")
        self.lbLoading.place(relx=0, rely=0, relheight=0.99, relwidth=0.99, anchor="nw")
        self.window.update()

        color = self.color.get()
        self.dpi.applyAbnormalityMask(color)

        #Remove Loading and show image
        self.lbLoading.place_forget()
        self.showImage(self.dpi.outputTumorSegmentation, self.lb_outputImage)
        self.bt_saveTumorSegmentation.config(state="normal", bg= "#0d88d9")
        self.bt_generateReport.config(state="normal", bg= "#50fa7b")

    def saveImage(self):
        path_image = filedialog.asksaveasfilename(filetypes= [
            (".jpg", ".jpg" ),
            (".jpeg", ".jpeg"),
            (".png", ".png")
        ], defaultextension=".jpg")

        if len(path_image) > 0:
            self.dpi.saveFile(path_image)

    def generatePDF(self):
        path_pdf = filedialog.asksaveasfilename(filetypes= [(".pdf", ".pdf" )], defaultextension=".pdf")
        try:
            path = os.path.dirname(__file__)
            cv2.imwrite(path+"aux1.jpeg", cv2.cvtColor(self.dpi.inputImage, cv2.COLOR_RGB2BGR))
            cv2.imwrite(path+"aux2.jpeg", cv2.cvtColor(self.dpi.outputTumorSegmentation, cv2.COLOR_RGB2BGR))
            cv2.imwrite(path+"aux3.jpeg", cv2.cvtColor(self.dpi.enumeratedOutput, cv2.COLOR_RGB2BGR))

            pdf = canvas.Canvas(path_pdf, pagesize=A4)
            print(path)
            pdf.setTitle("SEGMENTAÇÃO DE ANORMALIDADES EM MAMOGRAFIAS")
            pdf.drawString(mm2pt(20),mm2pt(287),"RESULTADOS DA SEGMENTAÇÃO")
            pdf.drawImage(path+"aux1.jpeg", mm2pt(45), mm2pt(152), mm2pt(125), mm2pt(125))
            pdf.drawImage(path+"aux2.jpeg", mm2pt(45), mm2pt(17), mm2pt(125), mm2pt(125))
            pdf.showPage()
            pdf.drawImage(path+"aux3.jpeg", mm2pt(20), mm2pt(97), mm2pt(170), mm2pt(170))
            results = self.dpi.textResults
            h = 87
            for r in results:
                if (h > 30):
                    pdf.drawString(mm2pt(20),mm2pt(h), "DETECÇÃO " + r[0])
                    pdf.drawString(mm2pt(35),mm2pt(h-10), "Área [px*px]: " + r[1])
                    pdf.drawString(mm2pt(35),mm2pt(h-20), "Raio [px]: " + r[4] + " Centro: (" + r[2] + "," + r[3] + ")")
                    h-=30
                else:
                    h = 287
                    pdf.showPage()
                    pdf.drawString(mm2pt(20),mm2pt(h), "DETECÇÃO " + r[0])
                    pdf.drawString(mm2pt(35),mm2pt(h-10), "Área [px*px]: " + r[1])
                    pdf.drawString(mm2pt(35),mm2pt(h-20), "Raio [px]: " + r[4] + " Centro: (" + r[2] + "," + r[3] + ")")
                    h -=30
            pdf.save()

        except:
            messagebox.showinfo(title="ERRO", message="Erro ao gerar o arquivo pdf, certifique-se que o arquivo desejado não esteja aberto em algum editor")

    def reset(self):
        self.disableAllButtons()

        #Apply default values
        self.sc_dilate.set(20)
        self.sc_contrast.set(1)
        self.sc_brightness.set(0)
        self.sc_threshold.set(220)
        self.sc_opnMorph.set(5)
        self.lb_inputImage.image = None
        self.lb_outputImage.image = None
        self.rb_cyan.select()

    def skipContrastAndBrightness(self):
        #button logic
        self.disableAllButtons()
        self.bt_segmentBreast.config(state="normal", bg= "#50fa7b")
        self.bt_dilate.config(state="normal", bg= "#50fa7b")
        self.bt_skipContrastBrightness.config(state="normal", bg="#ffb86c")
        self.bt_applyContrastBrightness.config(state="normal", bg= "#50fa7b")

        #copy image to next step result
        self.dpi.constrastBrightnessTumorSegmentation = self.dpi.outputBreastSegmentation

        self.bt_applyThresh.config(state="normal", bg= "#50fa7b")

    def components(self):
        #Frame 1 
        self.lb_inputImage = Label(self.frame1, bg="#282A36")
        self.lb_inputImage.place(relx=0.01, rely=0.07, relwidth=0.98, relheight=0.92)
        
        #Frame 2
        self.lb_outputImage = Label(self.frame2, bg="#282A36")
        self.lb_outputImage.place(relx=0.01, rely=0.07, relwidth=0.98, relheight=0.92)

        #Frame 3 
        #Header buttons
        self.bt_loadImage = Button(self.frame3, text="Carregar", command= self.openImage, fg="#f8f8f2", bg="#0d88d9", font="bold" )
        self.bt_loadImage.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.03)

        self.bt_segmentBreast = Button(self.frame3, text="Remover fundo", command= self.segmentBreast, 
                                        fg="#282A36", bg="#50fa7b", font="bold", disabledforeground="#f8f8f2")
        self.bt_segmentBreast.place(relx=0.51, rely=0.05, relwidth=0.48, relheight=0.03)

        self.bt_reset = Button(self.frame3, text="Reset", command= self.reset, 
                                        fg="#282A36", bg="#50fa7b", font="bold", disabledforeground="#f8f8f2")
        self.bt_reset.place(relx=0.01, rely=0.05, relwidth=0.48, relheight=0.03)

        #Dilate components
        self.lb_dilate= Label(self.frame3, text="Dilatação da Mama", fg="#f8f8f2", bg='#282A36', anchor="w", font="bold")
        self.lb_dilate.place(relx=0.01, rely=0.09, relwidth=0.98, relheight=0.02)

        self.sc_dilate = Scale(self.frame3, from_=3, to=30, orient= HORIZONTAL, resolution=1, 
                                fg="#f8f8f2", bg="#282A36", highlightbackground="#282A36", activebackground="#f1fa8c", troughcolor="#44475a")
        self.sc_dilate.place(relx=0.01, rely=0.12, relwidth=0.98, relheight=0.04)

        self.bt_dilate = Button(self.frame3, text="Dilatar", command= self.showDilate, 
                                    fg="#282A36", bg="#50fa7b", font="bold", disabledforeground="#f8f8f2")
        self.bt_dilate.place(relx=0.5, rely=0.17, relwidth=0.48, relheight=0.03)

        #Contrast and Brightness components
        self.lb_contrast = Label(self.frame3, text="Contraste", fg="#f8f8f2", bg='#282A36', anchor="w", font="bold")
        self.lb_contrast.place(relx=0.01, rely=0.21, relwidth=0.98, relheight=0.02)
        
        self.sc_contrast = Scale(self.frame3, from_=0, to=3, orient= HORIZONTAL, resolution=0.05,
                                     fg="#f8f8f2", bg="#282A36", highlightbackground="#282A36", activebackground="#f1fa8c", troughcolor="#44475a")
        self.sc_contrast.place(relx=0.01, rely=0.24, relwidth=0.98, relheight=0.04)
        
        self.lb_brightness = Label(self.frame3, text="Brilho", fg="#f8f8f2", bg='#282A36', anchor="w", font="bold")
        self.lb_brightness.place(relx=0.01, rely=0.29, relwidth=0.98, relheight=0.02)
        
        self.sc_brightness = Scale(self.frame3, from_=-100, to=100, orient= HORIZONTAL, resolution=0.1,
                                    fg="#f8f8f2", bg="#282A36", highlightbackground="#282A36", activebackground="#f1fa8c", troughcolor="#44475a")
        self.sc_brightness.place(relx=0.01, rely=0.33, relwidth=0.98, relheight=0.04)

        self.bt_skipContrastBrightness = Button(self.frame3, text="Pular", command= self.skipContrastAndBrightness,
                                         fg="#282A36", bg="#ffb86c", font="bold", disabledforeground="#f8f8f2")
        self.bt_skipContrastBrightness.place(relx=0.01, rely=0.38, relwidth=0.48, relheight=0.03)

        self.bt_applyContrastBrightness = Button(self.frame3, text="Aplicar", command= self.showConstrastAndBrigtness,
                                         fg="#282A36", bg="#50fa7b", font="bold", disabledforeground="#f8f8f2")
        self.bt_applyContrastBrightness.place(relx=0.5, rely=0.38, relwidth=0.48, relheight=0.03)

        #Thresholding components
        self.lb_threshold= Label(self.frame3, text="OTSU Threshold", fg="#f8f8f2", bg='#282A36', anchor="w", font="bold")
        self.lb_threshold.place(relx=0.01, rely=0.42, relwidth=0.98, relheight=0.02)

        self.sc_threshold = Scale(self.frame3, from_=0, to=255, orient= HORIZONTAL, resolution=1,
                                    fg="#f8f8f2", bg="#282A36", highlightbackground="#282A36", activebackground="#f1fa8c", troughcolor="#44475a")
        self.sc_threshold.place(relx=0.01, rely=0.45, relwidth=0.98, relheight=0.04)
        
        self.bt_applyThresh = Button(self.frame3, text="Aplicar", command= self.showThreshold, 
                                        fg="#282A36", bg="#50fa7b", font="bold", disabledforeground="#f8f8f2")
        self.bt_applyThresh.place(relx=0.5, rely=0.50, relwidth=0.48, relheight=0.03)

        #Opening Morphology components
        self.lb_opnMorph= Label(self.frame3, text="Morfologia de abertura", fg="#f8f8f2", bg='#282A36', anchor="w", font="bold")
        self.lb_opnMorph.place(relx=0.01, rely=0.54, relwidth=0.98, relheight=0.02)

        self.sc_opnMorph = Scale(self.frame3, from_=3, to=30, orient= HORIZONTAL, resolution=1, 
                                fg="#f8f8f2", bg="#282A36", highlightbackground="#282A36", activebackground="#f1fa8c", troughcolor="#44475a")
        self.sc_opnMorph.place(relx=0.01, rely=0.57, relwidth=0.98, relheight=0.04)

        self.bt_applyOpnMorph = Button(self.frame3, text="Aplicar", command= self.showOpeningMorphology, 
                                        fg="#282A36", bg="#50fa7b", font="bold", disabledforeground="#f8f8f2")
        self.bt_applyOpnMorph.place(relx=0.5, rely=0.62, relwidth=0.48, relheight=0.03)

        #Color radio buttons
        self.lb_Color= Label(self.frame3, text="Cor", fg="#f8f8f2", bg='#282A36', anchor="w", font="bold")
        self.lb_Color.place(relx=0.01, rely=0.66, relwidth=0.98, relheight=0.02)

        self.color = IntVar()

        self.rb_blue = Radiobutton(self.frame3, text="Azul",fg="#282A36", bg="#44475a", selectcolor='#80b3ff', indicatoron=0,   font="bold", variable=self.color, value=0)
        self.rb_blue.place(relx=0.01, rely=0.69, relwidth=0.48, relheight=0.03)

        self.rb_green = Radiobutton(self.frame3, text="Verde", fg="#282A36", bg="#44475a", selectcolor='#50fa7b', indicatoron=0, font="bold", variable=self.color, value=1)
        self.rb_green.place(relx=0.01, rely=0.73, relwidth=0.48, relheight=0.03)

        self.rb_red = Radiobutton(self.frame3, text="Red", fg="#282A36", bg="#44475a", selectcolor='#ff5555', indicatoron=0, font="bold", variable=self.color, value=2)
        self.rb_red.place(relx=0.01, rely=0.77, relwidth=0.48, relheight=0.03)

        self.rb_cyan = Radiobutton(self.frame3, text="Ciano",fg="#282A36", bg="#44475a", selectcolor='#8be9fd', indicatoron=0, font="bold", variable=self.color, value=3)
        self.rb_cyan.place(relx=0.51, rely=0.69, relwidth=0.48, relheight=0.03)

        self.rb_yellow = Radiobutton(self.frame3, text="Amarelo", fg="#282A36", bg="#44475a", selectcolor='#f1fa8c', indicatoron=0, font="bold", variable=self.color, value=4)
        self.rb_yellow.place(relx=0.51, rely=0.73, relwidth=0.48, relheight=0.03)

        self.rb_magenta = Radiobutton(self.frame3, text="Magenta", fg="#282A36", bg="#44475a", selectcolor='#ff19ff', indicatoron=0, font="bold", variable=self.color, value=5)
        self.rb_magenta.place(relx=0.51, rely=0.77, relwidth=0.48, relheight=0.03)

        #default color
        self.rb_cyan.select()

        #Footer buttons
        self.bt_segmentTumor = Button(self.frame3, text="Segmentar", command= self.segmentAbnormality,  fg="#282A36", bg="#50fa7b", font="bold", disabledforeground="#f8f8f2")
        self.bt_segmentTumor.place(relx=0.01, rely=0.92, relwidth=0.48, relheight=0.03)

        self.bt_saveTumorSegmentation = Button(self.frame3, text="Salvar", command=self.saveImage,  fg="#f8f8f2", bg="#0d88d9", font="bold", disabledforeground="#f8f8f2")
        self.bt_saveTumorSegmentation.place(relx=0.51, rely=0.92, relwidth=0.48, relheight=0.03)

        self.bt_generateReport = Button(self.frame3, text="Gerar Relatório", command=self.generatePDF, fg="#282A36", bg="#50fa7b", font="bold", disabledforeground="#f8f8f2")
        self.bt_generateReport.place(relx=0.01, rely=0.96, relwidth=0.98, relheight=0.03)

application()