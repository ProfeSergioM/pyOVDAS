# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 16:06:15 2019
@author: loly

##############################################################PARA IMPORTAR
import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_SeismicProc_lib as sp

##############################################################

"""

import os

import numpy as np

import sys
sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
import ovdas_getfromdb_lib as func
import ovdas_SeismicProc_lib as sp


def DRc(amp,freq,dist):
    DRc=(10*amp/freq*dist)/(4*np.pi*np.sqrt(2))
    return np.round(DRc,decimals=2)