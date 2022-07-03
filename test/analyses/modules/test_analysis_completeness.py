"""
Test analysis_completeness.py
To accelerate the tests and avoid traffic on ohsome, mocks are used for all requests to the ohsome
API
"""
import pytest
import requests
import json
import os
import filecmp
from multiprocessing import Queue
from unittest.mock import patch
from analyses.modules import analysis_completeness
from analyses.helpers import Bbox
from test.analyses.constants import TEST_LOCATION_PLOTS, TEST_DATA_PATH, TEST_LOCATION_STATUS_FILES


TEST_BBOX = Bbox.bbox_from_str("60.4511654,49.3308452,60.4523993,49.3315288;")
TEST_TIME_STR = "2014-01-01/2017-01-01/P1Y"

test_data_completeness = []
for name in ["test_data_completeness_0.json",  # 0. Value always 0
             "test_data_completeness_1.json",  # 1. Value always 100
             "test_data_completeness_2.json",  # 2. Value varying
             ]:
    with open(f"test/analyses/test_data/responses/completeness/{name}", encoding="utf8") as fw:
        test_data_completeness.append(json.load(fw))


def test_init() -> None:
    """
    Test the method '__init__'
    """
    completeness_analysis = analysis_completeness.CompletenessAnalysis(TEST_BBOX, TEST_TIME_STR)
    assert completeness_analysis.bbox == TEST_BBOX
    assert completeness_analysis.time == TEST_TIME_STR
    assert completeness_analysis.key is None
    assert completeness_analysis.measure == "density"
    assert completeness_analysis.measure_unit == "features per km²"
    assert completeness_analysis.plot_location == "./"
    assert completeness_analysis.status_file_path == "analyses.status"
    assert completeness_analysis.title == "Saturation Analysis"
    assert completeness_analysis.plot_name == "_plot_saturation_general.png"

    plot_location = "my/plot/location"
    status_file_path = "status/file/log.status"
    key = "amenity"
    measure = "length"
    measure_unit = "metres"
    completeness_analysis_2 = analysis_completeness.CompletenessAnalysis(TEST_BBOX,
                                                                         TEST_TIME_STR,
                                                                         plot_location,
                                                                         status_file_path,
                                                                         key,
                                                                         measure,
                                                                         measure_unit)
    assert completeness_analysis_2.bbox == TEST_BBOX
    assert completeness_analysis_2.time == TEST_TIME_STR
    assert completeness_analysis_2.key == key
    assert completeness_analysis_2.measure == measure
    assert completeness_analysis_2.measure_unit == measure_unit
    assert completeness_analysis_2.plot_location == plot_location
    assert completeness_analysis_2.status_file_path == status_file_path
    assert completeness_analysis_2.title == "Saturation Analysis for 'amenity' features"
    assert completeness_analysis_2.plot_name == "_plot_saturation_amenity.png"


def test_plot_location() -> None:
    """
    Test the property 'plot_location'
    """
    test_data_plot_location = "my/plot/location"
    completeness_analysis = analysis_completeness.CompletenessAnalysis(TEST_BBOX, TEST_TIME_STR,
                                                                       test_data_plot_location)
    completeness_analysis_2 = analysis_completeness.CompletenessAnalysis(
        TEST_BBOX, TEST_TIME_STR)  # Default value
    assert completeness_analysis.plot_location == test_data_plot_location
    assert completeness_analysis_2.plot_location == "./"


def test_status_file_path() -> None:
    """
    Test the property 'status_file_path'
    """
    test_data_status_file_path = "my/status/file.path"
    completeness_analysis = analysis_completeness.CompletenessAnalysis(
        TEST_BBOX, TEST_TIME_STR, status_file_path=test_data_status_file_path)
    completeness_analysis_2 = analysis_completeness.CompletenessAnalysis(
        TEST_BBOX, TEST_TIME_STR)  # Default value
    assert completeness_analysis.status_file_path == test_data_status_file_path
    assert completeness_analysis_2.status_file_path == "analyses.status"


def test_request_density() -> None:
    """
    Test the method 'request' with aggregation 'density'
    """
    with patch("requests.get") as mock:
        mock.return_value = test_data_completeness[0]
        result = analysis_completeness.CompletenessAnalysis.request("density",
                                      filter="amenity=* and (type:node or type:way)",
                                      bboxes="1.23,2.34,3.45,4.56",
                                      time="2014-01-01/2017-01-01/P1Y")
    mock.assert_called_once_with("https://api.ohsome.org/stable/elements/count/density",
                                 {
                                     "filter": "amenity=* and (type:node or type:way)",
                                     "bboxes": "1.23,2.34,3.45,4.56",
                                     "time": "2014-01-01/2017-01-01/P1Y"
                                 }
                                 )
    assert result == test_data_completeness[0]


def test_request_length() -> None:
    """
    Test the method 'request' with aggregation 'length'
    """
    with patch("requests.get") as mock:
        mock.return_value = test_data_completeness[0]
        result = analysis_completeness.CompletenessAnalysis.request("length",
                                      filter="amenity=* and (type:node or type:way)",
                                      bboxes="1.23,2.34,3.45,4.56",
                                      time="2014-01-01/2017-01-01/P1Y")
    mock.assert_called_once_with("https://api.ohsome.org/stable/elements/length",
                                 {
                                     "filter": "amenity=* and (type:node or type:way)",
                                     "bboxes": "1.23,2.34,3.45,4.56",
                                     "time": "2014-01-01/2017-01-01/P1Y"
                                 }
                                 )
    assert result == test_data_completeness[0]


def test_plot_results_always_zero() -> None:
    """
    Test the method 'plot_results' with values always 0
    """
    # Check whether output folder for plot tests exists and is empty
    assert os.path.exists(TEST_LOCATION_PLOTS)
    assert len(os.listdir(TEST_LOCATION_PLOTS)) == 0

    expected_plot_path = TEST_DATA_PATH + "plots/expected/completeness/plot_results_always_zero.png"
    actual_plot_path = TEST_LOCATION_PLOTS + "_plot_saturation_general.png"

    completeness_analysis = analysis_completeness.CompletenessAnalysis(
        TEST_BBOX, TEST_TIME_STR, plot_location=TEST_LOCATION_PLOTS)
    result = test_data_completeness[0]["result"]
    test_data = []
    for datum in result:
        test_data.append((datum["timestamp"], datum["value"]))
    completeness_analysis.plot_results(test_data, "My Title", "This is y")

    assert len(os.listdir(TEST_LOCATION_PLOTS)) == 1
    assert filecmp.cmp(expected_plot_path, actual_plot_path)
    os.remove(actual_plot_path)
    assert len(os.listdir(TEST_LOCATION_PLOTS)) == 0


def test_plot_results_constant() -> None:
    """
    Test the method 'plot_results' with values always 100
    """
    # Check whether output folder for plot tests exists and is empty
    assert os.path.exists(TEST_LOCATION_PLOTS)
    assert len(os.listdir(TEST_LOCATION_PLOTS)) == 0

    expected_plot_path = TEST_DATA_PATH + \
                         "plots/expected/completeness/plot_results_always_hundred.png"
    actual_plot_path = TEST_LOCATION_PLOTS + "_plot_saturation_general.png"

    completeness_analysis = analysis_completeness.CompletenessAnalysis(
        TEST_BBOX, TEST_TIME_STR, plot_location=TEST_LOCATION_PLOTS)
    result = test_data_completeness[1]["result"]
    test_data = []
    for datum in result:
        test_data.append((datum["timestamp"], datum["value"]))
    completeness_analysis.plot_results(test_data, "My Title", "This is y")

    assert len(os.listdir(TEST_LOCATION_PLOTS)) == 1
    assert filecmp.cmp(expected_plot_path, actual_plot_path)
    os.remove(actual_plot_path)
    assert len(os.listdir(TEST_LOCATION_PLOTS)) == 0


def test_plot_results_varying() -> None:
    """
    Test the method 'plot_results' with values varying
    """
    # Check whether output folder for plot tests exists and is empty
    assert os.path.exists(TEST_LOCATION_PLOTS)
    assert len(os.listdir(TEST_LOCATION_PLOTS)) == 0

    expected_plot_path = TEST_DATA_PATH + \
                         "plots/expected/completeness/plot_results_varying.png"
    actual_plot_path = TEST_LOCATION_PLOTS + "_plot_saturation_general.png"

    completeness_analysis = analysis_completeness.CompletenessAnalysis(
        TEST_BBOX, TEST_TIME_STR, plot_location=TEST_LOCATION_PLOTS)
    result = test_data_completeness[2]["result"]
    test_data = []
    for datum in result:
        test_data.append((datum["timestamp"], datum["value"]))
    completeness_analysis.plot_results(test_data, "My Title", "This is y")

    assert len(os.listdir(TEST_LOCATION_PLOTS)) == 1
    assert filecmp.cmp(expected_plot_path, actual_plot_path)
    os.remove(actual_plot_path)
    assert len(os.listdir(TEST_LOCATION_PLOTS)) == 0


@pytest.fixture
def completeness_analysis():
    return analysis_completeness.CompletenessAnalysis(TEST_BBOX,
                                                      TEST_TIME_STR,
                                                      plot_location=TEST_LOCATION_PLOTS,
                                                      status_file_path=TEST_LOCATION_STATUS_FILES +
                                                      "status.status")


class DummyResponse:
    def __init__(self, dict_contents):
        self.dict_contents = dict_contents

    def json(self):
        return self.dict_contents


def test_run_no_features(completeness_analysis):
    """
    Test the method 'run' with no features present, i.e. a lack of data
    """
    queue = Queue()
    with patch("requests.get") as mock:
        mock.return_value = DummyResponse(test_data_completeness[0])
        result = completeness_analysis.run(queue)
    mock.assert_called_once_with("https://api.ohsome.org/stable/elements/count/density",
                                 {
                                     "bboxes": "60.4511654,49.3308452,60.4523993,49.3315288",
                                     "time": "2014-01-01/2017-01-01/P1Y",
                                     "filter": "type:node or type:way"
                                 }
                                 )

    assert False  # ToDo: Add checks for status file, result, generated plot, and queue


test_data_run = [
    # 0. Lack of data, no features at all
    # ("", "test_data/test_data_run_0.json")
    # 1. Lack of data, no features with given key
    # 2. Lack of data, only few features with given key
    # 3. Very small bbox
    # 4. Large bbox
    # 5. Unsaturated yellow all features density
    # 6. Unsaturated red all features density
    # 7. Saturated all features density
    # 8. Unsaturated yellow features with given key density
    # 9. Unsaturated red features with given key density
    # 10. Saturated features with given key density
    # 11. Unsaturated yellow features with given key length
    # 12. Unsaturated red features with given key length
    # 13. Saturated features with given key length
    # (1, 2)
]
