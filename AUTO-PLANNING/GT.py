class Temp:
    '''
       this class mainly intended to generate a template automatically
       
    '''
    
    def  __init__(self,path,csv_file,colone_path):
        
        self.path = path
        self.csv = csv_file
        self.col = colone_path
        
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
    
    def modify_qp(self,qp,Vol,Dose,Weight,Opti_all,Surf_margin):
        
        self.qp = qp
        self.qp[15] = ''.join(['        refvolume=',str(Vol),'\n'])
        self.qp[18] = ''.join(['        isoconstraint=',str(Dose),'\n'])
        self.qp[-3] = ''.join(['        weight=',str(Weight),'\n'])
        self.qp[4] = ''.join(['        totalvolume=',str(Opti_all),'\n'])
        self.qp[5] = ''.join(['        sanesurfacedose=',str(Surf_margin),'\n'])      
        self.qp[-2] = ''.join(['    !END\n'])
        
        return self.qp[:-1]
    
    def modify_po(self,po,Dose,alpha):
        
        self.po = po
        self.po[18] = ''.join(['        isoconstraint=',str(Dose),'\n'])
        self.po[10] = ''.join(['        alpha=',str(alpha),'\n'])
        self.po[-2] = ''.join(['    !END\n'])
        
        return self.po[:-1]    
    
    
    def modify_se(self,se,Dose,Weight,Shrink_margin,Opti_all,Powe_Law):
    
        self.se = se 
        self.se[18] = ''.join(['        isoconstraint=',str(Dose),'\n'])
        self.se[-3] = ''.join(['        weight=',str(Weight),'\n'])
        self.se[9] = ''.join(['        shrinkmargin=',str(Shrink_margin),'\n'])
        self.se[4] = ''.join(['        totalvolume=',str(Opti_all),'\n'])        
        self.se[16] = ''.join(['        exponent=',str(Powe_Law),'\n'])
        self.se[-2] = ''.join(['    !END\n'])
        
        return self.se[:-1]


    def modify_pa(self,pa,Ref_dose,Volume,Weight,Powe_Law,Opti_all,Shrink_margin):

        self.pa = pa
        self.pa[13] = ''.join(['        refdose=',str(Ref_dose),'\n'])      
        self.pa[18] = ''.join(['        isoconstraint=',str(Volume),'\n'])       
        self.pa[-3] = ''.join(['        weight=',str(Weight),'\n'])
        self.pa[16] = ''.join(['        exponent=',str(Powe_Law),'\n'])        
        self.pa[4] = ''.join(['        totalvolume=',str(Opti_all),'\n'])        
        self.pa[9] = ''.join(['        shrinkmargin=',str(Shrink_margin),'\n'])           
        self.pa[-2] = ''.join(['    !END\n'])
        
        return self.pa[:-1]

    def modify_mxd(self,mxd,Dose,Weight,Opti_all,Shrink_margin):
        
        self.mxd = mxd
        self.mxd[18] = ''.join(['        isoconstraint=',str(Dose),'\n' ])       
        self.mxd[-3] = ''.join(['        weight=',str(Weight),'\n'])
        self.mxd[4] = ''.join(['        totalvolume=',str(Opti_all),'\n' ])      
        self.mxd[9] = ''.join(['        shrinkmargin=',str(Shrink_margin),'\n'])        
        self.mxd[-2] = ''.join(['    !END\n'])
        
        return self.mxd[:-1]

    def modify_qod(self,qod,Dose,RMS,Shrink_margin):

        self.qod = qod
        self.qod[17] = ''.join(['        thresholddose=',str(Dose),'\n']) 
        self.qod[18] = ''.join(['        isoconstraint=',str(RMS),'\n']) 
        self.qod[9] = ''.join(['        shrinkmargin=',str(Shrink_margin),'\n'  ])   
        self.qod[-2] = ''.join(['    !END\n']) 
        
        return self.qod[:-1]

    def read_struct(self,structure):
        '''
           This function output a list of structure name from struct.dcm file
        '''
        self.contours = []
        for i in range(len(structure.ROIContourSequence)):
            self.contour = {}
            self.contour['color'] = structure.ROIContourSequence[i].ROIDisplayColor
            self.contour['number'] = structure.ROIContourSequence[i].ReferencedROINumber
            self.contour['name'] = structure.StructureSetROISequence[i].ROIName
            assert self.contour['number'] == structure.StructureSetROISequence[i].ROINumber
            self.contour['contours'] = [s.ContourData for s in structure.ROIContourSequence[i].ContourSequence]
            self.contours.append(self.contour)
        
        return self.contours


    def read_csv(self):
        
        self.pres_strt,self.dose_frac = [],[]
        self.pres_strt_ind = {} # initialization
        
        import csv
        with open(self.csv) as csvfile:  
            readCSV = csv.reader(csvfile, delimiter=',')  
            prep = [row for row in readCSV]  
        
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

    def write_colone(self,template):
        
        template.append('')        
        s=''.join(template)          
        f = open(self.col,'w+')        
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
        stat = input('Do you want to change the name? if Yes enter 1 & No enter 0\n')
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
            template = self.ge_tem_pros(self.strt_ind_list,path_beam,dose_frac)
            
        else:
            
            template = self.ge_tem_HN(self.strt_ind_list,path_beam,dose_frac)
        
        template[-1] = '!ISPHANTOMMATERIAL    0\n' 
        
        self.write_colone(template)
        
        return self.strt_ind_list,self.tras
    

    