import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import boto3
import io

def extract_data(file_keys):
    s3_client = boto3.client('s3',
                            aws_access_key_id = 'AKIASVQKHKTTRJSXZN4V', 
                            aws_secret_access_key= '8ZlAby+DXcDJfCXxvqwDnJsUJ5Rmp4U3CR+EiVCv')
    BUCKET_NAME = 'tgp-group-assesssment' # replace with your bucket name
    dfs = []
    for file_key in file_keys:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=f"{file_key}.csv")
        csv_content = response['Body'].read().decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_content))
        dfs.append(df)
    return dfs

def preprocess_df(df_list):
    cleaned_dfs = []
    for df in df_list: 
        df = df[['country.value', 'date', 'value']]
        df = df.rename(columns={"country.value": "country_name", "date": "year"})
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df = df.dropna(subset=['year'])
        cleaned_dfs.append(df)
    return cleaned_dfs

def join_with_dim_country(df_list, dim_country_df):
    """
    This function takes a list of DataFrames and performs a left join with dim_country_df
    where df.country_name matches dim_country_df.tablename for each DataFrame in the list.
    
    Parameters:
    df_list (list of pd.DataFrame): List of DataFrames to be joined.
    dim_country_df (pd.DataFrame): The DataFrame to join with.
    
    Returns:
    list of pd.DataFrame: List of DataFrames after performing the left join.
    """
    joined_dfs = []
    for df in df_list:
        # Perform the left join
        joined_df = pd.merge(df, dim_country_df, how='left', left_on='country_name', right_on='tablename')
        joined_df = joined_df.drop(columns=['unnamed:_4'])

        joined_dfs.append(joined_df)
    return joined_dfs

file_keys = ['UrbanArea','IndividualsUsingInternet','FixedBroadbandSubs','MobileCellularSubs','AccountOwnershipAll',
             'AccountOwnershipYoung','AccountOwnershipOld','PrimaryEducation','SecondaryEducation','Poorest40','Richest60',
             'AccessFI','Penetration','DimCountry']

dfs = extract_data(file_keys)
urban_df = dfs[0]
internet_df = dfs[1]
broadband_df = dfs[2]
cellular_df = dfs[3]
fi_df = dfs[4]
fi_young_df = dfs[5]
fi_old_df = dfs[6]
fi_primary_df = dfs[7]
fi_secondary_df = dfs[8]
fi_poor_df = dfs[9]
fi_rich_df = dfs[10]  
final_access_df = dfs[11]
atm_bank_df = dfs[12]
dim_country_df = dfs[13]

dim_country_df.columns = dim_country_df.columns.str.lower().str.replace(r'(?<=\S) (?=\S)', '_', regex=True)
for col in final_access_df.columns:
    if final_access_df[col].dtype == 'object':  # Check if the column is of type object (string)
        final_access_df[col] = final_access_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

for col in atm_bank_df.columns:
    if atm_bank_df[col].dtype == 'object':  # Check if the column is of type object (string)
        atm_bank_df[col] = atm_bank_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

final_access_df['percent_with_access'] = pd.to_numeric(final_access_df['percent_with_access'], downcast='integer')
atm_bank_df['geographic_branch_penetration'] = pd.to_numeric(atm_bank_df['geographic_branch_penetration'], downcast='float')
atm_bank_df['demographic_branch_penetration'] = pd.to_numeric(atm_bank_df['demographic_branch_penetration'], downcast='float')
atm_bank_df['geographic_atm_penetration'] = pd.to_numeric(atm_bank_df['geographic_atm_penetration'], downcast='float')
atm_bank_df['demographic_atm_penetration'] = pd.to_numeric(atm_bank_df['demographic_atm_penetration'], downcast='float')

df_list = [urban_df, internet_df, broadband_df, cellular_df, fi_young_df, fi_df, fi_old_df, fi_primary_df, fi_secondary_df, fi_rich_df, fi_poor_df]
clean_dfs = preprocess_df(df_list)
clean_dfs.append(final_access_df)
clean_dfs.append(atm_bank_df)
join_dfs = join_with_dim_country(clean_dfs, dim_country_df)

urban_df = join_dfs[0]
internet_df = join_dfs[1]
broadband_df = join_dfs[2]
cellular_df = join_dfs[3]
fi_young_df = join_dfs[4]
fi_df = join_dfs[5]
fi_old_df = join_dfs[6]
fi_primary_df = join_dfs[7]
fi_secondary_df = join_dfs[8]
fi_rich_df = join_dfs[9]
fi_poor_df = join_dfs[10]
final_access_df = join_dfs[11]
atm_bank_df = join_dfs[12]

urban_df = urban_df.rename(columns={"value": "urban_population_percentage"})
internet_df = internet_df.rename(columns={"value": "internet_percentage"})
broadband_df = broadband_df.rename(columns={"value": "broadband_percentage"})
cellular_df = cellular_df.rename(columns={"value": "cellular_percentage"})
fi_df = fi_df.rename(columns={"value": "fi_percentage"})
fi_young_df = fi_young_df.rename(columns={"value": "fi_young_percentage"})
fi_old_df = fi_old_df.rename(columns={"value": "fi_old_percentage"})
fi_primary_df = fi_primary_df.rename(columns={"value": "fi_primary_percentage"})
fi_secondary_df = fi_secondary_df.rename(columns={"value": "fi_secondary_percentage"})
fi_rich_df = fi_rich_df.rename(columns={"value": "fi_rich_percentage"})
fi_poor_df = fi_poor_df.rename(columns={"value": "fi_poor_percentage"})

# Default values
default_region = 'East Asia & Pacific'
default_countries = [
    'China', 'Hong Kong SAR, China', 'Indonesia', 'Japan', 
    'Korea, Rep.', 'Malaysia', 'Thailand'
]
st.set_page_config(page_title="TGP Dashboard", layout="wide")
st.title("Digital Reach & Financial Access Dashboard for PayNet Malaysia")

# Create a region filter
regions = ['All'] + sorted(dim_country_df['region'].dropna().unique())
selected_region = st.selectbox('Select a Region', regions, index=regions.index(default_region))

# Filter data based on the selected region
if selected_region != 'All':
    filtered_dim_country_df = dim_country_df[dim_country_df['region'] == selected_region]
else:
    filtered_dim_country_df = dim_country_df

# Create a multi-select dropdown for selecting countries
selected_countries = st.multiselect('Select Countries', filtered_dim_country_df['tablename'].unique(), default=default_countries)

# Filter the DataFrame based on the selected countries
if selected_countries:
    filtered_urban_df = urban_df[urban_df['country_name'].isin(selected_countries)]
    filtered_internet_df = internet_df[internet_df['country_name'].isin(selected_countries)]
    filtered_broadband_df = broadband_df[broadband_df['country_name'].isin(selected_countries)]
    filtered_cellular_df = cellular_df[cellular_df['country_name'].isin(selected_countries)]
    filtered_fi_df = fi_df[fi_df['country_name'].isin(selected_countries)]
    filtered_fi_old_df = fi_old_df[fi_old_df['country_name'].isin(selected_countries)]
    filtered_fi_young_df = fi_young_df[fi_young_df['country_name'].isin(selected_countries)]
    filtered_fi_primary_df = fi_primary_df[fi_primary_df['country_name'].isin(selected_countries)]
    filtered_fi_secondary_df = fi_secondary_df[fi_secondary_df['country_name'].isin(selected_countries)]
    filtered_fi_poor_df = fi_poor_df[fi_poor_df['country_name'].isin(selected_countries)]
    filtered_fi_rich_df = fi_rich_df[fi_rich_df['country_name'].isin(selected_countries)]
    filtered_atm_bank_df = atm_bank_df[atm_bank_df['country_name'].isin(selected_countries)]
else:
    st.write("Please select at least one country.")
    filtered_urban_df = pd.DataFrame()  # Empty DataFrame if no country is selected
    filtered_internet_df = pd.DataFrame()  # Empty DataFrame if no country is selected
    filtered_broadband_df = pd.DataFrame()  # Empty DataFrame if no country is selected
    filtered_cellular_df = pd.DataFrame()  # Empty DataFrame if no country is selected
    filtered_fi_df = pd.DataFrame()  # Empty DataFrame if no country is selected
    filtered_fi_old_df = pd.DataFrame()  # Empty DataFrame if no country is selected
    filtered_fi_young_df = pd.DataFrame()  # Empty DataFrame if no country is selected
    filtered_fi_primary_df = pd.DataFrame()  # Empty DataFrame if no country is selected
    filtered_fi_secondary_df = pd.DataFrame()  # Empty DataFrame if no country is selected
    filtered_fi_poor_df = pd.DataFrame()  # Empty DataFrame if no country is selected
    filtered_fi_rich_df = pd.DataFrame()  # Empty DataFrame if no country is selected
    filtered_atm_bank_df = pd.DataFrame()  # Empty DataFrame if no country is selected


# Create a slider to select the year range
# Create a slider to select the year range
if not filtered_urban_df.empty:
    year_range = st.slider('Select Year Range', min_value=int(urban_df['year'].min()), max_value=2022, value=(int(urban_df['year'].min()), 2022))
    malaysia_internet_df = internet_df[internet_df['country_name'] == 'Malaysia']
    malaysia_fi_df = fi_df[fi_df['country_name'] == 'Malaysia']

    # Filter the DataFrame based on the selected year range
    filtered_urban_df = filtered_urban_df[(filtered_urban_df['year'] >= year_range[0]) & (filtered_urban_df['year'] <= year_range[1])]
    
    filtered_internet_df = filtered_internet_df[(filtered_internet_df['year'] >= (1990 if 1990 > year_range[0] else year_range[0])) & (filtered_internet_df['year'] <= year_range[1])]
    
    filtered_broadband_df = filtered_broadband_df[(filtered_broadband_df['year'] >= (1998 if 1998 > year_range[0] else year_range[0])) & (filtered_broadband_df['year'] <= year_range[1])]
    
    filtered_cellular_df = filtered_cellular_df[(filtered_cellular_df['year'] >= (1990 if 1990 > year_range[0] else year_range[0])) & (filtered_cellular_df['year'] <= year_range[1])]
    
    malaysia_internet_value = malaysia_internet_df[malaysia_internet_df['year'] == year_range[1]]['internet_percentage'].values[0] 
    pre_year = year_range[1] - 1
    pre_malaysia_internet_value = malaysia_internet_df[malaysia_internet_df['year'] == pre_year]['internet_percentage'].values[0] 
    malaysia_internet_value = round(malaysia_internet_value, 2)
    delta_malaysia_internet_value = round(malaysia_internet_value - pre_malaysia_internet_value,2)
    
    malaysia_fi_value = malaysia_fi_df[malaysia_fi_df['year'] == 2021]['fi_percentage'].values[0]
    pre_malaysia_fi_value = malaysia_fi_df[malaysia_fi_df['year'] == 2017]['fi_percentage'].values[0]
    delta_malaysia_fi_value = round(malaysia_fi_value - pre_malaysia_fi_value,2)
    
    filtered_fi_df = filtered_fi_df[(filtered_fi_df['year'] >= (2011 if 2011 > year_range[0] else year_range[0])) & (filtered_fi_df['year'] <= year_range[1])]
    filtered_years = filtered_fi_df['year'].unique()
    filtered_fi_df = filtered_fi_df[filtered_fi_df['year'].isin(filtered_years)]
    
    filtered_fi_old_df = filtered_fi_old_df[(filtered_fi_old_df['year'] >= (2011 if 2011 > year_range[0] else year_range[0])) & (filtered_fi_old_df['year'] <= year_range[1])]
    filtered_years = filtered_fi_old_df['year'].unique()
    filtered_fi_old_df = filtered_fi_old_df[filtered_fi_old_df['year'].isin(filtered_years)]
    
    filtered_fi_young_df = filtered_fi_young_df[(filtered_fi_young_df['year'] >= (2011 if 2011 > year_range[0] else year_range[0])) & (filtered_fi_young_df['year'] <= year_range[1])]
    filtered_years = filtered_fi_young_df['year'].unique()
    filtered_fi_young_df = filtered_fi_young_df[filtered_fi_young_df['year'].isin(filtered_years)]    

    filtered_fi_primary_df = filtered_fi_primary_df[(filtered_fi_primary_df['year'] >= (2011 if 2011 > year_range[0] else year_range[0])) & (filtered_fi_primary_df['year'] <= year_range[1])]
    filtered_years = filtered_fi_primary_df['year'].unique()
    filtered_fi_primary_df = filtered_fi_primary_df[filtered_fi_primary_df['year'].isin(filtered_years)]    

    filtered_fi_secondary_df = filtered_fi_secondary_df[(filtered_fi_secondary_df['year'] >= (2011 if 2011 > year_range[0] else year_range[0])) & (filtered_fi_secondary_df['year'] <= year_range[1])]
    filtered_years = filtered_fi_secondary_df['year'].unique()
    filtered_fi_secondary_df = filtered_fi_secondary_df[filtered_fi_secondary_df['year'].isin(filtered_years)]    

    filtered_fi_poor_df = filtered_fi_poor_df[(filtered_fi_poor_df['year'] >= (2011 if 2011 > year_range[0] else year_range[0])) & (filtered_fi_poor_df['year'] <= year_range[1])]
    filtered_years = filtered_fi_poor_df['year'].unique()
    filtered_fi_poor_df = filtered_fi_poor_df[filtered_fi_poor_df['year'].isin(filtered_years)]    

    filtered_fi_rich_df = filtered_fi_rich_df[(filtered_fi_rich_df['year'] >= (2011 if 2011 > year_range[0] else year_range[0])) & (filtered_fi_rich_df['year'] <= year_range[1])]
    filtered_years = filtered_fi_rich_df['year'].unique()
    filtered_fi_rich_df = filtered_fi_rich_df[filtered_fi_rich_df['year'].isin(filtered_years)]    

    # Create an Altair chart with wider line width
    urban_chart = alt.Chart(filtered_urban_df).mark_line(strokeWidth=3).encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('urban_population_percentage:Q', title='% of Population'),
        color='country_name:N',
        tooltip=['year', 'country_name', 'urban_population_percentage']
    ).properties(
        title='Urban Population'
    )

    internet_chart = alt.Chart(filtered_internet_df).mark_line(strokeWidth=3).encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('internet_percentage:Q', title='% of Population'),
        color='country_name:N',
        tooltip=['year', 'country_name', 'internet_percentage']
    ).properties(
        title='Individuals using the Internet'
    )

    broadband_chart = alt.Chart(filtered_broadband_df).mark_line(strokeWidth=3).encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('broadband_percentage:Q', title='per 100 people'),
        color='country_name:N',
        tooltip=['year', 'country_name', 'broadband_percentage']
    ).properties(
        title='Fixed broadband subscriptions'
    )

    cellular_chart = alt.Chart(filtered_cellular_df).mark_line(strokeWidth=3).encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('cellular_percentage:Q', title='per 100 people'),
        color='country_name:N',
        tooltip=['year', 'country_name', 'cellular_percentage']
    ).properties(
        title='Mobile Cellular Subscriptions'
    )

    fi_chart = alt.Chart(filtered_fi_df).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('fi_percentage:Q', title='% of Population ages 15+'),
        color='country_name:N',  # Different colors for each country
        column='country_name:N',  # Separate columns for each country
        tooltip=['country_name', 'year', 'fi_percentage']  # Show details on hover
    ).properties(
        title='Account Ownership at Financial Institution or Mobile-Money-Service Provider'
    )

    fi_old_chart = alt.Chart(filtered_fi_old_df).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('fi_old_percentage:Q', title='% of Population'),
        color='country_name:N',  # Different colors for each country
        column='country_name:N',  # Separate columns for each country
        tooltip=['country_name', 'year', 'fi_old_percentage']  # Show details on hover
    ).properties(
        title='Account Ownership for Older Adults (Age 25+)'
    )

    fi_young_chart = alt.Chart(filtered_fi_young_df).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('fi_young_percentage:Q', title='% of Population'),
        color='country_name:N',  # Different colors for each country
        column='country_name:N',  # Separate columns for each country
        tooltip=['country_name', 'year', 'fi_young_percentage']  # Show details on hover
    ).properties(
        title='Account Ownership for Younger Adults (Age 15 - 24)'
    )

    fi_primary_chart = alt.Chart(filtered_fi_primary_df).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('fi_primary_percentage:Q', title='% of Population'),
        color='country_name:N',  # Different colors for each country
        column='country_name:N',  # Separate columns for each country
        tooltip=['country_name', 'year', 'fi_primary_percentage']  # Show details on hover
    ).properties(
        title='Account Ownership for Individuals with Primary Education or Lower'
    )

    fi_secondary_chart = alt.Chart(filtered_fi_secondary_df).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('fi_secondary_percentage:Q', title='% of Population'),
        color='country_name:N',  # Different colors for each country
        column='country_name:N',  # Separate columns for each country
        tooltip=['country_name', 'year', 'fi_secondary_percentage']  # Show details on hover
    ).properties(
        title='Account Ownership for Individuals with Secondary Education or Higher'
    )

    fi_poor_chart = alt.Chart(filtered_fi_poor_df).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('fi_poor_percentage:Q', title='% of Population'),
        color='country_name:N',  # Different colors for each country
        column='country_name:N',  # Separate columns for each country
        tooltip=['country_name', 'year', 'fi_poor_percentage']  # Show details on hover
    ).properties(
        title='Account Ownership for B40 Group'
    )

    fi_rich_chart = alt.Chart(filtered_fi_rich_df).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('fi_rich_percentage:Q', title='% of Population'),
        color='country_name:N',  # Different colors for each country
        column='country_name:N',  # Separate columns for each country
        tooltip=['country_name', 'year', 'fi_rich_percentage']  # Show details on hover
    ).properties(
        title='Account Ownership for M40+ Group'
    )    

    # Calculate the width dynamically
    num_years = len(filtered_fi_df['year'].unique())
    bar_width = 14  # Desired bar width
    chart_width = num_years * bar_width

    # Combine separate columns into the same x-axis
    fi_chart = fi_chart.configure_facet(
        spacing=10
    ).properties(
        width = chart_width  # Width of each bar
    )

    # Combine separate columns into the same x-axis
    fi_old_chart = fi_old_chart.configure_facet(
        spacing=9
    ).properties(
        width = 58  # Width of each bar
    )

    # Combine separate columns into the same x-axis
    fi_young_chart = fi_young_chart.configure_facet(
        spacing=9
    ).properties(
        width = 58  # Width of each bar
    )

    # Combine separate columns into the same x-axis
    fi_primary_chart = fi_primary_chart.configure_facet(
        spacing=9
    ).properties(
        width = 58  # Width of each bar
    )

    # Combine separate columns into the same x-axis
    fi_secondary_chart = fi_secondary_chart.configure_facet(
        spacing=9
    ).properties(
        width = 58  # Width of each bar
    )

    # Combine separate columns into the same x-axis
    fi_poor_chart = fi_poor_chart.configure_facet(
        spacing=9
    ).properties(
        width = 58  # Width of each bar
    )

    # Combine separate columns into the same x-axis
    fi_rich_chart = fi_rich_chart.configure_facet(
        spacing=9
    ).properties(
        width = 58  # Width of each bar
    )

    # Create bar charts using Altair
    geo_branch_chart = alt.Chart(filtered_atm_bank_df).mark_bar().encode(
        x=alt.X('country_name:N', title='Country'),
        y=alt.Y('geographic_branch_penetration:Q', title='per 1000 Square Kilometer'),
        color='country_name:N'
    ).properties(
        title='Geographic Branch Penetration'
    )

    demo_branch_chart = alt.Chart(filtered_atm_bank_df).mark_bar().encode(
        x=alt.X('country_name:N', title='Country'),
        y=alt.Y('demographic_branch_penetration:Q', title='per 100,000 people'),
        color='country_name:N'
    ).properties(
        title='Demographic Branch Penetration'
    )

    # Create bar charts using Altair
    geo_atm_chart = alt.Chart(filtered_atm_bank_df).mark_bar().encode(
        x=alt.X('country_name:N', title='Country'),
        y=alt.Y('geographic_atm_penetration:Q', title='per 1000 Square Kilometer'),
        color='country_name:N'
    ).properties(
        title='Geographic ATM Penetration'
    )

    demo_atm_chart = alt.Chart(filtered_atm_bank_df).mark_bar().encode(
        x=alt.X('country_name:N', title='Country'),
        y=alt.Y('demographic_atm_penetration:Q', title='per 100,000 people'),
        color='country_name:N'
    ).properties(
        title='Demographic ATM Penetration'
    )

    # Combine separate columns into the same x-axis
    geo_branch_chart = geo_branch_chart.configure_facet(
        spacing=7
    ).properties(
        width = 60  # Width of each bar
    )

    # Combine separate columns into the same x-axis
    demo_branch_chart = demo_branch_chart.configure_facet(
        spacing=7
    ).properties(
        width = 60  # Width of each bar
    )

    # Combine separate columns into the same x-axis
    geo_atm_chart = geo_atm_chart.configure_facet(
        spacing=7
    ).properties(
        width = 60  # Width of each bar
    )

    # Combine separate columns into the same x-axis
    demo_atm_chart = demo_atm_chart.configure_facet(
        spacing=7
    ).properties(
        width = 60  # Width of each bar
    )


    col1, col2, col3 = st.columns([1, 1, 2]) 
    with col1:
      #st.subheader("Account Ownership at Financial Institution or Mobile-Money-Service Provider in Malaysia for Year 2021")
      st.markdown(
            f"""
            <div style='text-align: justify;'>
                <h3>Account Ownership at Financial Institution or Mobile-Money-Service Provider in Malaysia for Year 2021</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )      
      st.metric(label="% of Population ages 15+", value=f"{malaysia_fi_value}%", delta = f"{delta_malaysia_fi_value}% (2017)")

    with col2:
      #st.subheader("Individuals using Internet in Malaysia for Year " + f"{year_range[1]}")
      st.markdown(
            f"""
            <div style='text-align: justify;'>
                <h3>Individuals using Internet in Malaysia for Year {year_range[1]}</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
      st.metric(label="% of Population", value=f"{malaysia_internet_value}%", delta = f"{delta_malaysia_internet_value}% ({pre_year})")

    with col3:
      st.altair_chart(urban_chart, use_container_width=True)


    col1, col2, col3 = st.columns([1, 1, 1]) 
    with col1:
      st.altair_chart(internet_chart, use_container_width=True)

    with col2:
      st.altair_chart(broadband_chart, use_container_width=True)

    with col3:
      st.altair_chart(cellular_chart, use_container_width=True)


    st.altair_chart(fi_chart, use_container_width=False)
    
    col1, col2 = st.columns([1, 1])     
    with col1:
      st.altair_chart(fi_young_chart, use_container_width=False)
    
    with col2:
      st.altair_chart(fi_old_chart, use_container_width=False)


    col1, col2 = st.columns([1, 1])     
    with col1:
      st.altair_chart(fi_primary_chart, use_container_width=False)
    
    with col2:
      st.altair_chart(fi_secondary_chart, use_container_width=False)


    col1, col2 = st.columns([1, 1])     
    with col1:
      st.altair_chart(fi_poor_chart, use_container_width=False)
    
    with col2:
      st.altair_chart(fi_rich_chart, use_container_width=False)

    # Load geographic data for countries (GeoJSON file)
    geojson_url = 'https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json'

    # Create the choropleth map with a continuous color scale
    fig = px.choropleth(
        final_access_df,
        geojson=geojson_url,
        locations='country_name',
        featureidkey="properties.name",  # Match GeoJSON 'name' property to DataFrame 'country_name'
        color='percent_with_access',
        color_continuous_scale='YlOrRd',  # Use a continuous heatmap color scale
        range_color=[0, 100],  # Set the color scale range to match percentage values
        #projection='natural earth',
        title='Composite Measure of Access to Financial Services'
    )

    # Enhance the map's appearance
    fig.update_geos(
        showcoastlines=True,
        coastlinecolor="Black",
        showland=True,
        landcolor="lightgray",
        showocean=True,
        oceancolor="lightblue",
        showlakes=True,
        lakecolor="lightblue",
        showrivers=True,
        rivercolor="blue"
    )

    # Update layout for better aesthetics and ensure continuous colorbar
    fig.update_layout(
        margin={"r":0,"t":50,"l":0,"b":0},
        coloraxis_colorbar={
            'title': 'Access Level (%)',
            'thickness': 15,
            'len': 0.5,
            'outlinewidth': 1,
            'outlinecolor': 'black',
            'ticks': 'outside',
            'tickvals': [0, 20, 40, 60, 80, 100],  # Keep ticks to mark significant levels
            'ticktext': ['0', 'Low', 'Moderate', 'High', 'Very High'],
            'showticklabels': True,
        }
    )

    # Ensure colorbar is continuous
    fig.update_coloraxes(colorbar=dict(
        title="Access Level (%)",
        tickvals=[0, 20, 40, 60, 80, 100],  # Ticks still reflect key points
        ticktext=['0', 'Low', 'Moderate', 'High', 'Very High'],
        lenmode="fraction",
        len=0.75,  # Adjust length of the colorbar
        thickness=20,  # Adjust thickness of the colorbar
    ))

    # Display the figure in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])     
    with col1:
      st.altair_chart(geo_branch_chart, use_container_width=True)
    
    with col2:
      st.altair_chart(demo_branch_chart, use_container_width=True)

    with col3:
      st.altair_chart(geo_atm_chart, use_container_width=True)

    with col4:
      st.altair_chart(demo_atm_chart, use_container_width=True)
