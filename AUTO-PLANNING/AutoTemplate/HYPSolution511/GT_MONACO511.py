# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 09:36:32 2020

@author: Xiaotian Huang in Elekta Shanghai Co. Ltd.
"""

class HYP_Editor_MONACO511:
    '''
       This Class was mainly used to generate a template automatically
       This version was only for Monaco511 TPS
       
    '''
    
    def  __init__(self,hyp_element_path,protocol_xlsx,demo_xml_path,output_xml_path,contourname_path,NAMING_LIB,hyp_path_new,updated_template_path,new_contourname_path):
        
        self.hypelement = hyp_element_path # hyp elements (including each parts)
        
        self.xlsx = protocol_xlsx # protocol xlsx
        
        self.demo_xml_path = demo_xml_path # demo dosenormsettings.xml
        
        self.ouput_xml_path = output_xml_path # updated dosenormsettings.xml
        
        self.contour_path = contourname_path # contournames fold path 
        
        self.updated_contour_path = new_contourname_path  # updated contournames fold path
        
        self.NAMING_LIB = NAMING_LIB # naming lib of each hospitals
        
        self.updated_hyp_path = hyp_path_new # new path for writing the hyp file 
        
        self.new_template_path = updated_template_path
        
    def extract_xlsx(self,pt_id):
        '''
          To extract data from protocol.xlsx for protocol_dict
          e.g. 
            (Dmin > 60Gy) <-> ('GoalType' = 1, 'Dose = 6000', 'Volume = -1') -- Minimum dose
            (Dmax < 70Gy) <-> ('GoalType' = 2, 'Dose = 7000', 'Volume = -1') -- Maximum Dose
            (Dmean > 45Gy) -> ('GoalType' = 3, 'Dose = 4500', 'Volume = -1') -- Mean Dose(Lower Limit)
            (Dmean < 65Gy) -> ('GoalType' = 4, 'Dose = 6500', 'Volume = -1') -- Mean Dose(Upper Limit)
            (D50% > 50Gy) -> ('GoalType' = 5, 'Dose = 5000', 'Volume = 50') -- Minimum Dose Received by Relative Volume
            (D100cc > 50Gy) -> ('GoalType' = 6, 'Dose = 5000', 'Volume = 100000') -- Minimum Dose Received by Absolute Volume
            (D50% < 50Gy) -> ('GoalType' = 7, 'Dose = 5000', 'Volume = 50') -- Maximum Dose Received by Relative Volume
            (D100cc < 50Gy) -> ('GoalType' = 8, 'Dose = 5000', 'Volume = 100000') -- Maximum Dose Received by Absolute Volume
            (V50Gy > 100%) -> ('GoalType' = 9, 'Dose = 5000', 'Volume = 100') -- Minimum Relative Volume That Receives Dose
            (V50Gy > 100cc) -> ('GoalType' = 10, 'Dose = 5000', 'Volume = 1000000') -- Minimum Absolute Volume That Receives Dose
            (V50Gy < 50%) -> ('GoalType' = 11, 'Dose = 5000', 'Volume = 50') -- Maximum Relative Volume That Receives Dose
            (V50Gy < 100cc) -> ('GoalType' = 12, 'Dose = 5000', 'Volume = 1000000') -- Maximum Absolute Volume That Receives Dose

        '''
        import pandas as pd
        protocol = pd.read_excel(self.xlsx, sheet_name=pt_id,header=None)
        
        protocol_list = [[protocol[0][i],protocol[1][i],protocol[2][i]] for i in range(protocol.shape[0])]
        name_set = set([item[0] for item in protocol_list if item[0] != 'frac' and item[0] != 'prep'])
            
        self.protocol_dict = {name : [] for name in name_set} 
        for item in protocol_list:
            if item[0] != 'frac' and item[0] != 'prep':
                self.protocol_dict[item[0]].append([item[1],item[2]])
                
        for key in self.protocol_dict.keys():
            for i,item in enumerate(self.protocol_dict[key]):
                if 'D' in item[0] and 'cc' in item[0]:
                    self.protocol_dict[key][i].append('8')
                elif 'D' in item[0] and '%' in item[0]:
                    self.protocol_dict[key][i].append('7')
                elif 'V' in item[0] and 'Gy' in item[0]:
                    self.protocol_dict[key][i].append('9')
                elif 'Dmax' in item[0]:
                    self.protocol_dict[key][i].append('2')
                
        return self.protocol_dict
    
    
    def Read_HYP_element(self):
        '''
        This function was used to extract all the elements from hyp file(Monaco55)
        
        '''
        self.keyword = ['# Part1\n','# Part2\n','# Part3\n','# Part4_VMAT\n','# Part4_IMRT\n','# Part5\n',
                        '# se\n','# pa\n','# qp\n','# oq\n','# mxd\n']
        self.element = {}
        with open(self.hypelement,'r+') as f:
            
            line = f.readlines()
        
        self.index_ele = [line.index(item) for item in self.keyword]
        for i in range(len(self.keyword)-1):
            self.element[self.keyword[i]] = line[self.index_ele[i]+1:self.index_ele[i+1]]
            
        self.element[self.keyword[-1]] = line[self.index_ele[-1]+1:]
#        ss = line.split(' ')
        
        return self.element

    def pretty_xml(self,element, indent, newline, level=0): 
        '''
        # elemnt为传进来的Elment类，参数indent用于缩进，newline用于换行
        to genereate a beautiful xml with tab
        '''
        if element:  # 判断element是否有子元素    
            if (element.text is None) or element.text.isspace():  # 如果element的text没有内容
                element.text = newline + indent * (level + 1)
            else:
                element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)
                # else:  # 此处两行如果把注释去掉，Element的text也会另起一行
                # element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level
        temp = list(element)  # 将element转成list
        for subelement in temp:
            if temp.index(subelement) < (len(temp) - 1):  # 如果不是list的最后一个元素，说明下一个行是同级别元素的起始，缩进应一致
                subelement.tail = newline + indent * (level + 1)
            else:  # 如果是list的最后一个元素， 说明下一行是母元素的结束，缩进应该少一个    
                subelement.tail = newline + indent * level
            self.pretty_xml(subelement, indent, newline, level=level + 1)  # 对子元素进行递归操作

    def modify_MONACO_contournames(self,protocol_name):
        
        '''read contournames file from FocalData to 
        extract the structure names of CT '''
    
        with open(self.contour_path, "r+") as f:
            line = f.readlines()
        
        old_name = [line[2+i*18].split('\n')[0] for i in range(int(len(line)/18))]
        
        self.name = [line[2+i*18].split('\n')[0] for i in range(int(len(line)/18))]
        
        diff_name = [item for item in self.name if item not in protocol_name]
        
        
        # Rule for name modification
        
        for i,item in enumerate(self.name):
            
            if item in diff_name:
                
                if item == 'T joint R':
                    
                    self.name[i] = 'T.Joint R'
                    
                elif item == 'T joint L':
                    
                    self.name[i] = 'T.Joint L'
                    
                elif item == 'A Duct L':
                    
                    self.name[i] = 'A.D L'
                    
                elif item == 'A Duct R':
                    
                    self.name[i] = 'A.D R'
                    
                elif item == 'Pitutary':
                    
                    self.name[i] = 'Pituitary'
                    
                elif item == 'T Loble L':
                    
                    self.name[i] = 'T.Lobe L'
                    
                elif item == 'T Loble R':
                    
                    self.name[i] = 'T.Lobe R'
                    
                elif item == 'Optical chiasm':
                    
                    self.name[i] = 'Optical Chiasm'
                    
                elif item == 'Spinal cord':
                    
                    self.name[i] = 'Spinal Cord'
        
        
        with open("C:/auto template/Contour_RenameLog.txt", 'a', encoding="utf8") as logf:
            nameRecord = str(old_name) + "\t" +  str(self.name)
            logf.write(nameRecord)
        logf.close()
        print("Done")
        
        
        for i in range(int(len(line)/18)):
            
            line[2+i*18] = self.name[i] + '\n'
            
        s=''.join(line)          
        f = open(self.updated_contour_path,'w+')        
        f.seek(0)        
        f.write(s)        
        f.close()
        
        
        print(diff_name)
        
        return self.name  
    
    
    def mkdir(self):
        
        import os
        folder = os.path.exists(self.new_template_path)
     
        if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(self.new_template_path)            #makedirs 创建文件时如果路径不存在会创建这个路径
            print ("---  new folder...  ---")
            print ("---  OK  ---")
     
        else:
            print ("---  There is this folder!  ---")
    
    
    def name_sorting(self):
        
        '''
           This function was used for sorting name e.g.
           target first
           OARs next
           normal tissues
           Body/Patient
        '''
        self.sorted_name = ['PGTVrpn','PGTVnx','PGTVnd','PCTV',
                            'Optical Chiasm','Brain Stem','Spinal Cord',
                            'Optical Nerve R','Optical Nerve L',
                            'Lens R','Lens L','Eye R','Eye L',
                            'Pituitary','Brain','Parotid R','Parotid L',
                            'T.Joint R','T.Joint L','T.Lobe R',
                            'T.Lobe L', 'Larynx','A.D L','A.D R', 
                            'Mandible','Oral Cavity','Lung']
        
        return self.sorted_name
    
    def xml_solution(self,protocol_name):
        '''
           This function was used for extracting xml file and try to combine with protocol 
           to generate xml together.
           
        '''
        from lxml import etree as et

#        demo_xml_path = 'C:/Users/xhuae08006/Desktop/XHTOMO_AUTO/Modifier/demo_dosenormsettings.xml'
        parser = et.XMLParser(encoding="utf-8", remove_blank_text=True)
        tree = et.parse(self.demo_xml_path,parser=parser)
        root1 = tree.getroot()
        name = self.modify_MONACO_contournames(protocol_name)
        
        for child in root1[1]:
        #    print(child.tag, child.attrib)
            for subchild in child.findall('DoseStructureParametersList'):
                for i,strname in enumerate(name): # subchild -> DoseStructureParametersList, 16 means the number of structures
                    et.SubElement(subchild, 'DoseStructureParameter')
                    et.SubElement(subchild[i],'StructureName').text = strname
                    et.SubElement(subchild[i],'Enabled').text = '-1'
                    et.SubElement(subchild[i],'HighDoseRef').text ='5'
                    et.SubElement(subchild[i],'MinDoseRef').text = '95'
                    et.SubElement(subchild[i],'PrescribedDose').text = '-1'
                    et.SubElement(subchild[i],'RefDoseList')
                    et.SubElement(subchild[i],'DoseGoalList')
                    
                    if strname in self.protocol_dict.keys():
                        print('OK')
                        for subsubchild in subchild[i].findall('DoseGoalList'):
                            print(subsubchild)
                            for k in range(len(self.protocol_dict[strname])):
                                et.SubElement(subsubchild,'DoseGoal')
                                et.SubElement(subsubchild[k],'GoalType').text = self.protocol_dict[strname][k][-1]
                                if self.protocol_dict[strname][k][-1] == '9':
                                    et.SubElement(subsubchild[k],'Dose').text = str(float(self.protocol_dict[strname][k][0].split('Gy')[0].split('V')[1])*100)
                                else:    
                                    et.SubElement(subsubchild[k],'Dose').text = str(float(self.protocol_dict[strname][k][1].split('Gy')[0])*100)
                                if self.protocol_dict[strname][k][-1] == '8':
                                    et.SubElement(subsubchild[k],'Volume').text = str(float(self.protocol_dict[strname][k][0].split('cc')[0].split('D')[1])*1000)
                                elif self.protocol_dict[strname][k][-1] == '7':
                                    et.SubElement(subsubchild[k],'Volume').text = self.protocol_dict[strname][k][0].split('%')[0].split('D')[1]
                                elif self.protocol_dict[strname][k][-1] == '9':
                                    et.SubElement(subsubchild[k],'Volume').text = str(self.protocol_dict[strname][k][1]*100)
                                et.SubElement(subsubchild[k],'Tolerance').text = '0'
                                
                    else:
                        print('Flase')
                        for subsubchild in subchild[i].findall('RefDoseList'):
                            print()
                            et.SubElement(subsubchild,'RefDose')
                            et.SubElement(subsubchild[0],'RefType').text = '0'
                            et.SubElement(subsubchild[0],'RefValue').text = '-1'  
        
#        xml_path_output = 'C:/Users/xhuae08006/Desktop/XHTOMO_AUTO/Modifier/test_dosenormsettings.xml'
        self.pretty_xml(root1, '  ', '\n')  # 执行美化方法
        tree.write(self.ouput_xml_path,pretty_print = True,encoding="utf-8",standalone ="yes", xml_declaration = True)
        
        print('Done!')

    
    def exist_read_mod(self,path1):
    
        self.line = []  # store the pointer's location in file
        
        with open(path1, "r+",errors = 'ignore') as f:
            
          line1 = f.readline()
          
          self.line.append(line1)
          
          while line1:
              
    #        pointer.append(f.tell())  #record the pointer loaction to help write
            
            line1 = f.readline()
            
            self.line.append(line1)    
        
        return self.line
        
    def classify(self,strt_ind_list):
        
        self.level_OARs = {}
        for item in strt_ind_list:
            if item[2] > 2 and item[2] < 7:
                self.level_OARs[item[0]] = 1
            elif item[2] > 6 and item[2] < 16:
                self.level_OARs[item[0]] = 2
            elif item[2] == 16:
                self.level_OARs[item[0]] = 3
            elif item[2] > 16 and item[2] < 24:
                self.level_OARs[item[0]] = 3
        return self.level_OARs
    
    def modify_qp(self,Vol,Dose,Weight,Opti_all,Surf_margin):
        '''
           This function is target penalty 
        '''
        for i,item in enumerate(self.element['# qp\n']):
            
            if item.split('=')[0] == '        refvolume':
                self.element['# qp\n'][i] = ''.join(['        refvolume=',str(Vol),'\n'])
                             
            elif item.split('=')[0] == '        isoconstraint':
                self.element['# qp\n'][i] = ''.join(['        isoconstraint=',str(Dose),'\n'])
            
            elif item.split('=')[0] == '        weight':
                self.element['# qp\n'][i] = ''.join(['        weight=',str(Weight),'\n'])
                             
            elif item.split('=')[0] == '        totalvolume':
                self.element['# qp\n'][i] = ''.join(['        totalvolume=',str(Opti_all),'\n'])
                             
            elif item.split('=')[0] == '        sanesurfacedose':
                self.element['# qp\n'][i] = ''.join(['        sanesurfacedose=',str(Surf_margin),'\n']) 

        return self.element['# qp\n']
    
    def modify_po(self,po,Dose,alpha):
        '''
           This function is target EUD
        '''

        self.po = po
        self.po[18] = ''.join(['        isoconstraint=',str(Dose),'\n'])
        self.po[10] = ''.join(['        alpha=',str(alpha),'\n'])
        self.po[-2] = ''.join(['    !END\n'])
        
        return self.po[:-1]    
    
    
    def modify_se(self,Dose,Weight,Shrink_margin,Opti_all,Powe_Law):
    
        '''
           Serial function
        '''

        for i,item in enumerate(self.element['# se\n']):
            
            if item.split('=')[0] == '        isoconstraint':
                self.element['# se\n'][i] = ''.join(['        isoconstraint=',str(Dose),'\n'])
                             
            elif item.split('=')[0] == '        weight':
                self.element['# se\n'][i] = ''.join(['        weight=',str(Weight),'\n'])
            
            elif item.split('=')[0] == '        totalvolume':
                self.element['# se\n'][i] = ''.join(['        totalvolume=',str(Opti_all),'\n'])
                             
            elif item.split('=')[0] == '        exponent':
                self.element['# se\n'][i] = ''.join(['        exponent=',str(Powe_Law),'\n'])
                             
            elif item.split('=')[0] == '        shrinkmargin':
                self.element['# se\n'][i] = ''.join(['        shrinkmargin=',str(Shrink_margin),'\n'])

        return self.element['# se\n']


    def modify_pa(self,Ref_dose,Volume,Weight,Powe_Law,Opti_all,Shrink_margin):

        '''
           Parallel Function
        '''
        
        for i,item in enumerate(self.element['# pa\n']):
            
            if item.split('=')[0] == '        refdose':
                self.element['# pa\n'][i] = ''.join(['        refdose=',str(Ref_dose),'\n'])  
                             
            elif item.split('=')[0] == '        isoconstraint':
                self.element['# pa\n'][i] = ''.join(['        isoconstraint=',str(Volume),'\n'])   
            
            elif item.split('=')[0] == '        weight':
                self.element['# pa\n'][i] = ''.join(['        weight=',str(Weight),'\n'])
                             
            elif item.split('=')[0] == '        exponent':
                self.element['# pa\n'][i] = ''.join(['        exponent=',str(Powe_Law),'\n']) 
                             
            elif item.split('=')[0] == '        shrinkmargin':
                self.element['# pa\n'][i] = ''.join(['        shrinkmargin=',str(Shrink_margin),'\n'])
                             
            elif item.split('=')[0] == '        totalvolume':
                self.element['# pa\n'][i] = ''.join(['        totalvolume=',str(Opti_all),'\n']) 

        return self.element['# pa\n']      

    def modify_mxd(self,Dose,Weight,Opti_all,Shrink_margin):
        
        '''
           Maximum Dose

        '''
        for i,item in enumerate(self.element['# mxd\n']):
            
            if item.split('=')[0] == '        isoconstraint':
                self.element['# mxd\n'][i] = ''.join(['        isoconstraint=',str(Dose),'\n' ])   
                             
            elif item.split('=')[0] == '        weight':
                self.element['# mxd\n'][i] = ''.join(['        weight=',str(Weight),'\n'])
            
            elif item.split('=')[0] == '        totalvolume':
                self.element['# mxd\n'][i] = ''.join(['        totalvolume=',str(Opti_all),'\n'])
                             
            elif item.split('=')[0] == '        shrinkmargin':
                self.element['# mxd\n'][i] = ''.join(['        shrinkmargin=',str(Shrink_margin),'\n'])


        return self.element['# mxd\n']



    def modify_qod(self,Dose,RMS,Shrink_margin):

        '''
        quadratic overdose
        '''

        for i,item in enumerate(self.element['# oq\n']):
            
            if item.split('=')[0] == '        thresholddose':
                self.element['# oq\n'][i] = ''.join(['        thresholddose=',str(Dose),'\n']) 
                             
            elif item.split('=')[0] == '        isoconstraint':
                self.element['# oq\n'][i] = ''.join(['        isoconstraint=',str(RMS),'\n']) 

            elif item.split('=')[0] == '        shrinkmargin':
                self.element['# oq\n'][i] = ''.join(['        shrinkmargin=',str(Shrink_margin),'\n'])
                             
        return self.element['# oq\n']



    def read_csv(self):
        
        self.pres_strt,self.dose_frac = [],[]
        self.pres_strt_ind = {} # initialization
        
        import csv
        with open(self.csv) as csvfile:  
            readCSV = csv.reader(csvfile, delimiter=',')  
            prep = [row for row in readCSV]  
        
        prep = [item for item in prep if item != []]
        for i,item in enumerate(prep):
            prep[i][-1] = prep[i][-1].replace(' ','')
        self.pres_strt = list(set([l[0] for l in prep if l[0] != 'prep' and l[0] != 'frac' ]))
        
        self.dose_frac = [l for l in prep if l[0] == 'prep' or l[0] == 'frac' ]
        
        for item in self.pres_strt: self.pres_strt_ind[item] = [] # initialization
        
        
        
        for item in prep:
            
            if item[0] != 'prep' and item[0] != 'frac':
                
                if item[2][-1] != '%':
                    
                    self.pres_strt_ind[item[0]].append((item[1],float(item[2])/100))
                    
                else:
                    
                    self.pres_strt_ind[item[0]].append((item[1],float(item[2][:-1])))
    
        
        return self.pres_strt,self.dose_frac,self.pres_strt_ind

    def write_colone(self):
        
        self.template_line.append('')        
        s=''.join(self.template_line)          
        f = open(self.updated_hyp_path,'w+')        
        f.seek(0)        
        f.write(s)        
        f.close()


    def cf_OAR(self,path_new,OBJ):
        '''
        this function is aimed to convert the item to 
        most helpful one
        '''
        import re
        weight_OARs = 0.01
        k_se = 12
        k_pa = 3

        self.cost_fun = []
        for i,j in enumerate(OBJ[1]):
            
            if j[0][0] == 'D':
                       
                if j[0] == 'Dmean':
                    
                    se = self.modify_se(path_new['se'], j[1], weight_OARs, 0, 0, 1)        
                    self.cost_fun.extend(se)
                    
                elif j[0] == 'Dmax':
                    
                    mxd =self.modify_mxd(path_new['mxd'], j[1], weight_OARs, 0, 0)
                    self.cost_fun.extend(mxd)
                
                else:
                    
                    se = self.modify_se(path_new['se'], j[1]*0.75, weight_OARs, 0, 0, 16)
                    self.cost_fun.extend(se)
                
            
                
            elif j[0][0] == 'V' :
                
                ss = (re.findall("\d+", j[0]))
                s = float(ss[0])
                flag = j[1]
                
                if flag <= 15.0:               
                    se = self.modify_se(path_new['se'], s*0.75, weight_OARs, 3, 0, k_se)
                    self.cost_fun.extend(se)
                else:
                    pa = self.modify_pa(path_new['pa'], s, flag, weight_OARs, k_pa, 0, 0)
                    self.cost_fun.extend(pa)  
    
        return self.cost_fun


    def ge_tem_pros(self,strt_ind_list,path_beam,dose_frac):
    
        import math
        self.template_line = []
        grid = 3
        tar = [(item[0],item[1],float(item[1][0][0][1:])) for item in strt_ind_list if 'PTV' in item[0] or 'PGTV' in item[0] or 'GTV' in item[0]]
        tar.sort(key=lambda x:x[2],reverse = True)
        tar_nam = [item[0] for item in tar]
        
        
        OARs_nam = [item[0] for item in strt_ind_list if item[0] not in tar_nam]
        prep_name = []
        prep_name = prep_name + tar_nam + OARs_nam
        ##tar_res_nam = [item[0] for item in OARs_nam_level if 'PTV' in item[0] or 'PGTV' in item[0]] 
           

        ind = self.path[0].rindex('\\')
        path_new = {}
        for item in self.path:
            path_new[item[int(ind+1):-4]] = self.exist_read_mod(item)
        
        
        pres = float(dose_frac[1][1])/100
        weight_target = 1
        weight_OARs = 0.01
        k_se = 12
        k_pa = 3
        RMS = 1
        max_dose = 47.5
        ## ================== part1 ================= ##
        part1 = ['000610b6\n','!LAYERING\n']
        for item in prep_name:
            if item == 'patient' or item == 'BODY':
                part1.append(str('    ' + item + '\n'))       
            else:
                part1.append(str('    ' + item + ':T\n'))
                    
        part1.append('!END\n')
         
        ## ==================  part2 ================ ##    
        part2 = path_new['part2']  ## read template
        part2[-2] = '    conformalavoidance=0\n'
        part2 = part2[:-1]
        target = []
        OARs = []   
        
        for i,item in enumerate(tar):
            
            if i != len(tar)-1:  ## inner target 1
                
                part2[1] = '    name=' + item[0] +'\n' 
#                prep_v = float((item[1][0][1]+3)/100)
                prep_d = float(item[1][0][0][1:])
                tar_pen = self.modify_po(path_new['po'],prep_d,0.6) 
                qod = self.modify_qod(path_new['qod'],prep_d+2,RMS,0)
                target = target + part2 + tar_pen + qod
                target.append('!END\n')
                
            else:   ## external target
                
                part2[1] = '    name=' + item[0] +'\n'    
#                prep_v = float((item[1][0][1]+3)/100)
                prep_d = float(item[1][0][0][1:])
                po = self.modify_po(path_new['po'],prep_d,0.6)
                
                ## set two quadratic overdose to external targets
                qod1 = self.modify_qod(path_new['qod'],pres,RMS,0)
    #            QOD2 = temp_tool.modify_QOD(QOD_path,prep_d-4,RMS1,grid)
                qod2 = self.modify_qod(path_new['qod'],prep_d*1.1,RMS,grid*math.floor(abs(prep_d*1.1-pres)/grid))
                
                target = target + part2 + po +qod1 + qod2
                target.append('!END\n')
    
        for item in strt_ind_list:
            
            if item[0] not in tar_nam:
                            
                if item[-1] == 5: ##　stem and cord
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    cf1 = self.cf_OAR(path_new,item)
                    OARs = OARs + part2 + cf1
                    OARs.append('!END\n')                           
                                                      
                elif item[-1] == 6: ##  normal tissues
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    cf2 = self.cf_OAR(path_new,item)
                    OARs = OARs + part2 + cf2
                    OARs.append('!END\n')      
                elif item[-1] == 7: ##  normal tissues
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    cf3 = self.cf_OAR(path_new,item)
                    OARs = OARs + part2 + cf3
                    OARs.append('!END\n')        
                    
                elif item[-1] == 8: ##  normal tissues
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    cf4 = self.cf_OAR(path_new,item)
                    OARs = OARs + part2 + cf4
                    OARs.append('!END\n')     
                
                elif item[-1] == 9: ##  normal tissues
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    cf5 = self.cf_OAR(path_new,item)
                    OARs = OARs + part2 + cf5
                    OARs.append('!END\n')    
                
                
                elif item[-1] == 100: ## patient
                
                    part2[1] = '    name=' + item[0] +'\n'
                    ## global maximum dose
                    mxd1 = self.modify_mxd(path_new['mxd'], round(pres*1.06,2), weight_OARs, 1, 0)
                    ## the outer target dose
                    QOD1 = self.modify_qod(path_new['qod'],max_dose,RMS,grid*0)
                    QOD2 = self.modify_qod(path_new['qod'],max_dose*0.8,RMS/2,grid*math.floor((max_dose*0.2)/grid))
                    QOD3 = self.modify_qod(path_new['qod'],max_dose*0.6,RMS/2,grid*math.floor((max_dose*0.4)/grid))
                    OARs = OARs + part2 + mxd1 + QOD1 + QOD2 + QOD3
                    OARs.append('!END\n')
            
        
        ## ================== part3 ================ ##
        part3 = path_new['part3']
        part3[-2] = '!END\n'
        
        ## ================== part4 ================ ##
        part4 = self.exist_read_mod(path_beam)
        part4[-2] = '!END\n'
        
        ## ================== part5 ================ ##
        part5 = path_new['part5']
        for i,item in enumerate(part5):
            if 'FRACTIONS' in item:
                part5[i] = ''.join(['!FRACTIONS    ',dose_frac[0][1],'\n'])
            elif 'PRESCRIPTION' in item:
                part5[i] = ''.join(['!PRESCRIPTION    ',str(float(dose_frac[1][1])/100),'\n'])
        
        ## ================== template ==================== ##        
        self.template_line = self.template_line + part1 + target + OARs + part3[:-1] + part4[:-1] + part5[:-1]      
        print('###############################')
        print('template has been generated !')
        print('###############################')
        return self.template_line

    def hyp_solution_XHTOMO_HEADNECK(self,grid,fractions,prescription_dose,delivery_type):
        
        '''
           tar = [('PGTVrpn', 0.95, 61.6),
             ('PGTVnx', 0.95, 61.6),
             ('PGTVnd', 0.95, 59.36),
             ('PCTV', 0.95, 50.4)]
           
           OARs_level1 = ['Brain Stem','Spinal Cord']
           OARs_level2 = ['Optical Chiasm','Optical Nerve R','Optical Nerve L','Lens R','Lens L']
           OARs_level3 = ['Eye R','Eye L','Parotid R','Parotid L',,'Pituitary','Brain']
           OARs_level4 = ['T.Joint R','T.Joint L','T.Lobe R','T.Lobe L','Larynx','A.D L','A.D R','Mandible','Oral Cavity','Lung']  
        '''
        
        OARs_level1 = ['Brain Stem','Spinal Cord']
        OARs_level2 = ['Optical Chiasm','Optical Nerve R','Optical Nerve L','Lens R','Lens L','Eye R','Eye L']
        OARs_level3 = ['Parotid R','Parotid L','Pituitary','Brain','Larynx','Oral Cavity']
        OARs_level4 = ['T.Joint R','T.Joint L','T.Lobe R','T.Lobe L','A.D L','A.D R','Mandible','Lung']  

        self.template_line = []
        
        # deal with target
        tar = [(key,self.protocol_dict[key][0][1],float(self.protocol_dict[key][0][0].split('V')[1].split('Gy')[0])) for key in self.protocol_dict.keys() if 'PCTV' in key or 'PGTV' in key or 'GTV' in key]
        tar.sort(key=lambda x:x[2],reverse = True)
        tar_nam = [item[0] for item in tar]
        
        sorted_name = self.name_sorting()
        OARs_nam = [item for item in sorted_name if item not in tar_nam and item in self.protocol_dict.keys()]
        prep_name = tar_nam + OARs_nam +['BODY']
        OARs_nam = OARs_nam + ['BODY']  
              
        ## ============================ part1 ============================== ##
        part1 = ['000510b6\n','!LAYERING\n'] # Monaco5.11 serial number: 000510b6
        for item in prep_name:
            if item == 'patient' or item == 'BODY':
                part1.append(str('    ' + item + '\n'))       
            else:
                part1.append(str('    ' + item + ':T\n'))
                    
        part1.append('!END\n')
         
        ## ============================ part2 ============================== ##   
        part2 = self.element['# Part2\n'][:-1]  ## read template
        target = []
        OARs = []   
        
        # Target part
        for i,item in enumerate(tar):
            
            if i != len(tar)-1:  ## inner target 
                
                part2[1] = '    name=' + item[0] +'\n'

                # setting target penalty
                tar_pen = self.modify_qp(Vol = item[1],Dose = item[2],Weight = 1.0,Opti_all = 1,Surf_margin = 0)
                
                # setting quadratic overdose
                qod = self.modify_qod(Dose = item[2]+2,RMS = 0.5,Shrink_margin = 0)
                
                # combine them together
                target = target + part2 + tar_pen[:-1] + qod[:-1]
                target.append('!END\n')
                
            else:   ## external target
                
                part2[1] = '    name=' + item[0] +'\n'  
                
                # setting target penalty
                tar_pen_ext = self.modify_qp(Vol = item[1],Dose = item[2],Weight = 1.0,Opti_all = 1,Surf_margin = 0)
                target = target + part2 + tar_pen_ext[:-1]
                
                # first quadratic overdose to contrain inner target reigon to prevent hot dose release to low dose region
                qod1 = self.modify_qod(Dose = tar[i-1][-1],RMS = 0.5,Shrink_margin = 0)
                target = target + qod1[:-1]
                
                # second quadratic overdose to constarin 110% percent of external target dose region
                qod2 = self.modify_qod(Dose = round(item[2]*1.1,2),RMS = 0.75,Shrink_margin = grid)
                target = target + qod2[:-1]
                
                # third quadratic overdose to constrain 102% percent of external target dose region
                qod3 = self.modify_qod(Dose = round(item[2]*1.02,2),RMS = 1,Shrink_margin = grid*2)
                target = target + qod3[:-1]
                
                target.append('!END\n')
        
        # OARs part
        for item in OARs_nam:
            '''
            
            D_x_cc < y Gy => if x < 10, then two cost functions were added:
                1. serial (k = 12, Isoconstraint(EUD) = 0.75*y)
                2. maximum dose (isoconstraint = y)
                
            D_x_% < y Gy
            
            1. if  40% < x < 60%, then one cost function was added:
                serial (k = 1, isocostraint = y)
            2. if  20% < x < 40%, then one cost function was added:
                serial (k = 8, isoconstraint = 0.95*y)
            3. if  10% < x < 20%, then one cost function was added:
                serial (k = 12, isoconstaraint = 0.85*y)
            4. if  0% < x < 10%, then one cost function was added:
                serial (k = 15, isoconstraint = 0.75*y)
                
            
            '''
                            
            if item in OARs_level1:
                
                # setting a serial and maximum cost function 
                part2[1] = '    name=' + item +'\n'
                
                # CF: serial to contrain high dose region
                cf1 = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.90,Weight=0.01,
                                     Shrink_margin=0,Opti_all=0,Powe_Law=12)
                
                # CF: maximum to constrain maximum point 
                if 'max' in self.protocol_dict[item][0][0].split('D')[1]:
                    
                    cf2 = self.modify_mxd(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
                                      Opti_all=1,Shrink_margin=0)
                    
                elif '0.1cc' in self.protocol_dict[item][0][0].split('D')[1]:
                    
                    cf2 = self.modify_mxd(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.9,Weight=0.01,
                                      Opti_all=1,Shrink_margin=0)     
                else:
                    
                    cf2 = self.modify_mxd(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
                                      Opti_all=1,Shrink_margin=0)
                
                
                OARs = OARs + part2 + cf1[:-1] + cf2[:-1]
                OARs.append('!END\n')                           

                                                      
            elif item in OARs_level2:
                
                # setting a maximum CF if Dx% < D5%, else setting a serial CF
                part2[1] = '    name=' + item +'\n'
                
                cf = self.modify_mxd(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
                                      Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 
                
            elif item in OARs_level3:
                
                # setting two serial CFs if it appears D50%, else setting one serial CF
                part2[1] = '    name=' + item +'\n'
                
                if '50%' in self.protocol_dict[item][0][0].split('D'):
                    
                    cf1 = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.75,Weight=0.01,
                                     Shrink_margin=3,Opti_all=0,Powe_Law=12)
                    OARs = OARs + part2 + cf1[:-1]
                    
                    
                    cf2 = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
                                     Shrink_margin=0,Opti_all=0,Powe_Law=1)
                    OARs = OARs + cf2[:-1]
                    
                    
                    OARs.append('!END\n') 
                    
                else:
                    
                    cf1 = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
                                     Shrink_margin=0,Opti_all=0,Powe_Law=12)


                    OARs = OARs + part2 + cf1[:-1]
                    OARs.append('!END\n')                      
           
            elif item in OARs_level4:
                
                # setting a serial CFs if it don't appear D50%, else setting one parallel CFs
                part2[1] = '    name=' + item +'\n'
                
                if len(self.protocol_dict[item]) == 1:
                    # only one statistics DVH evaluation index
                    if '50%' not in self.protocol_dict[item][0][0].split('D'):
                        
                        cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.85,Weight=0.01,
                                     Shrink_margin=3,Opti_all=0,Powe_Law=12)
                        
                    elif '50%' in self.protocol_dict[item][0][0].split('D'):
                        
                        cf = self.modify_pa(Ref_dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Volume = 50,
                                             Weight=0.01,Powe_Law=4,Opti_all=0,Shrink_margin=0) 
                        
                    OARs = OARs + part2 + cf[:-1]
                    OARs.append('!END\n')   
                    
                else:
                    
                    # DVH statistics indices more than one
                    CF = []

                    for key in self.protocol_dict[item]:
                        
                        if 'cc' in key[0]:
                            
                            if float(key[0].split('D')[1].split('cc')[0]) <= 10:
                                
                                cf1 = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.85,
                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=12)
                                
                                cf2 = self.modify_mxd(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
                                      Opti_all=0,Shrink_margin=0)
                                
                                cf = cf1[:-1] + cf2[:-1]
                            
                        elif '%' in key[0]:
                            
                            if float(key[0].split('D')[1].split('%')[0]) <= 60 and float(key[0].split('D')[1].split('%')[0]) > 40:
                                
                                cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),
                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=1)
                                
                            elif float(key[0].split('D')[1].split('%')[0]) <= 40 and float(key[0].split('D')[1].split('%')[0]) > 20:

                                cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.95,
                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=8)
                                
                            elif float(key[0].split('D')[1].split('%')[0]) <= 20 and float(key[0].split('D')[1].split('%')[0]) > 10:

                                cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.90,
                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=12)
                                
                            elif float(key[0].split('D')[1].split('%')[0]) <= 10:

                                cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.85,
                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=15)
                            
                            cf = cf[:-1]
                        
                        CF = CF + cf

                    OARs = OARs + part2 + CF
                    OARs.append('!END\n')                           
                
                
                           
            elif item == 'BODY': ## patient
                
                part2[1] = '    name=' + item +'\n'
                
                ## global maximum dose
                mxd1 = self.modify_mxd(Dose= tar[0][-1]*1.1, Weight=0.01, Opti_all=1, Shrink_margin=0)
                OARs = OARs + part2 + mxd1[:-1]               
                ## the outer target dose
                QOD1 = self.modify_qod(Dose = tar[-1][-1], RMS = 0.5, Shrink_margin = 0)
                OARs = OARs + QOD1[:-1]
                
                QOD2 = self.modify_qod(Dose = tar[-1][-1]-5, RMS = 1.0, Shrink_margin = grid)
                OARs = OARs + QOD2[:-1]

                QOD3 = self.modify_qod(Dose = tar[-1][-1]-10, RMS = 1.5, Shrink_margin = grid*2)
                OARs = OARs + QOD3[:-1]

                QOD4 = self.modify_qod(Dose = tar[-1][-1]-15, RMS = 2.0, Shrink_margin = grid*3)
                OARs = OARs + QOD4[:-1]
                
                
                OARs.append('!END\n')
#            
        
        ## ============================ part3 ============================== ##
        part3 = self.element['# Part3\n'][:-1]
        
        ## ============================ part4 ============================== ##
        # here are two selections for part4
        
        if delivery_type == 'VMAT':
            # VMAT 360 ARC
            part4 = self.element['# Part4_VMAT\n'][:-1] 
        elif delivery_type == 'IMRT':
            # IMRT 9beams 
            part4 = self.element['# Part4_IMRT\n'][:-1]
        
        ## ============================ part5 ============================== ##
        part5 = self.element['# Part5\n'][:-1]
        for i,item in enumerate(part5):
            if 'FRACTIONS' in item:
                part5[i] = ''.join(['!FRACTIONS    ',str(fractions),'\n'])
            elif 'PRESCRIPTION' in item:
                part5[i] = ''.join(['!PRESCRIPTION    ',str(float(prescription_dose)),'\n'])
        
        ## ================== template ==================== ##        
        self.template_line = self.template_line + part1 + target + OARs + part3 + part4 + part5
        
        print('###############################')
        print('template has been generated !')
        print('###############################')
              
        
        return self.template_line






    def ge_tem_HN(self,strt_ind_list,path_beam,dose_frac):
        '''
           This function generate an initial .hyp template for optimization
           
           path:
           tar_res_nam:
           prep_name:
           OARs_nam_level: 这个必须是排好序的器官名称
           dose_criteria:
           dose_inf:
        '''
        import math
        grid = 3
        self.template_line = []
        prep_name = [item[0] for item in strt_ind_list]
        ##tar_res_nam = [item[0] for item in OARs_nam_level if 'PTV' in item[0] or 'PGTV' in item[0]] # 寻找靶区的名字
        
        ind = self.path[0].rindex('\\')
        path_new = {}
        for item in self.path:
            path_new[item[int(ind+1):-4]] = self.exist_read_mod(item)
        
        pres = float(dose_frac[1][1])/100
        prep_d2 = 50.96
        prep_cord =40
        prep_stem = 50 
        prep_patriod = [50,50]
        Vol_patriod = [60,30]
        prep_v = 0.98  ## 98% == 0.98
        weight_target = 1
        weight_OARs = 0.01
        k_se = 12
        k_pa = 3
        max_dose = 54  ## 视觉系统的限制条件
        len_max = 9 ## 视觉系统的len特殊照顾
        RMS0 = 0.5
        RMS1 = 1
        ## ================== 生成part1 ================= ##
        part1 = ['000610b6\n','!LAYERING\n']
        for item in prep_name:
            if item == 'patient' or item == 'BODY':
                part1.append(str('    ' + item + '\n'))       
            else:
                part1.append(str('    ' + item + ':T\n'))
                    
        part1.append('!END\n')
        ## ============================================== ##

        ## ================== 生成 part2 ================ ##
    
        part2 = path_new['part2']  ## 读取一个模板进来
        part2[-2] = '    conformalavoidance=0\n'
        part2 = part2[:-1]
        target = []
        OARs = []
        
        
        for item in strt_ind_list:
            
            if 'PGTV' in item[0]:  ## 内靶区
                
                part2[1] = ''.join(['    name=',item[0],'\n']) 
                tar_pen = self.modify_qp(path_new['qp'], prep_v, pres, weight_target, 0, 1)
                QOD = self.modify_qod(path_new['qod'],pres+1,RMS1,0)
                target = target + part2 + tar_pen + QOD
                target.append('!END\n')
                
            if 'PTV' in item[0]:   ## 外靶区
                
                part2[1] = '    name=' + item[0] +'\n' 
                qp = self.modify_qp(path_new['qp'], prep_v, prep_d2, weight_target, 0, 1)
                QOD1 = self.modify_qod(path_new['qod'],pres,RMS0,0)
    #            QOD2 = temp_tool.modify_qod(QOD_path,prep_d-4,RMS1,grid)
                QOD2 = self.modify_qod(path_new['qod'],prep_d2*1.1,RMS1+0.5,math.floor((pres-prep_d2*1.1)/3)*3)
                target = target + part2 + qp + QOD1 + QOD2
                target.append('!END\n')
                
            if item[2] == 5 or item[2] == 6:##　stem or stem prv
               
               if 'PRV' in item[0]: ## stem PRV
                   
                   part2[1] = '    name=' + item[0] +'\n'
                   se = self.modify_se(path_new['se'], prep_stem*0.75, weight_OARs, 0, 0, k_se)
                   OARs = OARs + part2 + se
                   OARs.append('!END\n')
                   
                   
               else:
                   ## stem 
                   
                   part2[1] = '    name=' + item[0] +'\n'
                   mxd = self.modify_mxd(path_new['mxd'], prep_stem, weight_OARs, 0, 0)
                   OARs = OARs + part2 + mxd
                   OARs.append('!END\n')
                 
            
            if item[2] == 3 or item[2] == 4: ##  cord or cord prv
                
               if 'PRV' in item[0]:
                   
                   part2[1] = '    name=' + item[0] +'\n'
                   se = self.modify_se(path_new['se'], prep_cord*0.75, weight_OARs, 0, 0, k_se)
                   OARs = OARs + part2 + se
                   OARs.append('!END\n')
                   
               else:
                   
                   part2[1] = '    name=' + item[0] +'\n'
                   mxd = self.modify_mxd(path_new['mxd'], prep_cord, weight_OARs, 0, 0)
                   OARs = OARs + part2 + mxd
                   OARs.append('!END\n')
                   
            
            
            if item[2] > 6 and item[2] < 16: ## optical system
                
                if 'len' in item[0] or 'Len' in item[0] or 'LEN' in item[0]:
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    mxd = self.modify_mxd(path_new['mxd'], len_max, weight_OARs, 0, 0)       
                    OARs = OARs + part2 + mxd
                    OARs.append('!END\n')
                    
                else:
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    mxd = self.modify_mxd(path_new['mxd'], max_dose, weight_OARs, 0, 0)       
                    OARs = OARs + part2 + mxd
                    OARs.append('!END\n')
    
            
            if item[2] > 15 and item[2] < 24: ## parotid or other
                
                if item[0].upper() == 'PAROTIDS' or item[0].upper() == 'PAROTID ALL':
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    se1 = self.modify_se(path_new['se'], prep_d2*0.75, weight_OARs, grid, 0, k_se)
    #                se2 = self.modify_se(se_path, prep_d2*0.75, weight_OARs, 2*grid, 0, k_se)
                    pa1 = self.modify_pa(path_new['pa'], prep_patriod[1], Vol_patriod[1], weight_OARs, k_pa, 0, 0)
    #                pa2 = self.modify_pa(pa_path, prep_patriod[1], Vol_patriod[1], weight_OARs, k_pa, 1, 0)
                    OARs = OARs + part2 + se1 + pa1
                    OARs.append('!END\n')
                
                elif item[0] == 'Thyroid' or item[0].upper() == 'THYROID':
                   
                    part2[1] = '    name=' + item[0] +'\n'
                    se1 = self.modify_se(path_new['se'], prep_d2*0.75, weight_OARs, grid, 0, k_se)
    #                se2 = self.modify_se(se_path, prep_d2*0.75, weight_OARs, 2*grid, 0, k_se)
                    pa1 = self.modify_pa(path_new['pa'], prep_patriod[0], Vol_patriod[0], weight_OARs, k_pa, 0, 0)
    #                pa2 = self.modify_pa(pa_path, prep_patriod[1], Vol_patriod[1], weight_OARs, k_pa, 1, 0)
                    OARs = OARs + part2 + se1 + pa1
                    OARs.append('!END\n')
                                 
                else:
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    se = self.modify_se(path_new['se'], prep_d2*0.75, weight_OARs, grid, 0, k_se)
                    OARs = OARs + part2 + se
                    OARs.append('!END\n')
            
            if item[2] == 24: ## patient
            
                part2[1] = '    name=' + item[0] +'\n'
                mxd1 =self.modify_mxd(path_new['mxd'], round(pres*1.075,0), weight_OARs, 1, 0)
    #            mxd2 = self.modify_mxd(mxd_path, prep_d2, weight_OARs, 0, grid)
    #            se1 = self.modify_se(se_path, prep_d2*0.75, weight_OARs, 2*grid, 0, k_se)
    #            se2 = temp_tool.modify_se(se_path, prep_d2*0.75, weight_OARs, 4*grid, 0, k_se)
    #            se3 = temp_tool.modify_se(se_path, prep_d2*0.75, weight_OARs, 8*grid, 0, k_se)
                QOD1 = self.modify_qod(path_new['qod'],prep_d2,RMS1,grid*0)
                QOD2 = self.modify_qod(path_new['qod'],prep_d2*0.8,RMS1,grid*math.floor((prep_d2*0.2)/grid))
                QOD3 = self.modify_qod(path_new['qod'],prep_d2*0.6,RMS1,grid*math.floor((prep_d2*0.4)/grid))
                OARs = OARs + part2 + mxd1 + QOD1 + QOD2 +QOD3
                OARs.append('!END\n')
            
        
        ## ================== part3 ================ ##
        part3 = path_new['part3']
        part3[-2] = '!END\n'
        
        ## ================== part4 ================ ##
        part4 = self.exist_read_mod(path_beam)
        part4[-2] = '!END\n'
        
        ## ================== part5 ================ ##
        part5 = path_new['part5']
        for i,item in enumerate(part5):
            if 'FRACTIONS' in item:
                part5[i] = ''.join(['!FRACTIONS    ',dose_frac[0][1],'\n'])
            elif 'PRESCRIPTION' in item:
                part5[i] = ''.join(['!PRESCRIPTION    ',str(float(dose_frac[1][1])/100),'\n'])
                
    
        
        ## ================== 生成总的template ==================== ##        
        self.template_line = self.template_line + part1 + target + OARs + part3[:-1] + part4[:-1] + part5[:-1]      
        print('###############################')
        print('template has been generated !')
        print('###############################')
        return self.template_line
    
    
    def ge_tem_HN1(self,OARs_nam_level,path,path_beam):
        '''
           This function generate an initial .hyp template for optimization
           
           path:
           tar_res_nam:
           prep_name:
           OARs_nam_level:
           dose_criteria:
           dose_inf:
        '''
    

        #%% 预先输入的信息
        import temp_tool
        import math
        grid = 3
        prep_name = [item[0] for item in OARs_nam_level]
        ##tar_res_nam = [item[0] for item in OARs_nam_level if 'PTV' in item[0] or 'PGTV' in item[0]] # 寻找靶区的名字
        
        self.template_line = []
        part2_path = path[0] 
        part3_path = path[1]  
        part5_path = path[2]
        
        pa_path = path[3] 
        qp_path = path[4] 
        se_path = path[5] 
        mxd_path = path[6] 
        
        part4_path = path_beam
        prep_v = 0.98
        prep_d = 69.96 
        prep_d2 = 50.96
        prep_cord =40
        prep_stem = 50 
        prep_patriod = [30,50]
        Vol_patriod = [50,30]
        
        weight_target = 1
        weight_OARs = 0.01
        k_se = 12
        k_pa = 3
        max_dose = 54  ## 视觉系统的限制条件
        len_max = 9 ## 视觉系统的len特殊照顾
       
        ## ================== 生成part1 ================= ##
        part1 = ['000610b6\n','!LAYERING\n']
        for item in prep_name:
            if item == 'patient' or item == 'BODY':
                part1.append(str('    ' + item + '\n'))       
            else:
                part1.append(str('    ' + item + ':T\n'))
                    
        part1.append('!END\n')
        ## ============================================== ##
        
        
        ## ================== 生成 part2 ================ ##
        
            
        part2 = temp_tool.exist_read_mod(part2_path)  ## 读取一个模板进来
        part2[-2] = '    conformalavoidance=0\n'
        part2 = part2[:-1]
        target = []
        OARs = []
        for item in OARs_nam_level:
            
            if 'PGTV' in item[0]:  ## 内靶区
                
                part2[1] = '    name=' + item[0] +'\n'  
                tar_pen = temp_tool.modify_qp(qp_path, prep_v, prep_d, weight_target, 1, 1)
                target = target + part2 + tar_pen
                target.append('!END\n')
                
            if 'PTV' in item[0]:   ## 外靶区
                
                part2[1] = '    name=' + item[0] +'\n'      
                qp = temp_tool.modify_qp(qp_path, prep_v, prep_d2, weight_target, 1, 1)
                mxd1 = temp_tool.modify_mxd(mxd_path, prep_d, weight_OARs, 0, grid)
                mxd2 = temp_tool.modify_mxd(mxd_path, prep_d2*1.1, weight_OARs, 0, math.ceil(prep_d-prep_d2*1.1))
                target = target + part2 + qp + mxd1 + mxd2
                target.append('!END\n')
                
            if item[1] == 5 or item[1] == 6:##　stem or stem prv
               
               if 'PRV' in item[0]: ## stem PRV
                   
                   part2[1] = '    name=' + item[0] +'\n'
                   se = temp_tool.modify_se(se_path, prep_stem*0.75, weight_OARs, 0, 1, k_se)
                   OARs = OARs + part2 + se
                   OARs.append('!END\n')
                   
                   
               else:
                   ## stem 
                   
                   part2[1] = '    name=' + item[0] +'\n'
                   mxd = temp_tool.modify_mxd(mxd_path, prep_stem, weight_OARs, 1, 0)
                   OARs = OARs + part2 + mxd
                   OARs.append('!END\n')
                 
            
            if item[1] == 3 or item[1] == 4: ##  cord or cord prv
                
               if 'PRV' in item[0]:
                   
                   part2[1] = '    name=' + item[0] +'\n'
                   se = temp_tool.modify_se(se_path, prep_cord*0.75, weight_OARs, 0, 1, k_se)
                   OARs = OARs + part2 + se
                   OARs.append('!END\n')
                   
               else:
                   
                   part2[1] = '    name=' + item[0] +'\n'
                   mxd = temp_tool.modify_mxd(mxd_path, prep_cord, weight_OARs, 1, 0)
                   OARs = OARs + part2 + mxd
                   OARs.append('!END\n')
                   
            
            
            if item[1] > 6 and item[1] < 16: ## optical system
                
                if 'len' in item[0] or 'Len' in item[0] or 'LEN' in item[0]:
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    mxd = temp_tool.modify_mxd(mxd_path, len_max, weight_OARs, 1, 0)       
                    OARs = OARs + part2 + mxd
                    OARs.append('!END\n')
                    
                else:
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    mxd = temp_tool.modify_mxd(mxd_path, max_dose, weight_OARs, 1, 0)       
                    OARs = OARs + part2 + mxd
                    OARs.append('!END\n')
    
            
            if item[1] > 15 and item[1] < 24: ## parotid or other
                
                if item[0].upper() == 'PAROTIDS' or item[0].upper() == 'PAROTID ALL':
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    se1 = temp_tool.modify_se(se_path, prep_d2*0.75, weight_OARs, grid, 0, k_se)
                    se2 = temp_tool.modify_se(se_path, prep_d2*0.75, weight_OARs, 2*grid, 0, k_se)
                    pa1 = temp_tool.modify_pa(pa_path, prep_patriod[0], Vol_patriod[0], weight_OARs, k_pa, 1, 0)
                    pa2 = temp_tool.modify_pa(pa_path, prep_patriod[1], Vol_patriod[1], weight_OARs, k_pa, 1, 0)
                    OARs = OARs + part2 + se1 + se2 + pa1 + pa2
                    OARs.append('!END\n')
                
                else:
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    se = temp_tool.modify_se(se_path, prep_d2*0.75, weight_OARs, grid, 0, k_se)
                    OARs = OARs + part2 + se
                    OARs.append('!END\n')
            
            if item[1] == 24: ## patient
            
                part2[1] = '    name=' + item[0] +'\n'
                mxd1 =temp_tool.modify_mxd(mxd_path, math.floor(prep_d*1.08), weight_OARs, 1, 0)
                mxd2 = temp_tool.modify_mxd(mxd_path, prep_d2, weight_OARs, 0, grid)
                se1 = temp_tool.modify_se(se_path, prep_d2*0.75, weight_OARs, 2*grid, 0, k_se)
                se2 = temp_tool.modify_se(se_path, prep_d2*0.75, weight_OARs, 4*grid, 0, k_se)
                se3 = temp_tool.modify_se(se_path, prep_d2*0.75, weight_OARs, 8*grid, 0, k_se)
                OARs = OARs + part2 + mxd1 + mxd2 + se1 + se2 + se3
                OARs.append('!END\n')
            
        
        ## ================== 生成 part3 ================ ##
        part3 = temp_tool.exist_read_mod(part3_path)
        part3[-2] = '!END\n'
        
        ## ================== 生成 part4 ================ ##
        part4 = temp_tool.exist_read_mod(part4_path)
        part4[-2] = '!END\n'
        
        ## ================== 生成 part5 ================ ##
        part5 = temp_tool.exist_read_mod(part5_path)
        
    
        
        ## ================== 生成总的template ==================== ##        
        template_line = template_line + part1 + target + OARs + part3[:-1] + part4[:-1] + part5[:-1]      
        print('###############################')
        print('template has been generated !')
        print('###############################')
        return template_line
    
    def XHTOMO_TEMPLATE_GENERATE(self,OARs_nam_level,path,path_beam):
        '''
           The Hyperion Monaco5.51 Template(.hyp) for XHTOMO cases template
        '''
        import pandas
        # read protocol(xlsx) from excel 
        protocol_xlsx = extract_xlsx()
        
        #%% 预先输入的信息
        import temp_tool
        import math
        grid = 3
        prep_name = [item[0] for item in OARs_nam_level]
        ##tar_res_nam = [item[0] for item in OARs_nam_level if 'PTV' in item[0] or 'PGTV' in item[0]] # 寻找靶区的名字
        
        self.template_line = []
        part2_path = path[0] 
        part3_path = path[1]  
        part5_path = path[2]
        
        pa_path = path[3] 
        qp_path = path[4] 
        se_path = path[5] 
        mxd_path = path[6] 
        
        part4_path = path_beam
        prep_v = 0.98
        prep_d = 69.96 
        prep_d2 = 50.96
        prep_cord =40
        prep_stem = 50 
        prep_patriod = [30,50]
        Vol_patriod = [50,30]
        
        weight_target = 1
        weight_OARs = 0.01
        k_se = 12
        k_pa = 3
        max_dose = 54  ## 视觉系统的限制条件
        len_max = 9 ## 视觉系统的len特殊照顾
       
        ## ================== 生成part1 ================= ##
        part1 = ['000610b6\n','!LAYERING\n']
        for item in prep_name:
            if item == 'patient' or item == 'BODY' or item == '':
                part1.append(str('    ' + item + '\n'))       
            else:
                part1.append(str('    ' + item + ':T\n'))
                    
        part1.append('!END\n')
        ## ============================================== ##
        
        
        ## ================== 生成 part2 ================ ##
        
            
        part2 = temp_tool.exist_read_mod(part2_path)  ## 读取一个模板进来
        part2[-2] = '    conformalavoidance=0\n'
        part2 = part2[:-1]
        target = []
        OARs = []
        for item in OARs_nam_level:
            
            if 'PGTV' in item[0]:  ## 内靶区
                
                part2[1] = '    name=' + item[0] +'\n'  
                tar_pen = temp_tool.modify_qp(qp_path, prep_v, prep_d, weight_target, 1, 1)
                target = target + part2 + tar_pen
                target.append('!END\n')
                
            if 'PTV' in item[0]:   ## 外靶区
                
                part2[1] = '    name=' + item[0] +'\n'      
                qp = temp_tool.modify_qp(qp_path, prep_v, prep_d2, weight_target, 1, 1)
                mxd1 = temp_tool.modify_mxd(mxd_path, prep_d, weight_OARs, 0, grid)
                mxd2 = temp_tool.modify_mxd(mxd_path, prep_d2*1.1, weight_OARs, 0, math.ceil(prep_d-prep_d2*1.1))
                target = target + part2 + qp + mxd1 + mxd2
                target.append('!END\n')
                
            if item[1] == 5 or item[1] == 6:##　stem or stem prv
               
               if 'PRV' in item[0]: ## stem PRV
                   
                   part2[1] = '    name=' + item[0] +'\n'
                   se = temp_tool.modify_se(se_path, prep_stem*0.75, weight_OARs, 0, 1, k_se)
                   OARs = OARs + part2 + se
                   OARs.append('!END\n')
                   
                   
               else:
                   ## stem 
                   
                   part2[1] = '    name=' + item[0] +'\n'
                   mxd = temp_tool.modify_mxd(mxd_path, prep_stem, weight_OARs, 1, 0)
                   OARs = OARs + part2 + mxd
                   OARs.append('!END\n')
                 
            
            if item[1] == 3 or item[1] == 4: ##  cord or cord prv
                
               if 'PRV' in item[0]:
                   
                   part2[1] = '    name=' + item[0] +'\n'
                   se = temp_tool.modify_se(se_path, prep_cord*0.75, weight_OARs, 0, 1, k_se)
                   OARs = OARs + part2 + se
                   OARs.append('!END\n')
                   
               else:
                   
                   part2[1] = '    name=' + item[0] +'\n'
                   mxd = temp_tool.modify_mxd(mxd_path, prep_cord, weight_OARs, 1, 0)
                   OARs = OARs + part2 + mxd
                   OARs.append('!END\n')
                   
            
            
            if item[1] > 6 and item[1] < 16: ## optical system
                
                if 'len' in item[0] or 'Len' in item[0] or 'LEN' in item[0]:
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    mxd = temp_tool.modify_mxd(mxd_path, len_max, weight_OARs, 1, 0)       
                    OARs = OARs + part2 + mxd
                    OARs.append('!END\n')
                    
                else:
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    mxd = temp_tool.modify_mxd(mxd_path, max_dose, weight_OARs, 1, 0)       
                    OARs = OARs + part2 + mxd
                    OARs.append('!END\n')
    
            
            if item[1] > 15 and item[1] < 24: ## parotid or other
                
                if item[0].upper() == 'PAROTIDS' or item[0].upper() == 'PAROTID ALL':
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    se1 = temp_tool.modify_se(se_path, prep_d2*0.75, weight_OARs, grid, 0, k_se)
                    se2 = temp_tool.modify_se(se_path, prep_d2*0.75, weight_OARs, 2*grid, 0, k_se)
                    pa1 = temp_tool.modify_pa(pa_path, prep_patriod[0], Vol_patriod[0], weight_OARs, k_pa, 1, 0)
                    pa2 = temp_tool.modify_pa(pa_path, prep_patriod[1], Vol_patriod[1], weight_OARs, k_pa, 1, 0)
                    OARs = OARs + part2 + se1 + se2 + pa1 + pa2
                    OARs.append('!END\n')
                
                else:
                    
                    part2[1] = '    name=' + item[0] +'\n'
                    se = temp_tool.modify_se(se_path, prep_d2*0.75, weight_OARs, grid, 0, k_se)
                    OARs = OARs + part2 + se
                    OARs.append('!END\n')
            
            if item[1] == 24: ## patient
            
                part2[1] = '    name=' + item[0] +'\n'
                mxd1 =temp_tool.modify_mxd(mxd_path, math.floor(prep_d*1.08), weight_OARs, 1, 0)
                mxd2 = temp_tool.modify_mxd(mxd_path, prep_d2, weight_OARs, 0, grid)
                se1 = temp_tool.modify_se(se_path, prep_d2*0.75, weight_OARs, 2*grid, 0, k_se)
                se2 = temp_tool.modify_se(se_path, prep_d2*0.75, weight_OARs, 4*grid, 0, k_se)
                se3 = temp_tool.modify_se(se_path, prep_d2*0.75, weight_OARs, 8*grid, 0, k_se)
                OARs = OARs + part2 + mxd1 + mxd2 + se1 + se2 + se3
                OARs.append('!END\n')
            
        
        ## ================== 生成 part3 ================ ##
        part3 = temp_tool.exist_read_mod(part3_path)
        part3[-2] = '!END\n'
        
        ## ================== 生成 part4 ================ ##
        part4 = temp_tool.exist_read_mod(part4_path)
        part4[-2] = '!END\n'
        
        ## ================== 生成 part5 ================ ##
        part5 = temp_tool.exist_read_mod(part5_path)
        
    
        
        ## ================== 生成总的template ==================== ##        
        template_line = template_line + part1 + target + OARs + part3[:-1] + part4[:-1] + part5[:-1]      
        print('###############################')
        print('template has been generated !')
        print('###############################')
        return template_line    
    
    
    

    def initial(self,struct,struct_set,path_beam,selection):
    
        ## ============ Read struct file =========== ##
        contours = self.read_struct(struct)
        stru_name = [item['name'] for item in contours]
        pres_name,dose_frac,strt_index = self.read_csv()
        ## ============ Read CSV file ============== ##
        
        
        ## if pres_name in stru_name
        Err = []
        self.tras = {}
        for item in pres_name:
            if item not in stru_name:
                print('Name Error: {}'.format(item))
                Err.append(item)
        print('This means this name is not in the struct_name.\n')
        for item in stru_name:
            print('the name in strut_set were: {}'.format(item))
        # stat = input('Do you want to change the name? if Yes enter 1 & No enter 0\n')
        stat = '0'
        print("stat:",stat)
        if stat == '1':
            for item in Err:
                print('Original one:{}'.format(item))
                ss = input('new one:')
                self.tras[item] = ss
        else:
            pass
        
        for item in strt_index.keys():
            
            if item in Err:
                strt_index[self.tras[item]] = strt_index[item]
                del strt_index[item]
        
        self.strt_ind_list = []
        ## solve the order issue
        for key in strt_index.keys():
            if key in struct_set.keys():
                self.strt_ind_list.append((key,strt_index[key],struct_set[key]))
                
        for item in stru_name:
            if item == 'Body' or item == 'patient' or item == 'BODY':
                self.strt_ind_list.append((item,'',struct_set[item]))
        
        self.strt_ind_list.sort(key=lambda x:x[2])   
        if selection == '1':
            ## this indicate the prostate
            template = self.ge_tem_pros1(self.strt_ind_list,path_beam,dose_frac)
            
        else:
            
            template = self.ge_tem_HN(self.strt_ind_list,path_beam,dose_frac)
        
        template[-1] = '!ISPHANTOMMATERIAL    0\n' 
        
        self.write_colone(template)
        
        return self.strt_ind_list,self.tras
    



class XML_Editor:
    '''
        This class mainly used to generate an isodose.xml in Monaco 5.5 for 
        DVH Statistics Columns 
        
        e.g. 
        (Dmin > 60Gy) <-> ('GoalType' = 1, 'Dose = 6000', 'Volume = -1') -- Minimum dose
        (Dmax < 70Gy) <-> ('GoalType' = 2, 'Dose = 7000', 'Volume = -1') -- Maximum Dose
        (Dmean > 45Gy) -> ('GoalType' = 3, 'Dose = 4500', 'Volume = -1') -- Mean Dose(Lower Limit)
        (Dmean < 65Gy) -> ('GoalType' = 4, 'Dose = 6500', 'Volume = -1') -- Mean Dose(Upper Limit)
        (D50% > 50Gy) -> ('GoalType' = 5, 'Dose = 5000', 'Volume = 50') -- Minimum Dose Received by Relative Volume
        (D100cc > 50Gy) -> ('GoalType' = 6, 'Dose = 5000', 'Volume = 100000') -- Minimum Dose Received by Absolute Volume
        (D50% < 50Gy) -> ('GoalType' = 7, 'Dose = 5000', 'Volume = 50') -- Maximum Dose Received by Relative Volume
        (D100cc < 50Gy) -> ('GoalType' = 8, 'Dose = 5000', 'Volume = 100000') -- Maximum Dose Received by Absolute Volume
        (V50Gy > 100%) -> ('GoalType' = 9, 'Dose = 5000', 'Volume = 100') -- Minimum Relative Volume That Receives Dose
        (V50Gy > 100cc) -> ('GoalType' = 10, 'Dose = 5000', 'Volume = 1000000') -- Minimum Absolute Volume That Receives Dose
        (V50Gy < 50%) -> ('GoalType' = 11, 'Dose = 5000', 'Volume = 50') -- Maximum Relative Volume That Receives Dose
        (V50Gy < 100cc) -> ('GoalType' = 12, 'Dose = 5000', 'Volume = 1000000') -- Maximum Absolute Volume That Receives Dose
        
        
    '''
    
    def  __init__(self,demo_xml_path,output_xml_path,protocol_xlsx):
        
        self.demo_xml_path = demo_xml_path
        self.ouput_xml_path = output_xml_path
        self.xlsx = protocol_xlsx
 
    def extract_xlsx(self):
        '''
          To extract data from protocol.xlsx for protocol_dict
        '''
        import pandas as pd
        protocol = pd.read_excel(self.xlsx, sheet_name=pt_id,header=None)
        
        protocol_list = [[protocol[0][i],protocol[1][i],protocol[2][i]] for i in range(protocol.shape[0])]
        name_set = set([item[0] for item in protocol_list if item[0] != 'frac' and item[0] != 'prep'])
            
        protocol_dict = {name : [] for name in name_set} 
        for item in protocol_list:
            if item[0] != 'frac' and item[0] != 'prep':
                protocol_dict[item[0]].append([item[1],item[2]])
                
        for key in protocol_dict.keys():
            for i,item in enumerate(protocol_dict[key]):
                if 'D' in item[0] and 'cc' in item[0]:
                    protocol_dict[key][i].append('8')
                elif 'D' in item[0] and '%' in item[0]:
                    protocol_dict[key][i].append('7')
                elif 'V' in item[0] and 'Gy' in item[0]:
                    protocol_dict[key][i].append('9')
                
        return protocol_dict

    def pretty_xml(self,element, indent, newline, level=0): 
        '''
        # elemnt为传进来的Elment类，参数indent用于缩进，newline用于换行
        to genereate a beautiful xml with tab
        '''
        if element:  # 判断element是否有子元素    
            if (element.text is None) or element.text.isspace():  # 如果element的text没有内容
                element.text = newline + indent * (level + 1)
            else:
                element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)
                # else:  # 此处两行如果把注释去掉，Element的text也会另起一行
                # element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level
        temp = list(element)  # 将element转成list
        for subelement in temp:
            if temp.index(subelement) < (len(temp) - 1):  # 如果不是list的最后一个元素，说明下一个行是同级别元素的起始，缩进应一致
                subelement.tail = newline + indent * (level + 1)
            else:  # 如果是list的最后一个元素， 说明下一行是母元素的结束，缩进应该少一个    
                subelement.tail = newline + indent * level
            self.pretty_xml(subelement, indent, newline, level=level + 1)  # 对子元素进行递归操作

       
                                
#    def xml_solution(self):
#        '''
#           This function was used for extracting xml file and try to combine with protocol 
#           to generate xml together.
#           
#        '''
#        from lxml import etree as et
#
##        demo_xml_path = 'C:/Users/xhuae08006/Desktop/XHTOMO_AUTO/Modifier/demo_dosenormsettings.xml'
#        parser = et.XMLParser(encoding="utf-8", remove_blank_text=True)
#        tree = et.parse(self.demo_xml_path,parser=parser)
#        root1 = tree.getroot()
#        protocol_dict = extract_xlsx()
#        
#        
#        for child in root1[1]:
#        #    print(child.tag, child.attrib)
#            for subchild in child.findall('DoseStructureParametersList'):
#                for i,strname in enumerate(name): # subchild -> DoseStructureParametersList, 16 means the number of structures
#                    et.SubElement(subchild, 'DoseStructureParameter')
#                    et.SubElement(subchild[i],'StructureName').text = strname
#                    et.SubElement(subchild[i],'Enabled').text = '-1'
#                    et.SubElement(subchild[i],'HighDoseRef').text ='5'
#                    et.SubElement(subchild[i],'MinDoseRef').text = '95'
#                    et.SubElement(subchild[i],'PrescribedDose').text = '-1'
#                    et.SubElement(subchild[i],'RefDoseList')
#                    et.SubElement(subchild[i],'DoseGoalList')
#                    
#                    if strname in protocol_dict.keys():
#                        print('OK')
#                        for subsubchild in subchild[i].findall('DoseGoalList'):
#                            print(subsubchild)
#                            for k in range(len(protocol_dict[strname])):
#                                et.SubElement(subsubchild,'DoseGoal')
#                                et.SubElement(subsubchild[k],'GoalType').text = protocol_dict[strname][k][-1]
#                                if protocol_dict[strname][k][-1] == '9':
#                                    et.SubElement(subsubchild[k],'Dose').text = str(float(protocol_dict[strname][k][0].split('Gy')[0].split('V')[1])*100)
#                                else:    
#                                    et.SubElement(subsubchild[k],'Dose').text = str(float(protocol_dict[strname][k][1].split('Gy')[0])*100)
#                                if protocol_dict[strname][k][-1] == '8':
#                                    et.SubElement(subsubchild[k],'Volume').text = str(float(protocol_dict[strname][k][0].split('cc')[0].split('D')[1])*1000)
#                                elif protocol_dict[strname][k][-1] == '7':
#                                    et.SubElement(subsubchild[k],'Volume').text = protocol_dict[strname][k][0].split('%')[0].split('D')[1]
#                                elif protocol_dict[strname][k][-1] == '9':
#                                    et.SubElement(subsubchild[k],'Volume').text = str(protocol_dict[strname][k][1]*100)
#                                et.SubElement(subsubchild[k],'Tolerance').text = '0'
#                                
#                    else:
#                        print('Flase')
#                        for subsubchild in subchild[i].findall('RefDoseList'):
#                            et.SubElement(subsubchild,'RefDose')
#                            et.SubElement(subsubchild[k],'RefType').text = '0'
#                            et.SubElement(subsubchild[k],'RefValue').text = '-1'  
#        
##        xml_path_output = 'C:/Users/xhuae08006/Desktop/XHTOMO_AUTO/Modifier/test_dosenormsettings.xml'
#        self.pretty_xml(root1, '  ', '\n')  # 执行美化方法
#        tree.write(self.ouput_xml_path,pretty_print = True,encoding="utf-8",standalone ="yes", xml_declaration = True)
#        
#        print('Done!')
    
    def modify_MONACO_contournames(self):
        
        '''read contournames file from FocalData to 
        extract the structure names of CT '''
    
        #contour_path = 'C:/Users/Public/Documents/CMS/FocalData/Installation/5~Clinc_XH/1~003/1~CT1/contournames'
        with open(self.contour_path, "r+") as f:
            line = f.readlines()
        
        self.name = [line[2+i*18].split('\n')[0] for i in range(int(len(line)/18))]
        
        
        
        
        return self.name    
    
class NAME_Deal():
    '''
       This class aims to solve following issues:
           1. names order in .hyp file which would be a big issue for optimization
           2. structure name inconsistency between contournames and names in treatment protocol
           3. how to standardize
    '''
    
    def  __init__(self,contour_path,csv_file,colone_path):
        
        self.contour_path = contour_path
        self.csv = csv_file
        self.col = colone_path   
    

    
    def modify_MONACO_nameorders(self):
        
        '''
           This function was used to rearrange the 
           name orders of protocol_dict to ensure 
           the name orders in hyp is correct
        '''
         
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    