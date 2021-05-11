from PIL import Image, ImageDraw
import csv

def gudness_eval(pixel, filter):
    gudness = 0
    for b,ideal in enumerate(filter):
        if b == 0:
            importance = 100
            diff = abs(pixel[b] - ideal)
            if diff > 128: diff = 256 - diff
        else:
            importance = 1
            diff = abs(pixel[b] - ideal)
        gudness += (256 - diff) * importance
    return gudness


def make_hour_locs(imgs):
    hourLocss = []
    for img in imgs:
        hourLocs = []
        y = 517
        print(img.getpixel((0,y)))
        baseV = img.getpixel((0,y))[2]
        print(baseV)
        #print(baseV)
        for x in range(0, img.width):
            value = img.getpixel((x,y))[2]
            if value != 254: print(value, end = ", ")
            if value < baseV-10: hourLocs.append(x)
        print()
        print(hourLocs)
        hourLocss.append(hourLocs)
    return hourLocss



print("BEGUN")

imgs = []
for i in range(1,8):
    print("IMG_NUM:", i)
    fileName = "den " + str(i) + ".gif"
    imgs.append(Image.open(fileName).convert('HSV'))

begin = (14,56)
steprange = (56,59)
linecolor = imgs[0].getpixel((14,56))
print(linecolor)

hour_locss = make_hour_locs(imgs)
for img_ix, img in enumerate(imgs):
    x,y = begin
    draw = ImageDraw.Draw(img)
    for i in range(9):
        draw.line((0,y, img.width-1,y), fill=(0,0,255))
        max_gudness = 0
        best_y = 0
        for a, plus_y in enumerate(range(*steprange)):
            gudness = gudness_eval(img.getpixel((x,y + plus_y)), linecolor)
            if gudness > max_gudness:
                best_y = y + plus_y
                max_gudness = gudness
        y = best_y

    hour_locs = hour_locss[img_ix]
    for x in hour_locs:
        draw.line((x,0, x,img.height-1), fill=(0,0,126))
    img = img.convert("RGB")
    img.save(f"den_{img_ix+1}.png")
