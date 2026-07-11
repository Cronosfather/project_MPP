"""Collect final SU2 force coefficients."""
from __future__ import annotations
import argparse, csv
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def final_coefficients(folder: Path) -> dict:
    files=sorted(folder.glob("history*.csv"))
    if not files: return {"result":"missing"}
    frame=pd.read_csv(files[-1], skipinitialspace=True); frame.columns=[str(c).strip().strip('"') for c in frame.columns]
    out={"result":"available"}; last=frame.iloc[-1]
    for target, aliases in {"CL":["CL","Lift"],"CD":["CD","Drag"]}.items():
        for alias in aliases:
            if alias in frame.columns: out[target]=float(last[alias]); break
    return out

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--manifest",type=Path,default=ROOT/"cases/case_manifest.csv"); a=p.parse_args()
    with a.manifest.open(encoding="utf-8") as stream: rows=list(csv.DictReader(stream))
    output=[{**row,**final_coefficients(ROOT/row["path"])} for row in rows]
    results=ROOT/"results"; results.mkdir(exist_ok=True); pd.DataFrame(output).to_csv(results/"steady_summary.csv",index=False)
    print(f"Wrote {results/'steady_summary.csv'}")
if __name__ == "__main__": main()

