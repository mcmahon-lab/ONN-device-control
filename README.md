# ONN-device-control

This repository contains the device control modules for implementating the optical matrix-vector multiplier demonstrated in the following paper:

Author *et al.* (2021). An optical neural network using less than 1 photon per multiplication. *Journal Title, Volume* (Issue), page range. DOI

The scripts for training neural networks executed in the experiments are available [here](https://github.com/mcmahon-lab/ONN-QAT-SQL).

## [Android_Display_Control](https://github.com/mcmahon-lab/ONN-device-control/blob/master/Android_Display_Control)

The Android control module to control the cell phone (OLED display).

Adopted from <https://github.com/chris-blay/android-open-accessory-bridge>.

## [NN_models](https://github.com/mcmahon-lab/ONN-device-control/blob/master/NN_models)

Neural network model with trained parameters.

The training code is available [here](https://github.com/mcmahon-lab/ONN-QAT-SQL).

## [SLM](https://github.com/mcmahon-lab/ONN-device-control/blob/master/SLM)

The Python script to control the 1920 x 1152 Analog Spatial Light Modulator, Meadowlark Optics.

Adopted from <https://github.com/wavefrontshaping/slmPy>.

## [data_collection](https://github.com/mcmahon-lab/ONN-device-control/blob/master/data_collection)

Jupyter notebooks that control the experimental setup to collect data.

## [oscilloscope](https://github.com/mcmahon-lab/ONN-device-control/blob/master/oscilloscope)

The Python script to control the oscilloscope that reads the data from the multi-pixel photon counter (MPPC, C13366 series GA type, Hamamatsu Photonics).

## [utils](https://github.com/mcmahon-lab/ONN-device-control/blob/master/utils)

Utility functions used in the experiments.

# License

The code in this repository is released under the following license:

[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)

A copy of this license is given in this repository as license.txt.