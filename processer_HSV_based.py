from PIL import Image, ImageDraw
import csv

print("BEGUN")

imgs = []
for i in range(1,8):
    print("IMG_NUM:", i)
    fileName = "den_" + str(i) + ".png"
    imgs.append(Image.open(fileName))


hourStep  = 2
imgStarts = [(20,23), (20,24), (0,26), (0,27), (0,28), (20,29), (20,30)]
#imgStarts = [(20,23), (20,24), (0,26)]
dates     = imgStarts[:]
firstDate = imgStarts[0]
for a, i in enumerate(imgStarts):
    hour = i[0] - firstDate[0]
    days = i[1] - firstDate[1]
    imgStarts[a] = int(hour/hourStep + days*24/hourStep)
print(imgStarts)
print(imgs)

tempStarts  = [-10, -10, -10, -10, -10, 0, 0]
valPerPixss = [[5/57, 12.5/57, 2/57],
               [5/57, 12.5/57, 2/57],
               [5/57, 12.5/57, 1/57],
               [5/57, 12.5/57, 2/57],
               [5/57, 12.5/57, 2/57],
               [5/57, 12.5/57, 2/57],
               [5/57, 12.5/57, 2/57]]
filters    =((255, 216, 230),
             (128, 206, 238),
             (85, 91, 131))

def MakeHourLocs(imgs, invert = False):
    hourLocss = []
    for img in imgs:
        img = img.convert('HSV')
        hourLocs = []
        y = 517
        print(img.getpixel((0,y)))
        baseV = img.getpixel((0,y))[2]
        print(baseV)
        #print(baseV)
        for x in range(0, img.width):
            value = img.getpixel((x,y))[2]
            if value != 254: print(value, end = ", ")
            if invert:
                if value == baseV: hourLocs.append(x); blk = False
                if img.getpixel((x,y)) == (0,0,0) and not(blk):
                    hourLocs.append(None)
                    blk = True
            else:
                if value < baseV-10: hourLocs.append(x-14)

        '''diffs = []
        prev  = False
        for a,i in enumerate(hourLocs):
            diff = i-prev
            if diff > 80:
                hourLocs.insert(a, (i+prev)//2)
            prev = i'''
        print(hourLocs)
        hourLocss.append(hourLocs)
    return hourLocss

hourLocss = MakeHourLocs(imgs)


print("\n INITTED \n")


def find_best_y(x, pixels, filters, img):
    maxGudnesses = [0, 0, 0]
    bestYs       = [None, None, None]

    for y in range(0,img.height):
        index = y*img.width + x+1
        pixel = pixels[index]
        # if x < 89 and y < 87: pass
        if False: pass
        else:
            #if pixel != [199,199,199]: print(pixel)

            y = img.height  - y


            for a,i in enumerate(filters):
                gudness = 0
                for b,ideal in enumerate(i):
                    if b == 0:
                        importance = 100
                        diff = abs(pixel[b] - ideal)
                        if diff > 128: diff = 256 - diff
                    else:
                        importance = 1
                        diff = abs(pixel[b] - ideal)
                    gudness += (256 - diff) * importance
                if gudness > maxGudnesses[a]:
                    maxGudnesses[a]= gudness
                    bestYs[a]      = y
    return maxGudnesses, bestYs


def subtract_by_lowest(lst):
    if min(lst) != max(lst):
        min_num = min(lst)
        lst = [i - min_num for i in lst]
    return lst


def delete_lowest(lst):
    lst.remove(min(lst))
    return lst


def avg_func(lst):
    return sum(lst)/len(lst)


def weighted_average(weights, lst):
    assert len(weights) == len(lst), f"PARAMETERS NOT OF EQUAL LENGTH {weights}, \n {lst}"
    return sum([weights[i]*lst[i] for i in range(len(lst))]) / sum(weights)


def MakeVals(valPerPixs, img, tempStart, hourLocs, imgIndex):
    global filters, hourStep

    pointsMade = [[],[],[]]
    gudList = [[],[],[]]

    img = img.crop((14, 56, 807, 507))
    #img.show()
    #print("converting")
    img = img.convert('HSV')
    draw = ImageDraw.Draw(img)
    #print("extracting data")
    pixels = img.getdata()
    #print("extracted")
    pixels = list(pixels)
    #for i in pixels: print(pixels)
    #img.show()

    x = hourLocs[0]
    odd = 1
    while x < img.width:
        #print(x)
        indices = [None, None, None]
        mxGss = [[],[],[]]  # maxGudnessess
        beYss = [[],[],[]]  # bestYss
        for x_minor in range(0,3):
            if x+x_minor+1 < img.width:
                maxGudnesses, bestYs = find_best_y(x + x_minor, pixels, filters, img)
                for type_ix in range(0,3):
                    cx, cy = (x+x_minor+1, img.height-bestYs[type_ix])
                    img.putpixel((cx,cy), (0,0,0))
                    draw.rectangle((cx-2,cy-2, cx+2, cy+2), outline=(200,50, 255-int(maxGudnesses[type_ix]/26100*255)+150), width=1)
                    print("################################################", int(maxGudnesses[type_ix]/26100*255), "VALUE_CALC")

                    mxGss[type_ix].append(maxGudnesses[type_ix])
                    beYss[type_ix].append(bestYs[type_ix])

        sub_mxGss = [[],[],[]]
        for type_ix in range(0,3):
            sub_mxGss[type_ix] = subtract_by_lowest(mxGss[type_ix])
            # beYss is henceforth discarded and substituted by bestYs because of prior code
            bestYs[type_ix] = round(weighted_average(sub_mxGss[type_ix], beYss[type_ix]))

            maxGudnesses[type_ix] = avg_func(delete_lowest(mxGss[type_ix]))

        print("BESTS -> TEMP:", maxGudnesses[0],
                     "  HUMI:", maxGudnesses[1],
                     "  AIRS:", maxGudnesses[2],
                     "  X:", x, "  Y:", img.height - bestYs[2])
        for a,i in enumerate(pointsMade):
            if a == 0: add = tempStart
            else: add = 0
            i.append(round((bestYs[a]*valPerPixs[a] + add)*10)/10)
            #i.append(odd-1 + imgStarts[imgIndex])
            gudList[a].append(maxGudnesses[a])
            img.putpixel((x, img.height-bestYs[a]), (200,50, 255-int(maxGudnesses[a]/26100*255)))
            cx, cy = (x, img.height-bestYs[a])
            draw.rectangle((cx-3,cy-3, cx+3, cy+3), outline=(200,50, 255-int(maxGudnesses[a]/26100*255)), width=1)

        if odd%2 == 0: x = hourLocs[odd//2]; odd += 1
        elif odd//2 + 1 < len(hourLocs):x = (hourLocs[odd//2] + hourLocs[odd//2 + 1])//2; odd += 1
        else: x = hourLocs[odd//2] + 33; odd += 1
        if len(hourLocs) <= odd//2: break

    # img.show()
    for i in pointsMade: print(i)
    return pointsMade, gudList, hourLocs




nowDate = firstDate
table = [[],[],[]]
guds = [[],[],[]]
locss= []
for a,img in enumerate(imgs):
    print("\n \n PROCESS IMG", a)
    new, newGud, locs = MakeVals(valPerPixss[a], img, tempStarts[a], hourLocss[a], a)
    if a == 0: print(new)
    #print(newGud, "NEW_GUD")
    for b,i in enumerate(new):
        table[b].append(i)
        guds[b].append(newGud[b])
        #table[b].extend(["img" + str(a+1)] + i + ["len" + str(len(i))])
    locss.append(locs)



print("\n \n UNIFY")
newTable = []
newImgs = []
totalWidth = 0
for t,type in enumerate(table):
    newType = []
    for a, img in enumerate(type):
        print("\n \n")
        hour = ((firstDate[0]/hourStep + len(newType))%(24/hourStep))*hourStep
        day = firstDate[1] + ((firstDate[0]/hourStep + len(newType))//(24/hourStep))
        print(hour, day, dates[a])
        #assert (hour, day) == dates[a], (hour, day, dates[a])
        if a+1 < len(imgStarts):
            try: otherImg  = type[a+1]
            except IndexError:
                print("########################\nINDEX ERROR\n########################")
                print("TYPE ", type)
                print("LEN-TYPE ", len(type))
                print("INDEX-IN-TYPE ", a+1)
                print("INDEX-OF-TYPE ", t)
                quit()


            if a<1: low = 0
            else: low = len(newType) - imgStarts[a]
            if low < 0:
                print("LOW is LOW", low, len(newType), imgStarts[a])
                totalWidth += 33*abs(low)
                newType.extend([None]*abs(low))
                low = 0
            index = max(low+1, imgStarts[a+1] - imgStarts[a])
            ll = 0
            if low+1 > imgStarts[a+1] - imgStarts[a]: ll = low+1 - (imgStarts[a+1] - imgStarts[a])
            print(index, len(img), "LEN_IMG")
            print("  ", low, index, "LOW + INDEX", imgStarts[a-1:a+2])
            print(img, "IMG", img[low : index])
            print(otherImg, "OTHER_IMG")

            if True:
                toReduce1 = img[index:]
                toReduce2 = otherImg[ll:len(img)-(imgStarts[a+1] - imgStarts[a])]
                print(toReduce1, toReduce2, "COMPARING", len(toReduce1), len(toReduce2))
                #assert toReduce1 == toReduce2, (a, img)
                final = []
                for b, i in enumerate(toReduce1):
                    j = toReduce2[b]
                    gudI = guds[t][a][index + b]
                    gudJ = guds[t][a+1][b]
                    if   gudI > gudJ: final.append(i)
                    elif gudI < gudJ: final.append(j)
                    else:             final.append((i+j)/2)
                print(final, "FINAL", len(final))


            newType.extend(img[low : index])

            if t == 0:
                newImg = imgs[a].copy()
                x1 = locss[a][low//2] + 14
                x2 = locss[a][len(locss[a])-1]-1 + 14
                newImg = newImg.crop((x1, 0, x2+10, newImg.height))
                newImgs.append((newImg, totalWidth))
                totalWidth += x2-x1


            newType.extend(final)
            print(newType, "NEWTYPE", len(newType), imgStarts[a])
        else:
            print(img, "IMG")
            low = len(newType) - imgStarts[a]
            newType.extend(img[low:])
            if t == 0:
                print(a, locss[a])
                newImg = imgs[a].copy()
                x1 = locss[a][low//2] + 14
                x2 = locss[a][len(locss[a])-1]-1 + 14
                newImg = newImg.crop((x1, 0, x2+10, newImg.height))
                #newImg.show()
                newImgs.append((newImg, totalWidth))
                totalWidth += x2-x1
    '''prev = -1
    for i in newType:
        assert i == prev+1, i
        prev = i'''
    print(newType, "NEW_TYPE")
    newTable.append(newType)


print(imgs)
joined = Image.new('HSV', (totalWidth, imgs[0].height))
for img in newImgs:
    joined.paste(img[0], (img[1], 0))

hourloc = MakeHourLocs([joined], invert = True)[0]
print(hourloc)
hourLocs= []
nn = []
for a,i in enumerate(hourloc):
    if i is not None: hourLocs.append(i)
    if a+1 < len(hourloc) and (i is not None) and (hourloc[a+1] is not None):
        hourLocs.append((i + hourloc[a+1])//2)
    #print(hourLocs)
for a,type in enumerate(newTable):
    print(len(hourLocs), len(type))
    index = 0
    draw = ImageDraw.Draw(joined)
    for b,i in enumerate(type):
        if i is None:
            pass
        else:
            try:
                print(index, len(hourLocs), len(type))
                x = hourLocs[index]
                if a == 0:
                    yy =  (i+10)/valPerPixss[0][a]
                else:
                    yy =  i/valPerPixss[0][a]
                y = int(450 - yy + 56)

                col = list(filters[a])
                col[2] = 200
                col = tuple(col)
                if b != 0: draw.line((last_x,last_y, x,y), fill=col, width=3)
                last_x = x
                last_y = y
            except: pass
            index += 1

joined.show()
joined = joined.convert('RGB')
joined.save("joined.png")



newTable.append([])
newTable.append([])
for i in range(0,3):
    newTable.append([])
toAvg = [[],[],[]]
for i in range(0, len(newTable[0])):
    for a,type in enumerate(toAvg):
        print(type)
        toAvg[a].append(newTable[a][i])
    hour = ((firstDate[0]/hourStep + i)%(24/hourStep))*hourStep
    if hour == 0:
        for a,type in enumerate(toAvg):
            n = []
            for thing in type:
                if thing is not None:
                    n.append(thing)
            newTable[a+5].append(sum(n)/len(n))
        toAvg = [[],[],[]]
        day = firstDate[1] + ((firstDate[0]/hourStep + i)//(24/hourStep))
    else:
        for a,type in enumerate(toAvg):
            newTable[a+5].append("")
        day = ""
    newTable[3].append(hour)
    newTable[4].append(day)


with open('NEUweather.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, lineterminator = "\n")
    [writer.writerow(r) for r in newTable]
'''print(MakeVals(valPerPixs, tStep, img))
print(MakeVals(valPerPixs, tStep, img))'''
