class FineTune_Funcs:
    
    '''
       This class store all kinds of modifier functions.
    '''

    def __init__(self,dvh_stat_calc,IMRT_TABLE,Flag,OAR_preferences):

        self.dvh_stat_calc = dvh_stat_calc     # store the current calculation DVH statistics criteria and discrepancy between protocols
        self.IMRT_Constraints = IMRT_TABLE     # all the variables stored in IMRT_TABLE
        self.Mark = Flag                       # mark current Monaco TPS state
        self.OARs_prefer = OAR_preferences     # mark the OARs should be protected especially  OAR_preferences = ['Spinal Cord','Brain Stem','Larynx'...]


    def _NPC_Modifier_V1(self):        
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
        
        IE = self.IMRT_Constraints['ISE']
        
        IC = self.IMRT_Constraints['ISE']
        
        W = self.IMRT_Constraints['ISE']
        
        R = self.IMRT_Constraints['ISE']

        Thres_Dose = self.IMRT_Constraints['thresholddose'] # specific for quadratic overdose 
        
        diff_result = {}         ## 打一个补丁,将原来的diff换成新的
        for key in diff.keys():
            diff_result[key] = diff[key][0][1]
        
        target = [diff_result[i] for i in tar_res_nam]
        tar_sum = sum([math.floor(item) for item in target])
    
    
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
        
        return self.inf,flag



    def dvh_stat_ind_VeryBad_OARs(self,strt_name,dvh_index):
        '''
        strt_name: 'PGTVnd','Parotid L'
        dvh_index: (0,['D50% < 3800 cGy', 23.7, 0.62368, '7'])

        alpha = 0.05 is a small pertubation for dvh stat indices
        DVH statistics indices evaluation criteria: OARs
        1) VeryBad      =>  jtem(diff_from_protocol) > 1.5
        2) LittleBad    =>  jtem(diff_from_protocol) > 1.0 - alpha & jtem(diff_from_protocol) <= 1.5
        3) Ideal        =>  jtem(diff_from_protocol) > 0.7 - alpha & jtem(diff_from_protocol) <= 1.0 - alpha
        4) WellDone     =>  jtem(diff_from_protocol) > 0.4 - alpha & jtem(diff_from_protocol) <= 0.7 - alpha
        5) Perfect      =>  jtem(diff_from_protocol) <= 0.4 - alpha


        relative impact 0-0.25 +
                        0.25-0.5 ++
                        0.5-0.75 +++
                        0.75-1.0 ++++
######################################################################
######################################################################
        if rlp <= 0.25 && weight <= 0.75: 
            1) isc > ise, isc_new = ise; 
            2) isc < ise, isc_new = isc - diff_ratio1
        
        if rlp > 0.25 && rlp <= 0.5 && weight <= 0.75:
            1) isc > ise, isc_new = ise; 
            2) isc < ise, isc_new = isc - diff_ratio1          

        if rlp > 0.5 && rlp <= 0.75 && weight <= 0.75:
            1) isc > ise, isc_new = ise; 
            2) isc < ise, isc_new = isc - diff_ratio1      

        if rlp > 0.75 && rlp <= 1.00 && weight <= 0.75:
            1) isc > ise, isc_new = ise; 
            2) isc < ise, isc_new = isc - diff_ratio1      
#######################################################################
#######################################################################

#######################################################################
#######################################################################
        if rlp <= 0.25 && weight <= 1.5 and weight > 0.75:
            1) isc > ise, isc_new = isc*(1/diff_ratio); 
            2) isc < ise, isc_new = isc - diff_ratio1      

        if rlp > 0.25 && rlp <= 0.5 && weight <= 1.5 and weight > 0.75:
            1) isc > ise, isc_new = isc*(1/diff_ratio); 
            2) isc < ise, isc_new = isc - diff_ratio1       

        if rlp > 0.5 && rlp <= 0.75 && weight <= 1.5 and weight > 0.75:
            1) isc > ise, isc_new = isc*(1/diff_ratio); 
            2) isc < ise, isc_new = isc - diff_ratio1     

        if rlp > 0.75 && rlp <= 1.00 && weight <= 1.5 and weight > 0.75:
            1) isc > ise, isc_new = isc*(1/diff_ratio); 
            2) isc < ise, isc_new = isc - diff_ratio1    
#######################################################################
#######################################################################    

#######################################################################
####################################################################### 
        if weight > 1.5:
            1) isc > ise, isc_new = isc - diff_ratio1  

#######################################################################
#######################################################################
        '''
        delta_RLP1, delta_RLP2, delta_RLP3, delta_RLP4 = 0.25,0.5,0.75,1
        delta_WGT1, delta_WGT2  = 0.75, 1.5

        # it's a very bad index of DVH
        if strt_name in self.OARs_prefer:
            # if OARs in preference list means need more constraints 

            if self.RLP[strt_name].shape != (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name].values[dvh_index] <= delta_RLP1 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP2 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP3 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP4 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

            elif self.RLP[strt_name].shape == (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name] <= delta_RLP1 and self.WGT[strt_name] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP2 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP3 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name].values: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP4 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

        else:
            # if OARs not in preference list means need more constraints 

            if self.RLP[strt_name].shape != (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name].values[dvh_index] <= delta_RLP1 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP2 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP3 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP4 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

            elif self.RLP[strt_name].shape == (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name] <= delta_RLP1 and self.WGT[strt_name] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP2 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP3 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name].values: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP4 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

        return self.IMRT_Constraints_Updated

    def dvh_stat_ind_LittleBad_OARs(self,strt_name,dvh_index):
        '''

        alpha = 0.05 is a small pertubation for dvh stat indices

        DVH statistics indices evaluation criteria: OARs
        1) VeryBad      =>  jtem(diff_from_protocol) > 1.5
        2) LittleBad    =>  jtem(diff_from_protocol) > 1.0 - alpha & jtem(diff_from_protocol) <= 1.5
        3) Ideal        =>  jtem(diff_from_protocol) > 0.7 - alpha & jtem(diff_from_protocol) <= 1.0 - alpha
        4) WellDone     =>  jtem(diff_from_protocol) > 0.4 - alpha & jtem(diff_from_protocol) <= 0.7 - alpha
        5) Perfect      =>  jtem(diff_from_protocol) <= 0.4 - alpha
        '''

        delta_RLP1, delta_RLP2, delta_RLP3, delta_RLP4 = 0.25,0.5,0.75,1
        delta_WGT1, delta_WGT2  = 0.75, 1.5

        # it's a very bad index of DVH
        if strt_name in self.OARs_prefer:
            # if OARs in preference list means need more constraints 

            if self.RLP[strt_name].shape != (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name].values[dvh_index] <= delta_RLP1 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP2 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP3 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP4 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

            elif self.RLP[strt_name].shape == (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name] <= delta_RLP1 and self.WGT[strt_name] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP2 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP3 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name].values: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP4 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

        else:
            # if OARs not in preference list means need more constraints 

            if self.RLP[strt_name].shape != (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name].values[dvh_index] <= delta_RLP1 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP2 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP3 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP4 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

            elif self.RLP[strt_name].shape == (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name] <= delta_RLP1 and self.WGT[strt_name] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP2 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP3 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name].values: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP4 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

        return self.IMRT_Constraints_Updated

    def dvh_stat_ind_Ideal_OARs(self,strt_name,dvh_index):
        '''

        alpha = 0.05 is a small pertubation for dvh stat indices

        DVH statistics indices evaluation criteria: OARs
        1) VeryBad      =>  jtem(diff_from_protocol) > 1.5
        2) LittleBad    =>  jtem(diff_from_protocol) > 1.0 - alpha & jtem(diff_from_protocol) <= 1.5
        3) Ideal        =>  jtem(diff_from_protocol) > 0.7 - alpha & jtem(diff_from_protocol) <= 1.0 - alpha
        4) WellDone     =>  jtem(diff_from_protocol) > 0.4 - alpha & jtem(diff_from_protocol) <= 0.7 - alpha
        5) Perfect      =>  jtem(diff_from_protocol) <= 0.4 - alpha
        '''
        delta_RLP1, delta_RLP2, delta_RLP3, delta_RLP4 = 0.25,0.5,0.75,1
        delta_WGT1, delta_WGT2  = 0.75, 1.5

        # it's a very bad index of DVH
        if strt_name in self.OARs_prefer:
            # if OARs in preference list means need more constraints 

            if self.RLP[strt_name].shape != (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>
                print('dvh_index:{}'.format(dvh_index))
                print('dvh_index:{}'.format(dvh_index))
                print('relative impact:{}'.format(self.RLP[strt_name].values))
                if self.RLP[strt_name].values[dvh_index] <= delta_RLP1 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP2 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP3 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP4 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

            elif self.RLP[strt_name].shape == (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name] <= delta_RLP1 and self.WGT[strt_name] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP2 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP3 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name].values: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP4 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value


        else:
            # if OARs not in preference list means need more constraints 

            if self.RLP[strt_name].shape != (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>
                print('self.RLP[strt_name]:{}'.format(self.RLP[strt_name]))
                print('self.RLP[strt_name].values:{}'.format(self.RLP[strt_name].values))
                print('dvh_index:{}'.format(dvh_index))
                if self.RLP[strt_name].values[dvh_index] <= delta_RLP1 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP2 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP3 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP4 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

            elif self.RLP[strt_name].shape == (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name] <= delta_RLP1 and self.WGT[strt_name] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP2 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP3 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name].values: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP4 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

        return self.IMRT_Constraints_Updated

    def dvh_stat_ind_WellDone_OARs(self,strt_name,dvh_index):
        '''

        alpha = 0.05 is a small pertubation for dvh stat indices

        DVH statistics indices evaluation criteria: OARs
        1) VeryBad      =>  jtem(diff_from_protocol) > 1.5
        2) LittleBad    =>  jtem(diff_from_protocol) > 1.0 - alpha & jtem(diff_from_protocol) <= 1.5
        3) Ideal        =>  jtem(diff_from_protocol) > 0.7 - alpha & jtem(diff_from_protocol) <= 1.0 - alpha
        4) WellDone     =>  jtem(diff_from_protocol) > 0.4 - alpha & jtem(diff_from_protocol) <= 0.7 - alpha
        5) Perfect      =>  jtem(diff_from_protocol) <= 0.4 - alpha
        '''
        delta_RLP1, delta_RLP2, delta_RLP3, delta_RLP4 = 0.25,0.5,0.75,1
        delta_WGT1, delta_WGT2  = 0.75, 1.5

        # it's a very bad index of DVH
        if strt_name in self.OARs_prefer:
            # if OARs in preference list means need more constraints 

            if self.RLP[strt_name].shape != (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name].values[dvh_index] <= delta_RLP1 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP2 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP3 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP4 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

            elif self.RLP[strt_name].shape == (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name] <= delta_RLP1 and self.WGT[strt_name] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP2 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP3 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name].values: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP4 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

        else:
            # if OARs not in preference list means need more constraints 

            if self.RLP[strt_name].shape != (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name].values[dvh_index] <= delta_RLP1 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP2 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP3 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP4 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

            elif self.RLP[strt_name].shape == (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name] <= delta_RLP1 and self.WGT[strt_name] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP2 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP3 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name].values: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP4 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

        return self.IMRT_Constraints_Updated

    def dvh_stat_ind_Perfect_OARs(self,strt_name,dvh_index):
        '''

        alpha = 0.05 is a small pertubation for dvh stat indices

        DVH statistics indices evaluation criteria: OARs
        1) VeryBad      =>  jtem(diff_from_protocol) > 1.5 - 
        2) LittleBad    =>  jtem(diff_from_protocol) > 1.0 - alpha & jtem(diff_from_protocol) <= 1.5 - alpha
        3) Ideal        =>  jtem(diff_from_protocol) > 0.7 - alpha & jtem(diff_from_protocol) <= 1.0 - alpha
        4) WellDone     =>  jtem(diff_from_protocol) > 0.4 - alpha & jtem(diff_from_protocol) <= 0.7 - alpha
        5) Perfect      =>  jtem(diff_from_protocol) <= 0.4 - alpha
        '''
        delta_RLP1, delta_RLP2, delta_RLP3, delta_RLP4 = 0.25,0.5,0.75,1
        delta_WGT1, delta_WGT2  = 0.75, 1.5

        # it's a very bad index of DVH
        if strt_name in self.OARs_prefer:
            # if OARs in preference list means need more constraints 

            if self.RLP[strt_name].shape != (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name].values[dvh_index] <= delta_RLP1 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP2 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP3 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP4 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

            elif self.RLP[strt_name].shape == (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name] <= delta_RLP1 and self.WGT[strt_name] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP2 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP3 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name].values: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP4 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

        else:
            # if OARs not in preference list means need more constraints 

            if self.RLP[strt_name].shape != (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name].values[dvh_index] <= delta_RLP1 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP2 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP3 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name].values[dvh_index] <= delta_RLP4 and self.WGT[strt_name].values[dvh_index] < delta_WGT1: 

                    if self.ISC[strt_name].values[dvh_index] > self.ISE[strt_name].values[dvh_index]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISE[strt_name].values[dvh_index]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value[dvh_index] = self.ISC[strt_name].values[dvh_index] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

            elif self.RLP[strt_name].shape == (): 
                # separate two types. e.g type(IMRT_TABLE['RLP'].loc['Lung'])== <class 'numpy.float64'> 
                #                     e.g type(IMRT_TABLE['RLP'].loc['BODY'])== <class 'pandas.core.series.Series'>

                if self.RLP[strt_name] <= delta_RLP1 and self.WGT[strt_name] < delta_WGT1: # relative impact < + and weight < 0.5
                    
                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP2 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP3 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name].values: # isoconstraint > isoeffect


                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                elif self.RLP[strt_name] <= delta_RLP4 and self.WGT[strt_name] < delta_WGT1: 

                    if self.ISC[strt_name] > self.ISE[strt_name]: # isoconstraint > isoeffect

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISE[strt_name]   # replace Isoconstraint with isoeffect

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

                    else:

                        temp_value = self.IMRT_Constraints_Updated.at[strt_name,'ISC']

                        temp_value = self.ISC[strt_name] - self.dvh_diff_ratio_l1 # indicate it's the diff_ratio

                        self.IMRT_Constraints_Updated.at[strt_name,'ISC'] = temp_value

        return self.IMRT_Constraints_Updated


    def _NPC_Modifier_V2(self):
        
        '''
          1) Check each strcuture DVH statistics e.g. Parotid L D50% < 30, diff = 0.7
        '''
        self.IMRT_Constraints_Updated = self.IMRT_Constraints

        self.ISC = self.IMRT_Constraints['ISC']
        self.ISE = self.IMRT_Constraints['ISE']
        self.WGT = self.IMRT_Constraints['WGT']
        self.RLP = self.IMRT_Constraints['RLP']
        self.ThDose = self.IMRT_Constraints['thresholddose'] # specific for quadratic overdose 

        self.dvh_diff_ratio_l1, self.dvh_diff_ratio_l2, self.dvh_diff_ratio_l3, self.dvh_diff_ratio_l4 = 1.5, 1.0, 0.7, 0.4  # determine the boundary values


        for item in self.dvh_stat_calc.keys(): 
            # go through all the structure name

           if 'pgtv' not in item.lower() and 'pctv' not in item.lower():   # indicate the OARs

               for j,jtem in enumerate(self.dvh_stat_calc[item]): # go through each dvh statistics index

                   print('j,jtem:{},{}'.format(j,jtem))

                   if jtem[2] > self.dvh_diff_ratio_l1:      # very bad

                       self.IMRT_Constraints_Updated = self.dvh_stat_ind_VeryBad_OARs(item,(j,j))

                   elif jtem[2] > self.dvh_diff_ratio_l2:    # Little bad

                       self.IMRT_Constraints_Updated = self.dvh_stat_ind_LittleBad_OARs(item,j)

                   elif jtem[2] > self.dvh_diff_ratio_l3:    # Ideal

                       self.IMRT_Constraints_Updated = self.dvh_stat_ind_Ideal_OARs(item,j)

                   elif jtem[2] > self.dvh_diff_ratio_l4:    # WellDone

                       self.IMRT_Constraints_Updated = self.dvh_stat_ind_WellDone_OARs(item,j)

                   else:                                     # Perfect

                       self.IMRT_Constraints_Updated = self.dvh_stat_ind_Perfect_OARs(item,j)

           else:        
               # indicate the target region

               for j,jtem in enumerate(self.dvh_stat_calc[item]): # go through each dvh statistics index

                   if jtem[2] > 1.0:

                       self.IMRT_Constraints_Updated = self.IMRT_Constraints_Updated

                   elif jtem[2] > 0.9:

                       self.IMRT_Constraints_Updated = self.IMRT_Constraints_Updated

        mark = 2
        return self.IMRT_Constraints_Updated,mark






