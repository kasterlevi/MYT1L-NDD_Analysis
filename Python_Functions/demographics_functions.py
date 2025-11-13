import pandas as pd
import numpy as np

def get_gene_data_RNAP(RNAP_location): 
    RNAP_Stats = pd.read_csv(RNAP_location,  encoding='utf8')
    status = "Overall Participant Status Check the second option when no more data will be collected for Part 1, whether or not the participant completed all parts. EHR and Genome Connect do not need to be complete.  Note: Before checking 'Data Collection is Finished', go to the 'Check for PHI in text' report, search for this participant, and remove all PHI from open text boxes. Replace with relationship (i.e. 'mom,' 'child') when necessary.   "
    RNAP_Stats['Study ID'] = [str(x) for x in RNAP_Stats['Study ID']]
    RNAP_Stats = RNAP_Stats[RNAP_Stats['Data Access Group'] != 'test'].reset_index(drop=True)
    RNAP_Stats = RNAP_Stats[[RNAP_Stats.loc[x, 'Study ID'].isnumeric() for x in range(len(RNAP_Stats))]].reset_index(drop=True)
    # Have to do special thing to figure out the current status for each individual
    complete_status = np.unique(RNAP_Stats[RNAP_Stats[status].str.contains("Data Collection is Finished").fillna(False)]['Study ID'])
    RNAP_Stats['RNAP Status'] = False
    for i in range(len(RNAP_Stats)):
        if RNAP_Stats.loc[i,'Study ID'] in complete_status:
            RNAP_Stats.loc[i,'RNAP Status'] = True   
    RNAP_Stats = RNAP_Stats.rename(columns = {"Complete?.1": "EConsent", "Gene on list": "Primary Brain Gene", "Primary Brain Gene - not in priority list ": "Primary Brain Gene - not in priority list", "Gene not listed":'Primary Brain Gene - not in either list' })
    RNAP_Stats = RNAP_Stats.reset_index(drop=True)
    
    for i in range(len(RNAP_Stats)):
        if RNAP_Stats.loc[i,'Primary Brain Gene'] == "Primary Brain Gene - not in priority list":
            if RNAP_Stats.loc[i, "Primary Brain Gene - not in priority list"] == 'Gene is not on the list':
                RNAP_Stats.loc[i,'Primary Brain Gene'] = RNAP_Stats.loc[i,'Primary Brain Gene - not in either list']
            else:
                RNAP_Stats.loc[i,'Primary Brain Gene'] = RNAP_Stats.loc[i,"Primary Brain Gene - not in priority list"]
                
            

    brain_column_list = ['Primary Brain Gene',
           'First Additional Gene in which the additional variant is located',
           'Second Additional Gene in which the additional variant is located',
           'Third Additional Gene in which the additional variant is located',
           'Fourth Additional Gene in which the additional variant is located',
           'Fifth Additional Gene in which the additional variant is located']
    
    brain_results_column_list = [" Primary Brain Gene - ACMG Classification on Clinical Genetic Report",
                         "First Additional Gene - ACMG Classification on Clinical Genetic Report",
                         "Second Additional Gene - ACMG Classification on Clinical Genetic Report",
                         "Third Additional Gene - ACMG Classification on Clinical Genetic Report",
                         "Fourth Additional Gene - ACMG Classification on Clinical Genetic Report",
                         "Fifth Additional Gene - ACMG Classification on Clinical Genetic Report"]

    brain_gene_list = []
    for column in brain_column_list:  
        brain_gene_list = list(RNAP_Stats[column]) + brain_gene_list
    
    brain_results_list = []
    for column in brain_results_column_list:  
        brain_results_list = list(RNAP_Stats[column]) + brain_results_list
        
    entity_list = []
    for i in range(len(brain_column_list)):
        entity_list = list(RNAP_Stats["Study ID"]) + entity_list
        
    econsent_list = []
    for i in range(len(brain_column_list)):
        econsent_list = list(RNAP_Stats["EConsent"]) + econsent_list
       
    data = pd.DataFrame({'Brain Gene': brain_gene_list, 'ACMG Classification': brain_results_list, "EntityID": entity_list, "Econsent": econsent_list})
    return data[data['Brain Gene'].notnull()]
        
        
        
        
        
        