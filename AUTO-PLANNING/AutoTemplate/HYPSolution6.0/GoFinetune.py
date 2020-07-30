# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 11:42:10 2020

@author: Henry Huang in Elekta Shanghai Co. Ltd.
"""
       

from HYP_TP_60 import Initialization_MON60
import sys
import pandas as pd

pt_id = sys.argv[1]
delivery_method = sys.argv[2]
fx = sys.argv[3]
prep_dose=sys.argv[4]
#LABEL equals 'Site' in Monaco script
LABEL=sys.argv[5]
grid_dose = sys.argv[6]
path = sys.argv[7]
protocol_xlsx = sys.argv[8]
PT_path = sys.argv[9]
planname = sys.argv[10]
iter = sys.argv[11]


#pt_id = '003'
#delivery_method = 'VMAT'
#fx = 28
#prep_dose= 61.6
#LABEL equals 'Site' in Monaco script
#LABEL= 'NPC'
#grid_dose = 3 # mm
#path = 'C:/autotemplate/HYPSolution6.0'
#protocol_xlsx = 'C:/autotemplate/XHprotocol.xlsx'
#PT_path = 'C:/Users/Public/Documents/CMS/FocalData/Installation/Clinic_XH/1~'
#planname = '05291023'
#iter = '0'


OAR_preferences = ['Brain Stem','Oral Cavity']

X = Initialization_MON60(pt_id,
                       delivery_method,
                       fx,
                       prep_dose,
                       grid_dose,
                       path,
                       protocol_xlsx,
                       PT_path)

protocol_dict = X.extract_xlsx(pt_id)  # protocol_dict store the constraints in protocol

#DVH = X.csv_read_to_dvh() # DVH Raw Data Struct
#dvh_inf = X.DVH_MAX_MEAN(DVH) # Dmean and Dmax extracted

# need to change if Yvonne could provide the modified version of DVH Statistics table 
#dvh_stat_calc = X.DVH_Stat_Extract(dvh_inf,DVH) 



###############################################################################
###############################################################################
######### Monaco TPS load Treatment Template into GUI #########################
######### Start Phase 1 Optimization Fleunce Map Optimization #################
######### Monaco TPS export DVH.csv and current template.hyp file #############
###############################################################################
###############################################################################

# absolute DVH csv file path
DVH_JSON ='C:/autotemplate/dvh/DVHStatistics_' + pt_id + '_' + planname + '_' + str(iter) + '.json'

# temporary hyp file path
hyp_path = 'C:/autotemplate/temporary.hyp'

# updated hyp file path
#FMO1_hyp_path_updated = 'C:/Users/Public/Documents/CMS/FocalData/MonacoTemplates'
FMO1_hyp_path_updated = 'C:/autotemplate/'

# load treatment plan template (raw data structure)
# strt_fun,strt_index,line = X.read_template()    # need to update 
line,strt_index,IMRT_TABLE = X.Read_Template_60()
print(IMRT_TABLE)

# read DVH Statistics Information from Monaco TPS
dvh_stat_calc = X.DVH_Stat_Extract_JSON(DVH_JSON)


# start Fine Tunning Template file
New_IMRT_CONSTRAINT,Old_IMRT_CONSTRAINT = X.MAIN_Tune_TP_60(LABEL,
                   DVH_JSON,
                   OAR_preferences,
                   pt_id,
                   delivery_method)

IMRT_cosntraints_path = 'C:/autotemplate/IMRTconstraints/' + pt_id + '_' + planname + "_" + iter + '.csv'
New_IMRT_CONSTRAINT.to_csv(IMRT_cosntraints_path, encoding='utf-8')

path = 'C:/GitFolder/RL-Application-in-TPS/AUTO-PLANNING/AutoTemplateTuning/projects/dose prediction/DATA'
