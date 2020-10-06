#!/usr/bin/env python
# coding: utf-8

import os
from itertools import islice
import numpy as np
#os.system("cp data.inpt data_bulk.inpt")
#os.system("cp runtime.inpt runtime_bulk.inpt")

name = []
typ = []
file = []
count = []
mass_elec = []
width = []
magnitude = []
pot_typ = []
pot1 = []
pot2 = []
pot3 = []
pot4 = []
pot5 = []
pot6 = []
bohr = 0.529177
with open('elec.inpt') as f:
    nb_elec = f.readline()
    counter = int(nb_elec)
    elec_type = f.readline()
    for i in range(int(nb_elec)):
        temp = f.readline()
        name.append(temp.split()[0])
        typ.append(temp.split()[1])
        if typ[i] == 'wall':
            counter = counter - 1
        count.append(int(temp.split()[2]))
        mass_elec.append(temp.split()[3])
        width.append(temp.split()[4])
        magnitude.append(temp.split()[5])
        pot_typ.append(temp.split()[6])
        if pot_typ[i] == "lj":
            pot1.append(float(temp.split()[7]))
            pot2.append(float(temp.split()[8]))
        if pot_typ[i] == "ft":
            pot1.append(float(temp.split()[7]))
            pot2.append(float(temp.split()[8]))
            pot3.append(float(temp.split()[9]))
            pot4.append(float(temp.split()[10]))
            pot5.append(float(temp.split()[11]))
            pot6.append(float(temp.split()[12]))
    elec_charges = f.readline()
    neutrality = f.readline()
    compute_force = f.readline()
natom_elec = 0
natom_add = 0

for i in range(int(nb_elec)):
    if typ[i] == 'elec':
        natom_elec += int(count[i]) 

    natom_add += int(count[i])
    
out = open("runtime.inpt", "w")  
lj = False
ft = False
species = []
mass = []
with open("runtime_bulk.inpt", "r") as run:
    
    for line in run:
        if (line.lstrip()).startswith("molecules"):
            break
        else :
            out.write("{0}".format(line))

        if (line.lstrip()).startswith("name"):
            species.append(line.split()[1])
        if (line.lstrip()).startswith("mass"):
            mass.append(line.split()[1])
    for i in range(int(nb_elec)):  
        if typ[i] == 'elec':
            out.write("  species_type\n")
            out.write("    name {0}\n".format(name[i]))
            out.write("    count {0}\n".format(count[i]))
            out.write("    charge gaussian {0}  {1}\n".format(width[i], magnitude[i]))
            out.write("    mass {0}\n".format(mass_elec[i]))
            out.write("    mobile False\n\n")
        if typ[i] == 'wall':
            out.write("  species_type\n")
            out.write("    name {0}\n".format(name[i]))
            out.write("    count {0}\n".format(count[i]))    
            out.write("    charge point 0.0\n")
            out.write("    mass {0}\n".format(mass_elec[i]))
            out.write("    mobile False\n\n")
                
    out.write("molecules\n")   
    for line in run:
        if (line.lstrip()).startswith("interactions"):
            break
        else :
            out.write("{0}".format(line))
            
    out.write("electrodes\n\n")        
    for i in range(counter):
        out.write("  electrode_type\n")
        out.write("  name   {0}\n".format(name[i]))
        out.write("  species   {0}\n".format(name[i]))
        out.write("  potential   0\n")
        out.write("  #piston 0.0 1\n")
        out.write("  #thomas_fermi_length 0.0\n")
        out.write("  #voronoi_volume ***\n\n")
    out.write("  {0}".format(elec_charges))
    out.write("  {0}".format(neutrality))
    out.write("  {0}\n".format(compute_force))
    
    out.write("interactions\n")
    for line in run:
        if (line.lstrip()).startswith("coulomb"):
            out.write("{0}".format(line))
            
        if (line.lstrip()).startswith("lennard-jones"):
            lj = True
            out.write("\n{0}".format(line))
            out.write("    #lj_3D_tail_correction\n")
            out.write("     lj_rcut XXX\n")
        if (line.lstrip()).startswith("lj_pair"):
            out.write("{0}".format(line))
                
        if (line.lstrip()).startswith("fumi-tosi"):
            ft = True
            out.write("\n{0}".format(line))
            out.write("     #ft_3D_pressure_tail_correction\n")
            out.write("      ft_rcut XXX\n")   
        if (line.lstrip()).startswith("ft_pair"):
            out.write("{0}".format(line))
            
    for i in range(int(nb_elec)):   
        if lj:
            out.write("     lj_pair  {0:4s} {1:4s}  {2}   {3}\n".format(name[i], name[i],
                        pot1[i], pot2[i]))
        if ft:
            out.write("     ft_pair  {0:4s} {1:4s}  {2}  {3}  {4}  {5}  {6}  {7}\n".format(
                           name[i], name[i], pot1[i], pot2[i], pot3[i], pot4[i], pot5[i], pot6[i]))


with open("runtime_bulk.inpt", "r") as run:
    for line in run:
        if (line.lstrip()).startswith("lj_rule"):
            out.write("{0}".format(line))
        if (line.lstrip()).startswith("ft_rule"):
            out.write("{0}".format(line))

        if (line.lstrip()).startswith("damping"):
            out.write("\n{0}".format(line)) 
            
        if (line.lstrip()).startswith("tt_pair"):
            out.write("{0}".format(line))
    for i in range(int(nb_elec)):
        for j in range(len(species)):
            if float(mass[j]) > 2.0:
                out.write("     tt_pair   {0:4s}   {1:4s}     2.0000000000000000        4"
                       "       1.0000000000000000\n".format(name[i], species[j]))

    out.write('\n')
    out.write('output\n')
    out.write(' default 1\n')

natom = 0
natom_tot = 0

out2 = open("data.inpt", "w")
with open("data_backk.inpt", "r") as data:

    head = list(islice(data, 2))
    for n in range(2):
       out2.write(str(head[n]))
    ligne = data.readline()
    natom = int(ligne.split()[1])
    natom_tot = natom + natom_add
    out2.write("num_atoms                      {0}\n".format(natom_tot))
    out2.write("num_electrode_atoms              {0}\n".format(natom_elec))

    head = list(islice(data, 4))
    for n in range(1,3):
        out2.write(str(head[n]))
    out2.write("  # coordinates :      {0} species - step  0\n".format(natom_tot))

    atname, atx, aty, atz = np.loadtxt(data, dtype='str', unpack= True)
    atx = atx.astype(float)
    aty = aty.astype(float)
    atz = atz.astype(float)

    bulk_minz = np.amin(atz)
    bulk_maxz = np.amax(atz)


if elec_type == 'planar\n':   
    elec1x, elec1y, elec1z = np.loadtxt('planar_elec_ua', unpack= True)

if elec_type == 'porous\n':
    elec1x, elec1y, elec1z = np.loadtxt('porous_left_ua', unpack= True)
    elec2x, elec2y, elec2z = np.loadtxt('porous_right_ua', unpack= True)

elec_thick = (np.amax(elec1z) - np.amin(elec1z))

for n in range(len(atx)):
    atz[n] = atz[n]-bulk_minz + elec_thick + 6.0 + 1.10
    out2.write(" {0}    {1}  {2}  {3}\n".format(atname[n], atx[n], aty[n], atz[n]))

if elec_type == 'planar\n':
   for i in range(int(nb_elec)):
       if i == 1:
          for j in range(int(count[i])):
              out2.write(" {0}    {1}  {2}  {3}\n".format(
                      name[i], elec1x[j], elec1y[j], elec1z[j]+elec_thick+bulk_maxz+13.10))
       else:
           for j in range(int(count[i])):
               out2.write(" {0}    {1}  {2}  {3}\n".format(
                       name[i], elec1x[j], elec1y[j], elec1z[j]+1.10))

if elec_type == 'porous\n':
   for i in range(len(count)):
       if i == 0:
           for n in range(int(count[i]/2)):
                   out2.write(" {0}    {1}  {2}  {3}\n".format(
                      name[i], elec1x[n], elec1y[n], elec1z[n]+1.10))
           for n in range(int(count[i]/2), count[i]):
                   m = n - int(count[i]/2)
                   out2.write(" {0}    {1}  {2}  {3}\n".format(
                           name[i], elec2x[m], elec2y[m], elec2z[m]+elec_thick+bulk_maxz+13.10))

       for n in range(count[i]):
           m = n + int(count[0]/2)
           if i == 1:        
                out2.write(" {0}    {1}  {2}  {3}\n".format(
                          name[i], elec1x[m], elec1y[m], elec1z[m]+1.10))
           if i == 2:
                out2.write(" {0}    {1}  {2}  {3}\n".format(
                          name[i], elec1x[m], elec1y[m], elec1z[m]+elec_thick+bulk_maxz+13.10))

 
