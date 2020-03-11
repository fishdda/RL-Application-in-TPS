# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 11:42:10 2020

@author: Henry Huang in Elekta Shanghai Co. Ltd.
"""

#from GT_MONACO511_20200302 import HYP_Editor_MONACO511
from GT_MONACO511_20200302 import Initialization

###############################################################################
#################################   GUI   #####################################
#pt_id = '003'
#delivery_method = 'VMAT'
pt_id_list = ['002','003','004','005','006','0010','0016','0020','0026','0028']
delivery_method_list = ['IMRT','VMAT']
fx = 28
prep_dose=61.6
grid_dose = 2.5
###############################################################################


# default file path 
path = 'C:/auto template/HYPSolution5.11'

# absolute path for electronic protocol 
protocol_xlsx = 'C:/auto template/XH protocol.xlsx'


for pt_id in pt_id_list:
    for delivery_method in delivery_method_list:
        X = Initialization(pt_id,
                       delivery_method,
                       fx,
                       prep_dose,
                       grid_dose,
                       path,
                       protocol_xlsx)
        
        X.MAIN_GENERATE()