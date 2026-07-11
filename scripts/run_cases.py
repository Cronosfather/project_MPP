"""Run Gmsh and SU2 for manifest cases."""
from __future__ import annotations
import argparse, csv, shutil, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def execute(command: list[str], cwd: Path, log_name: str) -> None:
    with (cwd/log_name).open("w", encoding="utf-8") as log:
        subprocess.run(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True)

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--manifest", type=Path, default=ROOT/"cases/case_manifest.csv")
    p.add_argument("--mesh", action="store_true"); p.add_argument("--solve", action="store_true"); p.add_argument("--case")
    a=p.parse_args()
    if not a.mesh and not a.solve: p.error("select --mesh and/or --solve")
    if a.mesh and not shutil.which("gmsh"): raise SystemExit("gmsh executable not found in PATH")
    if a.solve and not shutil.which("SU2_CFD"): raise SystemExit("SU2_CFD executable not found in PATH")
    with a.manifest.open(encoding="utf-8") as stream: rows=list(csv.DictReader(stream))
    for row in rows:
        if a.case and row["case"] != a.case: continue
        folder=ROOT/row["path"]
        if a.mesh: execute(["gmsh","geometry.geo","-2","-format","su2","-o","mesh.su2"],folder,"gmsh.log")
        if a.solve: execute(["SU2_CFD","config.cfg"],folder,"su2.log")
        print(f"completed: {row['case']}")
if __name__ == "__main__": main()

