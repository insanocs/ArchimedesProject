import requests
import numpy as np
import cv2
from io import BytesIO
from PIL import Image, ImageChops
from time import sleep

colors_earth = [[202,227,255],
    [255,255,255],
    [255,255,255],
    [228,228,228],
    [196,196,196],
    [136,136,136],
    [78,78,78],
    [0,0,0],
    [244,179,174],
    [255,167,209],
    [255,84,178],
    [255,101,101],
    [229,0,0],
    [154,0,0],
    [254,164,96],
    [229,149,0],
    [160,106,66],
    [96,64,40],
    [245,223,176],
    [255,248,137],
    [229,217,0],
    [148,224,68],
    [2,190,1],
    [104,131,56],
    [0,101,19],
    [202,227,255],
    [0,211,221],
    [0,131,199],
    [0,0,234],
    [25,25,115],
    [207,110,228],
    [130,0,128]
    ]
colors_moon = [[49,46,47],[99,92,90],[49,46,47],[99,92,90],[129,119,107],[198,181,165],[255,237,212],[150,86,122],[202,112,145],[96,67,79],[136,79,94],[175,101,103],[195,124,107],[221,153,126],[233,181,140],[198,139,91],[140,89,74],[94,68,63],[225,173,86],[248,207,142],[239,220,118],[206,190,85],[157,159,55],[114,121,43],[81,94,46],[69,100,79],[80,134,87],[187,209,138],[91,84,108],[106,113,137],[122,148,156],[174,215,185]]
colors_1bit = [[0,0,0],[255,255,255],[0,0,0],[255,255,255]]

def get_chunk(x, y, canvas):
    if canvas == "m":
        num_canvas = 1
        canv_size = 16384
    elif canvas == "1":
        num_canvas = 7
        canv_size = 65536
    else:
        num_canvas = 0
        canv_size = 65536
    chunk_y = ((canv_size // 2) + int(y)) // 256
    chunk_x = ((canv_size // 2) + int(x)) // 256
    # get data from the server
    data = requests.get(f'https://pixelplanet.fun/chunks/{num_canvas}/{chunk_x}/{chunk_y}.bmp').content
    # construct a numpy array from it
    arr = np.zeros((256, 256), np.uint8)
    if len(data) != 65536:
        return arr
        print('Data size differs from 65536')
    for i in range(65536):
        c = data[i]
        # protected pixels are shifted up by 128
        if c >= 128:
            c = c - 128
        arr[i // 256, i % 256] = c
    return arr

def get_chunks(xs, ys, w, h, canvas):
    xs, ys, w, h = int(xs), int(ys), int(w), int(h)
    if canvas == "m":
        num_canvas = 1
        canv_size = 16384
    elif canvas == "1":
        num_canvas = 7
        canv_size = 65536
    else:
        num_canvas = 0
        canv_size = 65536
    c_start_y = ((canv_size // 2) + ys) // 256
    c_start_x = ((canv_size // 2) + xs) // 256
    c_end_y = ((canv_size // 2) + ys + h) // 256
    c_end_x = ((canv_size // 2) + xs + w) // 256
    c_occupied_y = c_end_y - c_start_y + 1
    c_occupied_x = c_end_x - c_start_x + 1
    if canvas == "m":
        colorsf = colors_moon
    elif canvas == "1":
        colorsf = colors_1bit
    else:
        colorsf = colors_earth
    # the final image
    data = np.zeros((0, c_occupied_x * 256), np.uint8)
    # go through the chunks
    for y in range(c_occupied_y):
        # the row
        row = np.zeros((256, 0), np.uint8)
        for x in range(c_occupied_x):
            # append the chunk to the row
            row = np.concatenate((row, get_chunk((int(x) * 256) + int(xs), (int(y) * 256) + int(ys), canvas)), axis=1)
        # append the row to the image
        data = np.concatenate((data, row), axis=0)
    img = np.zeros((256 * c_occupied_y, 256 * c_occupied_x, 3), np.uint8)
    for y in range(256 * c_occupied_y):
        for x in range(256 * c_occupied_x):
            r, g, b = colorsf[data[y, x]]
            img[y, x] = (b, g, r)
    h, w, rd = img.shape
    cv2.imwrite('multiplos.png', img)
    return h, w, c_occupied_x, c_occupied_y

def differ(xs, ys, img, canvas):
    if canvas == "m":
        num_canvas = 1
        canv_size = 16384
    elif canvas == "1":
        num_canvas = 7
        canv_size = 65536
    else:
        num_canvas = 0
        canv_size = 65536
    c_start_x = ((canv_size // 2) + int(xs)) // 256
    c_start_y = ((canv_size // 2) + int(ys)) // 256
    start_in_d_x = int(xs) + ((canv_size // 2) - (int(c_start_x) * 256))
    start_in_d_y = int(ys) + ((canv_size // 2) - (int(c_start_y) * 256))
    #print(start_in_d_x)
    #print(start_in_d_y)
    data_im = Image.open("multiplos.png")
    #print(img.size[0], img.size[1])
    kek = data_im.crop((start_in_d_x, start_in_d_y, start_in_d_x + img.size[0], start_in_d_y + img.size[1])).convert('RGBA')

    datas3 = img.getdata()
    datas4 = kek.getdata()

    toTransparent = []
    index = 0
    print(img.size)
    print(datas3)
    for item in datas3:
        if item[3] == 0:
            toTransparent.append((255, 255, 255, 17))
            index += 1
        else:
            toTransparent.append((datas4[index][0], datas4[index][1], datas4[index][2]))
            index += 1

    kek.putdata(toTransparent)

    diff = ImageChops.difference(img, kek)
    datas = diff.getdata()

    errors = 0
    non_transp = 0
    newData = []

    diff.save('b4.png')

    for item in datas:
        if item[0] == 0 and item[1] == 0 and item[2] == 0 and item[3] == 0:
            non_transp += 1
            newData.append((255, 255, 255, 0))
        elif item[3] == 17:
            newData.append((255, 255, 255, 0))
        else:
            non_transp += 1
            errors += 1
            newData.append((255, 0, 0, 255))

    diff.putdata(newData)

    diff.save('after.png')

    ungrayed = img.convert('LA')
    ungrayed.save('ungrayed.png')
    new_grayed = Image.open('ungrayed.png').convert('RGBA')
    new_grayed.paste(diff, (0,0), diff)
    return errors, non_transp, new_grayed