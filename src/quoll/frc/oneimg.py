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


import argparse
import os
from typing import Callable, Optional

import miplib.data.iterators.fourier_ring_iterators as iterators
import miplib.processing.image as imops
import miplib.ui.cli.miplib_entry_point_options as opts
import numpy as np
import pandas as pd
from miplib.analysis.resolution import analysis as frc_analysis
from miplib.analysis.resolution.fourier_ring_correlation import FRC
from miplib.data.containers.fourier_correlation_data import \
    FourierCorrelationDataCollection
from miplib.data.containers.image import Image as miplibImage
from miplib.data.io import read as miplibread
from miplib.processing import windowing
from quoll.io import reader, tiles


def miplib_oneimg_FRC_calibrated(
    image: miplibImage,
    args: argparse.Namespace,
    average: Optional[bool] = True,
    trim: Optional[bool] = True,
    z_correction: Optional[float] = 1,
    calibration_func: Optional[Callable] = None):
    """ Calculate single image FRC, adapted from miplib

    Args:
        image (miplib image object): x-values in the FRC curve
        args (argparse Namespace): parameters for FRC calculation.
                                   see *miplib.ui.frc_options* for details.
                                   default = None
        calibration_func (callable): function that applies a correction factor to the
                                     frequencies of the FRC curve to match the 1 img
                                     FRC to the 2 img FRC

    Returns:
        FourierCorrelationData object: special dict which contains the results.
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


def calc_frc_res(Image: reader.Image):
    """Calculates one image FRC resolution for quoll Image object

    Args:
        Image (reader.Image): Quoll.io.reader.Image instance

    Raises:
        ValueError: if Image is not square

    Returns:
        FourierCorrelationData object: special dict which contains the results.
    """
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
    """ Calculates local FRC on a quoll Image

    Image is split into square tiles and FRC resolution is calculated for all tiles

    Args:
        Image (reader.Image): Quoll.io.reader.Image instance
        tile_size (int): length of one side of the square tile in pixels
        tiles_dir (str): path to directory holding tiles

    Returns:
        pandas DataFrame: df containing the resolutions in physical units
                          of all tiles
    """
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


def plot_resolution_heatmap(
    Image: reader.Image,
    results_df: pd.DataFrame,
):
    tileshape = list(Image.tiles.values())[0].shape
    restiles = [np.full(shape=tileshape, fill_value=res) for res in np.array(results_df.Resolution)]
    heatmap = tiles.reassemble_tiles(
        tiles=restiles,
        nTiles=Image.tile_arrangement,
    )
    return heatmap
