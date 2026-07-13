"""Quantify residual and force stability over the final iteration window."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

def analyze(path: Path, window: int, force_tolerance: float, residual_target: float,
            screening_force_tolerance: float = 0.01, screening_residual_target: float = -7.0) -> dict:
    data=pd.read_csv(path,skipinitialspace=True); data.columns=[str(c).strip().strip('"') for c in data.columns]
    tail=data.tail(window); last=data.iloc[-1]
    metrics={"history":str(path),"iterations":int(last["Inner_Iter"])+1,"window":len(tail)}
    for name in ("CL","CD"):
        mean=float(tail[name].mean()); span=float(tail[name].max()-tail[name].min())
        metrics[name]={"last":float(last[name]),"mean":mean,"std":float(tail[name].std()),
                       "span":span,"relative_span":span/max(abs(mean),1e-12)}
    metrics["rms_pressure_last"]=float(last["rms[P]"])
    metrics["residual_pass"]=metrics["rms_pressure_last"] <= residual_target
    metrics["force_pass"]=all(metrics[n]["relative_span"] <= force_tolerance for n in ("CL","CD"))
    metrics["screening_pass"]=(metrics["rms_pressure_last"] <= screening_residual_target and
        all(metrics[n]["relative_span"] <= screening_force_tolerance for n in ("CL","CD")))
    metrics["status"]=("verified" if metrics["residual_pass"] and metrics["force_pass"]
        else "screening" if metrics["screening_pass"] else "provisional")
    return metrics

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("history",type=Path); p.add_argument("--window",type=int,default=200)
    p.add_argument("--force-tolerance",type=float,default=0.005); p.add_argument("--residual-target",type=float,default=-8.0)
    p.add_argument("--output",type=Path); a=p.parse_args(); result=analyze(a.history,a.window,a.force_tolerance,a.residual_target)
    text=json.dumps(result,indent=2); print(text)
    if a.output: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text+"\n",encoding="utf-8")
if __name__=="__main__": main()
