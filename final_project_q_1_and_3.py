

# Q3 CODE
import pandas as pd
import altair as alt
from altair import datum
import geopandas as gpd
from vega_datasets import data
#import gpdvega
import json
import seaborn as sns
import matplotlib.pyplot as plt
from geopandas import GeoDataFrame

df_3 = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv?v=2021-02-17').fillna(0)

df_3 = df_3[['iso_code', 'continent', 'location',
             'date', 'total_cases', 'total_vaccinations',
             'people_vaccinated', 'people_fully_vaccinated',
             'new_vaccinations', 'population', 'gdp_per_capita']]


## Plotting GDP Per Capita vs Percentage Vaccinated

# remove all instances of where total vaccinations is 0 
df_3_vacc = df_3[df_3['total_vaccinations'] != 0]

# create new dataframe to add rows to
df_recent_date = pd.DataFrame(columns = ['iso_code', 'continent', 'location',
                                         'date', 'total_cases', 'total_vaccinations',
                                         'people_vaccinated', 'people_fully_vaccinated',
                                         'new_vaccinations', 'population', 'percent_vaccinated',
                                         'gdp_per_capita'])

# get list of all country iso codes
countries_3 = df_3_vacc['iso_code'].unique()

# find most recent day for each country
for country in countries_3:
    # one country
    new = df_3_vacc[df_3_vacc['iso_code'] == country]
    # last row for that country
    recent_day = new.iloc[[-1]].copy()
    # replace people vaccinated column if missing
    if (recent_day['people_vaccinated'] == 0).any():
        recent_day['people_vaccinated'] = recent_day['total_vaccinations']
    # calculate percent vaccinated
    recent_day['percent_vaccinated'] = (recent_day['people_vaccinated'] / recent_day['population']) * 100
    # add to dataframe
    df_recent_date = df_recent_date.append(recent_day)

# remove rows where gdp per capita is 0
df_recent_date = df_recent_date[df_recent_date['gdp_per_capita'] != 0]

# plot log vs log correlation
line_log = alt.Chart(df_recent_date).mark_point().encode(
    alt.Y('percent_vaccinated:Q',
          scale = alt.Scale(type = 'log')),
    alt.X('gdp_per_capita:Q',
          scale = alt.Scale(type = 'log'))
).properties(
    width=600, height=600
)

# plot x vs y correlation
line = alt.Chart(df_recent_date).mark_point().encode(
    alt.Y('percent_vaccinated:Q'),
    alt.X('gdp_per_capita:Q')
).properties(
    width=600, height=600
)

# side by side and save
side_by_side_q3 = line | line_log
side_by_side_q3.save('side_by_side_q3.html')



## Plotting GDP Per Capita Choropleth Map
df_3_gdp = df_3[['iso_code', 'gdp_per_capita']]
df_3_gdp = df_3_gdp.groupby(by = 'iso_code').max()

df_3_gdp.reset_index(inplace = True)

print(df_3_gdp)

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Manually enter missing iso codes and missing rows to fill in map
world.iloc[43,3] = 'FRA'
world.iloc[21,3] = 'NOR'
world.iloc[174,3] = 'KOS'
df_3_gdp.iloc[150, 0] = 'KOS'
tkm_row = pd.DataFrame({'iso_code':['TKM'], 
                        'gdp_per_capita':[69966.64]})
df_3_gdp = df_3_gdp.append(tkm_row)

print(df_3_gdp[df_3_gdp['iso_code'] == 'KOS'])

# merge dataframes using iso codes from COVID data frame and convert to geodataframe
merged_world_df = df_3_gdp.merge(world, how = 'left', left_on = 'iso_code', right_on = 'iso_a3')
merged_world_df = GeoDataFrame(merged_world_df)

# plot with hue corresponding to GDP per capita
fig, ax = plt.subplots(1, figsize = (30, 30))
world.plot(ax = ax, color = '#CCCCCC')
merged_world_df.plot(ax = ax, column = 'gdp_per_capita', legend = True)
fig.savefig('worldplot.png')








'''
world['test'] = 0

for i in range (len(world)):
    world['test'][i] = i

country_list = df_recent_date['iso_code'].unique()

#for country in country_list:
    #new_row = world[world['iso_a3'] == country]


#world = data.countries()


#print(world.columns)

#merged_world_df = df_recent_date.merge(world, how = 'inner', left_on = 'iso_code', right_on = 'iso_a3')



print(world)
#print(merged_world_df)


merged_df_json = json.loads(world.to_json())

merged_df_data = alt.Data(values = merged_df_json['features'])

#print(merged_df_data)

colors = alt.Chart(merged_df_data).mark_geoshape().encode(
    color = 'test:Q'
)

colors.save('choro.html')


countries = alt.topo_feature(data.world_110m.url, 'countries')

countries = data.countries()

print(countries.columns)

chart1 = alt.Chart(countries).mark_geoshape().encode(
    color='percentage_vaccinated:Q'
).transform_lookup(
    lookup='location',
    from_=alt.LookupData(df_recent_date, 'country', list(df_recent_date.columns))
).properties(
    width=500,
    height=300
)

chart1.save('chart1.html')

#merged_world_df = alt.utils.sanitize_dataframe(merged_world_df)

#print(df_recent_date.head())

#print(merged_world_df)

#merged_world_df['geometry'] = merged_world_df['geometry'].to_json()


#countries_map = alt.Chart(merged_world_df).mark_geoshape(
#    color = 'percent_vaccinated:Q'
#)

#countries_map.save('countries_map.html')


#countries = alt.topo_feature(data.world_110m.url, 'countries')

#merged_world_df = countries.merge(df_recent_date, how = 'left', left_on = 'country', right_on = 'location')

#countries = countries[countries['year'] == 2000]

print(type(countries))

chart = alt.Chart(merged_world_df).mark_geoshape(
    fill='lightgray',
    stroke='white'
).project(
    "equirectangular"
).properties(
    width=500,
    height=300
)

chart.save('chart.html')
'''