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


import os
# Utility imports
import unittest
import numpy as np

import miplib.ui.cli.miplib_entry_point_options as opts
from miplib.data.io import read as miplibread
from quoll.frc import oneimg
from quoll.frc import frc_calibration_functions as cf
from quoll.io import reader


class OneImgFRCTest(unittest.TestCase):
    """
    Tests the one image FRC
    Test image = ChargeSuppression/SerialFIB-79, Tile 42
    """

    def test_miplib_basic(self):
        """
        Tests that the adapted miplib one image FRC works with basic case
        """
        miplibImg = miplibread.get_image("./data/042.tif")
        args = opts.get_frc_script_options([None])

        result = oneimg.miplib_oneimg_FRC_calibrated(
            miplibImg,
            args,
            oneimg.calibration_func_RFI
        )

        self.assertIsNotNone(result)

    def test_calc_frc_res(self):
        """
        Tests that the one-image FRC can be calculated from quoll.io.reader.Image
        """
        Img = reader.Image("./data/042.tif")
        result = oneimg.calc_frc_res(
            Image=Img,
            calibration_func=oneimg.calibration_func_RFI
        )
        self.assertAlmostEqual(result.resolution["resolution"], 32.1159278)
        self.assertIsNotNone(result)

    def test_calc_frc_res_error(self):
        """
        Tests that error is raised if the input image is not square
        """
        Img = reader.Image("./data/042_notsquare.tif")
        self.assertRaises(ValueError, oneimg.calc_frc_res, Img)

    def test_calc_local_frc(self):
        """
        Tests on SerialFIB57 2048x2048 patch whether the local resolution is calculated
        and heatmap is plotted
        """
        Img = reader.Image(
            filename="./data/SerialFIB57_2048x2048.tif",
            pixel_size=3.3724,
            unit="nm"
        )

        results_df = oneimg.calc_local_frc(
            Img,
            tile_size=512,
            tiles_dir="./data/tiles2/",
            calibration_func=oneimg.calibration_func_RFI)

        # Check that tiles are created and saved
        self.assertNotEqual(len(os.listdir("./data/tiles2")), 0)

        # Check that the mean resolution > pxsize (i.e., not NaNs for all tiles, since we know
        # this is not the case with the known data)
        self.assertGreater(results_df.Resolution.mean(), 3.3724)

        resolution_heatmap = oneimg.plot_resolution_heatmap(
            Img, results_df,
            save_overlay=True,
            save_heatmap=True
        )

        self.assertTrue(os.path.exists("./data/SerialFIB57_2048x2048_overlay.svg"))
        self.assertTrue(os.path.exists("./data/SerialFIB57_2048x2048_heatmap.tif"))

        # check that the resolution heatmap is not empty
        self.assertGreater(np.mean(resolution_heatmap), 0)

    def test_set_calibration_func(self):
        """
        Tests that calibration function can be set to a custom function
        In this test, calibration function is set to return the exact same 
        value, so the result should be equal to uncalibrated.
        """
        Img = reader.Image("./data/042.tif")
        result_calibrated = oneimg.calc_frc_res(
            Image=Img,
            calibration_func=lambda x: x  # just return original value
        )
        result_uncalibrated = oneimg.calc_frc_res(
            Image=Img,
            calibration_func=None
        )
        self.assertAlmostEqual(
            result_calibrated.resolution["resolution"], 
            result_uncalibrated.resolution["resolution"])
        self.assertIsNotNone(result_calibrated.resolution["resolution"])
        self.assertIsNotNone(result_uncalibrated.resolution["resolution"])
    def test_set_calibration_func(self):
        """
        Tests that calibration function can be set to a custom function
        In this test, calibration function is set to return the exact same 
        value, so the result should be equal to uncalibrated.
        """
        Img = reader.Image("./data/042.tif")
        result_calibrated = oneimg.calc_frc_res(
            Image=Img,
            calibration_func=lambda x: x  # just return original value
        )
        result_uncalibrated = oneimg.calc_frc_res(
            Image=Img,
            calibration_func=None
        )
        self.assertAlmostEqual(
            result_calibrated.resolution["resolution"], 
            result_uncalibrated.resolution["resolution"])
        self.assertIsNotNone(result_calibrated.resolution["resolution"])
        self.assertIsNotNone(result_uncalibrated.resolution["resolution"])
