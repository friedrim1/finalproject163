'''
Matthew Friedrich
CSE 163 Section AG

This file contains the functions get_q1_plot, ______,
get_q3_xy_plot, and get_q3_map_plot. Each function takes
the output from a respective function in final_project_processing.py
as a parameter. Then, each function outputs a plot, _____ as an
Altair object and _____ as a Matplotlib object, which then can be saved
in main. Altair plots are interactive, therefore they must be saved
as a '.html' file.
'''


import altair as alt
import geopandas as gpd
import matplotlib.pyplot as plt
import final_project_processing_163


def get_q1_plot(q1_plot_df):
    '''
    Takes processed pandas dataframe from final_project_processing
    as a parameter. Plots top 10 countries with highest percentage
    vaccinated. Creates selection variables based on cursor position, then
    displays vertical ruler on top of chart based on the x-position
    of the cursor. Highlights points that are currently selected, and
    displays text with percentage vaccinated for each selected point.
    Returns an altair plot.
    '''
    # plot percentage vaccinated vs time with color corresponting to country
    line = alt.Chart(q1_plot_df).mark_line().encode(
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
    selectors = alt.Chart(q1_plot_df).mark_point().encode(
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
    rules = alt.Chart(q1_plot_df).mark_rule(color='grey').encode(
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


def get_q2_plot(q2_map_df):

    # load geopandas built-in variable for country shapes
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    fig, ax = plt.subplots(1, figsize=(10, 8))
    ax.axis('off')
    world.plot(ax=ax, color='#EEEEEE', edgecolor='#FFFFFF')
    q2_map_df.plot(ax=ax,
                   column='percent_vaccinated',
                   legend=True, vmin=0, vmax=70,
                   legend_kwds={'label': 'Percentage Vaccinated',
                                'orientation': 'horizontal'})
    ax.set_title('Percentage of Population with '
                 'One Dose of COIVD-19 Vaccine by Nation')
    return(fig)


def get_q3_xy_plot(q3_xy_plot_df):
    '''
    Takes processed pandas dataframe from final_project_processing
    as a parameter. Plots two separate scatter plots:
    The first has GDP per capita on the x-axis and percentage
    vaccinated on the y-axis, and the scales are normal.
    The second has GDP per capita on the x-axis and percentage
    vaccinated on the y-axis, and the x and y axes are logarithmic.
    For both plots, a tooltip was added so that by mvoing the cursor
    over a point, the country name, percentage vaccinated, GDP per
    capita, and total COVID-19 cases is displayed in a text box.
    The figures are then put side by side. Returns an altair plot.
    '''
    # plot log vs log correlation
    scatter_log = alt.Chart(q3_xy_plot_df).mark_point().encode(
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
    scatter = alt.Chart(q3_xy_plot_df).mark_point().encode(
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
    xy_plot_q3 = scatter | scatter_log

    return(xy_plot_q3)


def get_q3_map_plot(q3_map_plot_df):
    '''
    Takes processed pandas dataframe from final_project_processing
    as a parameter. Plots world map as base in grey. Then plots
    choropleth map of all countries with hue corresponding to
    GDP per capita. Returns matplotlib plot.
    '''
    # load geopandas built-in variable for country shapes
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # plot with hue corresponding to GDP per capita
    fig, ax = plt.subplots(1, figsize=(10, 8))
    ax.axis('off')
    world.plot(ax=ax, color='#CCCCCC')
    q3_map_plot_df.plot(ax=ax,
                        column='gdp_per_capita',
                        legend=True,
                        legend_kwds={'label': 'GDP Per Capita',
                                     'orientation': 'horizontal'})
    ax.set_title('GDP Per Capita by Nation (2011 $USD)')
    return(fig)


def main():
    data = final_project_processing_163.get_filtered_data(
                            'https://covid.ourworldindata.org/data/'
                            'owid-covid-data.csv?v=2021-02-17')
    q1_df = final_project_processing_163.get_q1_df(data)
    q2_map_df = final_project_processing_163.get_q2_map_df(data)
    q3_xy_df = final_project_processing_163.get_q3_xy_df(data)
    q3_map_df = final_project_processing_163.get_q3_map_df(data)
    q1_plot = get_q1_plot(q1_df)
    q1_plot.save('q1.html')
    q2_map_plot = get_q2_plot(q2_map_df)
    q2_map_plot.savefig('q2_map.png')
    q3_xy_plot = get_q3_xy_plot(q3_xy_df)
    q3_map_plot = get_q3_map_plot(q3_map_df)
    q3_xy_plot.save('q3_xy.html')
    q3_map_plot.savefig('q3_map.png')


if __name__ == "__main__":
    main()
