from os import listdir
from os.path import isfile, isdir, join, splitext, basename
from sys import argv
from zipfile import ZipFile
import csv
import json
import re

class Pbr(object):
    def __init__(self, path):
        self.path = path
        self.dictionary = {}
        self.dictionaryCSV = {}
        self.textures = {'baseColor':['baseColor', 'baseColour', 'albedo','diffuse', 'diff', 'color', 'colour','albedom', 'alb', 'bs', 'difuse','base_color', 'base_colour', 'alb'],
                         'roughness':['roughness', 'rougness', 'rough', 'rh', 'roughnes', 'rou'],
                          'metallic':['metallic', 'metalness', 'metal', 'metalic','metalnes', 'metallness'],
                            'normal':['normal', 'normals', 'norm', 'nrml', 'nrm', 'nor', '_n', '_nm'],
                        'glossiness':['glossiness', 'gloss', 'glos'],
                'metallicSmoothness':['metallicSmoothness'],
                'albedoTransparency':['albedoTransparency'],
                          'specular':['specular', 'spec']}

    def main(self):
        imagesList = self.filesToImages(self.path)
        return self.matchImageNames(imagesList)

    def isArchive(self, file):
        file = basename(file.lower())
        if file.endswith(".zip"):
            return file
        elif file.endswith(".rar"):
            pass
            #return file
        elif file.endswith(".7z"):
            return file

    def whatImage(self, i):
        i = basename(i.lower())
        if i.endswith(".png"):
            return i
        elif i.endswith(".jpg"):
            return i
        elif i.endswith(".tga"):
            return i
        elif i.endswith(".bmp"):
            return i
        elif i.endswith(".psd"):
            return i
        elif i.endswith(".exr"):
            return i
        elif i.endswith(".tiff"):
            return i

    def isImages(self, listFiles):
        # takes list of files and returns list of images
        listImages = []
        for i in listFiles:
            a = self.whatImage(i)
            if a != None:
                listImages.append(a)
        return listImages

    def isImage(self, image):        
        return self.whatImage(image)

    def listZip(self, path):
        # returns list of files inside ZIP archive
        zip = ZipFile(path)
        return self.isImages(zip.namelist())

    def filesToImages(self, path):
        # take files list and returns images list 
        imagesList = []
        for f in listdir(path):
            pathFile = join(path,f)
            if self.isArchive(f) != None:
                zip = self.listZip(pathFile)
                imagesList += zip
            elif isdir(pathFile):
                dir = listdir(pathFile)
                imagesList += self.isImages(dir)
            elif isfile(pathFile):
                g = self.isImage(f)
                imagesList.append(g)
        return imagesList

    def dictionaryAdd(self, dictionary, key, *value):
        if key not in dictionary.keys():
            dictionary[key] = [value]
        else:
            dictionary[key].append(value)

    def regex(self, image, value):
        #regex = re.compile('.*' + re.escape(v.lower()) + '\..*')
        regex = re.compile('(.*?|)' + re.escape(value.lower()) + '(\..*|.*?\..*)')
        return regex.match(image.lower())

    def matchImageNames(self, images):
        # take images list and returns map:imageFile.jpg dictionary
        for image in images:
            if image != None:
                for key, value in self.textures.items():
                    for v in value:
                        if self.regex(image, v):
                            self.dictionaryAdd(self.dictionary, key.lower(), file)
        return self.dictionary

    def log(self, name):
        with open('logfile.json', 'a+') as logFile:
            json.dump((name, "\n", self.dictionary),logFile)

    def writeCSV(self, *values):
        #add line to CSV file
        with open('output.csv', 'a+') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(values)

    def metalnessWorkflow(self):
        maps = 'baseColor', 'metallic', 'roughness', 'normal'
        return self.blueprint(maps)

    def specularWorkflow(self):
        maps = 'baseColor', 'specular', 'glossiness', 'normal'
        return self.blueprint(maps)

    def metallicSmoothnessWorkflow(self):
        maps = 'AlbedoTransparency', 'MetallicSmoothness', 'Normal'
        return self.blueprint(maps)

    def blueprint(self, maps):
        no = len(maps)
        for i in maps:
            if i.lower() in self.dictionary.keys():
                no -= 1
                if no <= 0:
                    return True

    def workflow(self):
        if self.metalnessWorkflow() and self.specularWorkflow() is True:
            return("Spcular&Metal PBR")
        if self.metalnessWorkflow() is True:
            return("Metalic/Rough PBR")
        elif self.specularWorkflow() is True:
            return("Specular/Glos PBR")
        elif self.metallicSmoothnessWorkflow() is True:
            return("MetalicSpecul PBR")
        else:
            return("IS NOT PBR")


for file in listdir(argv[1]):
    print(file)
    pbr = Pbr(join(argv[1], file))
    pbr.main()
    
    pbr.writeCSV(pbr.workflow(), file)
    pbr.log(file)