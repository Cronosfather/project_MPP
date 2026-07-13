"""Validate parameter relationships and rendered Gmsh physical groups."""
from __future__ import annotations
import argparse, csv, re
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"ground", "inlet", "outlet", "farfield", "body_lower", "body_upper",
            "body_leading", "body_trailing", "fluid"}

def validate_study(path: Path) -> list[str]:
    s = yaml.safe_load(path.read_text(encoding="utf-8")); g=s["geometry"]
    errors=[]
    if not 0 < g["throat_x_over_L"] < g["diffuser_start_x_over_L"] < 1:
        errors.append("expected 0 < throat_x < diffuser_start_x < 1")
    minimum=min(float(v) for v in s["steady_2d"]["heights_over_L"])
    if minimum <= 5*float(g["first_layer_height_over_L"]):
        errors.append("minimum clearance is too small relative to first layer height")
    if g["domain_inlet_x_over_L"] >= 0 or g["domain_outlet_x_over_L"] <= 1:
        errors.append("outer domain does not enclose the body")
    if g["inlet_clearance_delta_over_L"] <= 0 or g["diffuser_exit_clearance_delta_over_L"] <= 0:
        errors.append("Venturi inlet and exit clearances must remain above the throat")
    return errors

def validate_cases(manifest: Path) -> list[str]:
    errors=[]
    with manifest.open(encoding="utf-8") as stream: rows=list(csv.DictReader(stream))
    for row in rows:
        geo=(ROOT/row["path"]/"geometry.geo").read_text(encoding="utf-8")
        groups=set(re.findall(r'Physical (?:Curve|Surface)\("([^"]+)"\)',geo))
        missing=REQUIRED-groups
        if missing: errors.append(f"{row['case']}: missing groups {sorted(missing)}")
    return errors

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--study",type=Path,default=ROOT/"config/study.yaml")
    p.add_argument("--manifest",type=Path,default=ROOT/"cases/case_manifest.csv"); a=p.parse_args()
    errors=validate_study(a.study)+validate_cases(a.manifest)
    if errors: raise SystemExit("Geometry validation failed:\n- "+"\n- ".join(errors))
    print("Geometry parameters and physical groups: OK")
if __name__ == "__main__": main()
