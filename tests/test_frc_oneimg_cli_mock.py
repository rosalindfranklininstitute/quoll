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


from unittest import mock
import unittest
import shutil
import os
import sys
from quoll.ui import frc_oneimg_ui

class OneImgFRCCLIMockTest(unittest.TestCase):
    """
    Tests the one image FRC CLI
    Test image = ChargeSuppression/SerialFIB-79, Tile 42
    """

    @mock.patch(
        'sys.argv',
        ["oneimgfrc",
        "./data/042.tif",
        "3.3724",
        "--save_csv"],
    )
    def test_oneimgfrc_notiles_savecsv(self):
        frc_oneimg_ui.oneimgfrc()
        self.assertTrue(os.path.exists("./data/042_oneimgfrc.csv"))
        os.remove("./data/042_oneimgfrc.csv")
    
    @mock.patch(
        'sys.argv',
        ["oneimgFRC",
         "./data/SerialFIB57_2048x2048.tif",
         "3.3724",
         "-ts",
         "512",
         "-td",
         "./data/tiles",
         "--save_csv"
         ]
    )
    def test_oneimgfrc_tiles_savecsv(self):
        frc_oneimg_ui.oneimgfrc()
        self.assertTrue(os.path.exists("./data/SerialFIB57_2048x2048_oneimgfrc.csv"))
        os.remove("./data/SerialFIB57_2048x2048_oneimgfrc.csv")
        shutil.rmtree("./data/tiles", ignore_errors=True)

    @mock.patch(
        'sys.argv',
        ["oneimgFRC",
         "./data/SerialFIB57_2048x2048.tif",
         "3.3724",
         "-ts",
         "512",
         "-td",
         "./data/tiles",
         "--save_heatmap",
         "--save_overlay",]
    )
    def test_oneimgfrc_tiles_saveplots(self):
        frc_oneimg_ui.oneimgfrc()
        self.assertTrue(os.path.exists("./data/SerialFIB57_2048x2048_overlay.svg"))
        self.assertTrue(os.path.exists("./data/SerialFIB57_2048x2048_heatmap.tif"))
        os.remove("./data/SerialFIB57_2048x2048_overlay.svg")
        os.remove("./data/SerialFIB57_2048x2048_heatmap.tif")
        shutil.rmtree("./data/tiles", ignore_errors=True)


if __name__ == "__main__":
    unittest.main()