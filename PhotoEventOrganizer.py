import os

__author__ = 'luigolas'
import pyexiv2
from datetime import timedelta
# from datetime import datetime
from os import listdir, makedirs, rename
from os.path import isfile, join, exists
from VideoDate import video_creation_date
# import sys
from operator import itemgetter
import hashlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
#import PhevorGUi as phevo


def same_group(elem1, elem2, gap):
    return abs(elem1 - elem2) <= gap


def dateformated(date):
    # return date.strftime("%d-%m-%Y")
    return date.strftime("%Y-%m-%d")


def valid_format(elem):
    return image_format(elem) or video_format(elem)


def image_format(elem):
    return (".jpg" in elem) or (".JPG" in elem)


def video_format(elem):
    return (".mp4" in elem) or (".MP4" in elem)
    #TODO Admit mpg format
           #  (".MPG" in elem) or (".mpg" in elem)


def read_all_dates(elem):
    if image_format(elem):
        metadata = pyexiv2.ImageMetadata(elem)
        metadata.read()
        keys = metadata.exif_keys
        for key in keys:
            if "time" in key.lower() or "date" in key.lower():
                print key + ": " + str(metadata[key].value)


def read_date(elem):
    if image_format(elem):
        metadata = pyexiv2.ImageMetadata(elem)
        metadata.read()
        keys = metadata.exif_keys

        if 'Exif.Image.DateTime' in keys:
            return metadata['Exif.Image.DateTime'].value
        elif "Exif.Image.DateTimeOriginal" in keys:
            return metadata['Exif.Image.DateTimeOriginal'].value
        elif 'Exif.Photo.DateTimeOriginal' in keys:
            return metadata['Exif.Photo.DateTimeOriginal'].value
        elif 'Exif.Photo.DateTimeDigitized'in keys:
            return metadata['Exif.Photo.DateTimeDigitized'].value
        else:
            print elem + " - " + str(metadata.exif_keys)
    elif video_format(elem):
        return video_creation_date(elem)
    else:
        print "Not recognized"


def pick_sooner(elemlist):
    sooner_time = elemlist[0][1]
    if len(elemlist) > 1:
        for elem in elemlist[1:]:
            time = elem[1]
            if time < sooner_time:
                sooner_time = time

    return sooner_time


def create_filelist(folders):
    """

    :rtype : list
    """

    filelist = []
    for folder in folders:
        if folder[-1] != "/":
            folder += "/"

        print "Reading folder " + folder
        for path, subdirs, files in os.walk(folder):
            files = [f for f in files if not f[0] == '.']
            subdirs[:] = [d for d in subdirs if not d[0] == '.']
            for filename in files:
                if valid_format(filename):
                    time = read_date(os.path.join(path, filename))
                    filelist.append([filename, time, path+"/"])
        filelist.sort(key=itemgetter(1))

    return filelist


def duplicated(img1, img2):
    """
    Calculates duplicated image by hash

    """
    image_file_1 = open(img1).read()
    hex1 = hashlib.md5(image_file_1).hexdigest()
    image_file_2 = open(img2).read()
    hex2 = hashlib.md5(image_file_2).hexdigest()
    return hex1 == hex2


def main(gap, folders, destfolder, loose_size=3, simulated=True):
    filelist = create_filelist(folders)
    print "Number of files: " + str(len(filelist))

    # First Element
    elem = filelist[0]
    groups = {dateformated(elem[1]): [elem]}

    for elem in filelist[1:]:
        time = elem[1]
        #filename = elem[0]

        # Compare with other elements
        classified = False
        for g in groups:
            for photo in groups[g]:
                if same_group(time, photo[1], gap):
                    groups[g].append(elem)
                    classified = True
                    break

        if not classified:
            #Group already exists: 2 different events in the same day
            if any(dateformated(time) in name for name in groups.keys()):
                #Add hour element to the name
                #First time: modify name of coincidental key
                if dateformated(time) in groups.keys():
                    #Time data of "sooner" element
                    time2 = pick_sooner(groups[dateformated(time)])
                    groups[dateformated(time2) + "-" + str(time2.hour) + "h"] = groups.pop(dateformated(time))
                groups[dateformated(time) + "-" + str(time.hour) + "h"] = [elem]
            else:
                groups[dateformated(time)] = [elem]

    print "Number of groups: " + str(len(groups.keys()))
    for x in sorted(groups.keys()):
        print x + ": " + str(len(groups[x]))

    if destfolder[-1] != "/":
        destfolder += "/"
    # Folder Creation
    i = 0
    for g in groups:
        i += len(groups[g])
        #TODO Some times more files processed than there are ?
        if not simulated:
            newpath = destfolder + g + "/"
            if not exists(newpath):
                makedirs(newpath)
            else:
                # print newpath + " not created ***"
                pass

            if not exists(destfolder):
                makedirs(destfolder)

            # # TODO Loose photos support
            # if len(groups[g]) <= loose_size:
            #     #plot images
            #     size = len(groups[g])
            #     i = 0
            #     pics = []
            #     for photo in groups[g]:
            #         name = photo[0]
            #         folder = photo[2]
            #         if ".mp4" in name:
            #             continue
            #         pics.append(folder + name)
            #     print pics
            #     if len(pics) > 0:
            #         phevo.show_pics(pics)

            #Move files
            for photo in groups[g]:
                name = photo[0]
                folder = photo[2]
                if name in listdir(newpath):
                    if duplicated(newpath+name, folder+name):
                        # Create folder duplicated
                        #TODO Really useful??
                        if not exists(newpath + "duplicated/"):
                            makedirs(newpath + "duplicated/")
                        name = "duplicated/" + name
                        print "Duplicated in", newpath + name
                    else:
                        name += "-1"
                        #Make sure the name is not taken already
                        while name in listdir(newpath):
                            name += "-1"

                rename(folder + photo[0], newpath + name)
    print i

if __name__ == "__main__":
    gap = timedelta(hours=5)
    # folder = "TestPhotos/"
    # folders = ["/media/Datos/Google Drive/Fotos LG G2/"]
    # folders = ["TestPhotos/", "TestPhotos/duplicatedtest"]
    # destfolder = "TestPhotos/classified/"
    # destfolder = "/media/Datos/Google Drive/Fotos con Osita/Viaje La Gomera La Palma/"
    # folders = ["/media/Datos/Fotos La Gomera y La Palma/premislav",
    #            "/media/Datos/Fotos La Gomera y La Palma/Lilah",
    #            "/media/Datos/Fotos La Gomera y La Palma/Gosia",
    #            "/media/Datos/Google Drive/Fotos con Osita/Viaje La Gomera La Palma"
    #            ]

    #destfolder = "/home/luigolas/Fotos LG G2 temp temp/Result/"
    #folders = ["/home/luigolas/PycharmProjects/PyPhoto/"]
    destfolder = "/media/luigolas/TeresitoDrive/Fotos LG G2 Result/"
    folders = ["/media/luigolas/TeresitoDrive/Fotos LG G2/",
               "/media/luigolas/TeresitoDrive/Fotos LG G2 tal",
               "/media/luigolas/TeresitoDrive/Fotos LG G2 temp",
               "/media/luigolas/TeresitoDrive/LG G2 TEMP"]
    main(gap, folders, destfolder, simulated=False)
    # folder = "/media/Datos/teeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeemp/Fotos La Gomera y La Palma/premislav/"
    # # folder = "/media/Datos/teeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeemp/Fotos La Gomera y La Palma/Lilah/"
    # # folder = "/media/Datos/teeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeemp/Fotos La Gomera y La Palma/Gosia/"
    # # folder = "/media/Datos/teeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeemp/Viaje La Gomera La Palma/"
    # files = [filename for filename in listdir(folder) if isfile(join(folder, filename)) & valid_format(filename)]
    # files = create_filelist(folder, files)
    # elem = files[1]
    # read_all_dates(elem[2]+elem[0])