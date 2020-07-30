class DICOM_DVH:
    # please note current DICOM data structure follows 
    # DATA
    # -- 002
    # -- -- CT1.dcm
    # -- -- CT2.dcm
    # -- -- Structure.dcm
    # -- -- Plan.dcm
    # -- -- Dose.dcm
    # -- -- BeamDose.dcm

    def __init__(self,data_path):
        self.data_path = data_path
        self.STRT,self.DOSE,self.DVH_DATA_ = [],[],[]



    def Extrac_DOSE_STRT(self):
        ''' 
        Extract Dose matrix and strcuture from DICOM files
        '''
        import os
        import pydicom
        # load the dicom data to current scripts
        file_name = os.listdir(self.data_path)
        for nam in file_name:
            temp_name = os.listdir(os.path.join(self.data_path,nam))
            for dcm_nam in temp_name:
                dcm = pydicom.read_file(os.path.join(self.data_path,nam,dcm_nam),force=True)
                if dcm.Modality == 'RTDOSE' and dcm.DoseSummationType == 'PLAN':
                    self.DOSE.append(dcm)
                elif dcm.Modality == 'RTSTRUCT':
                    self.STRT.append(dcm)

        return self.DOSE, self.STRT
    
    def Extrac_DVH(self):
        '''
        Extract DVH data from DICOM files for further evaluation
        '''
        DVH_DATA = {}
        for TEST_DOSE,TEST_STRT in zip(self.DOSE,self.STRT):
            for i in range(len(TEST_STRT.StructureSetROISequence)):
                if TEST_STRT.StructureSetROISequence[i].ROINumber ==  TEST_DOSE.DVHSequence[i].DVHReferencedROISequence[0].ReferencedROINumber:
                    DVH_DATA[TEST_STRT.StructureSetROISequence[i].ROIName] =  TEST_DOSE.DVHSequence[i].DVHData
                else:
                    print(TEST_STRT.StructureSetROISequence[i].ROIName)
                    continue
            self.DVH_DATA_.append(DVH_DATA)
        
        return self.DVH_DATA_
 

    


