import Tkinter as tk
from Tkinter import *
import cv2
import glob
import time
from PIL import ImageTk
from PIL import Image
from tkFileDialog import *

import os

class PictureTagger(tk.Tk):
    def __init__(self,inputDirectory="frames"):
        tk.Tk.__init__(self)

        self.timestring = time.strftime("%Y%m%d-%H%M%S")
        self.directory_name = "OUT_" + str(self.timestring)
        if not os.path.exists(self.directory_name):
            os.makedirs(self.directory_name)
        self.boxes = []
        self.objects_pointers = []
        self.input_directory= inputDirectory

        #print(input_directory)
        #IMAGE ARRAY
        self.cv_img = []
        self.cv_img = glob.glob(self.input_directory + '/*.jpg')
        self.cv_img.sort()

        #COUNTERS
        self.max_counter = len(self.cv_img)
        self.counter = 0
        self.count_positive = 0
        self.count_negative = 0

        #read first image
        self.image = cv2.imread(self.cv_img[self.counter])
        #rearrange color channel
        self.printableImage = self.returnPrintableImage(self.image)

        #inherit size for canvas from image
        self.y, self.x = self.image.shape[:2]

        #App customization
        self.title("PictureTagger v1.1")

        #DRAG AND RECTANGLE COORDS
        self.recx = 0
        self.recy = 0

        #PICTURE FRAME
        self.pictureFrame = Frame(self)
        self.Backwards = Button(self.pictureFrame, text='<', command=lambda: self.leftKeyPress())
        self.canvas = tk.Canvas(self.pictureFrame, width=self.x, height=self.y, cursor="cross")
        self.canvas.create_image(0, 0, image=self.printableImage, anchor='nw')
        self.Forward = Button(self.pictureFrame, text='>', command=lambda: self.rightKeyPress())

        #BUTTONS FRAME
        self.buttonsFrame = Frame(self)
        self.SavePositiveFrame = Button(self.buttonsFrame, text='Save Positive Frame (S)', command=lambda: self.savePositiveFrame())
        self.SaveNegativeFrame = Button(self.buttonsFrame, text='Save Negative Frame (N)', command=lambda: self.saveNegativeFrame())
        self.ClearFrame = Button(self.buttonsFrame, text='Clear Frame (D)', command=lambda: self.clearFrame())
        self.UndoRectangle = Button(self.buttonsFrame, text='Undo Last Rectangle (F)', command=lambda: self.undoRectangle())

        #LOGBOX FRAME
        self.logBoxFrame = Frame(self)
        self.logBox = Text(self.logBoxFrame, height=10, width=self.y/3)
        self.scrollbarLogBox = Scrollbar(self.logBoxFrame)
        self.logBox.config(yscrollcommand=self.scrollbarLogBox.set)
        self.scrollbarLogBox.config(command=self.logBox.yview)

        #GRID TIME
        #BUTTONS FRAME
        self.SavePositiveFrame.grid(row=0, column=0, padx=(10, 10))
        self.SaveNegativeFrame.grid(row=0, column=1, padx=(10, 10))
        self.ClearFrame.grid(row=0, column=2, padx=(10, 10))
        self.UndoRectangle.grid(row=0, column=3, padx=(10, 10))


        #PICTURE FRAME
        self.Backwards.grid(row=0,column=0)
        self.canvas.grid(row=0,column=2)
        self.Forward.grid(row=0,column=3)

        #LOG BOX FRAME
        self.logBox.grid(row=0, column=0)
        self.scrollbarLogBox.grid(row=0,column=1)

        #FRAME LAYOUT
        self.pictureFrame.grid(row=0)
        self.buttonsFrame.grid(row=1)
        self.logBoxFrame.grid(row=2)

        #BINDS
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.bind("<Left>",self.leftKeyPress)
        self.bind("<Right>", self.rightKeyPress)

        self.appendLog("Init")
        self.appendLog("Input directory " + self.input_directory)
        self.appendLog("Output directory " + self.directory_name)
    def undoRectangle(self):
        if (len(self.objects_pointers) >= 1):
            if (len(self.objects_pointers) == 1):
                self.canvas.delete(self.objects_pointers[-1])
                self.objects_pointers.pop()
                self.boxes.pop()
                self.appendLog("No more rectangles on frame.")
            else:
                self.canvas.delete(self.objects_pointers[-1])
                self.objects_pointers.pop()
                self.boxes.pop()
                self.appendLog("Remaining rectangles count - " + str(len(self.objects_pointers)))
                for box in self.boxes:
                    self.appendLog( str(box))
        else:
            self.appendLog("No more rectangles on frame.")
    def on_button_press(self, event):
        self.recx = event.x
        self.recy = event.y

    def on_button_release(self, event):
        x0,y0 = (self.recx, self.recy)
        x1,y1 = (event.x, event.y)
        self.objects_pointers.append(self.canvas.create_rectangle(x0,y0,x1,y1,width=3, outline="red"))
        self.boxes.append((x0,y0,x1,y1))
        self.appendLog("Drawn rectangle : " + str((x0,y0,x1,y1)))

    def leftKeyPress(self,a="",b=""):
        self.counter -= 1
        if (self.counter < 0):
            self.counter = self.max_counter -1
        self.image = cv2.imread(self.cv_img[self.counter])
        self.printableImage = self.returnPrintableImage(self.image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.printableImage, anchor='nw')
        self.appendLog("Backward frame")

    def rightKeyPress(self,a="",b=""):
        self.counter+=1
        if (self.counter >= self.max_counter):
            self.counter = 0
        self.image = cv2.imread(self.cv_img[self.counter])
        self.printableImage = self.returnPrintableImage(self.image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.printableImage, anchor='nw')
        self.appendLog("Forward frame")

    def returnPrintableImage(self,image):
        #converts opencv image from bgr to rgb and generates tk compat image
        b, g, r = cv2.split(image)
        printableImage = cv2.merge((r, g, b))
        printableImage = Image.fromarray(printableImage)
        printableImage = ImageTk.PhotoImage(printableImage)
        return printableImage

    def appendLog(self, quote):
        textToAppend = "[INFO] [" + str(time.strftime("%Y-%m-%d-%H:%M:%S")) + " ] [ " + quote + " ] \n"
        self.logBox.insert('1.0', textToAppend)
    def clearFrame(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.printableImage, anchor='nw')
        self.boxes = []
        self.objects_pointers = []
        self.appendLog("Frame clear")
    def saveNegativeFrame(self):
        self.count_negative += 1
        cv2.imwrite(self.directory_name+"/negative_frame_%d.jpg" % self.count_negative, self.image)  # save frame as JPEG file
        file = open(self.directory_name+"/"+self.timestring + "_negative.txt", "a")
        outputString = ""
        outputString += "negative_frame_%d.jpg" % (self.count_negative)
        outputString += "\n"
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.printableImage, anchor='nw')
        self.boxes = []
        self.objects_pointers = []
        file.write(outputString)
        file.close()
        self.appendLog("Saved negative frame " + str("negative_frame_%d.jpg" % self.count_negative))
        self.clearFrame()
        self.rightKeyPress()
    def savePositiveFrame(self):
        outputString = ""
        self.count_positive += 1
        outputString += "positive_frame_%d.jpg %d" % (self.count_positive, len(self.objects_pointers))
        cv2.imwrite(self.directory_name+"/positive_frame_%d.jpg" % self.count_positive, self.image)  # save frame as JPEG file
        file = open(self.directory_name + "/" + self.timestring + ".txt", "a")
        for box in self.boxes:
            outputString += " %d %d %d %d" % (box[0], box[1], box[2], box[3])
        outputString += "\n"
        file.write(outputString)
        file.close()
        self.appendLog("Saved positive frame " + str("positive_frame_%d.jpg" % self.count_positive))
        self.clearFrame()
        self.leftKeyPress()
    def pressed(self):
        print("PRESSED")


def main():
    root = Tk()
    root.iconify()
    os.path.basename(askdirectory(title='Choose an input directory for images', mustexist=1))
    root.destroy()
    app = PictureTagger()
    app.mainloop()

if __name__ == "__main__":
    main()
