"""Extract body-lower pressure and skin-friction fields from SU2 surface VTU."""
from __future__ import annotations
import argparse, json, re, struct
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def read_appended_arrays(vtu: Path) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Read selected SU2 VTU arrays without decoding unrelated sparse arrays."""
    payload=vtu.read_bytes()
    marker=b'<AppendedData encoding="raw">'
    marker_start=payload.index(marker)+len(marker)
    raw_start=payload.index(b"_",marker_start)+1
    header=payload[:marker_start].decode("utf-8")
    pattern=re.compile(
        r'<DataArray type="(?P<type>\w+)" Name="(?P<name>[^"]*)" '
        r'NumberOfComponents=\s*"(?P<components>\d+)" offset="(?P<offset>\d+)"'
    )
    dtype_map={"Float32":"<f4","Float64":"<f8"}
    selected={"", "Pressure_Coefficient", "Skin_Friction_Coefficient", "Y_Plus"}
    arrays: dict[str,np.ndarray]={}
    for match in pattern.finditer(header):
        name=match.group("name")
        if name not in selected or match.group("type") not in dtype_map: continue
        start=raw_start+int(match.group("offset")); byte_count=struct.unpack_from("<Q",payload,start)[0]
        dtype=np.dtype(dtype_map[match.group("type")]); components=int(match.group("components"))
        if byte_count % dtype.itemsize:
            if name=="Y_Plus": continue
            raise ValueError(f"{name or 'coordinates'} byte count is not aligned to {dtype}")
        array=np.frombuffer(payload,offset=start+8,count=byte_count//dtype.itemsize,dtype=dtype)
        if components>1: array=array.reshape((-1,components))
        arrays[name]=array.copy()
    missing={"", "Pressure_Coefficient", "Skin_Friction_Coefficient"}-arrays.keys()
    if missing: raise ValueError(f"missing required VTU arrays: {sorted(missing)}")
    return arrays.pop(""),arrays

def extract(vtu: Path, output: Path) -> dict:
    points,pdata=read_appended_arrays(vtu)
    cp=np.asarray(pdata["Pressure_Coefficient"]).reshape(-1)
    cf=np.asarray(pdata["Skin_Friction_Coefficient"])
    if len(cp) != len(points) or len(cf) != len(points):
        raise ValueError("Cp or skin-friction array does not match surface coordinates")
    frame=pd.DataFrame({"x":points[:,0],"z":points[:,1],"cp":cp,
        "cf_x":cf[:,0],"cf_z":cf[:,1],"cf_magnitude":np.linalg.norm(cf[:,:2],axis=1)})
    frame=frame.sort_values("x").drop_duplicates(subset=["x","z"]).reset_index(drop=True)
    output.parent.mkdir(parents=True,exist_ok=True); frame.to_csv(output,index=False)
    yplus=np.asarray(pdata.get("Y_Plus",[])).reshape(-1)
    result={"source":str(vtu),"output":str(output),"points":len(frame),
        "cp_min":float(frame.cp.min()),"cp_max":float(frame.cp.max()),
        "cf_max":float(frame.cf_magnitude.max()),
        "y_plus_status":"available" if len(yplus)==len(points) else "unmapped_sparse_array",
        "y_plus_values":int(len(yplus)),"coordinate_points":int(len(points))}
    if len(yplus)==len(points):
        result.update({"y_plus_min":float(yplus.min()),"y_plus_mean":float(yplus.mean()),
            "y_plus_max":float(yplus.max())})
    return result

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("case"); p.add_argument("--output",type=Path); a=p.parse_args()
    case=ROOT/"cases"/a.case; output=a.output or ROOT/"results"/f"{a.case}_body_lower.csv"
    print(json.dumps(extract(case/"surface.vtu",output),indent=2))
if __name__=="__main__": main()
