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
        print("if", sum(common_things) / len(common_things))
        return sum(common_things) / len(common_things)
    # otherwise return the average of the most common values (can have multiple most common values)
    else:
        print("else", round(sum(common_things) / len(common_things), 1))
        return round(sum(common_things) / len(common_things), 1)


def find_similar(lines, slopes, most):
    good_lines = []
    rounded = []
    for x in slopes:
        try:
            x = round(x)
            rounded.append(x)
        except OverflowError:
            rounded.append(999)

    for i in range(len(lines)):
        if -10 <= rounded[i] <= 10:
            increment = 2
        else:
            increment = 100
        if float(most + increment) > rounded[i] > float(most - increment):
            good_lines.append(lines[i])

    return good_lines


def center(og):
    frame = filters(og)
    lines = cv2.HoughLinesP(frame, 1, np.pi / 180, threshold=120, minLineLength=100, maxLineGap=999999)
    cv2.rectangle(og, (500, 100), (1300, 1000), 255, 10)
    endpts = []
    slopes = []
    avg_x1, avg_y1, avg_x2, avg_y2 = 0, 0, 0, 0
    if lines is not None:
        for i in lines:
            x1, y1, x2, y2 = i[0]
            try:
                slopes.append(((y2 - y1) / (x2 - x1)))
            except ZeroDivisionError:
                slopes.append(999)

        freq = most_common(slopes)
        good_lines = find_similar(lines, slopes, freq)
        for i in good_lines:
            x1, y1, x2, y2 = i[0]
            cv2.line(og, (x1, y1), (x2, y2), (0, 0, 255), 10)

            avg_x1 += x1
            avg_y1 += y1
            avg_x2 += x2
            avg_y2 += y2

            endpts.append(((x1, y1), (x2, y2)))

        if len(good_lines) > 0:
            avg_x1 /= len(good_lines)
            avg_y1 /= len(good_lines)
            avg_x2 /= len(good_lines)
            avg_y2 /= len(good_lines)

        avg_line = (int(avg_x1), int(avg_y1), int(avg_x2), int(avg_y2))
        cv2.line(og, (avg_line[0], avg_line[1]), (avg_line[2], avg_line[3]), (0, 255, 0), 10)

    else:
        print("no lines")
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

