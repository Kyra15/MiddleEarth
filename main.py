import cv2
import numpy as np


# applies the filters for grayscale, gaussian blur, canny edge, and a rectangle mask onto the frame given
def filters(pic):
    bw = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
    gauss_bw = cv2.GaussianBlur(bw, (15, 15), 0)
    canny_gauss_bw = cv2.Canny(gauss_bw, 100, 200, apertureSize=5)
    mask = np.zeros(pic.shape[:2], dtype="uint8")
    cv2.rectangle(mask, (500, 100), (1300, 1000), 255, -1)
    masked = cv2.bitwise_and(canny_gauss_bw, canny_gauss_bw, mask=mask)
    return masked


# given a list, rounds all values and finds the most common value and returns that
# if all values are unique or occur the same number of times, average all the values together
def most_common(lst):
    rounded = []
    for x in lst:
        try:
            x = round(x)
        except OverflowError:
            x = 999
        rounded.append(x)

    print(rounded)

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


# finds slopes that are similar to the most common slope and returns those lines
def find_similar(lines, slopes, most):
    good_lines = []
    rounded = []
    for x in slopes:
        try:
            x = round(x)
            rounded.append(x)
        except OverflowError:
            rounded.append(999)

    # if the slope is horizontal, then make it so that the slopes have to be within 2 of the most common slope
    for i in range(len(lines)):
        if -10 <= rounded[i] <= 10:
            increment = 2
        # otherwise, make it so the slopes have to be within 100 of the most common slope
        # this is because vertical slopes have a higher margin of error and will vary more greatly with small movements
        # whereas horizontal slopes will have a small variation
        else:
            increment = 100
        if float(most + increment) > rounded[i] > float(most - increment):
            good_lines.append(lines[i])

    return good_lines


# detect and output the lines and middle lines of the frame given
def center(og):
    # apply the filters and detect the lines with HoughLinesP
    frame = filters(og)
    lines = cv2.HoughLinesP(frame, 1, np.pi / 180, threshold=130, minLineLength=100, maxLineGap=999999)
    cv2.rectangle(og, (500, 100), (1300, 1000), 255, 10)
    slopes = []
    avg_x1, avg_y1, avg_x2, avg_y2 = 0, 0, 0, 0
    # find the slopes of each line detected
    if lines is not None:
        for i in lines:
            x1, y1, x2, y2 = i[0]
            try:
                slopes.append(((y2 - y1) / (x2 - x1)))
            except ZeroDivisionError:
                slopes.append(999)

        # find the most common slope in the frame
        freq = most_common(slopes)
        # find the lines with similar slopes to the most common slope and display them
        good_lines = find_similar(lines, slopes, freq)
        for i in good_lines:
            x1, y1, x2, y2 = i[0]
            cv2.line(og, (x1, y1), (x2, y2), (0, 0, 255), 10)

            # add the coordinates of each line to a total sum
            avg_x1 += x1
            avg_y1 += y1
            avg_x2 += x2
            avg_y2 += y2

        # to prevent a divide by zero error, check to make sure at least some lines were outputted
        # calculate the average of all the endpoints of the outputted lines
        if len(good_lines) > 0:
            avg_x1 /= len(good_lines)
            avg_y1 /= len(good_lines)
            avg_x2 /= len(good_lines)
            avg_y2 /= len(good_lines)

        # display the line
        cv2.line(og, (int(avg_x1), int(avg_y1)), (int(avg_x2), int(avg_y2)), (0, 255, 0), 10)
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
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    else:
        break

# stop the video capture object and destroy all the open cv windows
video.release()
cv2.destroyAllWindows()
