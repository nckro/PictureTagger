import cv2
import glob
import time

boxes = []
objects_pointers = []

# OUR ARRAY FOR IMAGES
cv_img = []
cv_img = glob.glob('frames/*.jpg')
cv_img.sort()
max_counter = len(cv_img)
counter=0

image=cv2.imread(cv_img[counter])
success = 1

count = 0
count_negative = 0
stop_var = 0
mouse_down = 0

timestring = time.strftime("%Y%m%d-%H%M%S")


def printHelp():
    print "[HOW TO USE]"
    print " [LEFT_ARROW] / [RIGHT_ARROW]  - frame before / frame next"
    print " [S] - save positive frame with rectangles"
    print " [N] - save positive frame with rectangles"
    print " [D] - clear all rectangles"
    print " [F] - undo last rectangle"
    print " [ESC] - exit"

#function to clear boxes drawn and empty objects_pointer stack
def clearFrame(backupFrame):
    global image
    cv2.imshow("w1", backupFrame)
    image = backupFrame.copy()
    objects_pointers = []
    print "[INFO] (" + str(time.strftime("%Y-%m-%d-%H:%M:%S")) + ") Frame Cleared"
#function to save snap frame from video and add path to file alongside object count and positions
def saveFrame(frame):
    global count
    global objects_pointers
    outputString = ""
    count+= 1
    outputString+= "positive_frame_%d.jpg %d" % (count,count)
    cv2.imwrite("positive_frame_%d.jpg" % count, frame)  # save frame as JPEG file
    file = open(timestring+".txt", "a")
    for objectPointer in objects_pointers:
        outputString+= " %d %d %d %d" % (objectPointer[0],objectPointer[1],objectPointer[2],objectPointer[3])
    outputString += "\n"
    file.write(outputString)
    file.close()
    print "[INFO] (" + str(time.strftime("%Y-%m-%d-%H:%M:%S")) + ") Saved frame " + str("positive_frame_%d.jpg" % count)
    objects_pointers = []
    clearFrame(frame)
    nextFrame()

def saveFrameNegative(frame):
    global count_negative
    count_negative += 1
    cv2.imwrite("negative_frame_%d.jpg" % count_negative, frame)  # save frame as JPEG file
    file = open(timestring + "_negative.txt", "a")
    outputString = ""
    outputString += "negative_frame_%d.jpg" % (count_negative)
    outputString += "\n"
    objects_pointers = []
    file.write(outputString)
    file.close()
    print "[INFO] (" + str(time.strftime("%Y-%m-%d-%H:%M:%S")) + ") Saved frame " + str("negative_frame_%d.jpg" % count_negative)
    clearFrame(frame)
    nextFrame()
def nextFrame():
    global counter, backup_img
    counter += 1
    #print(counter)
    if (counter >= max_counter):
        counter = 0
        print(counter)
    image = cv2.imread(cv_img[counter])
    backup_img = image.copy()
    cv2.imshow("w1", image)
    print "[INFO] (" + str(time.strftime("%Y-%m-%d-%H:%M:%S")) + ") Next frame"
def undoLastRectangle():
    global objects_pointers, backup_img, image
    image_undo = backup_img.copy()
    color = (100, 255, 100)
    outputString = ""
    if(len(objects_pointers) >= 1):
        if(len(objects_pointers) == 1):
            objects_pointers.pop()
            cv2.imshow("w1", image_undo)
            print "[INFO] (" + str(time.strftime("%Y-%m-%d-%H:%M:%S")) + ") No remaining rectangle "
        else:
            objects_pointers.pop()
            #print "---------------------LEN"
            #print len(objects_pointers)
            print "[INFO] (" + str(time.strftime("%Y-%m-%d-%H:%M:%S")) + ") Remaining rectangle count -  " + str(len(objects_pointers))
            for objectPointer in objects_pointers:
                outputString = " %d %d %d %d" % (objectPointer[0], objectPointer[1], objectPointer[2], objectPointer[3])
                #print "--------" + outputString + "\n"
                r_start = (objectPointer[0], objectPointer[1])
                r_end = (objectPointer[2], objectPointer[3])
                outputString = " %s %s " % (r_start,r_end)
                #print "--------" + outputString + "\n"
                cv2.rectangle(image_undo, r_start, r_end, color, 2)
                cv2.imshow("w1", image_undo)
                print "[INFO] (" + str(time.strftime("%Y-%m-%d-%H:%M:%S")) + ") Remaining rectangle " + str(outputString)
    else:
        cv2.imshow("w1", image_undo)
        print "[INFO] (" + str(time.strftime("%Y-%m-%d-%H:%M:%S")) + ") No remaining rectangle "
    image = image_undo.copy()
def onMouse(event, x, y, flags, param):
    # onMouse function for drawing rectangles on video frame
    global mouse_down
    # we tell python that mouse_down variable is global
    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_down = 1
        #print 'Start Mouse Position: ' + str(x) + ', ' + str(y)
        sbox = [x, y]
        boxes.append(sbox)
    elif event == cv2.EVENT_LBUTTONUP:
        mouse_down = 0
        #print 'End Mouse Position: ' + str(x) + ', ' + str(y)
        ebox = [x, y]
        boxes.append(ebox)
        color = (100, 255, 100)
        #print "boxes[-2][0]=" + str(boxes[-2][0]) + "boxes[-2][1]=" + str(boxes[-2][1])
        #print " ### ### ###\n"
        #print "boxes[-1][0]=" + str(boxes[-1][0]) + "boxes[-1][1]=" + str(boxes[-1][1])
        rect_start=(boxes[-2][0],boxes[-2][1])
        rect_end=(boxes[-1][0],boxes[-1][1])
        object_pointer = (boxes[-2][0],boxes[-2][1],boxes[-1][0],boxes[-1][1])
        objects_pointers.append(object_pointer)
        cv2.rectangle(image, rect_start, rect_end, color,2)
        cv2.imshow("w1", image)
        outputString = " %s %s " % (rect_start, rect_end)
        print "[INFO] (" + str(time.strftime("%Y-%m-%d-%H:%M:%S")) + ") New rectangle " + str(outputString)
        boxes.pop()
        boxes.pop()



cv2.namedWindow("w1")
cv2.setMouseCallback('w1',onMouse)
printHelp()
#print("---------------------------------")
#print(counter)
print "[INFO] (" + str(time.strftime("%Y-%m-%d-%H:%M:%S")) + ") Start "
image = cv2.imread(cv_img[counter])
backup_img = image.copy()
cv2.imshow("w1", image)

old_rest = 0
while success:
    res = cv2.waitKey(1)
    if(old_rest != res):
        #print res
        old_rest = res
    if res == 27:
        break
    if res == 65363:
        counter+=1
        #print(counter)
        if(counter >= max_counter):
            counter = 0
            #print(counter)
        image = cv2.imread(cv_img[counter])
        backup_img = image.copy()
        cv2.imshow("w1", image)
        print "[INFO] (" + str(time.strftime("%Y-%m-%d-%H:%M:%S")) + ") Frame after"
    if res == 65361:
        counter-=1
        #print(counter)
        if (counter < 0):
            counter = max_counter-1
            #print(counter)
        image = cv2.imread(cv_img[counter])
        backup_img = image.copy()
        cv2.imshow("w1", image)
        print "[INFO] (" + str(time.strftime("%Y-%m-%d-%H:%M:%S")) + ") Frame before"
    if res == ord('d'):
        clearFrame(backup_img)
    if res == ord('s'):
        saveFrame(backup_img)
    if res == ord('n'):
        saveFrameNegative(backup_img)
    if res == ord('f'):
        undoLastRectangle()
