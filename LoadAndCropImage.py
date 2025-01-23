import glob
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skimage import img_as_ubyte, io
from skimage.filters import threshold_otsu
from skimage.filters.rank import entropy
from skimage.morphology import disk
from skimage.util import crop, img_as_ubyte
from tifffile import imread


class LoadAndCropImage():

    def __init__(self, pathstring):
        """constructor"""
        self.pathstring = pathstring
        # self.SelectChannel()
        # self.CreateImagecrops()

    def SelectChannel(self):
        """ 
        This function helps in choosing the correct channel for cropping images
        
        Attributes:
        
        :params self: does not take an argument
        :return: returns the channel to crop in python array format (from 0)
        """
        print(self.pathstring)
        Noof_files = 0
        for file in (os.listdir(self.pathstring)):
            # print(file[0])
            if file.endswith('.ome.tif'):
                file
                Noof_files += 1
                if Noof_files == 1:
                    print(file)
                    ChannelIndex = file.find('C0')
        if Noof_files == 0:
            raise NameError
        else:
            Noof_Channels = int(os.listdir(self.pathstring)[
                                Noof_files-1][ChannelIndex+1:ChannelIndex+3])
            print(Noof_Channels)
            self.Noof_Channels = Noof_Channels
            self.Channel2crop = int(input('There are ' + str(self.Noof_Channels+1) +
                                    ' channels in this dataset \n Enter which channel to use for random crops?: '))
            if self.Channel2crop < 1 or self.Channel2crop > self.Noof_Channels+1:
                raise ValueError
            else:
                self.Channel2crop = self.Channel2crop-1
                return self.Channel2crop

    def CreateImagecrops(self, stacks=10, xpixels=180, ypixels=180, Noof_cropsforThisDataset=50):
        """
        This function helps in creating image crops from selected channel

        Attributes:

        :param stacks: no of stacks the crop should have (default 50)
        :param xpixels: Width of the crop in pixels (default 180)
        :param ypixels: Length of the crop in pixels (default 180)
        :param Noof_cropsforThisDataset: No of crops made for this dataset (Default 50)
        :return: does not return anything. Directly saves files

        """

        print(self.pathstring)
        self.stacks = stacks
        self.xpixels = int(xpixels)
        self.ypixels = int(ypixels)
        self.Noof_cropsforThisDataset = Noof_cropsforThisDataset
        print(self.pathstring + '\\'+os.listdir(self.pathstring)[0])
        Path2image = (self.pathstring + '\\'+os.listdir(self.pathstring)[0])

        OriginalImage = Image.open(Path2image)
        # OriginalImage=io.imread(Path2image)
        print(OriginalImage.size)
        self.idimx, self.idimy = OriginalImage.size
        # self.idimx,self.idimy=np.shape(OriginalImage)
        self.Images_in_Selected_Channel = glob.glob(
            self.pathstring+'\*C0'+str(self.Channel2crop)+'*')
        
        loops=0;
        while loops < self.Noof_cropsforThisDataset:
            self.zstart = np.random.randint(low=0, high=len(self.Images_in_Selected_Channel)-self.stacks)
           
            image = img_as_ubyte(io.imread(self.Images_in_Selected_Channel[self.zstart]))
            #plt.imshow(image,cmap='gray');
            #bit_8image=img_as_ubyte(image)
            print(len(image))
            self.xstart = int(np.random.randint(
                low=0, high=self.idimx-xpixels))
            self.ystart = int(np.random.randint(
                low=0, high=self.idimy-ypixels))

            self.ylength = self.idimy-(self.ystart+self.ypixels)
            self.xlength = self.idimx-(self.xstart+self.xpixels)

            print(self.ystart, self.ypixels, self.idimy, self.ylength,
                  self.xstart, self.xpixels, self.idimx, self.xlength)
        #CroppedImage=images[self.ystart:self.ylength, self.xstart:self.xlength]
            entropy_img = entropy(image, disk(3))
            # plt.imshow(entropy_img)
            # plt.hist(entropy_img.flat,bins=100,range=(0,5))
            thresh = threshold_otsu(entropy_img)
            binary = entropy_img >= thresh+1
            plt.imshow(binary)

            CroppedMask=crop(binary, ((self.ystart, self.ylength),(self.xstart, self.xlength)), copy='False')
            if np.count_nonzero(CroppedMask)/np.size(CroppedMask)>0.12:
                images = img_as_ubyte(io.ImageCollection(self.Images_in_Selected_Channel[self.zstart:self.zstart+self.stacks]))
                print('read all images from '+str(loops+1) + ' set')
                print(len(images))
                CroppedImage = crop(images, ((0, 0), (self.ystart, self.ylength),(self.xstart, self.xlength)), copy='False')
                print('cropped')
                # io.imsave('imagecollection8bit.tiff',img_as_ubyte(io.ImageCollection.concatenate(CroppedImage)))
                io.imsave('imagecrops'+str(loops+1)+'.tiff', io.ImageCollection.concatenate(CroppedImage))
                print('saved')
                loops+=1
            else:
                continue


pathstring = (r"Z:\$$$$\$$$\$$$\$$$\mouseC_PV488_Myo6568")

#img=LoadAndCropImage(pathstring)

#img.SelectChannel()

#img.CreateImagecrops()

#append parameter in tifffiles imwrite or tifffile

# exit()
