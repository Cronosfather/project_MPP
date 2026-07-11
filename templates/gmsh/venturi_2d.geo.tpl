// MPP parameterized 2-D Venturi underfloor.
L = {length_m};
h = {height_m};
lc = {mesh_size_m};
th = {thickness_m};
hin = {inlet_clearance_m};
hout = {exit_clearance_m};
xt = {throat_x_m};
xd = {diffuser_start_x_m};
xmin = {domain_inlet_x_m};
xmax = {domain_outlet_x_m};
ztop = {domain_top_z_m};

// Outer farfield, counter-clockwise.
Point(1) = {{xmin, 0, 0, lc}};
Point(2) = {{xmax, 0, 0, lc}};
Point(3) = {{xmax, ztop, 0, lc}};
Point(4) = {{xmin, ztop, 0, lc}};
Line(1) = {{1, 2}}; // moving ground
Line(2) = {{2, 3}}; // outlet
Line(3) = {{3, 4}}; // upper farfield
Line(4) = {{4, 1}}; // inlet

// Closed solid body. Lower contour runs nose to tail and contains the throat.
Point(10) = {{0.00*L, hin, 0, lc/5}};
Point(11) = {{0.15*L, hin-0.25*(hin-h), 0, lc/5}};
Point(12) = {{xt, h, 0, lc/6}};
Point(13) = {{xd, h, 0, lc/6}};
Point(14) = {{1.00*L, hout, 0, lc/5}};
Spline(10) = {{10, 11, 12, 13, 14}};
Point(15) = {{1.00*L, hout+th, 0, lc/4}};
Point(16) = {{0.00*L, hin+th, 0, lc/4}};
Line(11) = {{14, 15}};
Line(12) = {{15, 16}};
Line(13) = {{16, 10}};

Curve Loop(20) = {{1, 2, 3, 4}};
Curve Loop(21) = {{10, 11, 12, 13}};
Plane Surface(30) = {{20, 21}};

Physical Curve("ground") = {{1}};
Physical Curve("outlet") = {{2}};
Physical Curve("farfield") = {{3}};
Physical Curve("inlet") = {{4}};
Physical Curve("body") = {{10, 11, 12, 13}};
Physical Surface("fluid") = {{30}};

// Boundary-layer field on all solid-body curves.
Field[1] = BoundaryLayer;
Field[1].CurvesList = {{10, 11, 12, 13}};
Field[1].Size = {first_layer_height_m};
Field[1].Thickness = {boundary_layer_thickness_m};
Field[1].Ratio = {boundary_layer_growth};
Field[1].Quads = 1;
BoundaryLayer Field = 1;

Mesh.CharacteristicLengthMin = {first_layer_height_m};
Mesh.CharacteristicLengthMax = lc;
Mesh.Algorithm = 6;
Mesh.Smoothing = 10;
