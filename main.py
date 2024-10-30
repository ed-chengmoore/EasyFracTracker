# Update to ensure starting franchises consistently add "Thereafter average" to each subsequent period
import os
import pandas as pd

# Define paths for the input and output directories
input_directory = 'input'
output_directory = 'output'

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Load the control file
control_file_path = os.path.join(input_directory, 'new_franchises_control.csv')
control_df = pd.read_csv(control_file_path)

# Dynamically retrieve franchise names from control file by excluding 'Month' column
franchise_names = [col for col in control_df.columns if col != 'Month']

# Iterate over each franchise type listed in the control file
for franchise_name in franchise_names:
    # Load the corresponding franchise data CSV file
    franchise_file_path = os.path.join(input_directory, f"{franchise_name}.csv")
    franchise_df = pd.read_csv(franchise_file_path)
    franchise_df.columns = franchise_df.columns.str.strip()  # Clean column headers
    
    # Extract rows for revenue and cost directly by position
    revenue_row = franchise_df.iloc[1]  # "Monthly Revenue" row at index 1
    expense_row = franchise_df.iloc[2]  # "Monthly Expenses" row at index 2
    
    # Initialize data for aging progression by month
    output_data = []  # To store monthly cash flow results
    monthly_franchise_ages = []  # Track each new franchise's age per month
    
    # Determine the count of starting franchises that are consistently using "Thereafter average"
    starting_franchises = 0
    
    # Process each period in the control file
    for index, row in control_df.iterrows():
        period_label = row['Month']  # Period (e.g., 'Y1M1', 'Y1M2')
        
        # Check if this is the "Starting" row
        if period_label == "Starting":
            # Set the count of starting franchises, which will use "Thereafter average" going forward
            starting_franchises = int(row[franchise_name] if pd.notna(row[franchise_name]) else 0)
            period_inflow = starting_franchises * revenue_row['Thereafter average']
            period_outflow = starting_franchises * expense_row['Thereafter average']
        else:
            # Calculate inflow/outflow for starting franchises for the current period
            period_inflow = starting_franchises * revenue_row['Thereafter average']
            period_outflow = starting_franchises * expense_row['Thereafter average']
            
            # For other rows, add new franchises (starting at age 1 month)
            new_franchises = int(row[franchise_name] if pd.notna(row[franchise_name]) else 0)
            monthly_franchise_ages.extend([1] * new_franchises)
            
            # Calculate total inflow and outflow for newly added franchises this month
            for i in range(len(monthly_franchise_ages)):
                franchise_age = monthly_franchise_ages[i]
                
                # Determine revenue and cost based on aging (up to 9 months, then "Thereafter average")
                if franchise_age <= 9:
                    period_inflow += revenue_row[f'Month {franchise_age}']
                    period_outflow += expense_row[f'Month {franchise_age}']
                else:
                    period_inflow += revenue_row['Thereafter average']
                    period_outflow += expense_row['Thereafter average']
                
                # Increment the age of this franchise for the next period
                monthly_franchise_ages[i] += 1
        
        # Append monthly data to output for this franchise
        output_data.append({
            'Franchise': franchise_name,
            'Period': period_label,
            'Total Cash Inflow': period_inflow,
            'Total Cash Outflow': period_outflow,
            'Net Cash Flow': period_inflow - period_outflow
        })
    
    # Store output data for each franchise in the output directory as separate CSVs
    output_df = pd.DataFrame(output_data)
    franchise_output_path = os.path.join(output_directory, f'{franchise_name}_cashflow_output.csv')
    output_df.to_csv(franchise_output_path, index=False)

print("Separate franchise outputs saved to 'output' directory.")
