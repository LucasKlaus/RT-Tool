import pandas as pd 
import numpy as np
from datetime import date

class RT_Cleaner:
    
    # Instantiate the object
    def __init__(self, df, fluidigm=False):
        self.df = df
        self.fluidigm = fluidigm

    def read_csv(self):
        if self.fluidigm == True:
            self.df = pd.read_csv(f'{self.df}.csv', decimal = '.', delimiter = ',', skiprows=11)
        else:
            self.df = pd.read_csv(f'{self.df}.csv', decimal = '.', delimiter = ',', skiprows=36, encoding='unicode_escape')

    # Returns the cleaned data
    def return_cleaned_data(self, export_file=False, print_data=True):

        # Select and rename the relevant columns
        if self.fluidigm == True:
            self.df = self.df[['Name', 'Name.1', 'Value']]
            self.df.columns = ['Sample', 'Detector', 'Ct']

        # Rename the columns to 'Sample', 'Detector', and 'Ct'
        self.df = self.df[['Sample', 'Detector', 'Ct']]
            
        # Remove columns without any data
        self.df = self.df.loc[:, ~self.df.columns.str.contains('^Unnamed')]
            
        # Filter out rows where 'Sample' is 'H2O'
        self.df = self.df[(self.df['Sample'] != 'H2O') & (self.df['Sample'] != 'H20')]
            
        # Ensure 'Ct' is numeric and replace values greater than 50 with NaN
        self.df['Ct'] = pd.to_numeric(self.df['Ct'], errors='coerce')
            
        self.df.loc[self.df['Ct'] > 50, 'Ct'] = np.nan  
        self.df['Unique_Detector'] = self.df['Detector'] + '_' + (self.df.groupby(['Sample', 'Detector']).cumcount() + 1).astype(str)
        self.df = self.df.pivot(index='Sample', columns='Unique_Detector', values='Ct')

        if export_file == True:
            today = date.today()
            self.df.to_csv(f'{today} Cleaned_Fluidigm_data.csv')
        
        if print_data == True:
            print(self.df.head())

    # Print the header of the cleaned data
    def print_cleaned_data(self, rows=5):
        print(self.df.head(rows))
    
    # This method exports the cleaned data as an excel file with a user defined file name
    def cleaned_data_to_excel(self, excel_name):
        self.df.to_excel(f'{excel_name}.xlsx', sheet_name=f'Cleaned {self.excel_name}')

    # This method exports the cleaned data as a .csv file with a user defined file name
    def cleaned_data_to_csv(self, csv_name):
        self.df.to_csv(f'{csv_name}.csv', decimal=',', float_format='%.2f', sep=';')


class RQ_Calculator:
    
    # Instantiates the object
    def __init__(self, df):
        try:
            self.df = pd.read_csv(f'{df}.csv', delimiter = ',', decimal = '.', index_col=0).round(2)
            print(self.df.head())
        except:
            print('The input ".csv" file contains the wrong format!')

    def calculate_RQ(self, file_name = f'Auswertung Realtime {date.today()}'):
        controls = input('Control samples (separated by space): ')
        controls = controls.split()
        housekeeping = input('What is the name of the housekeeping gene: ')
        housekeeping_matches = [s for s in self.df if housekeeping in s]
        housekeeping_mean = np.round(np.mean(self.df[housekeeping_matches], axis = 1),2)

        # Removes the housekeeping gene from the list of genes
        target_genes = list(self.df.columns)
        for i in housekeeping_matches:
            target_genes.remove(i)

        # Summarizes the names of the genes
        genes = []
        for i in target_genes:
            gene = i.split('_')[0]
            genes.append(gene)
        genes = np.unique(genes)

        # Begin to calculate the RQ and write it into a new Excel file
        with pd.ExcelWriter(f'{file_name}.xlsx', mode='w') as writer:
            for i in genes:
                
                # Identifies all columns which contain the name of the selected target gene
                target_matches = [s for s in target_genes if i in s] # Gets the individual columns from the same gene
                
                # Calculates the mean of the target gene from all individual columns
                target_mean = np.round(np.mean(self.df[target_matches], axis = 1),2) 
                
                # Calculates the delta-Ct values
                delta_Ct = target_mean - housekeeping_mean

                # Calculates the mean of all delta-Ct values from the selected control samples
                control_delta_Ct_mean = np.round(np.mean(delta_Ct[controls]),2)
                
                # Calculates the delta-delta-Ct values
                delta_delta_Ct = delta_Ct-control_delta_Ct_mean

                # Calculates the relative expression (RQ) of the genes
                rq = 2**(-delta_delta_Ct)

                # Calculates the mean RQ values of all control samples
                rq_control_mean = np.round(np.mean(rq[controls]),2)

                # Calculates the normalized RQ values
                rq_norm = rq/rq_control_mean
                
                # Calculates the mean normalized RQ values of all controls; MUST equal 1
                control_rq_norm_mean = np.round(np.mean(rq_norm[controls]), 2)
                
                # Creates the dataframe for the excel sheet and adds a "Type" column for each sample
                data = pd.DataFrame(self.df[housekeeping_matches])
                data.insert(0, 'Type', ['Control' if sample in controls else 'Sample' for sample in self.df.index])

                # Provides the mean Ct values of the housekeeping gene
                data[f'{housekeeping} Mean'] = housekeeping_mean

                # Provides the Ct values of the target gene
                data[target_matches] = self.df[target_matches]

                # Provides the mean Ct values of the target gene
                data[f'{i} Mean'] = target_mean

                # Adds the dCt, Mean (control) dCt, ddCt and RQ
                data['dCt'] = delta_Ct
                data['Mean dCt'] = np.nan
                data.loc[controls[0], 'Mean dCt'] = control_delta_Ct_mean
                data['ddCt'] = delta_delta_Ct
                data['RQ'] = np.round(rq, 2)

                # Adds the mean (control) RQ
                data['Mean RQ'] = np.nan
                data.loc[controls[0], 'Mean RQ'] = rq_control_mean

                # Adds the normalized RQ values for each sample
                data['RQ (norm.)'] = np.round(rq_norm, 2)

                # Adds the mean normalized RQ values of the controls; MUST equal 1
                data['Mean RQ (norm.)'] = np.nan
                data.loc[controls[0], 'Mean RQ (norm.)'] = control_rq_norm_mean

                # Sorts the dataframe, so that the control samples come first
                data = data.sort_values(by='Type', ascending=True)

                # Writes the data frame into an excel sheet named after the target gene
                data.to_excel(writer, sheet_name=i)


    
