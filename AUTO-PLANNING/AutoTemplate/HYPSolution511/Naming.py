# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 14:15:37 2020

@author: Henry Huang in Elekta Shanghai Ltd
"""
class NAME_Deal():
    '''
       This class aims to solve following issues:
           1. names order in .hyp file which would be a big issue for optimization
           2. structure name inconsistency between contournames and names in treatment protocol
           3. how to standardize for each patient's name
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
         
