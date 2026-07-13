import struct
from pathlib import Path

import numpy as np

from scripts.postprocess_underfloor import read_appended_arrays


def test_read_appended_arrays_ignores_unrelated_arrays(tmp_path: Path) -> None:
    arrays = [
        ("", 3, np.array([[0.0, 0.1, 0.0], [1.0, 0.2, 0.0]], dtype="<f4")),
        ("Pressure_Coefficient", 1, np.array([-1.2, -0.4], dtype="<f4")),
        (
            "Skin_Friction_Coefficient",
            3,
            np.array([[0.01, 0.0, 0.0], [0.02, 0.0, 0.0]], dtype="<f4"),
        ),
    ]
    offsets = []
    blocks = []
    offset = 0
    for _, _, values in arrays:
        raw = values.tobytes()
        block = struct.pack("<Q", len(raw)) + raw
        offsets.append(offset)
        blocks.append(block)
        offset += len(block)
    tags = "\n".join(
        f'<DataArray type="Float32" Name="{name}" NumberOfComponents= "{components}" '
        f'offset="{array_offset}" format="appended"/>'
        for (name, components, _), array_offset in zip(arrays, offsets)
    )
    vtu = tmp_path / "surface.vtu"
    vtu.write_bytes(
        (f'<VTKFile><UnstructuredGrid><Piece><PointData>{tags}</PointData></Piece>'
         f'</UnstructuredGrid><AppendedData encoding="raw">\n_').encode()
        + b"".join(blocks)
        + b"\n</AppendedData></VTKFile>"
    )

    points, point_data = read_appended_arrays(vtu)

    np.testing.assert_allclose(points[:, :2], [[0.0, 0.1], [1.0, 0.2]])
    np.testing.assert_allclose(point_data["Pressure_Coefficient"], [-1.2, -0.4])
    assert point_data["Skin_Friction_Coefficient"].shape == (2, 3)
