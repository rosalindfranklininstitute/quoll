# Copyright 2022 Rosalind Franklin Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.


import numpy as np


""" When adding calibration functions here, ensure that your function starts 
with `calibration_func` or else it will not be discovered in the CLI/Napari"""

def calibration_func_RFI(frequencies: list) -> list:
    """ Calibration function to match 1 image FRC to 2 image FRC.

    Redone for EM images.

    Args:
        frequencies (list): x-values in the FRC curve

    Returns:
        list: frequencies with correction factor applied
    """
    correction = 2.066688385682453 + 0.09896293544729941 * np.log(0.08470690336138625 * frequencies)
    corrected_frequencies = frequencies / correction
    return corrected_frequencies
