# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 09:36:32 2020

@author: Henry Huang in Elekta Shanghai Co. Ltd.
"""

class HYP_Editor_MONACO551:
    '''
       This Class was mainly used to generate a template automatically
       This version was only for Monaco551 TPS
       
    '''
    
    def  __init__(self,hyp_element_path,
                       protocol_xlsx,
                       demo_xml_path,
                       output_xml_path,
                       contourname_path,
                       NAMING_LIB,
                       hyp_path_new,
                       updated_template_path,
                       new_contourname_path):
        
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
                        '# se\n','# pa\n','# qp\n','# oq\n','# mxd\n','# conf\n','# po\n','# ov\n','# uv\n']
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
                    
                elif item == 'L eye':
                    
                    self.name[i] = 'Eye L'
                    
                elif item == 'R eye':
                    
                    self.name[i] = 'Eye R'
                
        
        
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
                            'Mandible','Oral Cavity','Lung','R6','R7']
        
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
                                    
                                elif self.protocol_dict[strname][k][-1] == '2':                    
                                    et.SubElement(subsubchild[k],'Volume').text = str(-1)
                                
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
        
    def csv_read_to_dvh(self):
        '''
           This function was used to extract DVH data from csv file
           20200330 was updated and no error occurs
        '''
        import csv
        import os
        ss = os.listdir('C:/auto template/dvh')
        dir_list = sorted(ss,  key=lambda x: os.path.getmtime(os.path.join('C:/auto template/dvh', x)))
        csv_file = [item for item in dir_list if item.split('.')[1] == 'csv']
        
        path_dvh = os.path.join('C:/auto template/dvh',csv_file[-1])
        csv_reader = csv.reader(open(path_dvh, encoding='utf-8'))
        row = [ row for row in csv_reader]
        # clean dvh data


        dvh_ = row[3:-3]  ## remove redundant data
        dvh = []
        for i in dvh_:
            if ' ' in i[0] or '  ' in i[0]: # organ name
                kk = i[0].split('  ')
            kkk = [j for j in kk if j!='' and j!=' ']

            if ' ' in i[1]:                 # absolute dose
                dd = i[1].split(' ')
            ddd = [j for j in dd if j!='' and j!=' ']

            if ' ' in i[2]:                 # relative volume
                vv = i[2].split(' ')
            vvv = [j for j in vv if j!='' and j!=' ']
            
            dvh.append(kkk+ddd+vvv)
            
        for i,item in enumerate(dvh):
            if len(item)>3:
                st = ''
                for j in item[0:-2]:
                    st += (j+' ')
                dvh[i] = [st[:-1],dvh[i][-2],dvh[i][-1]]
            else:
                pass

        flag = []
        for i in range(len(dvh)-1):
            if dvh[i][0] != dvh[i+1][0]:
                flag.append((dvh.index(dvh[i]),dvh[i][0]))
                continue
        flag.append((dvh.index(dvh[-1]),dvh[-1][0])) # to mark the position of each organ's name
        
        self.DVH = {item[1]:[] for item in flag}
                
        for j in range(len(flag)):
            
            if j != 0:
                
                for k in range(flag[j-1][0]+1,flag[j][0]+1):
                    
                    self.DVH[flag[j][1]].append((float(dvh[k][1]),float(dvh[k][2])))
                    
            else:
                
                for k in range(flag[j][0]+1):
                    
                    self.DVH[flag[j][1]].append((float(dvh[k][1]),float(dvh[k][2])))
        
        return self.DVH

    def DVH_MAX_MEAN(self,dvh_data):
        '''
           This function deals with the dvh data for evaluation and guide for next parameters modification
           dvh_data : dict.({'Brain':[(d1,v1),(d2,v2),....]})
           dvh_data_diff : differential dvh data
           
           In this program, PTV5096's maximum dose has some problems.
        '''
        dvh_data_diff = {}
        self.dvh_inf = {}
        self.dvh_inf['Dmean'] = {}
        self.dvh_inf['Dmax'] = {}
        for key in dvh_data.keys():
            
            dvh_data_diff[key] = [(dvh_data[key][i][0],dvh_data[key][i][1]-dvh_data[key][i+1][1]) for i in range(len(dvh_data[key])-1)]
            
            dvh_data_diff[key].append((dvh_data[key][-1][0],dvh_data[key][-1][1]))
            
            self.dvh_inf['Dmean'][key] = round(sum(item[0]*item[1] for item in dvh_data_diff[key])/sum([item[1] for item in dvh_data_diff[key]]),1)
         
                
            for item in dvh_data[key]:
                
                if item[1] == 0:
                    
                    flag = dvh_data[key].index(item)
                    break
                
            self.dvh_inf['Dmax'][key] = dvh_data[key][flag-1][0]
     
        return self.dvh_inf

    def DVH_Stat_Extract(self,dvh_inf,dvh_new_data):
            #plan_results1
            '''
            This function returns a plan results of DVH
            the name of dvh_new_data must be consistent with struct_index
            e.g.

            self.protocol_dict = {'PCTV': [['V50.4Gy', 0.95, '9']],
                                    'Mandible': [['D50%', '35Gy', '7'], ['D2cc', '60Gy', '8']]}

            self.dvh_stat_calc = {'PCTV': [['V50.4Gy', 0.95, 0.98, 1.12, '9']],
                                    'Mandible': [['D50%', '35Gy', '30Gy', 0.67, '7'], ['D2cc', '60Gy', '56Gy', 0.88, '8']]}
            '''
            import numpy as np
            from scipy.interpolate import interp1d 
            # self.dvh_indices,self.diff_result = {},{}
            # for item in pres_strt_ind.keys(): self.dvh_indices[item] = []
            # for item in pres_strt_ind.keys(): self.diff_result[item] = []
            self.dvh_stat_calc = {item:[] for item in self.protocol_dict.keys()}
            
            for item in self.protocol_dict.keys():
                    
                    for j in self.protocol_dict[item]:
                        # e.g. j = ['V50.4Gy', 0.95, '9']
                        
                        if j[0][0] == 'D':
                            
                            if j[0][1:] == 'max' or j[0][1:] == 'mean':  # Dmean or Dmax

                                cal_dose = round(dvh_inf[j[0]][item]/100,1)
                                diff_index = cal_dose/float(self.protocol_dict[item][j][1].split('Gy')[0])

                                self.dvh_stat_calc[item].append([self.protocol_dict[item][j][0],
                                                                self.protocol_dict[item][j][1],
                                                                str(cal_dose)+'Gy',diff_index,
                                                                self.protocol_dict[item][j][-1]])
                            elif j[0][-1] == '%': # DX%

                                Relative_Vol = float(j[0].split('D')[1].split('%')[0])
                                # execute interpolate algorithm to get calculated dose
                                mini = 10000
                                dose = float(j[0][1:])*100
                                for item1 in dvh_new_data[item]:
                                    if abs(item1[0]-dose) < mini:
                                        mini = abs(item1[0]-dose)
                                        mini_id = dvh_new_data[item].index(item1)


                                cal_dose = round(dvh_inf[j[0]][item]/100,1)
                                diff_index = cal_dose/float(self.protocol_dict[item][j][1].split('Gy')[0])

                                self.dvh_stat_calc[item].append([self.protocol_dict[item][j][0],
                                                                self.protocol_dict[item][j][1],
                                                                str(cal_dose)+'Gy',diff_index,
                                                                self.protocol_dict[item][j][-1]])
                            
                            
                        elif j[1] == 95.0:
                            
                            cover = float(j[0][1:])*100  ## indicate prescription dose
                            
                            for item1 in dvh_new_data[item]:
                                ## retify the problem in 0-5100
                                if item1[1] == 100:
                                    
                                    index = dvh_new_data[item].index(item1)
                                    
                                    print('appear 5096 in 0-5111')
                                    
                                    
                            if cover <= dvh_new_data[item][index][0]:
                                
                                self.dvh_indices[item].append((j[0],100))
                            
                            else:
                                
                                mini = 100
                                mini_id = 0
                                for item1 in dvh_new_data[item]:
                                    if abs(item1[0]-cover) <= mini:
                                        mini = abs(item1[0]-cover)
                                        mini_id = dvh_new_data[item].index(item1)
                                        
                                x,y = [],[]
                                for i in range(mini_id-1,mini_id+2):
                                    y.append(round(dvh_new_data[item][i][1],4))
                                    x.append(round(dvh_new_data[item][i][0],4))
                                    
                                x = np.array(x)
                                y = np.array(y)
                                f=interp1d(x,y,kind = 'linear')#interpolate
                                self.dvh_indices[item].append((j[0],round(float(f(cover)),4)))
                            
                        elif j[0][0] == 'V':
                        
                            ## to find with interpolate without consider 0.03cc              
                            mini = 10000
                            dose = float(j[0][1:])*100
                            for item1 in dvh_new_data[item]:
                                if abs(item1[0]-dose) < mini:
                                    mini = abs(item1[0]-dose)
                                    mini_id = dvh_new_data[item].index(item1)
                            xx = [dvh_new_data[item][i][0] for i in range(mini_id-1,mini_id+2)]
                            yy = [dvh_new_data[item][i][1] for i in range(mini_id-1,mini_id+2)]
                            f=interp1d(xx,yy,kind = 'linear')  #linear interpolate
                            self.dvh_indices[item].append((j[0],round(float(f(dose)),2)))   
                            
            for item in self.dvh_indices:
                for i,j in zip(self.dvh_indices[item],pres_strt_ind[item]):
                    self.diff_result[item].append((j[0],round(i[1]/j[1],2)))
            




            
            return self.dvh_indices #self.dvh_stat_calc



    def modify_conf_551(self,Opti_all,isoconstraint):
        '''
           This function is conformality
        '''
        # initialization of cost functions
        self.element = self.Read_HYP_element()
        
        if Opti_all == 1:
            
            for i,item in enumerate(self.element['# conf\n']):
                                 
                if item.split('=')[0] == '        isoconstraint':
                    self.element['# conf\n'][i] = ''.join(['        isoconstraint=',str(isoconstraint),'\n'])
                                
                elif item.split('=')[0] == '        totalvolume':
                    self.element['# conf\n'][i] = ''.join(['        totalvolume=',str(Opti_all),'\n'])

        else:
            
            for i,item in enumerate(self.element['# conf\n']):
                                 
                if item.split('=')[0] == '        isoconstraint':
                    self.element['# conf\n'][i] = ''.join(['        isoconstraint=',str(isoconstraint),'\n'])
                                
                elif item.split('=')[0] == '        totalvolume':
                    self.element['# conf\n'][i] = ''.join(['        totalvolume=',str(1-Opti_all),'\n'])

        return self.element['# conf\n']
    
    def modify_qp_551(self,Vol,Dose,Weight,Opti_all,Surf_margin):
        '''
           This function is target penalty 
        '''
        
        # initialization of cost functions
        self.element = self.Read_HYP_element()
        
        if Opti_all == 1:
            
            for i,item in enumerate(self.element['# qp\n']):
                
                if item.split('=')[0] == '        refvolume':
                    self.element['# qp\n'][i] = ''.join(['        refvolume=',str(Vol),'\n'])
                                 
                elif item.split('=')[0] == '        isoconstraint':
                    self.element['# qp\n'][i] = ''.join(['        isoconstraint=',str(Dose),'\n'])
                
                elif item.split('=')[0] == '        weight':
                    self.element['# qp\n'][i] = ''.join(['        weight=',str(Weight),'\n'])
                                 
                elif item.split('=')[0] == '        sanesurfacedose':
                    self.element['# qp\n'][i] = ''.join(['        sanesurfacedose=',str(Surf_margin),'\n']) 
                                 
                elif item.split('=')[0] == '        applyshrinkmargintooars':
                    self.element['# qp\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])

        return self.element['# qp\n']
    
    def modify_po_551(self,po,Dose,alpha):
        '''
           This function is target EUD
        '''
        # initialization of cost functions
        self.element = self.Read_HYP_element()

        self.po = po
        self.po[18] = ''.join(['        isoconstraint=',str(Dose),'\n'])
        self.po[10] = ''.join(['        alpha=',str(alpha),'\n'])
        self.po[-2] = ''.join(['    !END\n'])
        
        return self.po[:-1]    
    
    
    def modify_se_551(self,Dose,Weight,Shrink_margin,Opti_all,Powe_Law):
    
        '''
           Serial function
        '''
        # initialization of cost functions
        self.element = self.Read_HYP_element()
        
        if Opti_all == 1:
        
            for i,item in enumerate(self.element['# se\n']):
                
                if item.split('=')[0] == '        isoconstraint':
                    self.element['# se\n'][i] = ''.join(['        isoconstraint=',str(Dose),'\n'])
                                 
                elif item.split('=')[0] == '        weight':
                    self.element['# se\n'][i] = ''.join(['        weight=',str(Weight),'\n'])
                                 
                elif item.split('=')[0] == '        exponent':
                    self.element['# se\n'][i] = ''.join(['        exponent=',str(Powe_Law),'\n'])

                elif item.split('=')[0] == '        applyshrinkmargintooars':
                    self.element['# se\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])
                                 
        else:
            
            for i,item in enumerate(self.element['# se\n']):
                
                if item.split('=')[0] == '        isoconstraint':
                    self.element['# se\n'][i] = ''.join(['        isoconstraint=',str(Dose),'\n'])
                                 
                elif item.split('=')[0] == '        weight':
                    self.element['# se\n'][i] = ''.join(['        weight=',str(Weight),'\n'])
                                 
                elif item.split('=')[0] == '        exponent':
                    self.element['# se\n'][i] = ''.join(['        exponent=',str(Powe_Law),'\n'])

                elif item.split('=')[0] == '        applyshrinkmargintooars':
                    self.element['# se\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])    
                                 
                elif item.split('=')[0] == '        groupmargins':
              
                    for j,jtem in enumerate(list(reversed(self.tar_nam))):
                        
                        self.element['# se\n'].insert(i+1,'        !END\n')
                        self.element['# se\n'].insert(i+1,'            targetmargin='+str(Shrink_margin)+'\n') 
                        self.element['# se\n'].insert(i+1,'            shrinkmargintarget='+jtem+'\n')             
                        self.element['# se\n'].insert(i+1,'        !SHRINKMARGINTARGET\n')      

        return self.element['# se\n']


    def modify_pa_551(self,Ref_dose,Volume,Weight,Powe_Law,Opti_all,Shrink_margin):

        '''
           Parallel Function
        '''
        
        # initialization of cost functions
        self.element = self.Read_HYP_element()
        
        if Opti_all == 1:
            
            for i,item in enumerate(self.element['# pa\n']):
                
                if item.split('=')[0] == '        refdose':
                    self.element['# pa\n'][i] = ''.join(['        refdose=',str(Ref_dose),'\n'])  
                                 
                elif item.split('=')[0] == '        isoconstraint':
                    self.element['# pa\n'][i] = ''.join(['        isoconstraint=',str(Volume),'\n'])   
                
                elif item.split('=')[0] == '        weight':
                    self.element['# pa\n'][i] = ''.join(['        weight=',str(Weight),'\n'])
                                 
                elif item.split('=')[0] == '        exponent':
                    self.element['# pa\n'][i] = ''.join(['        exponent=',str(Powe_Law),'\n']) 
                                 
                elif item.split('=')[0] == '        applyshrinkmargintooars':
                    self.element['# pa\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])

        else:
            
            for i,item in enumerate(self.element['# pa\n']):
                
                if item.split('=')[0] == '        refdose':
                    self.element['# pa\n'][i] = ''.join(['        refdose=',str(Ref_dose),'\n'])  
                                 
                elif item.split('=')[0] == '        isoconstraint':
                    self.element['# pa\n'][i] = ''.join(['        isoconstraint=',str(Volume),'\n'])   
                
                elif item.split('=')[0] == '        weight':
                    self.element['# pa\n'][i] = ''.join(['        weight=',str(Weight),'\n'])
                                 
                elif item.split('=')[0] == '        exponent':
                    self.element['# pa\n'][i] = ''.join(['        exponent=',str(Powe_Law),'\n']) 
                                 
                elif item.split('=')[0] == '        applyshrinkmargintooars':
                    self.element['# pa\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])

                elif item.split('=')[0] == '        groupmargins':
              
                    for j,jtem in enumerate(list(reversed(self.tar_nam))):
                        
                        self.element['# pa\n'].insert(i+1,'        !END\n')
                        self.element['# pa\n'].insert(i+1,'            targetmargin='+str(Shrink_margin)+'\n') 
                        self.element['# pa\n'].insert(i+1,'            shrinkmargintarget='+jtem+'\n')             
                        self.element['# pa\n'].insert(i+1,'        !SHRINKMARGINTARGET\n')                                                       

        return self.element['# pa\n']      

    def modify_mxd_551(self,Dose,Weight,Opti_all,Shrink_margin):
        
        '''
           Maximum Dose function 

        '''
        
        # initialization of cost functions
        self.element = self.Read_HYP_element()
        
        if Opti_all == 1:
            # means all structure voxels would be considered in
            
            for i,item in enumerate(self.element['# mxd\n']):
            
                if item.split('=')[0] == '        isoconstraint':
                    self.element['# mxd\n'][i] = ''.join(['        isoconstraint=',str(Dose),'\n' ])   
                                 
                elif item.split('=')[0] == '        weight':
                    self.element['# mxd\n'][i] = ''.join(['        weight=',str(Weight),'\n'])

                elif item.split('=')[0] == '        applyshrinkmargintooars':
                    self.element['# mxd\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])

        else:
            # means should shrink for each PTV
 
            for i,item in enumerate(self.element['# mxd\n']):
                
                if item.split('=')[0] == '        isoconstraint':
                    self.element['# mxd\n'][i] = ''.join(['        isoconstraint=',str(Dose),'\n' ])   
                                 
                elif item.split('=')[0] == '        weight':
                    self.element['# mxd\n'][i] = ''.join(['        weight=',str(Weight),'\n'])
        
                elif item.split('=')[0] == '        applyshrinkmargintooars':
                    self.element['# mxd\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])     
                   
                elif item.split('=')[0] == '        groupmargins':
              
                    for j,jtem in enumerate(list(reversed(self.tar_nam))):
                        
                        self.element['# mxd\n'].insert(i+1,'        !END\n')
                        self.element['# mxd\n'].insert(i+1,'            targetmargin='+str(Shrink_margin)+'\n') 
                        self.element['# mxd\n'].insert(i+1,'            shrinkmargintarget='+jtem+'\n')             
                        self.element['# mxd\n'].insert(i+1,'        !SHRINKMARGINTARGET\n')
                                                                       

        return self.element['# mxd\n']



    def modify_qod_551(self,Dose,RMS,Shrink_margin,Opti_all,LABEL):

        '''
        quadratic overdose
        self.tar_nam = ['PGTVprn','PGTVnx','PGTVnd','PCTV']
        LABEL: define the cost function in which structure,
        LABEL = e.g. [('PGTVnx',0.95,61.6),'TARGET')], ('Spinal Cord','OARs'),('patient','BODY')
        '''
        import math
        # initialization of cost functions
        self.element = self.Read_HYP_element()
        
        if LABEL[1] == 'OARs':
            # indicate the order in optimization
        
            if Opti_all == 1:
                # means all structure voxels would be considered in
                
                for i,item in enumerate(self.element['# oq\n']):
                    
                    if item.split('=')[0] == '        thresholddose':
                        self.element['# oq\n'][i] = ''.join(['        thresholddose=',str(Dose),'\n']) 
                                     
                    elif item.split('=')[0] == '        isoconstraint':
                        self.element['# oq\n'][i] = ''.join(['        isoconstraint=',str(RMS),'\n']) 
            
                    elif item.split('=')[0] == '        applyshrinkmargintooars':
                        self.element['# oq\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])
                                 
            else:
                # means should shrink for each PTV
     
                for i,item in enumerate(self.element['# oq\n']):
                    
                    if item.split('=')[0] == '        thresholddose':
                        self.element['# oq\n'][i] = ''.join(['        thresholddose=',str(Dose),'\n']) 
                                     
                    elif item.split('=')[0] == '        isoconstraint':
                        self.element['# oq\n'][i] = ''.join(['        isoconstraint=',str(RMS),'\n']) 
            
                    elif item.split('=')[0] == '        applyshrinkmargintooars':
                        self.element['# oq\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])     
              
                    elif item.split('=')[0] == '        groupmargins':
                  
                        for j,jtem in enumerate(list(reversed(self.tar_nam))):
                            
                            self.element['# oq\n'].insert(i+1,'        !END\n')
                            self.element['# oq\n'].insert(i+1,'            targetmargin='+str(Shrink_margin)+'\n') 
                            self.element['# oq\n'].insert(i+1,'            shrinkmargintarget='+jtem+'\n')             
                            self.element['# oq\n'].insert(i+1,'        !SHRINKMARGINTARGET\n')
                                     
        elif LABEL[1] == 'TARGET':
            # indicate the order in optimization
        
            if Opti_all == 1:
                # means all structure voxels would be considered in
                
                for i,item in enumerate(self.element['# oq\n']):
                    
                    if item.split('=')[0] == '        thresholddose':
                        self.element['# oq\n'][i] = ''.join(['        thresholddose=',str(Dose),'\n']) 
                                     
                    elif item.split('=')[0] == '        isoconstraint':
                        self.element['# oq\n'][i] = ''.join(['        isoconstraint=',str(RMS),'\n']) 
            
                    elif item.split('=')[0] == '        applyshrinkmargintooars':
                        self.element['# oq\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])
                                 
            else:
                # means should shrink for each PTV
     
                for i,item in enumerate(self.element['# oq\n']):
                    
                    if item.split('=')[0] == '        thresholddose':
                        self.element['# oq\n'][i] = ''.join(['        thresholddose=',str(Dose),'\n']) 
                                     
                    elif item.split('=')[0] == '        isoconstraint':
                        self.element['# oq\n'][i] = ''.join(['        isoconstraint=',str(RMS),'\n']) 
            
                    elif item.split('=')[0] == '        applyshrinkmargintooars':
                        self.element['# oq\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])     
              
                    elif item.split('=')[0] == '        groupmargins':
                        
                        ind = self.tar_nam.index(LABEL[0])
                        print('target name index:',ind)
                        tar_name = self.tar_nam[:ind]
                  
                        for j,jtem in enumerate(list(reversed(tar_name))):
                            
                            Shrink_margin = round(abs(self.tar[ind-1-j][-1]-Dose)*0.5,1)
                            print(Shrink_margin)
                            self.element['# oq\n'].insert(i+1,'        !END\n')
                            self.element['# oq\n'].insert(i+1,'            targetmargin='+str(Shrink_margin)+'\n') 
                            self.element['# oq\n'].insert(i+1,'            shrinkmargintarget='+jtem+'\n')             
                            self.element['# oq\n'].insert(i+1,'        !SHRINKMARGINTARGET\n')

        if LABEL[1] == 'BODY':
            # indicate the order in optimization
        
            if Opti_all == 1:
                # means all structure voxels would be considered in
                
                for i,item in enumerate(self.element['# oq\n']):
                    
                    if item.split('=')[0] == '        thresholddose':
                        self.element['# oq\n'][i] = ''.join(['        thresholddose=',str(Dose),'\n']) 
                                     
                    elif item.split('=')[0] == '        isoconstraint':
                        self.element['# oq\n'][i] = ''.join(['        isoconstraint=',str(RMS),'\n']) 
            
                    elif item.split('=')[0] == '        applyshrinkmargintooars':
                        self.element['# oq\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])
                                 
            else:
                # means should shrink for each PTV
     
                for i,item in enumerate(self.element['# oq\n']):
                    
                    if item.split('=')[0] == '        thresholddose':
                        self.element['# oq\n'][i] = ''.join(['        thresholddose=',str(Dose),'\n']) 
                                     
                    elif item.split('=')[0] == '        isoconstraint':
                        self.element['# oq\n'][i] = ''.join(['        isoconstraint=',str(RMS),'\n']) 
            
                    elif item.split('=')[0] == '        applyshrinkmargintooars':
                        self.element['# oq\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])     
              
                    elif item.split('=')[0] == '        groupmargins':
                  
                        for j,jtem in enumerate(list(reversed(self.tar_nam))):
                            
                            Shrink_margin = math.floor(abs(self.tar[3-j][-1]-Dose)/2)
                            self.element['# oq\n'].insert(i+1,'        !END\n')
                            self.element['# oq\n'].insert(i+1,'            targetmargin='+str(Shrink_margin)+'\n') 
                            self.element['# oq\n'].insert(i+1,'            shrinkmargintarget='+jtem+'\n')             
                            self.element['# oq\n'].insert(i+1,'        !SHRINKMARGINTARGET\n')
                             
        return self.element['# oq\n']

    def modify_ov_551(self,Ref_dose,Volume,Weight,Shrink_margin,Opti_all):
    
        '''
           Overdose DVH function
        '''
        # initialization of cost functions
        self.element = self.Read_HYP_element()
        
        if Opti_all == 1:
        
            for i,item in enumerate(self.element['# ov\n']):
                
                if item.split('=')[0] == '        isoconstraint':
                    self.element['# ov\n'][i] = ''.join(['        isoconstraint=',str(Volume),'\n'])
                                 
                elif item.split('=')[0] == '        weight':
                    self.element['# ov\n'][i] = ''.join(['        weight=',str(Weight),'\n'])
                                 
                elif item.split('=')[0] == '        thresholddose':
                    self.element['# ov\n'][i] = ''.join(['        thresholddose=',str(Ref_dose),'\n'])

                elif item.split('=')[0] == '        applyshrinkmargintooars':
                    self.element['# ov\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])
                                 
        else:
            
            for i,item in enumerate(self.element['# ov\n']):
                
                if item.split('=')[0] == '        isoconstraint':
                    self.element['# ov\n'][i] = ''.join(['        isoconstraint=',str(Volume),'\n'])
                                 
                elif item.split('=')[0] == '        weight':
                    self.element['# ov\n'][i] = ''.join(['        weight=',str(Weight),'\n'])
                                 
                elif item.split('=')[0] == '        thresholddose':
                    self.element['# ov\n'][i] = ''.join(['        thresholddose=',str(Ref_dose),'\n'])

                elif item.split('=')[0] == '        applyshrinkmargintooars':
                    self.element['# ov\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])    
                                 
                elif item.split('=')[0] == '        groupmargins':
              
                    for j,jtem in enumerate(list(reversed(self.tar_nam))):
                        
                        self.element['# ov\n'].insert(i+1,'        !END\n')
                        self.element['# ov\n'].insert(i+1,'            targetmargin='+str(Shrink_margin)+'\n') 
                        self.element['# ov\n'].insert(i+1,'            shrinkmargintarget='+jtem+'\n')             
                        self.element['# ov\n'].insert(i+1,'        !SHRINKMARGINTARGET\n')      

        return self.element['# ov\n']

    def modify_uv_551(self,Ref_dose,Volume,Weight,Shrink_margin,Opti_all):
    
        '''
           Underdose DVH function
        '''
        # initialization of cost functions
        self.element = self.Read_HYP_element()
        
        if Opti_all == 1:
        
            for i,item in enumerate(self.element['# uv\n']):
                
                if item.split('=')[0] == '        isoconstraint':
                    self.element['# uv\n'][i] = ''.join(['        isoconstraint=',str(Volume),'\n'])
                                 
                elif item.split('=')[0] == '        weight':
                    self.element['# uv\n'][i] = ''.join(['        weight=',str(Weight),'\n'])
                                 
                elif item.split('=')[0] == '        thresholddose':
                    self.element['# uv\n'][i] = ''.join(['        thresholddose=',str(Ref_dose),'\n'])

                elif item.split('=')[0] == '        applyshrinkmargintooars':
                    self.element['# uv\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])
                                 
        else:
            
            for i,item in enumerate(self.element['# se\n']):
                
                if item.split('=')[0] == '        isoconstraint':
                    self.element['# uv\n'][i] = ''.join(['        isoconstraint=',str(Volume),'\n'])
                                 
                elif item.split('=')[0] == '        weight':
                    self.element['# uv\n'][i] = ''.join(['        weight=',str(Weight),'\n'])
                                 
                elif item.split('=')[0] == '        thresholddose':
                    self.element['# uv\n'][i] = ''.join(['        thresholddose=',str(Ref_dose),'\n'])

                elif item.split('=')[0] == '        applyshrinkmargintooars':
                    self.element['# uv\n'][i] = ''.join(['        applyshrinkmargintooars=',str(1-Opti_all),'\n'])    
                                 
                elif item.split('=')[0] == '        groupmargins':
              
                    for j,jtem in enumerate(list(reversed(self.tar_nam))):
                        
                        self.element['# uv\n'].insert(i+1,'        !END\n')
                        self.element['# uv\n'].insert(i+1,'            targetmargin='+str(Shrink_margin)+'\n') 
                        self.element['# uv\n'].insert(i+1,'            shrinkmargintarget='+jtem+'\n')             
                        self.element['# uv\n'].insert(i+1,'        !SHRINKMARGINTARGET\n')      

        return self.element['# uv\n']

    def DVH_Stat_Extract_JSON(self,DVH_JSON):
        
        '''
           This function was develped to extract DVH statistics from JSON
            e.g.
            self.dvh_stat_calc = {'PCTV': [['V50.4Gy > 95%', 0.98, 1.12, '9']],
                                 'Mandible': [['D50% < 35Gy', 30, 0.67, '7'], ['D2cc < 60Gy', 56, 0.88, '8']]}
            
            self.protocol_dict = {'PCTV': [['V50.4Gy', 0.95, '9']],
                                 'Mandible': [['D50%', '35Gy', '7'], ['D2cc', '60Gy', '8']]}


        '''
        import json 
        self.dvh_stat_calc = {item:[] for item in self.protocol_dict.keys()}

        with open(DVH_JSON,'r', encoding='UTF-8') as f:
            load_dict = json.load(f)

        for i,item in enumerate(load_dict['StatisticsOfStructureList']):

            if item['StructureName'] in self.protocol_dict.keys():
                
                for j,jtem in enumerate(load_dict['StatisticsOfStructureList'][i]['DoseInfoList']):
                    
                    calc_dose = round(float(jtem['RefDose'])/100,2)
                    print(self.protocol_dict[item['StructureName']],j,item['StructureName'],jtem['DosimetricCriterion'])

                    if jtem['DosimetricCriterion'] != None:
                        if type(self.protocol_dict[item['StructureName']][j][1]) == float:

                            diff_indx = round(calc_dose/float(self.protocol_dict[item['StructureName']][j][1]),5)
                            self.dvh_stat_calc[item['StructureName']].append([jtem['DosimetricCriterion'],
                                                                            calc_dose, diff_indx,
                                                                            self.protocol_dict[item['StructureName']][j][-1]])

                        elif type(self.protocol_dict[item['StructureName']][j][1]) == str:
                            diff_indx = round(calc_dose/float(self.protocol_dict[item['StructureName']][j][1].split('Gy')[0]),5)
                            self.dvh_stat_calc[item['StructureName']].append([jtem['DosimetricCriterion'],
                                                                            calc_dose, diff_indx,
                                                                            self.protocol_dict[item['StructureName']][j][-1]])

        return self.dvh_stat_calc

    def read_template(self):
        
        '''
           1) Read template.hyp file and transfer to another Data format
           2) Extract isoconstraint information from Data format
           Need further changes for read_template
        '''
        
        self.line,self.strt,self.pointer,self.dose_eng_index ,self.strt_index= [],[],[],[],[]
        self.strt_fun = {}
     
        with open(self.hyp_path, "r+") as f:
            
          line1 = f.readline()
          
          self.line.append(line1)
          
          while line1:
              
            self.pointer.append(f.tell())  #record the pointer loaction to help write
            
            line1 = f.readline()
            
            self.line.append(line1)
    
        # mark place of structure in line
        self.strt_index = [i for i,a in enumerate(self.line) if a=='!VOIDEF\n']
        
        self.dose_eng_index = [i for i,a in enumerate(self.line) if a=='!DOSE_ENGINES\n']
        
        count = len(self.strt_index)
        
        self.strt = [self.line[j+1][9:-1] for j in self.strt_index]
                
        # list_fun record number of cost function and type    
        for index in range(count):
            
            count_fun = 0
            
            list_fun = []
            
            indx = [4,6,9,10,13,16,18,19,20,23,21,22] #? what's this mean
            
            type_cost = ['type=se','type=pa','type=mxd','type=po','type=qp','type=conf','type=o_q','type=u_q','type=u_v','type=o_v']
            
            if index == count-1:
                
                for flag in range(self.strt_index[index],self.dose_eng_index[0]):
                    
                    if self.line[flag] == '    !COSTFUNCTION\n':
                        
                        count_fun = count_fun + 1
                        
                        list_fun.append([self.line[flag+1][8:-1],flag+1])
                        
                        # cost functions differ with flag+1
                        if self.line[flag+1][8:-1] in type_cost:
                            
                            for item in indx:
                                
                                list_fun.append([self.line[flag+item][8:-1],flag+item])                               
            else:
                
                for flag in range(self.strt_index[index],self.strt_index[index+1]):
                    
                    if self.line[flag] == '    !COSTFUNCTION\n':
                        
                        count_fun = count_fun + 1
                        
                        list_fun.append([self.line[flag+1][8:-1],flag+1])
                        
                        if self.line[flag+1][8:-1] in type_cost:
                            
                            for item in indx:
                                
                                list_fun.append([self.line[flag+item][8:-1],flag+item])
                       
            list_fun.append(count_fun)
            
            self.strt_fun[self.strt[index]] = list_fun    
    
        return self.strt_fun,self.strt_index,self.line



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
        OARs_level5 = ['R1','R2','R3','R4','R5','R6','R7','R8','R9']  # ring structures

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
                    
                    cf1 = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*1.5,Weight=0.01,
                                     Shrink_margin=3,Opti_all=0,Powe_Law=15)
                    OARs = OARs + part2 + cf1[:-1]
                    
                    
                    cf2 = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
                                     Shrink_margin=0,Opti_all=0,Powe_Law=1)
                    OARs = OARs + cf2[:-1]
                    
                    
                    OARs.append('!END\n') 
                    
                else:
                    
                    cf1 = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
                                     Shrink_margin=0,Opti_all=0,Powe_Law=15)


                    OARs = OARs + part2 + cf1[:-1]
                    OARs.append('!END\n')                      
           
            elif item in OARs_level4:
                
                # setting a serial CFs if it don't appear D50%, else setting one parallel CFs
                part2[1] = '    name=' + item +'\n'
                
                if len(self.protocol_dict[item]) == 1:
                    # only one statistics DVH evaluation index
                    if '50%' not in self.protocol_dict[item][0][0].split('D'):
                        
                        cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
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
                                
                                cf1 = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),
                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=12)
                                
                                cf2 = self.modify_mxd(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
                                      Opti_all=0,Shrink_margin=0)
                                
                                cf = cf1[:-1] + cf2[:-1]
                            
                        elif '%' in key[0]:
                            
                            if float(key[0].split('D')[1].split('%')[0]) <= 60 and float(key[0].split('D')[1].split('%')[0]) > 40:
                                
                                cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),
                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=1)
                                
                            elif float(key[0].split('D')[1].split('%')[0]) <= 40 and float(key[0].split('D')[1].split('%')[0]) > 20:

                                cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.99,
                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=10)
                                
                            elif float(key[0].split('D')[1].split('%')[0]) <= 20 and float(key[0].split('D')[1].split('%')[0]) > 10:

                                cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.98,
                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=15)
                                
                            elif float(key[0].split('D')[1].split('%')[0]) <= 10:

                                cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.97,
                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=20)
                            
                            cf = cf[:-1]
                        
                        CF = CF + cf

                    OARs = OARs + part2 + CF
                    OARs.append('!END\n')                           
            
            elif item in OARs_level5:
                
                part2[1] = '    name=' + item +'\n'
                
                cf = self.modify_mxd(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
                                      Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
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

    def hyp_solution_NPC_V1(self,grid,fractions,prescription_dose,delivery_type):
        
        '''
           hyp_solution_NPC used for Head and neck cases
           tar = [('PGTVrpn', 0.95, 61.6),
             ('PGTVnx', 0.95, 61.6),
             ('PGTVnd', 0.95, 59.36),
             ('PCTV', 0.95, 50.4)]
           
           OARs_level1 = ['Brain Stem','Spinal Cord']
           OARs_level2 = ['Optical Chiasm','Optical Nerve R','Optical Nerve L','Lens R','Lens L']
           OARs_level3 = ['Eye R','Eye L','Parotid R','Parotid L',,'Pituitary','Brain']
           OARs_level4 = ['T.Joint R','T.Joint L','T.Lobe R','T.Lobe L','Larynx','A.D L','A.D R','Mandible','Oral Cavity','Lung']  
        '''
        
        self.template_line = []
        
        # deal with target
        tar = [(key,self.protocol_dict[key][0][1],
                float(self.protocol_dict[key][0][0].split('V')[1].split('Gy')[0]))
           for key in self.protocol_dict.keys() if 'PCTV' in key or 'PGTV' in key or 'GTV' in key]
        tar.sort(key=lambda x:x[2],reverse = True)
        self.tar_nam = [item[0] for item in tar]
        
        sorted_name = self.name_sorting()
        OARs_nam = [item for item in sorted_name if item not in self.tar_nam and item in self.protocol_dict.keys()] + ['R6','R7']
        prep_name = self.tar_nam + OARs_nam +['BODY']
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
                tar_pen = self.modify_qp_551(Vol = item[1],Dose = item[2],Weight = 1.0,Opti_all = 1,Surf_margin = 0)
                
                # setting quadratic overdose
                qod = self.modify_qod_551(Dose = int(item[2]+1.5),RMS = 0.25,Shrink_margin = 0,Opti_all = 0)
                
                # combine them together
                target = target + part2 + tar_pen[:-1] + qod[:-1]
                target.append('!END\n')
                
            else:   ## external target
                
                part2[1] = '    name=' + item[0] +'\n'  
                
                # setting target penalty
                tar_pen_ext = self.modify_qp_551(Vol = item[1],Dose = item[2],Weight = 1.0,Opti_all = 1,Surf_margin = 0)
                target = target + part2 + tar_pen_ext[:-1]
                
                # first quadratic overdose to contrain inner target reigon to prevent hot dose release to low dose region
                qod1 = self.modify_qod_551(Dose = tar[i-1][-1],RMS = 0.25,Shrink_margin = 0,Opti_all = 0)
                target = target + qod1[:-1]
                
                # second quadratic overdose to constarin 110% percent of external target dose region
                qod2 = self.modify_qod(Dose = int(item[2]*1.1),RMS = 0.5,Shrink_margin = grid)
                target = target + qod2[:-1]
                
                # third quadratic overdose to constrain 102% percent of external target dose region
                qod3 = self.modify_qod(Dose = int(item[2]*1.02),RMS = 0.75,Shrink_margin = grid*2)
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
            
            if item == 'Brain Stem':
                
                part2[1] = '    name=' + item +'\n'
                
                # select the maximum value from protocol request and 0.8*prescription dose
                max_dose = max(float(self.protocol_dict[item][0][1].split('Gy')[0]),
                               0.8*tar[0][-1])
                
                # select CF: maximum                
                cf = self.modify_mxd(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 
                
            elif item == 'Spinal Cord':
                                
                part2[1] = '    name=' + item +'\n'                

                # select the maximum value from protocol request and 0.75*prescription dose
                max_dose = max(float(self.protocol_dict[item][0][1].split('Gy')[0]),
                               0.75*tar[0][-1])
                
                # select CF:maximum 
                cf = self.modify_mxd(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')  
                                
            elif item == 'Optical Chiasm' or item == 'Optical Nerve L' or item == 'Optical Nerve R':
                
                part2[1] = '    name=' + item +'\n'                

                # select the maximum value from protocol request and 0.75*prescription dose
                max_dose = max(float(self.protocol_dict[item][0][1].split('Gy')[0]),
                               0.75*tar[0][-1])
                
                # select CF:maximum 
                cf = self.modify_mxd(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')  

            elif item == 'Lens R' or item == 'Lens L':
                                 
                part2[1] = '    name=' + item +'\n'                

                # select the maximum value from protocol request
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                
                # select CF:maximum
                cf = self.modify_mxd(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')                  
            
            elif item == 'Eye R' or item == 'Eye L':
                                 
                part2[1] = '    name=' + item +'\n'                


                if '%' in self.protocol_dict[item][0][0]:
                    
                    percent = float(self.protocol_dict[item][0][0].split('D')[1].split('%')[0])
                    
                    if percent < 10: 
                                                
                        # select CF: maximum
                        max_dose =  float(self.protocol_dict[item][0][1].split('Gy')[0])
                        cf = self.modify_mxd(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                        
                    elif percent < 35:
                        
                        # select CF: serial
                        eud_dose = 0.75*tar[0][-1]           
                        cf = self.modify_se(Dose=int(eud_dose),Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=12)                       


                elif 'cc' in self.protocol_dict[item][0][0]:
                    
                    vol = float(self.protocol_dict[item][0][0].split('D')[1].split('cc')[0])
                    
                    if vol < 10: 
                                                
                        # select CF: maximum
                        max_dose =  float(self.protocol_dict[item][0][1].split('Gy')[0])
                        cf = self.modify_mxd(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                        
                    elif vol < 35:
                        
                        # select CF: serial
                        eud_dose = 0.75*tar[0][-1]           
                        cf = self.modify_se(Dose=int(eud_dose),Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=12)    
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')               

            elif item == 'Parotid R' or item == 'Parotid L':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: serial (constrain high dose region)
                eud_dose1 = 0.5*tar[0][-1]
                cf1 = self.modify_se(Dose= eud_dose1,Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1]
            
                # select CF2: serial (constrain mean dose)
                eud_dose2 = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf2 = self.modify_se(Dose= eud_dose2,Weight=0.01,Shrink_margin=0,Opti_all=1,Powe_Law=1) 
                
                OARs = OARs + cf2[:-1]
                OARs.append('!END\n')   

            elif item == 'Oral Cavity':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: serial (constrain high dose region)
                eud_dose = 0.65*tar[0][-1]
                cf1 = self.modify_se(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1] 
                
                # select CF2: serial (constrain mean dose, eud = pro_dose+2Gy)
                eud_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf2 = self.modify_se(Dose= int(eud_dose),Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=1) 

                OARs = OARs + cf2[:-1]
                OARs.append('!END\n')         

            elif item == 'Larynx':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: serial (constrain high dose region)
                eud_dose = 0.65*tar[0][-1]
                cf1 = self.modify_se(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1]
            
                # select CF2: parallel (constrain mean dose, eud = pro_dose+2Gy)
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf2 = self.modify_pa(Ref_dose= int(max_dose),Volume = 50, Weight=0.01,Powe_Law=4,Opti_all=1,Shrink_margin=0) 
                
                OARs = OARs + cf2[:-1]
                OARs.append('!END\n') 
                
            elif item == 'Pitutary' or item == 'Pituitary':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF: Parallel (constrain D50% and optimize all)
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf = self.modify_pa(Ref_dose= int(max_dose),Volume = 50, Weight=0.01,Powe_Law=4,Opti_all=1,Shrink_margin=0) 

                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 

            elif item == 'T.Lobe R' or item == 'T.Lobe L':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF: Serial (constrain high dose region)
                eud_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf1 = self.modify_se(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 

                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')                 
                               
            elif item == 'Brain':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF: Maximum (Constrain D5%)
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf = self.modify_mxd(Dose= int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                        
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')                  
                
            elif item == 'Mandible':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: Quadratic Overdose(Constrain D2cc/Max Dose)
                max_dose = tar[0][-1]
                cf1 = self.modify_qod(Dose= int(max_dose),RMS = 0.25,Shrink_margin = 0) 
                # cf1 = self.modify_mxd(Dose=max_dose,Weight=0.01,Opti_all=1,Shrink_margin=0)
                # cf1 = self.modify_se(Dose= max_dose*0.75,Weight=0.01,Shrink_margin=0.25,Opti_all=0,Powe_Law=12) 
                OARs + part2 + cf1[:-1]
                
                # select CF1: Serial (Constrain D50% dose )
                eud_dose = tar[0][-1]*0.6
                cf2 = self.modify_se(Dose= int(eud_dose),Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=1)    
    
                OARs = OARs + cf2[:-1]
                OARs.append('!END\n') 

            elif item == 'A.D L' or item == 'A.D R' or item == 'T.Joint R' or item == 'T.Joint L':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Parallel (Constrain D50% dose )
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf = self.modify_pa(Ref_dose= int(max_dose),Volume = 50, Weight=0.01,Powe_Law=4,Opti_all=0,Shrink_margin=0)   
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')

            elif item == 'Lung':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Serial (Constrain high dose )
                eud_dose = tar[0][-1]*0.6
                cf = self.modify_se(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')  

            # assistance structure like SPPRV,BSPRV,R6,R7
            elif item == 'SPPRV':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Maximum (Constrain high dose )
                max_dose = tar[-1][-1]*0.6
                cf = self.modify_mxd(Dose= int(max_dose), Weight=0.01, Opti_all=1, Shrink_margin=0)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 

            elif item == 'BSPRV':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Maximum (Constrain high dose )
                max_dose = tar[-1][-1]*0.7
                cf = self.modify_mxd(Dose= int(max_dose), Weight=0.01, Opti_all=1, Shrink_margin=0)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 

            elif item == 'R6' or item == 'R7':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Maximum (Constrain high dose )
                max_dose = tar[-1][-1]*0.7
                cf = self.modify_mxd(Dose= int(max_dose), Weight=0.01, Opti_all=1, Shrink_margin=0)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')
                   
#            if item in OARs_level1:
#                
#                # setting a serial and maximum cost function 
#                part2[1] = '    name=' + item +'\n'
#                
#                # CF: serial to contrain high dose region
#                cf1 = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.90,Weight=0.01,
#                                     Shrink_margin=0,Opti_all=0,Powe_Law=12)
#                
#                # CF: maximum to constrain maximum point 
#                if 'max' in self.protocol_dict[item][0][0].split('D')[1]:
#                    
#                    cf2 = self.modify_mxd(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
#                                      Opti_all=1,Shrink_margin=0)
#                    
#                elif '0.1cc' in self.protocol_dict[item][0][0].split('D')[1]:
#                    
#                    cf2 = self.modify_mxd(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.9,Weight=0.01,
#                                      Opti_all=1,Shrink_margin=0)     
#                else:
#                    
#                    cf2 = self.modify_mxd(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
#                                      Opti_all=1,Shrink_margin=0)
#                
#                
#                OARs = OARs + part2 + cf1[:-1] + cf2[:-1]
#                OARs.append('!END\n')                           
#
#                                                      
#            elif item in OARs_level2:
#                
#                # setting a maximum CF if Dx% < D5%, else setting a serial CF
#                part2[1] = '    name=' + item +'\n'
#                
#                cf = self.modify_mxd(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
#                                      Opti_all=1,Shrink_margin=0)
#                
#                OARs = OARs + part2 + cf[:-1]
#                OARs.append('!END\n') 
#                
#            elif item in OARs_level3:
#                
#                # setting two serial CFs if it appears D50%, else setting one serial CF
#                part2[1] = '    name=' + item +'\n'
#                
#                if '50%' in self.protocol_dict[item][0][0].split('D'):
#                    
#                    cf1 = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*1.5,Weight=0.01,
#                                     Shrink_margin=3,Opti_all=0,Powe_Law=15)
#                    OARs = OARs + part2 + cf1[:-1]
#                    
#                    
#                    cf2 = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
#                                     Shrink_margin=0,Opti_all=0,Powe_Law=1)
#                    OARs = OARs + cf2[:-1]
#                    
#                    
#                    OARs.append('!END\n') 
#                    
#                else:
#                    
#                    cf1 = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
#                                     Shrink_margin=0,Opti_all=0,Powe_Law=15)
#
#
#                    OARs = OARs + part2 + cf1[:-1]
#                    OARs.append('!END\n')                      
#           
#            elif item in OARs_level4:
#                
#                # setting a serial CFs if it don't appear D50%, else setting one parallel CFs
#                part2[1] = '    name=' + item +'\n'
#                
#                if len(self.protocol_dict[item]) == 1:
#                    # only one statistics DVH evaluation index
#                    if '50%' not in self.protocol_dict[item][0][0].split('D'):
#                        
#                        cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
#                                     Shrink_margin=3,Opti_all=0,Powe_Law=12)
#                        
#                    elif '50%' in self.protocol_dict[item][0][0].split('D'):
#                        
#                        cf = self.modify_pa(Ref_dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Volume = 50,
#                                             Weight=0.01,Powe_Law=4,Opti_all=0,Shrink_margin=0) 
#                        
#                    OARs = OARs + part2 + cf[:-1]
#                    OARs.append('!END\n')   
#                    
#                else:
#                    
#                    # DVH statistics indices more than one
#                    CF = []
#
#                    for key in self.protocol_dict[item]:
#                        
#                        if 'cc' in key[0]:
#                            
#                            if float(key[0].split('D')[1].split('cc')[0]) <= 10:
#                                
#                                cf1 = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),
#                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=12)
#                                
#                                cf2 = self.modify_mxd(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
#                                      Opti_all=0,Shrink_margin=0)
#                                
#                                cf = cf1[:-1] + cf2[:-1]
#                            
#                        elif '%' in key[0]:
#                            
#                            if float(key[0].split('D')[1].split('%')[0]) <= 60 and float(key[0].split('D')[1].split('%')[0]) > 40:
#                                
#                                cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),
#                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=1)
#                                
#                            elif float(key[0].split('D')[1].split('%')[0]) <= 40 and float(key[0].split('D')[1].split('%')[0]) > 20:
#
#                                cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.99,
#                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=10)
#                                
#                            elif float(key[0].split('D')[1].split('%')[0]) <= 20 and float(key[0].split('D')[1].split('%')[0]) > 10:
#
#                                cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.98,
#                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=15)
#                                
#                            elif float(key[0].split('D')[1].split('%')[0]) <= 10:
#
#                                cf = self.modify_se(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0])*0.97,
#                                                    Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=20)
#                            
#                            cf = cf[:-1]
#                        
#                        CF = CF + cf
#
#                    OARs = OARs + part2 + CF
#                    OARs.append('!END\n')                           
#            
#            elif item in OARs_level5:
#                
#                part2[1] = '    name=' + item +'\n'
#                
#                cf = self.modify_mxd(Dose=float(self.protocol_dict[item][0][1].split('Gy')[0]),Weight=0.01,
#                                      Opti_all=1,Shrink_margin=0)
#                
#                OARs = OARs + part2 + cf[:-1]
#                OARs.append('!END\n') 
                
                           
            elif item == 'BODY' or item == 'Patient' or item == 'Body': ## patient
                
                part2[1] = '    name=' + item +'\n'
                
                ## global maximum dose
                mxd1 = self.modify_mxd(Dose= int(tar[0][-1]*1.1), Weight=0.01, Opti_all=1, Shrink_margin=0)
                OARs = OARs + part2 + mxd1[:-1]
                
                ## the outer target dose
                QOD1 = self.modify_qod(Dose = int(tar[-1][-1]), RMS = 0.5, Shrink_margin = 0)
                OARs = OARs + QOD1[:-1]
                
                QOD2 = self.modify_qod(Dose = int(tar[-1][-1])-5, RMS = 0.75, Shrink_margin = grid)
                OARs = OARs + QOD2[:-1]

                QOD3 = self.modify_qod(Dose = int(tar[-1][-1])-10, RMS = 1, Shrink_margin = grid*2)
                OARs = OARs + QOD3[:-1]

                QOD4 = self.modify_qod(Dose = int(tar[-1][-1])-15, RMS = 1.25, Shrink_margin = grid*3)
                OARs = OARs + QOD4[:-1]

                QOD5 = self.modify_qod(Dose = int(tar[-1][-1])-20, RMS = 1.5, Shrink_margin = grid*4)
                OARs = OARs + QOD5[:-1]                
                
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
            # IMRT 9beams step&shoot
            part4 = self.element['# Part4_IMRT\n'][:-1]
        
        ## ============================ part5 ============================== ##
        part5 = self.element['# Part5\n'][:-1]
        for i,item in enumerate(part5):
            if 'FRACTIONS' in item:
                part5[i] = ''.join(['!FRACTIONS    ',str(fractions),'\n'])
            
            elif 'PRESCRIPTION' in item:
                part5[i] = ''.join(['!PRESCRIPTION    ',str(float(prescription_dose)),'\n'])
                
            elif 'DOSEGRIDSIZE' in item:
                part5[i] = ''.join(['!DOSEGRIDSIZE    ',str(float(grid)),'\n'])
            
#            elif 'MAXNARCS' in item:
#                part5[i] = ''.join(['!MAXNARCS    ',str(float(ARCS)),'\n'])
        
        ## ================== template ==================== ##        
        self.template_line = self.template_line + part1 + target + OARs + part3 + part4 + part5
        
        print('###############################')
        print('template has been generated !')
        print('###############################')
              
        
        return self.template_line   

    def hyp_solution_NPC_V2(self,grid,fractions,prescription_dose,delivery_type):
        
        '''
          This is another version of NPC model
        '''
        self.template_line = []
        
        # deal with target
        self.tar = [(key,self.protocol_dict[key][0][1],
                float(self.protocol_dict[key][0][0].split('V')[1].split('Gy')[0]))
           for key in self.protocol_dict.keys() if 'PCTV' in key or 'PGTV' in key or 'GTV' in key]
        self.tar.sort(key=lambda x:x[2],reverse = True)
        self.tar_nam = [item[0] for item in self.tar]
        
        sorted_name = self.name_sorting()
#        OARs_nam = [item for item in sorted_name if item not in self.tar_nam and item in self.protocol_dict.keys()] + ['R6','R7']
        OARs_nam = [item for item in sorted_name if item not in self.tar_nam and item in self.protocol_dict.keys()] + ['PostAvoid','TracheaAvoid']
        prep_name = self.tar_nam + OARs_nam +['BODY']
        OARs_nam = OARs_nam + ['BODY']  
        ## ============================ part1 ============================== ##
        part1 = ['000610b6\n','!LAYERING\n'] # Monaco5.51 serial number: 000610b6
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
        for i,item in enumerate(self.tar):
            
            if i != len(self.tar)-1:  ## inner target 
                
                part2[1] = '    name=' + item[0] +'\n'

                # setting target penalty
                tar_pen = self.modify_qp_551(Vol = item[1],Dose = item[2],Weight = 1.0,Opti_all = 1,Surf_margin = 0)
                
                # setting quadratic overdose
                qod = self.modify_qod_551(Dose = int(item[2]+1.5),RMS = 0.25,Shrink_margin = 0,Opti_all = 0,LABEL = [item[0],'TARGET'])
                
                # combine them together
                target = target + part2 + tar_pen[:-1] + qod[:-1]
                target.append('!END\n')
                
            else:   ## external target
                
                part2[1] = '    name=' + item[0] +'\n'  
                
                # setting target penalty
                tar_pen_ext = self.modify_qp_551(Vol = item[1],Dose = item[2],Weight = 1.0,Opti_all = 1,Surf_margin = 0)
                target = target + part2 + tar_pen_ext[:-1]
                
                # first quadratic overdose to contrain inner target reigon to prevent hot dose release to low dose region
                qod1 = self.modify_qod_551(Dose = self.tar[i-1][-1],RMS = 0.25,Shrink_margin = 0,Opti_all = 0,LABEL =[item[0],'TARGET'])
                target = target + qod1[:-1]
                
                # second quadratic overdose to constarin 110% percent of external target dose region
                qod2 = self.modify_qod_551(Dose = int(item[2]*1.1),RMS = 0.5,Shrink_margin = grid*2, Opti_all= 0,LABEL =[item[0],'TARGET'])
                target = target + qod2[:-1]
                
                # third quadratic overdose to constrain 102% percent of external target dose region
                qod3 = self.modify_qod_551(Dose = int(item[2]*1.02),RMS = 1,Shrink_margin = grid*3, Opti_all = 0,LABEL =[item[0],'TARGET'])
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
            
            if item == 'Brain Stem':
                
                part2[1] = '    name=' + item +'\n'
                
                # select the maximum value from protocol request and 0.8*prescription dose
                max_dose = max(float(self.protocol_dict[item][0][1].split('Gy')[0]),
                               0.8*self.tar[0][-1])
                
                # select CF: maximum                
                cf = self.modify_mxd_551(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 
                
            elif item == 'Spinal Cord':
                                
                part2[1] = '    name=' + item +'\n'                

                # select the maximum value from protocol request and 0.75*prescription dose
                max_dose = max(float(self.protocol_dict[item][0][1].split('Gy')[0]),
                               0.75*self.tar[0][-1])
                
                # select CF:maximum 
                cf = self.modify_mxd_551(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')  
                                
            elif item == 'Optical Chiasm' or item == 'Optical Nerve L' or item == 'Optical Nerve R':
                
                part2[1] = '    name=' + item +'\n'                

                # select the maximum value from protocol request and 0.75*prescription dose
                max_dose = max(float(self.protocol_dict[item][0][1].split('Gy')[0]),
                               0.75*self.tar[0][-1])
                
                # select CF:maximum 
                cf = self.modify_mxd_551(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')  

            elif item == 'Lens R' or item == 'Lens L':
                                 
                part2[1] = '    name=' + item +'\n'                

                # select the maximum value from protocol request
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                
                # select CF:maximum
                cf = self.modify_mxd_551(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')                  
            
            elif item == 'Eye R' or item == 'Eye L':
                                 
                part2[1] = '    name=' + item +'\n'                


                if '%' in self.protocol_dict[item][0][0]:
                    
                    percent = float(self.protocol_dict[item][0][0].split('D')[1].split('%')[0])
                    
                    if percent < 10: 
                                                
                        # select CF: maximum
                        max_dose =  float(self.protocol_dict[item][0][1].split('Gy')[0])
                        cf = self.modify_mxd_551(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                        
                    elif percent < 35:
                        
                        # select CF: serial
                        eud_dose = 0.8*self.tar[0][-1]           
                        cf = self.modify_se_551(Dose=int(eud_dose),Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=12)                       

                    else:
                        
                        # select CF: serial
                        eud_dose = 0.8*self.tar[0][-1]           
                        cf = self.modify_se_551(Dose=int(eud_dose),Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=12)      
                        
                elif 'cc' in self.protocol_dict[item][0][0]:
                    
                    vol = float(self.protocol_dict[item][0][0].split('D')[1].split('cc')[0])
                    
                    if vol < 10: 
                                                
                        # select CF: maximum
                        max_dose =  float(self.protocol_dict[item][0][1].split('Gy')[0])
                        cf = self.modify_mxd_551(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                        
                    elif vol < 35:
                        
                        # select CF: serial
                        eud_dose = 0.75*self.tar[0][-1]           
                        cf = self.modify_se_551(Dose=int(eud_dose),Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=12)    

                    else:
                        
                        # select CF: serial
                        eud_dose = 0.75*self.tar[0][-1]           
                        cf = self.modify_se_551(Dose=int(eud_dose),Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=12)    
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')               

            elif item == 'Parotid R' or item == 'Parotid L':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: serial (constrain high dose region)
                eud_dose1 = 0.5*self.tar[0][-1]
                cf1 = self.modify_se_551(Dose= eud_dose1,Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1]
            
                # select CF2: serial (constrain mean dose)
                eud_dose2 = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf2 = self.modify_se_551(Dose= eud_dose2+2,Weight=0.01,Shrink_margin=0,Opti_all=1,Powe_Law=1) 
                
                OARs = OARs + cf2[:-1]
                OARs.append('!END\n')   

            elif item == 'Oral Cavity':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: serial (constrain high dose region)
                eud_dose = 0.65*self.tar[0][-1]
                cf1 = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1] 
                
                # select CF2: serial (constrain mean dose, eud = pro_dose+2Gy)
                eud_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])+2
                cf2 = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=1) 

                OARs = OARs + cf2[:-1]
                OARs.append('!END\n')         

            elif item == 'Larynx':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: serial (constrain high dose region)
                eud_dose = 0.65*self.tar[0][-1]
                cf1 = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1]
            
                # select CF2: parallel (constrain mean dose, eud = pro_dose+2Gy)
                eud_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])+2
                cf2 = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=1) 
                
                OARs = OARs + cf2[:-1]
                OARs.append('!END\n') 
                
            elif item == 'Pitutary' or item == 'Pituitary':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF: Parallel (constrain D50% and optimize all)
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf = self.modify_pa_551(Ref_dose= int(max_dose),Volume = 50, Weight=0.01,Powe_Law=4,Opti_all=1,Shrink_margin=0) 

                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 

            elif item == 'T.Lobe R' or item == 'T.Lobe L':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF: Serial (constrain high dose region)
                eud_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf1 = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 

                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')                 
                               
            elif item == 'Brain':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF: Maximum (Constrain D5%)
#                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
#                cf = self.modify_mxd_551(Dose= int(max_dose)+5,Weight=0.01,Opti_all=1,Shrink_margin=grid)
                eud_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])+5
                cf = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                        
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')                  
                
            elif item == 'Mandible':
                
                print('Mandible')
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: Quadratic Overdose(Constrain D2cc/Max Dose)
                max_dose = self.tar[0][-1]
                cf1 = self.modify_qod_551(Dose= int(max_dose),RMS = 0.25,Shrink_margin = grid,Opti_all = 0,LABEL =[item[0],'OARs']) 
                # cf1 = self.modify_mxd(Dose=max_dose,Weight=0.01,Opti_all=1,Shrink_margin=0)
                # cf1 = self.modify_se(Dose= max_dose*0.75,Weight=0.01,Shrink_margin=0.25,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1]
                
                # select CF1: Serial (Constrain D50% dose )
                eud_dose = max(self.tar[0][-1]*0.65,float(self.protocol_dict[item][0][1].split('Gy')[0]))
                cf2 = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=1)    
    
                OARs = OARs + cf2[:-1]
                OARs.append('!END\n') 
                

            elif item == 'A.D L' or item == 'A.D R' or item == 'T.Joint R' or item == 'T.Joint L':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Parallel (Constrain D50% dose )
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf = self.modify_pa_551(Ref_dose= int(max_dose),Volume = 50, Weight=0.01,Powe_Law=4,Opti_all=0,Shrink_margin=0)   
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')

            elif item == 'Lung':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Serial (Constrain high dose )
                eud_dose = max(self.tar[0][-1]*0.6,float(self.protocol_dict[item][0][1].split('Gy')[0]))
                cf = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')  

            # assistance structure like SPPRV,BSPRV,R6,R7
            elif item == 'SPPRV':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Maximum (Constrain high dose )
                max_dose = self.tar[-1][-1]*0.6
                cf = self.modify_mxd_551(Dose= int(max_dose), Weight=0.01, Opti_all=1, Shrink_margin=0)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 

            elif item == 'BSPRV':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Maximum (Constrain high dose )
                max_dose = self.tar[-1][-1]*0.7
                cf = self.modify_mxd_551(Dose= int(max_dose), Weight=0.01, Opti_all=1, Shrink_margin=0)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 

            elif item == 'R6' or item == 'R7' or item == 'PostAvoid' or item == 'TracheaAvoid':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Maximum (Constrain high dose )
                max_dose = self.tar[-1][-1]*0.75
                cf = self.modify_mxd_551(Dose= int(max_dose), Weight=0.01, Opti_all=1, Shrink_margin=0)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')

            elif item == 'BODY' or item == 'Patient' or item == 'Body': ## patient
                
                part2[1] = '    name=' + item +'\n'
                
                ## global maximum dose
                mxd1 = self.modify_mxd_551(Dose= int(self.tar[0][-1]*1.1), Weight=0.01, Opti_all=1, Shrink_margin=0)
                OARs = OARs + part2 + mxd1[:-1]
                
                ## the outer target dose
                QOD1 = self.modify_qod_551(Dose = int(self.tar[-1][-1]), RMS = 0.5, Shrink_margin = 0, Opti_all=0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD1[:-1]
                
                QOD2 = self.modify_qod_551(Dose = int(self.tar[-1][-1])-5, RMS = 0.75, Shrink_margin = grid,Opti_all = 0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD2[:-1]

                QOD3 = self.modify_qod_551(Dose = int(self.tar[-1][-1])-10, RMS = 1, Shrink_margin = grid*2,Opti_all = 0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD3[:-1]

                QOD4 = self.modify_qod_551(Dose = int(self.tar[-1][-1])-15, RMS = 1.25, Shrink_margin = grid*3, Opti_all= 0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD4[:-1]

                QOD5 = self.modify_qod_551(Dose = int(self.tar[-1][-1])-20, RMS = 2.0, Shrink_margin = grid*4, Opti_all = 0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD5[:-1]                
                
                OARs.append('!END\n')
                
        ## ============================ part3 ============================== ##
        part3 = self.element['# Part3\n'][:-1]
        
        ## ============================ part4 ============================== ##
        # here are two selections for part4
        
        if delivery_type == 'VMAT':
            # VMAT 360 ARC
            part4 = self.element['# Part4_VMAT\n'][:-1] 
        elif delivery_type == 'IMRT':
            # IMRT 9beams step&shoot
            part4 = self.element['# Part4_IMRT\n'][:-1]
        
        ## ============================ part5 ============================== ##
        part5 = self.element['# Part5\n'][:-1]
        for i,item in enumerate(part5):
            if 'FRACTIONS' in item:
                part5[i] = ''.join(['!FRACTIONS    ',str(fractions),'\n'])
            
            elif 'PRESCRIPTION' in item:
                part5[i] = ''.join(['!PRESCRIPTION    ',str(float(prescription_dose)),'\n'])
                
            elif 'DOSEGRIDSIZE' in item:
                part5[i] = ''.join(['!DOSEGRIDSIZE    ',str(float(grid)),'\n'])
            
#            elif 'MAXNARCS' in item:
#                part5[i] = ''.join(['!MAXNARCS    ',str(float(ARCS)),'\n'])
        
        ## ================== template ==================== ##        
        self.template_line = self.template_line + part1 + target + OARs + part3 + part4 + part5
        
        print('###############################')
        print('template has been generated !')
        print('###############################')
              
        
        return self.template_line   

    def hyp_solution_NPC_V3(self,grid,fractions,prescription_dose,delivery_type):
        
        '''
          This is another version of NPC model
        '''
        self.template_line = []
        
        # deal with target
        self.tar = [(key,self.protocol_dict[key][0][1],
                float(self.protocol_dict[key][0][0].split('V')[1].split('Gy')[0]))
           for key in self.protocol_dict.keys() if 'PCTV' in key or 'PGTV' in key or 'GTV' in key]
        self.tar.sort(key=lambda x:x[2],reverse = True)
        self.tar_nam = [item[0] for item in self.tar]
        
        sorted_name = self.name_sorting()
#        OARs_nam = [item for item in sorted_name if item not in self.tar_nam and item in self.protocol_dict.keys()] + ['R6','R7']
        OARs_nam = [item for item in sorted_name if item not in self.tar_nam and item in self.protocol_dict.keys()] + ['PostAvoid','TracheaAvoid']
        prep_name = self.tar_nam + OARs_nam +['BODY']
        OARs_nam = OARs_nam + ['BODY']  
        ## ============================ part1 ============================== ##
        part1 = ['000610b6\n','!LAYERING\n'] # Monaco5.51 serial number: 000610b6
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
        for i,item in enumerate(self.tar):
            
            if i != len(self.tar)-1:  ## inner target 
                
                part2[1] = '    name=' + item[0] +'\n'

                # setting target penalty
                tar_pen = self.modify_qp_551(Vol = item[1],Dose = item[2],Weight = 1.0,Opti_all = 1,Surf_margin = 0)
                
                # setting quadratic overdose
                qod = self.modify_qod_551(Dose = int(item[2]+2),RMS = 0.5,Shrink_margin = 0,Opti_all = 0,LABEL = [item[0],'TARGET'])
                
                # combine them together
                target = target + part2 + tar_pen[:-1] + qod[:-1]
                target.append('!END\n')
                
            else:   ## external target
                
                part2[1] = '    name=' + item[0] +'\n'  
                
                # setting target penalty
                tar_pen_ext = self.modify_qp_551(Vol = item[1],Dose = item[2],Weight = 1.0,Opti_all = 1,Surf_margin = 0)
                target = target + part2 + tar_pen_ext[:-1]
                
                # first quadratic overdose to contrain inner target reigon to prevent hot dose release to low dose region
                qod1 = self.modify_qod_551(Dose = self.tar[i-1][-1],RMS = 0.5,Shrink_margin = 0,Opti_all = 0,LABEL =[item[0],'TARGET'])
                target = target + qod1[:-1]
                
                # second quadratic overdose to constarin 110% percent of external target dose region
                qod2 = self.modify_qod_551(Dose = int(item[2]*1.08),RMS = 1,Shrink_margin = grid*2, Opti_all= 0,LABEL =[item[0],'TARGET'])
                target = target + qod2[:-1]
                
                # third quadratic overdose to constrain 102% percent of external target dose region
                qod3 = self.modify_qod_551(Dose = int(item[2]*1.0),RMS = 2,Shrink_margin = grid*3, Opti_all = 0,LABEL =[item[0],'TARGET'])
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
            
            if item == 'Brain Stem':
                
                part2[1] = '    name=' + item +'\n'
                
                # select the maximum value from protocol request and 0.8*prescription dose
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                
                # select CF: maximum                
                cf = self.modify_mxd_551(Dose=int(max_dose)+1,Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 
                
            elif item == 'Spinal Cord':
                                
                part2[1] = '    name=' + item +'\n'                

                # select the maximum value from protocol request and 0.75*prescription dose
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                
                # select CF:maximum 
                cf = self.modify_mxd_551(Dose=int(max_dose)+2,Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')  
                                
            elif item == 'Optical Chiasm' or item == 'Optical Nerve L' or item == 'Optical Nerve R':
                
                part2[1] = '    name=' + item +'\n'                

                # select the maximum value from protocol request and 0.75*prescription dose
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                
                # select CF:maximum 
                cf = self.modify_mxd_551(Dose=int(max_dose)+1,Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')  

            elif item == 'Lens R' or item == 'Lens L':
                                 
                part2[1] = '    name=' + item +'\n'                

                # select the maximum value from protocol request
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                
                # select CF:maximum
                cf = self.modify_mxd_551(Dose=int(max_dose)+1,Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')                  
            
            elif item == 'Eye R' or item == 'Eye L':
                                 
                part2[1] = '    name=' + item +'\n'                


                if '%' in self.protocol_dict[item][0][0]:
                    
                    percent = float(self.protocol_dict[item][0][0].split('D')[1].split('%')[0])
                    
                    if percent < 10: 
                                                
                        # select CF: maximum
                        max_dose =  float(self.protocol_dict[item][0][1].split('Gy')[0])
                        cf = self.modify_mxd_551(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                        
                    else:
                        
                        # select CF: serial
                        eud_dose = 0.5*self.tar[-1][-1]           
                        cf = self.modify_se_551(Dose=int(eud_dose),Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=12)                       


                elif 'cc' in self.protocol_dict[item][0][0]:
                    
                    vol = float(self.protocol_dict[item][0][0].split('D')[1].split('cc')[0])
                    
                    if vol < 10: 
                                                
                        # select CF: maximum
                        max_dose =  float(self.protocol_dict[item][0][1].split('Gy')[0])
                        cf = self.modify_mxd_551(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                        
                    else:
                        
                        # select CF: serial
                        eud_dose = 0.5*self.tar[-1][-1]           
                        cf = self.modify_se_551(Dose=int(eud_dose),Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=12)    
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')               

            elif item == 'Parotid R' or item == 'Parotid L':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: serial (constrain high dose region)
                eud_dose1 = 0.65*self.tar[-1][-1]
                cf1 = self.modify_se_551(Dose= eud_dose1,Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1]
            
                # select CF2: serial (constrain mean dose)
                eud_dose2 = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf2 = self.modify_se_551(Dose= eud_dose2+2,Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=1) 
                
                OARs = OARs + cf2[:-1]
                OARs.append('!END\n')   

            elif item == 'Oral Cavity':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: serial (constrain high dose region)
                eud_dose1 = 0.85*self.tar[-1][-1]
                cf1 = self.modify_se_551(Dose= int(eud_dose1),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1] 
                
                # select CF2: serial (constrain mean dose, eud = pro_dose+2Gy)
                eud_dose2 = max(float(self.protocol_dict[item][0][1].split('Gy')[0]),0.8*self.tar[-1][-1])
                cf2 = self.modify_se_551(Dose= int(eud_dose2),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=1) 

                OARs = OARs + cf2[:-1]
                OARs.append('!END\n')         

            elif item == 'Larynx':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: serial (constrain high dose region)
                eud_dose1 = 0.75*self.tar[-1][-1]
                cf1 = self.modify_se_551(Dose= int(eud_dose1),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1]
            
                # select CF2: parallel (constrain mean dose, eud = pro_dose+2Gy)
                eud_dose2 = max(float(self.protocol_dict[item][0][1].split('Gy')[0]),0.7*self.tar[-1][-1])
                cf2 = self.modify_se_551(Dose= int(eud_dose2),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=1) 
                
                OARs = OARs + cf2[:-1]
                OARs.append('!END\n') 
                
            elif item == 'Pitutary' or item == 'Pituitary':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF: Parallel (constrain D50% and optimize all)
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf = self.modify_pa_551(Ref_dose= int(max_dose),Volume = 50, Weight=0.01,Powe_Law=4,Opti_all=0,Shrink_margin=0) 

                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 

            elif item == 'T.Lobe R' or item == 'T.Lobe L':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF: Serial (constrain high dose region)
                eud_dose = max(float(self.protocol_dict[item][0][1].split('Gy')[0]),0.8*self.tar[-1][-1])
                cf1 = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 

                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')                 
                               
            elif item == 'Brain':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF: Maximum (Constrain D5%)
#                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
#                cf = self.modify_mxd_551(Dose= int(max_dose)+5,Weight=0.01,Opti_all=1,Shrink_margin=grid)
                eud_dose = max(float(self.protocol_dict[item][0][1].split('Gy')[0]),0.75*self.tar[-1][-1])
                cf = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                        
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')                  
                
            elif item == 'Mandible':
                
                print('Mandible')
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: Quadratic Overdose(Constrain D2cc/Max Dose)
                max_dose = self.tar[-1][-1]
                cf1 = self.modify_qod_551(Dose= int(max_dose),RMS = 0.25,Shrink_margin = grid,Opti_all = 0,LABEL =[item[0],'OARs']) 
                # cf1 = self.modify_mxd(Dose=max_dose,Weight=0.01,Opti_all=1,Shrink_margin=0)
                # cf1 = self.modify_se(Dose= max_dose*0.75,Weight=0.01,Shrink_margin=0.25,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1]
                
                # select CF1: Serial (Constrain D50% dose )
                eud_dose = self.tar[-1][-1]*0.8
                cf2 = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=1)    
    
                OARs = OARs + cf2[:-1]
                OARs.append('!END\n') 
                

            elif item == 'A.D L' or item == 'A.D R' or item == 'T.Joint R' or item == 'T.Joint L':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Parallel (Constrain D50% dose )
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf = self.modify_pa_551(Ref_dose= int(max_dose),Volume = 50, Weight=0.01,Powe_Law=4,Opti_all=0,Shrink_margin=0)   
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')

            elif item == 'Lung' or item == 'Lungs':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Serial (Constrain high dose )
                eud_dose = self.tar[-1][-1]*0.65
                cf = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')  

            # assistance structure like SPPRV,BSPRV,R6,R7
            elif item == 'SPPRV':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Maximum (Constrain high dose )
                max_dose = self.tar[-1][-1]*0.65
                cf = self.modify_mxd_551(Dose= int(max_dose), Weight=0.01, Opti_all=1, Shrink_margin=0)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 

            elif item == 'BSPRV':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Maximum (Constrain high dose )
                max_dose = self.tar[-1][-1]*0.75
                cf = self.modify_mxd_551(Dose= int(max_dose), Weight=0.01, Opti_all=1, Shrink_margin=0)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 

            elif item == 'R7' or item == 'TracheaAvoid':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Maximum (Constrain high dose )
                max_dose = self.tar[-1][-1]*0.8
                cf = self.modify_mxd_551(Dose= int(max_dose)+2, Weight=0.01, Opti_all=1, Shrink_margin=0)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')
                
            elif item == 'R6' or item == 'PostAvoid':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Maximum (Constrain high dose )
                max_dose = self.tar[-1][-1]*0.75
                cf = self.modify_mxd_551(Dose= int(max_dose)+2, Weight=0.01, Opti_all=1, Shrink_margin=0)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')


            elif item == 'BODY' or item == 'Patient' or item == 'Body': ## patient
                
                part2[1] = '    name=' + item +'\n'
                
                ## global maximum dose
                mxd1 = self.modify_mxd_551(Dose= int(self.tar[0][-1]*1.1), Weight=0.01, Opti_all=1, Shrink_margin=0)
                OARs = OARs + part2 + mxd1[:-1]
                
                ## the outer target dose
                QOD1 = self.modify_qod_551(Dose = int(self.tar[-1][-1]), RMS = 0.5, Shrink_margin = 0, Opti_all=0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD1[:-1]
                
                QOD2 = self.modify_qod_551(Dose = int(self.tar[-1][-1])-5, RMS = 0.75, Shrink_margin = grid,Opti_all = 0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD2[:-1]

                QOD3 = self.modify_qod_551(Dose = int(self.tar[-1][-1])-10, RMS = 1, Shrink_margin = grid*2,Opti_all = 0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD3[:-1]

                QOD4 = self.modify_qod_551(Dose = int(self.tar[-1][-1])-15, RMS = 1.25, Shrink_margin = grid*3, Opti_all= 0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD4[:-1]

                QOD5 = self.modify_qod_551(Dose = int(self.tar[-1][-1])-20, RMS = 2.0, Shrink_margin = grid*4, Opti_all = 0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD5[:-1]                
                
                OARs.append('!END\n')
                
        ## ============================ part3 ============================== ##
        part3 = self.element['# Part3\n'][:-1]
        
        ## ============================ part4 ============================== ##
        # here are two selections for part4
        
        if delivery_type == 'VMAT':
            # VMAT 360 ARC
            part4 = self.element['# Part4_VMAT\n'][:-1] 
        elif delivery_type == 'IMRT':
            # IMRT 9beams step&shoot
            part4 = self.element['# Part4_IMRT\n'][:-1]
        
        ## ============================ part5 ============================== ##
        part5 = self.element['# Part5\n'][:-1]
        for i,item in enumerate(part5):
            if 'FRACTIONS' in item:
                part5[i] = ''.join(['!FRACTIONS    ',str(fractions),'\n'])
            
            elif 'PRESCRIPTION' in item:
                part5[i] = ''.join(['!PRESCRIPTION    ',str(float(prescription_dose)),'\n'])
                
            elif 'DOSEGRIDSIZE' in item:
                part5[i] = ''.join(['!DOSEGRIDSIZE    ',str(float(grid)),'\n'])
            
#            elif 'MAXNARCS' in item:
#                part5[i] = ''.join(['!MAXNARCS    ',str(float(ARCS)),'\n'])
        
        ## ================== template ==================== ##        
        self.template_line = self.template_line + part1 + target + OARs + part3 + part4 + part5
        
        print('###############################')
        print('template has been generated !')
        print('###############################')
              
        
        return self.template_line   

    def hyp_solution_NPC_PeterThoughts(self,grid,fractions,prescription_dose,delivery_type):
        
        '''
          This is another version of NPC model
        '''
        self.template_line = []
        
        # deal with target
        self.tar = [(key,self.protocol_dict[key][0][1],
                float(self.protocol_dict[key][0][0].split('V')[1].split('Gy')[0]))
           for key in self.protocol_dict.keys() if 'PCTV' in key or 'PGTV' in key or 'GTV' in key]
        self.tar.sort(key=lambda x:x[2],reverse = True)
        self.tar_nam = [item[0] for item in self.tar]
        
        sorted_name = self.name_sorting()
#        OARs_nam = [item for item in sorted_name if item not in self.tar_nam and item in self.protocol_dict.keys()] + ['R6','R7']
        OARs_nam = [item for item in sorted_name if item not in self.tar_nam and item in self.protocol_dict.keys()] + ['PostAvoid','TracheaAvoid']
        prep_name = self.tar_nam + OARs_nam +['BODY']
        OARs_nam = OARs_nam + ['BODY']  
        ## ============================ part1 ============================== ##
        part1 = ['000610b6\n','!LAYERING\n'] # Monaco5.51 serial number: 000610b6
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
        for i,item in enumerate(self.tar):
            
            if i != len(self.tar)-1:  ## inner target 
                
                part2[1] = '    name=' + item[0] +'\n'

                # setting target penalty
                tar_pen = self.modify_qp_551(Vol = item[1],Dose = item[2],Weight = 1.0,Opti_all = 1,Surf_margin = 0)
                
                # setting quadratic overdose
                qod = self.modify_qod_551(Dose = int(item[2]+2),RMS = 0.5,Shrink_margin = 0,Opti_all = 0,LABEL = [item[0],'TARGET'])
                
                # combine them together
                target = target + part2 + tar_pen[:-1] + qod[:-1]
                target.append('!END\n')
                
            else:   ## external target
                
                part2[1] = '    name=' + item[0] +'\n'  
                
                # setting target penalty
                tar_pen_ext = self.modify_qp_551(Vol = item[1],Dose = item[2],Weight = 1.0,Opti_all = 1,Surf_margin = 0)
                target = target + part2 + tar_pen_ext[:-1]
                
                # first quadratic overdose to contrain inner target reigon to prevent hot dose release to low dose region
                qod1 = self.modify_qod_551(Dose = self.tar[i-1][-1],RMS = 0.5,Shrink_margin = 0,Opti_all = 0,LABEL =[item[0],'TARGET'])
                target = target + qod1[:-1]
                
                # second quadratic overdose to constarin 110% percent of external target dose region
                qod2 = self.modify_qod_551(Dose = int(item[2]*1.08),RMS = 1,Shrink_margin = grid*2, Opti_all= 0,LABEL =[item[0],'TARGET'])
                target = target + qod2[:-1]
                
                # third quadratic overdose to constrain 102% percent of external target dose region
                qod3 = self.modify_qod_551(Dose = int(item[2]*1.0),RMS = 2,Shrink_margin = grid*3, Opti_all = 0,LABEL =[item[0],'TARGET'])
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
            
            if item == 'Brain Stem':
                
                part2[1] = '    name=' + item +'\n'
                
                # select the maximum value from protocol request and 0.8*prescription dose
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                
                # select CF: maximum                
                cf = self.modify_mxd_551(Dose=int(max_dose)+1,Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 
                
            elif item == 'Spinal Cord':
                                
                part2[1] = '    name=' + item +'\n'                

                # select the maximum value from protocol request and 0.75*prescription dose
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                
                # select CF:maximum 
                cf = self.modify_mxd_551(Dose=int(max_dose)+2,Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')  
                                
            elif item == 'Optical Chiasm' or item == 'Optical Nerve L' or item == 'Optical Nerve R':
                
                part2[1] = '    name=' + item +'\n'                

                # select the maximum value from protocol request and 0.75*prescription dose
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                
                # select CF:maximum 
                cf = self.modify_mxd_551(Dose=int(max_dose)+1,Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')  

            elif item == 'Lens R' or item == 'Lens L':
                                 
                part2[1] = '    name=' + item +'\n'                

                # select the maximum value from protocol request
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                
                # select CF:maximum
                cf = self.modify_mxd_551(Dose=int(max_dose)+1,Weight=0.01,Opti_all=1,Shrink_margin=0)
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')                  
            
            elif item == 'Eye R' or item == 'Eye L':
                                 
                part2[1] = '    name=' + item +'\n'                


                if '%' in self.protocol_dict[item][0][0]:
                    
                    percent = float(self.protocol_dict[item][0][0].split('D')[1].split('%')[0])
                    
                    if percent < 10: 
                                                
                        # select CF: maximum
                        max_dose =  float(self.protocol_dict[item][0][1].split('Gy')[0])
                        cf = self.modify_mxd_551(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                        
                    else:
                        
                        # select CF: serial
                        eud_dose = 0.5*self.tar[-1][-1]           
                        cf = self.modify_se_551(Dose=int(eud_dose),Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=12)                       


                elif 'cc' in self.protocol_dict[item][0][0]:
                    
                    vol = float(self.protocol_dict[item][0][0].split('D')[1].split('cc')[0])
                    
                    if vol < 10: 
                                                
                        # select CF: maximum
                        max_dose =  float(self.protocol_dict[item][0][1].split('Gy')[0])
                        cf = self.modify_mxd_551(Dose=int(max_dose),Weight=0.01,Opti_all=1,Shrink_margin=0)
                        
                    else:
                        
                        # select CF: serial
                        eud_dose = 0.5*self.tar[-1][-1]           
                        cf = self.modify_se_551(Dose=int(eud_dose),Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=12)    
                
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')               

            elif item == 'Parotid R' or item == 'Parotid L':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: serial (constrain high dose region)
                eud_dose1 = 0.65*self.tar[-1][-1]
                cf1 = self.modify_se_551(Dose= eud_dose1,Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1]
            
                # select CF2: serial (constrain mean dose)
                eud_dose2 = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf2 = self.modify_se_551(Dose= eud_dose2+2,Weight=0.01,Shrink_margin=0,Opti_all=0,Powe_Law=1) 
                
                OARs = OARs + cf2[:-1]
                OARs.append('!END\n')   

            elif item == 'Oral Cavity':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: serial (constrain high dose region)
                eud_dose1 = 0.85*self.tar[-1][-1]
                cf1 = self.modify_se_551(Dose= int(eud_dose1),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1] 
                
                # select CF2: serial (constrain mean dose, eud = pro_dose+2Gy)
                eud_dose2 = max(float(self.protocol_dict[item][0][1].split('Gy')[0]),0.8*self.tar[-1][-1])
                cf2 = self.modify_se_551(Dose= int(eud_dose2),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=1) 

                OARs = OARs + cf2[:-1]
                OARs.append('!END\n')         

            elif item == 'Larynx':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: serial (constrain high dose region)
                eud_dose1 = 0.75*self.tar[-1][-1]
                cf1 = self.modify_se_551(Dose= int(eud_dose1),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1]
            
                # select CF2: parallel (constrain mean dose, eud = pro_dose+2Gy)
                eud_dose2 = max(float(self.protocol_dict[item][0][1].split('Gy')[0]),0.7*self.tar[-1][-1])
                cf2 = self.modify_se_551(Dose= int(eud_dose2),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=1) 
                
                OARs = OARs + cf2[:-1]
                OARs.append('!END\n') 
                
            elif item == 'Pitutary' or item == 'Pituitary':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF: Parallel (constrain D50% and optimize all)
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf = self.modify_pa_551(Ref_dose= int(max_dose),Volume = 50, Weight=0.01,Powe_Law=4,Opti_all=0,Shrink_margin=0) 

                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 

            elif item == 'T.Lobe R' or item == 'T.Lobe L':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF: Serial (constrain high dose region)
                eud_dose = max(float(self.protocol_dict[item][0][1].split('Gy')[0]),0.8*self.tar[-1][-1])
                cf1 = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 

                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')                 
                               
            elif item == 'Brain':
                                 
                part2[1] = '    name=' + item +'\n'    
                
                # select CF: Maximum (Constrain D5%)
#                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
#                cf = self.modify_mxd_551(Dose= int(max_dose)+5,Weight=0.01,Opti_all=1,Shrink_margin=grid)
                eud_dose = max(float(self.protocol_dict[item][0][1].split('Gy')[0]),0.75*self.tar[-1][-1])
                cf = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12) 
                        
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')                  
                
            elif item == 'Mandible':
                
                print('Mandible')
                part2[1] = '    name=' + item +'\n'    
                
                # select CF1: Quadratic Overdose(Constrain D2cc/Max Dose)
                max_dose = self.tar[-1][-1]
                cf1 = self.modify_qod_551(Dose= int(max_dose),RMS = 0.25,Shrink_margin = grid,Opti_all = 0,LABEL =[item[0],'OARs']) 
                # cf1 = self.modify_mxd(Dose=max_dose,Weight=0.01,Opti_all=1,Shrink_margin=0)
                # cf1 = self.modify_se(Dose= max_dose*0.75,Weight=0.01,Shrink_margin=0.25,Opti_all=0,Powe_Law=12) 
                OARs = OARs + part2 + cf1[:-1]
                
                # select CF1: Serial (Constrain D50% dose )
                eud_dose = self.tar[-1][-1]*0.8
                cf2 = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=1)    
    
                OARs = OARs + cf2[:-1]
                OARs.append('!END\n') 
                

            elif item == 'A.D L' or item == 'A.D R' or item == 'T.Joint R' or item == 'T.Joint L':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Parallel (Constrain D50% dose )
                max_dose = float(self.protocol_dict[item][0][1].split('Gy')[0])
                cf = self.modify_pa_551(Ref_dose= int(max_dose),Volume = 50, Weight=0.01,Powe_Law=4,Opti_all=0,Shrink_margin=0)   
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')

            elif item == 'Lung' or item == 'Lungs':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Serial (Constrain high dose )
                eud_dose = self.tar[-1][-1]*0.65
                cf = self.modify_se_551(Dose= int(eud_dose),Weight=0.01,Shrink_margin=grid,Opti_all=0,Powe_Law=12)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')  

            # assistance structure like SPPRV,BSPRV,R6,R7
            elif item == 'SPPRV':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Maximum (Constrain high dose )
                max_dose = self.tar[-1][-1]*0.65
                cf = self.modify_mxd_551(Dose= int(max_dose), Weight=0.01, Opti_all=1, Shrink_margin=0)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 

            elif item == 'BSPRV':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Maximum (Constrain high dose )
                max_dose = self.tar[-1][-1]*0.75
                cf = self.modify_mxd_551(Dose= int(max_dose), Weight=0.01, Opti_all=1, Shrink_margin=0)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n') 

            elif item == 'R7' or item == 'TracheaAvoid':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Maximum (Constrain high dose )
                max_dose = self.tar[-1][-1]*0.8
                cf = self.modify_mxd_551(Dose= int(max_dose)+2, Weight=0.01, Opti_all=1, Shrink_margin=0)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')
                
            elif item == 'R6' or item == 'PostAvoid':
                                 
                part2[1] = '    name=' + item +'\n'    

                # select CF: Maximum (Constrain high dose )
                max_dose = self.tar[-1][-1]*0.75
                cf = self.modify_mxd_551(Dose= int(max_dose)+2, Weight=0.01, Opti_all=1, Shrink_margin=0)    
    
                OARs = OARs + part2 + cf[:-1]
                OARs.append('!END\n')


            elif item == 'BODY' or item == 'Patient' or item == 'Body': ## patient
                
                part2[1] = '    name=' + item +'\n'
                
                ## global maximum dose
                mxd1 = self.modify_mxd_551(Dose= int(self.tar[0][-1]*1.1), Weight=0.01, Opti_all=1, Shrink_margin=0)
                OARs = OARs + part2 + mxd1[:-1]
                
                ## the outer target dose
                QOD1 = self.modify_qod_551(Dose = int(self.tar[-1][-1]), RMS = 0.5, Shrink_margin = 0, Opti_all=0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD1[:-1]
                
                QOD2 = self.modify_qod_551(Dose = int(self.tar[-1][-1])-5, RMS = 0.75, Shrink_margin = grid,Opti_all = 0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD2[:-1]

                QOD3 = self.modify_qod_551(Dose = int(self.tar[-1][-1])-10, RMS = 1, Shrink_margin = grid*2,Opti_all = 0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD3[:-1]

                QOD4 = self.modify_qod_551(Dose = int(self.tar[-1][-1])-15, RMS = 1.25, Shrink_margin = grid*3, Opti_all= 0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD4[:-1]

                QOD5 = self.modify_qod_551(Dose = int(self.tar[-1][-1])-20, RMS = 2.0, Shrink_margin = grid*4, Opti_all = 0,LABEL =[item[0],'BODY'])
                OARs = OARs + QOD5[:-1]                
                
                OARs.append('!END\n')
                
        ## ============================ part3 ============================== ##
        part3 = self.element['# Part3\n'][:-1]
        
        ## ============================ part4 ============================== ##
        # here are two selections for part4
        
        if delivery_type == 'VMAT':
            # VMAT 360 ARC
            part4 = self.element['# Part4_VMAT\n'][:-1] 
        elif delivery_type == 'IMRT':
            # IMRT 9beams step&shoot
            part4 = self.element['# Part4_IMRT\n'][:-1]
        
        ## ============================ part5 ============================== ##
        part5 = self.element['# Part5\n'][:-1]
        for i,item in enumerate(part5):
            if 'FRACTIONS' in item:
                part5[i] = ''.join(['!FRACTIONS    ',str(fractions),'\n'])
            
            elif 'PRESCRIPTION' in item:
                part5[i] = ''.join(['!PRESCRIPTION    ',str(float(prescription_dose)),'\n'])
                
            elif 'DOSEGRIDSIZE' in item:
                part5[i] = ''.join(['!DOSEGRIDSIZE    ',str(float(grid)),'\n'])
            
#            elif 'MAXNARCS' in item:
#                part5[i] = ''.join(['!MAXNARCS    ',str(float(ARCS)),'\n'])
        
        ## ================== template ==================== ##        
        self.template_line = self.template_line + part1 + target + OARs + part3 + part4 + part5
        
        print('###############################')
        print('template has been generated !')
        print('###############################')
              
        
        return self.template_line   
        
    def hyp_solution_Prostate_V1(self,grid,fractions,prescription_dose,delivery_type):
        
        return 1
        
          

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


class Initialization_MON551(HYP_Editor_MONACO551):    
    
    '''
       This class save all the initialization parameters for generation
    '''
    
    def __init__(self,pt_id,
                      delivery_method,
                      fx,
                      prep_dose,
                      grid_dose,
                      path,
                      protocol_xlsx,
                      PT_path):
        import os
        
        self.pt_id = pt_id
        self.delivery_method = delivery_method
        self.fx = fx
        self.prep_dose = prep_dose
        self.grid_dose = grid_dose
        self.protocol_xlsx = protocol_xlsx
        
        
        # original template folder and file path
        hyp_element_path = os.path.join(path,'hyp_element551.txt')
        demo_xml_path = os.path.join(path,'demo_dosenormsettings.xml')
        self.absolute_path = os.path.join(path,'remaining4files')
        

        # updated new template folder and file path
        
        self.updated_template_path = 'C:/Users/Public/Documents/CMS/FocalData/MonacoTemplates'
        # self.updated_template_path = os.path.join(path,self.pt_id)
        updated_template_path2 = os.path.join(path,self.pt_id)
        output_xml_path = os.path.join(self.updated_template_path,self.pt_id+self.delivery_method+'.dosenormsettings.xml')
        hyp_path_new = os.path.join(self.updated_template_path,self.pt_id+self.delivery_method+'.hyp')


        # once ct image was loaded, check the structure name with protocol
        contourname_path = PT_path + self.pt_id + '/1~CT1/contournames'
        new_contourname_path = PT_path + self.pt_id + '/1~CT1/contournames1'
        NAMING_LIB = {'TARGET_NAME_LIB':{'gtv','ctv','ptv','pgtv','pctv'},
                      'OARs_NAME_LIB_HN':
                          {'Level1':{'spinal cord','brain stem','stem','cord','prv','prv bs','scprv','prv sc'},
                           'Level2':{'optical nerve r','optical nerve l','optical nerve',
                                     'lens r','lens l','lens',
                                     'eye r','eye l','eye',
                                     'brain','optical chiasm'
                                     }}}


        HYP_Editor_MONACO551.__init__(self,hyp_element_path,
                                                     protocol_xlsx,
                                                     demo_xml_path,
                                                     output_xml_path,
                                                     contourname_path,
                                                     NAMING_LIB,
                                                     hyp_path_new,
                                                     updated_template_path2,
                                                     new_contourname_path)
    
    def Standardize_Contour_Name(self):
        
        '''
           This script was used for naming standardization
        '''
        self.new_name = HYP_Editor_MONACO551.modify_MONACO_contournames(self,protocol_name)
    
    
    def MAIN_GENERATE(self,LABEL):
        '''
        Main function for generate template
        '''
        
        from shutil import copyfile
        import os
        
        HYP_Editor_MONACO551.mkdir(self)
        # read protocol to dict
        self.protocol_dict = HYP_Editor_MONACO551.extract_xlsx(self,self.pt_id)
        
        # read hyp elements into RAM
        self.ele = HYP_Editor_MONACO551.Read_HYP_element(self)
        #print(ele)
        
        # generate new hyp file
        if LABEL == 'NPC':
            self.updated_template = HYP_Editor_MONACO551.hyp_solution_NPC_V3(self,
                                                             grid=self.grid_dose,
                                                             fractions=self.fx,
                                                             prescription_dose=self.prep_dose,
                                                             delivery_type=self.delivery_method)
        elif LABEL == 'Prostate':
            self.updated_template = HYP_Editor_MONACO551.hyp_solution_Prostate_V1(self,
                                                             grid=self.grid_dose,
                                                             fractions=self.fx,
                                                             prescription_dose=self.prep_dose,
                                                             delivery_type=self.delivery_method)            
        
        HYP_Editor_MONACO551.write_colone(self)
        
        # generate new xml file
        HYP_Editor_MONACO551.xml_solution(self,list(self.protocol_dict.keys()))
        
        # remaining task: copy the remaining 4 files into new template folder
        # X.PLN, X.TEL, X.isodosesettings, X.dvhparam
        
        copyfile(os.path.join(self.absolute_path,self.delivery_method,'5.51.isodosesettings.xml'), os.path.join(self.updated_template_path,self.pt_id+self.delivery_method+'.isodosesettings.xml'))
        copyfile(os.path.join(self.absolute_path,self.delivery_method,'5.51.dvhparam.xml'), os.path.join(self.updated_template_path,self.pt_id+self.delivery_method+'.dvhparam.xml'))
        copyfile(os.path.join(self.absolute_path,self.delivery_method,'5.51.PLN'), os.path.join(self.updated_template_path,self.pt_id+self.delivery_method+'.pln'))
        copyfile(os.path.join(self.absolute_path,self.delivery_method,'5.51.TEL'), os.path.join(self.updated_template_path,self.pt_id+self.delivery_method+'.tel'))

    
    