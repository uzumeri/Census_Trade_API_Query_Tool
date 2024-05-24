# ## US Census International Trade API Retrieval and Processing Program 
# This program is designed to interact with a Census API, allowing for the retrieval of specific datasets based on user input. 
# It's structured to guide users through a series of questions to pinpoint the exact data they need, including determining the correct 
# API endpoint and the parameters that define their query. 

# ### Features:
# - **Dynamic Endpoint Selection:** The program prompts the user with questions to accurately determine the most relevant API endpoint for their data needs.
# - **Data Cleaning Option:** Before saving the data, users have the choice to perform data cleaning operations, allowing for the removal of irrelevant or 
#     corrupt data, ensuring the dataset's quality.
# - **CSV Export:** The final dataset can be saved directly to a CSV file. Users can choose between saving the raw data directly from the API or the 
#     cleaned data after processing.
# 
# ### Workflow: 
# 1. **User Interaction:** The program starts by asking the user a series of questions. These questions are designed to gather information about the 
#      type of data the user is interested in. This step is crucial for determining the appropriate API endpoint and the necessary parameters for the query.
# 2. **API Call:** Based on the user's input, the program constructs a query and makes a call to the specified Census API endpoint. This step involves 
#      fetching the data from the Census database that matches the user's specified criteria.
# 3. **Data Processing:** Once the data is retrieved, the user is presented with the option to clean the data. This step involves filtering out 
#      unnecessary or irrelevant information and correcting any discrepancies, ensuring the dataset's accuracy and relevance.
# 4. **Export to CSV:** The final step involves exporting the processed data to a CSV file. The user can choose to save the raw data as it was 
#      retrieved from the API or the cleaned data. The CSV file is then stored in a specified location, making it accessible for further analysis or reporting.
# 
# ### Usage:
# 
# - Ensure you have the necessary API key and permissions to access the Census data.
# - Run the program and follow the on-screen prompts to input your data requirements.
# - Choose between cleaning the data or saving the raw data directly.
#  
# ##### Additional information regarding the US Census API at https://www.census.gov/data/developers/data-sets/international-trade.html 
# AND
# ##### Guide to International Trade Statistics https://www.census.gov/foreign-trade/guide/index.html
#
# ## Note you may need to have an API key.
# 
# #### Request key at https://api.census.gov/data/key_signup.html

######  START OF PROGRAM  ######

# import Libraries
import numpy as np
import pandas as pd
import sys
import requests as req
import os
import trade_api_functions as taf


def main():
    # ## Request and store API Key
    print("Welcome to the US Census International Trade API program! This tool allows you to access and save international trade data.", "\n")

    # Initialize the API key
    key = taf.get_key()


    # Ask the user for the trade data type they are interested in.
    imp_exp = taf.get_imp_exp()

    # Ask the user how they want to pull the data.
    endpoint = taf.get_endpoint()
        
    trade_type = taf.determine_trade_type(imp_exp, endpoint)

    # Determine the base URL for the API requests
    base_url = taf.determine_base_url(imp_exp, endpoint)

    # Determine the base parameters for the API requests
    parameters = taf.determine_base_params(trade_type)

    # Determine if there is a key and add it to the parameters
    if key:
        parameters['key'] = key


    # ## Additional User Specified Parameters
    code_list, cty_codes, dist_codes, port_codes, state, commodity = taf.get_user_defined_parameters(endpoint, trade_type, imp_exp)


    # ## Determine time frame

    print("What time period would you like to pull data for?")
    start_year = int(taf.valid_year_input("Enter the 4 digit year you would like to start from (e.g. 2010): "))
    end_year = int(taf.valid_year_input("Enter the 4 digit year you would like to end at (e.g. 2020): ")) + 1

    # Ensure start_year is not greater than end_year
    while int(start_year) > int(end_year):
        print("The start year cannot be greater than the end year. Please enter the years again.")
        start_year = taf.valid_year_input("Enter the 4 digit year you would like to start from (e.g. 2010): ")
        end_year = taf.valid_year_input("Enter the 4 digit year you would like to end at (e.g. 2020): ")


    # Make the API call to fetch the data
    print("""
          "Some data users may experience performance issues while querying. Using a single query to pull data on all 
          countries and or all commodities will result in error. In general, the API can handle a large number of smaller 
          data calls better than it can handle one large data call. We suggest you limit the size of the query by breaking 
          up the call and combining the output. One way to do this is by using a wild card “*”."
          _International Trade Data API User Guide_
          """)
    data = taf.make_call(base_url, parameters, start_year, end_year, imp_exp, code_list, cty_codes, dist_codes, port_codes, state) 

    # Check if the data is empty
    if data is None:
        print("No data was found for the specified parameters. Please review the error message above and try again.")
    else:
        print("Data was successfully retrieved!")


    # create a directory to save the data
    save_dir = taf.save_directory()

    # Ask the user if they would like to clean the data before saving it
    cleaned = taf.prompt_yes_no("Would you like to clean the data before saving to a csv file? (Yes/No): ")
    if cleaned:
        cleaned_data = taf.clean_data(data, trade_type)
        taf.save_data(cleaned_data, trade_type, save_dir, commodity, cleaned=True)
    else:
        print("Data will be saved as is.")
        taf.save_data(data, trade_type, save_dir, commodity, cleaned=False)

main()