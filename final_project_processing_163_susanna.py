'''
Matthew Friedrich
Susanna Liu
CSE 163 Section AG

This file contains the functions get_filtered_data,
get_q1_df, get_q2_map_df, get_q3_xy_df, and get_q3_map_df.
Each of these functions are used to process data in
the COVID-19 dataset acquired from Our World in Data.
These functions are used in the file final_project_plotting.py,
with their outputs as parameters to create plots for each
of our research questions.
'''


import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame


def get_filtered_data(file_url):
    '''
    Takes url of COVID-19 CSV file as a parameter.
    Reads url of CSV file into a pandas dataframe.
    Fills N/A values with 0, and filters for only
    relevant columns. Returns pandas dataframe.
    '''
    df = pd.read_csv(file_url).fillna(0)
    df_relevant = df[['iso_code', 'continent', 'location',
                      'date', 'total_cases', 'total_vaccinations',
                      'people_vaccinated', 'people_fully_vaccinated',
                      'new_vaccinations', 'population', 'gdp_per_capita']]
    return(df_relevant)


def get_q1_df(filtered_data):
    '''
    Takes filtered pandas dataframe as a parameter.
    Creates new dataframe with same columns which
    contains the vaccination data for the most recent
    day which each country has data for. Calculates
    percent vaccinated on most recent day and takes
    top 10 countries with highest percent vaccinated.
    Filters original dataframe to contain only those
    countries, but for all days. Calculates percent
    vaccinated for all days for those 10 countries.
    Returns pandas dataframe with percent vaccinated
    for all days for top 10 countries.
    '''
    # remove countries with population under 1 million
    # and where total vaccinations is 0
    df_relevant = filtered_data[filtered_data['population'] >= 1000000]
    df_relevant = df_relevant[df_relevant['total_vaccinations'] != 0]

    # create new data frame to add most recent day to
    max_date_df = pd.DataFrame(columns=df_relevant.columns)
    # duplicate to use later
    adjusted_top_10_df = max_date_df

    # get list of all countries iso codes
    countries = df_relevant['iso_code'].unique()

    # Find most recent day for each country
    # For each country you must check if people vaccinated is zero.
    # Some countries will have some days for people vaccinated but
    # not all, therefore this is a case by case basis.
    for country in countries:
        # one country
        new_country = df_relevant[df_relevant['iso_code'] == country]
        # last row for that country
        max_day = new_country.iloc[[-1]].copy()
        # replace people vaccinated column if missing
        if (max_day['people_vaccinated'] == 0).any():
            max_day['people_vaccinated'] = max_day['total_vaccinations']
        # calculate percent vaccinated
        max_day['percent_vaccinated'] = \
            (max_day['people_vaccinated'] / max_day['population']) * 100
        # add to new data frame
        max_date_df = max_date_df.append(max_day)

    # remove row for world
    max_date_df = max_date_df[max_date_df['location'] != 'World']

    # remove countries where total cases are 0
    max_date_df = max_date_df[max_date_df['total_cases'] != 0]

    # get top 10 sorted by percent vaccinated
    top_10 = max_date_df.sort_values(by='percent_vaccinated',
                                     ascending=False).head(10)
    top_10_countries = top_10['iso_code']

    # get slice of original data frame that contains the top 10 countries
    top_10_df = df_relevant[df_relevant['iso_code'].isin(top_10_countries)]

    # Get top 10 countries with percent vaccinated for all days.
    # For each country you must check if people vaccinated is zero.
    # Some countries will have some days for people vaccinated but
    # not all, therefore it needs to be replaced with total vaccinations.
    for country in top_10_countries:
        # create new country
        new_country = top_10_df[top_10_df['iso_code'] == country].copy()
        # if missing people vaccinated, replace with total vaccinations value
        if (new_country['people_vaccinated'] == 0).any():
            new_country['people_vaccinated'] = \
                new_country['total_vaccinations']
        # calculate percent vaccinated
        new_country['percent_vaccinated'] = \
            new_country['people_vaccinated'] / new_country['population'] * 100
        # add to data frame
        adjusted_top_10_df = adjusted_top_10_df.append(new_country)

    return(adjusted_top_10_df)

#### NEED COMMENTING ####
def get_q2_map_df(filtered_data):
    '''
    Takes a filtered dataset as a parameter. Filters it down
    to contain only relevant data to analysis. New dataset
    is used to calculate each country's percentage of vaccination.
    Percentage calculated takes the number of people that have been
    given one and at least one dose of vaccine. It does not reflect
    the percentage of total vaccinations distributed over population.
    Percentage per country is merged with geometrical data of the
    world and returned.
    '''
    # Filter only for columns needed to plot map
    q2_df = filtered_data[['iso_code',
                           'continent',
                           'location',
                           'date',
                           'people_vaccinated',
                           'total_vaccinations',
                           'population']]

    # Removing days that portray total vaccinations
    # as 0 to prevent illogical data spikes
    # Some countries that have not yet started issuing vaccines will also
    # be removed from this analysis
    q2_df = q2_df[q2_df['total_vaccinations'] != 0]

    # Create blank dataframe to store latest dates that contain relevant data
    latest_data = pd.DataFrame(columns=q2_df.columns)

    # Get a list of all country iso codes
    countries = q2_df['iso_code'].unique()

    for country in countries:
        new_country = q2_df[q2_df['iso_code'] == country]
        # Latest data for that country
        recent_day = new_country.iloc[[-1]].copy()
        # Replace people vaccinated data with total vaccinated if missing
        if (recent_day['people_vaccinated'] == 0).any():
            recent_day['people_vaccinated'] = recent_day['total_vaccinations']
        # Calculate percent vaccinated for country
        recent_day['percent_vaccinated'] = \
            (recent_day['people_vaccinated'] / recent_day['population']) * 100
        # Add data to dataframe
        latest_data = latest_data.append(recent_day)

    # Remove world row
    latest_data = latest_data[latest_data['location'] != 'World']

    # load geopandas built-in variable for country shapes
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Fill in missing iso codes for countries in world data
    world.loc[world['name'] == 'Norway', 'iso_a3'] = 'NOR'
    world.loc[world['name'] == 'France', 'iso_a3'] = 'FRA'
    world.loc[world['name'] == 'N. Cyprus', 'iso_a3'] = 'OWID_NCY'
    world.loc[world['name'] == 'Somaliland', 'iso_a3'] = 'SOM'
    world.loc[world['name'] == 'Kosovo', 'iso_a3'] = 'OWID_KOS'

    # Combining world geopanda dataset with vaccine dataset's latest data
    merged_df = latest_data.merge(world,
                                  left_on='iso_code',
                                  right_on='iso_a3',
                                  how='left')
    merged_df = GeoDataFrame(merged_df)

    return(merged_df)


def get_q3_xy_df(filtered_data):
    '''
    Takes filtered pandas dataframe as a parameter.
    Creates new pandas dataframe with same columns which
    contains the vaccination data for the most recent
    day which each country has data for.
    Returns new pandas dataframe.
    '''
    # remove rows where total vaccinations is 0
    df_3_vacc = filtered_data[filtered_data['total_vaccinations'] != 0]

    # create new dataframe to add rows to
    df_recent_date = pd.DataFrame(columns=df_3_vacc.columns)

    # get list of all country iso codes
    countries_3 = df_3_vacc['iso_code'].unique()

    # Get vaccination percentage for all
    # countries on most recent day.
    # Find most recent day for each country, then
    # calculate percent vaccinated and add to dataframe
    for country in countries_3:
        # one country
        new = df_3_vacc[df_3_vacc['iso_code'] == country]
        # last row for that country
        recent_day = new.iloc[[-1]].copy()
        # replace people vaccinated column if missing
        if (recent_day['people_vaccinated'] == 0).any():
            recent_day['people_vaccinated'] = recent_day['total_vaccinations']
        # calculate percent vaccinated
        recent_day['percent_vaccinated'] = \
            (recent_day['people_vaccinated'] / recent_day['population']) * 100
        # add to dataframe
        df_recent_date = df_recent_date.append(recent_day)

    # remove rows where gdp per capita is 0
    df_recent_date = df_recent_date[df_recent_date['gdp_per_capita'] != 0]

    return(df_recent_date)


def get_q3_map_df(filtered_data):
    '''
    Takes filtered pandas dataframe as a parameter.
    Filters for only country iso code (3 letter identifier)
    and GDP per capita. Loads geopandas built-in dataframe,
    and manually replaces missing iso codes. Manually adds
    iso code and GDP per capita for Turkmenistan. Merges
    dataframes based on country iso code using keys from the
    GDP per capita dataframe. Converts to GeoDataFrame.
    Returns GeoDataFrame.
    '''
    # Plotting GDP Per Capita Choropleth Map
    df_3_gdp = filtered_data[['iso_code', 'gdp_per_capita']]

    # take one row from each country
    # gdp per capita is the same for all rows of a country
    # but taking the max to be sure
    df_3_gdp = df_3_gdp.groupby(by='iso_code').max()
    df_3_gdp.reset_index(inplace=True)

    # load geopandas built-in variable for country shapes
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Manually enter missing iso codes and missing rows to fill in map
    world.iloc[43, 3] = 'FRA'
    world.iloc[21, 3] = 'NOR'
    world.iloc[174, 3] = 'KOS'
    df_3_gdp.iloc[150, 0] = 'KOS'
    tkm_row = pd.DataFrame({'iso_code': ['TKM'],
                            'gdp_per_capita': [6966.64]})
    df_3_gdp = df_3_gdp.append(tkm_row)

    # merge dataframes using iso codes from COVID data frame
    # and convert to geodataframe
    merged_world_df = df_3_gdp.merge(world,
                                     how='left',
                                     left_on='iso_code',
                                     right_on='iso_a3')
    merged_world_df = GeoDataFrame(merged_world_df)

    return(merged_world_df)
