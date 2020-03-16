# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 11:42:10 2020

@author: Henry Huang in Elekta Shanghai Co. Ltd.
"""
       
#from GT_MONACO511_20200302 import HYP_Editor_MONACO511
from GT_MONACO_551 import Initialization_MON551

###############################################################################
#################################   GUI   #####################################
#pt_id = '003'
#,'003','004','005','006','0010','0016','0020'
#delivery_method = 'VMAT'
pt_id_list = ['002']
delivery_method_list = ['VMAT']
fx = 28
prep_dose=61.6
grid_dose = 2.5
###############################################################################


# default file path 
path = 'C:/auto template/HYPSolution5.51'

# absolute path for electronic protocol 
protocol_xlsx = 'C:/auto template/XH protocol.xlsx'

# absolute path for structure name changes
PT_path = 'C:/Users/Public/Documents/CMS/FocalData/Installation/5~Clinic_XH/1~'

for pt_id in pt_id_list:
    for delivery_method in delivery_method_list:
        X = Initialization_MON551(pt_id,
                       delivery_method,
                       fx,
                       prep_dose,
                       grid_dose,
                       path,
                       protocol_xlsx,
                       PT_path)
        
        X.MAIN_GENERATE('NPC')
###############################################################################