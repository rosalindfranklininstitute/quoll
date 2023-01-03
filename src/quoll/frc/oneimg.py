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

import matplotlib.pyplot as plt
import miplib.data.iterators.fourier_ring_iterators as iterators
import miplib.processing.image as imops
import miplib.ui.cli.miplib_entry_point_options as opts
import numpy as np
import pandas as pd
import tifffile
from miplib.analysis.resolution import analysis as frc_analysis
from miplib.analysis.resolution.fourier_ring_correlation import FRC
from miplib.data.containers.fourier_correlation_data import \
    FourierCorrelationDataCollection
from miplib.data.containers.image import Image as miplibImage
from miplib.processing import windowing
from tqdm import tqdm

from quoll.frc import frc_calibration_functions as cf
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
        image (miplib.data.containers.image.Image): Image to be evaluated
        args (argparse Namespace): parameters for FRC calculation.
                                   see *miplib.ui.frc_options* for details.
                                   default = None
        calibration_func (callable): function that applies a correction factor 
                                     to the frequencies of the FRC curve to
                                     match the 1 img FRC to the 2 img FRC.
                                     Import from quoll.frc.frc_calibration_
                                     functions. If None, no calibration is
                                     performed.

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
    
    else:
        frc_data[0].correlation["frequency"] = freqs

    # Analyze results
    analyzer = frc_analysis.FourierCorrelationAnalysis(
        frc_data, 
        image1.spacing[0], 
        args
    )

    result = analyzer.execute(z_correction=z_correction)[0]

    return result


def calc_frc_res(
    Image: reader.Image,
    calibration_func: Optional[Callable] = None
    ):
    """Calculates one image FRC resolution for quoll Image object

    Args:
        Image (reader.Image): Quoll.io.reader.Image instance
        calibration_func (callable): function that applies a correction factor 
                                     to the frequencies of the FRC curve to
                                     match the 1 img FRC to the 2 img FRC. If 
                                     None, no calibration is applied. Import
                                     from quoll.frc.frc_calibration_functions.

    Raises:
        ValueError: if Image is not square

    Returns:
        FourierCorrelationData object: special dict which contains the results.
    """
    if Image.img_dims[0] == Image.img_dims[1]:
        miplibImg = miplibImage(
            Image.img_data,
            (Image.pixel_size, Image.pixel_size)
        )
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
    tiles_dir: Optional[str] = None,
    calibration_func: Optional[Callable] = None
):
    """ Calculates local FRC on a quoll Image

    Image is split into square tiles and FRC resolution is calculated for all
    tiles

    Args:
        Image (reader.Image): Quoll.io.reader.Image instance
        tile_size (int): length of one side of the square tile in pixels
        tiles_dir (str): path to directory holding tiles, none by default.
                         Tiles only saved if tiles_dir is not none.
        calibration_func (callable): function that applies a correction factor
                                     to the frequencies of the FRC curve to
                                     match the 1 img FRC to the 2 img FRC. 
                                     If None, no calibration is applied. Import
                                     from quoll.frc.frc_calibration_functions.
    Returns:
        pandas DataFrame: df containing the resolutions in physical units
                          of all tiles
    """
    # Create patches
    tiles.create_patches(
        Image=Image,
        tile_size=tile_size,
        tiles_output=tiles_dir
    )

    # Calculate local FRC on the patches
    resolutions = {"Resolution": {}}
    for i in tqdm(list(Image.tiles.keys())):
        try:
            Img = reader.Image(
                img_data=Image.tiles[i],
                pixel_size=Image.pixel_size,
                unit=Image.unit,
            )
            result = calc_frc_res(Img, calibration_func)
            resolutions["Resolution"][i] = result.resolution["resolution"]

        except:
            resolutions["Resolution"][i] = np.nan

    return pd.DataFrame.from_dict(resolutions)


def plot_resolution_heatmap(
    Image: reader.Image,
    results_df: pd.DataFrame,
    show: Optional[bool] = False,
    save_overlay: Optional[bool] = False,
    save_heatmap: Optional[bool] = False,
):
    """Generate a heatmap of resolutions
    
    Optionally display the heatmap overlaid on the original image,
    save this overlay, or save the heatmap alone.

    Args:
        Image (reader.Image): Quoll.reader.Image object
        results_df (pd.DataFrame): output of `oneimg.calc_local_frc`
        show (Optional[bool], optional): Show the overlay. Defaults to False.
        save_overlay (Optional[bool], optional): Saves overlay as svg. 
                                                 Defaults to False.
        save_heatmap (Optional[bool], optional): Saves heatmap as tif. 
                                                 Defaults to False.

    Returns:
        array: image reassembled from tiles
    """
    tileshape = list(Image.tiles.values())[0].shape
    restiles = [np.full(shape=tileshape, fill_value=res) for res in np.array(results_df.Resolution)]
    heatmap = tiles.reassemble_tiles(
        tiles=restiles,
        nTiles=Image.tile_arrangement,
    )


    def plot_overlay():
        plt.figure()
        plt.imshow(Image.img_data, cmap="Greys_r")
        plt.imshow(heatmap, cmap="viridis", alpha=0.4)
        plt.colorbar(label=f"Resolution ({Image.unit})")


    if show is True:
        plot_overlay()
        plt.show()
    
    if save_overlay is True:
        plot_overlay()
        ov_fname = f"{os.path.splitext(Image.filename)[0]}_overlay.svg"
        plt.savefig(ov_fname)
        print(f"Overlay saved as {ov_fname}")
        
    if save_heatmap is True:
        heatmap_fname = f"{os.path.splitext(Image.filename)[0]}_heatmap.tif"
        tifffile.imwrite(
            heatmap_fname,
            heatmap.astype("uint8"),
        )
        print(f"Heatmap saved as {heatmap_fname}")
        
    return heatmap
