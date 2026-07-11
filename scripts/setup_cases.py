"""Generate reproducible baseline cases from YAML."""
from __future__ import annotations
import argparse, csv
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

def render(template: str, values: dict[str, object]) -> str:
    return template.format(**values)

def case_name(height: float, mesh: str) -> str:
    token = f"{height:.4f}".rstrip("0").rstrip(".").replace(".", "p")
    return f"steady2d_h_{token}_{mesh}"

def generate(study_path: Path) -> list[dict[str, object]]:
    study = yaml.safe_load(study_path.read_text(encoding="utf-8"))
    gmsh = (ROOT / "templates/gmsh/venturi_2d.geo.tpl").read_text(encoding="utf-8")
    su2 = (ROOT / "templates/su2/steady_2d.cfg.tpl").read_text(encoding="utf-8")
    root = ROOT / "cases"; root.mkdir(exist_ok=True)
    rows = []
    length = float(study["reference"]["length_m"])
    geometry = study["geometry"]
    for mesh, ratio in study["steady_2d"]["mesh_levels"].items():
        for h_ratio in study["steady_2d"]["heights_over_L"]:
            name = case_name(float(h_ratio), mesh); folder = root / name; folder.mkdir(exist_ok=True)
            values = {"length_m": length, "height_m": float(h_ratio)*length,
                "mesh_size_m": float(ratio)*length,
                "thickness_m": float(geometry["thickness_over_L"])*length,
                "inlet_clearance_m": float(geometry["inlet_clearance_over_L"])*length,
                "exit_clearance_m": float(geometry["diffuser_exit_clearance_over_L"])*length,
                "throat_x_m": float(geometry["throat_x_over_L"])*length,
                "diffuser_start_x_m": float(geometry["diffuser_start_x_over_L"])*length,
                "domain_inlet_x_m": float(geometry["domain_inlet_x_over_L"])*length,
                "domain_outlet_x_m": float(geometry["domain_outlet_x_over_L"])*length,
                "domain_top_z_m": float(geometry["domain_top_z_over_L"])*length,
                "first_layer_height_m": float(geometry["first_layer_height_over_L"])*length,
                "boundary_layer_thickness_m": float(geometry["boundary_layer_thickness_over_L"])*length,
                "boundary_layer_growth": float(geometry["boundary_layer_growth"]),
                "velocity_mps": study["flow"]["velocity_mps"],
                "density_kgm3": study["flow"]["density_kgm3"],
                "viscosity_pas": study["flow"]["viscosity_pas"],
                "reference_area_m2": study["reference"]["area_2d_m2"], **study["solver"]}
            (folder/"geometry.geo").write_text(render(gmsh, values), encoding="utf-8")
            (folder/"config.cfg").write_text(render(su2, values), encoding="utf-8")
            rows.append({"case": name, "path": folder.relative_to(ROOT), "h_over_L": h_ratio,
                         "mesh": mesh, "status": "configured"})
    with (root/"case_manifest.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
    return rows

def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--study", type=Path, default=ROOT/"config/study.yaml")
    rows = generate(p.parse_args().study.resolve()); print(f"Generated {len(rows)} cases")

if __name__ == "__main__": main()
