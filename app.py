import streamlit as st
import pandas as pd
import plotly.express as px
from random import sample
from APIcall import get_chat_completions
from collections import defaultdict
import numpy as np
import plotly.graph_objects as go

# Load the dataset
@st.cache_data
def load_data():
    return pd.read_csv('myverbs.csv')

data = load_data()

tab1, tab2, tab3 = st.tabs(["Recommend", "Summary","Brand Map"])

# Sidebar filters
st.sidebar.title("Filters")

# Radio button to select between Total and Filtered
filter_type = st.sidebar.radio("Select view:", ["Total", "Filtered"])


if filter_type == "Filtered":
        # Obtain unique values for age and brand
        all_age_groups = data['Age'].unique()
        all_brands = data['Brand'].unique()

        # Define filter variables with all options selected by default
        age_filter = st.sidebar.multiselect("Select Age:", all_age_groups, all_age_groups)
        brand_filter = st.sidebar.multiselect("Select Brand:", all_brands, all_brands)

        # Apply filters
        filtered_data = data[(data['Age'].isin(age_filter)) & (data['Brand'].isin(brand_filter))]

        # Calculate topic percentages using filtered data
        topics = filtered_data.columns[1:13]
        topic_percentages = {}
        topic_samples = {}
        for topic in topics:
            topic_percentages[topic] = round((filtered_data[topic] == '✓').sum() / len(filtered_data) * 100, 4)
            positive_indices = filtered_data.index[filtered_data[topic] == '✓'].tolist()
            sample_size = min(3, len(positive_indices))
            topic_samples[topic] = sample(filtered_data.loc[positive_indices, 'text'].tolist(), sample_size)

        # Create a chart for topic percentages using filtered data
        st.write("## Topic Percentages")
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
        heading = get_chat_completions(f"Summarise the top topics in two sentences, in the format X, Y, and Z are the top 5 cited themes, accounting for x% of the total mentions(no decimals). Here's the data {topic_percentages}. Omit the 'Other' mentions from your heading as they aren't meaningful.")
        st.write(heading)

        # Display the chart in the main area
        st.plotly_chart(fig)

        # Display the filtered dataset in a separate tab in the sidebar
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
        topics = data.columns[1:13]
        topic_percentages = {}
        topic_samples = {}
        for topic in topics:
            topic_percentages[topic] = round((data[topic] == '✓').sum() / len(data) * 100, 4)
            positive_indices = data.index[data[topic] == '✓'].tolist()
            sample_size = min(3, len(positive_indices))
            topic_samples[topic] = sample(data.loc[positive_indices, 'text'].tolist(), sample_size)

        # Create a chart for topic percentages for total dataset
        st.write("## Topic Percentages (Total)")
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
        heading = get_chat_completions(f"Summarise the top topics in two sentences, in the format X, Y, and Z are the top 5 cited themes, accounting for x% of the total mentions (no decimals). Here's the data {topic_percentages}. Don't comment on the 'Other' mentions.")
        st.write(heading)

        # Display the chart for total dataset in the main area
        st.plotly_chart(fig)

        # Display the total dataset in a separate tab in the sidebar
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

with tab2:
    st.write("## Summary by Age Group")



    # Grouping data by age
    age_groups = data.groupby('Age')

    # Initialize dictionaries to store results for each age group
    age_group_topic_percentages = defaultdict(dict)
    age_group_topic_samples = defaultdict(dict)

    for age, age_group_data in age_groups:
        # Filtering data for the current age group
        filtered_data = age_group_data
        
        # Perform the analysis for each topic
        for topic in topics:
            topic_percentages = round((filtered_data[topic] == '✓').sum() / len(filtered_data) * 100, 4)
            positive_indices = filtered_data.index[filtered_data[topic] == '✓'].tolist()
            sample_size = min(3, len(positive_indices))
            topic_samples = sample(filtered_data.loc[positive_indices, 'text'].tolist(), sample_size)
            
            # Storing results for each topic in the current age group
            age_group_topic_percentages[age][topic] = topic_percentages
            age_group_topic_samples[age][topic] = topic_samples

        
    
    @st.cache_data()
    def get_age_summary(prompt):
        summary = get_chat_completions(prompt)
        return summary
    
    age_summary = get_age_summary(f"Summarise any interesting differences by age within a single paragraph, focusing on the percentages of the total mentions (no decimals). Here's the data {age_group_topic_percentages}. Don't comment on the 'Other' mentions. And use a direct market research style, e.g. 'Over 55s over index on X, Y, and Z, accounting for x% of the total mentions. Under 25s under index on A, B, and C, accounting for y% of the total mentions'.")
    
    st.write(age_summary)

    st.write("## Summary by Brand")

    # Grouping data by brand
    brand_groups = data.groupby('Brand')

    # Initialize dictionaries to store results for each brand group
    brand_group_topic_percentages = defaultdict(dict)
    brand_group_topic_samples = defaultdict(dict)

    for brand, brand_group_data in brand_groups:
        # Filtering data for the current brand group
        filtered_data = brand_group_data
        
        # Perform the analysis for each topic
        for topic in topics:
            topic_percentages = round((filtered_data[topic] == '✓').sum() / len(filtered_data) * 100, 4)
            positive_indices = filtered_data.index[filtered_data[topic] == '✓'].tolist()
            sample_size = min(3, len(positive_indices))
            topic_samples = sample(filtered_data.loc[positive_indices, 'text'].tolist(), sample_size)
            
            # Storing results for each topic in the current brand group
            brand_group_topic_percentages[brand][topic] = topic_percentages
            brand_group_topic_samples[brand][topic] = topic_samples

    # Create a summary for brand groups
    
    @st.cache_data()
    def get_brand_summary(prompt):
        summary = get_chat_completions(prompt)
        return summary
    
    
    brand_summary = get_brand_summary(f"Summarise any intereseting differences by brand within a single paragraph, focusing on percentages of the total mentions (no decimals). Here's the data {brand_group_topic_percentages}. Don't comment on the 'Other' mentions.And use a direct market reseaarch style, e.g. 'Brand(s) A over index on X, Y, and Z, accounting for x% of the total mentions. Brand C under index on A, B, and C, accounting for y% of the total mentions'")    
    st.write(brand_summary)


with tab3:
    st.write("## Relative difference by Brand (PCA)")
    
    title = '**Experimental - need higher base size to validate & compare to STM**'
    df = pd.read_csv("coordinatesPD.csv")


# Define function to create scatter plot
    def create_scatter_plot(df, title):
        # Extract data
        x = df['Dim 1']
        y = df['Dim 2']
        labels = df.iloc[:, 0]  # Extract labels from the first unnamed column

        # Add jitter to x-coordinates for age categories
        jitter_amount = 0.02
        brand_indices = [0, 1, 2, 3, 4, 5]  # Assuming brand categories are the first 6 rows
        x[brand_indices] = x[brand_indices] + np.random.uniform(-jitter_amount, jitter_amount, len(brand_indices))

        # Create scatter plot
        fig = go.Figure()

        # Add markers for all categories
        fig.add_trace(go.Scatter(x=x, y=y, mode='markers', text=labels,
                                marker=dict(color=['red' if i in brand_indices else 'blue' for i in range(len(x))], size=10)))

        # Add annotations for all categories except "Brands"
        for i, txt in enumerate(labels):
            if i not in brand_indices:
                y_coord = y[i] - 0.03 - (i % 5) * 0.01  # Adjust y-coordinate to space out the labels
                fig.add_annotation(x=x[i], y=y_coord, text=txt,
                                showarrow=False, font=dict(color='blue', size=10))

        # Add annotations for "Aged_" values with leader lines
        aged_labels = [labels[i] for i in brand_indices]
        for i, txt in enumerate(aged_labels):
            fig.add_annotation(x=x[brand_indices[i]], y=y[brand_indices[i]]+0.03, text=txt,
                            showarrow=True, arrowhead=1, ax=0, ay=-20, arrowwidth=1, arrowcolor='red', font=dict(color='red', size=10))

        # Add vertical line through the X axis
        fig.add_shape(type="line", x0=0.2, y0=-0.4, x1=0.2, y1=0.75,
                    line=dict(color="lightgrey", width=1))

        # Add horizontal line through the Y axis
        fig.add_shape(type="line", x0=-1, y0=0, x1=1, y1=0,
                    line=dict(color="lightgrey", width=1))

        # Calculate dynamic axis range
        x_range = [x.min() - 0.1, x.max() + 0.1]
        y_range = [y.min() - 0.1, y.max() + 0.1]

        # Update layout with dynamic axis range
        fig.update_layout(title=title,
                        xaxis_title='Dimension 1',
                        yaxis_title='Dimension 2',
                        xaxis=dict(showline=True, linecolor='lightgrey', zeroline=False, range=x_range),
                        yaxis=dict(showline=True, linecolor='lightgrey', zeroline=False, range=y_range),
                        plot_bgcolor='white',  # Set background color to white
                        height=700)  # Adjust height here
        return fig


    # Create and display scatter plot
    fig = create_scatter_plot(df, title)
    st.plotly_chart(fig)