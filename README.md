# quoll
Image quality assessment for electron tomography

# Installation

1. Clone the repository. In a terminal:

```
git clone https://github.com/rosalindfranklininstitute/quoll.git
```

2. Navigate to the Quoll directory and create a new conda environment for Quoll. This installs all the pre-requisite libraries to use Quoll. Don't forget to activate this environment

```
conda env create -n quoll -f quoll_env.yaml
conda activate quoll
```

3. Pip install the quoll package

```
pip install -e .
```


# Examples

The [examples](https://github.com/rosalindfranklininstitute/quoll/tree/main/examples) folder contains Jupyter notebooks for example usage.

Alternatively the [tests](https://github.com/rosalindfranklininstitute/quoll/tree/main/tests) also go through some ways of using quoll.

# CLI Usage examples

To use the one-image FRC in the command line, once Quoll is installed.

```
oneimgFRC -h
```
brings up the help options for the one image FRC

To run the one image FRC on a single image without tiling (i.e., estimate resolution of the entire image),
```
oneimgFRC <image_filename> <pixel_size>
```

To run the one image FRC on a single image split into square tiles of length `n` pixels,
```
oneimgFRC <image_filename> <pixel_size> --tile_size <n, e.g., 128> --tiles_dir <tiles_dir>
```

The resolution results, resolution heatmap, and the overlay of the resolution heatmap on the image can be saved with the flags `--save_csv`, `--save_overlay`, `--save_heatmap`. 

The resolution heatmap overlaid on the original image can be displayed with the `--show_plot` flag.
