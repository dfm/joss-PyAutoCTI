import numpy as np
import autocti as ac


class TestExtractions:
    def test__parallel_serial_calibration_section__extracts_everything(self):

        layout = ac.ci.Layout2DCIUniform(normalization=1.0, region_list=[(0, 1, 0, 1)])

        arr = [
            [0.0, 1.0, 2.0, 3.0],
            [0.0, 1.0, 2.0, 3.0],
            [0.0, 1.0, 2.0, 3.0],
            [0.0, 1.0, 2.0, 3.0],
            [0.0, 1.0, 2.0, 3.0],
        ]

        array = ac.Array2D.manual(array=arr, layout_ci=layout, pixel_scales=1.0)

        assert (layout.parallel_serial_calibration_frame == arr).all()

        layout = ac.ci.Layout2DCIUniform(normalization=1.0, region_list=[(0, 1, 0, 1)])

        array = ac.Array2D.manual(array=arr, layout_ci=layout, pixel_scales=1.0)

        assert (layout.parallel_serial_calibration_frame == arr).all()

    def test__smallest_parallel_trails_rows_to_frame_edge__x2_ci_region__bottom_frame_geometry(
        self,
    ):

        layout = ac.ci.Layout2DCIUniform(
            normalization=10.0, region_list=[(0, 3, 0, 3), (5, 7, 0, 3)]
        )

        array = ac.Array2D.manual(
            array=np.ones((10, 5)), layout_ci=layout, pixel_scales=1.0
        )

        assert layout.smallest_parallel_trails_rows_to_frame_edge == 2

        array = ac.Array2D.manual(
            array=np.ones((8, 5)), layout_ci=layout, pixel_scales=1.0
        )

        assert layout.smallest_parallel_trails_rows_to_frame_edge == 1

    def test__serial_trails_columns__extract_two_columns__second_and_third__takes_coordinates_after_right_of_region(
        self, layout_ci_7x7
    ):

        array = ac.Array2D.manual(
            array=np.ones((10, 10)),
            layout_ci=layout_ci_7x7,
            scans=ac.Scans(
                serial_overscan=ac.Region2D((0, 1, 0, 10)),
                serial_prescan=ac.Region2D((0, 1, 0, 1)),
                parallel_overscan=ac.Region2D((0, 1, 0, 1)),
            ),
            pixel_scales=1.0,
        )

        assert layout.layout.serial_trails_columns == 10

        array = ac.Array2D.manual(
            array=np.ones((50, 50)),
            layout_ci=layout_ci_7x7,
            scans=ac.Scans(
                serial_overscan=ac.Region2D((0, 1, 0, 50)),
                serial_prescan=ac.Region2D((0, 1, 0, 1)),
                parallel_overscan=ac.Region2D((0, 1, 0, 1)),
            ),
            pixel_scales=1.0,
        )

        assert layout.layout.serial_trails_columns == 50

    def test__parallel_trail_size_to_frame_edge__parallel_trail_size_to_edge(self):

        layout = ac.ci.Layout2DCIUniform(
            normalization=1.0, region_list=[ac.Region2D(region=(0, 3, 0, 3))]
        )

        array = ac.Array2D.manual(
            array=np.ones((5, 100)), layout_ci=layout, pixel_scales=1.0
        )

        assert layout.parallel_trail_size_to_frame_edge == 2

        array = ac.Array2D.manual(
            array=np.ones((7, 100)), layout_ci=layout, pixel_scales=1.0
        )

        assert layout.parallel_trail_size_to_frame_edge == 4

        layout = ac.ci.Layout2DCIUniform(
            normalization=1.0,
            region_list=[
                ac.Region2D(region=(0, 2, 0, 3)),
                ac.Region2D(region=(5, 8, 0, 3)),
                ac.Region2D(region=(11, 14, 0, 3)),
            ],
        )

        array = ac.Array2D.manual(
            array=np.ones((15, 100)), layout_ci=layout, pixel_scales=1.0
        )

        assert layout.parallel_trail_size_to_frame_edge == 1

        array = ac.Array2D.manual(
            array=np.ones((20, 100)), layout_ci=layout, pixel_scales=1.0
        )

        assert layout.parallel_trail_size_to_frame_edge == 6


class TestCIFrameAPI:
    def test__manual__makes_array_using_inputs(self):

        layout = ac.ci.Layout2DCIUniform(normalization=10.0, region_list=[(0, 1, 0, 1)])

        array = ac.Array2D.manual(
            array=[[1.0, 2.0], [3.0, 4.0]],
            layout_ci=layout,
            scans=ac.Scans(
                parallel_overscan=(0, 1, 0, 1),
                serial_prescan=(1, 2, 1, 2),
                serial_overscan=(0, 2, 0, 2),
            ),
            pixel_scales=1.0,
        )

        assert (array == np.array([[1.0, 2.0], [3.0, 4.0]])).all()
        assert layout.layout_ci.region_list == [(0, 1, 0, 1)]
        assert layout.original_roe_corner == (1, 0)
        assert layout.layout.parallel_overscan == (0, 1, 0, 1)
        assert layout.layout.serial_prescan == (1, 2, 1, 2)
        assert layout.layout.serial_overscan == (0, 2, 0, 2)
        assert (layout.mask == np.array([[False, False], [False, False]])).all()
        assert layout.native.layout_ci.region_list == [(0, 1, 0, 1)]

        array = ac.Array2D.manual(
            array=[[1.0, 2.0], [3.0, 4.0]],
            layout_ci=layout,
            roe_corner=(0, 0),
            scans=ac.Scans(
                parallel_overscan=(0, 1, 0, 1),
                serial_prescan=(1, 2, 1, 2),
                serial_overscan=(0, 2, 0, 2),
            ),
            pixel_scales=1.0,
        )

        assert (array == np.array([[3.0, 4.0], [1.0, 2.0]])).all()
        assert layout.layout_ci.region_list == [(1, 2, 0, 1)]
        assert layout.original_roe_corner == (0, 0)
        assert layout.layout.parallel_overscan == (1, 2, 0, 1)
        assert layout.layout.serial_prescan == (0, 1, 1, 2)
        assert layout.layout.serial_overscan == (0, 2, 0, 2)
        assert (layout.mask == np.array([[False, False], [False, False]])).all()

        array = ac.Array2D.manual(
            array=[[1.0, 2.0], [3.0, 4.0]],
            layout_ci=layout,
            roe_corner=(1, 1),
            scans=ac.Scans(
                parallel_overscan=(0, 1, 0, 1),
                serial_prescan=(1, 2, 1, 2),
                serial_overscan=(0, 2, 0, 2),
            ),
            pixel_scales=1.0,
        )

        assert (array == np.array([[2.0, 1.0], [4.0, 3.0]])).all()
        assert layout.layout_ci.region_list == [(0, 1, 1, 2)]
        assert layout.original_roe_corner == (1, 1)
        assert layout.layout.parallel_overscan == (0, 1, 1, 2)
        assert layout.layout.serial_prescan == (1, 2, 0, 1)
        assert layout.layout.serial_overscan == (0, 2, 0, 2)
        assert (layout.mask == np.array([[False, False], [False, False]])).all()

        array = ac.Array2D.manual(
            array=[[1.0, 2.0], [3.0, 4.0]],
            layout_ci=layout,
            roe_corner=(0, 1),
            scans=ac.Scans(
                parallel_overscan=(0, 1, 0, 1),
                serial_prescan=(1, 2, 1, 2),
                serial_overscan=(0, 2, 0, 2),
            ),
            pixel_scales=1.0,
        )

        assert (array == np.array([[4.0, 3.0], [2.0, 1.0]])).all()
        assert layout.layout_ci.region_list == [(1, 2, 1, 2)]
        assert layout.original_roe_corner == (0, 1)
        assert layout.layout.parallel_overscan == (1, 2, 1, 2)
        assert layout.layout.serial_prescan == (0, 1, 0, 1)
        assert layout.layout.serial_overscan == (0, 2, 0, 2)
        assert (layout.mask == np.array([[False, False], [False, False]])).all()

    def test__full_ones_zeros__makes_frame_using_inputs(self):

        layout = ac.ci.Layout2DCIUniform(normalization=10.0, region_list=[(0, 3, 0, 3)])

        array = ac.Array2D.full(
            fill_value=8.0,
            shape_native=(2, 2),
            layout_ci=layout,
            scans=ac.Scans(
                parallel_overscan=(0, 1, 0, 1),
                serial_prescan=(1, 2, 1, 2),
                serial_overscan=(0, 2, 0, 2),
            ),
            pixel_scales=1.0,
        )

        assert (array == np.array([[8.0, 8.0], [8.0, 8.0]])).all()
        assert layout.layout_ci.region_list == [(0, 3, 0, 3)]
        assert layout.original_roe_corner == (1, 0)
        assert layout.layout.parallel_overscan == (0, 1, 0, 1)
        assert layout.layout.serial_prescan == (1, 2, 1, 2)
        assert layout.layout.serial_overscan == (0, 2, 0, 2)
        assert (layout.mask == np.array([[False, False], [False, False]])).all()

        array = ac.Array2D.ones(
            shape_native=(2, 2),
            layout_ci=layout,
            scans=ac.Scans(
                parallel_overscan=(0, 1, 0, 1),
                serial_prescan=(1, 2, 1, 2),
                serial_overscan=(0, 2, 0, 2),
            ),
            pixel_scales=1.0,
        )

        assert (array == np.array([[1.0, 1.0], [1.0, 1.0]])).all()
        assert layout.layout_ci.region_list == [(0, 3, 0, 3)]
        assert layout.original_roe_corner == (1, 0)
        assert layout.layout.parallel_overscan == (0, 1, 0, 1)
        assert layout.layout.serial_prescan == (1, 2, 1, 2)
        assert layout.layout.serial_overscan == (0, 2, 0, 2)
        assert (layout.mask == np.array([[False, False], [False, False]])).all()

        array = ac.Array2D.zeros(
            shape_native=(2, 2),
            layout_ci=layout,
            scans=ac.Scans(
                parallel_overscan=(0, 1, 0, 1),
                serial_prescan=(1, 2, 1, 2),
                serial_overscan=(0, 2, 0, 2),
            ),
            pixel_scales=1.0,
        )

        assert (array == np.array([[0.0, 0.0], [0.0, 0.0]])).all()
        assert layout.layout_ci.region_list == [(0, 3, 0, 3)]
        assert layout.original_roe_corner == (1, 0)
        assert layout.layout.parallel_overscan == (0, 1, 0, 1)
        assert layout.layout.serial_prescan == (1, 2, 1, 2)
        assert layout.layout.serial_overscan == (0, 2, 0, 2)
        assert (layout.mask == np.array([[False, False], [False, False]])).all()

    def test__extracted_array_from_array_and_extraction_region(self):

        array = ac.Array2D.manual(
            array=[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]],
            layout_ci=ac.ci.Layout2DCIUniform(
                region_list=[(0, 1, 0, 1), (1, 2, 1, 2)], normalization=10.0
            ),
            scans=ac.Scans(
                parallel_overscan=None,
                serial_prescan=(0, 2, 0, 2),
                serial_overscan=(1, 2, 1, 2),
            ),
            pixel_scales=1.0,
        )

        array = ac.Array2D.extracted_array_from_array_and_extraction_region(
            array=array, extraction_region=ac.Region2D(region=(1, 3, 1, 3))
        )

        assert (array == np.array([[5.0, 6.0], [8.0, 9.0]])).all()
        assert layout.layout_ci.region_list == [(0, 1, 0, 1)]
        assert layout.original_roe_corner == (1, 0)
        assert layout.layout.parallel_overscan == None
        assert layout.layout.serial_prescan == (0, 1, 0, 1)
        assert layout.layout.serial_overscan == (0, 1, 0, 1)
        assert (layout.mask == np.array([[False, False], [False, False]])).all()

    def test__manual_mask__makes_array_using_inputs(self):

        layout = ac.ci.Layout2DCIUniform(normalization=10.0, region_list=[(0, 1, 0, 1)])

        mask = ac.Mask2D.manual(mask=[[False, True], [False, False]], pixel_scales=1.0)

        array = ac.Array2D.manual_mask(
            array=[[1.0, 2.0], [3.0, 4.0]],
            mask=mask,
            layout_ci=layout,
            scans=ac.Scans(
                parallel_overscan=(0, 1, 0, 1),
                serial_prescan=(1, 2, 1, 2),
                serial_overscan=(0, 2, 0, 2),
            ),
        )

        assert (array == np.array([[1.0, 0.0], [3.0, 4.0]])).all()
        assert layout.layout_ci.region_list == [(0, 1, 0, 1)]
        assert layout.original_roe_corner == (1, 0)
        assert layout.layout.parallel_overscan == (0, 1, 0, 1)
        assert layout.layout.serial_prescan == (1, 2, 1, 2)
        assert layout.layout.serial_overscan == (0, 2, 0, 2)
        assert (layout.mask == np.array([[False, True], [False, False]])).all()

        array = ac.Array2D.manual_mask(
            array=[[1.0, 2.0], [3.0, 4.0]],
            mask=mask,
            layout_ci=layout,
            roe_corner=(0, 0),
            scans=ac.Scans(
                parallel_overscan=(0, 1, 0, 1),
                serial_prescan=(1, 2, 1, 2),
                serial_overscan=(0, 2, 0, 2),
            ),
        )

        assert (array == np.array([[3.0, 4.0], [1.0, 0.0]])).all()
        assert layout.layout_ci.region_list == [(1, 2, 0, 1)]
        assert layout.original_roe_corner == (0, 0)
        assert layout.layout.parallel_overscan == (1, 2, 0, 1)
        assert layout.layout.serial_prescan == (0, 1, 1, 2)
        assert layout.layout.serial_overscan == (0, 2, 0, 2)
        assert (layout.mask == np.array([[False, False], [False, True]])).all()

        array = ac.Array2D.manual_mask(
            array=[[1.0, 2.0], [3.0, 4.0]],
            mask=mask,
            layout_ci=layout,
            roe_corner=(1, 1),
            scans=ac.Scans(
                parallel_overscan=(0, 1, 0, 1),
                serial_prescan=(1, 2, 1, 2),
                serial_overscan=(0, 2, 0, 2),
            ),
        )

        assert (array == np.array([[0.0, 1.0], [4.0, 3.0]])).all()
        assert layout.layout_ci.region_list == [(0, 1, 1, 2)]
        assert layout.original_roe_corner == (1, 1)
        assert layout.layout.parallel_overscan == (0, 1, 1, 2)
        assert layout.layout.serial_prescan == (1, 2, 0, 1)
        assert layout.layout.serial_overscan == (0, 2, 0, 2)
        assert (layout.mask == np.array([[True, False], [False, False]])).all()

        array = ac.Array2D.manual_mask(
            array=[[1.0, 2.0], [3.0, 4.0]],
            mask=mask,
            layout_ci=layout,
            roe_corner=(0, 1),
            scans=ac.Scans(
                parallel_overscan=(0, 1, 0, 1),
                serial_prescan=(1, 2, 1, 2),
                serial_overscan=(0, 2, 0, 2),
            ),
        )

        assert (array == np.array([[4.0, 3.0], [0.0, 1.0]])).all()
        assert layout.layout_ci.region_list == [(1, 2, 1, 2)]
        assert layout.original_roe_corner == (0, 1)
        assert layout.layout.parallel_overscan == (1, 2, 1, 2)
        assert layout.layout.serial_prescan == (0, 1, 0, 1)
        assert layout.layout.serial_overscan == (0, 2, 0, 2)
        assert (layout.mask == np.array([[False, False], [True, False]])).all()

    def test__from_array__from_frame__makes_frame_using_inputs(self):

        layout = ac.ci.Layout2DCIUniform(normalization=10.0, region_list=[(0, 1, 0, 1)])

        mask = ac.Mask2D.manual(mask=[[False, True], [False, False]], pixel_scales=1.0)

        array = ac.Array2D.full(
            shape_native=(2, 2),
            fill_value=8.0,
            layout_ci=layout,
            scans=ac.Scans(
                parallel_overscan=(0, 1, 0, 1),
                serial_prescan=(1, 2, 1, 2),
                serial_overscan=(0, 2, 0, 2),
            ),
            pixel_scales=1.0,
        )

        array = ac.Array2D.from_array(array=array, mask=mask)

        assert (array == np.array([[8.0, 0.0], [8.0, 8.0]])).all()
        assert (layout.native == np.array([[8.0, 0.0], [8.0, 8.0]])).all()
        assert layout.layout_ci.region_list == [(0, 1, 0, 1)]
        assert layout.original_roe_corner == (1, 0)
        assert layout.layout.parallel_overscan == (0, 1, 0, 1)
        assert layout.layout.serial_prescan == (1, 2, 1, 2)
        assert layout.layout.serial_overscan == (0, 2, 0, 2)
        assert (layout.mask == np.array([[False, True], [False, False]])).all()

        array = ac.Array2D.full(
            shape_native=(2, 2),
            fill_value=8.0,
            layout_ci=layout,
            roe_corner=(0, 0),
            scans=ac.Scans(
                parallel_overscan=(0, 1, 0, 1),
                serial_prescan=(1, 2, 1, 2),
                serial_overscan=(0, 2, 0, 2),
            ),
            pixel_scales=1.0,
        )

        array = ac.Array2D.from_array(array=array, mask=mask)

        assert (array == np.array([[8.0, 0.0], [8.0, 8.0]])).all()
        assert layout.layout_ci.region_list == [(1, 2, 0, 1)]
        assert layout.original_roe_corner == (0, 0)
        assert layout.layout.parallel_overscan == (1, 2, 0, 1)
        assert layout.layout.serial_prescan == (0, 1, 1, 2)
        assert layout.layout.serial_overscan == (0, 2, 0, 2)
        assert (layout.mask == np.array([[False, True], [False, False]])).all()


class TestCIFrameEuclid:
    def test__euclid_array_for_four_quandrants__loads_data_and_dimensions(
        self, euclid_data
    ):

        layout = ac.ci.Layout2DCIUniform(normalization=10.0, region_list=[(0, 1, 0, 1)])

        euclid_array = ac.Array2DEuclid.top_left(array=euclid_data, layout_ci=layout)

        assert isinstance(euclid_array, ac.Array2D)
        assert euclid_layout.layout_ci.region_list == [(2085, 2086, 0, 1)]
        assert euclid_layout.original_roe_corner == (0, 0)
        assert euclid_layout.shape_native == (2086, 2128)
        assert (euclid_array == np.zeros((2086, 2128))).all()
        assert euclid_layout.layout.parallel_overscan == (2066, 2086, 51, 2099)
        assert euclid_layout.layout.serial_prescan == (0, 2086, 0, 51)
        assert euclid_layout.layout.serial_overscan == (20, 2086, 2099, 2128)

        euclid_array = ac.Array2DEuclid.top_right(array=euclid_data, layout_ci=layout)

        assert isinstance(euclid_array, ac.Array2D)
        assert euclid_layout.layout_ci.region_list == [(2085, 2086, 2127, 2128)]
        assert euclid_layout.original_roe_corner == (0, 1)
        assert euclid_layout.shape_native == (2086, 2128)
        assert (euclid_array == np.zeros((2086, 2128))).all()
        assert euclid_layout.layout.parallel_overscan == (2066, 2086, 51, 2099)
        assert euclid_layout.layout.serial_prescan == (0, 2086, 0, 51)
        assert euclid_layout.layout.serial_overscan == (20, 2086, 2099, 2128)

        euclid_array = ac.Array2DEuclid.bottom_left(array=euclid_data, layout_ci=layout)

        assert isinstance(euclid_array, ac.Array2D)
        assert euclid_layout.layout_ci.region_list == [(0, 1, 0, 1)]
        assert euclid_layout.original_roe_corner == (1, 0)
        assert euclid_layout.shape_native == (2086, 2128)
        assert (euclid_array == np.zeros((2086, 2128))).all()
        assert euclid_layout.layout.parallel_overscan == (2066, 2086, 51, 2099)
        assert euclid_layout.layout.serial_prescan == (0, 2086, 0, 51)
        assert euclid_layout.layout.serial_overscan == (0, 2066, 2099, 2128)

        euclid_array = ac.Array2DEuclid.bottom_right(
            array=euclid_data, layout_ci=layout
        )

        assert isinstance(euclid_array, ac.Array2D)
        assert euclid_layout.layout_ci.region_list == [(0, 1, 2127, 2128)]
        assert euclid_layout.original_roe_corner == (1, 1)
        assert euclid_layout.shape_native == (2086, 2128)
        assert (euclid_array == np.zeros((2086, 2128))).all()
        assert euclid_layout.layout.parallel_overscan == (2066, 2086, 51, 2099)
        assert euclid_layout.layout.serial_prescan == (0, 2086, 0, 51)
        assert euclid_layout.layout.serial_overscan == (0, 2066, 2099, 2128)

    def test__left_side__chooses_correct_frame_given_input(self, euclid_data):

        layout = ac.ci.Layout2DCIUniform(normalization=10.0, region_list=[(0, 1, 0, 1)])

        euclid_array = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text1", quadrant_id="E", layout_ci=layout
        )

        assert euclid_layout.layout_ci.region_list == [(0, 1, 0, 1)]
        assert euclid_layout.original_roe_corner == (1, 0)

        euclid_array = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text2", quadrant_id="E", layout_ci=layout
        )

        assert euclid_layout.layout_ci.region_list == [(0, 1, 0, 1)]
        assert euclid_layout.original_roe_corner == (1, 0)

        euclid_array = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text3", quadrant_id="E", layout_ci=layout
        )

        assert euclid_layout.layout_ci.region_list == [(0, 1, 0, 1)]
        assert euclid_layout.original_roe_corner == (1, 0)

        euclid_array = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text1", quadrant_id="F", layout_ci=layout
        )

        assert euclid_layout.layout_ci.region_list == [(0, 1, 2127, 2128)]
        assert euclid_layout.original_roe_corner == (1, 1)

        euclid_array = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text2", quadrant_id="F", layout_ci=layout
        )

        assert euclid_layout.layout_ci.region_list == [(0, 1, 2127, 2128)]
        assert euclid_layout.original_roe_corner == (1, 1)

        euclid_array = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text3", quadrant_id="F", layout_ci=layout
        )

        assert euclid_layout.layout_ci.region_list == [(0, 1, 2127, 2128)]
        assert euclid_layout.original_roe_corner == (1, 1)

        euclid_array = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text1", quadrant_id="G", layout_ci=layout
        )

        assert euclid_layout.layout_ci.region_list == [(2085, 2086, 2127, 2128)]
        assert euclid_layout.original_roe_corner == (0, 1)

        euclid_array = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text2", quadrant_id="G", layout_ci=layout
        )

        assert euclid_layout.layout_ci.region_list == [(2085, 2086, 2127, 2128)]
        assert euclid_layout.original_roe_corner == (0, 1)

        euclid_array = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text3", quadrant_id="G", layout_ci=layout
        )

        assert euclid_layout.layout_ci.region_list == [(2085, 2086, 2127, 2128)]
        assert euclid_layout.original_roe_corner == (0, 1)

        euclid_array = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text1", quadrant_id="H", layout_ci=layout
        )

        assert euclid_layout.layout_ci.region_list == [(2085, 2086, 0, 1)]
        assert euclid_layout.original_roe_corner == (0, 0)

        euclid_array = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text2", quadrant_id="H", layout_ci=layout
        )

        assert euclid_layout.layout_ci.region_list == [(2085, 2086, 0, 1)]
        assert euclid_layout.original_roe_corner == (0, 0)

        euclid_array = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text3", quadrant_id="H", layout_ci=layout
        )

        assert euclid_layout.layout_ci.region_list == [(2085, 2086, 0, 1)]
        assert euclid_layout.original_roe_corner == (0, 0)

    def test__right_side__chooses_correct_frame_given_input(self, euclid_data):

        layout = ac.ci.Layout2DCIUniform(normalization=10.0, region_list=[(0, 1, 0, 1)])

        frame = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text4", quadrant_id="E", layout_ci=layout
        )

        assert frame.original_roe_corner == (0, 1)

        frame = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text5", quadrant_id="E", layout_ci=layout
        )

        assert frame.original_roe_corner == (0, 1)

        frame = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text6", quadrant_id="E", layout_ci=layout
        )

        assert frame.original_roe_corner == (0, 1)

        frame = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text4", quadrant_id="F", layout_ci=layout
        )

        assert frame.original_roe_corner == (0, 0)

        frame = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text5", quadrant_id="F", layout_ci=layout
        )

        assert frame.original_roe_corner == (0, 0)

        frame = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text6", quadrant_id="F", layout_ci=layout
        )

        assert frame.original_roe_corner == (0, 0)

        frame = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text4", quadrant_id="G", layout_ci=layout
        )

        assert frame.original_roe_corner == (1, 0)

        frame = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text5", quadrant_id="G", layout_ci=layout
        )

        assert frame.original_roe_corner == (1, 0)

        frame = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text6", quadrant_id="G", layout_ci=layout
        )

        assert frame.original_roe_corner == (1, 0)

        frame = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text4", quadrant_id="H", layout_ci=layout
        )

        assert frame.original_roe_corner == (1, 1)

        frame = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text5", quadrant_id="H", layout_ci=layout
        )

        assert frame.original_roe_corner == (1, 1)

        frame = ac.Array2DEuclid.from_ccd_and_quadrant_id(
            array=euclid_data, ccd_id="text6", quadrant_id="H", layout_ci=layout
        )

        assert frame.original_roe_corner == (1, 1)
