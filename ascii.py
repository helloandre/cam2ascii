#!/usr/bin/python
import sys, cv, time, curses, math, getopt

# NOTE: size given in y,x
def toNums(image, size):
    image_size = cv.GetSize(image)
    scale_x = int(max(math.floor(image_size[0]/size[1]), 1))
    scale_y = int(max(math.floor(image_size[1]/size[0]), 1))
         
    # create grayscale version
    grayscale = cv.CreateImage(image_size, 8, 1)
    cv.CvtColor(image, grayscale, cv.CV_BGR2GRAY)

    cv.EqualizeHist(grayscale, grayscale)

    # calculate the averages of all scale x scale pixels
    output = []
    for row in range(0, image_size[1]-scale_y+1, scale_y):
        r = []
        for col in range(0, image_size[0]-scale_x+1, scale_x):
            subrect = cv.GetSubRect(grayscale, (col, row, scale_x, scale_y))
            avg = cv.Avg(subrect)[0]
            r.append(avg)
        output.append(r)
    return output

def toAscii(values):
    available = ['.', '-', '+', '=', 'I', 'X', 'H', 'M', '8', '0', '@']
    chars = []
    for row in values:
        r = []
        for col in row:
            val = available[int(math.floor(col/23)-1)]
            r.append(val)
        chars.append(r)
    return chars


def draw(scr, capture):
    frame = cv.QueryFrame(capture)

    # options
    if (mirror):
        cv.Flip(frame, frame, 1)
    if (show_frame):
        cv.ShowImage("w1", frame)

    size = scr.getmaxyx()
    
    values = toNums(frame, size)
    chars = toAscii(values)

    for y in range(0, size[0]-1):
        for x in range(0, size[1]-1):
            scr.addch(y,x,ord(chars[y][x]))
    
    scr.refresh()

def runner(scr):
    capture = cv.CaptureFromCAM(-1)
    cv.NamedWindow("w1", cv.CV_WINDOW_AUTOSIZE)
    while True:
        draw(scr, capture)


show_frame = False
mirror = False
if __name__ == '__main__':
    options, args = getopt.getopt(sys.argv[1:],'fm')
    for opt in options:
        if opt[0] == '-f':
            show_frame = True
        if opt[0] == '-m':
            mirror = True

    curses.wrapper(runner)