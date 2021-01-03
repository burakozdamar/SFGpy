#!/usr/bin/env/python3

import re
import sys
import numpy as np

sys.path.append('..')

ff = sys.argv[1]
gg = "py_pos_recentered.xyz"

from utils.xyz_utils import read_xyz
from collections import Counter,namedtuple
from itertools import cycle, count, groupby

mass = {'H': 1.00794,'x':0,'C':12.0107,'O':15.9994,'Si':28.0855,'Cl':35.4527,'K':39.0983,'Al':26.981539}
pbc_ = np.array([13.386,13.286,85])


def memoize_mass(ff):
  mass_arr = []
  with open(ff) as f:
    xyz = read_xyz(f)
    atomtypes = xyz.atomtypes
  # silicons or alums coming later from C
  if 'C' in atomtypes:
    mass_arr = np.array([mass[atom] if atom == 'Si' else 0 for atom in atomtypes])
  return mass_arr, atomtypes

mass_arr, atomtypes = memoize_mass(ff)

def translate(arr1,arr2):
  return arr1-arr2

def calcul_CM(xyz):
  coords = xyz.coords
  com = np.average(coords, axis=0, weights=mass_arr)
  t = pbc(translate(coords, com))
  return t

def pbc(arr):
  arr = np.where(arr < -pbc_/2, arr+pbc_, arr)
  arr = np.where(arr >  pbc_/2, arr-pbc_, arr)
  return arr 

def write_xyz(fout, coords, title="", atomtypes=("A",)):
  fout.write("%d\n%s\n" % (coords.size / 3, title))
  for x, atomtype in zip(coords.reshape(-1, 3), cycle(atomtypes)):
    #fout.write("%s %.8g %.8g %.8g\n" % (atomtype, x[0], x[1], x[2]))
    fout.write('{:2s} {:>12.6f} {:>12.6f} {:>12.6f}\n'.format(atomtype, x[0], x[1], x[2]))

def read_boxdata():
  with open("../warehouse/BOXDATA") as f:
    ll = [l.strip() for l in f.readlines()]
    res = [list(sub) for ele, sub in groupby(ll, key = bool) if ele] 
    k = [item[0] for item in res]
    v = [item[1:] for item in res]
    v = [[i.split(' ') if len(i.split(' '))>1 else i for i in sl] for sl in v]
    return dict(zip(k,v))

def open_file(ff):

  with open(ff) as f:
    with open(gg,'w') as g:
      for i in count(1):
        try:
          xyz = read_xyz(f)
          if i%1000==0: print(f"{i}")
          t = calcul_CM(xyz)
          write_xyz(g, t, title="", atomtypes=atomtypes) 
          #write_to_file(g,t)
        except ValueError as e:
          print("DONE")
          break
  
open_file(ff)
read_boxdata()
