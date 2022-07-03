"""
Test analysis_currentness.py
To accelerate the tests and avoid traffic on ohsome, mocks are used for all requests to the ohsome
API
"""

from analyses.modules import analysis_currentness
from test.analyses.constants import TEST_LOCATION_PLOTS, TEST_DATA_PATH
import pandas as pd
import os
import filecmp


test_data_plot_results = [
    # 2. Multiple features, one in each category
    # 3. Multiple features, one category empty
    # 4. Multiple features, all in one category
    # 5. Key given
    # 6. No key given
    # 7. Column 'TimeDelta' missing
]


test_data_run = [
    # 0. No key specified
    # 1. Key specified
]

# TODO: Test init


def test_plot_location():
    test_data_plot_location = "my/plot/location"
    currentness_analyses = analysis_currentness.CurrentnessAnalysis([], test_data_plot_location)
    currentness_analyses_2 = analysis_currentness.CurrentnessAnalysis([])  # Default value
    assert currentness_analyses.plot_location == test_data_plot_location
    assert currentness_analyses_2.plot_location == "./"


def test_status_file_path():
    test_data_status_file_path = "my/status/path/file.status"
    currentness_analyses = analysis_currentness.CurrentnessAnalysis(
        [], status_file_path=test_data_status_file_path)
    currentness_analyses_2 = analysis_currentness.CurrentnessAnalysis([])  # Default value
    assert currentness_analyses.status_file_path == test_data_status_file_path
    assert currentness_analyses_2.status_file_path == "analyses.status"


def test_plot_results_no_features():
    # Check whether output folder for plot tests exists and is empty
    assert os.path.exists(TEST_LOCATION_PLOTS)
    assert len(os.listdir(TEST_LOCATION_PLOTS)) == 0
    features = pd.DataFrame(columns=["TimeDelta"])
    currentness_analyses = analysis_currentness.CurrentnessAnalysis([], TEST_LOCATION_PLOTS)
    currentness_analyses.plot_results(features)
    assert len(os.listdir(TEST_LOCATION_PLOTS)) == 0


def test_plot_results_one_feature():
    # Check whether output folder for plot tests exists and is empty
    assert os.path.exists(TEST_LOCATION_PLOTS)
    assert len(os.listdir(TEST_LOCATION_PLOTS)) == 0
    features = pd.DataFrame(columns=["TimeDelta"])
    features.loc[0] = [2*365.25]
    expected_plot_path = TEST_DATA_PATH+"plots/expected/currentness/plot_results_one_feature.png"
    actual_plot_path = TEST_LOCATION_PLOTS+"_plot_last_edit_general.png"
    currentness_analyses = analysis_currentness.CurrentnessAnalysis([], TEST_LOCATION_PLOTS)
    currentness_analyses.plot_results(features)
    assert len(os.listdir(TEST_LOCATION_PLOTS)) == 1
    assert filecmp.cmp(expected_plot_path, actual_plot_path)
    os.remove(actual_plot_path)
    assert len(os.listdir(TEST_LOCATION_PLOTS)) == 0
