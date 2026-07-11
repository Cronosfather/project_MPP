// MPP 2-D baseline domain; a parameterized Venturi contour follows in M1.
SetFactory("OpenCASCADE");
L = 1.0;
h = 0.3;
lc = 0.025;
xmin = -4*L;
xmax = 6*L;
ztop = 3*L;
Rectangle(1) = {xmin, 0, 0, xmax-xmin, ztop, 0};
Rectangle(2) = {0, h, 0, L, 0.04, 0};
BooleanDifference(3) = { Surface{1}; Delete; }{ Surface{2}; Delete; };
Physical Surface("fluid") = {3};
Mesh.CharacteristicLengthMin = lc/4;
Mesh.CharacteristicLengthMax = lc;
Mesh.Algorithm = 6;

