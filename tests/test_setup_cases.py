from scripts.setup_cases import case_name, render
from scripts.check_geometry import REQUIRED, validate_study
from scripts.analyze_convergence import analyze
from pathlib import Path
import pandas as pd

def test_case_name_is_path_safe():
    assert case_name(0.075, "medium") == "steady2d_h_0p075_medium"

def test_render_replaces_values():
    assert render("h={height_m}", {"height_m": 0.1}) == "h=0.1"

def test_study_geometry_relationships():
    assert validate_study(Path("config/study.yaml")) == []

def test_body_boundaries_are_separated():
    assert {"body_lower", "body_upper", "body_leading", "body_trailing"} <= REQUIRED
    assert "body" not in REQUIRED

def test_convergence_requires_residual_and_force_stability(tmp_path):
    history=tmp_path/"history.csv"
    pd.DataFrame({"Inner_Iter":[0,1,2],"rms[P]":[-7.0,-8.1,-8.2],"CL":[-1,-1,-1],"CD":[.1,.1,.1]}).to_csv(history,index=False)
    assert analyze(history,3,.005,-8.0)["status"] == "verified"

def test_screening_status_is_distinct_from_verified(tmp_path):
    history=tmp_path/"history.csv"
    pd.DataFrame({"Inner_Iter":[0,1,2],"rms[P]":[-7.1,-7.2,-7.3],"CL":[-1,-1.004,-1.006],"CD":[.1,.1003,.1005]}).to_csv(history,index=False)
    assert analyze(history,3,.005,-8.0)["status"] == "screening"
