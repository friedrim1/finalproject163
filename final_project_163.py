import pandas as pd
import altair as alt
import geopandas as gpd
import matplotlib.pyplot as plt
from geopandas import GeoDataFrame

#### added to processing file ####
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

#### non-plotting part added to processing file ####
def get_q1_plot(filtered_data):

    # remove countries with population under 1 million
    # and where total vaccinations is 0
    df_relevant = filtered_data[filtered_data['population'] >= 1000000]
    df_relevant = df_relevant[df_relevant['total_vaccinations'] != 0]

    # create new data frame to add most recent day to
    max_date_df = pd.DataFrame(columns=['iso_code', 'continent',
                                        'location', 'date', 'total_cases',
                                        'total_vaccinations',
                                        'people_vaccinated',
                                        'people_fully_vaccinated',
                                        'new_vaccinations', 'population',
                                        'percent_vaccinated',
                                        'gdp_per_capita'])
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

    # plot percentage vaccinated vs time with color corresponting to country
    line = alt.Chart(adjusted_top_10_df).mark_line().encode(
        x=alt.X('date:T', axis=alt.Axis(title='Date')),
        y=alt.Y('percent_vaccinated:Q',
                axis=alt.Axis(title='Percent Vaccinated')),
        color=alt.Color('location',
                        legend=alt.Legend(title='Country'),
                        sort=alt.EncodingSortField('percent_vaccinated:Q',
                                                   op='max',
                                                   order='descending'))
    )

    # create nearest selection using cursor position
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            encodings=['x'], empty='none')

    # transparent selectors across the chart. gives location of cursor
    selectors = alt.Chart(adjusted_top_10_df).mark_point().encode(
        x='date:T',
        opacity=alt.value(0)
    ).add_selection(
        nearest
    )

    # draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # display percentage vaccinated, and highlight based on selection
    text = line.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'percent_vaccinated:Q', alt.value(' '))
    )

    # draw a vertical ruler using cursor position
    rules = alt.Chart(adjusted_top_10_df).mark_rule(color='grey').encode(
        x='date:T'
    ).transform_filter(
        nearest
    )

    # combine all parts, add title
    q1_plot = alt.layer(
        line, selectors, points, text, rules
    ).properties(
        width=600, height=400,
        title={
            'text': 'Percentage of Population with COVID-19 Vaccine',
            'subtitle': ['Displaying top 10 countries. Excluded countries '
                         'with population smaller than',
                         '1,000,000. Counts individuals who have recieved'
                         ' at least one vaccine dose.'],
            'color': 'black',
            'subtitleColor': 'darkgrey'
        }
    )

    return(q1_plot)


def get_q2_plot(filtered_data):
    print('Hello')

#### non-plotting part added to processing file ####
def get_q3_xy_plot(filtered_data):

    # remove rows where total vaccinations is 0
    df_3_vacc = filtered_data[filtered_data['total_vaccinations'] != 0]

    # create new dataframe to add rows to
    df_recent_date = pd.DataFrame(columns=['iso_code', 'continent',
                                           'location', 'date', 'total_cases',
                                           'total_vaccinations',
                                           'people_vaccinated',
                                           'people_fully_vaccinated',
                                           'new_vaccinations', 'population',
                                           'percent_vaccinated',
                                           'gdp_per_capita'])

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

    # plot log vs log correlation
    line_log = alt.Chart(df_recent_date).mark_point().encode(
        alt.Y('percent_vaccinated:Q',
              scale=alt.Scale(type='log'),
              title='Percentage Vaccinated'),
        alt.X('gdp_per_capita:Q',
              scale=alt.Scale(type='log'),
              title='GDP Per Capita'),
        tooltip=[alt.Tooltip('location:N', title='Country'),
                 alt.Tooltip('percent_vaccinated:Q',
                 title='Percent Vaccinated'),
                 alt.Tooltip('gdp_per_capita:Q',
                 title='GDP Per Capita'),
                 alt.Tooltip('total_cases:Q',
                 title='Total Cases')]
    ).properties(
        width=600, height=600,
        title={
            'text': 'Log - Log Percentage Vaccinated vs. GDP Per Capita',
            'color': 'black'
        }
    )

    # plot x vs y correlation
    line = alt.Chart(df_recent_date).mark_point().encode(
        alt.Y('percent_vaccinated:Q',
              title='Percentage Vaccinated'),
        alt.X('gdp_per_capita:Q',
              title='GDP Per Capita'),
        tooltip=[alt.Tooltip('location:N', title='Country'),
                 alt.Tooltip('percent_vaccinated',
                             title='Percent Vaccinated'),
                 alt.Tooltip('gdp_per_capita',
                             title='GDP Per Capita'),
                 alt.Tooltip('total_cases',
                             title='Total Cases')]
    ).properties(
        width=600, height=600,
        title={
            'text': 'Percentage Vaccinated vs. GDP Per Capita',
            'color': 'black'
        }
    )

    # side by side
    xy_plot_q3 = line | line_log

    return(xy_plot_q3)

#### non-plotting part added to processing file ####
def get_q3_map_plot(filtered_data):

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

    # plot with hue corresponding to GDP per capita
    fig, ax = plt.subplots(1, figsize=(40, 30))
    ax.axis('off')
    world.plot(ax=ax, color='#CCCCCC')
    merged_world_df.plot(ax=ax, column='gdp_per_capita',
                         legend=True,
                         legend_kwds={'label': 'GDP Per Capita',
                                      'orientation': 'horizontal'})
    return(fig)


def main():
    filtered_data = \
        get_filtered_data('https://covid.ourworldindata.org'
                          '/data/owid-covid-data.csv?v=2021-02-17')
    q1 = get_q1_plot(filtered_data)
    q1.save('q1.html')
    q3_xy = get_q3_xy_plot(filtered_data)
    q3_xy.save('q3_xy.html')
    q3_map = get_q3_map_plot(filtered_data)
    q3_map.savefig('q3_map.png')


if __name__ == "__main__":
    main()
