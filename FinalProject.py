"""
Class: CS230--Section 002
Name: Michael Morse
Description: Final Project - Meteorite dataset
I pledge that I have completed the programming assignment independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
"""

# Imports
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
import base64


def fixYear(dataFrame):
    df = dataFrame.drop(dataFrame[dataFrame['year'] > 2023].index, inplace=True)
    return df


def mapByYear(dataFrame):
    st.header("Type a year to see where meteorites landed in that year!")
    selected_columns = ['reclat', 'reclong', 'year']
    df_map = dataFrame[selected_columns].rename(columns={'reclat': 'lat', 'reclong': 'lon'}).dropna()
    year_filter = st.text_input("Which year would you like to see? ", value='--')
    if year_filter == '--':
        st.write("You are currently viewing all recorded meteorite landings")
        st.map(df_map, zoom=0)
    else:
        try:
            df_map = df_map.query('year ==' + year_filter)
            if df_map.empty:
                st.write(f'There were no meteorite landings in the year {year_filter}!')
            else:
                st.write(f'Here are the meteorite landings from the year {year_filter}')
                st.map(df_map, zoom=0)
        except:
            st.error("Please enter a valid year")
            st.stop()


def mapBySize(dataFrame):
    # Edit the dataframe to include necessary information
    selected_columns = ['reclat', 'reclong', 'mass (g)']

    # Streamlit functions
    st.header('Choose a filter type and explore meteorites by their size!')
    filter_by = st.selectbox('Filter',
                             ['Greater than', 'Equal to', 'Less than'])
    size_filter = st.slider(label='Select a mass (kg)', min_value=0, max_value=60000, step=1000) * 1000
    num = st.number_input('How many would you like to see?',
                          step=5)
    df_map = mapLargestN(dataFrame, num=num)[selected_columns].rename(
        columns={'reclat': 'lat', 'reclong': 'lon', 'mass (g)': 'mass'}).dropna()
    if filter_by == 'Greater than':
        df_map = df_map.query('mass >=' + str(size_filter))
        st.map(df_map, zoom=0)
    elif filter_by == 'Less than':
        df_map = df_map.query('mass <=' + str(size_filter))
        st.map(df_map, zoom=0)
    elif filter_by == 'Equal to':
        df_map = df_map.query('mass ==' + str(size_filter))
        st.map(df_map, zoom=0)


# This function filters the dataframe based on a set number of entries desired. Default is 100.

# Parameters:
    # dataFrame: the original dataframe
    # num: number of entries desired, default is 100

# Returns:
    # The sorted dataframe


def mapLargestN(dataFrame, num=100):
    df_sorted = dataFrame.sort_values(by=['mass (g)'], ascending=False)
    return df_sorted.head(num)


# This function graphs meteorite records in a histogram, based on a date range

# Parameters:
    # dataFrame: the original dataframe

# Returns:
    # A histogram of meteorite records from the date range


def graphByYear(dataFrame):
    st.header('Select a date range to update the histogram.')
    years = []
    for index, row in dataFrame.iterrows():
        years.append(row['year'])
    show_years = st.slider('What years would you like to see?', 1700, 2023, (1950, 2020))
    bin_length = int((show_years[1] - show_years[0]) / 10)
    bins = [i for i in range(show_years[0], show_years[1]+1, bin_length)]
    fig, ax = plt.subplots()
    ax.hist(years, bins=bins, rwidth=.95)
    plt.title(f"Meteorite Landings from {show_years[0]} to {show_years[1]}")
    plt.xlabel('Year')
    plt.ylabel('Number')
    st.pyplot(fig)


def barByClass(dataFrame):
    grouped_df = dataFrame.groupby('recclass')
    recclass_list = grouped_df.groups.keys()
    selected_class = st.multiselect('Select the classifications to add them to the chart', recclass_list)
    filtered_df = dataFrame[dataFrame['recclass'].isin(selected_class)]
    chart = alt.Chart(filtered_df).mark_bar(color='red').encode(
        x=alt.X('recclass', title='Classification'),
        y=alt.Y('count(mass (g))', title='Recordings')
    ).properties(width=600, height=400)
    st.altair_chart(chart, use_container_width=True)


def pieByClass(dataFrame):
    counts = dataFrame.groupby('recclass')['name'].count()
    classifications = counts.index.tolist()
    selected_class = st.multiselect('Select one or more classifications', classifications)
    filtered_data = dataFrame[dataFrame['recclass'].isin(selected_class)]
    counts_selected = filtered_data.groupby('recclass')['name'].count()
    total_falls = dataFrame['name'].count()
    percent_selected = counts_selected / total_falls * 100
    fig, ax = plt.subplots()
    ax.pie(percent_selected, labels=percent_selected.index, autopct='%1.1f%%')
    ax.set_title('Proportion of Meteorite Falls by Classification')
    st.pyplot(fig)


def exploreRawData(dataFrame):
    df = dataFrame.rename(columns={'name': 'Name', 'id': "ID", 'nametype': 'Name Type',
                                   'recclass': 'Classification', 'mass (g)': 'Mass (grams)',
                                   'fall': 'Fall', 'year': 'Year', 'reclat': 'Latitude',
                                   'reclong': 'Longitude', 'GeoLocation': 'Location'})
    st.header('Explore the raw data using filters below:')
    st.subheader('Table Display Settings')
    columns = st.multiselect(
        label="Select columns",
        options=list(df.columns),
        default=list(df.columns)[:2])
    values = st.selectbox(
        label="Select value",
        options=list(df.columns),
        index=4)
    pivot = pd.pivot_table(df, index=columns, values=values)
    st.write(pivot)


def graphsHeader():
    st.header('Explore the meteorite classifications!')
    if st.checkbox("Click to see NASA's guide to meteorite classification"):
        st.image('classification.png')
        st.caption('https://curator.jsc.nasa.gov/education/classification.cfm')


def main():
    # gif
    file_ = open("meteorite.gif", "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()

    # sidebar
    st.sidebar.markdown(
        f'<img src="data:image/gif;base64,{data_url}" alt="meteorite gif" width=304>',
        unsafe_allow_html=True)
    st.sidebar.title('Welcome!')
    mode = st.sidebar.radio('How would you like to explore the data?',
                            ['Maps', 'Graphs', 'Raw Data'])
    st.sidebar.header('About')
    st.sidebar.write('This site explores all recorded meteorite landings.')
    st.sidebar.write('Created by Michael Morse')

    # Title
    st.title('Meteorite Landings')

    # Initialize DataFrame
    df = pd.read_csv('Meteorite_Landings.csv')

    # Choose mode
    if mode == 'Maps':
        mapByYear(df)
        mapBySize(df)
    elif mode == 'Graphs':
        graphByYear(df)
        graphsHeader()
        view_mode = st.radio('How would you like to view the classifications?',
                             ['Pie Chart', 'Bar Chart'])
        if view_mode == 'Pie Chart':
            pieByClass(df)
        elif view_mode == 'Bar Chart':
            barByClass(df)
    elif mode == 'Raw Data':
        exploreRawData(df)


if __name__ == '__main__':
    main()
