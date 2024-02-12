import cv2
import numpy as np
import math


# applies the filters for grayscale, gaussian blur, thresholding, canny edge,
# and a rectangle mask onto the frame given
def filters(pic):
    bw = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(bw, 165, 255, cv2.THRESH_BINARY)[1]
    cv2.imshow("thresh", thresh)
    canny_gauss_bw = cv2.Canny(thresh, 150, 200, apertureSize=3, L2gradient=True)
    cv2.imshow("canny", canny_gauss_bw)
    mask = np.zeros(pic.shape[:2], dtype="uint8")
    cv2.rectangle(mask, (500, 100), (1300, 1000), 255, -1)
    masked = cv2.bitwise_and(canny_gauss_bw, canny_gauss_bw, mask=mask)
    return masked


# finds slopes that are similar to the most common slope and returns those lines
def find_similar(lines, slopes, most):
    good_lines = []
    rounded = []
    for x in slopes:
        try:
            x = round(x)
            rounded.append(x)
        except OverflowError:
            rounded.append(99)

    # if the slope is horizontal, then make it so that the slopes have to be within 2 of the most common slope
    for i in range(len(lines)):
        # if -5 <= rounded[i] <= 5:
        #     increment = 2
        # # otherwise, make it so the slopes have to be within 100 of the most common slope
        # # this is because vertical slopes have a higher margin of error and will vary more greatly with small movements
        # # whereas horizontal slopes will have a small variation
        # else:
        #     increment = 60
        try:
            if abs(rounded[i] - rounded[i + 1]) == 0:
                good_lines.append(lines[i])
                good_lines.append(lines[i + 1])
        except:
            continue
    return good_lines


# given a list, rounds all values and finds the most common value and returns that
# if all values are unique or occur the same number of times, average all the values together
def most_common(lst):
    rounded = []
    for x in lst:
        try:
            x = round(x)
        except OverflowError:
            x = 99
        rounded.append(x)

    count = 0
    common_things = set()

    for i in rounded:
        current = rounded.count(i)
        # if the current number of occurrences for the item is greater than the counter,
        # then set the counter to be that number and add the item to a set of common values
        if current > count:
            count = current
            common_things = {i}
        # otherwise, if the current number of occurrences for the item is equal to the counter,
        # add the item to the set of common values
        elif current == count:
            common_things.add(i)
    # if the count of everything is 1 (meaning everything is unique)
    # return the average of the values
    if count == 1:
        return sum(common_things) / len(common_things)
    # otherwise return the average of the most common values (can have multiple most common values)
    else:
        return round(sum(common_things) / len(common_things), 1)


# detect and output the lines and middle lines of the frame given
def center(og):
    # apply the filters and detect the lines with HoughLinesP
    frame = filters(og)
    lines = cv2.HoughLinesP(frame, rho=1, theta=np.pi / 180, threshold=100, minLineLength=50, maxLineGap=999)
    cv2.rectangle(og, (500, 100), (1300, 1000), 255, 10)
    slopes = []
    good = []
    # find the slopes of each line detected
    if lines is not None:
        for i in lines:
            x1, y1, x2, y2 = i[0]
            try:
                slopes.append(((y2 - y1) / (x2 - x1)))
            except RuntimeWarning or ZeroDivisionError:
                slopes.append(99)

        # find the most common slope in the frame
        freq = most_common(slopes)
        # find the lines with similar slopes to the most common slope and display them
        good_lines = find_similar(lines, slopes, freq)

        good_dist = []

        if good_lines is not None:

            # loop through the good lines from the slopes
            for i in good_lines:
                x1, y1, x2, y2 = i[0]
                print("lines", len(good_lines))

                # Initialize a variable to check if the lines are too close
                # find the distance between the new line points and the old line
                dist = any(
                    math.dist([x1, y1], [pt1[0], pt1[1]]) < 100 or
                    math.dist([x2, y2], [pt2[0], pt2[1]]) < 100
                    for pt1, pt2 in good_dist
                )

                # If the lines are farther than 100px apart, append the new lines to the new list
                # and draw the line on the image
                if not dist:
                    good_dist.append([[x1, y1], [x2, y2]])
                    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 10)

            # to prevent a divide by zero error, check to make sure that at least 1 line was detected
            # calculate the average of two of the endpoints of the outputted lines
            if good_dist is not None:
                print("dist", len(good_dist))
                for i in range(len(good_dist)):
                    cv2.line(og, (good_dist[i][0][0], good_dist[i][0][1]),
                             (good_dist[i][1][0], good_dist[i][1][1]), (0, 0, 255), 10, cv2.LINE_AA)
                    good.append(
                        (good_dist[i][0][0], good_dist[i][0][1], good_dist[i][1][0], good_dist[i][1][1]))
                if len(good) >= 2:
                    cv2.line(og,
                             (round((good[0][0] + good[1][0]) / 2), round((good[0][1] + good[1][1]) / 2)),
                             (round((good[0][2] + good[1][2]) / 2), round((good[0][3] + good[1][3]) / 2)),
                             (0, 255, 0), 10, cv2.LINE_AA)
    else:
        return og
    return og


# create video capture object
video = cv2.VideoCapture(0)

while video.isOpened():
    # read each frame
    ret, img = video.read()
    if ret:

        # detect and draw the Hough Lines P by calling the center function
        center_frame = center(img)

        # show the frame
        cv2.imshow("Detected Frame", center_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# stop the video capture object and destroy all the open cv windows
video.release()
cv2.destroyAllWindows()
