size = 10; // element's size
Mesh.CharacteristicLengthMin = size;
Mesh.CharacteristicLengthMax = size;
Mesh.Algorithm = 6; // Frontal-Delaunay
Mesh.RecombinationAlgorithm = 2; // simple full-quad
Mesh.RecombineAll = 1;

Point(1) = {0, 0, 0, size}; // left bottom
Point(2) = {10, 0, 0, size}; // right bottom
Point(3) = {10, 10, 0, size}; // right top
Point(4) = {0, 10, 0, size}; // left top

Line(1) = {1, 2}; // bottom
Line(2) = {2, 3}; // right
Line(3) = {3, 4}; // top
Line(4) = {4, 1}; // left

Curve Loop(1) = {1:4};
Plane Surface(1) = {1};
Physical Curve("RIGHT") = {2};
Physical Curve("LEFT") = {4};
