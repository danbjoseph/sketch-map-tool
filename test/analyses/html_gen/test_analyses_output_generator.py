"""
Test analyses_output_generator.py
"""
import json
from typing import Tuple, List, Dict

import pytest
import os
from datetime import datetime
from analyses.helpers import AnalysisResult, QualityLevel, Bbox
from analyses.html_gen import analyses_output_generator


def get_dummy_results() -> Tuple[List[AnalysisResult], List[AnalysisResult], List[AnalysisResult]]:
    """
    Provide dummy analyses results for test purposes
    """
    good_results = [
        AnalysisResult("Looks very good", QualityLevel.GREEN),
        AnalysisResult("Looks excellent", QualityLevel.GREEN, 1.5, "You should be happy",
                       "plot1.png", "My cool report")
    ]
    medium_results = [
        AnalysisResult("Looks ok", QualityLevel.YELLOW),
        AnalysisResult("Looks not too bad", QualityLevel.YELLOW, 0.5,
                       "You should worry a bit, but not too much", "plot2.png", "My cool report")
    ]
    bad_results = [
        AnalysisResult("Looks bad", QualityLevel.RED),
        AnalysisResult("Looks too bad", QualityLevel.RED, 3,
                       "Oh dear...", "plot3.png", "My cool report")
    ]
    return good_results, medium_results, bad_results


test_data_get_general_score = [
    # 0. Only one, green
    (get_dummy_results()[0][0:1], QualityLevel.GREEN),
    # 1. Only one, yellow
    (get_dummy_results()[1][0:1], QualityLevel.YELLOW),
    # 2. Only one, red
    (get_dummy_results()[2][0:1], QualityLevel.RED),
    # 3. Multiple, green
    (get_dummy_results()[0], QualityLevel.GREEN),
    # 4. Average of green and yellow, same weights (1):
    (get_dummy_results()[0][0:1]+get_dummy_results()[1][0:1], QualityLevel.GREEN),
    # 5. Average of yellow and red, same weights (1):
    # (get_dummy_results()[1][0:1]+get_dummy_results()[2][0:1], QualityLevel.YELLOW),
    # TODO: Discuss whether commercial rounding should be implemented or not
    # 6. Average of green and red, same weights (1):
    (get_dummy_results()[0][0:1]+get_dummy_results()[2][0:1], QualityLevel.YELLOW),
    # 7. Average of yellow and red, red has higher weight:
    (get_dummy_results()[1][1:]+get_dummy_results()[2][1:], QualityLevel.RED),
    # 8. Average of yellow and green, 1 green, 2 yellow:
    (get_dummy_results()[1]+get_dummy_results()[0][:1], QualityLevel.YELLOW),
    # 9. Average of yellow and red, 1 yellow, 2 red and higher weight:
    (get_dummy_results()[1][0:1]+get_dummy_results()[2], QualityLevel.RED),
    # 10. Average of yellow and red, 2 yellow, 2 red, red has higher weight:
    (get_dummy_results()[1]+get_dummy_results()[2], QualityLevel.RED),
]

test_data_get_result_texts = [
    # 0. All importances, all levels, suggestions, multiple analyses
    (get_dummy_results()[0]+get_dummy_results()[1]+get_dummy_results()[2],
     (
         {
             QualityLevel.RED: {
                 "very important": ["Looks too bad"],
                 "important": ["Looks bad"],
                 "less important": []
             },
             QualityLevel.YELLOW: {
                 "very important": [],
                 "important": ["Looks ok"],
                 "less important": ["Looks not too bad"]
             },
             QualityLevel.GREEN: {
                 "very important": ["Looks excellent"],
                 "important": ["Looks very good"],
                 "less important": []
             }},
         ["You should be happy", "You should worry a bit, but not too much", "Oh dear..."])),

    # 1. Only one importance
    (get_dummy_results()[0][0:1] + get_dummy_results()[1][0:1] + get_dummy_results()[2][0:1],
     ({QualityLevel.RED: {
         "very important": [],
         "important": ["Looks bad"],
         "less important": []
     },
          QualityLevel.YELLOW: {
              "very important": [],
              "important": ["Looks ok"],
              "less important": []
          },
          QualityLevel.GREEN: {
              "very important": [],
              "important": ["Looks very good"],
              "less important": []
          }}, [])),

    # 2. Only one level
    (get_dummy_results()[0],
     ({QualityLevel.RED: {
         "very important": [],
         "important": [],
         "less important": []
     },
          QualityLevel.YELLOW: {
              "very important": [],
              "important": [],
              "less important": []
          },
          QualityLevel.GREEN: {
              "very important": ["Looks excellent"],
              "important": ["Looks very good"],
              "less important": []
          }}, ["You should be happy"])),

    # 3. No suggestions
    (get_dummy_results()[1][0:1] + get_dummy_results()[2][0:1],
     ({QualityLevel.RED: {
         "very important": [],
         "important": ["Looks bad"],
         "less important": []
     },
          QualityLevel.YELLOW: {
              "very important": [],
              "important": ["Looks ok"],
              "less important": []
          },
          QualityLevel.GREEN: {
              "very important": [],
              "important": [],
              "less important": []
          }}, [])),

    # 4. One suggestion
    (get_dummy_results()[1][0:1] + get_dummy_results()[2],
     ({QualityLevel.RED: {
         "very important": ["Looks too bad"],
         "important": ["Looks bad"],
         "less important": []
     },
          QualityLevel.YELLOW: {
              "very important": [],
              "important": ["Looks ok"],
              "less important": []
          },
          QualityLevel.GREEN: {
              "very important": [],
              "important": [],
              "less important": []
          }}, ["Oh dear..."])),

    # 5. Only one analysis
    (get_dummy_results()[0][1:2],
     ({QualityLevel.RED: {
         "very important": [],
         "important": [],
         "less important": []
     },

          QualityLevel.YELLOW: {
              "very important": [],
              "important": [],
              "less important": []
          },
          QualityLevel.GREEN: {
              "very important": ["Looks excellent"],
              "important": [],
              "less important": []
          }}, ["You should be happy"]))
]


@pytest.mark.parametrize("test_input,expected", test_data_get_general_score)
def test_get_general_score(test_input: List[AnalysisResult], expected: QualityLevel) -> None:
    """
    Test the function 'get_general_score' with multiple test cases defined in
    'test_data_get_general_score'
    """
    assert analyses_output_generator.get_general_score(test_input) == expected


@pytest.mark.parametrize("test_input,expected", test_data_get_result_texts)
def test_get_result_test(test_input: List[AnalysisResult],
                         expected: Tuple[
                             Dict[QualityLevel, Dict[str, List[str]]], List[str]
                         ]) -> None:
    """
    Test the function 'get_result_test' with multiple test cases defined in
    'test_data_get_result_test'
    """
    assert analyses_output_generator.get_result_texts(test_input) == expected


def test_write_results_to_json() -> None:
    """
    Test the function 'write_results_to_json'. Creates a JSON file in the directory in which
    the test is executed and removes it subsequently
    """
    bbox = Bbox.bbox_from_str("8.68913412,49.4098982,8.69604349,49.4137201;")
    results = get_dummy_results()[0]+get_dummy_results()[1]+get_dummy_results()[2]
    pdf_link = "my_dummy_link/report.pdf"
    json_path = "test_output.json"
    analyses_output_generator.write_results_to_json(bbox, results, pdf_link, json_path)
    current_date = datetime.today().date().strftime("%Y-%m-%d")
    center_point = bbox.get_center_point()

    with open(json_path, encoding="utf8") as fr:
        stored_data = json.load(fr)

    assert stored_data["PDF_LINK"] == pdf_link
    assert stored_data["CREATION_DATE"] == current_date
    assert stored_data["RESTART_LINK"] == f"../../analyses?bbox={bbox.get_str(mode='comma')}"
    assert stored_data["MAP_COORDINATES"] == f"{center_point[0]},{center_point[1]}"
    assert stored_data["PLOYGON_COORDINATES"] == f"[[{bbox.lat1},{bbox.lon1}]," \
                                                 f"[{bbox.lat2},{bbox.lon1}]," \
                                                 f"[{bbox.lat2},{bbox.lon2}]," \
                                                 f"[{bbox.lat1},{bbox.lon2}]]"
    assert stored_data["LEVEL"] == "1"  # Yellow, needs to be string as it's used in an image path
    #                                     for the corresponding traffic light
    assert stored_data["MSG_LEVEL_RED"] == {
                 "very important": ["Looks too bad"],
                 "important": ["Looks bad"],
                 "less important": []
             }
    assert stored_data["MSG_LEVEL_YELLOW"] == {
                 "very important": [],
                 "important": ["Looks ok"],
                 "less important": ["Looks not too bad"]
             }
    assert stored_data["MSG_LEVEL_GREEN"] == {
                 "very important": ["Looks excellent"],
                 "important": ["Looks very good"],
                 "less important": []
             }
    assert stored_data["SUGGESTION_LIST"] == ["You should be happy",
                                              "You should worry a bit, but not too much",
                                              "Oh dear..."]
    os.remove(json_path)
