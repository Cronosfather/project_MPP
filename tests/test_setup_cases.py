from scripts.setup_cases import case_name, render

def test_case_name_is_path_safe():
    assert case_name(0.075, "medium") == "steady2d_h_0p075_medium"

def test_render_replaces_values():
    assert render("h={height_m}", {"height_m": 0.1}) == "h=0.1"

