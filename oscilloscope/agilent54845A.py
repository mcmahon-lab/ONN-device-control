import visa
import numpy as np

class Agilent54845A:
    def __init__(self,instrument,chan_num=1):
        """
        Default constructor only requires direct access to the underlyign visa
        handler. See the method fromResourceManager for a more user-friendly way
        of constructing the class.
        """
        self.channel_num = chan_num
        self.instrument = instrument

    @classmethod
    def fromResourceManager(cls,resource_manager,device_type="GPIB"):
        """
        Parameters:
        -----------
        resource_manager                    Resource manager from the visa module.
                                            See pyvisa documentation.
        device_type                         Specifies the type of device to
                                            communicate with.
        """
        resources = resource_manager.list_resources()
        gpib_resources = list(filter(lambda resource_id :
                                        device_type in resource_id, resources))

        # need to handle if no GPIB devices found
        if len(gpib_resources) == 0: raise Exception("No GPIB devices found.")

        # need to handle if more than one GPIB resource connected.
        # TODO: this will be necessary when we add AWG or another GPIB device.
        if len(gpib_resources) > 1: raise Exception("More than one device found")

        instrument = resource_manager.open_resource(gpib_resources[0])
        instrument.timeout = 6000
        #instrument.write("*RST")

        return cls(instrument)

    def get_xrange(self):
        return self.instrument.query_ascii_values("WAV:XRAN?")[0]

    def get_xunits(self):
        return self.instrument.query("WAV:XUN?").rstrip('\n')

    def get_yrange(self):
        return self.instrument.query_ascii_values("WAV:YRAN?")[0]

    def get_yunits(self):
        return self.instrument.query("WAV:YUN?").rstrip('\n')

    def get_offset(self):
        return self.instrument.query_ascii_values("CHAN%d:OFFS?" % self.channel_num)[0]

    def get_bottom_bound(self):
        """ Gets the voltage at the bottom of the scope window. """
        return self.get_offset() - 0.5*self.get_yrange()

    def get_top_bound(self):
        """ Gets the voltage at the top of the scope window. """
        return self.get_offset() + 0.5*self.get_yrange()

    def set_offset(self,value):
        """ Sets the center of the window of the scope. """
        offset_command = "CHAN%d:OFFS " % self.channel_num
        self.instrument.write(offset_command + str(value))

    def set_range(self,value):
        """ Sets the total vertical range of the scope. """
        range_command = "CHAN%d:RANG " % self.channel_num
        self.instrument.write(range_command + str(value))

    def recenter(self):
        v_average = self.instrument.query_ascii_values("MEAS:VAV?")[0]
        self.instrument.write("CHAN" + str(self.channel_num) + ":OFFS " + str(v_average))

    def scope_autoscale(self):
        """
        Instructs the oscilloscope to autoscale the axes. Returns the
        values of the ranges after doing the autoscale.
        """
        self.instrument.write("AUT")

        # return range of x,y values after doing auto scale
        return {'x' : [self.get_xrange(), self.get_xunits()],
                'y': [self.get_yrange(), self.get_yunits()]}

    def reset_window(self):
        """
        Resets the window to full scale (16 V), then brings the signal to center.
        """
        self.set_range(16)
        self.recenter()
        self.recenter() # twice needed in case signal was out of range the first time.

    def autoscale(self):
        """
        Auto scaling function to find the optimal window for a given signal.
        """
        self.reset_window()
        self.rescale(True)

    def rescale(self,quick_scale=True):
        """
        Rescales the window based on measurements on signal iteratively as best it
        can to fill a noisy signal + 5sigma of fluctauations to the entire window.

        By setting quick_scale=True, it will first attempt a rough guess of the final
        window config before starting an iterative procedure. If this is used just after
        reset_window(), this should speed up the scaling.

        Usage:
            self.reset_window()
            self.rescale(False)
        Parameters:
        -----------
        quick_scale                         Boolean to to decide whether or not
                                            to 'one-shot' the window config. Use
                                            only if used a reset_window() before.
        """
        self.instrument.write("MEAS:CLE") # clear current measurements.
        self.instrument.write("MEAS:STAT ON") # turn on statistics tracking

        # measurements to perform.
        self.instrument.write("MEAS:VMAX")
        self.instrument.write("MEAS:VMIN")
        self.instrument.write("MEAS:VAV")
        time.sleep(8)

        # contains results of all three measurements.
        query = self.instrument.query("MEAS:RES?").split(",")

        # maximum voltage of signal
        vmax = np.array(query[1:7],dtype=float)
        if query[0].upper() != "V MAX(1)":
            raise Exception(query[0] + " is not measuring maximum voltage.")

        # minimum voltage of signal
        vmin = np.array(query[8:14],dtype=float)
        if query[7].upper() != "V MIN(1)":
            raise Exception(query[7] + " is not measuring minimum voltage.")

        # average signal of signal
        vav = np.array(query[15:21],dtype=float)
        if query[14].upper() != "V AVG(1)":
            raise Exception(query[14] + " is not measuring minimum voltage.")

        num_samples = vmax[-1]
        if num_samples < 5:
            raise Warning("Only collected " + str(num_samples) + " samples.")

        # if signal goes outside of current window bounds, zoom out before continuing.
        if vmin[1] < self.get_bottom_bound() or vmax[2] > self.get_top_bound():
            self.set_offset((vav[2] + vav[1])/2)
            self.set_range(self.get_yrange()*2)
            self.rescale(False)
            return

        # find the maximum deviation of the signal from its average while accounting
        # for 5 sigma of fluctuations.
        v_amp = vmax if np.abs(vmax[2] - vav[2]) > np.abs(vmin[2] - vav[2] ) else vmin
        v_amp_max = np.abs(v_amp[2] - vav[2]) + 5*np.sqrt(2)*v_amp[4]

        # if high voltage signal, oscilloscope is not capable of performing high
        # resolution zooms. If this is the case, attempt zoom beyond scope capabilities.
        # Additionally, turn off 'one-shot' attempt as this is not accurate for
        # high voltages.
        rmin = 0.064
        if vav[2] > 1.0:
            rmin = 0.8
            quick_scale = False

        # ESCAPE CONDITION
        range = self.get_yrange()
        if range/2 < v_amp_max or range/2 < rmin:
            self.set_offset((vav[2] + vav[1])/2)
            return

        # one-shot attempt
        if quick_scale:
            self.set_range(v_amp_max)
            self.recenter()
            self.rescale(False)
            return

        # iterative attempts
        self.set_range(range/2)
        self.set_offset((vav[2] + vav[1])/2)
        self.rescale(False)

    def id(self):
        return self.instrument.query('*IDN?')

    def set_waveform_source(self,channel_num):
        """
        Parameters
        ----------
        channel_num                     Sets the source for the WAVEFORM operation
                                        the channel given by channel_num.
        """
        self.channel_num = channel_num
        self.instrument.write("WAV:SOUR CHAN %d" % channel_num)

    def enable_header_data(self):
        self.instrument.write("SYST:HEAD ON")

    def disable_header_data(self):
        self.instrument.write("SYST:HEAD OFF")

    def get_waveform(self):
        """
        Main data-taking function. Grabs the waveform currently measured by
        oscilloscope while checking that the waveform is currently within window
        bounds. If not, will automatically autoscale.
        """
        num_attempts = 0
        while True:
            wave = self.instrument.query_ascii_values("WAV:DATA?",container = np.array)
            within_bounds = (wave < self.get_top_bound()).all() and (wave > self.get_bottom_bound()).all()
            if within_bounds:
                return wave
            else:
                self.autoscale()
                num_attempts += 1


    def get_num_points(self):
        """
        Returns the number of points measured by the scope for the waveform function.
        """
        return int(self.instrument.query_ascii_values("WAV:POIN?")[0])

    def close(self):
        self.instrument.close()
