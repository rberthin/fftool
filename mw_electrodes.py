#!/usr/bin/env python
# coding: utf-8

# import os
# os.system("cp data.inpt data_backk.inpt")
# os.system("cp runtime.inpt runtime_backk.inpt")


name = []
typ = []
file = []
count = []
mass = []
width = []
magnitude = []
pot_typ = []
pot1 = []
pot2 = []
pot3 = []
pot4 = []
pot5 = []
pot6 = []

with open('elec.inpt') as f:
    nb_elec = f.readline()
    counter = int(nb_elec)
    for i in range(int(nb_elec)):
        temp = f.readline()
        name.append(temp.split()[0])
        typ.append(temp.split()[1])
        if typ[i] == 'wall':
            counter = counter - 1
        count.append(temp.split()[2])
        mass.append(temp.split()[3])
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

        temp = f.readline()
        file.append(temp.split()[0])
    elec_charges = f.readline()
    neutrality = f.readline()
    compute_force = f.readline()

out = open("runtime.inpt", "w")  
lj = False
ft = False
species = []

with open("runtime_backk.inpt", "r") as run:
    
    for line in run:
        if (line.lstrip()).startswith("molecules"):
            break
        else :
            out.write("{0}".format(line))

        if (line.lstrip()).startswith("name"):
            species.append(line.split()[1])
    print(species)        
    for i in range(int(nb_elec)):  
        if typ[i] == 'elec':
            out.write("  species_type\n")
            out.write("    name {0}\n".format(name[i]))
            out.write("    count {0}\n".format(count[i]))
            out.write("    charge gaussian {0}  {1}\n".format(width[i], magnitude[i]))
            out.write("    mass {0}\n".format(mass[i]))
            out.write("    mobile False\n\n")
        if typ[i] == 'wall':
            out.write("  species_type\n")
            out.write("    name {0}\n".format(name[i]))
            out.write("    count {0}\n".format(count[i]))    
            out.write("    charge point 0.0\n")
            out.write("    mass {0}\n".format(mass[i]))
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


# In[45]:


with open("runtime_backk.inpt", "r") as run:
    for line in run:
        if (line.lstrip()).startswith("lj_rule"):
            out.write("{0}".format(line))
        if (line.lstrip()).startswith("ft_rule"):
            out.write("{0}".format(line))

        if (line.lstrip()).startswith("damping"):
            out.write("\n{0}".format(line)) 
            
        if (line.lstrip()).startswith("tt_pair"):
            out.write("{0}".format(line))
               


# In[ ]:




