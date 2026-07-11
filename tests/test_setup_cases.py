from scripts.setup_cases import case_name, render
from scripts.check_geometry import validate_study
from pathlib import Path

def test_case_name_is_path_safe():
    assert case_name(0.075, "medium") == "steady2d_h_0p075_medium"

def test_render_replaces_values():
    assert render("h={height_m}", {"height_m": 0.1}) == "h=0.1"

def test_study_geometry_relationships():
    assert validate_study(Path("config/study.yaml")) == []
