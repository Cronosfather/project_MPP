"""Run Gmsh and SU2 for manifest cases."""
from __future__ import annotations
import argparse, csv, importlib.util, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def execute(command: list[str], cwd: Path, log_name: str) -> None:
    with (cwd/log_name).open("w", encoding="utf-8") as log:
        subprocess.run(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True)

def archive_existing(folder: Path) -> Path | None:
    artifacts=[folder/name for name in ("config.cfg","history.csv","su2.log","forces_breakdown.dat")]
    if not any(path.exists() for path in artifacts[1:]): return None
    stamp=datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    destination=folder/"runs"/stamp; destination.mkdir(parents=True,exist_ok=False)
    for path in artifacts:
        if path.exists(): shutil.copy2(path,destination/path.name)
    return destination

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--manifest", type=Path, default=ROOT/"cases/case_manifest.csv")
    p.add_argument("--mesh", action="store_true"); p.add_argument("--solve", action="store_true"); p.add_argument("--case")
    p.add_argument("--no-archive", action="store_true", help="do not archive existing text results before solve")
    a=p.parse_args()
    if not a.mesh and not a.solve: p.error("select --mesh and/or --solve")
    gmsh_exe=shutil.which("gmsh")
    if a.mesh and not gmsh_exe and importlib.util.find_spec("gmsh") is None:
        raise SystemExit("neither gmsh executable nor Python gmsh package was found")
    su2_exe=shutil.which("SU2_CFD")
    local_su2=ROOT/"tools/su2-8.5.0/runtime/bin/SU2_CFD.exe"
    if not su2_exe and local_su2.exists(): su2_exe=str(local_su2)
    if a.solve and not su2_exe: raise SystemExit("SU2_CFD executable not found in PATH or tools/su2-8.5.0")
    with a.manifest.open(encoding="utf-8") as stream: rows=list(csv.DictReader(stream))
    for row in rows:
        if a.case and row["case"] != a.case: continue
        folder=ROOT/row["path"]
        if a.mesh:
            command=[gmsh_exe,"geometry.geo","-2","-format","su2","-o","mesh.su2"] if gmsh_exe else [sys.executable,str(ROOT/"scripts/generate_mesh.py"),"geometry.geo","mesh.su2"]
            execute(command,folder,"gmsh.log")
        if a.solve:
            archived=None if a.no_archive else archive_existing(folder)
            if archived: print(f"archived previous run: {archived.relative_to(ROOT)}")
            execute([su2_exe,"config.cfg"],folder,"su2.log")
        print(f"completed: {row['case']}")
if __name__ == "__main__": main()
