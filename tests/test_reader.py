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


# Utility imports
import unittest

from quoll.io import reader


class ReaderTest(unittest.TestCase):
    """
    Tests the reader module.
    Test data is from Fiji sample images (blobs)
    """

    def test_2D_8bit_tiffreader(self):
        """
        Tests that 8bit 2D images are read correctly
        """
        Img = reader.Image(
            filename="./data/blobs.tif",
            pixel_size=1,
            unit="nm",)

        self.assertEqual(Img.filename, "./data/blobs.tif")
        self.assertEqual(Img.img_bitdepth, "uint8")
        self.assertEqual(Img.pixel_size, 1)
        self.assertEqual(Img.unit, "nm")
        self.assertEqual(Img.img_dims, (256,256))

    def test_2D_mrcreader(self):
        """
        Tests that 2D mrc files are read correctly
        Test data is from https://www.ebi.ac.uk/empiar/EMPIAR-10987/
        """
        Img = reader.Image(
            filename="./data/L4_ts_03_sort_bin8_1img.mrc",
            pixel_size=13.12,
            unit="Angstrom",
        )

        self.assertEqual(Img.filename, "./data/L4_ts_03_sort_bin8_1img.mrc")
        self.assertEqual(Img.img_bitdepth, "uint16")
        self.assertEqual(Img.pixel_size, 13.12)
        self.assertEqual(Img.unit, "Angstrom")
        self.assertEqual(Img.img_dims, (720, 512))

    def test_3D_mrcreader(self):
        """
        Tests that 3D mrc files are read correctly
        Test data is from https://www.ebi.ac.uk/empiar/EMPIAR-10987/
        """
        Img = reader.Image(
            filename="./data/L4_ts_03_sort_bin8.mrc",
            pixel_size=13.12,
            unit="Angstrom",
        )

        self.assertEqual(Img.filename, "./data/L4_ts_03_sort_bin8.mrc")
        self.assertEqual(Img.img_bitdepth, "uint16")
        self.assertEqual(Img.pixel_size, 13.12)
        self.assertEqual(Img.unit, "Angstrom")
        self.assertEqual(Img.img_dims, (41, 720, 512))

    def test_TS_importer_mrc_mdoc(self):
        """
        Tests that tilt series can be imported correctly with mdoc
        """
        TS = reader.TiltSeries(
            filename="./data/L4_ts_03_sort_bin8.mrc",
            pixel_size=13.12,
            unit="Angstrom",
            mdoc_file="./data/L4_ts_03_sort.mrc.mdoc"
        )
        self.assertEqual(TS.img_type, "TiltSeries")
        self.assertEqual(TS.filename, "./data/L4_ts_03_sort_bin8.mrc")
        self.assertEqual(TS.img_bitdepth, "uint16")
        self.assertEqual(TS.pixel_size, 13.12)
        self.assertEqual(TS.unit, "Angstrom")
        self.assertEqual(TS.img_dims, (41, 720, 512))
        self.assertEqual(len(TS.tilt_angles), 41)

    def test_TS_importer_mrc_tlt(self):
        """
        Tests that tilt series can be imported correctly with tlt
        """
        TS = reader.TiltSeries(
            filename="./data/L4_ts_03_sort_bin8.mrc",
            pixel_size=13.12,
            unit="Angstrom",
            tilt_angle_file="./data/L4_ts_03_sort.tlt"
        )
        self.assertEqual(TS.img_type, "TiltSeries")
        self.assertEqual(TS.filename, "./data/L4_ts_03_sort_bin8.mrc")
        self.assertEqual(TS.img_bitdepth, "uint16")
        self.assertEqual(TS.pixel_size, 13.12)
        self.assertEqual(TS.unit, "Angstrom")
        self.assertEqual(TS.img_dims, (41, 720, 512))
        self.assertEqual(len(TS.tilt_angles), 41)

    def test_TS_importer_noTA_error(self):
        """
        Tests that error is raised when no tilt angles are specified when importing tiltseries
        """
        self.assertRaises(
            ValueError,
            reader.TiltSeries,
            filename="./data/L4_ts_03_sort_bin8.mrc",)

if __name__ == '__main__':
    unittest.main()
