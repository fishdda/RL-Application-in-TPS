class DATAPROCESS:
    '''
    Currently, this class is only specific to VMAT plans 
    '''

    def __init__(self,RAW_DATA_PATH,NEW_DATA_PATH):
        self.RAW_DATA_PATH = RAW_DATA_PATH
        self.NEW_DATA_PATH = NEW_DATA_PATH
        self.PLAN = {}

    def TRANSFER_RAW_DATA(self):

        import numpy as np 
        import os
        import pydicom 

        # deal with CT image data, dose data and MLC & MU intensity

        file_names = os.listdir(self.RAW_DATA_PATH)

        for j,file_nam in enumerate(file_names):
            CT_ = []
            print('This is {}th patient'.format(j))
            temp_files = os.listdir(os.path.join(self.RAW_DATA_PATH,file_nam)) # all CT names
            for dcm_nam in temp_files:
                # 
                dcm = pydicom.read_file(os.path.join(self.RAW_DATA_PATH,file_nam,dcm_nam),force=True)
                if dcm.Modality == 'CT':
                    print(dcm.Modality)
                    dcm.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
                    img = dcm.pixel_array

                    CT_.append(img)
                    intercept = dcm.RescaleIntercept
                    slope = dcm.RescaleSlope

                # The intercept is usually -1024, so air is approximately 0

                elif dcm.Modality == 'RTDOSE' and dcm.DoseSummationType == 'PLAN':

                    dcm.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
                    DOSE = np.array(dcm.pixel_array * dcm.DoseGridScaling)
                    print('The DOSE array shape:{}'.format(DOSE.shape))
                    np.save(self.NEW_DATA_PATH + file_nam + '_Dose.npy',DOSE)

                elif dcm.Modality == 'RTPLAN':

                    
                    Total_MU = float(dcm.FractionGroupSequence[0].ReferencedBeamSequence[0].BeamMeterset)
                    MLC = np.zeros([160,len(dcm.BeamSequence[0].ControlPointSequence)])
                    JAW = np.zeros([2,len(dcm.BeamSequence[0].ControlPointSequence)])
                    MU_,Gantry = [],[]
                    for j in range(len(dcm.BeamSequence[0].ControlPointSequence)):
                        # extract JAW and MLC
                        JAW[:,j] = np.array(dcm.BeamSequence[0].ControlPointSequence[j].BeamLimitingDevicePositionSequence[0].LeafJawPositions).T
                        MLC[:,j] = dcm.BeamSequence[0].ControlPointSequence[j].BeamLimitingDevicePositionSequence[1].LeafJawPositions
                        Gantry.append(dcm.BeamSequence[0].ControlPointSequence[j].GantryAngle)
                        MU_.append(float(dcm.BeamSequence[0].ControlPointSequence[j].CumulativeMetersetWeight))
                    MU = []
                    for k,ktem in enumerate(MU):
                        if k > 1:
                            MU.append((MU_[k]-MU_[k-1])*Total_MU)
                        else:
                            MU.append(ktem)

                    self.PLAN['MU'] = MU
                    self.PLAN['Gantry'] = Gantry
                    self.PLAN['JAW'] = JAW
                    self.PLAN['MLC'] = MLC
                    np.save(self.NEW_DATA_PATH + file_nam + '_Plan.npy',PLAN)

            CT = np.array(CT_)
            CT[CT == -2000] = 0

            if slope != 1:
                CT = slope * CT.astype(np.float64)
                CT = img.astype(np.int16)
            CT1 = CT + np.int16(intercept)
            print('The CT array shape: {}'.format(CT1.shape))
            np.save(self.NEW_DATA_PATH + file_nam + '_CT.npy',CT1)


    def Fluence_Map(self):
        '''
           Merge all the segment in one fluence map
        '''



