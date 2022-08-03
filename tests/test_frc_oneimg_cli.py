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
import subprocess
import unittest
import shutil

class OneImgFRCCLITest(unittest.TestCase):
    """
    Tests the one image FRC CLI
    Test image = ChargeSuppression/SerialFIB-79, Tile 42
    """

    def test_oneimgfrc_notiles(self):
        """
        Tests that oneimg FRC CLI works on a basic case with no tiles
        """
        cmd = [
            "oneimgFRC",
            "./data/042.tif",
            "3.3724"
        ]
        run = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            stderr=subprocess.STDOUT
        )

        self.assertIsNone(run.stderr)
    
    def test_oneimgfrc_notiles_saveresults(self):
        """
        Tests that oneimg FRC CLI with basic case, no tiling, saves csv results
        """
        cmd = [
            "oneimgFRC",
            "./data/042.tif",
            "3.3724",
            "--save_csv"
        ]
        run = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            stderr=subprocess.STDOUT
        )
        self.assertTrue(os.path.exists("./data/042_oneimgfrc.csv"))
        os.remove("./data/042_oneimgfrc.csv")
    
    def test_oneimgfrc_tiles(self):
        """
        Tests that the oneimg FRC CLI works on a basic case with tiling
        """
        if os.path.isdir("./data/tiles"):
            shutil.rmtree("./data/tiles")
        cmd = [
            "oneimgFRC",
            "./data/SerialFIB57_2048x2048.tif",
            "3.3724",
            "-ts",
            "512",
            "-td",
            "./data/tiles"
        ]
        run = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            stderr=subprocess.STDOUT
        )
        self.assertIsNone(run.stderr)
    
    def test_oneimgfrc_tiles_saveresults(self):
        """
        Tests that the oneimg FRC CLI works on a basic case with tiling,
        saves csv results
        """
        if os.path.isdir("./data/tiles"):
            shutil.rmtree("./data/tiles")
        cmd = [
            "oneimgFRC",
            "./data/SerialFIB57_2048x2048.tif",
            "3.3724",
            "-ts",
            "512",
            "-td",
            "./data/tiles",
            "--save_csv"
        ]
        run = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            stderr=subprocess.STDOUT
        )
        self.assertTrue(os.path.exists("./data/SerialFIB57_2048x2048_oneimgfrc.csv"))
        os.remove("./data/SerialFIB57_2048x2048_oneimgfrc.csv")
    
    def test_oneimgfrc_tiles_save_plots(self):
        """
        Tests that the oneimg FRC CLI with tiling saves heatmaps and overlays when
        requested
        """
        if os.path.isdir("./data/tiles"):
            shutil.rmtree("./data/tiles")
        cmd = [
            "oneimgFRC",
            "./data/SerialFIB57_2048x2048.tif",
            "3.3724",
            "-ts",
            "512",
            "-td",
            "./data/tiles",
            "--save_heatmap",
            "--save_overlay",
        ]
        run = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            stderr=subprocess.STDOUT
        )
        self.assertTrue(os.path.exists("./data/SerialFIB57_2048x2048_overlay.svg"))
        self.assertTrue(os.path.exists("./data/SerialFIB57_2048x2048_heatmap.tif"))
        os.remove("./data/SerialFIB57_2048x2048_overlay.svg")
        os.remove("./data/SerialFIB57_2048x2048_heatmap.tif")
