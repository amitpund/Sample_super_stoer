import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

# Streamlit page configuration
st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:", layout="wide")

# Title and styling
st.title(":bar_chart: Sample Superstore EDA")
st.markdown(
    '<style>div.block-container{padding-top:1rem;}</style>',
    unsafe_allow_html=True
)

# File uploader
f1 = st.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xlsx", "xls"])
if f1 is not None:
    filename = f1.name
    st.write(f"File uploaded: {filename}")
    if filename.endswith(('.csv', '.txt')):
        df = pd.read_csv(f1, encoding="ISO-8859-1")
    elif filename.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(f1, engine='openpyxl')
else:
    # Default file loading (use local file if not uploaded)
    st.warning("Using default dataset.")
    # Update the default file path as needed
    default_path = "Superstore.csv"
    if os.path.exists(default_path):
        df = pd.read_csv(default_path, encoding="ISO-8859-1")
    else:
        st.error("Default dataset not found!")
        st.stop()

# Ensure "Order Date" is datetime
if "Order Date" in df.columns:
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
    df.dropna(subset=["Order Date"], inplace=True)
else:
    st.error("The dataset does not contain an 'Order Date' column.")
    st.stop()

# Date range selection
col1, col2 = st.columns((2))
startDate = df["Order Date"].min()
endDate = df["Order Date"].max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# Filter data based on date range
if date1 > date2:
    st.error("Start Date must be before End Date.")
else:
    df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)]
    st.success(f"Data filtered from {date1.date()} to {date2.date()}.")

# Sidebar filters
st.sidebar.header("Choose Your Filters: ")

# Region filter
regions = st.sidebar.multiselect("Pick Your Region(s):", df["Region"].unique())
if regions:
    df = df[df["Region"].isin(regions)]

# State filter
states = st.sidebar.multiselect("Pick Your State(s):", df["State"].unique())
if states:
    df = df[df["State"].isin(states)]

# City filter
cities = st.sidebar.multiselect("Pick Your City(s):", df["City"].unique())
if cities:
    df = df[df["City"].isin(cities)]

# Display filtered data
st.subheader("Filtered Data")
st.write(f"Data contains {df.shape[0]} rows and {df.shape[1]} columns after filtering.")
st.dataframe(df)

# Category-wise sales
category_df = df.groupby(by=["Category"], as_index=False)["Sales"].sum()

# Visualizations
with col1:
    st.subheader("Category-Wise Sales")
    fig = px.bar(
        category_df,
        x="Category",
        y="Sales",
        text=category_df["Sales"].apply(lambda x: f"${x:,.2f}"),  # Format as currency
        template="seaborn",
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Region-Wise Sales")
    fig = px.pie(
        df,
        values="Sales",
        names="Region",
        hole=0.5,
        title="Sales Distribution by Region",
    )
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns((2))

# Function to generate download button for dataframes
def download_button(df, file_name, button_label):
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=button_label,
        data=csv_data,
        file_name=file_name,
        mime="text/csv",
        help="Click to download the data as a CSV file"
    )

# Category data
with cl1:
    with st.expander("Category View Data"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        download_button(category_df, "Category.csv", "Download Category Data")

# Region data
with cl2:
    with st.expander("Region View Data"):
        region_df = df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region_df.style.background_gradient(cmap="Blues"))
        download_button(region_df, "Region.csv", "Download Region Data")

# Time Series Analysis
df["month_year"] = df["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")

linechart = df.groupby(df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum().reset_index()
fig2 = px.line(
    linechart,
    x="month_year",
    y="Sales",
    labels={"Sales": "Amount", "month_year": "Month-Year"},
    height=500,
    width=1000,
    template="gridon",
)
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of Time Series:"):
    st.write(linechart.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button("Download Data", data=csv, file_name="TimeSeries.csv", mime="text/csv")

# Treemap Visualization
st.subheader("Hierarchical View of Sales Using Treemap")
fig3 = px.treemap(
    df,
    path=["Region", "Category", "Sub-Category"],
    values="Sales",
    hover_data=["Sales"],
    color="Sub-Category",
)
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

# Pie Charts
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Segment-Wise Sales")
    segment_data = df.groupby("Segment", as_index=False)["Sales"].sum()
    fig = px.pie(
        segment_data,
        values="Sales",
        names="Segment",
        template="plotly_dark",
    )
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Category-Wise Sales")
    category_data = df.groupby("Category", as_index=False)["Sales"].sum()
    fig = px.pie(
        category_data,
        values="Sales",
        names="Category",
        template="gridon",
    )
    st.plotly_chart(fig, use_container_width=True)

# Summary Table
import plotly.figure_factory as ff
st.subheader(":point_right: Month-Wise Sub-Category Sales Summary")
with st.expander("Summary Table"):
    summary_df = df.head(5)[["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(summary_df, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month-Wise Sub-Category Table")
    df["month"] = df["Order Date"].dt.month_name()
    sub_category_pivot = pd.pivot_table(
        data=df, values="Sales", index=["Sub-Category"], columns="month", aggfunc="sum"
    )
    st.write(sub_category_pivot.style.background_gradient(cmap="Blues"))

# Scatter Plot
st.subheader("Relationship Between Sales and Profits Using Scatter Plot")
fig = px.scatter(
    df,
    x="Sales",
    y="Profit",
    size="Quantity",
    title="Scatter Plot of Sales vs. Profit",
)
fig.update_layout(
    title_font=dict(size=20),
    xaxis_title="Sales",
    yaxis_title="Profit",
    height=500,
    width=900,
)
st.plotly_chart(fig, use_container_width=True)

with st.expander("view Data"):
    st.write(df.iloc[:500,1:20:2].style.background_gradient(cmap = "Oranges"))

# Download the original dataset
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Data",
    data=csv,
    file_name="Data.csv",
    mime="text/csv"
)

# Footer section
st.markdown(
    """
    <hr style='border:1px solid #000;'>
    <div style='text-align:center;'>
        <strong>Developed by Amit Pund</strong>
    </div>
    """,
    unsafe_allow_html=True
)

