# -*- coding: utf-8 -*-
# © Ihor Mirzov, UJV Rez, March 2019

"""
    Convert Gmsh .inp-file to CalculiX .inp-file.
    Run with command:
        python3 gmsh2ccx.py -g gmsh3.inp -c ccx3.inp -e S3 -ns 1
        python3 gmsh2ccx.py -g gmsh4.inp -c ccx4.inp -e S4 -ns 1
"""

import sys, argparse
from INPParser import Mesh

# Converts element types from gmsh to ccx
def rename_element(gmsh_elem_type):
    dic =\
        {
            'C1D2':'B31', # 2 node beam
            'T3D2':'B31', # 2 node beam
            'C1D3':'B32', # 3 node beam
            'T3D3':'B32', # 3 node beam
            'C2D3':'S3', # 3 node shell
            'CPS3':'S3', # 3 node shell
            'C2D4':'S4', # 4 node shell
            'CPS4':'S4', # 4 node shell
        }
    try:
        ccx_elem_type = dic[gmsh_elem_type]
    except:
        ccx_elem_type = gmsh_elem_type
        print('Error converting element type', gmsh_elem_type)
    return ccx_elem_type

# Element's edge number
def edge_number(etype, elem_nodes, n1, n2):
    # See Calculix 2.15 documentation, chapter "7.114 *SURFACE"

    # Triangular and quadrilateral shell elements
    if etype in ('S3', 'S4'):
        """
            tri (S3):
                Edge 3: 1-2
                Edge 4: 2-3
                Edge 5: 3-1
            quad (S4):
                Edge 3: 1-2
                Edge 4: 2-3
                Edge 5: 3-4
                Edge 6: 4-1
        """
        for edge in range(len(elem_nodes)-1):
            if elem_nodes[edge]==n1 and elem_nodes[edge+1]==n2:
                return edge+3
        return len(elem_nodes)+2

    # Triangular and quadrilateral plane stress, plane strain and axisymmetric elements
    if etype in ('CPS3', 'CPS4', 'CPE3', 'CPE4'):
        """
            tri (S3):
                Edge 1: 1-2
                Edge 2: 2-3
                Edge 3: 3-1
            quad (S4):
                Edge 1: 1-2
                Edge 2: 2-3
                Edge 3: 3-4
                Edge 4: 4-1
        """
        for edge in range(len(elem_nodes)-1):
            if elem_nodes[edge]==n1 and elem_nodes[edge+1]==n2:
                return edge+1
        return len(elem_nodes)

if __name__ == '__main__':

    # Command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("--gmsh", "-g",
                        help="Gmsh .inp file name",
                        type=str, default='gmsh3.inp')
    parser.add_argument("--ccx", "-c",
                        help="Calculix .inp file name",
                        type=str, default='ccx3.inp')
    parser.add_argument("--etype", "-e",
                        help="Element type: S3 or S4",
                        type=str, default='S3')
    parser.add_argument("--nodesets", "-ns",
                        help="Specify whether to output node sets: 0 or 1",
                        type=int, default=0)
    args = parser.parse_args()


    mesh = Mesh(args.gmsh) # parse mesh, define nodes, elements and centroids

    # Process lines of gmsh-file and write ccx-file
    with open(args.ccx, 'w') as ccx:

        # Nodes block
        if len(mesh.nodes):
            ccx.write('*NODE, NSET=ALL\n') # append name of the node set
            for k,v in mesh.nodes.items():
                coords = str(v)[1:-1]
                # if not '0.0, 0.0, 0.0' in coords:
                ccx.write('\t{0}, {1}\n'.format(k, coords)) # v without braces

        # Elements block
        if len(mesh.elements):
            ccx.write('*ELEMENT, type=' + args.etype + ', ELSET=ALL\n')
            for elem, nodes in mesh.elements.items():
                gmsh_elem_type = mesh.types[elem]
                ccx_elem_type = rename_element(gmsh_elem_type)
                if args.etype == ccx_elem_type: # save only needed elements
                    ccx.write('\t{0}, {1}\n'.format(elem, str(nodes)[1:-1])) # v without braces

        # Process node and element sets and define element edges
        for setname in mesh.esets.keys(): # ['LEFT', 'RIGHT']
            # Write node set
            if args.nodesets:
                ccx.write('*NSET, NSET={0}\n'.format(setname))
                for e in mesh.esets[setname]:
                    for n in mesh.elements[e]:
                        ccx.write('\t{0},\n'.format(n))

            # Elements of type 'args.etype', grouped by edge numbers
            E = {} # {'edge1':(elements1), 'edge2':(elements2), }
            for edge in range(6): # there is no 2D element with edge number > 6
                E[edge+1] = () # in the ccx inp.-file edge number should start from 1
            for sbe in mesh.esets[setname]: # beam elements composing free surface
                n1 = mesh.elements[sbe][0] # node 1 of surface beam element
                n2 = mesh.elements[sbe][1] # node 2 of surface beam element

                # Find 'args.etype' element by the nodes n1, n2
                for elem, nodes in mesh.elements.items():
                    gmsh_elem_type = mesh.types[elem]
                    ccx_elem_type = rename_element(gmsh_elem_type)
                    if (args.etype == ccx_elem_type) and (n1 in nodes) and (n2 in nodes): # we've got element
                        if nodes.index(n1) > nodes.index(n2):
                            n1, n2 = n2, n1 # n1 should have smaller index in element's nodes
                        edge = edge_number(ccx_elem_type, nodes, n1, n2)
                        E[edge] += (elem, )
                        break

            # Write element sets grouped by edges
            for edge, elems in E.items():
                if len(elems):
                    ccx.write('*ELSET, ELSET={0}_S{1}\n'.format(setname, edge))
                    for e in elems:
                        ccx.write('\t{0},\n'.format(e))

            # Write surface elements
            ccx.write('*SURFACE, name={0}, type=ELEMENT\n'.format(setname))
            for edge, elems in E.items():
                if len(elems):
                    ccx.write('\t{0}_S{1}, S{1}\n'.format(setname, edge))

        print('Convertion OK')
