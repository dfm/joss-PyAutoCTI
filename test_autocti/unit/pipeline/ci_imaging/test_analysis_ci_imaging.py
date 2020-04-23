from os import path

import pytest
from astropy import cosmology as cosmo
import numpy as np

import autofit as af
import arctic as ac
import autocti.charge_injection as ci
from autocti.util import exc
from test_autocti.mock import mock_pipeline

from autocti.pipeline.phase.ci_imaging import PhaseCIImaging

pytestmark = pytest.mark.filterwarnings(
    "ignore:Using a non-tuple sequence for multidimensional indexing is deprecated; use `arr[tuple(seq)]` instead of "
    "`arr[seq]`. In the future this will be interpreted as an arrays index, `arr[np.arrays(seq)]`, which will result "
    "either in an error or a different result."
)

directory = path.dirname(path.realpath(__file__))


class TestChecks:
    def test__parallel_and_serial_checks_raise_exception(
        self, phase_ci_imaging_7x7, ci_imaging_7x7
    ):

        phase_ci_imaging_7x7.meta_dataset.parallel_total_density_range = (1.0, 2.0)

        analysis = phase_ci_imaging_7x7.make_analysis(
            datasets=[ci_imaging_7x7], clocker=None
        )

        instance = af.ModelInstance()
        instance.parallel_traps = [ac.Trap(density=0.75), ac.Trap(density=0.75)]

        analysis.check_total_density_within_range(instance=instance)

        instance = af.ModelInstance()
        instance.parallel_traps = [ac.Trap(density=1.1), ac.Trap(density=1.1)]

        with pytest.raises(exc.PriorException):
            analysis.check_total_density_within_range(instance=instance)

        phase_ci_imaging_7x7.meta_dataset.parallel_total_density_range = None
        phase_ci_imaging_7x7.meta_dataset.serial_total_density_range = (1.0, 2.0)

        analysis = phase_ci_imaging_7x7.make_analysis(
            datasets=[ci_imaging_7x7], clocker=None
        )

        instance = af.ModelInstance()
        instance.serial_traps = [ac.Trap(density=0.75), ac.Trap(density=0.75)]

        analysis.check_total_density_within_range(instance=instance)

        instance = af.ModelInstance()
        instance.serial_traps = [ac.Trap(density=1.1), ac.Trap(density=1.1)]

        with pytest.raises(exc.PriorException):
            analysis.check_total_density_within_range(instance=instance)


class TestFit:
    def test__fit_figure_of_merit__log_likelihood_matches_via_manual_fit(
        self, ci_imaging_7x7, ci_pre_cti_7x7, traps_x1, ccd_volume, parallel_clocker
    ):

        phase = PhaseCIImaging(
            parallel_traps=traps_x1,
            parallel_ccd_volume=ccd_volume,
            non_linear_class=mock_pipeline.MockNLO,
            phase_name="test_phase",
        )

        analysis = phase.make_analysis(
            datasets=[ci_imaging_7x7], clocker=parallel_clocker
        )
        instance = phase.model.instance_from_unit_vector([])

        log_likelihood_via_analysis = analysis.fit(instance=instance)

        ci_post_cti = parallel_clocker.add_cti(
            image=ci_pre_cti_7x7,
            parallel_traps=traps_x1,
            parallel_ccd_volume=ccd_volume,
        )

        fit = ci.CIFitImaging(
            masked_ci_imaging=analysis.masked_ci_imagings[0], ci_post_cti=ci_post_cti
        )

        assert fit.log_likelihood == log_likelihood_via_analysis

    def test__hyper_noise_scalar_properties_of_phase(
        self, ci_imaging_7x7, ci_pattern_7x7, parallel_clocker
    ):

        noise_scaling_maps_list_of_ci_regions = [
            ci.CIFrame.ones(
                shape_2d=(7, 7), pixel_scales=1.0, ci_pattern=ci_pattern_7x7
            )
        ]
        noise_scaling_maps_list_of_parallel_trails = [
            ci.CIFrame.full(
                fill_value=2.0,
                shape_2d=(7, 7),
                pixel_scales=1.0,
                ci_pattern=ci_pattern_7x7,
            )
        ]

        phase = PhaseCIImaging(
            phase_name="test_phase",
            hyper_noise_scalar_of_ci_regions=ci.CIHyperNoiseScalar,
            hyper_noise_scalar_of_parallel_trails=ci.CIHyperNoiseScalar,
        )

        analysis = phase.make_analysis(
            datasets=[ci_imaging_7x7],
            clocker=parallel_clocker,
            results=mock_pipeline.MockResults(
                noise_scaling_maps_list_of_ci_regions=noise_scaling_maps_list_of_ci_regions,
                noise_scaling_maps_list_of_parallel_trails=noise_scaling_maps_list_of_parallel_trails,
            ),
        )

        instance = phase.model.instance_from_prior_medians()

        hyper_noise_scalars = analysis.hyper_noise_scalars_from_instance(
            instance=instance
        )

        assert len(hyper_noise_scalars) == 2
        assert len(phase.model.priors) == 2

        assert instance.hyper_noise_scalar_of_ci_regions == 0.5
        assert instance.hyper_noise_scalar_of_parallel_trails == 0.5
