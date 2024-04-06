import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import millify as mf
import plotly.colors as pc


st.set_page_config(page_title="Superstore Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded")

# Load data
@st.cache_data
def load_data():
    data = pd.read_csv('data.csv', parse_dates=['Order Date', 'Ship Date'], dayfirst=True) # Specify date formats
    data['Ship Date'] = data['Ship Date'] + pd.DateOffset(years=2)
    data['Year'] = data['Order Date'].dt.year
    data['Days to Ship'] = (data['Ship Date'] - data['Order Date']).dt.days
    return data.dropna()

data = load_data()
print(data)

#main area bckgrnd
css_style = """
<style>
    /* Targeting the root HTML element inside Streamlit's main content area */
    .stApp {
        background-color: ##000000 !important;
    }
</style>
"""

st.markdown(css_style, unsafe_allow_html=True)

custom_css = """
<style>
/* Target the sidebar */
.st-bc {
    background-color: #6885c3; /* Change background color to a light blue */
    border-radius: 3px; /* Add border radius for rounded corners */
    border: 0px solid #8888FF; /* Add border with a lighter shade of blue */
}

/* Target the selectbox */
.st-bb {
    border-color: #FFD700; /* Change border color to gold */
    border-width: 0px; /* Change border width */
    border-radius: 8px; /* Add border radius for rounded corners */
    color: #FFFFFF; /* Change text color to white for contrast */
}

/* Target the slider */
.st-ei {
    background-color: #32CD32; /* Change background color to lime green */
    border-radius: 15px; /* Add border radius for rounded corners */
    border: 2px solid #98FB98; /* Add border with a paler green */
}
</style>
"""

css = """
<style>
    .main .block-container {
        background-color: #000000; /* Ensure the main area keeps a black background */
    }
</style>
"""

# Display custom CSS
st.markdown(custom_css + css, unsafe_allow_html=True)

    
# Sidebar
logo_path ="images.jpg"
st.sidebar.image(logo_path, use_column_width=True)

        
color_theme_list = ['inferno', 'blues', 'cividis', 'greens', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
selected_color_theme = st.sidebar.selectbox('Select a color theme', color_theme_list)
st.sidebar.title("Please filter") 
years = sorted(data['Year'].unique().tolist())
years.insert(0, 'All')
selected_year = st.sidebar.selectbox("Select Year", years)

#itt találtam egy ilyen megoldást is
selected_state = st.sidebar.selectbox("Select State", ['All'] + sorted(data['State'].unique().tolist()))
selected_city = st.sidebar.selectbox("Select City", ['All'] + sorted(data['City'].unique().tolist()))
selected_category = st.sidebar.selectbox("Select Category", ['All'] + sorted(data['Category'].unique().tolist()))
selected_subcategory = st.sidebar.selectbox("Select Subcategory", ['All'] + sorted(data['Sub-Category'].unique().tolist()))
selected_discount = st.sidebar.slider("Select Discount", min_value=0.0, max_value=1.0, step=0.05)

# Initialize filtered_data
filtered_data = data

# Filter data based on selected year
if selected_year != 'All':
    filtered_data = data[data['Year'] == int(selected_year)]
else:
    filtered_data = data

if selected_state != 'All':
    filtered_data = filtered_data[filtered_data['State'] == selected_state]
if selected_city != 'All':
    filtered_data = filtered_data[filtered_data['City'] == selected_city]
if selected_category != 'All':
    filtered_data = filtered_data[filtered_data['Category'] == selected_category]
if selected_subcategory != 'All':
    filtered_data = filtered_data[filtered_data['Sub-Category'] == selected_subcategory]
filtered_data = filtered_data[filtered_data['Discount'] >= selected_discount]

def get_colors_from_scale(scale_name, num_colors):
    colors = pc.sample_colorscale(scale_name, num_colors *  2)
    return colors[:num_colors]

# Summary Section
#st.title("Superstores")

title = """
<div style="text-align: center; color: White; font-size: 62px;"><strong>Superstore Sales 2023</strong></div>
"""
st.markdown(title, unsafe_allow_html=True)

st.header("Summary Section")
st.divider()
total_sales = mf.millify(filtered_data['Sales'].sum(), 1)
total_profit = mf.millify(filtered_data['Profit'].sum(),1)
col1, col2, col3 = st.columns(3)
st.divider()
distinct_orders = filtered_data['Order ID'].nunique()
col1.metric("Total Sales", f"${total_sales}")
col2.metric("Total Profit", f"${total_profit}")
col3.metric("Distinct Orders", f"{distinct_orders} orders")


col1, col2 = st.columns([0.5 , 0.5])
# Top 10 Products by Sales
col1.header("Top  10 Products by Sales")
top_10_sales = filtered_data.groupby('Product Name')['Sales'].sum().nlargest(10).reset_index()
top_10_sales = top_10_sales[::-1]
fig_sales = px.bar(top_10_sales, x='Sales', y='Product Name', title='Top  10 Products by Sales', orientation='h', text='Product Name', color='Sales', color_continuous_scale=selected_color_theme)
fig_sales.update_traces(textfont_size=200, textangle=0, textposition="inside", insidetextanchor="start") # y tengely feliratait balra rendezve a bar charton jelenít meg
fig_sales.update_yaxes(tickvals=[], showticklabels=False)  #eltávolítja az y tengely feliratát
col1.plotly_chart(fig_sales, use_container_width= True)

# Top 10 Products by Profit
col2.header("Top  10 Products by Profit")
top_10_profit = filtered_data.groupby('Product Name')['Profit'].sum().nlargest(10).reset_index()
top_10_profit = top_10_profit[::-1]
fig_profit = px.bar(top_10_profit,  x='Profit', y='Product Name', title='Top  10 Products by Profit', orientation='h', text='Product Name', color='Profit', color_continuous_scale=selected_color_theme)
fig_profit.update_traces(textfont_size=200, textangle=0, textposition="inside", insidetextanchor="start")
fig_profit.update_yaxes(tickvals=[], showticklabels=False)
col2.plotly_chart(fig_profit, use_container_width= True)

col1, col2 = st.columns(2)
# Average Days to Ship an Order
col1.header("Average Days to Ship an Order")
avg_days_to_ship = filtered_data.groupby('Year')['Days to Ship'].mean().reset_index()
fig_avg_days_to_ship = px.line(avg_days_to_ship, x='Year', y='Days to Ship', title='Average Days to Ship an Order')
fig_avg_days_to_ship.update_xaxes(tickmode='linear', tickvals=avg_days_to_ship['Year'].unique())
col1.plotly_chart(fig_avg_days_to_ship)

# Sales Trends by Product Category
col2.header("Sales Trends by Product Category")
sales_trends = filtered_data.groupby(['Year', 'Category'])['Sales'].sum().reset_index()

# Get a list of colors from the selected color scale
num_categories = len(sales_trends['Category'].unique())
colors = get_colors_from_scale(selected_color_theme, num_categories)

fig_sales_trends = px.bar(sales_trends, x='Year', y='Sales', color='Category', barmode='stack', title='Sales Trends by Product Category', text_auto=True, color_discrete_sequence=colors)
fig_sales_trends.update_layout(legend_title_text='Product Category')
col2.plotly_chart(fig_sales_trends)

# Heatmap for Average Days to Ship across Years and Product Categories
col1.header("Heatmap for Average Days to Ship")
heatmap_data = filtered_data.groupby(['Year', 'Category'])['Days to Ship'].mean().reset_index()
fig_heatmap = px.imshow(heatmap_data.pivot(index='Category', columns='Year', values='Days to Ship'),
                        labels=dict(x="Year", y="Product Category", color="Avg Days to Ship"),
                        x=heatmap_data['Year'].unique().tolist(),
                        y=heatmap_data['Category'].unique().tolist(),
                        color_continuous_scale=selected_color_theme)
col1.plotly_chart(fig_heatmap)

# Donut Chart for Sales Distribution by Product Category
col2.header("Sales Distribution by Product Category")
sales_distribution = filtered_data.groupby('Category')['Sales'].sum().reset_index()

# Get a list of colors from the selected color scale
num_categories = len(sales_distribution['Category'].unique())
colors = get_colors_from_scale(selected_color_theme, num_categories)

fig_donut = px.pie(sales_distribution, values='Sales', names='Category', title='Sales Distribution by Product Category',
                   hole=0.5, color_discrete_sequence=colors)
fig_donut.update_layout(legend_title_text='Product Category')
col2.plotly_chart(fig_donut)


# Scatter Plot for Sales vs Profit
st.header("Scatter Plot for Sales vs Profit")

# Get a list of colors from the selected color scale
num_categories = len(filtered_data['Category'].unique())
colors = get_colors_from_scale(selected_color_theme, num_categories)

fig_scatter = px.scatter(filtered_data, x='Sales', y='Profit', color='Category', title='Sales vs Profit', color_discrete_sequence=colors)
fig_scatter.update_layout(legend_title_text='Product Category')
st.plotly_chart(fig_scatter)

#filtered data spreadsheet
columns_to_display = ['City', 'Category', 'Sales', 'Profit', 'Year']

selected_data = filtered_data[columns_to_display]

# Displaying the selected columns in the dataframe
st.header("Filtered Data Spreadsheet (main information)")
st.dataframe(selected_data, use_container_width=True, height=400)

#tábla alján a top profitok
st.header ("Top profit by cities")
top20 = data.groupby('City')['Profit'].sum().reset_index().sort_values(by='Profit', ascending=False).head(20)
st.dataframe(top20)