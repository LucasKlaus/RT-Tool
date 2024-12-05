# RT-Tool
A program which can read the raw BioMark Fluidigm Gene expression or Applied Biosystem 7500 Realtime PCR System raw ".csv", cleans them and calculates the relative gene expression using the ddCt method.

## How to Use the RT_Cleaner Tool
1. First, import the RT_Cleaner object from the RT_Tool library
2. Instantiate an RT_cleaner object and run the *read_csv* method while passing the name of the ".csv"-file containing the RAW gene expression data. (Optionally: Set "fluidigm = **True**" if the raw data contains gene expression data from the BioMark Fluidigm Chip).
3. Next, run the *return_cleaned_data* method in order to return the cleaned gene expression data. Set *export_file* to **True** if you want to export the cleaned data as a ".csv" file. By default, the cleaned data is printed to the terminal (optionally turn this off by setting *print_data* to **False**).
4. (Optional) You can return the cleaned data as a ".csv" file using the *cleaned_data_to_excel* or the *cleaned_data_to_csv* function. In both cases, you can add a name for the file. 

## How to Use the RQ_Calculator Tool
1. First, import the RQ_Calculator object from the RT_Tool library
2. Instantiate a RQ_calculator object by passing the name (and directory) of a clean(ed) ".csv" file. If the file is not cleaned, the program wont run.
3. Run the *calculate_RQ* method and pass the names of the control samples, as well as the name of the housekeeping gene. (Optionally) Pass a name for the exported file after the RQ calculation
4. The program will return an excel file containing all calculations for the quantification of relative gene expression using the *Delta-Delta-Ct* method, with each sheet displaying the calculations for the respective target gene