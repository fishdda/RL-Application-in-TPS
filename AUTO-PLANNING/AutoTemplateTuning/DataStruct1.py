import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydicom
import os

CF = {'po':'Target EUD','qp':'Target Penalty','se':'Serial',
      'pa':'Parallel','mxd':'Maximum Dose','o_q': 'Quadratic Overdose'} ## Cost Function names for regular use

Constraint = [('type','name of cf'),('usedensity',None),('effectweighting',None),
              ('totalvolume','optimize for all volume'),('sanesurfacedose',None),
              ('multicriterial','MCO'),('relaxfirst',None),('usebiasdose',None),
              ('shrinkmargin','Shrink Margin in IMRT constraints(mm)'),
              ('alpha',None),('beta_alpha',None),('celldensity','sensitivity in target EUD'),
              ('refdose','Dose Reference'),('functreserve',None),
              ('refvolume','Volume for Parallel'),('exponent','K in serial,parallel'),
              ('thresholddose','threshold dose'),('isoconstraint',None),
              ('isoeffect',None),('relativeimpact','++++ in IMRT constraints console'),
              ('status','off or on to include in optimization'),('manual','human adjust weights'),
              ('weight','the lagrange factor in optimization')]


def read_struct_name(structure):
    '''
       This function output a list of structure name from struct.dcm file
    '''
    contours = []
    for i in range(len(structure.ROIContourSequence)):
        contour = {}
        contour['color'] = structure.ROIContourSequence[i].ROIDisplayColor
        contour['number'] = structure.ROIContourSequence[i].ReferencedROINumber
        print(contour['number'])
        contour['name'] = structure.StructureSetROISequence[i].ROIName
        print(contour['name'])
        assert contour['number'] == structure.StructureSetROISequence[i].ROINumber
        contour['contours'] = [s.ContourData for s in structure.ROIContourSequence[i].ContourSequence]
        contours.append(contour)
    stru_name = [item['name'] for item in contours]
    
    return stru_name


stru_path = 'C:\\Users\\EXTHuaXia\\Desktop\\Elekta-Biomind-RLAUTO\\warm_HN\\database\\case\\prostate\\struct_file\\20180125_StrctrSets.dcm'
struct= pydicom.read_file(stru_path,force=True)
stru_name = read_struct_name(struct)
# # print(stru_name)

# data1 = pd.DataFrame({item:{item1: 0 for item1 in CF} for item in stru_name})
# target = ['CTV6750','CTV4750','PTV4750','PTV6750']

# for name in stru_name:
#     if name in target:
#         data1[name]['po'] = 1
#         data1[name]['qp'] = 1
#         data1[name]['o_q'] = 3
#         data1[name]['mxd'] = 2
#         data1[name]['se'] = 2
#     else:
#         if name == 'patient' or name == 'Body':
#             data1[name]['o_q'] = 3
#             data1[name]['mxd'] = 2
#             data1[name]['se'] = 2
#         else:
#             data1[name]['se'] = 3
#             data1[name]['pa'] = 3
#             data1[name]['mxd'] = 1
#             data1[name]['o_q'] = 1

# # print(data1)

# order = ['CTV6750','CTV4750','PTV6750','PTV4750',
#  'Bladder', 'Rectum','Femoral Head L', 'Femoral Head R' , 
#  'Penile Bulb', 'Pubic Bone', 'patient']
# # print(data1.head())
# data1 = data1.loc[:,order]

# new_order = []
# for i in data1.columns:
#     for j in CF.keys():
#         for k in range(int(data1[i][j])):
#             new_order.append(''.join([i,'-',j,'-',str(k+1)]))

# template_pros = {item[0]:{item1:0 for item1 in new_order} for item in Constraint}
# template_pros = pd.DataFrame(template_pros)
# template_pros = template_pros.loc[new_order,[item[0] for item in Constraint]] #reorder the index
# template_pros = template_pros.T
# # template_pros.to_csv("template_pros.csv",header=True,index = True)
# # print(template_pros.shape)
# # print(template_pros.head())

# ## Next would give the value to template
# hyp_template = pd.read_excel('C:\\Users\\Shelter6\\Desktop\\warm\\database\\txtfile\\file1\\hyp_template.xlsx', sheetname='Part2', header=0)
# # print(hyp_template)

# for item in template_pros.columns:
#     template_pros[item] = hyp_template[item.split('-')[1]]
# # for i in template_pros.columns:
# #     for j in Constraint:
# #         template_pros.loc[i,j[0]] = hyp_template.loc[i.split('-')[1],j[0]]

# # print(template_pros)
# # template_pros.to_csv("template_pros.csv",header=True,index = True)


# ## then I need to generate the template

# data1 = pd.DataFrame({item:{item1: 0 for item1 in CF} for item in stru_name})
target = ['CTV6750','CTV4750','PTV4750','PTV6750']

# for name in stru_name:
#     if name in target:
#         data1[name]['po'] = 1
#         data1[name]['qp'] = 1
#         data1[name]['o_q'] = 3
#         data1[name]['mxd'] = 2
#         data1[name]['se'] = 2
#     else:
#         if name == 'patient' or name == 'Body':
#             data1[name]['o_q'] = 3
#             data1[name]['mxd'] = 2
#             data1[name]['se'] = 2
#         else:
#             data1[name]['se'] = 3
#             data1[name]['pa'] = 3
#             data1[name]['mxd'] = 1
#             data1[name]['o_q'] = 1

# data1 = data1.loc[:,order]
# # print(data1.T)

# ###########################################
# template_line = []
# # read template_pros
# CFs = pd.read_csv('template_pros.csv')
# print(CFs)

# ## ================== part1 ================= ##
# part1 = ['000610b6\n','!LAYERING\n']
# for item in order:
#     if item == 'patient' or item == 'BODY':
#         part1.append(str('    ' + item + '\n'))       
#     else:
#         part1.append(str('    ' + item + ':T\n'))
            
# part1.append('!END\n')
# ## ========================================== ##

# ## ==================  part2 ================ ##    
# part2 = []
# strt_head = ['!VOIDEF\n','    name=','    storenodose=0\n',
# '    conformalavoidance=0\n','!END\n']

# for item in order:
#     strt_head[1] = ''.join([strt_head[1],item,'\n'])
#     for item1 in CFs.columns:
#         if item == item1.split('-')[0]:
#             strt_head.insert(-1,'    !COSTFUNCTION\n')
#             for i in [kk[0] for kk in Constraint]:
#                 strt_head.insert(-1,''.join(['        ',i,'=',str(CF.loc[item1,i]),'\n']))
#             strt_head.insert(-1,'    !END\n')



# # target = []
# # OARs = []   

# # for i,item in enumerate(tar):
    
# #     if i != len(tar)-1:  ## inner target 1
        
# #         part2[1] = '    name=' + item[0] +'\n' 
# # #                prep_v = float((item[1][0][1]+3)/100)
# #         prep_d = float(item[1][0][0][1:])
# #         tar_pen = self.modify_po(path_new['po'],prep_d,0.6) 
# #         qod = self.modify_qod(path_new['qod'],prep_d+2,RMS,0)
# #         target = target + part2 + tar_pen + qod
# #         target.append('!END\n')
        
# #     else:   ## external target
        
# #         part2[1] = '    name=' + item[0] +'\n'    
# # #                prep_v = float((item[1][0][1]+3)/100)
# #         prep_d = float(item[1][0][0][1:])
# #         po = self.modify_po(path_new['po'],prep_d,0.6)
        
# #         ## set two quadratic overdose to external targets
# #         qod1 = self.modify_qod(path_new['qod'],pres,RMS,0)
# # #            QOD2 = temp_tool.modify_QOD(QOD_path,prep_d-4,RMS1,grid)
# #         qod2 = self.modify_qod(path_new['qod'],prep_d*1.1,RMS,6)#grid*math.floor(abs(prep_d*1.1-pres)/grid)
        
# #         target = target + part2 + po +qod1 + qod2
# #         target.append('!END\n')

# # for item in strt_ind_list:
    
# #     if item[0] not in tar_nam:
                    
# #         if item[-1] == 5: ##　stem and cord
            
# #             part2[1] = '    name=' + item[0] +'\n'
# #             cf1 = self.cf_OAR(path_new,item)
# #             OARs = OARs + part2 + cf1
# #             OARs.append('!END\n')                           
                                              
# #         elif item[-1] == 6: ##  normal tissues
            
# #             part2[1] = '    name=' + item[0] +'\n'
# #             cf2 = self.cf_OAR(path_new,item)
# #             OARs = OARs + part2 + cf2
# #             OARs.append('!END\n')      
# #         elif item[-1] == 7: ##  normal tissues
            
# #             part2[1] = '    name=' + item[0] +'\n'
# #             cf3 = self.cf_OAR(path_new,item)
# #             OARs = OARs + part2 + cf3
# #             OARs.append('!END\n')        
            
# #         elif item[-1] == 8: ##  normal tissues
            
# #             part2[1] = '    name=' + item[0] +'\n'
# #             cf4 = self.cf_OAR(path_new,item)
# #             OARs = OARs + part2 + cf4
# #             OARs.append('!END\n')     
        
# #         elif item[-1] == 9: ##  normal tissues
            
# #             part2[1] = '    name=' + item[0] +'\n'
# #             cf5 = self.cf_OAR(path_new,item)
# #             OARs = OARs + part2 + cf5
# #             OARs.append('!END\n')    
        
        
# #         elif item[-1] == 100: ## patient
        
# #             part2[1] = '    name=' + item[0] +'\n'
# #             ## global maximum dose
# #             mxd1 = self.modify_mxd(path_new['mxd'], round(pres*1.06,2), weight_OARs, 1, 0)
# #             ## the outer target dose
# #             QOD1 = self.modify_qod(path_new['qod'],max_dose,RMS,1) #grid*0
# #             QOD2 = self.modify_qod(path_new['qod'],max_dose*0.8,RMS,6) #grid*math.floor((max_dose*0.2)/grid)
# #             QOD3 = self.modify_qod(path_new['qod'],max_dose*0.6,RMS,9)  #grid*math.floor((max_dose*0.4)/grid)
# #             OARs = OARs + part2 + mxd1 + QOD1 + QOD2 + QOD3 
# #             OARs.append('!END\n')
# import pandas as pd
# import matplotlib.pyplot as plt

# dat = pd.read_csv("C:\\Users\\EXTHuaXia\\Desktop\\Elekta-Biomind-RLAUTO\\warm_HN\\WARM_FMO_ITER70_TARGETPENALTY.csv",header=0)
# print(dat)
# V40,V50,V60 = [],[],[]
# RV40,RV50,RV62 = [],[],[]
# PTV6750,PTV4750 = [],[]
# order = []
# for i in dat.columns[1:]:
#     order.append(int(i))
#     print('order:{}'.format(i))
#     V40.append(float(dat.loc[0,i].split(",")[1].replace(' ','').split(")")[0]))
#     V50.append(float(dat.loc[0,i].split(",")[3].replace(' ','').split(")")[0]))
#     V60.append(float(dat.loc[0,i].split(",")[5].replace(' ','').split(")")[0]))
#     PTV4750.append(float(dat.loc[3,i].split(",")[-1].replace(' ','').split(")")[0]))
#     PTV6750.append(float(dat.loc[4,i].split(",")[-1].replace(' ','').split(")")[0]))
#     RV40.append(float(dat.loc[6,i].split(",")[1].replace(' ','').split(")")[0]))
#     RV50.append(float(dat.loc[6,i].split(",")[3].replace(' ','').split(")")[0]))
#     RV62.append(float(dat.loc[6,i].split(",")[5].replace(' ','').split(")")[0]))

# print('V40:{}'.format(V40))
# print('V50:{}'.format(V50))
# print([item-25 for item in order])
# plt.figure(figsize= (10,10))
# plt.subplot(331)
# plt.plot([item-36 for item in order],V40,'r-+')
# plt.xlabel('iteration')
# plt.ylabel('V40Gy_Bladder(%)',fontsize=16)
# # plt.title('V40Gy_Bladder(%)')
# plt.grid()
# plt.subplot(332)
# plt.plot([item-36 for item in order],V50,'b-+')
# plt.xlabel('iteration')
# plt.ylabel('V50Gy_Bladder(%)',fontsize=16)
# # plt.title('V50Gy_Bladder(%)')
# plt.grid()
# plt.subplot(333)
# plt.plot([item-25 for item in order],V60,'g-+')
# # plt.xlabel('iteration')
# plt.ylabel('V60Gy_Bladder(%)',fontsize=16)
# # plt.title('V60Gy_Bladder(%)')
# plt.grid()
# plt.subplot(334)
# plt.plot([item-36 for item in order],PTV6750,'m-+')
# plt.xlabel('iteration')
# plt.ylabel('V67.5Gy_PTV(%)',fontsize=16)
# # plt.title('V67.5Gy_PTV(%)')
# plt.ylim(90,105)
# plt.grid()
# plt.subplot(335)
# plt.plot([item-36 for item in order],PTV4750,'y-+')
# plt.xlabel('iteration')
# plt.ylabel('V47.5Gy_PTV(%)',fontsize=16)
# # plt.title('V47.5Gy_PTV(%)')
# plt.ylim(90,105)
# plt.grid()
# plt.subplot(337)
# plt.plot([item-36 for item in order],RV40,'r-+')
# plt.xlabel('iteration')
# plt.ylabel('V40Gy_Rectum(%)',fontsize=16)
# # plt.title('V40Gy_Rectum(%)')
# plt.grid()
# plt.subplot(338)
# plt.plot([item-36 for item in order],RV50,'b-+')
# plt.xlabel('iteration')
# plt.ylabel('V50Gy_Rectum(%)',fontsize=16)
# # plt.title('V50Gy_Rectum(%)')
# plt.grid()
# plt.subplot(339)
# plt.plot([item-36 for item in order],RV62,'g-+')
# plt.xlabel('iteration')
# plt.ylabel('V62.5Gy_Rectum(%)',fontsize=16)
# # plt.title('V62.5Gy_Rectum(%)')
# plt.grid()
# plt.show()
