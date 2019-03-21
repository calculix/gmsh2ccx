# gmsh2ccx

Convert Gmsh .inp-file to CalculiX .inp-file.
Works fine with 2D quad and tri first order elements.
From Gmsh 'Physical Curve' generates *NSET and *SURFACE.
For *SURFACE corectly accounts for element's face/edge number.
It makes possible later to apply boundary conditions on surfaces.

Run with command:
    python3 gmsh2ccx.py gmsh.inp ccx.inp mtype
    where:
        - gmsh.inp is input file name to process (obtained from Gmsh)
        - ccx.inp is output file name (for Caclulix)
        - 'mtype' is CacluliX element type - now could be 'S3'
        (for 2D triangular mesh) or 'S4' (for 2D quadrilateral mesh)



# inp.py

Parses Gmsh or CalculiX .inp-file.
Works fine with 2D quadrilateral and triangular first order elements.
