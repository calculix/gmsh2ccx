© Ihor Mirzov, May 2019  
Distributed under GNU General Public License v3.0

<br/><br/>



# Gmsh to CalculiX converter (.inp to .inp)

The problem is that for 2D cases during exporting mesh in the .inp-format Gmsh does not generate *SURFACE keyword and does not list element edges belonging to the 'Physical Curve'. It makes impossible later to apply boundary conditions on 2D element's edges in CalculiX.

Moreover, for each geometrical line Gmsh creates and exports beam (T3D2) elements which in 2D case is absolutely unacceptable, because leads to unwanted entities in the Calculix model.

<br/><br/>



# gmsh3.geo, gmsh4.geo

Gmsh example files. You'll need 'gmsh' command to be available in your OS. Generate 2D square and mesh it with CPS3 or CPS4 elements with command:

    gmsh gmsh3.geo -2 -o gmsh3.inp -v 0 -save_all

for triangular mesh or:

    gmsh gmsh4.geo -2 -o gmsh4.inp -v 0 -save_all

for quadrilateral mesh.

<br/><br/>



# gmsh2ccx.py

Convert Gmsh .inp-file to CalculiX .inp-file. Works with 2D first order triangles and quadrangles. Tested in Gmsh 4.2.2 and Calculix 2.15.

The script from Gmsh element sets corresponding to the 'Physical Curve' generates *SURFACE and *NSET (optionally) blocks. For the *SURFACE corectly accounts for element's edge numbers.

Run with command:

    python3 gmsh2ccx.py -g gmsh3.inp -c ccx3.inp -e S3 -ns 1

or

    python3 gmsh2ccx.py -g gmsh4.inp -c ccx4.inp -e S4 -ns 1

where:

- gmsh3.inp/gmsh4.inp are input file names to process (obtained from Gmsh)

- ccx3.inp/ccx3.inp are output file names (for Caclulix)

- S3/S4 are CacluliX element types: S3 for 2D triangular mesh, S4 for 2D quadrilateral mesh

- ns is a flag showing whether to output node sets (1) or not (0) 

The script needs INPParser.py library.

<br/><br/>



# INPParser.py

Parses finite element mesh in the Abaqus, Gmsh or CalculiX .inp-file.

Tested on C3D8, 2D quadrilateral and triangular first order elements.

Reads nodes coordinates, elements composition, node and element sets, surfaces.

Calculates elements cendroid coordinates.

Generates triangles or quadrangles list to use with matplotlib.

'project_field_on_centroids' method interpolates node field to elements centroids.

<br/><br/>



# Your help

- Simply use this software and ask questions.
- Share your models and screenshots.
- Report problems by [posting issues](https://github.com/imirzov/gmsh2ccx/issues).
- Do something from the [TODO-list](#TODO).

<br/><br/>



# TODO

- dimensionality parameter in INPParser.py
- automatically distinguish mesh dimensions (2D/3D)
- automatically distinguish elements type (S3/S4/S6/S8)
- check elements normals
- second order elements S6, S8
