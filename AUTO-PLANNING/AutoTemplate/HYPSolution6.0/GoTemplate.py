# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 11:42:10 2020

@author: Henry Huang in Elekta Shanghai Co. Ltd.
"""
       

from HYP_TP_60 import Initialization_MON60
import sys

###############################################################################
###############   Arguments are passing from Monaco Script   ##################
###############################################################################

# pt_id = sys.argv[1]
# delivery_method = sys.argv[2]
# fx = sys.argv[3]
# prep_dose=sys.argv[4]

# #LABEL equals 'Site' in Monaco script
# LABEL=sys.argv[5]

# grid_dose = sys.argv[6]
# path = sys.argv[7]
# protocol_xlsx = sys.argv[8]
# PT_path = sys.argv[9]



pt_id = '0019'
delivery_method = 'VMAT'
fx = 28
prep_dose=61.6

# LABEL equals 'Site' in Monaco script
LABEL='NPC'

grid_dose = 3
path = 'C:/autotemplate/HYPSolution6.0'
protocol_xlsx = 'C:/auto template/XH protocol.xlsx'
PT_path = 'C:/Users/Public/Documents/CMS/FocalData/Installation/5~Clinic_XH/1~'




OAR_preferences = ['Brain Stem','Oral Cavity']


###############################################################################
#grid_dose = 3

# default file path 
#path = 'C:/autotemplate/HYPSolution5.51'

# absolute path for electronic protocol 
#protocol_xlsx = 'C:/autotemplate/XH protocol.xlsx'

# absolute path for structure name changes
#PT_path = 'C:/Users/Public/Documents/CMS/FocalData/Installation/Clinic_XH/1~'

print ('test by Yvonne')
X = Initialization_MON60(pt_id,
                       delivery_method,
                       fx,
                       prep_dose,
                       grid_dose,
                       path,
                       protocol_xlsx,
                       PT_path)
        
X.MAIN_GENERATE(LABEL)
