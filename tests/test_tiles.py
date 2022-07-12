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
import shutil
import numpy as np
# Utility imports
import unittest

from quoll.io import reader, tiles
from tifffile import TiffFile


class TilesTest(unittest.TestCase):
    """
    Tests the tiles
    """

    def test_tiles_extraction(self):
        """
        Tests that the tiles are created correctly from a quoll.io.reader.Image object
        """
        Img = reader.Image("./data/blobs.tif")
        tiles_list, (nTilesX, nTilesY) = tiles.extract_tiles(Img, 128, 128, pad=True)

        self.assertEqual(len(tiles_list), nTilesX * nTilesY)
        self.assertEqual(tiles_list[0].shape, (128, 128))


    def test_square_tiles_saving(self):
        """
        Tests that the square tiles for local image resolution estimation with
        one image FRC are exported correctly
        """
        Img = reader.Image("./data/blobs.tif", pixel_size=50, unit="nm")

        tiles_dir = "./data/tiles"

        tiles.create_patches(
            Img,
            tile_size=128,
            tiles_output=tiles_dir,
            pad=True
        )

        self.assertEqual(len(os.listdir(tiles_dir)), 4)

        with TiffFile(os.path.join(tiles_dir, os.listdir(tiles_dir)[0])) as tif:
            res = tif.pages[0].tags["XResolution"].value
            unit = tif.imagej_metadata["unit"]

        self.assertAlmostEqual(res[0]/res[1], 0.02)
        self.assertEqual(unit, "nm")

        self.assertEqual(len(Img.tiles), len(os.listdir(tiles_dir)))
        self.assertEqual(Img.tiles[list(Img.tiles.keys())[0]].shape, (128, 128))
        self.assertEqual(Img.tile_arrangement, (2,2))

        shutil.rmtree(tiles_dir)
    

    def test_reassemble_tiles(self):
        """
        Tests that tiles are reassembled correctly
        """
        Img = reader.Image("./data/blobs.tif", pixel_size=50, unit="nm")

        tiles_dir = "./data/tiles"

        tiles.create_patches(
            Img,
            tile_size=128,
            tiles_output=tiles_dir,
            pad=True
        )

        reassembled = tiles.reassemble_tiles(
            list(Img.tiles.values()),
            Img.tile_arrangement,
        )

        self.assertTrue(np.allclose(reassembled, Img.img_data))

        shutil.rmtree(tiles_dir)
