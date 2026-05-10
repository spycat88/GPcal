"""
    GPcal: a library for various handheld gaming devices
    Author: Kdog
    Version: 0.1
    SPDX-License-Identifier: MIT
"""

from pathlib import Path
import sys

# Default value used when calibration is reset
# DEFAULT_AXIS_MAX : this one is not critical as it only
# impacts the SDL layer (truncate the value) and it will be
# updated during the calibration procedure with an optimal
# value
DEFAULT_AXIS_MAX=0x580
# DEFAULT_TRIGGER_MAX: this one is tricky because the reported value
# from the driver for a trigger is modified with it. The simplified 
# formula is trigger = max(TRIGGER_MAX - raw_value, 0)
# If the value is too low, the range of the trigger is decimated.
# It's better to chose a too big value which will be lowered during
# the calibration procedure.
DEFAULT_TRIGGER_MAX=0x755


class GPCalibration:
    PARAM_PATHS = [
        "/sys/module/retroid/parameters",
        "/sys/module/rsinput/parameters",
        "/sys/module/mangmi/parameters"
    ]

    PARAM_NAMES = [
        "axis_leftx_antideadzone", "axis_leftx_center", "axis_leftx_deadzone", "axis_leftx_max", "axis_leftx_min",
        "axis_lefty_antideadzone", "axis_lefty_center", "axis_lefty_deadzone", "axis_lefty_max", "axis_lefty_min",
        "axis_leftz_antideadzone", "axis_leftz_center", "axis_leftz_deadzone", "axis_leftz_max", "axis_leftz_min",
        "axis_rightx_antideadzone", "axis_rightx_center", "axis_rightx_deadzone", "axis_rightx_max", "axis_rightx_min",
        "axis_righty_antideadzone", "axis_righty_center", "axis_righty_deadzone", "axis_righty_max", "axis_righty_min",
        "axis_rightz_antideadzone", "axis_rightz_center", "axis_rightz_deadzone", "axis_rightz_max", "axis_rightz_min",
        "trigger_left_antideadzone", "trigger_left_deadzone", "trigger_left_max",
        "trigger_right_antideadzone", "trigger_right_deadzone", "trigger_right_max",
        "update_params"
    ]

    def __init__(self, path=None, default_axis_max=DEFAULT_AXIS_MAX, default_trigger_max=DEFAULT_TRIGGER_MAX):
        self.default_axis_max = default_axis_max
        self.default_trigger_max = default_trigger_max
        if path:
            self.syspath = Path(path)
        else:
            self.syspath = self._find_driver_path()
        if not self.syspath or not self.syspath.exists():
            exit(1)
        self.load_parameters()

    def _find_driver_path(self):
        for p in self.PARAM_PATHS:
            parameters = Path(p)
            if parameters.is_dir():
                return parameters
        return None

    def load_parameters(self):
        try:
            for param in self.PARAM_NAMES:
                file_path = self.syspath / param
                if file_path.exists():
                    with open(file_path, "r") as f:
                        setattr(self, param, int(f.readline().strip()))
        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
            exit(1)
        except: #handle other exceptions such as attribute errors
            print(f"Unexpected error:{sys.exc_info()[0]}")
            exit(1)

    def save_parameters(self, savepath):
        with open(savepath,"w") as savefile:
            savefile.write("#!/usr/bin/env bash\n")
            savefile.write("#\n")
            savefile.write("# Gamepad calibration\n")
            savefile.write("# Made with the Kdog GPcal tool\n")
            savefile.write("# SPDX-License-Identifier: MIT\n")
            savefile.write("#\n")
            for param in self.PARAM_NAMES:
                if param == "update_params": continue
                val = getattr(self, param)
                savefile.write(f"echo {val} > {self.syspath}/{param}\n")
            savefile.write(f"echo 1 > {self.syspath}/update_params\n")

    def apply_parameters(self):
        self.update_params=1
        try:
            for param in self.PARAM_NAMES:
                with open(self.syspath / param, "w") as f:
                    f.write(str(getattr(self, param)))
        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
            exit(1)
        except: #handle other exceptions such as attribute errors
            print(f"Unexpected error:{sys.exc_info()[0]}")
            exit(1)

    def reset_axis_left(self):
        self.axis_leftx_antideadzone=0
        self.axis_leftx_center=0
        self.axis_leftx_deadzone=0
        self.axis_leftx_max=self.default_axis_max
        self.axis_leftx_min=-self.default_axis_max
        self.axis_lefty_antideadzone=0
        self.axis_lefty_center=0
        self.axis_lefty_deadzone=0
        self.axis_lefty_max=self.default_axis_max
        self.axis_lefty_min=-self.default_axis_max
        self.axis_leftz_antideadzone=0
        self.axis_leftz_center=0
        self.axis_leftz_deadzone=0
        self.axis_leftz_max=self.default_axis_max
        self.axis_leftz_min=-self.default_axis_max
        self.apply_parameters()

    def reset_axis_right(self):
        self.axis_rightx_antideadzone=0
        self.axis_rightx_center=0
        self.axis_rightx_deadzone=0
        self.axis_rightx_max=self.default_axis_max
        self.axis_rightx_min=-self.default_axis_max
        self.axis_righty_antideadzone=0
        self.axis_righty_center=0
        self.axis_righty_deadzone=0
        self.axis_righty_max=self.default_axis_max
        self.axis_righty_min=-self.default_axis_max
        self.axis_rightz_antideadzone=0
        self.axis_rightz_center=0
        self.axis_rightz_deadzone=0
        self.axis_rightz_max=self.default_axis_max
        self.axis_rightz_min=-self.default_axis_max
        self.apply_parameters()

    def reset_trigger_left(self):
        self.trigger_left_antideadzone=0
        self.trigger_left_deadzone=0
        self.trigger_left_max=self.default_trigger_max
        self.apply_parameters()

    def reset_trigger_right(self):
        self.trigger_right_antideadzone=0
        self.trigger_right_deadzone=0
        self.trigger_right_max=self.default_trigger_max
        self.apply_parameters()

    def reset_all(self):
        self.reset_axis_left()
        self.reset_axis_right()
        self.reset_trigger_left()
        self.reset_trigger_right()
    
    def __str__(self):
        return f"self.axis_leftx_antideadzone={self.axis_leftx_antideadzone}\n" \
                +f"self.axis_leftx_center={self.axis_leftx_center}\n" \
                +f"self.axis_leftx_deadzone={self.axis_leftx_deadzone}\n" \
                +f"self.axis_leftx_max={self.axis_leftx_max}\n" \
                +f"self.axis_leftx_min={self.axis_leftx_min}\n" \
                +f"self.axis_lefty_antideadzone={self.axis_lefty_antideadzone}\n" \
                +f"self.axis_lefty_center={self.axis_lefty_center}\n" \
                +f"self.axis_lefty_deadzone={self.axis_lefty_deadzone}\n" \
                +f"self.axis_lefty_max={self.axis_lefty_max}\n" \
                +f"self.axis_lefty_min={self.axis_lefty_min}\n" \
                +f"self.axis_leftz_antideadzone={self.axis_leftz_antideadzone}\n" \
                +f"self.axis_leftz_center={self.axis_leftz_center}\n" \
                +f"self.axis_leftz_deadzone={self.axis_leftz_deadzone}\n" \
                +f"self.axis_leftz_max={self.axis_leftz_max}\n" \
                +f"self.axis_leftz_min={self.axis_leftz_min}\n" \
                +f"self.axis_rightx_antideadzone={self.axis_rightx_antideadzone}\n" \
                +f"self.axis_rightx_center={self.axis_rightx_center}\n" \
                +f"self.axis_rightx_deadzone={self.axis_rightx_deadzone}\n" \
                +f"self.axis_rightx_max={self.axis_rightx_max}\n" \
                +f"self.axis_rightx_min={self.axis_rightx_min}\n" \
                +f"self.axis_righty_antideadzone={self.axis_righty_antideadzone}\n" \
                +f"self.axis_righty_center={self.axis_righty_center}\n" \
                +f"self.axis_righty_deadzone={self.axis_righty_deadzone}\n" \
                +f"self.axis_righty_max={self.axis_righty_max}\n" \
                +f"self.axis_righty_min={self.axis_righty_min}\n" \
                +f"self.axis_rightz_antideadzone={self.axis_rightz_antideadzone}\n" \
                +f"self.axis_rightz_center={self.axis_rightz_center}\n" \
                +f"self.axis_rightz_deadzone={self.axis_rightz_deadzone}\n" \
                +f"self.axis_rightz_max={self.axis_rightz_max}\n" \
                +f"self.axis_rightz_min={self.axis_rightz_min}\n" \
                +f"self.trigger_left_antideadzone={self.trigger_left_antideadzone}\n" \
                +f"self.trigger_left_deadzone={self.trigger_left_deadzone}\n" \
                +f"self.trigger_left_max={self.trigger_left_max}\n" \
                +f"self.trigger_right_antideadzone={self.trigger_right_antideadzone}\n" \
                +f"self.trigger_right_deadzone={self.trigger_right_deadzone}\n" \
                +f"self.trigger_right_max={self.trigger_right_max}\n" \
                +f"self.update_params={self.update_params}\n"
