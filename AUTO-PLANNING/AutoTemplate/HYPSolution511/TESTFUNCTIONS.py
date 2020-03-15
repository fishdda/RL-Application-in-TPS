# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 15:21:34 2020

@author: xhuae08006
"""

from GT_MONACO511_20200302 import Initialization

###############################################################################
#################################   GUI   #####################################
pt_id = '003'
delivery_method = 'VMAT'
fx = 28
prep_dose=61.6
grid_dose = 2.5
###############################################################################


# default file path 
path = 'C:/auto template/HYPSolution5.11'

# absolute path for electronic protocol 
protocol_xlsx = 'C:/auto template/XH protocol.xlsx'




X = Initialization(pt_id,
               delivery_method,
               fx,
               prep_dose,
               grid_dose,
               path,
               protocol_xlsx)

X.MAIN_GENERATE()