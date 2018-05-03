import sys

energies={'0':40, '-8000':32.5, '-12000':24.0, '-16000':12.0, '-20000':5.9,'-24000':3.1,'-28000':1.5, '-18000':9,'-22000':4.5, '-19000':7.5, '-14000':18.0,'-15000':15.0,'-13000':21.0,'-10000':28.0}

area=680*1e-4*547*1e-4 #Microns to cm

energy=energies[sys.argv[1]]
energy*=1e-3 #Micro Joules to mJ

print "Flux in mJ/cm2", energy/area 
