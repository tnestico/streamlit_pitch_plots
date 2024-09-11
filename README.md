# MLB & AAA Pitch Plots App

## Overview

This application is a data visualization tool that fetches MLB and AAA pitching data for a selected pitcher from the MLB Stats API. It uses Streamlit for the web interface and Polars for data manipulation. The app outputs the pitcher's data into both a plot and table to illustrate and summarize the data.

## Features

- Fetches MLB and AAA pitching data from the MLB Stats API.
- Filters the data based on user inputs.
- Generates and displays plots and tables based on the filtered data.

## Requirements

- Python 3.7+
- Streamlit
- Polars
- Seaborn
- Requests
- st_aggrid

api_scraper.py can be found in this [Repository](https://github.com/tnestico/mlb_scraper)

## Installation

1. Clone the repository:
    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the Streamlit application:
    ```sh
    streamlit run app.py
    ```

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Use the interface to input the required parameters:
    - Select the league (MLB or AAA).
    - Select the pitcher.
    - Select the batter handedness.
    - Select the start and end dates.
    - Select the plot type.

4. Click the "Generate Plot" button to generate and display the plot and table.

## Code Explanation

### Main Components

- **Data Fetching**: The `fetch_data()` function is used to fetch the original data.
- **Data Conversion and Filtering**: The `ploter.df_to_polars()` function converts the fetched data to a Polars DataFrame and filters it based on the user inputs.
- **Plot Generation**: The `ploter.final_plot()` function generates the final plot based on the filtered data.

### Error Handling

- If the filtered DataFrame is empty, the application prompts the user to select different parameters.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
