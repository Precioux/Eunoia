import os
import pandas as pd

# Directory containing the result files
results_folder = 'results/'

# List to store DataFrames
dataframes = []

# Iterate over all Excel files in the results directory
for file in os.listdir(results_folder):
    if file.endswith('.xlsx'):
        file_path = os.path.join(results_folder, file)
        df = pd.read_excel(file_path, engine='openpyxl')
        dataframes.append(df)

# Concatenate all DataFrames
combined_df = pd.concat(dataframes, ignore_index=True)

# Save the combined DataFrame to a new Excel file
combined_excel_output_path = 'final_results.xlsx'
combined_df.to_excel(combined_excel_output_path, index=False)

print(f'Combined file saved to {combined_excel_output_path}')