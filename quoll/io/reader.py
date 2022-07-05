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

import mrcfile
import os
import skimage
import tifffile
import matplotlib.pyplot as plt

from quoll.io.mdoc_parser import Mdoc

from typing import Optional

class Image:
    """
    Class for a generic image
    """

    def __init__(
        self,
        filename: str,
        pixel_size: Optional[float] = None,
        unit: Optional[str] = None,
    ):
        """
        Initialises an image object

        Args:
            filename (str): Path to the image
            pixel_size (Optional[float], optional): Size of pixel in physical units. Defaults to None.
            unit (Optional[str], optional): Unit of pixel size. Defaults to None.
        """

        self.filename = filename
        self.pixel_size = pixel_size
        self.unit = unit
        self.get_image()

        # extra attributes for holding tiles
        self.tiles = {}
    

    def get_image(self):
        """
        Import an image
        """
        if os.path.splitext(self.filename)[1] != ".mrc":
            self.img_data = tifffile.imread(self.filename)

        elif os.path.splitext(self.filename)[1] == ".mrc":
            with mrcfile.open(self.filename) as mrc:
                self.img_data = mrc.data
        
        else:
            raise IOError("Image cannot be imported. Quoll uses skimage and mrcfile")
        
        self.img_dims = self.img_data.shape
        self.img_bitdepth = self.img_data.dtype

    def show(
        self,
        slice: Optional[int] = 0,
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
    ):
        """
        Displays images

        Args:
            slice (Optional[int], optional): Slice of 3D image to display. Defaults to 0.
            vmin (Optional[float], optional): vmin of display range. Defaults to None.
            vmax (Optional[float], optional): vmax of display range. Defaults to None.
        """
        plt.figure()
        if len(self.img_data.shape) == 2:
            plt.imshow(self.img_data, cmap="Greys", vmin=vmin, vmax=vmax)
        else:
            plt.imshow(self.img_data[slice, :, :], cmap="Greys", vmin=vmin, vmax=vmax)
        plt.show()


class TiltSeries(Image):
    def __init__(
        self,
        filename: str,
        pixel_size: Optional[float] = None,
        unit: Optional[str] = None,
        mdoc_file: Optional[str] = None,
        tilt_angle_file: Optional[str] = None,
    ):
        super().__init__(filename, pixel_size, unit)
        self.img_type = "TiltSeries"
        self.mdoc_file = mdoc_file
        self.tilt_angle_file = tilt_angle_file
        self.get_tilt_angles()
    
    def get_tilt_angles(self):
        if self.mdoc_file is not None:
            self.mdoc = Mdoc(self.mdoc_file)
            self.mdoc.get_tilt_angles()
            self.tilt_angles = self.mdoc.tilt_angles
        
        elif self.tilt_angle_file is not None:
            with open(self.tilt_angle_file, "r") as f:
                tas = f.readlines()
            self.tilt_angles = [float(ta) for ta in tas]
        
        else:
            raise ValueError("Tilt angles have to be specified")