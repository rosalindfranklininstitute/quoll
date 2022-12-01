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

import math
import os

import numpy as np
import tifffile


def extract_tiles(Image, tile_size_x, tile_size_y, pad=True):
    """Split image `img` into square tiles of equal size `tile_size`

    The image is zero-padded to ensure that the entire image is sampled.

    Parameters
    ----------
    img : np array
        Numpy array containing the image
    tile_size_x : int
        Width of tile in px
    tile_size_y : int
        Height of tile in px
    pad : bool
        If true, apply zero padding to ensure the whole image is covered

    Returns
    -------
    list
        List containing numpy arrays of shape `(tile_size, tile_size)`
        taken from the image.
    """

    img = Image.img_data

    # How many tiles will we use
    nTilesX = math.ceil(img.shape[1] / tile_size_x)
    nTilesY = math.ceil(img.shape[0] / tile_size_y)

    if pad is True:
         # Calculate padded size and create empty image
        paddedX = math.ceil(nTilesX * tile_size_x)
        paddedY = math.ceil(nTilesY * tile_size_y)
        padded_img = np.zeros(shape=(paddedY, paddedX))

        # Place image in the centre of the padded image
        ybounds = [int((paddedX/2) - (img.shape[1]/2)), int((paddedX/2) + (img.shape[1]/2))]
        xbounds = [int((paddedY/2) - (img.shape[0]/2)), int((paddedY/2) + (img.shape[0]/2))]
        padded_img[xbounds[0]:xbounds[1], ybounds[0]:ybounds[1]] = img

        img_to_tile = padded_img

    else:
        # No zero padding but the tiles might not cover the whole image
        img_to_tile = img

    # Split into tiles
    tiles = []
    for i in range(nTilesX):
        for j in range(nTilesY):
            tile_xbounds = [j*tile_size_y, (j*tile_size_y) + tile_size_y]
            tile_ybounds = [i*tile_size_x, (i*tile_size_x) + tile_size_x]
            tile = img_to_tile[tile_xbounds[0]:tile_xbounds[1], tile_ybounds[0]:tile_ybounds[1]]
            tiles.append(tile)
    return tiles, (nTilesX, nTilesY)


def create_patches(Image, tile_size, tiles_output=None, pad=True):
    """Split an image into square patches. All patches will be square if pad=True.
    Otherwise, patches at the edges do not fit neatly into the square patches will
    be returned (these are not square). Patches are saved as .tif's in tiles_output.

    Args:
        img (str, path-like OR array): Path to image or array containing image
        tilesize (int): Length of one side of the square patch, in pixel units
        tiles_output (str, path-like): Path to directory containing tiles/patches
        px_size (int): Pixel size in physical units
        pad (bool, optional): Zero-pad image so square patches fit neatly. Defaults to True.
        unit (str, optional): Physical unit of pixel size. Defaults to "nm".
    """

    tiles, (nTilesX, nTilesY) = extract_tiles(Image, tile_size, tile_size, pad)
    resolution = (1/Image.pixel_size, 1/Image.pixel_size)

    if tiles_output is not None:
        if os.path.isdir(tiles_output) is False:
            os.mkdir(tiles_output)
        if len(os.listdir(tiles_output)) != 0:
            for f in list(os.listdir(tiles_output)):
                try:
                    os.remove(os.path.join(tiles_output, f))
                except:
                    print(f"Could not remove {f}")
        for i, tile in enumerate(tiles):
            tile_fn = os.path.join(tiles_output, f"{i:03}.tif")
            tifffile.imwrite(
                tile_fn,
                tile.astype('uint8'),
                imagej=True,
                resolution=resolution,
                metadata={'unit': Image.unit}
            )

            Image.tiles[i] = tile.astype('uint8')

    else:
        for i, tile in enumerate(tiles):
            Image.tiles[i] = tile.astype('uint8')
    
    Image.tile_arrangement = (nTilesX, nTilesY)


def reassemble_tiles(
    tiles: list,
    nTiles: tuple
):
    nTilesX, nTilesY = nTiles
    tile_size_x = tiles[0].shape[1]
    tile_size_y = tiles[0].shape[0]
    img = np.zeros(shape=(nTilesY * tile_size_y, nTilesX * tile_size_x))
    counter = 0
    for i in range(nTilesX):
        for j in range(nTilesY):
            tile_xbounds = [j*tile_size_y, (j*tile_size_y) + tile_size_y]
            tile_ybounds = [i*tile_size_x, (i*tile_size_x) + tile_size_x]
            img[tile_xbounds[0]:tile_xbounds[1], tile_ybounds[0]:tile_ybounds[1]] = tiles[counter]
            counter += 1
    return img
