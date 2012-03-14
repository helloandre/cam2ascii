#!/usr/bin/python
import sys, cv, time, curses, math, getopt
show_frame = mirror = stats = False
curr_sec = inc_rate = curr_rate = init = 0
available = [' ', '`', '.', '~', '+', 'I', 'X', 'O', '8', '%', 'W']
av_count = 256/len(available)
init_start = time.time()

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
    chars = []
    for row in values:
        r = []
        for col in row:
            index = max(int(math.floor(col/av_count))-1, 0)
            val = available[index]
            r.append(val)
        chars.append(r)
    return chars


def draw(scr, capture):
    global curr_sec, inc_rate, curr_rate
    frame = cv.QueryFrame(capture)

    # options
    if (mirror):
        cv.Flip(frame, frame, 1)
    if (show_frame):
        cv.ShowImage("w1", frame)
        return

    size = scr.getmaxyx()
    
    values = toNums(frame, size)
    chars = toAscii(values)

    for y in range(0, size[0]-1):
        for x in range(0, size[1]-1):
            scr.addch(y,x,ord(chars[y][x]))

    if (stats):
        curr_time = int(time.time())
        if curr_time > curr_sec:
            curr_rate = inc_rate
            inc_rate = 0
            curr_sec = curr_time
        else: 
            inc_rate+=1
        rate_str = "rate:"+str(curr_rate)
        init_str = " init:"+str(round(init, 4))+"s"
        scr.addstr(0, 0, rate_str)
        scr.addstr(0, len(rate_str), init_str)

    scr.refresh()

def runner(scr):
    global init
    capture = cv.CaptureFromCAM(-1)
    if (show_frame):
        cv.NamedWindow("w1", cv.CV_WINDOW_AUTOSIZE)
    init = time.time()-init_start
    while True:
        draw(scr, capture)

if __name__ == '__main__':
    options, args = getopt.getopt(sys.argv[1:],'fms')
    for opt in options:
        if opt[0] == '-f':
            show_frame = True
        if opt[0] == '-m':
            mirror = True
        if opt[0] == '-s':
            stats = True

    curses.wrapper(runner)