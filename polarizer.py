#!/usr/bin/env python3
# polarizer.py - add Drude oscillators to LAMMPS data file.
# Agilio Padua <agilio.padua@univ-bpclermont.fr>, version 2015/04/08
# http://tim.univ-bpclermont.fr/apadua

"""
Add Drude oscillators to LAMMPS data file.

The format of file containing specification of Drude oscillators is:

# type  dm/u  dq/e  k/(kJ/molA2)  alpha/A3  thole
C3H     1.0   0.0   4184.0        2.051     2.6
...

where:
dm is the mass to put on the Drude particle (taken from its core),
dq is the charge to put on the Drude particle (taken from its core),
k is the garmonic force constant of the bond between Drude and core,
alpha is the polarizability,
thole is a Thole damping parameter.

A Drude particle is created for each atom in the LAMMPS data file
that corresponds to an atom type given in the Drude file.
Since LAMMPS uses numbers for atom types in the data file, a comment
after each line in the Masses section has to be introduced to allow
identification of the atom types within the force field database:

Masses

   1   12.011  # C3H
   2   12.011  # CTO
...


This script will add new atom types, new atoms, new bond types and
new bonds to the data file. It will also add a new seciton called
"Drudes" containing information about core-drude particle relations.

"""

import sys
import argparse
import random
from copy import deepcopy


# keywords of header and main sections (from data.py in Pizza.py)

hkeywords = ["atoms", "ellipsoids", "lines", "triangles", "bodies",
             "bonds", "angles", "dihedrals", "impropers",
             "atom types", "bond types", "angle types", "dihedral types",
             "improper types", "xlo xhi", "ylo yhi", "zlo zhi", "xy xz yz"]

skeywords = [["Masses", "atom types"],
             ["Pair Coeffs", "atom types"],
             ["Bond Coeffs", "bond types"], ["Angle Coeffs", "angle types"],
             ["Dihedral Coeffs", "dihedral types"],
             ["Improper Coeffs", "improper types"],
             ["BondBond Coeffs", "angle types"],
             ["BondAngle Coeffs", "angle types"],
             ["MiddleBondTorsion Coeffs", "dihedral types"],
             ["EndBondTorsion Coeffs", "dihedral types"],
             ["AngleTorsion Coeffs", "dihedral types"],
             ["AngleAngleTorsion Coeffs", "dihedral types"],
             ["BondBond13 Coeffs", "dihedral types"],
             ["AngleAngle Coeffs", "improper types"],
             ["Atoms", "atoms"], ["Ellipsoids", "ellipsoids"],
             ["Lines", "lines"], ["Triangles", "triangles"],
             ["Bodies", "bodies"],
             ["Bonds", "bonds"],
             ["Angles", "angles"], ["Dihedrals", "dihedrals"],
             ["Impropers", "impropers"], ["Velocities", "atoms"],
             ["Molecules", "atoms"], ["Drudes", "atoms"]]


def atomline(at):
    return "{0:7d} {1:7d} {2:4d} {3:8.4f} {4:13.6e} {5:13.6e} {6:13.6e} "\
           "{7}\n".format(at['n'], at['mol'], at['id'], at['q'],
                          at['x'], at['y'], at['z'], at['note'])

def massline(att):
    return "{0:4d} {1:8.3f}  # {2}\n".format(att['id'], att['m'], att['type'])

def bdtline(bdt):
    return "{0:4d} {1:12.6f} {2:12.6f}  {3}\n".format(bdt['id'], bdt['k'],
                                                      bdt['r0'], bdt['note'])

def bondline(bd):
    return "{0:7d} {1:4d} {2:7d} {3:7d}  # {4}\n".format(bd['n'], bd['id'],
                                            bd['i'], bd['j'], bd['note'])

def drudeline(at):
    return "{0:7d} {1:1d} {2:7d}\n".format(at['n'], at['dflag'], at['dd'])


# --------------------------------------


class Data:
    
    def __init__(self, datafile):
        '''read LAMMPS data file (from data.py in Pizza.py)'''

        # for extract method
        self.atomtypes = []
        self.bondtypes = []
        self.atoms = []
        
        self.nselect = 1

        f = open(datafile, "r")

        self.title = f.readline()
        self.names = {}

        headers = {}
        while 1:
            line = f.readline().strip()
            if len(line) == 0:
                continue
            found = 0
            for keyword in hkeywords:
                if keyword in line:
                    found = 1
                    words = line.split()
                    if keyword == "xlo xhi" or keyword == "ylo yhi" or \
                      keyword == "zlo zhi":
                        headers[keyword] = (float(words[0]), float(words[1]))
                    elif keyword == "xy xz yz":
                        headers[keyword] = \
                          (float(words[0]), float(words[1]), float(words[2]))
                    else:
                        headers[keyword] = int(words[0])
            if not found:
                break
    
        sections = {}
        while 1:
            found = 0
            for pair in skeywords:
                keyword, length = pair[0], pair[1]
                if keyword == line:
                    found = 1
                    if length not in headers:
                        raise RuntimeError("data section {} has no matching"\
                                           " header value".format(line))
                    f.readline()
                    list = []
                    for i in range(headers[length]):
                        list.append(f.readline())
                    sections[keyword] = list
            if not found:
                raise RuntimeError("invalid section {} in data"\
                                   " file".format(line))
            f.readline()
            line = f.readline()
            if not line:
                break
            line = line.strip()
        
        f.close()
        self.headers = headers
        self.sections = sections
        
    def write(self, filename):
        '''write out a LAMMPS data file (from data.py in Pizza.py)'''

        with open(filename, "w") as f:
            f.write(self.title + '\n')
            for keyword in hkeywords:
                if keyword in self.headers:
                    if keyword == "xlo xhi" or keyword == "ylo yhi" or \
                       keyword == "zlo zhi":
                        pair = [ str(p) for p in self.headers[keyword] ]
                        f.write(pair[0] + ' ' + pair[1] + ' ' + keyword + '\n')
                    elif keyword == "xy xz yz":
                        triple = [ str(t) for t in self.headers[keyword] ]
                        f.write(triple[0] + ' ' + triple[1] + ' ' + triple[2] +
                                ' ' + keyword + '\n')
                    else:
                        f.write(str(self.headers[keyword]) + ' ' +
                                keyword + '\n')
            for pair in skeywords:
                keyword = pair[0]
                if keyword in self.sections:
                    f.write("\n{}\n\n".format(keyword))
                    for line in self.sections[keyword]:
                        f.write(line)

    def extract(self):
        """extract atom IDs, bond types and atoms from data"""
        
        # extract atom IDs
        for line in self.sections['Masses']:
            tok = line.split()
            if len(tok) < 4:
                print("warning: missing type for atom ID " + tok[0])
                continue
            atomtype = {}
            atomtype['id'] = int(tok[0])
            atomtype['m'] = float(tok[1])
            atomtype['type'] = tok[3]
            self.atomtypes.append(atomtype)

        # extract bond types
        # for line in self.sections['Bond Coeffs']:
        #     tok = line.split()
        #     bondtype = {}
        #     bondtype['id'] = int(tok[0])
        #     bondtype['k'] = float(tok[1])
        #     bondtype['r0'] = float(tok[2])
        #     note = ''
        #     for i in range(3, len(tok)):
        #         note += tok[i] + ' '
        #     bondtype['note'] = note.strip()
        #     self.bondtypes.append(bondtype)

        # extract atom registers
        for line in self.sections['Atoms']:
            tok = line.split()
            atom = {}
            atom['n'] = int(tok[0])
            atom['mol'] = int(tok[1])
            atom['id'] = int(tok[2])
            atom['q'] = float(tok[3])
            atom['x'] = float(tok[4])
            atom['y'] = float(tok[5])
            atom['z'] = float(tok[6])
            note = ''
            for i in range(7, len(tok)):
                note += tok[i] + ' '
            atom['note'] = note.strip()
            self.atoms.append(atom)

    def polarize(self, drude):
        """add Drude particles"""

        self.extract()

        natom = self.headers['atoms']
        nbond = self.headers['bonds']
        nattype = self.headers['atom types']
        nbdtype = self.headers['bond types']

        # create new atom types (IDs) for Drude particles and modify cores
        newattypes = []
        for att in self.atomtypes:
            att['dflag'] = 0
            for ddt in drude.types:
                if ddt['type'] == att['type']:
                    nattype += 1
                    newid = {}
                    newid['id'] = ddt['id'] = nattype
                    newid['m'] = ddt['dm']
                    att['m'] -= ddt['dm']
                    # label drude particles and cores
                    att['dflag'] = 1
                    newid['dflag'] = 2
                    newid['type'] = att['type'] + ' DP'
                    att['type'] += ' DC'
                    ddt['type'] += ' DC'
                    newattypes.append(newid)
                    break

        self.headers['atom types'] += len(newattypes)
        self.sections['Masses'] = []
        for att in self.atomtypes + newattypes:
            self.sections['Masses'].append(massline(att))

        # create new bond types for core-drude bonds
        newbdtypes = []
        for att in self.atomtypes:
            for ddt in drude.types:
                if ddt['type'] == att['type']:
                    nbdtype += 1
                    newbdtype = {}
                    newbdtype['id'] = ddt['bdid'] = nbdtype
                    newbdtype['k'] = ddt['k']
                    newbdtype['r0'] = 0.0
                    newbdtype['note'] = '# ' + ddt['type'] + '-DP'
                    newbdtypes.append(newbdtype)
                    break

        self.headers['bond types'] += len(newbdtypes)
        for bdt in newbdtypes:
            self.sections['Bond Coeffs'].append(bdtline(bdt))

        # create new atoms for Drude particles and new bonds with their cores
        random.seed(123)
        newatoms = []
        newbonds = []
        for atom in self.atoms:
            atom['dflag'] = 0            # 1: core, 2: drude, 0: other
            atom['dd'] = 0               # partner drude or core
            for att in self.atomtypes:
                if att['id'] == atom['id']:
                    break
            for ddt in drude.types:
                if ddt['type'] == att['type']:
                    natom += 1
                    newatom = deepcopy(atom)
                    newatom['n'] = natom
                    newatom['id'] = ddt['id']
                    newatom['q'] = ddt['dq']
                    newatom['note'] = atom['note'] + ' DP'
                    newatom['dflag'] = 2
                    newatom['dd'] = atom['n']
                    
                    # avoid superposition of cores and Drudes
                    newatom['x'] += 0.1 * (random.random() - 0.5)
                    newatom['y'] += 0.1 * (random.random() - 0.5)
                    newatom['z'] += 0.1 * (random.random() - 0.5)
                    
                    newatoms.append(newatom)
                    atom['q'] -= ddt['dq']
                    atom['dflag'] = 1
                    atom['dd'] = natom
                    atom['note'] += ' DC'
                                
                    nbond += 1
                    newbond = {}
                    newbond['n'] = nbond
                    newbond['id'] = ddt['bdid']
                    newbond['i'] = atom['n']
                    newbond['j'] = newatom['n']
                    newbond['note'] = ddt['type'] + '-DP'
                    newbonds.append(newbond) 
                    break
            
        self.headers['atoms'] += len(newatoms)
        self.headers['bonds'] += len(newbonds)
        self.sections['Atoms'] = []
        for atom in self.atoms + newatoms:
            self.sections['Atoms'].append(atomline(atom))        
        for bond in newbonds:                  
            self.sections['Bonds'].append(bondline(bond))

        self.sections['Drudes'] = []
        for atom in self.atoms + newatoms:
            self.sections['Drudes'].append(drudeline(atom))

        # update list of atom IDs
        for att in newattypes:
            self.atomtypes.append(att)

            
    def thole(self, drude, outfile, thole = 2.6, cutoff = 12.0):
        """print lines for pair_style thole"""

        dfound = False
        for att in self.atomtypes:
            if att['dflag'] == 2:
                dfound = True
                break
        if not dfound:
            return

        print("pair_style hybrid/overlay ... coul/long {0:.1f} "\
              "thole {1:.3f} {0:.1f}\n".format(cutoff, thole))

        print("fix Drudes all property/atom i_drudetype i_drudeid ghost yes")
        print("read_data {0} fix Drude null Drudes\n".format(outfile))

        # only Coulomb interactions between any atoms and drude particles
        print("pair_coeff  * {0}* coul/long".format(att['id']))

        # Thole parameters for I,J pairs
        ifound = False
        for atti in self.atomtypes:
            itype = atti['type'].split()[0]
            for ddt in drude.types:
                dtype = ddt['type'].split()[0]
                if dtype == itype:
                    alphai = ddt['alpha']
                    tholei = ddt['thole']
                    ifound = True
                    break
            jfound = False
            for attj in self.atomtypes:
                if attj['id'] < atti['id']:
                    continue
                jtype = attj['type'].split()[0]
                for ddt in drude.types:
                    dtype = ddt['type'].split()[0]
                    if dtype == jtype:
                        alphaj = ddt['alpha']
                        tholej = ddt['thole']
                        jfound = True
                        break
                if ifound and jfound:
                    alphaij = (alphai + alphaj) / 2.0
                    tholeij = (tholei * tholej)**0.5
                    print("pair_coeff {0:2} {1:2} thole {2:7.3f} "\
                          "{3:7.3f}".format(atti['id'], attj['id'],
                                            alphaij, tholeij))
                jfound = False
            ifound = False
        print("")

        gcores = gdrudes = ""
        for att in self.atomtypes:
            if att['dflag'] == 1:
                gcores += " {0}".format(att['id'])
            if att['dflag'] == 2:
                gdrudes += " {0}".format(att['id'])
        print("group CORES type" + gcores)
        print("group DRUDES type" + gdrudes)
        print("")

# --------------------------------------

kcal =  4.184                           # kJ
eV   = 96.485                           # kJ/mol
fpe0 =  0.000719756                     # (4 Pi eps0) in e^2/(kJ/mol A)


class Drude:
    """specification of drude oscillator types"""

    def __init__(self, drudefile, polar = '', positive = False, metal = False):
        self.types = []
        with open(drudefile, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or len(line) == 0:
                    continue
                tok = line.split()
                drude = {}
                drude['type'] = tok[0]
                drude['dm'] = float(tok[1])
                dq = float(tok[2])
                k = float(tok[3])
                drude['alpha'] = alpha = float(tok[4])
                drude['thole'] = float(tok[5])

                if polar == 'q':
                    dq = (fpe0 * k * alpha)**0.5
                elif polar == 'k':
                    k = dq*dq / (fpe0 * alpha)
                
                if positive:
                    drude['dq'] = abs(dq)
                else:
                    drude['dq'] = -abs(dq)

                if metal:
                    drude['k'] = k / (2.0 * eV)
                else:
                    drude['k'] = k / (2.0 * kcal)
                    
                self.types.append(drude)


# --------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description = 'Add Drude dipole polarization to LAMMPS data file')
    parser.add_argument('-d', '--drudeff', default = 'drude.ff',
                        help = 'Drude parameter file (default: drude.ff)')
    parser.add_argument('-t', '--thole', type = float, default = 2.6,
                        help = 'Thole damping parameter (default: 2.6)')
    parser.add_argument('-c', '--cutoff', type = float, default = 12.0,
                        help = 'distance cutoff/A (default: 12.0)')
    parser.add_argument('-q', '--qcalc', action = 'store_true',
                        help = 'Drude charges calculated from polarisability '\
                        '(default: q value from parameter file)')
    parser.add_argument('-k', '--kcalc', action = 'store_true',
                        help = 'Drude force constants calculated from '\
                        'polarisability (default: k value from parameter file)')
    parser.add_argument('-p', '--positive', action = 'store_true',
                        help = 'Drude particles have positive charge '\
                        '(default: negative charge)')
    parser.add_argument('-m', '--metal', action = 'store_true',
                        help = 'LAMMPS metal units (default: real units)')
    parser.add_argument('infile', help = 'input LAMMPS data file')
    parser.add_argument('outfile', help = 'output LAMMPS data file')
    args = parser.parse_args()

    if args.qcalc:
        polar = 'q'
    elif args.kcalc:
        polar = 'p'
    else:
        polar = ''
        
    data = Data(args.infile)
    drude = Drude(args.drudeff, polar, args.positive, args.metal)
    data.polarize(drude)
    data.write(args.outfile)
    print("# Copy the lines below into the LAMMPS input file")
    print("# Adapt the pair_style line as needed\n")
    data.thole(drude, args.outfile, args.thole, args.cutoff)
                                    
if __name__ == '__main__':
    main()