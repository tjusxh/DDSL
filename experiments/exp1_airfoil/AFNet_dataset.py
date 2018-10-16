# Import packages
import numpy as np
import pandas as pd
import os
import csv

import torch
from torch.utils.data import Dataset, DataLoader

# Function for getting normalized data
def getNormalizedData(csv_file):
    return csv_file.replace('.csv', '')+'_normalized.csv'

# Create dataset class
class AirfoilDataset(Dataset):
    def __init__(self, csv_file, shape_dir, set_type, train_size=0.7, test_size=0.2, random_seed=0):
        '''
        Args:
            csv_file (string): Path to csv file with CFD data for each airfoil.
            shape_dir (string): Directory containing airfoil shape files (.npy).
        '''
        
        assert (set_type in ['train', 'test', 'valid'])
        
        orig_csv_file=csv_file
        orig_df=pd.read_csv(orig_csv_file).drop('Unnamed: 0', axis=1)
        
        csv_file=getNormalizedData(csv_file)
        
        # Read csv
        df=pd.read_csv(csv_file).drop('Unnamed: 0', axis=1)
        
        # Set random seed
        np.random.seed(random_seed)

        data_size=len(df)

        idx_arr=np.arange(0,data_size)
        np.random.shuffle(idx_arr)

        num_train=np.round(train_size*data_size).astype('int')
        num_test=np.round(test_size*data_size).astype('int')
        
        idx=0
        if set_type=='train':
            idx=idx_arr[:num_train]
        elif set_type=='test':
            idx=idx_arr[num_train:num_train+num_test]
        elif set_type=='valid':
            idx=idx_arr[num_train+num_test:]
        self.airfoil_df=df.iloc[idx]
        self.orig_df=orig_df.iloc[idx]
        
        self.shape_dir=shape_dir
        
    def __len__(self):
        return len(self.airfoil_df)
    
    def __getitem__(self, idx):    
        # Get CFD info from dataframe
        name=self.airfoil_df['Name'].iloc[idx]
        Re=self.airfoil_df['Re'].iloc[idx]
        Cl=self.airfoil_df['Cl'].iloc[idx]
        Cd=self.airfoil_df['Cd'].iloc[idx]
        
        # Get unnormalized AoA
        orig_aoa=self.orig_df['AoA'].iloc[idx]
        aoa=str(orig_aoa).replace('.', '_')
        aoa='aoa_p_'+aoa
        aoa=aoa.replace('aoa_p_-', 'aoa_n_')
        
        # Get numpy shape file
        af_dir=self.airfoil_df['Directory'].iloc[idx]
        shape_dir=self.shape_dir
        npyfilename=shape_dir+'/'+af_dir+'_'+aoa+'.npy'
        shape=np.load(npyfilename)
        shape=np.stack((np.real(shape), np.imag(shape)), axis=2)
          
        # Create dictionary output
        sample={'name': name,\
                'shape': shape,\
                'Re': Re,\
                'Cl': Cl,\
                'Cd': Cd,\
                'aoa': orig_aoa}
        
        return sample