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
from inspect import getmembers

from matplotlib.pyplot import get
from quoll.frc import oneimg
from quoll.io import reader
from quoll.frc import frc_calibration_functions as cf


def get_calibration_functions() -> dict:
    """ Gets a dict of available calibration functions in `frc.frc_calibration_functions`
    Valid calibration functions all start with "calibration_func"

    Returns:
        dict: Dict of available calibration functions with keys = strings of the
              calibration function and values = the functions themselves
    """
    calibration_functions = {None: None}

    for member in getmembers(cf):
        if member[0].startswith("calibration_func"):
            calibration_functions[member[0]] = member[1]

    return calibration_functions


def get_args_oneimgFRC():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "image_filename",
        type=str,
        help="Filename of the image to be evaluated"
    )
    parser.add_argument(
        "pixel_size",
        type=float,
        help="Pixel size in physical units, nm by default unless --unit is set",
    )
    parser.add_argument(
        "--unit",
        type=str,
        default="nm",
        help="Physical unit of pixel size, default is nm"
    )
    parser.add_argument(
        "-cf", "--calibration_func",
        default=None,
        choices=get_calibration_functions().keys(),
        help="Function defining correction to match 1 image FRC to \
            2 image FRC. This function is instrument specific, so only \
            needs to be determined once for each instrument. \
            Defaults to None (no calibration applied) \
            This function applies a correction factor to return frequencies \
            on the 1-img FRC curve to match the 2-img version. \
            To set a custom calibration function please add your function to \
            frc.frc_calibration_functions.py."
    )
    parser.add_argument(
        "-ts", "--tile_size",
        type=int,
        default=0,
        help="Length of one side of the square tile to split \
            the image into, in pixels. Default=0, where the image \
            resolution is evaluated without tiling."
    )
    parser.add_argument(
        "-td", "--tiles_dir",
        type=str,
        help="Directory to save tiles in, must be specified \
            if tile_size > 0."
    )
    parser.add_argument(
        "--show_plot",
        action="store_true",
        help="Display resolution heatmap overlaid onto image"
    )
    parser.add_argument(
        "--save_overlay",
        action="store_true",
        help="Save the overlay image at <image_filename>_overlay.svg"
    )
    parser.add_argument(
        "--save_heatmap",
        action="store_true",
        help="Save the heatmap as <image_fname>_heatmap.tif"
    )
    parser.add_argument(
        "--save_csv",
        action="store_true",
        help="Saves the results as <image_fname>_oneimgfrc.csv"
    )
    return parser


def oneimgfrc():
    parser = get_args_oneimgFRC()
    args = parser.parse_args()

    Img = reader.Image(
        filename=args.image_filename,
        pixel_size=args.pixel_size,
        unit=args.unit
    )

    cal_funcs = get_calibration_functions()

    if args.tile_size == 0:
        result = oneimg.calc_frc_res(
            Img,
            calibration_func=cal_funcs[args.calibration_func]
        )
        print(f"Resolution of {Img.filename} is {result.resolution['resolution']} {Img.unit}")

        if args.save_csv is True:
            with open(f"{os.path.splitext(Img.filename)[0]}_oneimgfrc.csv", "w") as f:
                f.write(str(result.resolution['resolution']))
    
    elif args.tile_size > 0:
        results_df = oneimg.calc_local_frc(
            Img,
            tile_size=args.tile_size,
            tiles_dir=args.tiles_dir,
            calibration_func=cal_funcs[args.calibration_func]
        )

        print(results_df.Resolution.describe())

        if args.save_csv is True:
            results_df.to_csv(f"{os.path.splitext(Img.filename)[0]}_oneimgfrc.csv")

        resolution_heatmap = oneimg.plot_resolution_heatmap(
            Img,
            results_df,
            show=args.show_plot,
            save_overlay=args.save_overlay,
            save_heatmap=args.save_heatmap
        )
