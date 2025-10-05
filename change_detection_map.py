#!/usr/bin/env python3
"""
Create a simple change detection map from two single band satellite images in a
supported format

Author William Jay (willjayeo). October 2022
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


def get_rgb_map_from_string(rgb_map_str: str) -> tuple:
    """
    Returns a tuple containing the input RGB order string.

    Examples:
        'abb' returns ('a', 'b', 'b')
        'ab0' returns ('a', 'b', None)

    ValueError is raised if the input string does not not comprise three characters
    or any of the characters are not either 'a', 'b' or '0'
    """

    if len(rgb_map_str) != 3:
        raise ValueError(
            f"--rgb must be exactly 3 characters long: input '{rgb_map_str}' is invalid"
        )

    # Create list to populate output with
    result = []

    # Iterate through each colour
    for colour in rgb_map_str:

        # If colour is 'a' or 'b' then add them to the output list. If the colour is
        # '0', then add None
        match colour:

            case "a":
                result.append("a")

            case "b":
                result.append("b")

            case "0":
                result.append(None)

            case _:
                raise ValueError(f"Invalid character in --rgb: '{colour}'")

    return tuple(result)


def resample_arrays(array_a: xarray.DataArray, array_b: xarray.DataArray) -> tuple:
    """
    Resample the array with the finer resolution to the grid of the array with the
    coarser resolution
    """

    # If array a is larger, reproject array a to the dimensions of array b
    if sum(array_a.shape) > sum(array_b.shape):
        array_a = array_a.rio.reproject_match(array_b)

    # If array a is larger, reproject array b to the dimensions of array a
    else:
        array_b = array_b.rio.reproject_match(array_a)

    return array_a, array_b


def normalise_arrays(array_a: xarray.DataArray, array_b: xarray.DataArray) -> tuple:
    """
    Return arrays containing data normalised to the maximum range of the combined
    input arrays
    """

    # Get data value ranges
    min_a = array_a.min()
    max_a = array_a.max()
    min_b = array_b.min()
    max_b = array_b.max()

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
    array_a_normalised = (array_a - range_min) / data_range
    array_b_normalised = (array_b - range_min) / data_range

    return array_a_normalised, array_b_normalised


def make_rgb_stack(
    array_a: xarray.DataArray,
    array_b: xarray.DataArray,
    rgb_map=tuple,
) -> xarray.DataArray:
    """
    Return a three band array with the shape of row, col, band containing an RGB
    composite of the two images

    Input arrays must have identical dimensions
    """

    channels = sort_arrays_into_rgb_order(array_a, array_b, rgb_map)

    # Stack arrays into RGB
    rgb_array = numpy.vstack(channels)

    # TODO: Need to determine exactly what dimensions to drop for different datasets.
    # Sentinel2 MSI data appears to have this extra dimension at index 1. Other
    # datasets might have completely different array shapes
    if len(rgb_array) == 4:
        # Drop the spatial reference dimension (index 1)
        rgb_array = numpy.squeeze(rgb_array, axis=1)

    # Transpose dimensions so that it has the shape of (row, col, band)
    rgb_array = rgb_array.transpose((1, 2, 0))

    return rgb_array


def sort_arrays_into_rgb_order(
    array_a: xarray.DataArray, array_b: xarray.DataArray, rgb_order: tuple
) -> list:
    """
    Return a list of arrays in the defined RGB order.

    The rgb_order variable is expected to be a tuple containing three items. Each of
    these items is expected to be either 'a', 'b' or None. The output tuple from the
    function get_rgb_map_from_string produces this sort of tuple

    Examples:
        rgb_order of ('a', 'a', 'b') would sort arrays into a channel order of:
            R: array_a, G: array_a, B: array_a
        rgb_order of ('a', 'b', 'None') would sort arrays into a channel order of:
            R: array_a, G: array_b, B: blank array
    """

    # Make dictionary of arrays with 'a' or 'b' as they keys
    arrays = {"a": array_a, "b": array_b}

    # Iterate through the RGB order tuple and populate a list of arrays in the RGB order
    channel_list = []
    for key in rgb_order:

        if key is None:
            channel_list.append(numpy.zeros_like(array_a))

        else:
            channel_list.append(arrays[key])

    return channel_list


def main(
    img_a_path: str, img_b_path: str, rgb_map_str: str, verbose=False, debug=False
):
    """
    Steps:
        * Read data as arrays
        * Resample data if they have different grids
        * Normalise values
        * Visualise
    """

    # Open data as xarray.DataArray objects
    img_a_array = rioxarray.open_rasterio(img_a_path)
    img_b_array = rioxarray.open_rasterio(img_b_path)

    # Get band order from the user input, we do this early so invalid options can be
    # detected
    rgb_map = get_rgb_map_from_string(rgb_map_str)

    # Identify whether the data have different grids as we will need to resample the
    # higher (finer) resolution grid to matchs the lower (coarser) resolution grid
    if img_a_array.shape != img_b_array.shape:

        img_a_array, img_b_array = resample_arrays(img_a_array, img_b_array)

    # Normalise array values by the combined range of values
    img_a_array_normalised, img_b_array_normalised = normalise_arrays(
        img_a_array, img_b_array
    )

    # Create a RGB stack
    rgb_array = make_rgb_stack(img_a_array_normalised, img_b_array_normalised, rgb_map)

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
        "--image_a",
        type=str,
        default=None,
        required=True,
        help="Path to first input image",
    )
    parser.add_argument(
        "-b",
        "--image_b",
        default=None,
        required=True,
        help="Path to second input image",
    )

    parser.add_argument(
        "--rgb",
        default="aab",
        help=(
            "RGB mapping as three characters (either 'a', 'b' or '0').\nE.g. 'aab' "
            "results in R = --image_a, G = --image_a and B = --image_b or 'a0b' "
            "results in R = --image_a, G = empty and B = --image_b"
        ),
    )

    cmdline = parser.parse_args()

    main(cmdline.image_a, cmdline.image_b, cmdline.rgb)
