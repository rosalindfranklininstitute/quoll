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


import miplib.data.iterators.fourier_ring_iterators as iterators
from miplib.data.io import read as miplibread
import miplib.processing.image as imops
import miplib.ui.cli.miplib_entry_point_options as opts
import numpy as np
from miplib.analysis.resolution import analysis as frc_analysis
from miplib.analysis.resolution.fourier_ring_correlation import FRC
from miplib.data.containers.fourier_correlation_data import \
    FourierCorrelationDataCollection
from miplib.data.containers.image import Image as miplibImage
from miplib.processing import windowing
import argparse
from quoll.io import reader
from quoll.io import tiles
from typing import Optional
import pandas as pd
from typing import Callable
import os


def miplib_oneimg_FRC_calibrated(
    image: miplibImage, 
    args: argparse.Namespace,
    average: Optional[bool] = True, 
    trim: Optional[bool] = True, 
    z_correction: Optional[float] = 1, 
    calibration_func: Optional[Callable] = None):
    """
    A simple utility to calculate a regular FRC with a single image input. 
    Allows user to choose calibration function

    :param image: the image as an Image object
    :param args:  the parameters for the FRC calculation. See *miplib.ui.frc_options*
                  for details
    :param calibration_func: the function to return corrected frequencies, given 
                             uncalibrated frequencies as input.
    :return:      returns the FRC result as a FourierCorrelationData object

    """
    assert isinstance(image, miplibImage)

    frc_data = FourierCorrelationDataCollection()

    # Hamming Windowing
    if not args.disable_hamming:
        spacing = image.spacing
        image = miplibImage(windowing.apply_hamming_window(image), spacing)

    # Split and make sure that the images are the same siz
    image1, image2 = imops.checkerboard_split(image)
    #image1, image2 = imops.reverse_checkerboard_split(image)
    image1, image2 = imops.zero_pad_to_matching_shape(image1, image2)

    # Run FRC
    iterator = iterators.FourierRingIterator(image1.shape, args.d_bin)
    frc_task = FRC(image1, image2, iterator)
    frc_data[0] = frc_task.execute()

    if average:
        # Split and make sure that the images are the same size
        image1, image2 = imops.reverse_checkerboard_split(image)
        image1, image2 = imops.zero_pad_to_matching_shape(image1, image2)
        iterator = iterators.FourierRingIterator(image1.shape, args.d_bin)
        frc_task = FRC(image1, image2, iterator)

        frc_data[0].correlation["correlation"] *= 0.5
        frc_data[0].correlation["correlation"] += 0.5*frc_task.execute().correlation["correlation"]

    freqs = frc_data[0].correlation["frequency"].copy()

    # Apply correction
    if calibration_func is not None:
        frc_data[0].correlation["frequency"] = calibration_func(freqs)

    # Analyze results
    analyzer = frc_analysis.FourierCorrelationAnalysis(frc_data, image1.spacing[0], args)

    result = analyzer.execute(z_correction=z_correction)[0]

    return result


def calibration_func(frequencies: list) -> list:
    correction = 2.066688385682453 + 0.09896293544729941 * np.log(0.08470690336138625 * frequencies)
    corrected_frequencies = frequencies / correction
    return corrected_frequencies


def calc_frc_res(Image: reader.Image):
    if Image.img_dims[0] == Image.img_dims[1]:
        miplibImg = miplibread.get_image(Image.filename)
        args = opts.get_frc_script_options([None])
        result = miplib_oneimg_FRC_calibrated(
            miplibImg,
            args=args,
            calibration_func=calibration_func
        )
    else:
        raise ValueError("Input image must be square")
    return result


def calc_local_frc(
    Image: reader.Image,
    tile_size: int,
    tiles_dir: str,
):
    # Create patches
    tiles.create_patches(Image, tile_size, tiles_dir)

    # Calculate local FRC on the patches
    resolutions = {"Resolution": {}}
    for tile in os.listdir(tiles_dir):
        try:
            Img = reader.Image(os.path.join(tiles_dir, tile))
            result = calc_frc_res(Img)
            resolutions["Resolution"][tile] = result.resolution["resolution"]
        except:
            resolutions["Resolution"][tile] = np.nan
    
    return pd.DataFrame.from_dict(resolutions)
