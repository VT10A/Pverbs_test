import streamlit as st
import pandas as pd
from random import sample
from APIcall import get_chat_completions
import plotly.express as px




# Load the dataset
@st.cache_data
def load_data():
    return pd.read_csv('myverbs.csv')

data = load_data()

# Sidebar filters
st.sidebar.title("Filters")

# Radio button to select between Total and Filtered
filter_type = st.sidebar.radio("Select view:", ["Total", "Filtered"])

# From new documentation about Pandas 3.0.0, the copy_on_write option is set to False by default. This can cause performance issues with large datasets. To avoid this, we can set it to True to enable copy-on-write mode.
pd.options.mode.copy_on_write = True 

if filter_type == "Filtered":
    # Obtain unique values for country, age and brand
    all_Country_groups = data['Country'].unique()
    all_age_groups = data['Age'].unique()
    all_brands = data['Brand'].unique()

    # Define filter variables with all options selected by default
    country_filter = st.sidebar.multiselect("Select Country:", all_Country_groups, all_Country_groups)
    age_filter = st.sidebar.multiselect("Select Age:", all_age_groups, all_age_groups)
    brand_filter = st.sidebar.multiselect("Select Brand:", all_brands, all_brands)

    # Apply filters
    filtered_data = data[(data['Age'].isin(age_filter)) & (data['Brand'].isin(brand_filter)) & (data['Country'].isin(country_filter))]

    # Calculate topic percentages using filtered data
    topics = filtered_data.columns[1:20]
    topic_percentages = {}
    topic_samples = {}
    for topic in topics:
        topic_percentages[topic] = round((filtered_data[topic] == 1).sum() / len(filtered_data) * 100, 4)
        positive_indices = filtered_data.index[filtered_data[topic] == 1].tolist()
        sample_size = min(3, len(positive_indices))
        topic_samples[topic] = sample(filtered_data.loc[positive_indices, 'text'].tolist(), sample_size)

    # Create a chart for topic percentages using filtered data
    st.write("## Overall Satisfaction Topics % (Filtered)")
    fig = px.bar(x=list(topic_percentages.keys()), y=list(topic_percentages.values()), labels={'x':'Topics', 'y':'Percentage'})
    fig.update_layout(xaxis={'categoryorder':'total descending'}, yaxis_title="Percentage")

    # Construct custom hovertemplate with verbatim for each topic
    hovertemplate = []
    for topic, samples in topic_samples.items():
        tooltip_text = f"<b>{topic}</b><br><br>Percentage: {topic_percentages[topic]}%<br><br>Sample Verbatim:<br>"
        tooltip_text += "<br>".join([f"- {sample_text}" for sample_text in samples])
        hovertemplate.append(tooltip_text)

    # Update hovertemplate for each bar in the chart
    fig.update_traces(hovertemplate=hovertemplate)

    # Write a short heading
    heading = get_chat_completions(f"Summarise the top 4 topics - those with the highest % in descending order (excluding the 'Other' topic from this ranking) in two sentences, in the format X, Y, and Z are the top 4 cited themes. Make sure your commentry focuses on the items that have the highest percentages only (rank the top 4). Don't use decimals. Here's the data {topic_percentages}.")
    st.write(heading)

    # Display the chart in the main area
    st.plotly_chart(fig)

    # Display the filtered dataset in the main area
    st.write("## Filtered Dataset")
    st.write(filtered_data)

    # Add a download button for the filtered dataset
    csv = filtered_data.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='filtered_myverbs.csv',
        mime='text/csv'
    )
else:
    # Calculate topic percentages for total dataset
    topics = data.columns[1:20]
    topic_percentages = {}
    topic_samples = {}
    for topic in topics:
        topic_percentages[topic] = round((data[topic] == 1).sum() / len(data) * 100, 4)
        positive_indices = data.index[data[topic] == 1].tolist()
        sample_size = min(3, len(positive_indices))
        topic_samples[topic] = sample(data.loc[positive_indices, 'text'].tolist(), sample_size)

    # Create a chart for topic percentages for total dataset
    st.write("## Overall Satisfaction Topics % (Total)")
    fig = px.bar(x=list(topic_percentages.keys()), y=list(topic_percentages.values()), labels={'x':'Topics', 'y':'Percentage'})
    fig.update_layout(xaxis={'categoryorder':'total descending'}, yaxis_title="Percentage")

    # Construct custom hovertemplate with verbatim for each topic for total dataset
    hovertemplate = []
    for topic, samples in topic_samples.items():
        tooltip_text = f"<b>{topic}</b><br><br>Percentage: {topic_percentages[topic]}%<br><br>Sample Verbatim:<br>"
        tooltip_text += "<br>".join([f"- {sample_text}" for sample_text in samples])
        hovertemplate.append(tooltip_text)

    # Update hovertemplate for each bar in the chart for total dataset
    fig.update_traces(hovertemplate=hovertemplate)

    # Write a short heading
    heading = get_chat_completions(f"Summarise the top 4 topics - those with the highest % in descending order (excluding the 'Other' topic from this ranking) in two sentences, in the format X, Y, and Z are the top 4 cited themes. Make sure your commentry focuses on the items that have the highest percentages only (rank the top 4). Don't use decimals. Here's the data {topic_percentages}")
    st.write(heading)

    # Display the chart for total dataset in the main area
    st.plotly_chart(fig)

    # Display the total dataset in the main area
    st.write("## Total Dataset")
    st.write(data)

    # Add a download button for the total dataset
    csv = data.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='myverbs.csv',
        mime='text/csv'
    )
