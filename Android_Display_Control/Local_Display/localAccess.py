from aoab import AndroidOpenAccessoryBridge as AOAB
import usb

PIXEL_VENDOR_ID = 0x18d1
PIXEL_UNCONFIG_ID = 0x4ee7
PIXEL_CONFIG_ID = 0x2d01

def displayLocal(name):
  #create object to access Image Stream Local App
  if isinstance(name, str):
      try:
        comms = AOAB(PIXEL_VENDOR_ID, 
          PIXEL_UNCONFIG_ID, PIXEL_CONFIG_ID, 
          manufacturer='ImageStreamLocal', 
          model='AoabModel', 
          description='Display Local Images', 
          version=1, 
          uri=('https://github.com/chris-blay/android-open-accessory-bridge'), 
          serial='AoabSerial')
        comms.write(name.encode('utf-8'))
      except usb.core.USBError:
        print('USBError occurred')