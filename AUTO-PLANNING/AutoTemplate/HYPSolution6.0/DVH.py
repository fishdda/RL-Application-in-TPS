    
    def csv_read_to_dvh(self):
        '''
           This function was used to extract DVH data from csv file
           20200330 was updated and no error occurs
        '''
        import csv
        import os
        ss = os.listdir('C:/autotemplate/dvh')
        dir_list = sorted(ss,  key=lambda x: os.path.getmtime(os.path.join('C:/autotemplate/dvh', x)))
        csv_file = [item for item in dir_list if item.split('.')[1] == 'csv']
        
        path_dvh = os.path.join('C:/autotemplate/dvh',csv_file[-1])
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