import pytest
from astropy import cosmology as cosmo

import autofit as af
from autocti.pipeline.phase import phase_extensions
from autocti.charge_injection import ci_hyper


@pytest.fixture(name="lens_galaxy")
def make_lens_galaxy():
    return g.Galaxy(
        redshift=1.0, light=lp.SphericalSersic(), mass=mp.SphericalIsothermal()
    )


@pytest.fixture(name="source_galaxy")
def make_source_galaxy():
    return g.Galaxy(redshift=2.0, light=lp.SphericalSersic())


@pytest.fixture(name="all_galaxies")
def make_all_galaxies(lens_galaxy, source_galaxy):
    galaxies = af.ModelInstance()
    galaxies.lens = lens_galaxy
    galaxies.source = source_galaxy
    return galaxies


@pytest.fixture(name="instance")
def make_instance(all_galaxies):
    instance = af.ModelInstance()
    instance.galaxies = all_galaxies
    return instance


@pytest.fixture(name="result")
def make_result(lens_data_7x7, instance):
    return phase_imaging.PhaseImaging.Result(
        constant=instance,
        figure_of_merit=1.0,
        previous_variable=af.ModelMapper(),
        gaussian_tuples=None,
        analysis=phase_imaging.PhaseImaging.Analysis(
            lens_data=lens_data_7x7,
            cosmology=cosmo.Planck15,
            positions_threshold=1.0,
            image_path="",
        ),
        optimizer=None,
    )


class MostLikelyFit(object):
    def __init__(self, model_image_2d):
        self.model_image_2d = model_image_2d


class MockResult(object):
    def __init__(self, most_likely_fit=None):
        self.most_likely_fit = most_likely_fit
        self.analysis = MockAnalysis()
        self.variable = af.ModelMapper()
        self.cti_settings = None


class MockAnalysis(object):
    pass


# noinspection PyAbstractClass
class MockOptimizer(af.NonLinearOptimizer):
    def __init__(
        self,
        phase_name="mock_optimizer",
        phase_tag="tag",
        phase_folders=tuple(),
        model_mapper=None,
    ):
        super().__init__(
            phase_folders=phase_folders,
            phase_tag=phase_tag,
            phase_name=phase_name,
            model_mapper=model_mapper,
        )

    def fit(self, analysis):
        # noinspection PyTypeChecker
        return af.Result(None, analysis.fit(None), None)


class MockPhase(object):
    def __init__(self):
        self.phase_name = "phase name"
        self.phase_path = "phase_path"
        self.optimizer = MockOptimizer()
        self.phase_folders = [""]
        self.phase_tag = ""

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def run(self, *args, **kwargs):
        return MockResult()


@pytest.fixture(name="hyper_combined")
def make_combined():
    normal_phase = MockPhase()

    # noinspection PyUnusedLocal
    def run_hyper(*args, **kwargs):
        return MockResult()

    # noinspection PyTypeChecker
    hyper_combined = phase_extensions.CombinedHyperPhase(
        normal_phase, hyper_phase_classes=(phase_extensions.HyperNoisePhase,)
    )

    for phase in hyper_combined.hyper_phases:
        phase.run_hyper = run_hyper

    return hyper_combined


class TestHyperAPI(object):
    def test_combined_result(self, hyper_combined):
        result = hyper_combined.run(ci_datas=None)

        assert hasattr(result, "hyper_noise")
        assert isinstance(result.hyper_noise, MockResult)

        assert hasattr(result, "hyper_combined")
        assert isinstance(result.hyper_combined, MockResult)

    def test_combine_variables(self, hyper_combined):
        result = MockResult()
        hyper_noise_result = MockResult()

        hyper_noise_result.variable = af.ModelMapper()

        hyper_noise_result.variable.hyper_noise_scalar_of_ci_regions = (
            ci_hyper.CIHyperNoiseScalar
        )

        result.hyper_noise = hyper_noise_result

        variable = hyper_combined.combine_variables(result)

        assert isinstance(variable.hyper_noise_scalar_of_ci_regions, af.PriorModel)

        assert (
            variable.hyper_noise_scalar_of_ci_regions.cls == ci_hyper.CIHyperNoiseScalar
        )

    def test_instantiation(self, hyper_combined):
        assert len(hyper_combined.hyper_phases) == 1

        noise_phase = hyper_combined.hyper_phases[0]

        assert noise_phase.hyper_name == "hyper_noise"
        assert isinstance(noise_phase, phase_extensions.HyperNoisePhase)

    # def test_hyper_result(self, ccd_data_7x7):
    #     normal_phase = MockPhase()
    #
    #     # noinspection PyTypeChecker
    #     phase = phase_extensions.HyperGalaxyPhase(normal_phase)
    #
    #     # noinspection PyUnusedLocal
    #     def run_hyper(*args, **kwargs):
    #         return MockResult()
    #
    #     phase.run_hyper = run_hyper
    #
    #     result = phase.run(ccd_data_7x7)
    #
    #     assert hasattr(result, "hyper_galaxy")
    #     assert isinstance(result.hyper_galaxy, MockResult)
