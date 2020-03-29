# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 09:36:32 2020

@author: Henry Huang in Elekta Shanghai Co. Ltd.
"""

class TEMPLATE_FINE_TUNE:
    ''' 
       The TEMPLATE_FINE_TUNE class was used to modify the treatment plan 
       template in FMO of Monaco TPS.
       
       The workflow is displayed as follow:
           
           [1] Monaco Phase 1 optimization <flag = 1> 
           [2] Export DVH statistics table (csv,json) <flag = 0>
           [3] 'TEMPLATE_FINE_TUNE.py' read DVH stat and template.hyp in 
                last iteration and try to update template.hyp <flag => 1>
           [4] Monaco would be refed with new template file and FMO continue.
           [5] stopping criteria: DVH changes < 1% in last five iterations &
               iteration# > threshold
           [6] FMO finished <flag = 2> and Phase2 start automatically.
    '''
    def __init__(self,path,ind_loc_strt,iter_path,hyp_path,hyp_path_updated,DVH_CSV):
        '''
        Initalization of all parameters:
            1. protocol path <protocol_xlsx >
            2. template path <hyp_path>
        '''
        self.path = path
        self.ind = ind_loc_strt
        self.iter_path = iter_path
        self.dvh_name = ''
        self.hyp_path = hyp_path # temporary hyp file path
        self.hyp_path_updated = hyp_path_updated # updated hyp file path
        self.DVH_path = DVH_CSV # current DVH statistics CSV path 
  
    def read_dvh(self):
        
        with open(self.path[2][2], "r+") as f:
            line = f.readlines()
            
        for i in line[1]:
            if i == '=':
                k = line[1].index(i)
                
        self.dvh_name = line[1][k+2:]
        return self.dvh_name
    
    def write_dvh(self,new_name):
        """
           this function to change dvh_name
        """    
        f = open(self.path[2][2], "r+")
        
        line = f.readlines()
        
        line[1] = ''.join(['dvh_name = ',new_name])
        
        s=''.join(line)   
        
        f.seek(0)
        
        f.write(s)
        
        f.close()
        
    def write_tem_name(self):
        """
           write name to certain path
        """    
        f = open(self.path[2][7], "r+")
        
        line = f.readlines()
        
        ind = self.path[4].rindex('\\')
        
        line[1] = ''.join(['template = ',self.path[4][ind+1:-4]])
        
        s=''.join(line)   
        
        f.seek(0)
        
        f.write(s)
        
        f.close()
        
    def write_name(self,ID):
        """
           write name to certain path
        """    
        f = open(self.path[2][4], "r+")
        
        line = f.readlines()
        
        line[1] = ''.join(['name = ',ID])
        
        s=''.join(line)   
        
        f.seek(0)
        
        f.write(s)
        
        f.close()
    
    def csv_read_to_dvh(self):
        '''
           This function was used to extract DVH data from csv file
        '''
        import csv
        import os
        ss = os.listdir('C:\\auto template\\dvh')
        dir_list = sorted(ss,  key=lambda x: os.path.getmtime(os.path.join('C:\\auto template\\dvh', x)))
        csv_file = [item for item in dir_list if item.split('.')[1] == 'csv']
        
        path_dvh = os.path.join('C:\\auto template\\dvh',csv_file[-1])
        csv_reader = csv.reader(open(path_dvh, encoding='utf-8'))
        row = [ row for row in csv_reader]
        # clean dvh data


        dvh_ = row[3:-3]  ## remove redundant data
        dvh = []
        for i in dvh_:
            kk = i[0].split(' ')
            pp = [j for j in kk if j!='']
            dvh.append(pp)
            
        for i,item in enumerate(dvh):
            if len(item)>3:
                st = ''
                for j in item[0:-2]:
                    st += (j+' ')
                dvh[i] = [st[:-1],dvh[i][-2],dvh[i][-1]]
            else:
                pass
#        for item in row:
#            if len(item) == 3:
#                for i in range(len(item)):
#                    item[i] = item[i].replace(' ','')
                    
#        dvh = row[3:-3]  ## remove redundant data
        flag = []
        for i in range(len(dvh)-1):
            if dvh[i][0] != dvh[i+1][0]:
                flag.append((dvh.index(dvh[i]),dvh[i][0]))
                continue
        flag.append((dvh.index(dvh[-1]),dvh[-1][0]))
                
                
        self.DVH = {item[1]:[] for item in flag}
                
        for j in range(len(flag)):
            
            if j != 0:
                
                for k in range(flag[j-1][0]+1,flag[j][0]+1):
                    
                    self.DVH[flag[j][1]].append((float(dvh[k][1]),float(dvh[k][2])))
                    
            else:
                
                for k in range(flag[j][0]+1):
                    
                    self.DVH[flag[j][1]].append((float(dvh[k][1]),float(dvh[k][2])))
        
        return self.DVH
    
    def txt_read_to_dvh(self):
        '''
        This function was used for extracting DVH from txt file
        '''
    
        DVH = []   
        with open(self.txtpath, "r+") as f: 
            line = f.readlines()
            
        for item in line:
            if 'Structure Name' in item:
                flag = line.index(item)
                break
            
        
        for item in line[flag+1:-1]:
            m = []
            kk = item.split('  ')
            
            for i in kk:
                if i != '':
                    if '\n' in i:
                        m.append(i[:-2])
                    else:
                        m.append(i)
                        
            DVH.append(m)
        name = list(set([item[0] for item in DVH]))
        name.remove('')
        dvh = {}
        for i in name: dvh[i] = []
        
        for item in DVH:
            if '' not in item:
                dvh[item[0]].append((item[1],item[2]))
            
        return dvh
    

    def read_flag(self):
        '''
           Read txt file to mark current state of Monaco TPS
        '''
        with open('C:\\auto template\\flag.txt', "r+") as f: 
            line = f.readlines()
        return line[0]
    
    def write_flag(self):
        """
           Change flag to mark current state of Monaco TPS
        """    
        f = open('C:\\auto template\\flag.txt', "r+")        
        line = f.readlines()
        line[0] = '1'
        s=''.join(line)   
        f.seek(0)
        f.write(s)
        f.close()

    def write_flag_end(self):
        """
           this function to change flag from 0 to 1
        """    
        f = open('C:\\auto template\\flag.txt', "r+")        
        line = f.readlines()
        line[0] = '2'
        s=''.join(line)   
        f.seek(0)
        f.write(s)
        f.close()


       
    def write_iter(self,iter_num):
        """
           this function to change flag from 0 to 1
        """    
        f = open(self.iter_path, "r+")        
        line = f.readlines()
        line[1] = ''.join(['iteration = ',str(iter_num)])
        s=''.join(line)   
        f.seek(0)
        f.write(s)
        f.close()    
        
    def show_OARs(self,diff_result,tar_res_nam):
        '''
           This program tries to show OARs which are overdose
        '''
        self.OARs = {}
        
        for key in diff_result.keys():
            
            if key not in tar_res_nam:
            
                for item in diff_result[key]:
            
                 if item[1] > 1 and 'CTV' not in key and 'PTV' not in key:
                    
                    self.OARs[key] = diff_result[key]
        
        print('================================================')
        print('OARs still overdose:     \n')
        print(self.OARs)
        print('================================================')
         
    def read_template(self):
        
        '''
           This function read template.hyp file to another Data struct for
           later dealing
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
            
            indx = [4,6,9,10,13,16,18,19,20,23,21,22]
            
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
    
    def write_template(self,line,updated_struct_fun):
        """
            This function input: updated_struct_fun
                          output:
            both updated_struct_fun and flag all be written into files
        """
            
        # write the updated_struct_fun to the line 
        for key in updated_struct_fun:
            
            for value in updated_struct_fun[key]:
                
                if type(value) == list:
                    
                    line[value[1]] = '        ' + value[0] +'\n'
       
        # write list line to the original file
        s=''.join(line)   
        
        f = open(self.path[-1],'w+')
        
        f.seek(0)
        
        f.write(s)
        
        f.close()    
    
    def read_csv_zs(self,DVH,tras):
        '''
           This function outputs two variables:
               1) list of struct name
               2) dict of dose indices
        '''
        import csv
        # tras =  {'TM L': 'TMJ-L', 'TM R': 'TMJ-R'}
        self.pres_strt_ind = {}
        self.pres_strt = []
        self.dvh_data = {}
        
        with open(self.path[0]) as csvfile:  
            readCSV = csv.reader(csvfile, delimiter=',')  
            prep = [row for row in readCSV]  
        
        
        # to ensure the prep list has the same name with struct name
        for item in prep:
            if item[0] in tras.keys(): item[0] = tras[item[0]]
        ## extract the evaluation indices in prescription csv
        
        self.pres_strt = list(set([l[0] for l in prep if l[0] != 'prep' and l[0] != 'frac' ]))
        
#        dose_frac = [l for l in prep if l[0] == 'prep' or l[0] == 'frac' ]
        
        for item in self.pres_strt: self.pres_strt_ind[item] = [] # initialization
        
        for item in prep:
            
            if item[0] != 'prep' and item[0] != 'frac':
                
                if item[2][-1] != '%':
                    
                    self.pres_strt_ind[item[0]].append((item[1],float(item[2])/100))
                    
                else:
                    
                    self.pres_strt_ind[item[0]].append((item[1],float(item[2][:-1])))
    

        if tras == {}:
            self.dvh_data = DVH
        else: 
            for item in self.pres_strt:
                if item.replace(' ','') in DVH.keys():
                    self.dvh_data[item] = DVH[item.replace(' ','')] 
        
        
        
        return self.dvh_data,self.pres_strt_ind
 
    
    def DVH_inf(self,dvh_data):
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

    def back_strt_fun(self,struct_fun,struct_index,line,path,name,cost_name,loc):
        '''
           transfer the altered variable to struct_fun
           if you want to change cost function, remember to change 13
        '''       
        for key in name.keys():
              
            for n in range(len(name[key])):
                
                struct_fun[key][13 * n + loc][0] = cost_name + str(name[key][n][1])
    
        return struct_fun

    def extract_strt_fun(self,struct_fun,loc,start):
        '''
        To extract some parameters from struct_fun to help optimization
           name: e.g. isoconstraint,
           loc: e.g. location in struct_fun
           start: number start from the str
        '''
        self.name = {}
        
        for key in struct_fun.keys():
            
            self.name[key] = []
                
            for n in range(struct_fun[key][-1]):
                
                self.name[key].append([struct_fun[key][13*n][0],round(float(struct_fun[key][13*n+loc][0][start:]),5)])
         
        return self.name

 
    def plan_results1(self,dvh_inf,dvh_new_data,pres_strt_ind):
        '''
           This function returns a plan results of DVH
           the name of dvh_new_data must be consistent with struct_index
           
        '''
        import numpy as np
        from scipy.interpolate import interp1d 
        self.dvh_indices,self.diff_result = {},{}
        for item in pres_strt_ind.keys(): self.dvh_indices[item] = []
        for item in pres_strt_ind.keys(): self.diff_result[item] = []
        
        for item in pres_strt_ind:
                
                for j in pres_strt_ind[item]:
                    
                    if j[0] == 'Dmax':
                        
                        self.dvh_indices[item].append((j[0],round(dvh_inf[j[0]][item]/100,2)))
                        
                    elif j[0] == 'Dmean':
    
                        self.dvh_indices[item].append((j[0],round(dvh_inf[j[0]][item]/100,2)))
                        
                        
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
                        f=interp1d(xx,yy,kind = 'linear')#quadratic interpolate
                        self.dvh_indices[item].append((j[0],round(float(f(dose)),2)))   
                        
        for item in self.dvh_indices:
            for i,j in zip(self.dvh_indices[item],pres_strt_ind[item]):
                self.diff_result[item].append((j[0],round(i[1]/j[1],2)))
        




        
        return self.dvh_indices,self.diff_result

    def opt_prostate(self,diff_result,tar_res_nam):
        '''
           This is the optimization program for prostate
           inf: the dict stored the isoconstraints, isoeffects,weights,relative impact information etc.
           diff_result: a reference for evaluate the discrepancy from original prescription requirements
           tar_res_nam: list stored the target name
        '''
        import math
    #    count = 0
        
        IE = self.inf['ise'] 
        
        IC = self.inf['isc'] 
        
        W = self.inf['wgt'] 
        
        R = self.inf['rlp']  
        
        T = [diff_result[i] for i in tar_res_nam]
        
        print (T)
        
        # this line I need to count how many target dose coverage are ok(>1)
        tar_sum = sum([math.floor(item[0][1]) for item in T]) 
        
        # if all the PTV coverage is ok, then we could optimize the OARS dose
        if tar_sum == len(T):
            
            flag = 2 # indicate target is good
            
            print('Original parameters\n')
            
            ## so firstly we need to optimize the target dose 
            for key in IC.keys():
                ## restrict the constraints
                if key in tar_res_nam or key == 'patient':
                    
                    for i,item in enumerate(IC[key]):
                        ## item = [type='qp',70]
                        if item[0] == 'type=o_q':
                            
                            print(item)
                            
                            if R[key][i][1] <= 0.5: ##(+,++)
                                
                                IC[key][i][1] = (IE[key][i][1]+IC[key][i][1])/2
                                    
                            elif R[key][i][1] <= 0.75: ##(+++)
                                
                                if IC[key][i][1] > IE[key][i][1]:
                                    
                                    IC[key][i][1] = (IE[key][i][1]+IC[key][i][1])*2/3
                                    
                                else:
                                    
                                    IC[key][i][1] = min((IC[key][i][1]+R[key][i][1]),IE[key][i][1])
                            
                            else:  ##(++++)
                                
                                if IC[key][i][1] > IE[key][i][1]:
                                    
                                    IC[key][i][1] = IC[key][i][1]
                                    
                                else:
                                    
                                    IC[key][i][1] = max((IC[key][i][1]+R[key][i][1]),IE[key][i][1])
                                    
                                    
                        else:
                            
                            IC[key][i][1] = IC[key][i][1]
                                
                else: ## this means the normal tissue
                    
                    for i,item in enumerate(diff_result[key]):
                        
                        if item[1] > 1: # means overdose in normal tisses
                            # then we also check the relative impact to see how much it conflicts
                            # with the target
                            if R[key][i][1] >=0.75 or W[key][i][1] >3:    
                                # then we need to check the IC and IE
                                # then to update the IC_new
                                if IC[key][i][1] > IE[key][i][1]:
                                    
                                    IC[key][i][1] = (IC[key][i][1]+IE[key][i][1])/2
                                    
                                else:
                                    
                                    IC[key][i][1] = (IC[key][i][1]+IE[key][i][1])/2
                                                        
                            elif R[key][i][1] == 0 or W[key][i][1] == 0.01:
    
                                if IC[key][i][1] > IE[key][i][1]:
                                    
                                    IC[key][i][1] = IE[key][i][1]
                                    
                                else:
                                    
                                    IC[key][i][1] = IC[key][i][1] - item[1]                        
                                              
                            else:
                                if IC[key][i][1] > IE[key][i][1]:
                                    
                                    IC[key][i][1] = IE[key][i][1]
                                    
                                else:
                                    
                                    IC[key][i][1] = IC[key][i][1] - item[1]/2                               
    
                        elif item[1] <= 0.5:
                            
                            if R[key][i][1] >=0.75 or W[key][i][1] >3:    
                                
                                if IC[key][i][1] > IE[key][i][1]:
                                    
                                    IC[key][i][1] = IC[key][i][1] + item[1]
                                    
                                else:
                                    
                                    IC[key][i][1] = (IC[key][i][1]+IE[key][i][1])/2
                                                        
                            elif R[key][i][1] == 0 or W[key][i][1] == 0.01:
                                
                                IC[key][i][1] = (IE[key][i][1]+ IC[key][i][1])/2
                                              
                            else:
                                
                                if IC[key][i][1] > IE[key][i][1]:
                                    
                                    IC[key][i][1] = (IE[key][i][1]+IC[key][i][1])/2
                                    
                                else:
                                    
                                    IC[key][i][1] = IE[key][i][1]                             
                                
                        else: 
                            
                            if R[key][i][1] >=0.75 or W[key][i][1] >3:    
                                
                                if IC[key][i][1] > IE[key][i][1]:
                                    
                                    IC[key][i][1] = (IC[key][i][1]+IE[key][i][1])/2 
                                    
                                else:
                                    
                                    IC[key][i][1] = IC[key][i][1] + (1-item[1])/2
                                                        
                            elif R[key][i][1] == 0 or W[key][i][1] == 0.01:
                                
                                if IC[key][i][1] > IE[key][i][1]:
                                    
                                    IC[key][i][1] = IE[key][i][1]
                                    
                                else:
                                    
                                    IC[key][i][1] = IC[key][i][1] - item[1]
                                              
                            else:
                                
                                if IC[key][i][1] > IE[key][i][1]:
                                    
                                    IC[key][i][1] = (IE[key][i][1]+IC[key][i][1])/2
                                    
                                else:
                                    
                                    IC[key][i][1] -= item[1]/2                   
                    
                    
                
          
        else:
            # this situation means the target dose coverage did meet the request
            # which mainly caused from the OARS constrints
            flag = 3  # indicate this function is not good !
            
            print('Original parameters\n')
            
            for key in IC.keys():
                
                print(key,IC[key])
            
            #################################
            ## Please write your code here ##
            #################################
            
            
            
            for key in IC.keys(): # in this IC, the target cosntraints also in it
                
                if key in tar_res_nam or key == 'patient':
                    
                    for i,item in enumerate(IC[key]):
                        
                        IC[key][i][1] += R[key][i][1]/2
                        
                else:
                             
                    for i,item in enumerate(diff_result[key]):
                                               
                        if item[1] < 0.6:  ## 
                            
        
                            IC[key][i][1] += R[key][i][1]
                            
                        elif item[1] < 0.85: ## 
                            
                            IC[key][i][1] += R[key][i][1]/2
                            
                        else:                        
                             
                            IC[key][i][1]
                    
                        
    
    
    
        self.inf['ise'] = IE
        
        self.inf['isc'] = IC
        
        self.inf['wgt'] = W
        
        self.inf['rlp'] = R  
        
        
        
        return self.inf,flag


    def opt_HeadNeck(self,diff,tar_res_nam,level_OARs):        
        '''
           This is home developed automatic optimization module
           ##
           input: inf(iso_effect,iso_constraint,weight,rel_imp,step_size)
                  step_size(the step for adjusting dose parameters)
                  diff_result(the evaluation index)
                  level_OARs(the OARs with level for us)
                  theshold(theshold set for optimization)
                  
           ##       
           output: updated inf(iso_effect,iso_constraint,weight,rel_imp)
                   flag to mark whether target is overdose or underdose
                   
           希望采用自适应步长的方法进一步优化出比较好的结果
           而且此 program 也只是针对三个靶区结构
           此种写法目前只能针对每个器官对应一个评价指标，如果存在两个评价指标，此程序会报错
           
           relative_impact :
               1) +: 0-0.25
               2) ++: 0.25-0.5
               3) +++: 0.5-0.75
               4) ++++: 0.75-1.0
           
           
           ##
           这里没有才有input imrt constarints和evaluation indices一一对应来改变参数
           这里大部分情况是多对一的情况,或者是多对多情况
           
        
        '''
        import math
#        count = 0
        
        IE = self.inf['ise'] 
        
        IC = self.inf['isc'] 
        
        W = self.inf['wgt'] 
        
        R = self.inf['rlp']  

#        for item in tar_res_nam:
#        
#            del W[item]
#            
#            del IE[item]
#            
#            del IC[item]
#            
#            del R[item]
#    
#        del W['patient']
#        
#        del IE['patient']
#        
#        del IC['patient']
#        
#        del R['patient']
        
        diff_result = {}         ## 打一个补丁,将原来的diff换成新的
        for key in diff.keys():
            diff_result[key] = diff[key][0][1]
        
        target = [diff_result[i] for i in tar_res_nam]
        tar_sum = sum([math.floor(item) for item in target])
        
        prior_name = ['Neck']
        

    #    for item in diff_result.keys():
    #        if item == 'PAROTIDS':
    #            diff_result['Parotids'] = diff_result[item]
    #            del diff_result[item]
        ## force_OARs = {'Spinal Cord': 1, 'Cord PRV': 1,
        ## 'Brain Stem': 1, 'Stem PRV': 1, 'Len L': 2, 
        ## 'Len R': 2, 'Optic Chiasm': 2, 'Optic Nerve L': 2,
        ## 'Optic Nerve R': 2, 'Pituitary': 2, 'Inner Ears': 2,
        ## 'Parotids': 3, 'Esophagus': 4, 'Trachea': 4, 
        ## 'Thyroid': 4, 'Mandible': 4, 'Oral Cavity': 4, 'Larynx': 4, 'Neck': 4}
    
        if tar_sum == len(tar_res_nam):
            
            flag = 2 # indicate this functiion is good
            
            print('Original parameters\n')
            
            for key in IC.keys():
                
                print(key,IC[key])
                
            
            #################################
            ## please write your code here ##
            #################################
                if key in tar_res_nam or key == 'patient':
                    
                    for i,item in enumerate(IC[key]):
                        ## item = [type='qp',70]
                        if item[0] == 'type=o_q':
                            
                            print(item)
                            
                            if R[key][i][1] <= 0.5: ##(+,++)
                                
                                IC[key][i][1] = IE[key][i][1]
                                    
                            elif R[key][i][1] <= 0.75: ##(+++)
                                
                                if IC[key][i][1] > IE[key][i][1]:
                                    
                                    IC[key][i][1] = IE[key][i][1]
                                    
                                else:
                                    
                                    IC[key][i][1] = min((IC[key][i][1]+R[key][i][1]),IE[key][i][1])
                            
                            else:  ##(++++)
                                
                                if IC[key][i][1] > IE[key][i][1]:
                                    
                                    IC[key][i][1] = IC[key][i][1]
                                    
                                else:
                                    
                                    IC[key][i][1] = max((IC[key][i][1]+R[key][i][1]),IE[key][i][1])
                                    
                                    
                        else:
                            
                            IC[key][i][1] = IC[key][i][1]                
           
                
                if key in level_OARs and level_OARs[key] == 1: # this  indicate the stem and cord
                                    
                    for i in range(len(IE[key])):
                        
                        if 'PRV' in key.upper():
                    
                            if diff_result[key] > 1 :  # 这是对PRV给劲
                                
                                if R[key][i][1] >= 0.75 or W[key][i][1] >= 3:  # 变量极其难压制
                                    
                                    if IC[key][i][1] > IE[key][i][1]:
                                        
                                        IC[key][i][1] = (IC[key][i][1]+IE[key][i][1])/2
                                        
                                    else:
                                        
                                        IC[key][i][1]  += R[key][i][1]
                                                        
                                elif R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，这里需要将他压下去
                                    
                                    if IC[key][i][1] > IE[key][i][1]:
                                        
                                        IC[key][i][1] = (IE[key][i][1] + IC[key][i][1])/2
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)
    
                                
                                else:
                                    
                                    if IC[key][i][1] > IE[key][i][1]:
                                        
                                        IC[key][i][1] = (IC[key][i][1]+IE[key][i][1])/2
                                        
                                    else:
                                        
                                        IC[key][i][1] += round(diff_result[key],3)/3
                                                                          
                            elif diff_result[key] > 0.75: # 这是做计划次要矛盾
                                
                                if R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，可以直接赋值isoeffect
                                    ## 其实这里会陷入问题，对于isoconstraint,isoeffect,哪一个小取哪一个
                                    if IC[key][i][1] > IE[key][i][1]:
                                        
                                        IC[key][i][1] = IE[key][i][1]
                                        
                                    else:
                                        
                                        IC[key][i][1]  += round(diff_result[key],3)
                                
                                elif R[key][i][1] <= 0.5 and W[key][i][1] <= 5 and R[key][i][1] > 0 and W[key][i][1] > 0:  # 变量比较容易
                                    
                                    if IC[key][i][1] > IE[key][i][1]:
                                        
                                        IC[key][i][1] = IE[key][i][1]
                                        
                                    else:
                                        
                                        IC[key][i][1] += round(diff_result[key],3)/3
                                
                                else:
                                   
                                    if IC[key][i][1] > IE[key][i][1]:
                                        
                                        IC[key][i][1] = IC[key][i][1]
                                        
                                    else:
                                        
                                        IC[key][i][1]  = IE[key][i][1]
                            
                                
                            elif diff_result[key] > 0:  # 这种属于基本满足情况
                                
                                if R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，可以直接赋值isoeffect
                                    
                                    if IC[key][i][1] > IE[key][i][1]:
                                        
                                        IC[key][i][1] = IE[key][i][1]
                                        
                                    else:
                                        
                                        IC[key][i][1]  = IC[key][i][1]
                                
                                elif R[key][i][1] <= 0.5 and W[key][i][1] <= 3 and R[key][i][1] > 0 and W[key][i][1] > 0: # 考察一下权重和敏感度
                                    
                                    if IC[key][i][1] > IE[key][i][1]:
                                        
                                        IC[key][i][1] = IE[key][i][1]
                                        
                                    else:
                                        
                                        IC[key][i][1]  -= round(diff_result[key],3)/3
                                    
                                else:
                                        
                                        IC[key][i][1] = IC[key][i][1]
                                        
                        else:  
                            
                            if diff_result[key] > 1:# 这是对Stem&Cord的压制
                            
                                if R[key][i][1] >= 0.75 or W[key][i][1] >= 5:  # 变量极其难压制
                                    
                                    if IC[key][i][1] > IE[key][i][1]:
                                        
                                        IC[key][i][1] = IE[key][i][1]
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)/2 
                                                        
                                elif R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，这里需要将他压下去
                                    
                                    if IC[key][i][1] > IE[key][i][1]:
                                        
                                        IC[key][i][1] = IE[key][i][1]
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)
                                
                                else:
                                    if IC[key][i][1] > IE[key][i][1]:
                                        
                                        IC[key][i][1] = IE[key][i][1]
                                        
                                    else:
                                        
                                        IC[key][i][1] = IC[key][i][1] 
                                        
                            elif diff_result[key] >= 0.75: # 这是对Stem&Cord的压制
                                
                                if R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，可以直接赋值isoeffect
                                    ## 其实这里会陷入问题，对于isoconstraint,isoeffect,哪一个小取哪一个
                                    if IC[key][i][1] > IE[key][i][1]:
                                        
                                        IC[key][i][1] = IE[key][i][1]
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)/2
                                
                                elif R[key][i][1] < 0.75 and W[key][i][1] <= 3 and R[key][i][1] > 0 and W[key][i][1] > 0:  # 变量比较容易
                                    
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)//3
                                
                                else:
                                   
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IC[key][i][1]
                                    else:
                                        
                                        IC[key][i][1]  = IC[key][i][1] ##冻结
                                              
                            elif diff_result[key] > 0:  # 这种属于肯定满足情况
                                
                                if R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，可以直接赋值isoeffect
                                    
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]
                                        
                                    else:
                                        
                                        IC[key][i][1] = IC[key][i][1]
                                
                                elif R[key][i][1] < 0.75 and W[key][i][1] <= 3 and R[key][i][1] > 0 and W[key][i][1] > 0: # 考察一下权重和敏感度
                                    
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]
                                        
                                    else:
                                        
                                        IC[key][i][1] = IC[key][i][1]
                                    
                                else:
                                    
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IC[key][i][1]
                                        
                                    else:
                                        
                                        IC[key][i][1] = IE[key][i][1]
                                        
                if key in level_OARs and level_OARs[key] == 2: # 这说明是视觉系统
                
                    for i in range(len(IE[key])):
                        
                        if diff_result[key] > 1:  # 这是做计划的主要矛盾
                            
                            if R[key][i][1] >= 0.75 or W[key][i][1] > 5:  # 变量比较难压制
                                
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)/2 # isoconstraint走diff_result/2步长
                            
                            elif R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，这里需要将他压下去
                                
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                    
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)
                            
                            else:
                                
                                if IC[key][i][1] > IE[key][i][1]: 
                                        
                                    IC[key][i][1] = IE[key][i][1]                             
                                
                                else:
                                    
                                    IC[key][i][1] -= round(diff_result[key],3)/2 # isoconstraint走diff_result步长
                                
                        elif diff_result[key] >= 0.75:  #这是做计划的次要矛盾
                            
                            if R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，可以直接赋值isoeffect
                                ## 其实这里会陷入问题，对于isoconstraint,isoeffect,哪一个小取哪一个
                                if IC[key][i][1] > IE[key][i][1]: 
                                        
                                    IC[key][i][1] = IE[key][i][1]   
                                    
                                else:
                                    
                                    IC[key][i][1] -= round(diff_result[key],3)/2
                            
                            elif R[key][i][1] <= 0.75 and W[key][i][1] <= 3 and R[key][i][1] > 0 and W[key][i][1] > 0:  # 变量比较容易
    
                                if IC[key][i][1] > IE[key][i][1]: 
                                        
                                    IC[key][i][1] = IE[key][i][1]  
                                    
                                else:
                                    
                                    IC[key][i][1] = IC[key][i][1]
                            
                            else:
                                
                                if IC[key][i][1] > IE[key][i][1]: 
                                        
                                    IC[key][i][1] = IC[key][i][1] 
                                    
                                else:
                                    
                                    IC[key][i][1] += R[key][i][1]                              
                            
                        elif diff_result[key] > 0:  # 这种属于肯定满足情况
                            
                            if R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，可以直接赋值isoeffect
                                
                                if IC[key][i][1] > IE[key][i][1]: 
                                        
                                    IC[key][i][1] = IE[key][i][1]   
                                    
                                else:
                                    
                                    IC[key][i][1] -= round(diff_result[key],3)/3
                            
                            elif R[key][i][1] <= 0.5 and W[key][i][1] <= 3 and R[key][i][1] > 0 and W[key][i][1] > 0: # 考察一下权重和敏感度
                                
                                if IC[key][i][1] > IE[key][i][1]: 
                                        
                                    IC[key][i][1] = IE[key][i][1]  
                                    
                                else:
                                    
                                    IC[key][i][1] = IC[key][i][1]                            
                            else:
                                
                                if IC[key][i][1] > IE[key][i][1]: 
                                        
                                    IC[key][i][1] = IC[key][i][1]  
                                    
                                else:
                                    
                                    IC[key][i][1] += R[key][i][1]  
                                    
                if key in level_OARs and level_OARs[key] == 3: # this indicates parotids
                
                    for i in range(len(IE[key])):
                        
    #                    if i == 0:  # 这是指的第一个serial函数
    #                        IC[key][i][1] = IC[key][i][1]
    #                    
    #                    else:
                      
                            if diff_result[key] > 1:  # 这是做计划的主要矛盾
                                
                                if R[key][i][1] >= 0.75 or W[key][i][1] > 5:  # 变量比较难压制
                                    
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1]  = IC[key][i][1] # isoconstraint走diff_result/2步长
                                
                                
                                elif R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，这里需要将他压下去
                                    
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)
                                        
                                else:
                                    
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)/3
                                        
                            elif diff_result[key] > 0.85: # 这是做计划次要矛盾
                                
                                if R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，可以直接赋值isoeffect
                                    ## 其实这里会陷入问题，对于isoconstraint,isoeffect,哪一个小取哪一个
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)/2
                                
                                elif R[key][i][1] <= 0.75 and W[key][i][1] <= 3 and R[key][i][1] > 0 and W[key][i][1] > 0:  # 变量比较容易
                                    
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)/3    
                                        
                                else:
                                   
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IC[key][i][1]  
                                        
                                    else:
                                        
                                        IC[key][i][1] = IC[key][i][1]   
                        
                                
                            elif diff_result[key] > 0:  # 这种属于肯定满足情况
                                
                                if R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，可以直接赋值isoeffect
                                    
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] = IC[key][i][1]   
                                
                                elif R[key][i][1] <= 0.5 and W[key][i][1] <= 3 and R[key][i][1] > 0 and W[key][i][1] > 0: # 考察一下权重和敏感度
                                    
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)/2  
                                    
                                else:                                    
                                        IC[key][i][1] += R[key][i][1]
                                                         
                if key in level_OARs and level_OARs[key] == 4: # 这是剩余的organs
                
                    for i in range(len(IE[key])):
                        
                        if diff_result[key] > 1:  # 这是做计划的主要矛盾
                            
                            if key in prior_name:
                                
                                if R[key][i][1] >= 0.5 or W[key][i][1] >= 3:
                                    # 变量比较难压制
                                    if IC[key][i][1] < IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1] 
    
                                    else: 
    
                                        IC[key][i][1] += R[key][i][1]                                
    
                                else:
                                    ## 这表明这是很难压下去的
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] = IC[key][i][1]
                                                                    
                            else:
                                                    
                                if R[key][i][1] >= 0.75 or W[key][i][1] > 5:  # 变量比较难压制
                                    
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] = IC[key][i][1]                            
                                
                                elif R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，这里需要将他压下去
                                    
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)                            
                                else:
                                    
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)/2
                                        
                        elif diff_result[key] > 0.85: # 这是做计划次要矛盾
                            
                            if R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，可以直接赋值isoeffect
                                ## 其实这里会陷入问题，对于isoconstraint,isoeffect,哪一个小取哪一个
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)     
                            
                            elif R[key][i][1] <= 0.75 and W[key][i][1] <= 3 and R[key][i][1] > 0 and W[key][i][1] > 0:  # 变量比较容易
                                
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)/2                           
                            else:
                               
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IC[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] += R[key][i][1]     
                        
                            
                        elif diff_result[key] > 0:  # 这种属于肯定满足情况
                            
                            if R[key][i][1] == 0 and W[key][i][1] == 0.01:  # 僵尸指标，可以直接赋值isoeffect
                                
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)    
                                        
                            elif R[key][i][1] <= 0.5 and W[key][i][1] <= 3: # 考察一下权重和敏感度
                                
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IE[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] -= round(diff_result[key],3)/2                                
                            else:
                                
                                    if IC[key][i][1] > IE[key][i][1]: 
                                        
                                        IC[key][i][1] = IC[key][i][1]   
                                        
                                    else:
                                        
                                        IC[key][i][1] += R[key][i][1]          
        else:
            
            flag = 3  # indicate this function is not good !
            
            print('Original parameters\n')
            
            for key in IC.keys():
                
                print(key,IC[key])
            
            #################################
            ## Please write your code here ##
            #################################
            for key in R.keys():
                
                for i in range(len(R[key])):
                    
                    ### 这里不管加号多少，上调的幅度和加号成线性关系，如果是R = 0
                    ### 就不会改变
                    ## 打一个补丁
    #                if key == 'Parotids' and i == 0:
    #                    
    #                    pass    
                    
    #                else:
                        
                    if diff_result[key] < 0.6:  ## 表示这个指标压得很低，但是牺牲了靶区，可以多增加一点量来补偿靶区
                        
                        ## 如果指标压的很低，但是relative_impact很小的话，其实不会增加很大的量
                        ## 反而指标压的低，但是relative_impact很大的话，其实增加的量会比较大
                        IC[key][i][1] += R[key][i][1]
                        
                    elif diff_result[key] < 0.85: ## 表示指标压得不算太低，但是也需要补偿一些靶区
                        
                        IC[key][i][1] += R[key][i][1]/2
                        
                    else:                        ## 表示刚刚压住，需要减小一部分来补偿靶区
                         
                        IC[key][i][1] += R[key][i][1]/3
                    

        self.inf['ise'] = IE
        
        self.inf['isc'] = IC
        
        self.inf['wgt'] = W
        
        self.inf['rlp'] = R  
        
        
#        ## Check break conditions
#        for key in diff_result.keys():
#            
#            if key not in tar_res_nam and key != 'patient' and 'PTV' not in key and 'CTV' not in key and diff_result[key] < 1:
#                
#                count += 1
#        
#        if count == 15 and tar_sum == len(tar_res_nam):
#            
#            flag = count   ## set break out point 必须是靶区到达要求，危及器官压下来才可以退出
#            
#        else:
#            
#            flag = flag
        
        return self.inf,flag



    def exe1(self,tras):
        '''
          This function was mainly used for extract the dvh results for optimization 
        '''
        
        import random 
        import time
        
        flag = self.read_flag()   #read flag file
        while flag == '1':        
            '''
            This time sleep is for Monaco Calculation
            '''
            time.sleep(15)    
            
            flag = self.read_flag()      
            
            print ('flag = 1,waiting for Monaco Calculation...\n')      
        
        print ('flag = {}, start adjusting optimiation parameters...\n'.format(flag))    
            
        if flag == '0':      
            
            strt_fun,strt_index,line = self.read_template()   #read template information
        
            dvh_name = self.read_dvh()   #read saved name of dvh.csv
            
            DVH = self.csv_read_to_dvh()   #from .csv file extract the DVH data
            
            dvh_new_data,pres_strt_ind = self.read_csv_zs(DVH,tras)  #1) ensure names in dvh is consistent with struct 2)read prescription
            
            dvh_inf = self.DVH_inf(dvh_new_data)  #extract Dmean and Dmax from DVH
            
            dvh_indices,diff_result = self.plan_results1(dvh_inf,dvh_new_data,pres_strt_ind)   #calcualte the ratio of calculation and prescription
           
            self.write_dvh(str(dvh_name+str(random.randint(0,10)))) # to prevent the repetition of name
            
        return strt_fun,strt_index,line,diff_result


    def exe2(self,tar_res_nam,selection,level_OARs,tras):
        '''
           This function mainly was mainly used for parameters modification
        ''' 
        strt_fun,strt_index,line,diff_result = self.exe1(tras)     
        
        self.inf = {} # to store all the information in template(isoconstraint,isoeffect,weight,relative impact,shrink margin)
        
        for i,item in enumerate(self.ind[3]):
            
            self.inf[item] = self.extract_strt_fun(strt_fun,self.ind[0][i],self.ind[1][i])
        
        
        ####================opt_packages=========================## 
        if selection == '1':
            ## 用来优化前列腺cases
            inf,flag = self.opt_prostate(diff_result,tar_res_nam)
            
        else:
            ## 用来优化头颈cases
#            level_OARs
            inf,flag = self.opt_HeadNeck(diff_result,tar_res_nam,level_OARs)
        ####================opt_packages=========================##
        
        
        #to transfer the inforamtion to struct_fun
        struct_fun = self.back_strt_fun(strt_fun,strt_index,line,self.path[-1],inf['isc'],self.ind[2][1],self.ind[0][1])             
               
        for key in inf['isc'].keys():
            
            print('########################################')
            print('Updated parameters\n')
            print(key,inf['isc'][key])   
    
    
        
        return struct_fun,flag,inf,diff_result,line


    def exe3(self,tar_res_nam,selection,level_OARs,tras):
        '''
           this function mainly execute the struct_fun's transformation
        '''
        struct_fun_updated,mark3,information,diff_result,line = self.exe2(tar_res_nam,selection,level_OARs,tras)
        
        if mark3 == 3:
            print ('Target was underdose!!\n')
            print ('===========================================================================')
            print ([(item,diff_result[item][0][1]) for item in tar_res_nam])            
            print ('===========================================================================')
            
            ## print some OARs still overdose
            
            self.show_OARs(diff_result,tar_res_nam)
            
            self.write_template(line,struct_fun_updated) # transfer the updated template to .hyp
            
            
            # write flag to 1 to tell Monaco could reload template and calculate again
            self.write_flag()
       
        elif mark3 == 2:
            print('Target has maintained...\n')
            print ('===========================================================================')
            print ([(item,diff_result[item][0][1]) for item in tar_res_nam])  
            print ('===========================================================================')
            
            ## print some OARs still overdose
            
            self.show_OARs(diff_result,tar_res_nam)
            
            self.write_template(line,struct_fun_updated)
            
            # write flag to 1
            self.write_flag()
            
        else:
            
            print('Break out of the iteration and further optimization...\n')
            print ('===========================================================================')
            print ([(item,diff_result[item][0][1]) for item in tar_res_nam])      #        print ('Three target coverage {}: {} {}: {} {}: {}'.format(tar_res_nam[0],round(95*diff_result[tar_res_nam[0]],2),tar_res_nam[1],round(95*diff_result[tar_res_nam[1]],2),tar_res_nam[2],round(95*diff_result[tar_res_nam[2]],2)))
            print ('===========================================================================')
            
            ## print some OARs still overdose
            
            self.show_OARs(diff_result,tar_res_nam)
            
            self.write_template(line,struct_fun_updated)
            
            # write flag to 1
            self.write_flag()
    
        return mark3,information,diff_result

