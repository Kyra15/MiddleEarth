# import necessary libraries and functions from other files
import cv2
from processing import process


# create video capture object
video = cv2.VideoCapture(0)

while video.isOpened():
    # read each frame
    ret, img = video.read()
    if ret:

        # detect and draw the Hough Lines P by calling the center function
        final = process(img)

        # show the frame
        cv2.imshow("Detected Frame", final)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# stop the video capture object and destroy all the open cv windows
video.release()
cv2.destroyAllWindows()
