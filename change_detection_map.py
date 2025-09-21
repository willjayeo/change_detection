#! /usr/bin/env python
"""
Create a simple change detection map from two single band satellite images in a GDAL supported format
Author Will Jay (willjayeo). October 2022
"""

import argparse
import logging
import numpy
import rioxarray
import xarray

from matplotlib import pyplot


def setup_logger(verbose: bool = False, debug: bool = False):
    # Set logging level as defined from command line. Otherwise default to only log
    # warnings and errors
    if debug:
        logging.setLevel(logging.DEBUG)
    elif verbose:
        logging.setLevel(logging.INFO)
    else:
        logging.setLevel(logging.WARNING)


def normalise_arrays(
    img_a_array: xarray.DataArray, img_b_array: xarray.DataArray
) -> tuple:
    """
    Return arrays containing data normalised to the maximum range of the combined
    input arrays
    """

    # Get data value ranges
    min_a = img_a_array.min()
    max_a = img_a_array.max()
    min_b = img_b_array.min()
    max_b = img_b_array.max()

    # Get the lowest value of the combined arrays
    if max_a > max_b:
        range_max = max_a
    else:
        range_max = max_b

    # Get the maximum value of the combined arrays
    if min_a < min_b:
        range_min = min_a
    else:
        range_min = min_b

    # Calculate the total data range of the two arrays
    data_range = range_max - range_min

    # Normalise data
    img_a_array_normalised = (img_a_array - range_min) / data_range
    img_b_array_normalised = (img_b_array - range_min) / data_range

    return img_a_array_normalised, img_b_array_normalised


def make_rgb_stack(
    img_a_array_normalised: xarray.DataArray, img_b_array_normalised: xarray.DataArray
) -> xarray.DataArray:
    """
    Return a three band array with the shape of row, col, band containing an RGB
    composite of the two images
    """

    # TODO: Get a good contrast?

    # Stack arrays into RGB
    # TODO: Use differnt cases to control colour
    rgb_array = numpy.vstack(
        (img_a_array_normalised, img_a_array_normalised, img_b_array_normalised)
    )

    # TODO: Need to determine exactly what dimensions to drop for differnt datasets. Sentinel2 MSI data appears to have this extra dimension at index 1. Otherdatasets might have completely differnt arrayshapes
    if len(rgb_array) == 4:
        # Drop the spatial reference dimension (index 1)
        rgb_array = numpy.squeeze(rgb_array, axis=1)

    # Transpose dimensions so that it has the shape of (row, col, band)
    rgb_array = rgb_array.transpose((1, 2, 0))

    return rgb_array


def main(img_a_path: str, img_b_path: str, verbose=False, debug=False):
    """ """

    # Open data as xarray.DataArray objects
    img_a_array = rioxarray.open_rasterio(img_a_path)
    img_b_array = rioxarray.open_rasterio(img_b_path)

    # TODO: Resample to larger pixel array if inputs are differnt grids

    # TODO: CROP AREA OF INTEREST WITH COORDINATES

    # Normalise array values by the combined range of values
    img_a_array_normalised, img_b_array_normalised = normalise_arrays(img_a_array, img_b_array)

    # TODO: CONTRAST STRETCH THE IMAGES

    # Create a RGB stack
    rgb_array = make_rgb_stack(img_a_array_normalised, img_b_array_normalised)

    # Visualise RGB stack
    pyplot.imshow(rgb_array, interpolation="nearest")
    pyplot.show()


if __name__ == "__main__":
    helpstring = (
        "Make single change detection map from two single band satellite images"
    )
    parser = argparse.ArgumentParser(
        description=helpstring,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-a",
        "--img_a",
        type=str,
        default=None,
        required=True,
        help="Path to first input image",
    )
    parser.add_argument(
        "-b",
        "--img_b",
        default=None,
        required=True,
        help="Path to second input image",
    )

    cmdline = parser.parse_args()

    main(cmdline.img_a, cmdline.img_b)
