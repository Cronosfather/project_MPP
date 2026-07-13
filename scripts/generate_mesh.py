"""Generate a SU2 mesh with the Gmsh Python API."""
from __future__ import annotations
import argparse
from pathlib import Path
import gmsh

def generate(geometry: Path, output: Path) -> None:
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.open(str(geometry.resolve()))
        gmsh.model.mesh.generate(2)
        gmsh.option.setNumber("Mesh.SaveAll", 0)
        gmsh.write(str(output.resolve()))
    finally:
        gmsh.finalize()

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("geometry",type=Path); p.add_argument("output",type=Path)
    a=p.parse_args(); generate(a.geometry,a.output); print(f"Wrote {a.output}")
if __name__ == "__main__": main()
