import streamlit as st
import pandas as pd
import altair as alt

def clean_column_names(df_list):
    """
    This function takes a list of DataFrames as input, converts column names to lowercase, 
    and replaces spaces between characters with underscores for each DataFrame in the list.
    
    Parameters:
    df_list (list of pd.DataFrame): The list of DataFrames to be processed.
    
    Returns:
    list of pd.DataFrame: The list of DataFrames with cleaned column names.
    """
    cleaned_dfs = []
    for df in df_list: 
        df.columns = df.columns.str.lower().str.replace(r'(?<=\S) (?=\S)', '_', regex=True)
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
        joined_dfs.append(joined_df)
    return joined_dfs

urban_df = pd.read_csv('/content/drive/MyDrive/TGP_Assessment/API_SP.URB.TOTL.IN.ZS_DS2_en_csv_v2_2789503.csv',skiprows=4)
urban_df =urban_df.drop(columns = ['Unnamed: 68'])

internet_df = pd.read_csv('/content/drive/MyDrive/TGP_Assessment/API_IT.NET.USER.ZS_DS2_en_csv_v2_2789860.csv',skiprows=4)
internet_df =internet_df.drop(columns = ['Unnamed: 68'])

broadband_df = pd.read_csv('/content/drive/MyDrive/TGP_Assessment/API_IT.NET.BBND.P2_DS2_en_csv_v2_2836660.csv',skiprows=4)
broadband_df =broadband_df.drop(columns = ['Unnamed: 68'])

cellular_df = pd.read_csv('/content/drive/MyDrive/TGP_Assessment/API_IT.CEL.SETS.P2_DS2_en_csv_v2_2809477.csv',skiprows=4)
cellular_df =cellular_df.drop(columns = ['Unnamed: 68'])

fi_df = pd.read_csv('/content/drive/MyDrive/TGP_Assessment/API_FX.OWN.TOTL.ZS_DS2_en_csv_v2_2819275.csv', skiprows=4)
fi_df = fi_df.drop(columns=['Unnamed: 68'])


fi_young_df = pd.read_csv('/content/drive/MyDrive/TGP_Assessment/API_FX.OWN.TOTL.YG.ZS_DS2_en_csv_v2_2912133.csv', skiprows=4)
fi_young_df = fi_young_df.drop(columns=['Unnamed: 68'])

fi_old_df = pd.read_csv('/content/drive/MyDrive/TGP_Assessment/API_FX.OWN.TOTL.OL.ZS_DS2_en_csv_v2_2992411.csv',skiprows=4)
fi_old_df = fi_old_df.drop(columns=['Unnamed: 68'])

fi_primary_df = pd.read_csv('/content/drive/MyDrive/TGP_Assessment/API_FX.OWN.TOTL.PL.ZS_DS2_en_csv_v2_2911163.csv',skiprows=4)
fi_primary_df = fi_primary_df.drop(columns=['Unnamed: 68'])

fi_secondary_df = pd.read_csv('/content/drive/MyDrive/TGP_Assessment/API_FX.OWN.TOTL.SO.ZS_DS2_en_csv_v2_2912139.csv',skiprows=4)
fi_secondary_df = fi_secondary_df.drop(columns=['Unnamed: 68'])

fi_rich_df = pd.read_csv('/content/drive/MyDrive/TGP_Assessment/API_FX.OWN.TOTL.60.ZS_DS2_en_csv_v2_2876757.csv', skiprows=4)
fi_rich_df = fi_rich_df.drop(columns=['Unnamed: 68'])

fi_poor_df = pd.read_csv('/content/drive/MyDrive/TGP_Assessment/API_FX.OWN.TOTL.40.ZS_DS2_en_csv_v2_2913281.csv', skiprows=4)
fi_poor_df = fi_poor_df.drop(columns=['Unnamed: 68'])

dim_country_df = pd.read_csv('/content/drive/MyDrive/TGP_Assessment/Metadata_Country_API_IT.NET.USER.ZS_DS2_en_csv_v2_2789860.csv')
dim_country_df = dim_country_df.drop(columns=['Unnamed: 5','Country Code'])
dim_country_df.columns = dim_country_df.columns.str.lower().str.replace(r'(?<=\S) (?=\S)', '_', regex=True)

xls = pd.ExcelFile('/content/drive/MyDrive/TGP_Assessment/prr_data_for_website_0.xls')
dfs = {sheet_name: pd.read_excel(xls, sheet_name, skiprows=3) for sheet_name in xls.sheet_names}
access_df = dfs['Table A.1']
access_df.head()

# Assume df is your DataFrame

# Step 1: Drop the 'Unnamed: 0' column
access_df = access_df.drop(columns=['Unnamed: 0'])

# Step 2: Combine 'Unnamed: 1', 'Unnamed: 4', and 'Unnamed: 7' into one column under new rows
df_combined_1 = pd.concat([access_df['Unnamed: 1'], access_df['Unnamed: 4'], access_df['Unnamed: 7']], ignore_index=True).dropna().reset_index(drop=True)
df_combined_1.name = 'country_name'  # Naming the new column

# Step 3: Combine 'Unnamed: 2', 'Unnamed: 5', and 'Unnamed: 8' into one column under new rows
df_combined_2 = pd.concat([access_df['Unnamed: 2'], access_df['Unnamed: 5'], access_df['Unnamed: 8']], ignore_index=True).dropna().reset_index(drop=True)
df_combined_2.name = 'survey'  # Naming the new column

# Step 4: Combine 'Percent with access', 'Percent with access.1', and 'Percent with access.2' into one column under new rows
df_combined_percent = pd.concat([access_df['Percent with access'], access_df['Percent with access.1'], access_df['Percent with access.2']], ignore_index=True).dropna().reset_index(drop=True)
df_combined_percent.name = 'Percent_with_access'  # Naming the new column

# Step 5: Combine the three new columns into a final DataFrame
final_access_df = pd.DataFrame({
    'country_name': df_combined_1,
    'survey': df_combined_2,
    'Percent_with_access': df_combined_percent
})
for col in final_access_df.columns:
    if final_access_df[col].dtype == 'object':  # Check if the column is of type object (string)
        final_access_df[col] = final_access_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
# Display the resulting DataFrame
final_access_df.head()

atm_bank_df = dfs['Table A.3']
atm_bank_df.head()

atm_bank_df = atm_bank_df.drop(columns=['Unnamed: 0'])
atm_bank_df = atm_bank_df.rename(columns={"Unnamed: 1": "country_name"})
for col in atm_bank_df.columns:
    if atm_bank_df[col].dtype == 'object':  # Check if the column is of type object (string)
        atm_bank_df[col] = atm_bank_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
atm_bank_df.head()

df_list = [urban_df, internet_df, broadband_df, cellular_df, fi_young_df, fi_df, fi_old_df, fi_primary_df, fi_secondary_df, fi_rich_df, fi_poor_df, final_access_df, atm_bank_df]
cleaned_dfs = clean_column_names(df_list)
join_dfs = join_with_dim_country(cleaned_dfs, dim_country_df)

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

urban_long_df = urban_df.melt(id_vars=['country_name', 'region', 'incomegroup'], 
                              value_vars=[str(year) for year in range(1960, 2023)], 
                              var_name='year', 
                              value_name='urban_population_percentage')

# Convert 'year' to numeric
urban_long_df['year'] = pd.to_numeric(urban_long_df['year'], errors='coerce')
urban_long_df = urban_long_df.dropna(subset=['year'])

internet_long_df = internet_df.melt(id_vars=['country_name', 'region', 'incomegroup'], 
                              value_vars=[str(year) for year in range(1960, 2023)], 
                              var_name='year', 
                              value_name='internet_percentage')

# Convert 'year' to numeric
internet_long_df['year'] = pd.to_numeric(internet_long_df['year'], errors='coerce')
internet_long_df = internet_long_df.dropna(subset=['year'])

broadband_long_df = broadband_df.melt(id_vars=['country_name', 'region', 'incomegroup'], 
                              value_vars=[str(year) for year in range(1960, 2023)], 
                              var_name='year', 
                              value_name='broadband_percentage')

# Convert 'year' to numeric
broadband_long_df['year'] = pd.to_numeric(broadband_long_df['year'], errors='coerce')
broadband_long_df = broadband_long_df.dropna(subset=['year'])


cellular_long_df = cellular_df.melt(id_vars=['country_name', 'region', 'incomegroup'], 
                              value_vars=[str(year) for year in range(1960, 2023)], 
                              var_name='year', 
                              value_name='cellular_percentage')

# Convert 'year' to numeric
cellular_long_df['year'] = pd.to_numeric(cellular_long_df['year'], errors='coerce')
cellular_long_df = cellular_long_df.dropna(subset=['year'])

fi_long_df = fi_df.melt(id_vars=['country_name', 'region', 'incomegroup'], 
                              value_vars=[str(year) for year in range(1960, 2023)], 
                              var_name='year', 
                              value_name='fi_percentage')

# Convert 'year' to numeric
fi_long_df['year'] = pd.to_numeric(fi_long_df['year'], errors='coerce')
fi_long_df = fi_long_df.dropna(subset=['year'])

fi_old_long_df = fi_old_df.melt(id_vars=['country_name', 'region', 'incomegroup'], 
                              value_vars=[str(year) for year in range(1960, 2023)], 
                              var_name='year', 
                              value_name='fi_old_percentage')

# Convert 'year' to numeric
fi_old_long_df['year'] = pd.to_numeric(fi_old_long_df['year'], errors='coerce')
fi_old_long_df = fi_old_long_df.dropna(subset=['year'])

fi_young_long_df = fi_young_df.melt(id_vars=['country_name', 'region', 'incomegroup'], 
                              value_vars=[str(year) for year in range(1960, 2023)], 
                              var_name='year', 
                              value_name='fi_young_percentage')

# Convert 'year' to numeric
fi_young_long_df['year'] = pd.to_numeric(fi_young_long_df['year'], errors='coerce')
fi_young_long_df = fi_young_long_df.dropna(subset=['year'])

fi_primary_long_df = fi_primary_df.melt(id_vars=['country_name', 'region', 'incomegroup'], 
                              value_vars=[str(year) for year in range(1960, 2023)], 
                              var_name='year', 
                              value_name='fi_primary_percentage')

# Convert 'year' to numeric
fi_primary_long_df['year'] = pd.to_numeric(fi_primary_long_df['year'], errors='coerce')
fi_primary_long_df = fi_primary_long_df.dropna(subset=['year'])

fi_secondary_long_df = fi_secondary_df.melt(id_vars=['country_name', 'region', 'incomegroup'], 
                              value_vars=[str(year) for year in range(1960, 2023)], 
                              var_name='year', 
                              value_name='fi_secondary_percentage')

# Convert 'year' to numeric
fi_secondary_long_df['year'] = pd.to_numeric(fi_secondary_long_df['year'], errors='coerce')
fi_secondary_long_df = fi_secondary_long_df.dropna(subset=['year'])

fi_poor_long_df = fi_poor_df.melt(id_vars=['country_name', 'region', 'incomegroup'], 
                              value_vars=[str(year) for year in range(1960, 2023)], 
                              var_name='year', 
                              value_name='fi_poor_percentage')

# Convert 'year' to numeric
fi_poor_long_df['year'] = pd.to_numeric(fi_poor_long_df['year'], errors='coerce')
fi_poor_long_df = fi_poor_long_df.dropna(subset=['year'])

fi_rich_long_df = fi_rich_df.melt(id_vars=['country_name', 'region', 'incomegroup'], 
                              value_vars=[str(year) for year in range(1960, 2023)], 
                              var_name='year', 
                              value_name='fi_rich_percentage')

# Convert 'year' to numeric
fi_rich_long_df['year'] = pd.to_numeric(fi_rich_long_df['year'], errors='coerce')
fi_rich_long_df = fi_rich_long_df.dropna(subset=['year'])

# Default values
default_region = 'East Asia & Pacific'
default_countries = [
    'Australia', 'China', 'Hong Kong SAR, China', 'Indonesia', 'Japan', 
    'Korea, Rep.', 'Malaysia', 'Singapore', 'Thailand'
]
st.set_page_config(page_title="TGP Dashboard", layout="wide")

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
    filtered_urban_df = urban_long_df[urban_long_df['country_name'].isin(selected_countries)]
    filtered_internet_df = internet_long_df[internet_long_df['country_name'].isin(selected_countries)]
    filtered_broadband_df = broadband_long_df[broadband_long_df['country_name'].isin(selected_countries)]
    filtered_cellular_df = cellular_long_df[cellular_long_df['country_name'].isin(selected_countries)]
    filtered_fi_df = fi_long_df[fi_long_df['country_name'].isin(selected_countries)]
    filtered_fi_old_df = fi_old_long_df[fi_old_long_df['country_name'].isin(selected_countries)]
    filtered_fi_young_df = fi_young_long_df[fi_young_long_df['country_name'].isin(selected_countries)]
    filtered_fi_primary_df = fi_primary_long_df[fi_primary_long_df['country_name'].isin(selected_countries)]
    filtered_fi_secondary_df = fi_secondary_long_df[fi_secondary_long_df['country_name'].isin(selected_countries)]
    filtered_fi_poor_df = fi_poor_long_df[fi_poor_long_df['country_name'].isin(selected_countries)]
    filtered_fi_rich_df = fi_rich_long_df[fi_rich_long_df['country_name'].isin(selected_countries)]

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


# Create a slider to select the year range
if not filtered_urban_df.empty:
    year_range = st.slider('Select Year Range', min_value=int(urban_long_df['year'].min()), max_value=int(urban_long_df['year'].max()), value=(int(urban_long_df['year'].min()), int(urban_long_df['year'].max())))
    malaysia_internet_df = internet_long_df[internet_long_df['country_name'] == 'Malaysia']
    malaysia_fi_df = fi_long_df[fi_long_df['country_name'] == 'Malaysia']

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
        title='Account Ownership for Individuals with Primary Education or Lower (Age 25+)'
    )

    fi_secondary_chart = alt.Chart(filtered_fi_secondary_df).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('fi_secondary_percentage:Q', title='% of Population'),
        color='country_name:N',  # Different colors for each country
        column='country_name:N',  # Separate columns for each country
        tooltip=['country_name', 'year', 'fi_secondary_percentage']  # Show details on hover
    ).properties(
        title='Account Ownership for Individuals with Secondary Education or Higher (Age 25+)'
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
    bar_width = 10  # Desired bar width
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




