# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 11:42:10 2020

@author: xhuae08006
"""

from GT_MONACO511 import HYP_Editor_MONACO511
from shutil import copyfile
import os
import sys

###############################################################################
#################################   GUI   #####################################
pt_id = '0028'
delivery_method = 'VMAT'
fx = 28
prep_dose=61.6
###############################################################################




# default file path 
path = 'C:/auto template/HYPSolution5.11'

# absolute path for electronic protocol 
protocol_xlsx = 'C:/auto template/XH protocol.xlsx'

# original template folder and file path
hyp_element_path = os.path.join(path,'hyp_element511.txt')
demo_xml_path = os.path.join(path,'demo_dosenormsettings.xml')
absolute_path = os.path.join(path,'remaining4files')

# updated new template folder and file path
updated_template_path = os.path.join(path,pt_id)
output_xml_path = os.path.join(updated_template_path,pt_id+delivery_method+'.dosenormsettings.xml')
hyp_path_new = os.path.join(updated_template_path,pt_id+delivery_method+'.hyp')

# once ct image was loaded, check the structure name with protocol
contourname_path = 'C:/Users/Public/Documents/CMS/FocalData/Installation/5~Clinc_XH/1~'+ pt_id + '/1~CT1/contournames'
new_contourname_path = 'C:/Users/Public/Documents/CMS/FocalData/Installation/5~Clinc_XH/1~'+ pt_id + '/1~CT1/contournames1'
NAMING_LIB = {'TARGET_NAME_LIB':{'gtv','ctv','ptv','pgtv','pctv'},
              'OARs_NAME_LIB_HN':
                  {'Level1':{'spinal cord','brain stem','stem','cord','prv','prv bs','scprv','prv sc'},
                   'Level2':{'optical nerve r','optical nerve l','optical nerve',
                             'lens r','lens l','lens',
                             'eye r','eye l','eye',
                             'brain','optical chiasm'
                             }}}

# load HYP editor from editor_Monaco511
HYP = HYP_Editor_MONACO511(hyp_element_path,
                 protocol_xlsx,
                 demo_xml_path,
                 output_xml_path,
                 contourname_path,
                 NAMING_LIB,
                 hyp_path_new,
                 updated_template_path,
                 new_contourname_path)
HYP.mkdir()
# read protocol to dict
protocol_dict = HYP.extract_xlsx(pt_id)

# read hyp elements into RAM
ele = HYP.Read_HYP_element()
print(ele)

# generate new hyp file
updated_template = HYP.hyp_solution_XHTOMO_HEADNECK(grid=3,
                                                    fractions=fx,
                                                    prescription_dose=prep_dose,
                                                    delivery_type=delivery_method)

HYP.write_colone()

# generate new xml file
HYP.xml_solution(list(protocol_dict.keys()))

# remaining task: copy the remaining 4 files into new template folder

# X.PLN, X.TEL, X.isodosesettings, X.dvhparam

copyfile(os.path.join(absolute_path,delivery_method,'5.11.isodosesettings.xml'), os.path.join(updated_template_path,pt_id+delivery_method+'.isodosesettings.xml'))
copyfile(os.path.join(absolute_path,delivery_method,'5.11.dvhparam.xml'), os.path.join(updated_template_path,pt_id+delivery_method+'.dvhparam.xml'))
copyfile(os.path.join(absolute_path,delivery_method,'5.11.PLN'), os.path.join(updated_template_path,pt_id+delivery_method+'.pln'))
copyfile(os.path.join(absolute_path,delivery_method,'5.11.TEL'), os.path.join(updated_template_path,pt_id+delivery_method+'.tel'))
