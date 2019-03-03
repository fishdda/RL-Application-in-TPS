# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 17:14:57 2019

@author: Shelter6
"""
import tensorflow as tf

def main():
    ## generate template HN
    from MT import Tool
    from GT import Temp

    X = Temp(path_temp,csv_file,colone_path1)
    strt_ind_list,tras = X.initial(struct,struct_set,path_beam,selection)
    level_OARs = X.classify(strt_ind_list)
    print('the template path is following:\n')
    print('========================\n')
    print(colone_path1)
    print('========================\n')
    print('Please check the generated template!!!\n')
    print('.......\n')
    # F = input('If the template is ok, please enter 1; if not, please enter 0:\n')
    F = '1'
    print('F:',F)
    ## optimization
    if F == '1':
        
        sess = tf.Session()
#        saver = tf.train.Saver()

        Y = Tool(path,ind_loc_strt,iter_path,sess)
        Y.write_tem_name()
        Y.write_iter(iteration)
        Y.write_flag()

        start3 = time.time()

        sess.run(tf.global_variables_initializer())

        for k in range(iteration):

            fla3,inf,diff,score = Y.exe3(tar_res_nam,selection,level_OARs,tras,k)

            inf_iter['iteration' + str(k + 1)] = inf

            diff_iter['iteration' + str(k + 1)] = diff

            # print("Saving model...")
            # save_path = saver.save(sess, os.getcwd() + "/AC.ckpt")

        # To Write the flag from 1 to 2
            score_iter.append(score)

            if k > 0:
              if (score_iter[k] - score_iter[k-1]) < -0.85 or k > 50:
                break

              else:
                print ("Continue!!\n")
                pass

            else:
              print("Continue!!\n")



        Y.write_flag_end()

        end3 = time.time()

        print('the step consume {} s'.format(end3 - start3))

    else:
        Y = Tool(path,ind_loc_strt,iter_path)
        Y.write_iter(iteration)
        print('Please modify your initial template!!\n')


#%%==============================%%#
import os
import time
import random
import glob
import pydicom
ind_loc_strt = [[3,7,8,10,9],
[13,14,10,7,15],
['shrinkmargin=','isoconstraint=','isoeffect=','weight=','relativeimpact='],
['skg','isc','ise','wgt','rlp']]
def_path = os.getcwd()
txt_path = ''.join([def_path,'\\database\\txtfile\\file3'])
temp_path = 'C:\\auto template\\'
path_beam = ''.join([def_path,'\\database\\txtfile\\file2\\part4(beam_arc).txt'])
path_temp = glob.glob(''.join([def_path,'\\database\\txtfile\\file1\\*.txt']))
struct_set1 = {'CTV4500': 0,'CTV6750': 0,'CTV6275': 0,'CTV4750': 0,'Metal': 0,
              'Carbon Fiber': 0,'Foam Core': 0,'PTV6750': 1,'PTV6275': 2,
              'PTV4750': 3,'PTV4500': 4,'Bladder': 5,'Rectum': 6,'Pubic Bone': 7,
              'Femoral Head R': 8,'Femoral Head L':9,'Intestine': 10,
              'Penile Bulb': 11,'patient': 100}
struct_set2 = {'GTVnd6600': 100, 'Artifact': 100, 'Stem PRV': 6,'BrainPRV':6,
              'Thyroid': 19, 'TMJ-R': 14, 'Metal': 100, 'Lung L': 100,
              'Parotids': 16, 'CTVtb': 100, 'Pituitary': 12, 'SPPRV': 4,
              'Foam Core': 100, 'Trachea': 18, 'patient': 24, 'Len all': 100,
              'Cord PRV': 4, 'CordPRV': 4,'Len L': 7, 'CTV5096': 100, 'PGTVnd6600': 100,
              'FanDown': 100, 'Larynx': 22, 'Spinal Cord': 3, 'Eye R': 100,
              'PGTVnx6996-1': 100, 'spinalcord3': 100, 'Optic Chiasm': 9,
              'TMJ-L': 13, 'PAROTIDS': 16, 'PGTVnd6996': 1, 'Lung R': 100,
              'Len R': 8, 'TM R': 14, 'Oral Cavity': 21, 'Parotid all': 16,
              'Neck': 23, 'Mid': 100, 'Mandible': 20, 'NeckPc': 100,
              'teeth': 100, 'Optic Nerve L': 10, 'Inner Ears': 15,
              'PGTVnx6996': 0, 'OralCavity2': 100, 'FanUp': 100, 'Brain Stem': 5,
              'PTV5096-1': 100, 'GTVnx6996': 100, 'PTV5096': 2, 'Eye L': 100,
              'TM L': 13, 'Carbon Fiber': 100, 'PTVtb5936': 100, 'Neck2': 100,
              'GTVnd6996': 100, 'Optic Nerve R': 11, 'Parotid R': 100, 'BSPRV': 6,
              'Oral Cavity2': 100, 'Esophagus': 17, 'Optic Nerve all': 100,
              'Parotid L': 100, 'Brain': 100}
# ID = input('Please enter the patient ID:\n')
ID = '20180125'
print('Patient ID:', ID )
# selection = input('Please enter your selection: Prostate(enter 1) & HN(enter 2)\n')
selection = '1'
print('Selection:', selection)
if selection == '1':
    tar_res_nam = ['PTV6750','PTV4750']
    path_struct_set = glob.glob(''.join([def_path,'\\database\\case\\prostate\\struct_file\\*.dcm']))
    stru_path= ''.join([def_path,'\\database\\case\\prostate\\struct_file\\',ID,'_StrctrSets.dcm'])
    csv_file = ''.join([def_path,'\\database\\case\\prostate\\prescription\\',ID,'.csv'])
    colone_path1 = ''.join([temp_path,'template.hyp'])
    struct_set = struct_set1
else:
    tar_res_nam = ['PGTVnx6996','PGTVnd6996','PTV5096']
    path_struct_set = glob.glob(''.join([def_path,'\\database\\case\\HN\\struct_file\\*.dcm']))
    stru_path= ''.join([def_path,'\\database\\case\\HN\\struct_file\\',ID,'_StrctrSets.dcm'])
    csv_file = ''.join([def_path,'\\database\\case\\HN\\prescription\\',ID,'.csv'])
    colone_path1 = ''.join([temp_path,'template.hyp'])
    struct_set = struct_set2

dvh_path = ''.join(['C:\\Users\\Shelter6\\Desktop\\dvh\\',ID,'\\round4\\'])
path_ = [''.join([txt_path,'\\',item]) for item in os.listdir(txt_path) if item[-3:] == 'txt']
path = [csv_file,stru_path,path_,dvh_path,colone_path1]
struct= pydicom.read_file(stru_path,force=True)
inf_iter,diff_iter = {},{}
score_iter = []


fla3 = 0
# iteration = int(input('Please enter the wanted iterations:\n'))
iteration = 100
print('Iteration:', iteration)
iter_path = 'C:\\Users\\EXTHuaXia\\Desktop\\warm_HN\\database\\txtfile\\iteration.txt'

if __name__ == '__main__':
    main()
