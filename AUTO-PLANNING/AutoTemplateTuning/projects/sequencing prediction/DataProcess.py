import numpy as np 
import os
import pydicom 

# deal with CT image data, dose data and MLC & MU intensity
CT_path = 'C:/GitFolder/RL-Application-in-TPS/AUTO-PLANNING/AutoTemplateTuning/projects/dose prediction/DATA'
DATA_path = 'C:/GitFolder/SentDexGeek/DL Keras/MRI'
file_names = os.listdir(CT_path)

for j,file_nam in enumerate(file_names):
    CT_ = []
    print('This is {}th patient'.format(j))
    temp_files = os.listdir(os.path.join(CT_path,file_nam)) # all CT names
    for dcm_nam in temp_files:
        # 
        dcm = pydicom.read_file(os.path.join(CT_path,file_nam,dcm_nam),force=True)
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
            np.save(file_nam+'_Dose.npy',DOSE)

        elif dcm.Modality == 'RTPLAN':

            break

    CT = np.array(CT_)
    CT[CT == -2000] = 0

    if slope != 1:
        CT = slope * CT.astype(np.float64)
        CT = img.astype(np.int16)
    CT1 = CT + np.int16(intercept)
    print('The CT array shape: {}'.format(CT1.shape))
    np.save(file_nam+'_CT.npy',CT1)


## deal with VMAT Sequencer data
# reconstruct each segment with MLC positions extracted and MU listed

