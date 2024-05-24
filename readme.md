# Census Trade API Query Tool

## Overview

The Census Trade API Query Tool allows users to retrieve and analyze international trade data from the U.S. Census Bureau. This program is designed to be user-friendly, guiding users through a series of prompts to specify the data they need, including trade type, endpoint, and other parameters.

## Key Features

- **API Key Handling**: Users can choose to enter an API key or proceed without one, with notifications about the limitations of not using a key.
- **Trade Type Selection**: Users can specify whether they want import or export data.
- **Endpoint Selection**: Users can choose to pull data from the HS (Harmonized System), Port, or State endpoints.
- **Commodity Specification**: Users can specify a commodity, with options to enter HS codes directly or search a local directory for matching codes.
- **Country, District, Port, and State Specification**: Users can specify these parameters to refine their data query.

## Functions and Features

1. **API Key Handling**

   - Users are asked if they have an API key. They can enter their key or continue without it, with notifications about the limitations of not using a key.
2. **Trade Type Selection**

   - Users choose between import or export data.
3. **Endpoint Selection**

   - Users select the API endpoint: HS, Port, or State.
4. **Base URL and Parameters**

   - Base URL and parameters are set based on user inputs.
5. **Commodity Specification**

   - Users can specify a commodity.
   - If specified, users can enter HS codes directly or search a local directory.
   - A built-in function updates the local HS code files if needed.
   - Users can specify the HS code level and use wildcards if desired.
6. **Country Specification**

   - Users can specify a country, with the program identifying the correct country code for the API call.
7. **District, Port, and State Specification**

   - Depending on the endpoint, users can specify a district, port, or state, with the program validating these inputs.

## How to Use

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Rene-Jacobs/Census_Trade_API_Query_Tool.git
   ```
2. **Navigate to the Directory**

   ```bash
   cd census-trade-api
   ```
3. **Run the Program**

   ```bash
   python trade_api.py
   ```
4. **Follow the Prompts**

   - Enter your API key if you have one.
   - Specify whether you want import or export data.
   - Select the endpoint: HS, Port, or State.
   - Enter any specific commodities, countries, districts, ports, or states as prompted.
   - Specify the time period for the data.
5. **Data Retrieval and Saving**

   - The program will retrieve the data based on your inputs.
   - Choose whether to clean the data before saving.
   - The data will be saved as CSV files in the specified directory.

## Additional Information

- [US Census International Trade API](https://www.census.gov/data/developers/data-sets/international-trade.html)
- [Guide to International Trade Statistics](https://www.census.gov/foreign-trade/guide/index.html)
- [API Key Signup](https://api.census.gov/data/key_signup.html)

## Note

You may need an API key to enhance your experience and increase your daily API call limit. Obtain your API key by registering at the [API Key Signup](https://api.census.gov/data/key_signup.html) page.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
