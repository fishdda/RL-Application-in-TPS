from DataProcess import DATAPROCESS
CT_path = 'C:/GitFolder/RL-Application-in-TPS/AUTO-PLANNING/AutoTemplateTuning/projects/dose prediction/DATA'
DATA_path = 'C:/GitFolder/RL-Application-in-TPS/AUTO-PLANNING/AutoTemplateTuning/projects/sequencing prediction/DATA_/'
X = DATAPROCESS(CT_path,DATA_path)
X.TRANSFER_RAW_DATA()
