# -*- coding: utf-8 -*-
# © Ihor Mirzov, UJV Rez, March 2019
# Could be freely used and distributed with open-source software

"""
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
"""

import sys
from inp import Mesh

# Converts element types from gmsh to ccx
def rename_element(gmsh_elem_type):
    dic =\
        {
            'C1D2':'B31',
            'T3D2':'B31',
            'C1D3':'B32',
            'T3D3':'B32',
            'C2D3':'S3',
            'CPS3':'S3',
            'C2D4':'S4',
            'CPS4':'S4',
        }
    try:
        ccx_elem_type = dic[gmsh_elem_type]
    except:
        ccx_elem_type = gmsh_elem_type
        print('Error converting element type', gmsh_elem_type)
    return ccx_elem_type

# Element's edge number
def element_face(etype, elem_nodes, n1, n2):
    # See Calculix 2.15 documentation, chapter "7.114 *SURFACE"

    # Triangular and quadrilateral shell elements
    if etype in ('S3','S4'):
        """
            tri (S3):
                Face 3: 1-2
                Face 4: 2-3
                Face 5: 3-1
            quad (S4):
                Face 3: 1-2
                Face 4: 2-3
                Face 5: 3-4
                Face 6: 4-1
        """
        for fnum in range(len(elem_nodes)-1):
            if elem_nodes[fnum]==n1 and elem_nodes[fnum+1]==n2:
                return fnum+3
        return len(elem_nodes)+2

    # Triangular and quadrilateral plane stress, plane strain and axisymmetric elements
    if etype in ('CPS3', 'CPS4', 'CPE3', 'CPE4'):
        """
            tri (S3):
                Face 1: 1-2
                Face 2: 2-3
                Face 3: 3-1
            quad (S4):
                Face 1: 1-2
                Face 2: 2-3
                Face 3: 3-4
                Face 4: 4-1
        """
        for fnum in range(len(elem_nodes)-1):
            if elem_nodes[fnum]==n1 and elem_nodes[fnum+1]==n2:
                return fnum+1
        return len(elem_nodes)

if __name__ == '__main__':

    # Global parameters
    OK = True # if sys.argv are ok
    try: # get as a paramenter from console
        GMSH = sys.argv[1]
        CCX = sys.argv[2]
        mtype = sys.argv[3]
    except:
        print('Wrong parameters')
        OK = False

    if OK:
        mesh = Mesh(GMSH) # parse mesh, define nodes, elements and centroids
        # max_nodes = 0 # maximum amount of nodes in elements of all types

        # Process lines of gmsh-file and write ccx-file
        with open(CCX, 'w') as ccx:

            # Nodes block
            if len(mesh.nodes):
                ccx.write('*NODE, NSET=ALL\n') # append name of the node set
                for k,v in mesh.nodes.items():
                    coords = str(v)[1:-1]
                    if not '0.0, 0.0, 0.0' in coords:
                        ccx.write('\t{0}, {1}\n'.format(k, coords)) # v without braces

            # Elements block
            if len(mesh.elements):
                ccx.write('*ELEMENT, type=' + mtype + ', ELSET=ALL\n')
                for elem, nodes in mesh.elements.items():
                    # max_nodes = max(max_nodes, len(nodes))
                    gmsh_elem_type = mesh.types[elem]
                    ccx_elem_type = rename_element(gmsh_elem_type)
                    if mtype == ccx_elem_type: # save only needed elements
                        ccx.write('\t{0}, {1}\n'.format(elem, str(nodes)[1:-1])) # v without braces

            # Process node and element sets and define element faces
            for setname in mesh.esets.keys(): # ['CANALS', 'IN', 'OUT']
                # Write node set
                ccx.write('*NSET, NSET={0}\n'.format(setname))
                for e in mesh.esets[setname]:
                    for n in mesh.elements[e]:
                        ccx.write('\t{0},\n'.format(n))

                # Elements of type 'mtype', grouped by face numbers
                F = {} # {'facenum1':(elements1), 'facenum2':(elements2), }
                for fnum in range(6): # there is no element with more than 6 faces
                    F[fnum+1] = () # in the ccx inp.-file face number should start from 1
                for sbe in mesh.esets[setname]: # beam elements composing free surface
                    n1 = mesh.elements[sbe][0] # node 1 of surface beam element
                    n2 = mesh.elements[sbe][1] # node 2 of surface beam element

                    # Find 'mtype' element by the nodes n1, n2
                    for elem, nodes in mesh.elements.items():
                        gmsh_elem_type = mesh.types[elem]
                        ccx_elem_type = rename_element(gmsh_elem_type)
                        if (mtype == ccx_elem_type) and (n1 in nodes) and (n2 in nodes): # we've got element
                            if nodes.index(n1) > nodes.index(n2):
                                n1, n2 = n2, n1 # n1 should have smaller index in element's nodes
                            fnum = element_face(ccx_elem_type, nodes, n1, n2)
                            F[fnum] += (elem, )
                            break

                # Write element sets grouped by faces
                for fnum, elems in F.items():
                    if len(elems):
                        ccx.write('*ELSET, ELSET={0}_S{1}\n'.format(setname, fnum))
                        for e in elems:
                            ccx.write('\t{0},\n'.format(e))

                # Write surface elements
                ccx.write('*SURFACE, name={0}, type=ELEMENT\n'.format(setname))
                for fnum, elems in F.items():
                    if len(elems):
                        ccx.write('\t{0}_S{1}, S{1}\n'.format(setname, fnum))

        print('Convertion OK')
