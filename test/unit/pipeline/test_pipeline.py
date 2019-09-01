import builtins

import pytest

import autofit as af
import autocti as ac


class MockFile(object):
    def __init__(self):
        self.text = None
        self.filename = None

    def write(self, text):
        self.text = text

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


@pytest.fixture(name="mock_files", autouse=True)
def make_mock_file(monkeypatch):
    files = []

    def mock_open(filename, flag, *args, **kwargs):
        assert flag in ("w+", "w+b", "a")
        file = MockFile()
        file.filename = filename
        files.append(file)
        return file

    monkeypatch.setattr(builtins, "open", mock_open)
    return files


class Optimizer(object):
    def __init__(self, phase_name="dummy_phase"):
        self.phase_name = phase_name
        self.phase_path = ""


class DummyPhase(af.AbstractPhase):
    def make_result(self, result, analysis):
        pass

    def __init__(self, phase_name, phase_tag=None):
        super().__init__(phase_name)
        self.masked_image = None
        self.results = None
        self.phase_name = phase_name
        self.phase_tag = phase_tag
        self.phase_path = phase_name

        self.optimizer = Optimizer(phase_name)

    def run(self, ci_datas, cti_settings, results, pool):
        self.ci_datas = ci_datas
        self.cti_settings = cti_settings
        self.results = results
        self.pool = pool
        return af.Result(af.ModelInstance(), 1)


class TestPipeline(object):
    def test_run_pipeline(self):
        phase_1 = DummyPhase(phase_name="dummy1")
        phase_2 = DummyPhase(phase_name="dummy2")
        pipeline = ac.Pipeline("", phase_1, phase_2)

        pipeline.run(ci_datas=None, cti_settings=None, pool=None)

        assert len(phase_1.results) == 2
        assert len(phase_2.results) == 2

    def test_addition(self):
        phase_1 = DummyPhase(phase_name="dummy1")
        phase_2 = DummyPhase(phase_name="dummy2")
        phase_3 = DummyPhase(phase_name="dumy3")

        pipeline1 = ac.Pipeline("", phase_1, phase_2)
        pipeline2 = ac.Pipeline("", phase_3)

        assert (phase_1, phase_2, phase_3) == (pipeline1 + pipeline2).phases
