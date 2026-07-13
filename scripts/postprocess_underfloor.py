"""Extract body-lower pressure and skin-friction fields from SU2 surface VTU."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from meshio.vtu._vtu import VtuReader

ROOT = Path(__file__).resolve().parents[1]

def extract(vtu: Path, output: Path) -> dict:
    reader=VtuReader(str(vtu)); points=np.asarray(reader.points); pdata=reader.point_data
    cp=np.asarray(pdata["Pressure_Coefficient"]).reshape(-1)
    cf=np.asarray(pdata["Skin_Friction_Coefficient"])
    if len(cp) != len(points) or len(cf) != len(points):
        raise ValueError("Cp or skin-friction array does not match surface coordinates")
    frame=pd.DataFrame({"x":points[:,0],"z":points[:,1],"cp":cp,
        "cf_x":cf[:,0],"cf_z":cf[:,1],"cf_magnitude":np.linalg.norm(cf[:,:2],axis=1)})
    frame=frame.sort_values("x").drop_duplicates(subset=["x","z"]).reset_index(drop=True)
    output.parent.mkdir(parents=True,exist_ok=True); frame.to_csv(output,index=False)
    yplus=np.asarray(pdata.get("Y_Plus",[])).reshape(-1)
    return {"source":str(vtu),"output":str(output),"points":len(frame),
        "cp_min":float(frame.cp.min()),"cp_max":float(frame.cp.max()),
        "cf_max":float(frame.cf_magnitude.max()),
        "y_plus_status":"available" if len(yplus)==len(points) else "unmapped_sparse_array",
        "y_plus_values":int(len(yplus)),"coordinate_points":int(len(points))}

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("case"); p.add_argument("--output",type=Path); a=p.parse_args()
    case=ROOT/"cases"/a.case; output=a.output or ROOT/"results"/f"{a.case}_body_lower.csv"
    print(json.dumps(extract(case/"surface.vtu",output),indent=2))
if __name__=="__main__": main()
