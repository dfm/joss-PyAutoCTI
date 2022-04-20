import numpy as np

import autocti as ac


def test__array_2d_list_from(parallel_array, parallel_masked_array):
    extract = ac.Extract2DParallelFPR(region_list=[(1, 4, 0, 3)])

    fpr_list = extract.array_2d_list_from(array=parallel_array, pixels=(0, 1))
    assert (fpr_list[0] == np.array([[1.0, 1.0, 1.0]])).all()

    fpr_list = extract.array_2d_list_from(array=parallel_array, pixels=(2, 3))
    assert (fpr_list[0] == np.array([[3.0, 3.0, 3.0]])).all()

    extract = ac.Extract2DParallelFPR(region_list=[(1, 4, 0, 3), (5, 8, 0, 3)])

    fpr_list = extract.array_2d_list_from(array=parallel_array, pixels=(0, 1))
    assert (fpr_list[0] == np.array([[1.0, 1.0, 1.0]])).all()
    assert (fpr_list[1] == np.array([[5.0, 5.0, 5.0]])).all()

    fpr_list = extract.array_2d_list_from(array=parallel_array, pixels=(2, 3))
    assert (fpr_list[0] == np.array([[3.0, 3.0, 3.0]])).all()
    assert (fpr_list[1] == np.array([[7.0, 7.0, 7.0]])).all()

    fpr_list = extract.array_2d_list_from(array=parallel_array, pixels=(0, 3))
    assert (
        fpr_list[0] == np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 2.0], [3.0, 3.0, 3.0]])
    ).all()
    assert (
        fpr_list[1] == np.array([[5.0, 5.0, 5.0], [6.0, 6.0, 6.0], [7.0, 7.0, 7.0]])
    ).all()

    fpr_list = extract.array_2d_list_from(array=parallel_masked_array, pixels=(0, 3))

    assert (
        fpr_list[0].mask
        == np.array([[False, False, False], [False, True, False], [False, False, True]])
    ).all()

    assert (
        fpr_list[1].mask
        == np.array(
            [[False, False, False], [False, False, False], [True, False, False]]
        )
    ).all()


def test__stacked_array_2d_from(parallel_array, parallel_masked_array):
    extract = ac.Extract2DParallelFPR(region_list=[(1, 4, 0, 3), (5, 8, 0, 3)])

    stacked_fpr_list = extract.stacked_array_2d_from(
        array=parallel_array, pixels=(0, 3)
    )

    assert (
        stacked_fpr_list
        == np.array([[3.0, 3.0, 3.0], [4.0, 4.0, 4.0], [5.0, 5.0, 5.0]])
    ).all()

    extract = ac.Extract2DParallelFPR(region_list=[(1, 3, 0, 3), (5, 8, 0, 3)])

    stacked_fpr_list = extract.stacked_array_2d_from(
        array=parallel_array, pixels=(0, 2)
    )

    assert (stacked_fpr_list == np.array([[3.0, 3.0, 3.0], [4.0, 4.0, 4.0]])).all()

    stacked_fpr_list = extract.stacked_array_2d_from(
        array=parallel_masked_array, pixels=(0, 3)
    )

    assert (
        stacked_fpr_list
        == np.ma.array([[3.0, 3.0, 3.0], [4.0, 6.0, 4.0], [3.0, 5.0, 7.0]])
    ).all()
    assert (
        stacked_fpr_list.mask
        == np.ma.array(
            [[False, False, False], [False, False, False], [False, False, False]]
        )
    ).all()


def test__binned_array_1d_from(parallel_array, parallel_masked_array):
    extract = ac.Extract2DParallelFPR(region_list=[(1, 3, 0, 3), (5, 8, 0, 3)])

    fpr_line = extract.binned_array_1d_from(array=parallel_array, pixels=(0, 3))

    assert (fpr_line == np.array([3.0, 4.0, 5.0])).all()

    extract = ac.Extract2DParallelFPR(region_list=[(1, 3, 0, 3), (5, 8, 0, 3)])

    fpr_line = extract.binned_array_1d_from(array=parallel_array, pixels=(0, 2))

    assert (fpr_line == np.array([3.0, 4.0])).all()

    fpr_line = extract.binned_array_1d_from(array=parallel_masked_array, pixels=(0, 3))

    assert (fpr_line == np.array([9.0 / 3.0, 14.0 / 3.0, 5.0])).all()
