# Description: This file contains custom functions used in the main program file (trade_api.py).


# import Libraries
import numpy as np
import pandas as pd
import sys
import os
import requests as req
import re
import pyxlsb
from datetime import datetime, timedelta

# CUSTOM FUNCTIONS
# ==================================================================
# Custom Functions: update_commodity_wizard()
# ==================================================================
def update_commodity_wizard():
    """
    Checks the local commodity translation wizard file for updates 
    and downloads the latest version if necessary.
    """ 
    # Define the URL and local save path for the commodity wizard file
    dataweb_url = 'https://www.usitc.gov/documents/dataweb/commodity_translation_wizard.xlsb'
    codes_save_path = '../resources/commodity_translation_wizard.xlsb'

    # Ensure the directory exists
    os.makedirs(os.path.dirname(codes_save_path), exist_ok=True)

    # Check if the file exists and the last update was more than a month ago
    if os.path.exists(codes_save_path):
        last_modified = datetime.fromtimestamp(os.path.getmtime(codes_save_path))
        if datetime.now() - last_modified < timedelta(days=30):
            return
        else:
            print("It has been more than a month since the local HS Code files were updated. An update will be performed now.")
            print("Once the update is complete, the search will continue.")

    # Download the file
    try:
        response = req.get(dataweb_url, allow_redirects=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(codes_save_path, 'wb') as file:
            file.write(response.content)
        print(f"File has been downloaded and saved to {codes_save_path}")
    except req.RequestException as e:
        print(f"An error occurred: {e}")
        return  # Exit if the download fails

    # Extract and save sheets to CSV, ensuring leading zeros are preserved
    try:
        with pd.ExcelFile(codes_save_path, engine='pyxlsb') as xls:
            for sheet_name, output_filename in [('Import Concordance', 'import_codes.csv'),
                                                ('Export Concordance', 'export_codes.csv')]:
                # Read the Excel file with specific dtype for codes as strings to preserve leading zeros
                df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)
                # Save the DataFrame to a CSV file
                df.to_csv(f'../resources/{output_filename}', index=False)
                print(f"{sheet_name} has been saved to {output_filename}")
    except Exception as e:
        print(f"An error occurred while processing the Excel file: {e}")


# ==================================================================
# Custom Functions: prompt_yes_no()
# ==================================================================
def prompt_yes_no(message):
    """Prompt for a Yes/No response and return it.
    
    Parameters:
    - message (str): The message to display to the user.
    
    Returns:
    - bool: True if the response is 'Yes', False if the response is 'No'.
    """
    response = input(message).strip().lower()
    while response not in ["y", "yes", "n", "no"]:
        response = input("Invalid response. Please enter 'Yes' or 'No': ").strip().lower()
    return response.startswith('y')


# ==================================================================
# Custom Function: get_user_input()
# ==================================================================
def get_user_input(prompt, valid_responses):
    """Ask the user a question and return the response, ensuring it is within the valid responses.
    
    Parameters:
    - prompt (str): The question to ask the user.
    - valid_responses (list): A list of valid responses.

    Returns:
    - str: The user's response.
    """
    response = input(prompt).strip().lower()
    while response not in valid_responses:
        response = input(f"Invalid response. Please enter one of the following: {', '.join(valid_responses)}: ").strip().lower()
    return response


# ==================================================================
# Custom Function: validate_api_key()
# ==================================================================
def validate_api_key(key):
    """Validate the API key to ensure it is exactly 40 characters long or None.
    
    Parameters:
    - key (str): The API key to validate.

    Returns:
    - bool: True if the key is valid, False otherwise.
    """
    return len(key) == 40 or key == None


#==================================================================
# Custom Function: get_key()
#==================================================================
def get_key():
    """
    Prompts the user to enter an API key if they have one.

    Returns:
    - str: The API key entered by the user, or None if the user chooses to proceed without an API key.
    """
    key = None
    have_key = prompt_yes_no("Do you have an API key? (Yes/No): ") 

    if not have_key:
        print("To enhance your experience and increase your daily API call limit, an API Key is recommended.", "\n")
        print("You can obtain a 40-character API Key by registering at https://api.census.gov/data/key_signup.html.", "\n")
        
        proceed = prompt_yes_no("Would you like to proceed without an API key? (Yes/No): ")
        if not proceed:
            quit = prompt_yes_no("Would you like to quit the program? (Yes/No): ")
            if not quit:
                key = input("Please enter your API key or leave blank to proceed without an API key: ")
                while not validate_api_key(key):
                    if key == "":
                        key = None
                        break
                    else:
                        key = input("Invalid API key. Please enter a valid 40-character API key or leave blank to proceed without an API key: ")
            else:
                print("Thank you for using the US Census International Trade API program. Goodbye!")
                sys.exit()
    else:
        key = input("Please enter your API key or leave blank to proceed without an API key: ")
        while not validate_api_key(key):
            if key == "":
                key = None
                break
            else:
                key = input("Invalid API key. Please enter a valid 40-character API key or leave blank to proceed without an API key: ")
    if key:
        print("Your API key has been accepted. Proceeding with data retrieval...")
    else:
        print("Continuing without an API key. Note that you may be limited to 500 API calls per day.")
    return key


# ==================================================================
# Custom Function: get_imp_exp()
# ==================================================================
def get_imp_exp():
    """
    Ask the user for the trade data type they are interested in.

    Returns:
    - str: The trade data type ('imports' or 'exports').
    """
    t_type = input("Would you like to retrieve import or export data? (Import/Export): ").lower()
    
    while t_type not in ["i","imp", "imports", "import", "e", "exp", "exports", "export"]:
        t_type = input("Invalid entry. Please enter either 'import' or 'export': ").lower()
    if t_type in ["i","imp", "imports", "import"]:
        t_type = "imports"
    else:
        t_type = "exports"
    return t_type



# ==================================================================
# Custom Function: get_endpoint()
# ==================================================================
def get_endpoint():
    """
    Ask the user for the API endpoint they would like to use.

    Returns:
    - str: The selected API endpoint ('hs', 'port', or 'state').
    """
    endpoint_prompt = "Would you like to pull the data from the HS, port or state api endpoint? (hs/port/state): "
    endpoint = get_user_input(endpoint_prompt, ['h','hs', 'code', 'hs code', 'port', 'ports', 'p', 'state', 's', 'st'])
    if endpoint in ['h','hs', 'code', 'hs code']:
        endpoint = 'hs'
    elif endpoint in ['p', 'port', 'ports']:
        endpoint = 'port'
    else:
        endpoint = 'state'
    return endpoint


# ==================================================================
# Custom Function: determine_trade_type()
# ==================================================================
def determine_trade_type(imp_exp, endpoint):
    """
    Determines the trade type based on the input parameters.

    Parameters:
    - imp_exp (str): The type of data to fetch ('exports' or 'imports').
    - endpoint (str): The type of data to fetch ('hs', 'port', or 'state').

    Returns:
    - str: The trade type based on the input parameters.
    """
    if imp_exp == 'imports' and endpoint == 'hs':
        return 'imp_hs'
    elif imp_exp == 'imports' and endpoint == 'port':
        return 'imp_port'
    elif imp_exp == 'exports' and endpoint == 'hs':
        return 'exp_hs'
    elif imp_exp == 'exports' and endpoint == 'port':
        return 'exp_port'
    elif imp_exp == 'imports' and endpoint == 'state':
        return 'imp_st'
    else:
        return 'exp_st'
    
    
    # ==================================================================
# Custom Function: determine_base_url()
# ==================================================================
def determine_base_url(imp_exp, endpoint):
    """
    Determines the base URL for the API request based on the trade type and endpoint.

    Parameters:
    - imp_exp (str): The type of trade data to fetch ('exports' or 'imports').
    - endpoint (str): The type of data to fetch ('hs', 'port', or 'state').

    Returns:
    - str: The base URL for the API request.
    """ 
    # Determine the base URL for imports data with Harmonized System codes
    if imp_exp == 'imports' and endpoint == 'hs':
        return 'https://api.census.gov/data/timeseries/intltrade/imports/hs'
    # Determine the base URL for imports data with port information
    elif imp_exp == 'imports' and endpoint == 'port':
        return 'https://api.census.gov/data/timeseries/intltrade/imports/porths'
    # Determine the base URL for exports data with Harmonized System codes
    elif imp_exp == 'exports' and endpoint == 'hs':
        return 'https://api.census.gov/data/timeseries/intltrade/exports/hs'
    # Determine the base URL for exports data with port information
    elif imp_exp == 'exports' and endpoint == 'port':
        return 'https://api.census.gov/data/timeseries/intltrade/exports/porths' 
    # Determine the base URL for imports data with state information
    elif imp_exp == 'imports' and endpoint == 'state':
        return 'https://api.census.gov/data/timeseries/intltrade/imports/statehs'
    # Default to exports data with state information if none of the above conditions are met
    else:
        return 'https://api.census.gov/data/timeseries/intltrade/exports/statehs'
    

# ==================================================================
# Custom Function: determine_base_params()
# ==================================================================
def determine_base_params(trade_type):
    """
    Determines the base parameters for the API request based on the trade type.

    Parameters:
    - trade_type (str): The type of trade data to fetch.

    Returns:
    - dict: A dictionary of base parameters for the API request.
    """
    if trade_type == 'imp_hs':
        return {
            'get': 'I_COMMODITY,I_COMMODITY_LDESC,CTY_CODE,CTY_NAME,DISTRICT,DIST_NAME,UNIT_QY1,UNIT_QY2,GEN_VAL_YR,GEN_QY1_YR,GEN_QY1_YR_FLAG,GEN_QY2_YR,GEN_QY2_YR_FLAG,GEN_CHA_YR,GEN_CIF_YR,CC_YR,RP,CAL_DUT_YR,DUT_VAL_YR,CNT_CHA_YR,CNT_VAL_YR,CNT_WGT_YR,VES_WGT_YR,VES_VAL_YR,VES_CHA_YR,AIR_WGT_YR,AIR_VAL_YR,AIR_CHA_YR',
            'SUMMARY_LVL': 'DET'
            }
    elif trade_type == 'imp_port':
        return {
            'get': 'I_COMMODITY,I_COMMODITY_LDESC,PORT,PORT_NAME,CTY_CODE,CTY_NAME,GEN_VAL_YR,CNT_VAL_YR,CNT_WGT_YR,VES_VAL_YR,VES_WGT_YR,AIR_VAL_YR,AIR_WGT_YR',
            'SUMMARY_LVL': 'DET',
            } 
    elif trade_type == 'exp_hs':
        return {
            'get': 'E_COMMODITY,E_COMMODITY_LDESC,DF,CTY_CODE,CTY_NAME,DISTRICT,DIST_NAME,UNIT_QY1,UNIT_QY2,ALL_VAL_YR,QTY_1_YR,QTY_1_YR_FLAG,QTY_2_YR,QTY_2_YR_FLAG,CNT_VAL_YR,CNT_WGT_YR,CC_YR,AIR_VAL_YR,AIR_WGT_YR,VES_VAL_YR,VES_WGT_YR',
            'SUMMARY_LVL': 'DET',
            }
    elif trade_type == 'exp_port':
        return {
            'get': 'E_COMMODITY,E_COMMODITY_LDESC,PORT,PORT_NAME,CTY_CODE,CTY_NAME,ALL_VAL_YR,CNT_VAL_YR,CNT_WGT_YR,VES_VAL_YR,VES_WGT_YR,AIR_VAL_YR,AIR_WGT_YR',
            'SUMMARY_LVL': 'DET'
            }
    elif trade_type == 'imp_st':
        return {
            'get': 'I_COMMODITY,I_COMMODITY_LDESC,STATE,CTY_NAME,CTY_CODE,GEN_VAL_YR,VES_VAL_YR,VES_WGT_YR,CNT_VAL_YR,CNT_WGT_YR,AIR_VAL_YR,AIR_WGT_YR',
            'SUMMARY_LVL': 'DET',
        }
    else:
        return {
            'get': 'E_COMMODITY,E_COMMODITY_LDESC,STATE,CTY_NAME,CTY_CODE,ALL_VAL_YR,VES_VAL_YR,VES_WGT_YR,CNT_VAL_YR,CNT_WGT_YR,AIR_VAL_YR,AIR_WGT_YR',
            'SUMMARY_LVL': 'DET',
        }


# ==================================================================
# Custom Function: get_country_code()
# ==================================================================
def get_country_code(country):
    """
    Search the local country code file for all matches to the list of country names.
    
    Parameters:
    - country (str): A list of the names of the countries to search for.
    
    Returns:
    - str: A list of the country codes if a match is found, or None if no match is found.
    
    """
    country_code = []
    
    try: 
        # load the csb file
        country_df = pd.read_csv('../resources/country.csv', dtype=str)
        country_list = [ctry.strip() for ctry in country.split(',')]
        # Loop through the list of countries
        for country in country_list:
            matches = country_df[country_df['Name'].str.contains(country, case=False, na=False)]
            
            if not matches.empty:
                for _, row in matches.iterrows():
                    print(row['Name'], row['Code'])
                    country_code.append(row['Code'])
            else:
                print(f"No matches found for '{country}'")
                country_code = get_country_code(country)
                return country_code

        
        use = input("""If you would like to use all the codes listed above, press Enter. 
                    Otherwise, enter each desired code separated by a comma. """)
        if use != '':
            country_code = use.split(',')
            # remove any whitespace
            country_code = [code.strip() for code in country_code]
            for code in country_code:
                if code not in country_df['Code'].values:
                    print("One or more of the country codes entered is invalid. Please try again.")
                    country_code = get_country_code(country)
        
        print(f"Data for the following countries will be requested using the country codes: {country_code}")

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return country_code
    


# ==================================================================
# Custom Function: get_dist_code()
# ==================================================================
def get_dist_code(district):
    """
    Search the local district code file for a match to the input district name.

    Parameters:
    - district (str): The name of the district to search for.

    Returns:
    - str: The district code if a match is found, or None if no match is found.
    """
    district_code = []
    try: 
        # load the csb file
        district_df = pd.read_csv('../resources/district_port.csv', dtype=str)
        district_list = [dist.strip() for dist in district.split(',')]
        # Loop through the list of districts and filter the dataframe for matches
        for district in district_list:
            matches = district_df[district_df['Name'].str.contains(district, case=False, na=False)]
            
            if not matches.empty:
                for _, row in matches.iterrows():
                    print(row['Name'], row['District'])
                    district_code.append(row['District']) 
            else:
                print(f"No matches found for '{district}'")
                district_code = get_dist_code(district)
                return district_code                            
                
        
        use = input("""If you would like to use all the codes listed above, press Enter. 
                    Otherwise, enter each desired code separated by a comma. """)
        if use != '':
            district_code = use.split(',')
            # remove any whitespace
            district_code = [code.strip() for code in district_code]
            for code in district_code:
                if code not in district_df['District'].values:
                    print("One or more of the district codes entered is invalid. Please try again.")
                    district_code = get_dist_code(district)
                    
        else:
            # keep only the unique values
            district_code = list(set(district_code))
        
        print(f"Data for the desired district(s) will be retrieved using the code(s):{district_code}")                 

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return district_code



# ==================================================================
# Custom Function: get_port_code()
# ==================================================================
def get_port_code(port):
    """
    Search the local port code file for a match to the input port name.

    Parameters:
    - port (str): The name of the port to search for.

    Returns:
    - str: The port code if a match is found, or None if no match is found.
    """
    port_code = []
    
    try: 
        # load the csb file
        port_df = pd.read_csv('../resources/district_port.csv', dtype=str)
        port_list = [prt.strip() for prt in port.split(',')]
        # Loop through the list of ports
        for port in port_list:
            matches = port_df[port_df['Name'].str.contains(port, case=False, na=False)]
            
            if not matches.empty:
                for _, row in matches.iterrows():
                    print(row['Name'], row['Port'])
                    port_code.append(row['Port'])
            else:
                print(f"No matches found for '{port}'")
                port_code = get_port_code(port)
                return port_code
        
        use = input("""If you would like to use all the codes listed above, press Enter. 
                    Otherwise, enter each desired code separated by a comma. """)
        if use != '':
            port_code = use.split(',')
            # remove any whitespace
            port_code = [code.strip() for code in port_code]
            for code in port_code:
                if code not in port_df['Port'].values:
                    print("One or more of the district codes entered is invalid. Please try again.")
                    port_code = get_port_code(port)
                    
        else:
            # keep only the unique values
            port_code = list(set(port_code))
        
        print(f"Data for the desired port(s) will be retrieved using the code(s):{port_code}")                 

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return port_code


# ==================================================================
# Custom Function: validate_code_format()
# ==================================================================
def validate_code_format(code_list, endpoint):
    """Validate the format of each HS code in the list, 
    allowing wildcard '*' after 2, 4, or 6 digit codes."""
    
    hs_pattern = re.compile(r'^(\d{2}|\d{4}|\d{6})\*?$|\d{10}$')
    port_pattern = re.compile(r'^(\d{2}|\d{4})\*?$|\d{6}')
    
    # validate the code format based on the endpoint
    if endpoint == 'hs':
        return all(hs_pattern.match(code) for code in code_list)
    else:
        return all(port_pattern.match(code) for code in code_list) 

#==================================================================
# Custom Function: commodity_selection_codes()
#==================================================================
def commodity_selection_codes(commodity, endpoint, trade_type, imp_exp):
    """
    Determine the HS codes for the commodity based on user input.

    Parameters:
    - commodity (str): The name of the commodity to search for.
    - endpoint (str): The endpoint for the API request ('hs' or 'port').
    - trade_type (str): The type of trade data to fetch ('exports' or 'imports').
    - imp_exp (str): The type of data to fetch ('exports' or 'imports').

    Returns:
    - list: A list of HS codes for the commodity.    
    """
    code_list = None
    hs_codes = prompt_yes_no("Do you have the HS codes for your desired commodity? (Yes/No): ")
    if hs_codes:
        code_list = HS_codes_input(endpoint)
    else:
        search = prompt_yes_no("Would you like to search the local files for HS codes related to your commodity? (Yes/No): ")
        if search:
            code_list = commodity_codes_search(commodity, imp_exp, endpoint)
        else:
            print("You may look up your desired import codes at https://dataweb.usitc.gov/tariff/database")
            print("and the export codes at https://uscensus.prod.3ceonline.com/", "\n")
            hs_codes = get_user_input("Would you like to enter the HS codes now? (Yes/No): ", ['y', 'yes', 'n', 'no'])
            if hs_codes in ['y', 'yes']:
                code_list = HS_codes_input(endpoint, trade_type, commodity, imp_exp)
            else:
                quit = get_user_input("Would you like to quit the program or continue without specifying a commodity? (Quit/Continue): ", ['q', 'quit', 'c', 'continue'])
                if quit in ['q', 'quit']:
                    print("Thank you for using the US Census International Trade API program. Goodbye!")
                    sys.exit()
                else:
                    print("Continuing without specifying a commodity.")  
                    code_list = None
                    commodity = None
    return code_list


# ==================================================================
# Custom Function: HS_codes_input()
# ==================================================================
def HS_codes_input(endpoint):
    """
    Ask the user for the HS codes for the commodity they are interested in and validate the format.

    Parameters:
    - endpoint (str): The endpoint for the API request ('hs' or 'port').
    - trade_type (str): The type of trade data to fetch ('exports' or 'imports').
    - commodity (str): The name of the commodity to search for.
    - imp_exp (str): The type of data to fetch ('exports' or 'imports').

    Returns:
    - list: A list of HS codes for the commodity.
    """
    # Ask the user if they have the HS codes for the commodity they are interested in or if they would like to look them up
    code_list = []
    print("You may enter 2, 4, 6 or 10-digit codes if you are pulling data by HS code.")
    print("If you are pulling data by Port you may enter 2, 4 or 6 digit codes.")
    print('''You may use the wild card character '*' to search for all codes that start with the characters you enter.
For example, '85*' will return all HS codes that start with '85'.''', '\n')
    # Ask the user for the HS codes
    code_list = input("Please enter the HS codes for the commodity you are interested in, separated by commas: ").split(",")  
        
    while not validate_code_format(code_list, endpoint):
        print("""Error: One or more HS codes are in an incorrect format. You may enter 2, 4, 6 or 10-digit codes if you are pulling data by HS code. 
    If you are pulling data by Port you may enter 4 or 6 digit codes:. Please ensure all codes are in the correct format.""")
        code_list = input("Please enter the HS codes you want data for separated by commas. or type q to exit the program:  ").split(",")  
        
        if code_list == 'q':
            print("Thank you for using the US Census International Trade API program. Goodbye!")
            sys.exit()
            
    return code_list
    

# ==================================================================
# Custom Function: validate_state()
# ==================================================================
def validate_state(st):
    """
    Validate the input state abbreviation and return the full state name if valid.
    """
    try:
        # Load the CSV file
        state_df = pd.read_csv('../resources/states.csv')
        # Convert the input state abbreviation to uppercase to match the DataFrame's abbreviations
        st = st.upper()

        # Ensure DataFrame 'Abbreviation' column is in uppercase for case-insensitive comparison
        if st not in state_df['Abbreviation'].str.upper().values:
            print('Invalid state')
        else:
            # Fetch the full state name corresponding to the abbreviation
            state = state_df[state_df['Abbreviation'].str.upper() == st]['State'].values[0]
            print(f"Data for {state} will be requested")

    except Exception as e:
        print(f"An error occurred: {e}")
         

# ==================================================================
# Custom Function: valid_hs_lvl()
# ==================================================================
def valid_hs_lvl(endpoint):
    """
    Validate the Harmonized System level based on the endpoint.
    """
    if endpoint == 'hs':
        return ['','2','4','6','10']
    else:
        return ['','2','4','6'] 


# ==================================================================
# Custom Function: commodity_codes_search()
# ==================================================================
def commodity_codes_search(commodity, imp_exp, endpoint, hslvl=10):
    """
    Search local files for HS codes based on a keyword.
    Depending on the user's response and the data type (imports or exports), it searches
    the appropriate CSV file for matching descriptions and returns a list of HS codes.
    
    Parameters:
    - imp_exp (str): The type of data to search for ('imports' or 'exports').
    
    Returns:
    - code_list (list): A list of HS codes that match the search keyword.
    """ 
    code_list = []   
    file_name = '../resources/import_codes.csv' if imp_exp == 'imports' else '../resources/export_codes.csv'
    
    print("You may use 2, 4, 6 or 10-digit codes if you are pulling data by HS code. The default is 10 digits.")
    print("If you are pulling data by Port or State you may use 2, 4 or 6 digit codes. The default is 6 digits.")
    valid_levels = valid_hs_lvl(endpoint)
    hslvl = get_user_input("If you would like to specify the Harmonized System level, please enter it now. Otherwise, press Enter to continue with the default HS level:", valid_levels)
    if hslvl == '':
        hslvl = '10' if endpoint == 'hs' else '6'
    while hslvl not in valid_levels:
        hslvl = get_user_input("Invalid entry. Please enter a valid Harmonized System level: ", valid_levels)

    print(f"Searching local database for HS codes related to", {commodity},"...")
    update_commodity_wizard()
    
    try:
        # read the csv file as all strings to avoid mixed data types
        df = pd.read_csv(file_name, low_memory=False, dtype=str)
        matching_rows = df[df['description_long'].str.contains(commodity, case=False, na=False)]
        unique_rows = matching_rows[['hts10', 'description_long']].drop_duplicates()
                           
        # Convert 'hts10' column to string to ensure .str operations work
        hslvl = int(hslvl)
        unique_rows['hts10'] = unique_rows['hts10'].astype(str) 
        unique_rows['hts10'] = unique_rows['hts10'].str[:hslvl] 
        unique_rows = unique_rows.drop_duplicates(subset='hts10') 
         
        # Ask if user wants to use wildcard, if hslvl is not 10
        if (hslvl != 10 and endpoint == 'hs') | (endpoint != 'hs' and hslvl != 6):
            use_wildcard = prompt_yes_no("Do you want to use the wildcard '*' to retrieve all data that begins with the code level you have chosen? (Yes/No): ")
            if use_wildcard:
                unique_rows['hts10'] = unique_rows['hts10'] + '*'
          
            
        for index, row in unique_rows.iterrows():
            code_list.append(row['hts10'])
            print(f"{row['hts10']}\t{row['description_long']}")
    except FileNotFoundError:
        print(f"Error: The file {file_name} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")  

    use = input("""If you would like to use all the codes listed above, press Enter. 
                If you would like to use specific codes, ender each desired code separated by a comma. """)  
    if use != '':
        code_list = use.split(',')   
            
    return code_list


# ==================================================================
# Custom Function: get_user_defined_parameters()
#==================================================================
def get_user_defined_parameters(endpoint, trade_type, imp_exp):
    # Ask user if they would like to specify HS codes
    commodity = input("If you would like to specify a commodity, please enter the name of the commodity now. Otherwise, press Enter to continue without specifying a commodity:")
    if commodity != '':
        code_list = commodity_selection_codes(commodity, endpoint, trade_type, imp_exp)
    else:
        code_list = None
        commodity = None


    # Ask user if they would like to specify a country
    country = []
    country = input("If you would like to specify a country(s), please enter the name of the country(s) now. Otherwise, press Enter to continue without specifying a country:")
    if country != '':
        cty_codes = get_country_code(country)
    else:
        cty_codes = None


    # Depending on the endpoint, ask the user for additional information
    district = []
    dist_codes = None
    if endpoint == 'hs':
        district = input("If you would like to specify a district(s), please enter the name of the district(s) now. Otherwise, press Enter to continue without specifying a district:")
        if district != '':        
            dist_codes = get_dist_code(district)
        else:
            dist_codes = None


    port = []
    port_codes = None    
    if endpoint == 'port':
        port = input("If you would like to specify a port(s), please enter the name of the port(s) now. Otherwise, press Enter to continue without specifying a port:")
        if port != '':
            port_codes = get_port_code(port)
        else:
            port_codes = None

    state = []
    state = None        
    if endpoint == 'state':
        state = input("If you would like to specify a state(s), please enter the two character state(s) abbreviation now. Otherwise, press Enter to continue without specifying a state:").upper()
        if state != '':
            validate_state(state)
        else:
            state = None
    
    return code_list, cty_codes, dist_codes, port_codes, state, commodity


# ==================================================================
# Custom Function: valid_year_input()
# ==================================================================
def valid_year_input(prompt_message):
    """
    Prompts the user for a year input and validates it to ensure it is a 4-digit number.

    Parameters:
    - prompt_message (str): The message to display when asking the user for input.

    Returns:
    - str: A valid 4-digit year.
    """
    year = input(prompt_message)
    # Validate that the input is a 4-digit year
    while not (year.isdigit() and len(year) == 4):
        year = input("Invalid input. Please enter a 4-digit year: ")
    return year


# ==================================================================
# Custom Function: make_call()
# ==================================================================
def make_call(base_url, parameters, start_year, end_year, imp_exp, code_list, cty_codes, dist_codes, port_codes, state):
    """
    Fetches commodity data (either export or import) for a given list of commodity codes and year range,
    then compiles and returns the data as a pandas DataFrame.

    Parameters:
    - base_url (str): The base URL for the API requests.
    - parameters (dict): A dictionary of parameters for the API requests.
    - code_list (list): A list of commodity codes to fetch data for.
    - start_year (int): The starting year of the range (inclusive).
    - end_year (int): The ending year of the range (inclusive).
    - imp_exp (str): The type of data to fetch ('export' or 'import').

    Returns:
    - pandas.DataFrame: A DataFrame containing the compiled data.
    """

    all_data = pd.DataFrame()
    data = None
    commodity_param = 'E_COMMODITY' if imp_exp == 'exports' else 'I_COMMODITY'

    # Use a placeholder list with a single None value if code_list is None
    if code_list is None:
        code_list = [None]

    for code in code_list:
        if code is not None:
            parameters[commodity_param] = code

        years = range(start_year, end_year)

        # Create a list of parameter sets for each combination
        parameter_sets = [(year, cty, dist, port, st) for year in years
                        for cty in (cty_codes if cty_codes else [None])
                        for dist in (dist_codes if dist_codes else [None])
                        for port in (port_codes if port_codes else [None])
                        for st in (state if state else [None])]

        for year, cty, dist, port, st in parameter_sets:
            temp_params = parameters.copy()
            temp_params['time'] = year
            if cty: temp_params['CTY_CODE'] = cty
            if dist: temp_params['DISTRICT'] = dist
            if port: temp_params['PORT'] = port
            if st: temp_params['STATE'] = st

            response = req.get(base_url, params=temp_params)

            if response.status_code == 200:
                response_data = response.json()
                df = pd.DataFrame(response_data[1:], columns=response_data[0])
                all_data = pd.concat([all_data, df], ignore_index=True)
                all_data.to_csv('temp_data.csv', index=False)
                data = pd.read_csv('temp_data.csv', low_memory=False, dtype=str)
                os.remove('temp_data.csv')
            else:
                print(f"Error: API request for HS code {code} failed with status code: {response.status_code}")
                print(f"API request URL: {response.url}")

    return data
                

# ==================================================================
#Custom Function: clean_data()
# ==================================================================
def clean_data(data, trade_type):
    """
    Cleans the input DataFrame by performing operations specific to the type of data.
    This function combines cleaning steps for different data types into one.

    Parameters:
    - data (pd.DataFrame): The DataFrame to be cleaned.
    - trade_type (str): Specifies the type of data. Possible values are 'imp_hs', 'imp_port', 'exp_hs', 'exp_port'.

    Returns:
    - pd.DataFrame: The cleaned DataFrame.
    """   
    # First save the raw data to a new DataFrame
    raw_data = data.copy()    


    # Drop columns that were only needed for the API call
    data = data.drop(columns=['I_COMMODITY.1', 'E_COMMODITY.1', 'CTY_CODE.1','DISTRICT.1', 'STATE.1', 'COMM_LVL', 'SUMMARY_LVL'], errors='ignore')
    data = data.drop_duplicates()
    data = data.loc[:, ~data.columns.duplicated()]
    pd.set_option('future.no_silent_downcasting', True)
    data = data.replace('-', np.nan)
    data = data.replace('00', np.nan)
    data = data.dropna(axis=1, how='all')
    data = data.loc[:, (data != '0').any(axis=0)]
    data = data.drop_duplicates(subset=data.columns.difference(['time']))
    data['YEAR'] = data['time'].apply(lambda x: x.split('-')[0])
    data['MONTH'] = data['time'].apply(lambda x: x.split('-')[1])
    data = data.drop(columns=['time'], axis=1)
    
    # Clean the data based on the trade type
    if trade_type == 'imp_hs':
        data = data.dropna(subset=['CTY_CODE', 'DISTRICT', 'RP',])
        data = data.drop_duplicates(subset=['I_COMMODITY','CTY_CODE','DISTRICT','YEAR'], keep='last')
        data = data.sort_values(by=['YEAR', 'MONTH', 'I_COMMODITY', 'DIST_NAME', 'CTY_NAME'])
        
    
    elif trade_type == 'imp_port':
        data = data.dropna(subset=['PORT', 'CTY_CODE'])
        data.drop_duplicates(subset=['I_COMMODITY', 'CTY_CODE', 'PORT', 'YEAR'], keep='last', inplace=True)
        data.sort_values(by=['YEAR', 'MONTH', 'I_COMMODITY', 'PORT_NAME', 'CTY_NAME'], inplace=True)
        
    
    elif trade_type == 'exp_hs':
        data = data.dropna(subset=['CTY_CODE', 'DISTRICT', 'DF'])
        data = data.drop_duplicates(subset=['E_COMMODITY','CTY_CODE','DISTRICT','YEAR'], keep='last') 
        data = data.sort_values(by=['YEAR', 'MONTH', 'E_COMMODITY', 'DIST_NAME', 'CTY_NAME'])
        
    elif trade_type == 'exp_port':
        data = data.dropna(subset=['PORT', 'CTY_CODE'])
        data = data.drop_duplicates(subset=['E_COMMODITY','CTY_CODE','PORT','YEAR'], keep='last')
        data = data.sort_values(by=['YEAR', 'MONTH', 'E_COMMODITY', 'PORT_NAME', 'CTY_NAME'])
        
    elif trade_type == 'imp_st':
        data = data.dropna(subset=['CTY_CODE', 'STATE'])
        data = data.drop_duplicates(subset=['I_COMMODITY','CTY_CODE','STATE','YEAR'], keep='last')
        data = data.sort_values(by=['YEAR', 'MONTH', 'I_COMMODITY', 'CTY_NAME'])
        
    else:
        data = data.dropna(subset=['CTY_CODE', 'STATE'])
        data = data.drop_duplicates(subset=['E_COMMODITY','CTY_CODE','STATE','YEAR'], keep='last')
        data = data.sort_values(by=['YEAR', 'MONTH', 'E_COMMODITY', 'CTY_NAME'])
    data = data.reset_index(drop=True)

    # Filter out duplicate rows if the wildcard '*' was used
    if 'I_COMMODITY' in data.columns:
        comm_col = 'I_COMMODITY'
    else:
        comm_col = 'E_COMMODITY'
    longest_code = data[comm_col].str.len().max()
    data = data[data[comm_col].str.len() == longest_code] 
    
    return data, raw_data
   

# ==================================================================
# Custom Function: save_directory()
# ==================================================================
def save_directory():
    """ 
    Prompt the user to enter the directory where they would like to save the data.
    
    Returns:
    - str: The directory path where the user would like to save the data.
    """
    response = prompt_yes_no("Would you like to save the data to a specific directory? (Yes/No):  ")
    if response:
        save_directory = input("Please enter the directory where you would like to save the data:  ")
        return save_directory
    else:
        # default to the saved_data directory in this project
        return 'saved_data'
    

# ==================================================================
# Custom Function: save_data()
# ==================================================================
def save_data(data,raw_data, trade_type, save_dir, commodity=None, cty_name=None, name=None, cleaned=True):
    """ 
    Save the data to a CSV file for each year and by specific trade type and endpoint.
    
    Parameters:
    - data (pd.DataFrame): The DataFrame to be saved.
    - des (str): The description of the data to be saved.
    """
    
    # define the descriptor based on the values of commodity, cty_name, and name
    descriptor = ''
    if commodity:
        descriptor += commodity
    if cty_name:
        if commodity:
            descriptor += '_' + cty_name
        else:
            descriptor += cty_name
    if name:
        if cty_name or commodity:
            descriptor += '_' + name
        else:
            descriptor += name
        
    if cleaned:
        # Save the raw data first split the time column into year and month
        raw_data['YEAR'] = data['time'].apply(lambda x: x.split('-')[0])
        raw_data['MONTH'] = data['time'].apply(lambda x: x.split('-')[1])
        # drop the time column
        raw_data = data.drop(columns=['time'], axis=1)
        
        years = raw_data['YEAR'].unique()
        for year in years:
            data_year = raw_data[data['YEAR'] == year]
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            data_year.to_csv(f'{save_dir}/{descriptor}_{trade_type}_{year}_raw.csv', index=False)
                
        # save the cleaned data to a csv file for each year
        years = data['YEAR'].unique()
        for year in years:
            data_year = data[data['YEAR'] == year]
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            data_year.to_csv(f'{save_dir}/{descriptor}_{trade_type}_{year}_cleaned.csv', index=False)
    else:
        # split the time column into year and month
        data['YEAR'] = data['time'].apply(lambda x: x.split('-')[0])
        data['MONTH'] = data['time'].apply(lambda x: x.split('-')[1])
        # drop the time column
        data = data.drop(columns=['time'], axis=1)
        
        years = data['YEAR'].unique()
        for year in years:
            data_year = data[data['YEAR'] == year]
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            data_year.to_csv(f'{save_dir}/{descriptor}_{trade_type}_{year}_raw.csv', index=False)
    
    print(f"Data saved to {save_dir}/{descriptor}_{trade_type}.csv")
    
