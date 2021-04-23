# Send and Display PNG to Image Stream Andriod App
#
#  Loads two images at specfied file names. Sends and displays the first,
#  then after a user input, sends and displays the second.
#
#  Intended to serve as an example of how to send arbitrary png files to
#  the Image Stream Android app. Images must be 1920x1080. If a smaller image
#  is desired, pad it with zeros in appropriate positions. Further details found
#  in the Android_Display_Control READ_ME.
#
# Written by Brian Richard, bcr53
# Last Updated March 2020

import numpy as np
from PIL import Image

from image_stream import AndroidOpenAccessoryBridge as AOAB

PIXEL_VENDOR_ID = 0x18d1
PIXEL_UNCONFIG_ID =  0x4ee7
PIXEL_CONFIG_ID = 0x2d01

# add first file name here, with extention
img1 = Image.open('black.png')
# add second file name here, with extention
img2 = Image.open('test_digit_0_00003.png')
array1 = np.array(img1)
array2 = np.array(img2)
new_array1 = bytearray()
new_array2 = bytearray()


for i in range(array1.shape[0]):
  for j in range(array1.shape[1]):
    new_array1.append(array1[i, j, 0])
    new_array1.append(array1[i, j, 1])
    new_array1.append(array1[i, j, 2])

for i in range(array2.shape[0]):
  for j in range(array2.shape[1]):
    new_array2.append(array2[i, j, 0])
    new_array2.append(array2[i, j, 1])
    new_array2.append(array2[i, j, 2])

assert(len(new_array1) == 1920*1080*3)
assert(len(new_array2) == 1920*1080*3)
print('here')

aoab = AOAB(PIXEL_VENDOR_ID, PIXEL_UNCONFIG_ID, 
  PIXEL_CONFIG_ID,
  manufacturer='ImageStreamManufacturer',
  model='ImageStream1',
  description='Stream Images to Android',
  version=1,
  uri=('https://github.com/chris-blay/android-open-accessory-bridge'),
  serial='AoabSerial')
aoab.write(new_array1)
input()
aoab.write(new_array2)