© Ihor Mirzov, UJV Rez, March 2019

Could be freely used and distributed with open-source software



# gmsh2ccx

Convert Gmsh .inp-file to CalculiX .inp-file. Tested on 2D first order triangles and quadrangles.

From Gmsh 'Physical Curve' generates *NSET and *SURFACE blocks. (Gmsh itself does not generate *SURFACE keyword and does not list element edges belonging to the 'Physical Curve'.)

For *SURFACE corectly accounts for element's edge number. It makes possible later to apply boundary conditions on 2D element's edges.

Run with command:

    python3 gmsh2ccx.py gmsh.inp ccx.inp etype

where:

- gmsh.inp is input file name to process (obtained from Gmsh)

- ccx.inp is output file name (for Caclulix)

- 'etype' is CacluliX element type - now could be 'S3' (for 2D triangular mesh) or 'S4' (for 2D quadrilateral mesh)



# inp.py

Parses finite element mesh in the Abaqus, Gmsh or CalculiX .inp-file.

Tested on 2D quadrilateral and triangular first order elements.

Reads nodes coordinates, elements composition, node and element sets, surfaces.

Calculates elements cendroid coordinates.

Generates triangles or quadrangles list to use with matplotlib.

'project_field_on_centroids' method interpolates node field to elements centroids.
