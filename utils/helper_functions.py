from torchvision.transforms import ToTensor
from torchvision.transforms import ToPILImage
from torchvision.datasets import MNIST
import torch
import numpy as np
import math
import matplotlib.pyplot as plt
import PIL

def SplitMatBySign(mat_in):
    """
    The returns two torch.tensor. matPos are the nonnegative enetries of mat_in,
    with all the other entries set to zero. matNeg are the minus of the negative
    entries of mat_in, with the rest of the elements set to zero. In other words,
    mat_in = matPos - matNeg

    mat_in: the input image is either a PIL image, torch.tensor, or a numpy array,
    and it will be converted to torch.tensor before processed.
    """

    if isinstance(mat_in, (PIL.Image.Image,)) or isinstance(mat_in, (np.ndarray,)):
            mat = ToTensor()(mat_in)
    elif isinstance(mat_in, (torch.Tensor,)):
            mat = mat_in

    (matPos, matNeg) = (torch.zeros_like(mat), torch.zeros_like(mat))
    nonNegIdx = mat >= 0
    (matPos[nonNegIdx], matNeg[~nonNegIdx]) = (mat[nonNegIdx], -mat[~nonNegIdx])

    return matPos, matNeg

def GenAlignImage(image_size, viewfinder_size, corner_cube_size, line_width):
    """
    The function returns a numpy array of a viewfinder image used for phone and SLM alignment.
    The size of the image is height by width by color channel.

    image_size: a 2-element tuple that specifies the height and width of the image.

    viewfinder_size: a 2-element tuple that specifies the height and width of the viewfinder.

    corner_cube_size: a 2-element tuple that specifies the height and width of each corner cube.

    line_width: the line width of the cross bar in pixel numbers
    """
    assert line_width%2 == 1, "line_width should be a odd number to avoid rounding error."
    assert all((viewfinder_size[0]%2 == 1, viewfinder_size[1]%2 == 1)), "viewfinder width and height should be odd numbers to avoid rounding error."

    # Initialize the canvas
    image = np.zeros(shape=(*image_size,3), dtype='uint8')
    cornerCube = np.ones(shape=corner_cube_size, dtype='uint8')*255
    viewFinder = np.zeros(shape=viewfinder_size, dtype = 'uint8')

    # Draw 4 corner cubes to the image.
    viewFinder[0:corner_cube_size[0], 0:corner_cube_size[1]] = cornerCube
    viewFinder += np.flip(viewFinder, 0)
    viewFinder += np.flip(viewFinder, 1)

    # Draw the cross bar 
    # a square box no larger than the view finder
    crossBarBoxSize = (min(5*corner_cube_size[0], viewfinder_size[0]), min(5*corner_cube_size[0], viewfinder_size[1]))
    crossBarBoxSize = tuple(map(lambda x: x + x%2 - 1, crossBarBoxSize)) # if box edge size is even, minus 1 from it.
    crossBarBox = np.zeros(crossBarBoxSize, dtype='uint8')
    middleElements = (int((crossBarBox.shape[0]-1)/2), int((crossBarBox.shape[1]-1)/2)) # the middle element
    lineRange = (-int((line_width-1)/2), int((line_width+1)/2))
    middleRange = range(*tuple(map(sum, zip(middleElements, lineRange)))) 
    crossBarBox[middleRange, :] = 255 # Draw bars
    crossBarBox[:, middleRange] = 255
    barRange = (-int(line_width*2), int(line_width*2+1))
    arrowRange = range(*tuple(map(sum, zip(middleElements, barRange)))) 
    crossBarBox[arrowRange, 0:line_width] = 255
    halfbarRange = (-int(line_width*2), 1)
    halfarrowRange = range(*tuple(map(sum, zip(middleElements, halfbarRange)))) 
    crossBarBox[0:line_width, halfarrowRange] = 255

    # Add the cross bar to the center of the view finder.
    viewFinder = CenterEmbedding(crossBarBox, viewFinder)

    # Add the view finder to the center of the image.
    image[:,:,1] = CenterEmbedding(viewFinder, image[:,:,1])

    return image

def ConvertPhoneImageToSLMImage(image_phone, SLM_to_phone_zoom_ratio):
    """
    Resize the phone display image to be displayed on SLM, such that the phone
    display imaged onto SLM matches exactly the size and position of the one on
    the SLM. Returns a PIL image to be saved.

    image_phone: 2D numpy array with dtype uint8

    SLM_to_phone_zoom_ratio: the number of pixels on the SLM divided the number
    of pixels on the phone such that the pattern of their image are of the same
    size
    """
    r = SLM_to_phone_zoom_ratio # equals the number of pixels of a line on SLM divided the that of the same line on the phone.
    (h, w) = (1152, 1920) # SLM size

    #im = image_phone.transpose() # transpose the image from 1920x1080 to 1080x1920
    #im = im[::-1, :] # flip left and right

    # Pad the phone image to 1920x1600 to give enough margin for cropping later 
    if isinstance(image_phone, (np.ndarray,)):
        #im = np.zeros((1920, 1600), dtype="uint8")
        #im[:, 260:(260+1080)] = image_phone
        im = np.zeros((h, w), dtype="uint8")
        im[36:(36+1080), :] = image_phone.transpose()
        imPIL = PIL.Image.fromarray(im) # Convert from numpy to PIL image
    elif isinstance(image_phone, (torch.Tensor,)):
        #im = torch.zeros(1920, 1600, dtype=torch.uint8)
        #im[:, 260:(260+1080)] = image_phone
        im = torch.zeros(h, w, dtype = torch.uint8)
        im[36:(36+1080), :] = image_phone.t()
        imPIL = ToPILImage()(im) # Convert from numpy to PIL image

    # Adjust pixel values according to SLM LUT
    # im[im == 0] = 155 # pixel value for the max transmission intensity on SLM 
    # im[im == 255] = 77 # pixel value for the min transmission intensity on SLM
    
    # Resize the SLM image
    new_width = round(float(im.shape[1])*r/2)*2 # Calculate the resized image size, round to even number of pixels.
    new_height = round(float(im.shape[0])*r/2)*2 
    imPIL = imPIL.resize((new_width, new_height)) # Resize the image 

    # Transform the image on the SLM to have the same spatial orientation as that on the phone.
    imPIL = PIL.ImageOps.flip(imPIL)
    imPIL = PIL.ImageOps.mirror(imPIL)

    # Create a PIL image of the exactly same size as required by the SLM.
    rowOffset = int((imPIL.size[1] - h)/2) # Calculate the boundary coordinate for cropping the image
    colOffset = int((imPIL.size[0] - w)/2) # PIL.size sequence is reversed from numpy.shape!!!!!!!
    image_SLM = imPIL.crop((colOffset, rowOffset, colOffset+w, rowOffset+h)) # Crop the image to fit SLM size (1152x1920)

    return image_SLM

def NormalizeWeights(weights, biases):
    """
    Returns
    normWeights: w' = (w-min(w))/(max(w)-min(w)) 
    normBiases: b' = b/(max(w)-min(w))
    weightCompensate: w0 = min(w)/(max(w)-min(w))
    
    """
    normWeights = []
    normBiases = []
    weightCompensates = []

    for w, b in zip(weights, biases):
        w_min = torch.min(w)
        wShift = w-w_min
        w0 = torch.max(wShift)
        wPrime = wShift/w0
        wPrime = torch.cat((wPrime, torch.ones(1, wPrime.shape[1])), 0)
        dw = w_min/w0
        bPrime = b/w0 # b' = b/(max(w)-min(w))

        #print(f"min(w): {w_min}; max(w)-min(w): {wShift}")
        #print(f"-min(w)/(max(w)-min(w))={-wShift/w0}")
        #print(f"Is w' normalized and non-negative? {((wPrime>=0) & (wPrime<=1)).all()}")
        #print(bPrime)
        
        normWeights.append(wPrime)
        normBiases.append(bPrime)
        weightCompensates.append(dw)

    return normWeights, normBiases, weightCompensates

def CenterEmbedding(image, canvas):
    """
    Returns a 2D array of the same type and size as 'canvas', with image at the
    center of it. If any of the 'image' dimension exceeds that ofß 'canvas', the
    center part of the image is cropped to the same size of the canvas. 
    
    image: 2D numpy.array or torch.tensor

    canvas: 2D array of the same type as image.
    """
    dimCanvas = np.array(canvas.shape)
    dimImage = np.array(image.shape)
    
    # the minimum size that can contain either the canvas or the image 
    union_size = [max(d1,d2) for d1, d2 in zip(dimCanvas, dimImage)] 
    offsets = ((dimCanvas - dimImage)/2).astype(int)
    offset_canvas = offsets * (offsets >= 0).astype(int)
    offset_image = - offsets * (offsets < 0).astype(int)

    if isinstance(image, (np.ndarray,)) and isinstance(canvas, (np.ndarray,)):
        image_embedded = np.zeros(union_size)
    elif isinstance(image, (torch.Tensor,)) and isinstance(canvas, (torch.Tensor,)):
        image_embedded = torch.zeros(union_size, dtype=canvas.dtype)
    else:
        print("The input arrays must be either both numpy.ndarray or torch.tensor.")
        pass

    image_embedded[offset_image[0]:offset_image[0]+dimCanvas[0], offset_image[1]:offset_image[1]+dimCanvas[1]] = canvas
    image_embedded[offset_canvas[0]:offset_canvas[0]+dimImage[0], offset_canvas[1]:offset_canvas[1]+dimImage[1]] += image
    image_embedded = image_embedded[offset_image[0]:offset_image[0]+dimCanvas[0], offset_image[1]:offset_image[1]+dimCanvas[1]]

    return image_embedded

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(__file__)) # set working directory to the file directory

    x = torch.randn(4,4)
    p,n = SplitMatBySign(x)
    print(p)
    print(n)
    print(x)
    im_phone = GenAlignImage((1920,1080), (801,801), (20,20), 7)
    plt.imsave('../image/GreenViewFinder.bmp', im_phone)
    image_SLM = ConvertPhoneImageToSLMImage(im_phone[:,:,1], 1.0)
    image_SLM.save('../image/ViewFinder_1.bmp', format = 'bmp') # PIL.Image.save can save as 8-bit bmp