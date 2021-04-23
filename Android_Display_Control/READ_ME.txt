READ ME

General Guidance
-----------------
Any python script attempting to communicate with an Android App over USB should import aoab.py. If it is not in the same directory, then the file path will have to be linked.



aoab2.py
--------------------
Essentially just barebones USB communication adopted from:
 https://github.com/chris-blay/android-open-accessory-bridge

Primary change is the IDs have been changed to work with the Pixel hardware.

Sends up to 0xffff bytes of data. To be used with 'Image Stream Local' Android app.

IMPORTANT:
When creating an AndroidOpenAccessoryBridge object to communicate with an device, the manufacturer specified in the python script must match the manufacturer specified in app/src/main/res/xml/accessory_filter.xml


aoab3.py
--------------------
The same as aoab2.py, but can send up to 0xffffff bytes of data.
Duplicates AndroidOpenAccessoryBridge class found in image_stream.py

To be used with 'Image Stream' Android app.


image_stream.py
----------------
Handles communication with an Android device over USB. Data should be formatted into an array of bytes, and sent using the ‘write()’ method.

To send an image of N pixels, create a byte array of the following form: [R1, G1, B1, R2, … RN, GN, BN]. The Android app (described below) will interpret incoming data in this form.

Exit Android Studio and reconnect phone before use.


send_png.py
-------------
Similar operation to image_stream.py, only the byte array that is sent to the phone is constructed from a PNG file rather than locally in the script.

Exit Android Studio and reconnect phone before use.



ImageStream (Android Project)
--------------------------------
To use this project, download Android Studio and open the project directory. You can build and load the project onto any Android device. 

The app has two functions: display images and communicate over USB. The app expects to communicate with a computer running the image_stream.py script.

When you create an AndroidOpenAccessoryBridge object (from aoab.py), the manufacturer must match the manufacturer set in the Android Project. Currently, it is set to 'ImageStreamManufacturer'.

HOW TO SETUP:
Currently there are two proven ways to use the app:

Exit Android Studio before use for best results.

1) Connect the phone to the computer with USB. Do not open the app. Run a python script that sends data to the app. The app will open itself and display the image. This method works without fail, and for me is the simplest approach.

2) If you just plug in the phone and run the app, on the first attempt to communicate the phone remains black. To get around this, use the following steps. First, plug the phone in and open the app. Run a python script to send an image to the phone (you may notice that the screen does not change, but no errors are thrown). Now close the app on the phone, and re-open it. You can now freely communicate with the app and send images. By default, the app will display a black image until it receives an image to display.



localAccess.py
---------------
A python file containing functions to interact with the ImageStreamLocal Android app.

displayLocal(name) takes a string (name) that is the name of an image file stored locally in the 'app/src/main/res/drawable' directory of the Android project. The app will receive this string, and display the image in the corresponding file.


ImageStreamLocal (Android Project)
------------------------------------
To use this project, download Android Studio and open the project directory. You can build and load the project onto any Android device. 

The app has two functions: display images and communicate over USB. The app expects to communicate with a computer calling the displayLocal() function in localAccess.py.