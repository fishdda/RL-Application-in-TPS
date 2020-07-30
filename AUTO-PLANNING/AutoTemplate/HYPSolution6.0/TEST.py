
from Extract_DVH_Dose import DICOM_DVH

path = 'C:/GitFolder/RL-Application-in-TPS/AUTO-PLANNING/AutoTemplateTuning/projects/dose prediction/DATA'
DVH = DICOM_DVH(path)
DOSE,STRT = DVH.Extrac_DOSE_STRT()
DVH_DATA_ = DVH.Extrac_DVH()
print(len(DVH_DATA_))