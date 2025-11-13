import pandas as pd
import zipfile 
import numpy as np
import os

def extract_filetype_csvs(folder_name, file_type):
    '''
    This function takes z zipfile bundle of patient information and extracts the information for the specified file type. The resulting csvs of the given file type are saved in a dictionary that maps them to patients. 
    
    Inputs: 
        zip_files: A list of entity bundle zipflies downloaded from CIELO
        file_type: The EHR file type we want to obtain
    Output: 
        dictionary connecting participant IDs to their specific_file CSVs
    
    List of File Types: Diagnoses, Encounters, Labs, Medication Orders, Medication Administration, Vitals, Procedures, Imaging
    '''
    dictionary = {}
    
    delete_later_list = []
    
    # Get list of the ZipFiles
    zip_files = os.listdir(folder_name)
    # Iterate through each zip_file
    for zip_file in zip_files:
        with zipfile.ZipFile(folder_name + "/" + zip_file) as z:
            list_files = z.namelist()
            # Get the name of the summary file
            summary_file_name = [name for name in list_files if "File_details_summary" in name][0]
            # Return only file names for clinical notes
            note_csv_names = get_notes_files(summary_file_name, z, file_type)
            # Iterate through the note_csvs and add them to the dictionary
            for note_csv in note_csv_names:
                # with z.open(note_csv + (".csv" if not note_csv.endswith(".csv") else "")) as f:                    
                if "pdf" not in note_csv:
                    with z.open(note_csv + (".csv" if not (note_csv.endswith(".xlsx") or note_csv.endswith(".csv")) else "")) as f:
                        # Load csv and save to dictionary
                        if ".xlsx" in note_csv:
                            data = pd.read_excel(f)
                        else:
                            data = pd.read_csv(f, low_memory=False)                                     
                        delete_later_list.append(note_csv.split("/")[0])
                        data.rename(columns = {"ParticipantID":"PARTICIPANTID"}, inplace = True)
                        dictionary[note_csv.split("/")[0]] = data
                    
#                     # Load csv and save to dictionary
#                     data = pd.read_csv(f, low_memory=False)
#                     delete_later_list.append(note_csv.split("/")[0])
#                     dictionary[note_csv.split("/")[0]] = data
    return dictionary

def get_notes_files(summary_file_name, z, file_type):
    '''
    This function takes in the name of the summary_file from the zip, and returns the names of the files that contain 
    the specified type of note
    
    Input:
        summary_file_name: name of the summary file in the current zipfile as a string
        z: current zipfile object (that summary_file_name belongs to)
        file_type: The EHR file type we want to obtain
    Output:
        list of file names in the current zipfile object
    
    '''
    # Open Summary File
    with z.open(summary_file_name) as f:
        summary_df = pd.read_csv(f, low_memory=False)
        # Find list of clinical note names and put in correct format
        # print(np.unique(summary_df.loc[summary_df['FileTags'].notnull(),"FileTags"]))
        summary_df = summary_df.loc[summary_df["FileTags"] == file_type,['EntityID', "FileName", "FileCategory"]].astype(str)
    return list(summary_df['EntityID'] + "/" + summary_df['FileCategory'] + "/" + summary_df.index.astype(str) + "_" +  summary_df['FileName'])

def concat_single_csv_diagnoses(diagnoses_dict):
    """
    This function takes in the the dictionary containing the diagnosis CSV files and resturns the csvs concatonated together. 
    Inputs:
        diagnosis_dict: Dictionary mapping patients to diagnosis CSV files 
    Output:
        concatenated CSV files
    """
    column_list = []
    for key, value in diagnoses_dict.items():
        column_list.append(value)
    
    diagnoses_df = pd.concat(column_list).reset_index(drop=True)
    diagnoses_df = diagnoses_df[diagnoses_df['ICD10_CODE'].notnull()]
    diagnoses_df['ICD10_CODE'] = diagnoses_df['ICD10_CODE'].astype(str)
    # Remove rows where ICD10_CODE starts with a number (just a little data cleaning)
    diagnoses_df = diagnoses_df[~diagnoses_df["ICD10_CODE"].str.contains(r"^\d")]
    diagnoses_df = diagnoses_df[diagnoses_df['PARTICIPANTID'].notnull()]
    diagnoses_df['PARTICIPANTID'] = diagnoses_df['PARTICIPANTID'].astype(int).astype(str)
    return diagnoses_df

def concat_single_csv_any(file_dict):
    """
    This function takes in the the dictionary containing the CSV files and returns the csvs concatonated together. 
    Inputs:
        diagnosis_dict: Dictionary mapping patients to the specified CSV file type
    Output:
        concatenated CSV files
    """
    column_list = []
    for key, value in file_dict.items():
        curr_df = value
        value.columns = value.columns.str.lower().str.replace(' ', '').str.replace('.','').str.replace('_', '').str.replace("entityid","participantid")
        column_list.append(value)
    return pd.concat(column_list).reset_index(drop=True)