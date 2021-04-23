# aoab3 written by Brian Richard (bcr53), but mostly adopted from the below example on GitHub
# To be used with ImageStream Android app
# sends up to 0xffffff bytes of data

from __future__ import print_function, unicode_literals

import array
import sys
import time
import usb


PIXEL_VENDOR_ID = 0x18d1
PIXEL_UNCONFIG_ID =  0x4ee7
PIXEL_CONFIG_ID = 0x2d01
_B = 'B' if sys.version_info.major == 3 else b'B'


class AndroidOpenAccessoryBridge:

    def __init__(self,
                 vendor_id, unconfigured_product_id, configured_product_id,
                 manufacturer, model, description, version, uri, serial):
        self._vendor_id = int(vendor_id)
        self._unconfigured_product_id = int(unconfigured_product_id)
        self._configured_product_id = int(configured_product_id)
        self._device = self._configureAndOpenDevice(
            str(manufacturer),
            str(model),
            str(description),
            str(version),
            str(uri),
            str(serial))
        self._endpoint_out, self._endpoint_in = self._detectEndpoints()

    def __enter__(self):
        return self  # All 'enter' work is done in __init__().

    def __exit__(self, type, value, traceback):
        self.close()

    def _detectDevice(self, attempts_left=5):
        unconfigured_device = usb.core.find(
            idVendor=self._vendor_id, idProduct=self._unconfigured_product_id)
        configured_device = usb.core.find(
            idVendor=self._vendor_id, idProduct=self._configured_product_id)
        if not (configured_device is None):
            return configured_device, True
        elif not (unconfigured_device is None):
            return unconfigured_device, False
        elif attempts_left:
            time.sleep(1)
            return self._detectDevice(attempts_left - 1)
        else:
            raise usb.core.USBError('Device not connected')

    def _configureAndOpenDevice(
            self, manufacturer, model, description, version, uri, serial):
        device, is_configured = self._detectDevice()
        if not is_configured:
            # Validate version code.
            buf = device.ctrl_transfer(0xc0, 51, data_or_wLength=2)
            assert(len(buf) == 2 and (buf[0] | buf[1] << 8) == 2)
            # Send accessory.
            for i, data in enumerate(
                    (manufacturer, model, description, version, uri, serial)):
                assert(device.ctrl_transfer(
                       0x40, 52, wIndex=i, data_or_wLength=data) == len(data))
            # Put device into accessory mode.
            assert(device.ctrl_transfer(0x40, 53) == 0)
            usb.util.dispose_resources(device)
        else:
            # This brings your companion app back to foreground.
            device.reset()
            time.sleep(1)

        # Wait for configured device to show up
        attempts_left = 5
        while attempts_left:
            device, is_configured = self._detectDevice()
            if is_configured:
                return device
            time.sleep(1)
            attempts_left -= 1
        raise usb.core.USBError('Device not configured')

    def _detectEndpoints(self):
        assert(self._device)
        configuration = self._device.get_active_configuration()
        interface = configuration[(0, 0)]

        def first_out_endpoint(endpoint):
            return (usb.util.endpoint_direction(endpoint.bEndpointAddress)
                    == usb.util.ENDPOINT_OUT)

        def first_in_endpoint(endpoint):
            return (usb.util.endpoint_direction(endpoint.bEndpointAddress)
                    == usb.util.ENDPOINT_IN)

        endpoint_out = usb.util.find_descriptor(
            interface, custom_match=first_out_endpoint)
        endpoint_in = usb.util.find_descriptor(
            interface, custom_match=first_in_endpoint)
        assert(endpoint_out and endpoint_in)
        return endpoint_out, endpoint_in

    def write(self, data, timeout=None):
        assert(self._device and self._endpoint_out and data)
        size = len(data)
        size_bytes = array.array(_B, [(size & 0x00ff0000) >> 16,
            (size & 0x0000ff00) >> 8,
            (size & 0x000000ff)])
        data_bytes = array.array(_B, data)
        while True:
            try:
                bytes_wrote = self._endpoint_out.write(size_bytes,
                                                       timeout=timeout)
            except usb.core.USBError as e:
                if e.errno == 110:  # Operation timed out
                    print('here')
                    continue
                else:
                    raise e
            else:
                assert(bytes_wrote == 3)
                break
        assert(self._endpoint_out.write(data_bytes, timeout=timeout) == size)

    def read(self, timeout=None):
        assert(self._device and self._endpoint_in)
        try:
            size_bytes = self._endpoint_in.read(2, timeout=timeout)
            size = (size_bytes[0] << 16) | (size_bytes[1] << 8) | (size_bytes[2])
            return self._endpoint_in.read(size, timeout=timeout).tostring()
        except usb.core.USBError as e:
            if e.errno == 110:  # Operation timed out.
                return None
            else:
                raise e

    def close(self):
        assert(self._device and self._endpoint_out)
        self._endpoint_out.write(array.array(_B, [0, 0]))
        usb.util.dispose_resources(self._device)
        self._device = None
        self._endpoint_out = None
        self._endpoint_in = None