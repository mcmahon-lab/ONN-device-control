# Device Control Modules for Optical Neural Networks (ONNs)

This repository contains the device control modules for the optical matrix-vector multiplier demonstrated in the following paper:

>Tianyu Wang, Shi-Yuan Ma, Logan G. Wright, Tatsuhiro Onodera, Brian Richard and Peter L. McMahon. "An optical neural network using less than 1 photon per multiplication" _Nature communications_ **13**, 123 (2022) https://doi.org/10.1038/s41467-021-27774-8

The codes for training the neural network model executed in the experiment are available [here](https://github.com/mcmahon-lab/ONN-QAT-SQL).

## [Android_Display_Control](https://github.com/mcmahon-lab/ONN-device-control/blob/master/Android_Display_Control)

An Android application to control the OLED display of Google Pixel phone.

Adopted from <https://github.com/chris-blay/android-open-accessory-bridge>.

## [NN_models](https://github.com/mcmahon-lab/ONN-device-control/blob/master/NN_models)

The neural network models with trained parameters.

The training code is available [here](https://github.com/mcmahon-lab/ONN-QAT-SQL).

## [SLM](https://github.com/mcmahon-lab/ONN-device-control/blob/master/SLM)

The Python script to control the spatial light modulator (SLM, P1920-500-1100-HDMI, Meadowlark Optics).

Adopted from <https://github.com/wavefrontshaping/slmPy>.

## [data_collection](https://github.com/mcmahon-lab/ONN-device-control/blob/master/data_collection)

The Jupyter notebooks that control the experimental setup to collect data.

## [oscilloscope](https://github.com/mcmahon-lab/ONN-device-control/blob/master/oscilloscope)

The Python script to control the oscilloscope that reads data from the multi-pixel photon counter (MPPC, C13366 series GA type, Hamamatsu Photonics).

## [utils](https://github.com/mcmahon-lab/ONN-device-control/blob/master/utils)

Utility functions used in the experiments.

# License

The code in this repository is released under the following license:

[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)

A copy of this license is given in this repository as license.txt.
