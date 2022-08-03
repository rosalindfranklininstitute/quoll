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
import argparse
import os
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
    def test_oneimgfrc_notiles(self):
        frc_oneimg_ui.oneimgfrc()
        self.assertTrue(os.path.exists("./data/042_oneimgfrc.csv"))
        os.remove("./data/042_oneimgfrc.csv")

if __name__ == "__main__":
    unittest.main()