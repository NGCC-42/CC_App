import pandas as pd
import streamlit as st
import plotly.express as px
#from PIL import Image
import numpy as np
#from collections import ChainMap, defaultdict
#import difflib
import altair as alt
import matplotlib.pyplot as plt
#from operator import itemgetter
from datetime import datetime, timedelta
import openpyxl
import streamlit_shadcn_ui as ui
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu
#from fpdf import FPDF
#import base64

### SET WEB APP CONFIGURATIONS
st.set_page_config(page_title='Club Cannon Database', 
		   page_icon='club-cannon-icon-black.png',
                   layout='wide',
		   initial_sidebar_state='collapsed')

### SET HEADER IMAGE
#image = 'club-cannon-logo-bbb.png'
col1, col2, col3 = st.columns(3)

col2.image('logo.png', 
        use_container_width=True)

st.header('')

st.divider()


### LOAD FILES
sod_ss = 'SOD 1.22.25.xlsx'

hist_ss = 'CC Historical Sales.xlsx'

hsd_ss = 'HSD 11.8.24.xlsx'

quote_ss = 'Quote Report 10.23.24.xlsx'

#sales_sum_csv = 'Total Summary-2022 - Present.csv'

shipstat_ss_24 = '2024 SR 11.01.24.xlsx'
shipstat_ss_23 = '2023 SR.xlsx'

#prod_sales = 'Product Sales Data.xlsx'

wholesale_cust = 'wholesale_customers.xlsx'

cogs_ss = 'COGS 1.1.23 - 1.2.25.xlsx'

### LOAD SHEETS FROM PRODUCT SUMMARY

acc_2024 = 'Accessories 2024'
cntl_2024 = 'Controllers Sales 2024'
jet_2024 = 'Jet Sales 2024'
hh_2024 = 'Handheld Sales 2024'
hose_2024 = 'Hose Sales 2024'

acc_2023 = 'Accessories 2023'
cntl_2023 = 'Controllers Sales 2023'
jet_2023 = 'Jet Sales 2023'
hh_2023 = 'Handheld Sales 2023'
hose_2023 = 'Hose Sales 2023'

### LOAD SHEETS FROM SALES SUMMARY

total_sum = 'Total Summary'

### LOAD DATAFRAME(S) (RETAIN FORMATTING IN XLSX)

@st.cache_data
def create_dataframe(ss):

	df = pd.read_excel(ss,
					  dtype=object,
					  header=0)
	return df


df = create_dataframe(sod_ss)

df_hist = create_dataframe(hist_ss)
df_hist.fillna(0, inplace=True)

df_quotes = create_dataframe(quote_ss)

df_shipstat_24 = create_dataframe(shipstat_ss_24)

df_shipstat_23 = create_dataframe(shipstat_ss_23)

df_hsd = create_dataframe(hsd_ss)

df_wholesale = create_dataframe(wholesale_cust)

df_cogs = create_dataframe(cogs_ss)

@st.cache_data
def gen_ws_list():
    wholesale_list = []
    for ws in df_wholesale.name:
        wholesale_list.append(ws)
    return wholesale_list

wholesale_list = gen_ws_list()

### STRIP UNUSED COLUMN ###

df = df.drop(['Ordered Week', 'Customer Item Name'], axis=1)

### RENAME DF COLUMNS FOR SIMPLICITY ###

df_quotes.rename(columns={
    'Number': 'number',
    'Customer': 'customer',
    'CustomerContact': 'contact',
    'TotalInPrimaryCurrency': 'total',
    'CreatedUtc': 'date_created',
    'Status': 'status',
    'ClosedDate': 'closed_date'}, 
    inplace=True)


quote_cust_list = df_quotes['customer'].unique().tolist()

df.rename(columns={
    'Sales Order': 'sales_order',
    'Customer': 'customer',
    'Sales Person': 'channel',
    'Ordered Date': 'order_date',
    'Ordered Month': 'order_month',
    'Sales Order Status': 'status',
    'Line Item Name': 'item_sku',
    'Line Item': 'line_item',
    'Order Quantity': 'quantity',
    'Total Line Item $': 'total_line_item_spend',
    'Ordered Year': 'ordered_year'},
    inplace=True)

df.order_date = pd.to_datetime(df.order_date).dt.date

df_hsd.rename(columns={
    'Sales Order': 'sales_order',
    'Customer PO': 'po',
    'Customer': 'customer',
    'Item Name': 'item',
    'Item Description': 'description',
    'Quantity Ordered': 'quantity',
    'Value Shipped': 'value',
    'Shipped Date': 'date',
    'Shipped By': 'channel'},
     inplace=True)

df_shipstat_24.rename(columns={
                    'Ship Date':'shipdate',
                    'Recipient':'customer',
                    'Order #':'order_number',
                    'Provider':'provider',
                    'Service':'service',
                    'Items':'items',
                    'Paid':'cust_cost',
                    'oz':'weight',
                    '+/-':'variance'},
                    inplace=True)

df_shipstat_23.rename(columns={
                    'Ship Date':'shipdate',
                    'Recipient':'customer',
                    'Order #':'order_number',
                    'Provider':'provider',
                    'Service':'service',
                    'Items':'items',
                    'Paid':'cust_cost',
                    'oz':'weight',
                    '+/-':'variance'},
                    inplace=True)  

### DEFINE A FUNCTION TO CORRECT NAME DISCRPANCIES IN SOD

def fix_names(df):

    df.replace('Tim Doyle', 'Timothy Doyle', inplace=True)
    df.replace('ESTEFANIA URBAN', 'Estefania Urban', inplace=True)
    df.replace('estefania urban', 'Estefania Urban', inplace=True)
    df.replace('JR Torres', 'Jorge Torres', inplace=True)
    df.replace('Saul Dominguez', 'Coco Bongo', inplace=True)
    df.replace('Paul Souza', 'Pyro Spectaculars Industries, Inc. ', inplace=True)
    df.replace('CHRISTOPHER BARTOSIK', 'Christopher Bartosik', inplace=True)
    df.replace('Jon Ballog', 'Blair Entertainment / Pearl AV', inplace=True)
    df.replace('Jack Bermo', 'Jack Bermeo', inplace=True)
    df.replace('Tonz of Fun', 'Eric Walker', inplace=True)
    df.replace('Travis S. Johnson', 'Travis Johnson', inplace=True)
    df.replace('Yang Gao', 'Nebula NY', inplace=True)

    return df

df = fix_names(df)

### CREATE A LIST OF UNIQUE CUSTOMERS ###
unique_customer_list = df.customer.unique().tolist()
hist_customer_list = df_hist.customer.unique().tolist()
master_customer_list = list(set(unique_customer_list) | set(hist_customer_list))

### DEFINE FUNCTION TO CREATE PRODUCT DATAFRAME FROM EXCEL SPREADSHEET ###

@st.cache_data
def gen_product_df_from_excel(ss, sheet_name, cols=None):

	if cols == None:
		
	    df_product_year = pd.read_excel(ss,
	                                   names=['Product', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total'],
	                                   sheet_name=sheet_name,
		                               dtype=object,
	                                   header=1)
	else:
		
		df_product_year = pd.read_excel(ss,
									   usecols=cols,
									   names=['Product', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total'],
									   sheet_name=sheet_name,
									   dtype=object,
									   header=1)
	return df_product_year




### READ IN SALES SUMMARY CSV ###
@st.cache_data
def create_dataframe_csv(file):
	df = pd.read_csv(file, 
					usecols=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
	return df


### CREATE DATE LISTS ###

months = ['All', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
months_x = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
years = ['2022', '2023', '2024']


   
    
### DEFINE FUNCTION TO RENAME COLUMNS FOR CHART AXIS SORTING ###
@st.cache_data
def ordered_months(df):
    
    idx = 1
    temp_dict = {}
    for month in months_x:
        temp_dict[month] = str(idx)+ ' ' + month
        idx *= 10
    new_df = df.rename(columns = temp_dict)
    return new_df

def rev_ordered_months(df):
 
    idx_char = 1
    temp_dict = {}
    
    for month in df.head(0):
        if month == 'Product':
            pass
        else:
            temp_dict[month] = month[idx_char:]
            idx_char += 1

    rev_df = df.rename(columns = temp_dict)
    return rev_df


def format_for_chart_hh(data_dict):
    temp_dict = {'Years': [], 'Handheld Sales': []}

    for year, sales in data_dict.items():
        temp_dict['Years'].append(year)
              
        temp_dict['Handheld Sales'].append(sales)
                
    df = pd.DataFrame(temp_dict)
    
    return df

    

def plot_bar_chart_hh(df):
    st.write(alt.Chart(df).mark_bar().encode(
        x=alt.X('Years', sort=None).title('Year'),
        y='Handheld Sales',
    ).properties(height=800, width=1150).configure_mark(
        color='limegreen'
    ))



### DEFINE A FUNCTION TO CONVERT - SERIES --> DICT --> DATAFRAME ###

def format_for_chart(series):
    
    temp_dict = {'Months': months_x,
                'Units Sold': []}
    
    for month in series[1:]:
        if len(temp_dict['Units Sold']) >= 12:
            pass
        else:
            temp_dict['Units Sold'].append(month)
    df = pd.DataFrame(temp_dict)
    
    return df

#st.write(format_for_chart(df_cntl23_unt.iloc[0]))


### SCRIPT TO PLOT BAR GRAPH FOR PRODUCT SALES ###

def plot_bar_chart(df):
    st.write(alt.Chart(df).mark_bar().encode(
        x=alt.X('Months', sort=None).title('Month'),
        y='Units Sold',
    ).properties(height=500, width=750).configure_mark(
        color='limegreen'
    ))


def display_daily_plot(month, years=['All']):
    
    daily23, daily24, daily25 = daily_sales(month)
    col1.write(daily23)

    x = [i for i in range(len(daily24))]

    fig, ax = plt.subplots()

    if years == ['All']:
    
        ax.plot(x, daily23, label='2023', color='darkgreen', linewidth=2)
        ax.plot(x, daily24, label='2024', color='white', linewidth=2)
        ax.plot(x, daily25, label='2025', color='limegreen', linewidth=2)
        ax.set_facecolor('#000000')
        fig.set_facecolor('#000000')
        plt.yticks([1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000])
        plt.tick_params(axis='x', colors='white')
        plt.tick_params(axis='y', colors='white')
        plt.ylim(0, 20000)
        #plt.fill_between(x, daily23, color='darkgreen')
        #plt.fill_between(x, daily24, color='white', alpha=0.7)
        #plt.fill_between(x, daily25, color='limegreen')
        #plt.title('Annual Comparison', color='green')
        plt.figure(figsize=(10,10))
    
        fig.legend()
        
        col2.pyplot(fig)

    elif years == ['2025']:
        
        ax.plot(x, daily25, label='2025', color='limegreen', linewidth=2)
        ax.set_facecolor('#000000')
        fig.set_facecolor('#000000')
        plt.yticks([1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000])
   
        plt.tick_params(axis='x', colors='white')
        plt.tick_params(axis='y', colors='white')
        plt.ylim(0, 20000)
        plt.fill_between(x, daily25, color='limegreen')
        #plt.title('Annual Comparison', color='green')
        plt.figure(figsize=(10,10))
    
        #fig.legend()

        col2.pyplot(fig)
        
    elif years == ['2024']:
        
        ax.plot(x, daily24, label='2024', color='limegreen', linewidth=2)
        ax.set_facecolor('#000000')
        fig.set_facecolor('#000000')
        plt.yticks([1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000])
   
        plt.tick_params(axis='x', colors='white')
        plt.tick_params(axis='y', colors='white')
        plt.ylim(0, 20000)
        plt.fill_between(x, daily24, color='limegreen')
        #plt.title('Annual Comparison', color='green')
        plt.figure(figsize=(10,10))
    
        #fig.legend()

        col2.pyplot(fig)

    elif years == ['2023']:
        
        ax.plot(x, daily23, label='2023', color='limegreen', linewidth=2)
        ax.set_facecolor('#000000')
        fig.set_facecolor('#000000')
        plt.yticks([1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000])
   
        plt.tick_params(axis='x', colors='white')
        plt.tick_params(axis='y', colors='white')
        plt.ylim(0, 20000)
        plt.fill_between(x, daily23, color='limegreen')
        #plt.title('Annual Comparison', color='green')
        plt.figure(figsize=(10,10))
    
        #fig.legend()

        col2.pyplot(fig)
    
    return None

### CREATE AVG FUNCTION ###

def avg_month(dict):
    zero_count = 0
    total = 0
    for key, value in dict.items():
        if value == 0:
            zero_count += 1
        else:
            total += value
    return int(total / (len(dict) - zero_count))
            

### DEFINE FUNCTION TO CREATE DICTIONARY OF PRODUCT REVENUES AND TOTAL REVENUE FOR TYPE OF PRODUCT ###

def revenue_calculator(prod_df):
    
    product_rev_total = {}
    type_rev_total = 0
    
    
    idx = 0
    
    for row in prod_df['Product']:
        product_rev_total[row] = 0
        
        for month in months_x:
            product_rev_total[row] += prod_df[month].iloc[idx]
            type_rev_total += prod_df[month].iloc[idx]
    
        idx += 1    

    return product_rev_total, type_rev_total


### DEFINE FUNCTION TO FIND PRODUCT REVENUE PERCENTAGE OF TOTAL TYPE FROM DICTIONARY ###
@st.cache_data
def product_revenue_share(dict, total):

    percentage_dict = {}
    
    for key, value in dict.items():
        percentage_dict[key] = (value / total) * 100

    return percentage_dict

### DEFINE A FUNCTION TO TAKE PRODUCT SALES DATAFRAME AND RETURN DICTIONARY OF EACH PRODUCTS PERCENTAGE OF REVENUE OF TYPE ###

def percentage_of_revenue(prod_df):

    prod_rev_total, type_rev_total = revenue_calculator(prod_df)

    return product_revenue_share(prod_rev_total, type_rev_total)


### DEFINE A FUNCTION TO CREATE A DATAFRAME FROM DICTIONARY OF REVENUE PERCENTAGES ###
@st.cache_data
def dataframe_from_dict(dict):

    dict_of_lists = {'Products': [], 
                    'Share': []}

    for key, value in dict.items():
        dict_of_lists['Products'].append(key)
        dict_of_lists['Share'].append(value)

    df = pd.DataFrame(dict_of_lists)
    
    return df

### DEFINE A FUNCTION TO COMBINE MULTIPLE YEARS OF PRODUCT REVENUE DATA ###
@st.cache_data
def multiyear_product_revenue(list_of_dfs):

    product_revenue_totals = {}
    type_totals = 0
    
    rev_idx = 0
    
    for dfs in list_of_dfs:
    
        prod_rev, type_rev = revenue_calculator(dfs)
        type_totals += type_rev
        if rev_idx == 0:
            for key, value in prod_rev.items():
                product_revenue_totals[key] = value
        else:
            for key, value in prod_rev.items():
                product_revenue_totals[key] += value
                
        rev_idx += 1

    rev_percent_dict = product_revenue_share(product_revenue_totals, type_totals)
    
    return rev_percent_dict, product_revenue_totals, type_totals


### DEFINE A FUNCTION TO DISPLAY PRODUCT PROFIT DATA ###

def display_profit_data(df, product_selection):

    idx = 0
    for product in df['Product']:
        if product == product_selection:
            st.write('  - BOM Cost w/ Labor & Accessories:   ' + '${:,.2f}'.format(df['Cost'].iloc[idx]))
            st.write('  - Average Price:   ' + '${:,.2f}'.format(df['Avg Price'].iloc[idx]))
            st.write('  - Net Profit / Unit:   ' + '${:,.2f}'.format(df['Net Profit / Unit'].iloc[idx]))
        idx += 1

    return None


### WRITE A FUNCTION TO SORT NAMES BY CLOSEST MATCH TO INPUT ###

def sort_by_match(lst, target_string):

    return sorted(lst, key=lambda x: difflib.SequenceMatcher(None, x.lower(), target_string.lower()).ratio(), reverse=True)

@st.cache_data
def get_sales_orders(customer, dataFrame):

    temp_list = []

    ct = 0
    while df.iloc[idx + ct]['Sales Order'] == df.iloc[idx + ct + 1]['Sales Order']:
        
        temp_list.append(df.iloc[idx + ct]['Line Item Name'] + ' x ' + str(df.iloc[idx + ct]['Order Quantity']))
        ct += 1
            
    temp_dict[df.iloc[idx]['Sales Order']] = temp_list

    return temp_dict

### DEFINE A FUNCTION TO CALCULATE AND DISPLAY CHANGE IN CUSTOMER SPENDING ###
@st.cache_data
def percent_of_change(num1, num2):
    
    delta = num2 - num1
    if num1 == 0:
        perc_change = 100
    else:
        perc_change = (delta / num1) * 100
    if delta > 0:
        v = '+'
    else:
        v = ''

    return '{}{:,.2f}% from last year'.format(v, perc_change)

### MAKE LIST OF PRODUCT TYPES ###

product_types = ['Jets', 'Controllers', 'Hoses', 'Accessories', 'Handhelds']


### DEFINE FUNCTIONS TO CLEAN DATAFRAME FOR PROCESSING ###

@st.cache_data
def clean_df_std(df, row1, row2):

	clean_df = df[row1:row2].fillna(0)

	return clean_df

@st.cache_data
def clean_df_prof(df, row1, row2):

	clean_df = df[row1:row2].fillna(0).rename({'March': 'Cost', 'April': 'Avg Price', 'May': 'Net Profit / Unit', 'June': 'Total Net Profit'}, axis=1).drop(['January', 'February', 'July', 'August', 'September', 'October', 'November', 'December'], axis=1).reset_index()

	return clean_df




### CREATE LISTS OF CATEGORIES FROM DATAFRAME ###

@st.cache_data
def create_product_list(df):
	prod_list = df['Product'].unique().tolist()
	return prod_list



### DEFINE A FUNCTION TO CALCULATE PERCENTAGE OF A TOTAL ###
def percent_of_sales(type1, type2):

    total = type1 + type2
    
    if total == 0:
        return 0
    else:
        answer = (type1 / total) * 100
    
    return answer

### DEFINE A FUNCTION TO RETURN STRING SUM OF DICTIONARY VALUES ###
def sum_of_dict_values(dict):

    total = 0 
    for key, value in dict.items():
        total += value
    
    return '${:,.2f}'.format(total)

### DEFINE A FUNCTION TO CONVERT MONTH STRING TO NUMERICAL ###
def month_to_num(month):

    month_num = '01'

    if month == 'February':
        month_num = '02'
    elif month == 'March':
        month_num = '03'
    elif month == 'April':
        month_num = '04'
    elif month == 'May':
        month_num = '05'
    elif month == 'June':
        month_num = '06'
    elif month == 'July':
        month_num = '07'
    elif month == 'August':
        month_num = '08'
    elif month == 'September':
        month_num = '09'
    elif month == 'October':
        month_num = '10'
    elif month == 'November':
        month_num = '11'
    elif month == 'December':
        month_num = '12'
        
    return month_num

def num_to_month(month_num):

    month = 'January'

    if month_num == 2:
        month = 'February'
    elif month_num == 3:
        month = 'March'
    elif month_num == 4:
        month = 'April'
    elif month_num == 5:
        month = 'May'
    elif month_num == 6:
        month = 'June'
    elif month_num == 7:
        month = 'July'
    elif month_num == 8:
        month = 'August'
    elif month_num == 9:
        month = 'September'
    elif month_num == 10:
        month = 'October'
    elif month_num == 11:
        month = 'November'
    elif month_num == 12:
        month = 'December'

    return month



### SALES CHANNEL TRACKING ###
@st.cache_data
def sales_channel(year, month=['All']):

    website_rev_23 = 0
    fulcrum_rev_23 = 0
    website_rev_24 = 0
    fulcrum_rev_24 = 0
    
    website_rev_dict_23 = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0, '12': 0}
    fulcrum_rev_dict_23 = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0, '12': 0}
    website_rev_dict_24 = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0, '12': 0}
    fulcrum_rev_dict_24 = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0, '12': 0}
    
    idx = 0

    for sale in df.channel:
        
        order_month = df.iloc[idx].order_month[5:7]

        if df.iloc[idx].ordered_year == '2023':
    
            if sale[0] == 'F':
                website_rev_23 += df.iloc[idx].total_line_item_spend
                website_rev_dict_23[order_month] += df.iloc[idx].total_line_item_spend                

            else:
                fulcrum_rev_23 += df.iloc[idx].total_line_item_spend
                fulcrum_rev_dict_23[order_month] += df.iloc[idx].total_line_item_spend
            
        elif df.iloc[idx].ordered_year == '2024':
    
            if sale[0] == 'F':
                website_rev_24 += df.iloc[idx].total_line_item_spend
                website_rev_dict_24[order_month] += df.iloc[idx].total_line_item_spend 

            else:
                fulcrum_rev_24 += df.iloc[idx].total_line_item_spend
                fulcrum_rev_dict_24[order_month] += df.iloc[idx].total_line_item_spend           
            
        idx += 1

    if year == '2023':
        if month == ['All']:
            return website_rev_23, percent_of_sales(website_rev_23, fulcrum_rev_23), fulcrum_rev_23, percent_of_sales(fulcrum_rev_23, website_rev_23)
        else:
            total_web_sales = 0
            total_fulcrum_sales = 0
            for mnth in month:
                total_web_sales += website_rev_dict_23[month_to_num(mnth)]
                total_fulcrum_sales += fulcrum_rev_dict_23[month_to_num(mnth)]
            return total_web_sales, percent_of_sales(total_web_sales, total_fulcrum_sales), total_fulcrum_sales, percent_of_sales(total_fulcrum_sales, total_web_sales)

    elif year == '2024':
        if month == ['All']:
            return website_rev_24, percent_of_sales(website_rev_24, fulcrum_rev_24), fulcrum_rev_24, percent_of_sales(fulcrum_rev_24, website_rev_24)
        else:
            total_web_sales = 0
            total_fulcrum_sales = 0
            for mnth in month:               
                total_web_sales += website_rev_dict_24[month_to_num(mnth)]
                total_fulcrum_sales += fulcrum_rev_dict_24[month_to_num(mnth)]
            return total_web_sales, percent_of_sales(total_web_sales, total_fulcrum_sales), total_fulcrum_sales, percent_of_sales(total_fulcrum_sales, total_web_sales)       
    else:
        return None







### GENERATE SIDEBAR MENU ###
task_select = ''
#task_choice = ''

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #121212;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    task_choice = option_menu(None, ["Dashboard", "Product Reports",  "Customer Details", "Leaderboards", "Quote Reports"], 
        icons=['house', 'projector', 'person-circle', 'trophy', 'shadows'], 
        menu_icon="cast", default_index=0, orientation="vertical",
        styles={
            "container": {"padding": "0!important"},
            "icon": {"color": "limegreen", "font-size": "18px"}, 
            "nav-link": {"color": "white", "font-size": "22px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "limegreen"},
            }
        )


def style_metric_cards(
    background_color: str = "#000000",
    border_size_px: int = 1.5,
    border_color: str = "#00FF00",
    border_radius_px: int = 5,
    border_left_color: str = "#00FF00",
    box_shadow: bool = True,
) -> None:
    """
    Applies a custom style to st.metrics in the page

    Args:
        background_color (str, optional): Background color. Defaults to "#FFF".
        border_size_px (int, optional): Border size in pixels. Defaults to 1.
        border_color (str, optional): Border color. Defaults to "#CCC".
        border_radius_px (int, optional): Border radius in pixels. Defaults to 5.
        border_left_color (str, optional): Borfer left color. Defaults to "#9AD8E1".
        box_shadow (bool, optional): Whether a box shadow is applied. Defaults to True.
    """

    box_shadow_str = (
        "box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;"
        if box_shadow
        else "box-shadow: none !important;"
    )
    st.markdown(
        f"""
        <style>
            div[data-testid="stMetric"],
            div[data-testid="metric-container"] {{
                background-color: {background_color};
                border: {border_size_px}px solid {border_color};
                padding: 5% 1% 5% 5%;
                border-radius: {border_radius_px}px;
                border-left: 0.5rem solid {border_left_color} !important;
                {box_shadow_str}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )



bom_cost_jet = {'Pro Jet': 290.86, 'Quad Jet': 641.43, 'Micro Jet': 243.57, 'Cryo Clamp': 166.05}
bom_cost_control = {'The Button': 141.07, 'Shostarter': 339.42, 'Shomaster': 667.12}
bom_cost_hh = {'8FT - No Case': 143.62, '8FT - Travel Case': 219.06, '15FT - No Case': 153.84, '15FT - Travel Case': 231.01}
bom_cost_hose = {'2FT MFD': 20.08, '3.5FT MFD': 22.50, '5FT MFD': 24.25, '5FT STD': 31.94, '5FT DSY': 31.84, '5FT EXT': 33.24, '8FT STD': 32.42, '8FT DSY': 34.52, '8FT EXT': 34.82, '15FT STD': 43.55, '15FT DSY': 46.47, '15FT EXT': 46.77, '25FT STD': 59.22, '25FT DSY': 61.87, '25FT EXT': 62.17, '35FT STD': 79.22, '35FT DSY': 81.32, '35FT EXT': 81.62, '50FT STD': 103.57, '50FT EXT': 105.97, '100FT STD': 183.39}
bom_cost_acc = {'CC-AC-CCL': 29.17, 'CC-AC-CTS': 6.70, 'CC-F-DCHA': 7.15, 'CC-F-HEA': 6.86, 'CC-AC-RAA': 11.94, 'CC-AC-4PM': 48.12, 'CC-F-MFDCGAJIC': 7.83, ' CC-AC-CGAJIC-SET': 5.16, 'CC-CTC-20': 10.92, 'CC-CTC-50': 19.36, 'CC-AC-TC': 89.46, 'CC-VV-KIT': 29.28, 
                'CC-RC-2430': 847, 'CC-AC-LA2': 248.10, 'CC-SW-05': 157.24, 'CC-NPTC-06-STD': 10.99, 'CC-NPTC-10-DSY': 18.90, 'CC-NPTC-15-DSY': 27.08, 'CC-NPTC-25-DSY': 39.37}
bom_cost_mfx = {'MagicFX Commander': 355.73, 'Magic FX Smoke Bubble Blaster': 3328.63, 'MagicFX ARM SFX SAFETY TERMINATOR': 12.50, 'MagicFX Device Updater': 38.37, 'MagicFX PSYCO2JET': 1158.63, 'MagicFX Red Button': 61.23, 'MagicFX Replacement Keys': 7.27, 
                'MagicFX SFX Safety ARM Controller': 616.13, 'MagicFX SPARXTAR': 1623.63, 'MagicFX Sparxtar powder': 19.84, 'MagicFX StadiumBlaster': 2893.56, 'MagicFX StadiumBlower': 2858.90, 'MagicFX StadiumShot III': 2321.13, 'MagicFX SuperBlaster II': 1468.63, 
                'MagicFX Swirl Fan II': 1406.63, 'MagicFX Switchpack II': 448.73, 'MFX-AC-SBRV': 328.68, 'MFX-E2J-230': 3282.40, 'MFX-E2J-2LFA': 97, 'MFX-E2J-5LFCB': 128, 'MFX-E2J-F-ID': 30.45, 'MFX-E2J-F-OD': 37.92, 'MFX-E2J-FC': 673.48, 'MFX-E2J-FEH-1M': 46, 'MFX-E2J-FEH-2M': 69, 
                'MFX-E2J-OB': 46, 'MFX-ECO2JET-BKT': 193, 'MFX-SS3-RB': 136.13}

### DEFINE A FUNCTION TO CALCULATE TOTAL ITEM SALES ANNUALLY ###
@st.cache_data
def product_totals(dict, product, months=['All']):

    total = 0

    if months == ['All']:
        for m, prod in dict.items():
            total += prod[product]
        
    else:
        for month in months:
            total += dict[month][product]

    return total

### DEFINE A FUNCTION TO DISPLAY PRODUCT TOTALS AND MONTHLY BREAKDOWN ###

def display_category_totals(dict):
    
    for key, val in dict.items():
        st.subheader('{}:  \n'.format(key, val))
        for k, v in val.items():
            st.markdown(' - {} - {}  \n'.format(k, v))
            
    return None

### DEFINE FUNCTION TO GATHER MONTHLY SALES INTO DICTIONARY FROM DATAFRAME ###    
@st.cache_data
def get_monthly_sales(df, year):

	sales_dict = {'January': [0, 0], 'February': [0, 0], 'March': [0, 0], 'April': [0, 0], 'May': [0, 0], 'June': [0, 0], 'July': [0, 0], 'August': [0, 0], 'September': [0, 0], 'October': [0, 0], 'November': [0, 0], 'December': [0, 0]}

	idx = 0

	for sale in df.sales_order:
		
		month = num_to_month(df.iloc[idx].order_date.month)

		if df.iloc[idx].order_date.year == year:
			
			if df.iloc[idx].channel[0] == 'F':
				sales_dict[month][0] += df.iloc[idx].total_line_item_spend
			else:
				sales_dict[month][1] += df.iloc[idx].total_line_item_spend            

		idx += 1
	
	return sales_dict


### DEFINE FUNCTION TO DISPLAY MONTHLY SALES FOR ALL MONTHS ###
def display_monthly_sales(sales_dict):

	for month, sales in sales_dict.items():
		month_sales = sales[0] + sales[1]
		woo = percent_of_sales(sales[0], sales[1])
		fulcrum = percent_of_sales(sales[1], sales[0])
		st.write('**{}: ${:,.2f}**  \n({:.2f}% Web, {:.2f}% Fulcrum)'.format(month, month_sales, woo, fulcrum))

	return None
	
### DEFINE FUNTION TO CALCULATE TOTALS AND PERCENT BY CHANNEL ###
def calc_monthly_totals(sales_dict, months=['All']):

	total_sales = 0
	total_web = 0
	total_fulcrum = 0
	num_months = 0
	
	for month, sales in sales_dict.items():
		if months == ['All']:
			total_sales += (sales[0] + sales[1])
			total_web += sales[0]
			total_fulcrum += sales[1]
			if sales[0] + sales[1] < 100:
				pass
			else:
				num_months += 1
			
		else:
			for mnth in months:
				if month == mnth:
					total_sales += (sales[0] + sales[1])
					total_web += sales[0]
					total_fulcrum += sales[1]
				if sales[0] + sales [1] < 100:
					pass
				else:
					num_months += 1
						
	avg_month = total_sales / num_months                
	total_web_perc = percent_of_sales(total_web, total_fulcrum)
	total_fulcrum_perc = percent_of_sales(total_fulcrum, total_web)
	
	return total_sales, total_web_perc, total_fulcrum_perc, avg_month

@st.cache_data
def get_monthly_sales_wvr(df, year):

    sales_dict = {'January': [0, 0], 'February': [0, 0], 'March': [0, 0], 'April': [0, 0], 'May': [0, 0], 'June': [0, 0], 'July': [0, 0], 'August': [0, 0], 'September': [0, 0], 'October': [0, 0], 'November': [0, 0], 'December': [0, 0]}

    idx = 0

    for cust in df.customer:
		
        month = num_to_month(df.iloc[idx].order_date.month)
    
        if df.iloc[idx].order_date.year == year:
            if cust in wholesale_list:
                sales_dict[month][0] += df.iloc[idx].total_line_item_spend
            else:
                sales_dict[month][1] += df.iloc[idx].total_line_item_spend            

        idx += 1
	
    return sales_dict


def beginning_of_year(dt: datetime) -> datetime:
    return datetime(dt.year, 1, 1)

    
today = datetime.now()
#today = datetime(2024, 3, 5)
one_year_ago = today - timedelta(days=365)
two_years_ago = today - timedelta(days=730)
three_years_ago = today - timedelta(days=1095)


@st.cache_data
def get_monthly_sales_wvr_ytd():

    sales_dict = {'January': [0, 0], 'February': [0, 0], 'March': [0, 0], 'April': [0, 0], 'May': [0, 0], 'June': [0, 0], 'July': [0, 0], 'August': [0, 0], 'September': [0, 0], 'October': [0, 0], 'November': [0, 0], 'December': [0, 0]}
    sales_dict_minus1 = {'January': [0, 0], 'February': [0, 0], 'March': [0, 0], 'April': [0, 0], 'May': [0, 0], 'June': [0, 0], 'July': [0, 0], 'August': [0, 0], 'September': [0, 0], 'October': [0, 0], 'November': [0, 0], 'December': [0, 0]}
    sales_dict_minus2 = {'January': [0, 0], 'February': [0, 0], 'March': [0, 0], 'April': [0, 0], 'May': [0, 0], 'June': [0, 0], 'July': [0, 0], 'August': [0, 0], 'September': [0, 0], 'October': [0, 0], 'November': [0, 0], 'December': [0, 0]}

    idx = 0

    for cust in df.customer:

        order_date = df.iloc[idx].order_date
        month = num_to_month(df.iloc[idx].order_date.month)
    
        if two_years_ago.date() >= order_date >= beginning_of_year(two_years_ago).date():
            if cust in wholesale_list:
                sales_dict_minus2[month][0] += df.iloc[idx].total_line_item_spend
            else:
                sales_dict_minus2[month][1] += df.iloc[idx].total_line_item_spend 
                
        elif one_year_ago.date() >= order_date >= beginning_of_year(one_year_ago).date():
            if cust in wholesale_list:
                sales_dict_minus1[month][0] += df.iloc[idx].total_line_item_spend
            else:
                sales_dict_minus1[month][1] += df.iloc[idx].total_line_item_spend 
                
        elif today.date() >= order_date >= beginning_of_year(today).date():
            if cust in wholesale_list:
                sales_dict[month][0] += df.iloc[idx].total_line_item_spend
            else:
                sales_dict[month][1] += df.iloc[idx].total_line_item_spend 
                
        idx += 1
	
    return sales_dict, sales_dict_minus1, sales_dict_minus2

	
### FOR DASHBOARD ###  
@st.cache_data
def get_monthly_sales_v2(df, year):

    unique_sales_orders = []

    sales_dict = {'January': [[0, 0], [0, 0], [0]], 'February': [[0, 0], [0, 0], [0]], 'March': [[0, 0], [0, 0], [0]], 'April': [[0, 0], [0, 0], [0]], 'May': [[0, 0], [0, 0], [0]], 'June': [[0, 0], [0, 0], [0]], 'July': [[0, 0], [0, 0], [0]], 'August': [[0, 0], [0, 0], [0]], 'September': [[0, 0], [0, 0], [0]], 'October': [[0, 0], [0, 0], [0]], 'November': [[0, 0], [0, 0], [0]], 'December': [[0, 0], [0, 0], [0]]}
    idx = 0

    for sale in df.sales_order:
        
        month = num_to_month(df.iloc[idx].order_date.month)

        if df.iloc[idx].order_date.year == year:
            
            if df.iloc[idx].channel[0] == 'F':
                sales_dict[month][0][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders:
                    sales_dict[month][0][1] += 1
                    unique_sales_orders.append(sale)
            else:
                sales_dict[month][1][0] += df.iloc[idx].total_line_item_spend   
                if df.iloc[idx].line_item[:5] == 'Magic' or df.iloc[idx].line_item[:3] == 'MFX':
                    sales_dict[month][2][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders:
                    sales_dict[month][1][1] += 1
                    unique_sales_orders.append(sale)

        idx += 1
    
    return sales_dict



@st.cache_data
def get_monthly_sales_ytd():

    unique_sales_orders = []
    unique_sales_orders_minus1 = []
    unique_sales_orders_minus2 = []

    sales_dict = {'January': [[0, 0], [0, 0], [0]], 'February': [[0, 0], [0, 0], [0]], 'March': [[0, 0], [0, 0], [0]], 'April': [[0, 0], [0, 0], [0]], 'May': [[0, 0], [0, 0], [0]], 'June': [[0, 0], [0, 0], [0]], 'July': [[0, 0], [0, 0], [0]], 'August': [[0, 0], [0, 0], [0]], 'September': [[0, 0], [0, 0], [0]], 'October': [[0, 0], [0, 0], [0]], 'November': [[0, 0], [0, 0], [0]], 'December': [[0, 0], [0, 0], [0]]}
    sales_dict_minus1 = {'January': [[0, 0], [0, 0], [0]], 'February': [[0, 0], [0, 0], [0]], 'March': [[0, 0], [0, 0], [0]], 'April': [[0, 0], [0, 0], [0]], 'May': [[0, 0], [0, 0], [0]], 'June': [[0, 0], [0, 0], [0]], 'July': [[0, 0], [0, 0], [0]], 'August': [[0, 0], [0, 0], [0]], 'September': [[0, 0], [0, 0], [0]], 'October': [[0, 0], [0, 0], [0]], 'November': [[0, 0], [0, 0], [0]], 'December': [[0, 0], [0, 0], [0]]}
    sales_dict_minus2 = {'January': [[0, 0], [0, 0], [0]], 'February': [[0, 0], [0, 0], [0]], 'March': [[0, 0], [0, 0], [0]], 'April': [[0, 0], [0, 0], [0]], 'May': [[0, 0], [0, 0], [0]], 'June': [[0, 0], [0, 0], [0]], 'July': [[0, 0], [0, 0], [0]], 'August': [[0, 0], [0, 0], [0]], 'September': [[0, 0], [0, 0], [0]], 'October': [[0, 0], [0, 0], [0]], 'November': [[0, 0], [0, 0], [0]], 'December': [[0, 0], [0, 0], [0]]}

    idx = 0

    for sale in df.sales_order:
    
        
        order_date = df.iloc[idx].order_date
        month = num_to_month(df.iloc[idx].order_date.month)
            
        if df.iloc[idx].channel[0] == 'F':
            if two_years_ago.date() >= order_date >= beginning_of_year(two_years_ago).date():
                sales_dict_minus2[month][0][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders_minus2:
                    sales_dict_minus2[month][0][1] += 1
                    unique_sales_orders_minus2.append(sale)
                    
            elif one_year_ago.date() >= order_date >= beginning_of_year(one_year_ago).date():
                sales_dict_minus1[month][0][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders_minus1:
                    sales_dict_minus1[month][0][1] += 1
                    unique_sales_orders_minus1.append(sale)
                    
            elif today.date() >= order_date >= beginning_of_year(today).date():
                sales_dict[month][0][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders:
                    sales_dict[month][0][1] += 1
                    unique_sales_orders.append(sale)

        else:
            if two_years_ago.date() >= order_date >= beginning_of_year(two_years_ago).date():
                sales_dict_minus2[month][1][0] += df.iloc[idx].total_line_item_spend 
                if df.iloc[idx].line_item[:5] == 'Magic' or df.iloc[idx].line_item[:3] == 'MFX':
                    sales_dict_minus2[month][2][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders_minus2:
                    sales_dict_minus2[month][1][1] += 1
                    unique_sales_orders_minus2.append(sale)
                    
            elif one_year_ago.date() >= order_date >= beginning_of_year(one_year_ago).date():
                sales_dict_minus1[month][1][0] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].line_item[:5] == 'Magic' or df.iloc[idx].line_item[:3] == 'MFX':
                    sales_dict_minus1[month][2][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders_minus1:
                    sales_dict_minus1[month][1][1] += 1
                    unique_sales_orders_minus1.append(sale)
                    
            elif today.date() >= order_date >= beginning_of_year(today).date():
                sales_dict[month][1][0] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].line_item[:5] == 'Magic' or df.iloc[idx].line_item[:3] == 'MFX':
                    sales_dict[month][2][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders:
                    sales_dict[month][1][1] += 1
                    unique_sales_orders.append(sale)

        idx += 1

    return sales_dict, sales_dict_minus1, sales_dict_minus2



@st.cache_data
def calc_monthly_totals_v2(sales_dict, months=['All']):

    total_sales = 0
    total_web = 0
    total_fulcrum = 0
    num_months = 0
    magic_sales = 0
    
    for month, sales in sales_dict.items():
        if months == ['All']:
            total_sales += (sales[0][0] + sales[1][0])
            total_web += sales[0][0]
            total_fulcrum += sales[1][0]
            magic_sales += sales[2][0]
            if sales[0][0] + sales[1][0] < 100:
                pass
            else:
                num_months += 1
            
        else:
            for mnth in months:
                if month == mnth:
                    total_sales += (sales[0][0] + sales[1][0])
                    total_web += sales[0][0]
                    total_fulcrum += sales[1][0]
                if sales[0][0] + sales [1][0] < 100:
                    pass
                else:
                    num_months += 1
    if num_months == 0:
        num_months = 1
    avg_month = total_sales / num_months                
    total_web_perc = percent_of_sales(total_web, total_fulcrum)
    total_fulcrum_perc = percent_of_sales(total_fulcrum, total_web)
    
    return total_sales, total_web_perc, total_fulcrum_perc, avg_month, magic_sales

### FUNCTIONS FOR PLOTTING CHARTS ###
def format_for_chart_ms(data_dict, note=None):
    temp_dict = {'Months': months_x, 'Total Sales': []}
    
    for month, sales in data_dict.items():
        if len(temp_dict['Total Sales']) >= 12:
            pass
        else:
            temp_dict['Total Sales'].append(sales[0][0] + sales[1][0])
                
    df = pd.DataFrame(temp_dict)
    
    return df

def plot_bar_chart_ms(df):
	st.write(alt.Chart(df).mark_bar().encode(
		x=alt.X('Months', sort=None).title('Month'),
		y='Total Sales',
	).properties(height=500, width=750).configure_mark(
		color='limegreen'
	))

def plot_bar_chart_ms_comp(df):
	st.write(alt.Chart(df).mark_bar().encode(
		x=alt.X('Months', sort=None).title('Month'),
		y='Total Sales',
	).properties(height=500, width=350).configure_mark(
		color='limegreen'
	))

### DEFINE A FUNCTION TO EXTRACT DATA FROM SALES DICTIONARY 

@st.cache_data
def extract_transaction_data(sales_dict, month='All'):

    sales_sum = 0
    sales_sum_web = 0
    sales_sum_fulcrum = 0
    
    total_trans = 0
    total_trans_web = 0
    total_trans_fulcrum = 0

    avg_order = 0
    avg_order_web = 0
    avg_order_fulcrum = 0

    if month == 'All':
        for mnth, sales in sales_dict.items():
            sales_sum += sales[0][0] + sales[1][0]
            sales_sum_web += sales[0][0]
            sales_sum_fulcrum += sales[1][0]
            total_trans += sales[0][1] + sales[1][1]
            total_trans_web += sales[0][1]
            total_trans_fulcrum += sales[1][1]
    else:
        sales_sum_web = sales_dict[month][0][0]
        sales_sum_fulcrum = sales_dict[month][1][0]
        sales_sum = sales_sum_fulcrum + sales_sum_web
        total_trans_web = sales_dict[month][0][1]
        total_trans_fulcrum = sales_dict[month][1][1]
        total_trans = total_trans_web + total_trans_fulcrum

    if total_trans == 0:
        avg_order = 0
    elif total_trans_web == 0:
        avg_order_web = 0
    elif total_trans_fulcrum == 0:
        avg_order_fulcrum = 0
    else:
        avg_order = sales_sum / total_trans
        avg_order_web = sales_sum_web / total_trans_web
        avg_order_fulcrum = sales_sum_fulcrum / total_trans_fulcrum

    return [avg_order_web, avg_order_fulcrum, avg_order, sales_sum_web, sales_sum_fulcrum, sales_sum, total_trans_web, total_trans_fulcrum, total_trans]
            
            


def extract_transaction_data(sales_dict, month='All'):

    sales_sum = 0
    sales_sum_web = 0
    sales_sum_fulcrum = 0
    
    total_trans = 0
    total_trans_web = 0
    total_trans_fulcrum = 0

    avg_order = 0
    avg_order_web = 0
    avg_order_fulcrum = 0

    if month == 'All':
        for mnth, sales in sales_dict.items():
            sales_sum += sales[0][0] + sales[1][0]
            sales_sum_web += sales[0][0]
            sales_sum_fulcrum += sales[1][0]
            total_trans += sales[0][1] + sales[1][1]
            total_trans_web += sales[0][1]
            total_trans_fulcrum += sales[1][1]
    else:
        sales_sum_web = sales_dict[month][0][0]
        sales_sum_fulcrum = sales_dict[month][1][0]
        sales_sum = sales_sum_fulcrum + sales_sum_web
        total_trans_web = sales_dict[month][0][1]
        total_trans_fulcrum = sales_dict[month][1][1]
        total_trans = total_trans_web + total_trans_fulcrum

    if total_trans == 0:
        avg_order = 0
    elif total_trans_web == 0:
        avg_order_web = 0
    elif total_trans_fulcrum == 0:
        avg_order_fulcrum = 0
    else:
        avg_order = sales_sum / total_trans
        avg_order_web = sales_sum_web / total_trans_web
        avg_order_fulcrum = sales_sum_fulcrum / total_trans_fulcrum

    return [avg_order_web, avg_order_fulcrum, avg_order, sales_sum_web, sales_sum_fulcrum, sales_sum, total_trans_web, total_trans_fulcrum, total_trans]


### USE METRIC CARDS TO DISPLAY MONTHLY SALES DATA ###
def display_month_data_x(sales_dict1, sales_dict2=None, note=None):

    dBoard1 = st.columns(3)
    dBoard2 = st.columns(3)
    dBoard3 = st.columns(3)
    dBoard4 = st.columns(3)
    idx = 0
    idx1 = 0
    idx2 = 0
    idx3 = 0

    if note == None:
        for x in months_x:
    
            try:
                var = ''
                diff = (sales_dict1[x][0][0] + sales_dict1[x][1][0]) - (sales_dict2[x][1][0] + sales_dict2[x][0][0])
                if diff > 0:
                    var = '+'
                elif diff < 0:
                    var = '-'
                    
                if idx < 3:
                    with dBoard1[idx]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='{} ${:,} vs. prior year'.format(var, abs(int(diff))))
                elif idx >=3 and idx < 6:
                    with dBoard2[idx1]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='{} ${:,} vs. prior year'.format(var, abs(int(diff))))
                        idx1 += 1
                elif idx >= 6 and idx < 9:
                    with dBoard3[idx2]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='{} ${:,} vs. prior year'.format(var, abs(int(diff))))
                        idx2 += 1
                else:
                    with dBoard4[idx3]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='{} ${:,} vs. prior year'.format(var, abs(int(diff))))
                        idx3 += 1
        
                idx += 1
                
            except:
                
                if idx < 3:
                    with dBoard1[idx]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='')
                elif idx >=3 and idx < 6:
                    with dBoard2[idx1]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='')
                        idx1 += 1
                elif idx >= 6 and idx < 9:
                    with dBoard3[idx2]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='')
                        idx2 += 1
                else:
                    with dBoard4[idx3]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='')
                        idx3 += 1
        
                idx += 1
                
    return None


@st.cache_data
def calc_hist_metrics(sales_dict1, sales_dict2=None):

    sd1_wholesale = 0
    sd1_retail = 0
    sd1_tot = 0
    sd2_wholesale = 0
    sd2_retail = 0
    sd2_tot = 0
    
    sd1_wholesale_trans = 0
    sd1_retail_trans = 0
    sd1_trans_tot = 0
    sd2_wholesale_trans = 0
    sd2_retail_trans = 0
    sd2_trans_tot = 0

    sd1_avg_wholesale_trans = 0
    sd1_avg_retail_trans = 0
    sd1_avg_trans = 0
    sd2_avg_wholesale_trans = 0
    sd2_avg_retail_trans = 0
    sd2_avg_trans = 0
    
    sd1_avg_month = 0
    sd2_avg_month = 0 
    
    if sales_dict2 != None:

        for month, val in sales_dict1.items():
            sd1_wholesale += val[0][0]
            sd1_retail += val[1][0]
            
            sd1_wholesale_trans += val[0][1]
            sd1_retail_trans += val[1][1]
    
    
        for month, val in sales_dict2.items():
            sd2_wholesale += val[0][0]
            sd2_retail += val[1][0]
            
            sd2_wholesale_trans += val[0][1]
            sd2_retail_trans += val[1][1]

        sd1_tot = sd1_wholesale + sd1_retail
        sd2_tot = sd2_wholesale + sd2_retail
        sd1_trans_tot = sd1_wholesale_trans + sd1_retail_trans
        sd2_trans_tot = sd2_wholesale_trans + sd2_retail_trans

        if sd1_wholesale_trans == 0:
            sd1_avg_wholesale_trans = 0
        else:
            sd1_avg_wholesale_trans = sd1_wholesale / sd1_wholesale_trans
        if sd1_retail_trans == 0:
            sd1_avg_retail_trans = 0
        else:
            sd1_avg_retail_trans = sd1_retail / sd1_retail_trans
            

        sd1_avg_trans = sd1_tot / sd1_trans_tot
        sd1_avg_month = sd1_tot / 12
        
        if sd2_wholesale_trans == 0:
            sd2_avg_wholesale_trans = 0
        else:
            sd2_avg_wholesale_trans = sd2_wholesale / sd2_wholesale_trans
        if sd2_retail_trans == 0:
            sd2_avg_retail_trans = 0
        else:
            sd2_avg_retail_trans = sd2_retail / sd2_retail_trans
            
        sd2_avg_trans = sd2_tot / sd2_trans_tot
        sd2_avg_month = sd2_tot / 12

        return sd1_tot, sd1_trans_tot, sd1_avg_month, sd1_avg_trans, sd1_wholesale, sd1_retail, sd1_wholesale_trans, sd1_retail_trans, sd1_avg_wholesale_trans, sd1_avg_retail_trans, sd2_tot, sd2_trans_tot, sd2_avg_month, sd2_avg_trans, sd2_wholesale, sd2_retail, sd2_wholesale_trans, sd2_retail_trans, sd2_avg_wholesale_trans, sd2_avg_retail_trans

    else:     

        for month, val in sales_dict1.items():
            sd1_wholesale += val[0][0]
            sd1_retail += val[1][0]
            sd1_wholesale_trans += val[0][1]
            sd1_retail_trans += val[1][1]
            
        sd1_tot += sd1_wholesale + sd1_retail
        sd1_trans_tot += sd1_wholesale_trans + sd1_retail_trans

        sd1_avg_wholesale_trans = 0
        sd1_avg_retail_trans = sd1_retail / sd1_retail_trans
        sd1_avg_trans = sd1_tot / sd1_trans_tot    
        sd1_avg_month = sd1_tot / 5

        return sd1_tot, sd1_trans_tot, sd1_avg_month, sd1_avg_trans, sd1_wholesale, sd1_retail, sd1_wholesale_trans, sd1_retail_trans, sd1_avg_wholesale_trans, sd1_avg_retail_trans


@st.cache_data
def extract_handheld_data(df):

    dict_23 = {}
    dict_24 = {}
    dict_25 = {}
    hose_count_23 = {}
    hose_count_24 = {}
    hose_count_25 = {}
    
    # CREATE DATA DICTS 
    for month in months_x:
        dict_23[month] = {'8FT - No Case': [0,0],
                     '8FT - Travel Case': [0,0],
                     '15FT - No Case': [0,0],
                     '15FT - Travel Case': [0,0]}
        dict_24[month] = {'8FT - No Case': [0,0],
                     '8FT - Travel Case': [0,0],
                     '15FT - No Case': [0,0],
                     '15FT - Travel Case': [0,0]}
        dict_25[month] = {'8FT - No Case': [0,0],
                     '8FT - Travel Case': [0,0],
                     '15FT - No Case': [0,0],
                     '15FT - Travel Case': [0,0]}
        
        hose_count_23[month] = [0,0]
        hose_count_24[month] = [0,0]
        hose_count_25[month] = [0,0]
    
    idx = 0
    for line in df.line_item:

        if df.iloc[idx].order_date.year == 2025:
            if line[:16] == 'CC-HCCMKII-08-NC':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_24[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-08-TC':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_24[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-NC':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_24[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-TC':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_24[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
                
        if df.iloc[idx].order_date.year == 2024:
            if line[:16] == 'CC-HCCMKII-08-NC':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_24[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-08-TC':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_24[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-NC':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_24[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-TC':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_24[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
                
        elif df.iloc[idx].order_date.year == 2023:
            if line[:16] == 'CC-HCCMKII-08-NC':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_23[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-08-TC':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_23[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-NC':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_23[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-TC':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_23[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
                
        idx += 1
    
    return dict_23, dict_24, dict_25, hose_count_23, hose_count_24, hose_count_25


@st.cache_data
def extract_hose_data(df):

    dict_23 = {}
    dict_24 = {}
    dict_25 = {}

    # CREATE DATA DICTS 
    for month in months_x:
        dict_23[month] = {'2FT MFD': [0,0], '3.5FT MFD': [0,0], '5FT MFD': [0,0], '5FT STD': [0,0], '5FT DSY': [0,0], '5FT EXT': [0,0], '8FT STD': [0,0], '8FT DSY': [0,0], '8FT EXT': [0,0], '15FT STD': [0,0], '15FT DSY': [0,0], '15FT EXT': [0,0], '25FT STD': [0,0], '25FT DSY': [0,0], '25FT EXT': [0,0], '35FT STD': [0,0], '35FT DSY': [0,0], '35FT EXT': [0,0], '50FT STD': [0,0], '50FT EXT': [0,0], '100FT STD': [0,0], 'CUSTOM': [0,0]}
        dict_24[month] = {'2FT MFD': [0,0], '3.5FT MFD': [0,0], '5FT MFD': [0,0], '5FT STD': [0,0], '5FT DSY': [0,0], '5FT EXT': [0,0], '8FT STD': [0,0], '8FT DSY': [0,0], '8FT EXT': [0,0], '15FT STD': [0,0], '15FT DSY': [0,0], '15FT EXT': [0,0], '25FT STD': [0,0], '25FT DSY': [0,0], '25FT EXT': [0,0], '35FT STD': [0,0], '35FT DSY': [0,0], '35FT EXT': [0,0], '50FT STD': [0,0], '50FT EXT': [0,0], '100FT STD': [0,0], 'CUSTOM': [0,0]}
        dict_25[month] = {'2FT MFD': [0,0], '3.5FT MFD': [0,0], '5FT MFD': [0,0], '5FT STD': [0,0], '5FT DSY': [0,0], '5FT EXT': [0,0], '8FT STD': [0,0], '8FT DSY': [0,0], '8FT EXT': [0,0], '15FT STD': [0,0], '15FT DSY': [0,0], '15FT EXT': [0,0], '25FT STD': [0,0], '25FT DSY': [0,0], '25FT EXT': [0,0], '35FT STD': [0,0], '35FT DSY': [0,0], '35FT EXT': [0,0], '50FT STD': [0,0], '50FT EXT': [0,0], '100FT STD': [0,0], 'CUSTOM': [0,0]}
    
    idx = 0
    
    for line in df.line_item:

        if df.iloc[idx].order_date.year == 2025:
            if line[:8] == 'CC-CH-02':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['2FT MFD'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['2FT MFD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:8] == 'CC-CH-03':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['3.5FT MFD'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['3.5FT MFD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-05-M':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['5FT MFD'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['5FT MFD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-05-S':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['5FT STD'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['5FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-05-D':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['5FT DSY'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['5FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-05-E':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['5FT EXT'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['5FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-08-S':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['8FT STD'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['8FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-08-D':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['8FT DSY'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['8FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-08-E':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['8FT EXT'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['8FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-15-S':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['15FT STD'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['15FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-15-D':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['15FT DSY'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['15FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-15-E':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['15FT EXT'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['15FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-25-S':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['25FT STD'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['25FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-25-D':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['25FT DSY'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['25FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-25-E':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['25FT EXT'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['25FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-35-S':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['35FT STD'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['35FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-35-D':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['35FT DSY'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['35FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-35-E':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['35FT EXT'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['35FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-50-S':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['50FT STD'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['50FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-50-E':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['50FT EXT'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['50FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-CH-100':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['100FT STD'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['100FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:8] == 'CC-CH-XX':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['CUSTOM'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['CUSTOM'][1] += df.iloc[idx].total_line_item_spend

        if df.iloc[idx].order_date.year == 2024:
            if line[:8] == 'CC-CH-02':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['2FT MFD'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['2FT MFD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:8] == 'CC-CH-03':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['3.5FT MFD'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['3.5FT MFD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-05-M':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['5FT MFD'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['5FT MFD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-05-S':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['5FT STD'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['5FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-05-D':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['5FT DSY'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['5FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-05-E':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['5FT EXT'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['5FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-08-S':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT STD'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-08-D':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT DSY'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-08-E':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT EXT'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-15-S':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT STD'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-15-D':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT DSY'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-15-E':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT EXT'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-25-S':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['25FT STD'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['25FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-25-D':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['25FT DSY'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['25FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-25-E':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['25FT EXT'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['25FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-35-S':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['35FT STD'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['35FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-35-D':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['35FT DSY'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['35FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-35-E':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['35FT EXT'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['35FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-50-S':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['50FT STD'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['50FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-50-E':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['50FT EXT'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['50FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-CH-100':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['100FT STD'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['100FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:8] == 'CC-CH-XX':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CUSTOM'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CUSTOM'][1] += df.iloc[idx].total_line_item_spend
                
        if df.iloc[idx].order_date.year == 2023:
            if line[:8] == 'CC-CH-02':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['2FT MFD'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['2FT MFD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:8] == 'CC-CH-03':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['3.5FT MFD'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['3.5FT MFD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-05-M':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['5FT MFD'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['5FT MFD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-05-S':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['5FT STD'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['5FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-05-D':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['5FT DSY'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['5FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-05-E':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['5FT EXT'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['5FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-08-S':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['8FT STD'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['8FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-08-D':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['8FT DSY'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['8FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-08-E':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['8FT EXT'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['8FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-15-S':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['15FT STD'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['15FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-15-D':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['15FT DSY'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['15FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-15-E':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['15FT EXT'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['15FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-25-S':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['25FT STD'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['25FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-25-D':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['25FT DSY'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['25FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-25-E':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['25FT EXT'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['25FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-35-S':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['35FT STD'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['35FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-35-D':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['35FT DSY'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['35FT DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-35-E':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['35FT EXT'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['35FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-50-S':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['50FT STD'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['50FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:10] == 'CC-CH-50-E':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['50FT EXT'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['50FT EXT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-CH-100':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['100FT STD'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['100FT STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:8] == 'CC-CH-XX':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CUSTOM'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CUSTOM'][1] += df.iloc[idx].total_line_item_spend
                
        idx += 1
    
    return dict_23, dict_24, dict_25


@st.cache_data
def extract_acc_data(df):

    dict_23 = {}
    dict_24 = {}
    dict_25 = {}

    # CREATE DATA DICTS 
    for month in months_x:
        dict_23[month] = {'CC-AC-CCL': [0,0], 'CC-AC-CTS': [0,0], 'CC-F-DCHA': [0,0], 'CC-F-HEA': [0,0], 'CC-AC-RAA': [0,0], 'CC-AC-4PM': [0,0], 'CC-F-MFDCGAJIC': [0,0], ' CC-AC-CGAJIC-SET': [0,0], 'CC-CTC-20': [0,0], 'CC-CTC-50': [0,0], 'CC-AC-TC': [0,0], 'CC-VV-KIT': [0,0], 
                'CC-RC-2430': [0,0,0,0,0], 'CC-AC-LA2': [0,0], 'CC-SW-05': [0,0], 'CC-NPTC-06-STD': [0,0], 'CC-NPTC-10-DSY': [0,0], 'CC-NPTC-15-DSY': [0,0], 'CC-NPTC-25-DSY': [0,0]}
        dict_24[month] = {'CC-AC-CCL': [0,0], 'CC-AC-CTS': [0,0], 'CC-F-DCHA': [0,0], 'CC-F-HEA': [0,0], 'CC-AC-RAA': [0,0], 'CC-AC-4PM': [0,0], 'CC-F-MFDCGAJIC': [0,0], ' CC-AC-CGAJIC-SET': [0,0], 'CC-CTC-20': [0,0], 'CC-CTC-50': [0,0], 'CC-AC-TC': [0,0], 'CC-VV-KIT': [0,0], 
                'CC-RC-2430': [0,0,0,0,0], 'CC-AC-LA2': [0,0], 'CC-SW-05': [0,0], 'CC-NPTC-06-STD': [0,0], 'CC-NPTC-10-DSY': [0,0], 'CC-NPTC-15-DSY': [0,0], 'CC-NPTC-25-DSY': [0,0]}
        dict_25[month] = {'CC-AC-CCL': [0,0], 'CC-AC-CTS': [0,0], 'CC-F-DCHA': [0,0], 'CC-F-HEA': [0,0], 'CC-AC-RAA': [0,0], 'CC-AC-4PM': [0,0], 'CC-F-MFDCGAJIC': [0,0], ' CC-AC-CGAJIC-SET': [0,0], 'CC-CTC-20': [0,0], 'CC-CTC-50': [0,0], 'CC-AC-TC': [0,0], 'CC-VV-KIT': [0,0], 
                'CC-RC-2430': [0,0,0,0,0], 'CC-AC-LA2': [0,0], 'CC-SW-05': [0,0], 'CC-NPTC-06-STD': [0,0], 'CC-NPTC-10-DSY': [0,0], 'CC-NPTC-15-DSY': [0,0], 'CC-NPTC-25-DSY': [0,0]}
    
    idx = 0
    for line in df.line_item:
        

        if df.iloc[idx].order_date.year == 2025:
             if line[:9] == 'CC-AC-CCL':
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-CCL'][0] += df.iloc[idx].quantity
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-CCL'][1] += df.iloc[idx].total_line_item_spend
             elif line[:9] == 'CC-AC-CTS':
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-CTS'][0] += df.iloc[idx].quantity
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-CTS'][1] += df.iloc[idx].total_line_item_spend
             elif line[:9] == 'CC-F-DCHA':
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-F-DCHA'][0] += df.iloc[idx].quantity
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-F-DCHA'][1] += df.iloc[idx].total_line_item_spend
             elif line[:8] == 'CC-F-HEA':
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-F-HEA'][0] += df.iloc[idx].quantity
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-F-HEA'][1] += df.iloc[idx].total_line_item_spend
             elif line[:9] == 'CC-AC-RAA':
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-RAA'][0] += df.iloc[idx].quantity
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-RAA'][1] += df.iloc[idx].total_line_item_spend
             elif line[:9] == 'CC-AC-4PM':
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-4PM'][0] += df.iloc[idx].quantity
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-4PM'][1] += df.iloc[idx].total_line_item_spend
             elif line[:14] == 'CC-F-MFDCGAJIC':
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-F-MFDCGAJIC'][0] += df.iloc[idx].quantity
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-F-MFDCGAJIC'][1] += df.iloc[idx].total_line_item_spend
             elif line[:17] == ' CC-AC-CGAJIC-SET':
                 dict_25[num_to_month(df.iloc[idx].order_date.month)][' CC-AC-CGAJIC-SET'][0] += df.iloc[idx].quantity
                 dict_25[num_to_month(df.iloc[idx].order_date.month)][' CC-AC-CGAJIC-SET'][1] += df.iloc[idx].total_line_item_spend
             elif line[:9] == 'CC-CTC-20':
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-CTC-20'][0] += df.iloc[idx].quantity
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-CTC-20'][1] += df.iloc[idx].total_line_item_spend
             elif line[:9] == 'CC-CTC-50':
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-CTC-50'][0] += df.iloc[idx].quantity
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-CTC-50'][1] += df.iloc[idx].total_line_item_spend
             elif line[:8] == 'CC-AC-TC':
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-TC'][0] += df.iloc[idx].quantity
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-TC'][1] += df.iloc[idx].total_line_item_spend
             elif line[:9] == 'CC-VV-KIT':
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-VV-KIT'][0] += df.iloc[idx].quantity
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-VV-KIT'][1] += df.iloc[idx].total_line_item_spend
             elif line[:9] == 'CC-AC-LA2':
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-LA2'][0] += df.iloc[idx].quantity
                 dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-LA2'][1] += df.iloc[idx].total_line_item_spend
             elif line[:8] == 'CC-SW-05':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-SW-05'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-SW-05'][1] += df.iloc[idx].total_line_item_spend
             elif line[:14] == 'CC-NPTC-06-STD':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-06-STD'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-06-STD'][1] += df.iloc[idx].total_line_item_spend
             elif line[:14] == 'CC-NPTC-10-DSY':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-10-DSY'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-10-DSY'][1] += df.iloc[idx].total_line_item_spend
             elif line[:14] == 'CC-NPTC-15-DSY':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-15-DSY'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-15-DSY'][1] += df.iloc[idx].total_line_item_spend
             elif line[:14] == 'CC-NPTC-25-DSY':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-25-DSY'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-25-DSY'][1] += df.iloc[idx].total_line_item_spend
             elif line[:5] == 'CC-RC':
                 if line[:14] == 'CC-RC-2430-TTI':
                     pass
                 elif line[:14] == 'CC-RC-2430-PJI':
                     dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][2] += df.iloc[idx].quantity
                 elif line[:14] == 'CC-RC-2430-LAI':
                     dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][3] += df.iloc[idx].quantity                    
                 elif line[:14] == 'CC-RC-2430-QJF':
                     dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][4] += df.iloc[idx].quantity
                 else:
                     dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][0] += df.iloc[idx].quantity
                     dict_25[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][1] += df.iloc[idx].total_line_item_spend
                    
        if df.iloc[idx].order_date.year == 2024:
            if line[:9] == 'CC-AC-CCL':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-CCL'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-CCL'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-AC-CTS':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-CTS'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-CTS'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-F-DCHA':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-F-DCHA'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-F-DCHA'][1] += df.iloc[idx].total_line_item_spend
            elif line[:8] == 'CC-F-HEA':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-F-HEA'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-F-HEA'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-AC-RAA':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-RAA'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-RAA'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-AC-4PM':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-4PM'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-4PM'][1] += df.iloc[idx].total_line_item_spend
            elif line[:14] == 'CC-F-MFDCGAJIC':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-F-MFDCGAJIC'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-F-MFDCGAJIC'][1] += df.iloc[idx].total_line_item_spend
            elif line[:17] == ' CC-AC-CGAJIC-SET':
                dict_24[num_to_month(df.iloc[idx].order_date.month)][' CC-AC-CGAJIC-SET'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)][' CC-AC-CGAJIC-SET'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-CTC-20':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-CTC-20'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-CTC-20'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-CTC-50':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-CTC-50'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-CTC-50'][1] += df.iloc[idx].total_line_item_spend
            elif line[:8] == 'CC-AC-TC':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-TC'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-TC'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-VV-KIT':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-VV-KIT'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-VV-KIT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-AC-LA2':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-LA2'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-LA2'][1] += df.iloc[idx].total_line_item_spend
            elif line[:8] == 'CC-SW-05':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-SW-05'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-SW-05'][1] += df.iloc[idx].total_line_item_spend
            elif line[:14] == 'CC-NPTC-06-STD':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-06-STD'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-06-STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:14] == 'CC-NPTC-10-DSY':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-10-DSY'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-10-DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:14] == 'CC-NPTC-15-DSY':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-15-DSY'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-15-DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:14] == 'CC-NPTC-25-DSY':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-25-DSY'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-25-DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:5] == 'CC-RC':
                if line[:14] == 'CC-RC-2430-TTI':
                    pass
                elif line[:14] == 'CC-RC-2430-PJI':
                    dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][2] += df.iloc[idx].quantity
                elif line[:14] == 'CC-RC-2430-LAI':
                    dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][3] += df.iloc[idx].quantity                    
                elif line[:14] == 'CC-RC-2430-QJF':
                    dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][4] += df.iloc[idx].quantity
                else:
                    dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][0] += df.iloc[idx].quantity
                    dict_24[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][1] += df.iloc[idx].total_line_item_spend
                    

        
        if df.iloc[idx].order_date.year == 2023:
            if line[:9] == 'CC-AC-CCL':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-CCL'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-CCL'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-AC-CTS':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-CTS'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-CTS'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-F-DCHA':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-F-DCHA'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-F-DCHA'][1] += df.iloc[idx].total_line_item_spend
            elif line[:8] == 'CC-F-HEA':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-F-HEA'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-F-HEA'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-AC-RAA':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-RAA'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-RAA'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-AC-4PM':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-4PM'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-4PM'][1] += df.iloc[idx].total_line_item_spend
            elif line[:14] == 'CC-F-MFDCGAJIC':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-F-MFDCGAJIC'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-F-MFDCGAJIC'][1] += df.iloc[idx].total_line_item_spend
            elif line[:17] == ' CC-AC-CGAJIC-SET':
                dict_23[num_to_month(df.iloc[idx].order_date.month)][' CC-AC-CGAJIC-SET'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)][' CC-AC-CGAJIC-SET'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-CTC-20':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-CTC-20'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-CTC-20'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-CTC-50':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-CTC-50'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-CTC-50'][1] += df.iloc[idx].total_line_item_spend
            elif line[:8] == 'CC-AC-TC':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-TC'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-TC'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-VV-KIT':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-VV-KIT'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-VV-KIT'][1] += df.iloc[idx].total_line_item_spend
            elif line[:9] == 'CC-AC-LA2':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-LA2'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-AC-LA2'][1] += df.iloc[idx].total_line_item_spend
            elif line[:14] == 'CC-NPTC-06-STD':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-06-STD'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-06-STD'][1] += df.iloc[idx].total_line_item_spend
            elif line[:14] == 'CC-NPTC-10-DSY':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-10-DSY'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-10-DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:14] == 'CC-NPTC-15-DSY':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-15-DSY'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-15-DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:14] == 'CC-NPTC-25-DSY':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-25-DSY'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-NPTC-25-DSY'][1] += df.iloc[idx].total_line_item_spend
            elif line[:5] == 'CC-RC':
                if line[:14] == 'CC-RC-2430-TTI':
                    pass
                elif line[:14] == 'CC-RC-2430-PJI':
                    dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][2] += df.iloc[idx].quantity
                elif line[:14] == 'CC-RC-2430-LAI':
                    dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][3] += df.iloc[idx].quantity                    
                elif line[:14] == 'CC-RC-2430-QJF':
                    dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][4] += df.iloc[idx].quantity
                else:
                    dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][0] += df.iloc[idx].quantity
                    dict_23[num_to_month(df.iloc[idx].order_date.month)]['CC-RC-2430'][1] += df.iloc[idx].total_line_item_spend

                
        idx += 1
    
    return dict_23, dict_24, dict_25

@st.cache_data
def extract_control_data(df):

    dict_23 = {}
    dict_24 = {}
    dict_25 = {}

    # CREATE DATA DICTS 
    for month in months_x:
        dict_23[month] = {'The Button': [0,0,0],
                     'Shostarter': [0,0,0],
                     'Shomaster': [0,0,0]}
        dict_24[month] = {'The Button': [0,0,0],
                     'Shostarter': [0,0,0],
                     'Shomaster': [0,0,0]}
        dict_25[month] = {'The Button': [0,0,0],
                     'Shostarter': [0,0,0],
                     'Shomaster': [0,0,0]}
    
    idx = 0
    for line in df.line_item:

        if df.iloc[idx].order_date.year == 2025:
            if line[:7] == 'CC-TB-3':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['The Button'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['The Button'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_25[num_to_month(df.iloc[idx].order_date.month)]['The Button'][2] += df.iloc[idx].quantity  
            elif line[:8] == 'CC-SS-35':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['Shostarter'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['Shostarter'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_25[num_to_month(df.iloc[idx].order_date.month)]['Shostarter'][2] += df.iloc[idx].quantity  
            elif line[:5] == 'CC-SM':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['Shomaster'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['Shomaster'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_25[num_to_month(df.iloc[idx].order_date.month)]['Shomaster'][2] += df.iloc[idx].quantity 
                    
        if df.iloc[idx].order_date.year == 2024:
            if line[:7] == 'CC-TB-3':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['The Button'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['The Button'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_24[num_to_month(df.iloc[idx].order_date.month)]['The Button'][2] += df.iloc[idx].quantity  
            elif line[:8] == 'CC-SS-35':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['Shostarter'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['Shostarter'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_24[num_to_month(df.iloc[idx].order_date.month)]['Shostarter'][2] += df.iloc[idx].quantity  
            elif line[:5] == 'CC-SM':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['Shomaster'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['Shomaster'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_24[num_to_month(df.iloc[idx].order_date.month)]['Shomaster'][2] += df.iloc[idx].quantity 

        elif df.iloc[idx].order_date.year == 2023:
            if line[:7] == 'CC-TB-3':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['The Button'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['The Button'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_23[num_to_month(df.iloc[idx].order_date.month)]['The Button'][2] += df.iloc[idx].quantity 
            elif line[:8] == 'CC-SS-35':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['Shostarter'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['Shostarter'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_23[num_to_month(df.iloc[idx].order_date.month)]['Shostarter'][2] += df.iloc[idx].quantity 
            elif line[:5] == 'CC-SM':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['Shomaster'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['Shomaster'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_23[num_to_month(df.iloc[idx].order_date.month)]['Shomaster'][2] += df.iloc[idx].quantity 

                
        idx += 1
    
    return dict_23, dict_24, dict_25


@st.cache_data
def extract_jet_data(df):

    dict_23 = {}
    dict_24 = {}
    dict_25 = {}

    # CREATE DATA DICTS 
    for month in months_x:
        dict_23[month] = {'Pro Jet': [0,0,0],
                'Quad Jet': [0,0,0],
               'Micro Jet': [0,0,0],
               'Cryo Clamp': [0,0,0]}
        dict_24[month] = {'Pro Jet': [0,0,0],
                'Quad Jet': [0,0,0],
               'Micro Jet': [0,0,0],
               'Cryo Clamp': [0,0,0]}
        dict_25[month] = {'Pro Jet': [0,0,0],
                'Quad Jet': [0,0,0],
               'Micro Jet': [0,0,0],
               'Cryo Clamp': [0,0,0]}
    
    idx = 0
    for line in df.line_item:

        if df.iloc[idx].order_date.year == 2025:
            if line[:6] == 'CC-PRO':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['Pro Jet'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['Pro Jet'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_25[num_to_month(df.iloc[idx].order_date.month)]['Pro Jet'][2] += df.iloc[idx].quantity     
            elif line[:5] == 'CC-QJ':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['Quad Jet'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['Quad Jet'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_25[num_to_month(df.iloc[idx].order_date.month)]['Quad Jet'][2] += df.iloc[idx].quantity  
            elif line[:6] == 'CC-MJM':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['Micro Jet'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['Micro Jet'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_25[num_to_month(df.iloc[idx].order_date.month)]['Micro Jet'][2] += df.iloc[idx].quantity  
            elif line[:6] == 'CC-CC2':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['Cryo Clamp'][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['Cryo Clamp'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_25[num_to_month(df.iloc[idx].order_date.month)]['Cryo Clamp'][2] += df.iloc[idx].quantity 
                    
        if df.iloc[idx].order_date.year == 2024:
            if line[:6] == 'CC-PRO':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['Pro Jet'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['Pro Jet'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_24[num_to_month(df.iloc[idx].order_date.month)]['Pro Jet'][2] += df.iloc[idx].quantity     
            elif line[:5] == 'CC-QJ':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['Quad Jet'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['Quad Jet'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_24[num_to_month(df.iloc[idx].order_date.month)]['Quad Jet'][2] += df.iloc[idx].quantity  
            elif line[:6] == 'CC-MJM':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['Micro Jet'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['Micro Jet'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_24[num_to_month(df.iloc[idx].order_date.month)]['Micro Jet'][2] += df.iloc[idx].quantity  
            elif line[:6] == 'CC-CC2':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['Cryo Clamp'][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['Cryo Clamp'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_24[num_to_month(df.iloc[idx].order_date.month)]['Cryo Clamp'][2] += df.iloc[idx].quantity  
        elif df.iloc[idx].order_date.year == 2023:
            if line[:6] == 'CC-PRO':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['Pro Jet'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['Pro Jet'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_23[num_to_month(df.iloc[idx].order_date.month)]['Pro Jet'][2] += df.iloc[idx].quantity  
            elif line[:5] == 'CC-QJ':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['Quad Jet'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['Quad Jet'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_23[num_to_month(df.iloc[idx].order_date.month)]['Quad Jet'][2] += df.iloc[idx].quantity  
            elif line[:6] == 'CC-MJM':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['Micro Jet'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['Micro Jet'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_23[num_to_month(df.iloc[idx].order_date.month)]['Micro Jet'][2] += df.iloc[idx].quantity  
            elif line[:6] == 'CC-CC2':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['Cryo Clamp'][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['Cryo Clamp'][1] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].customer in wholesale_list:
                    dict_23[num_to_month(df.iloc[idx].order_date.month)]['Cryo Clamp'][2] += df.iloc[idx].quantity  
                
        idx += 1
    
    return dict_23, dict_24, dict_25

@st.cache_data
def collect_product_data(df, prod='All', years=[2023, 2024, 2025]):

    # NEEDS TO ALLOW FOR 2025 AND KICK OUT 2025 DATA

    jet23, jet24, jet25 = extract_jet_data(df)
    control23, control24, control25 = extract_control_data(df)
    handheld23, handheld24, handheld25, hh_hose_count_23, hh_hose_count_24, hh_hose_count_25 = extract_handheld_data(df)
    hose23, hose24, hose25 = extract_hose_data(df)
    acc23, acc24, acc25 = extract_acc_data(df)

    # INCLUDE HANDHELD HOSES IN COUNTS
    for key, val in hose23.items():
        hose23[key]['8FT STD'][0] += hh_hose_count_23[key][0]
        hose23[key]['15FT STD'][0] += hh_hose_count_23[key][1]
    for key, val in hose24.items():
        hose24[key]['8FT STD'][0] += hh_hose_count_24[key][0]
        hose24[key]['15FT STD'][0] += hh_hose_count_24[key][1] 
    for key, val in hose25.items():
        hose25[key]['8FT STD'][0] += hh_hose_count_25[key][0]
        hose25[key]['15FT STD'][0] += hh_hose_count_25[key][1] 

    return jet23, jet24, jet25, control23, control24, control25, handheld23, handheld24, handheld25, hose23, hose24, hose25, acc23, acc24, acc25


@st.cache_data
def organize_hose_data(dict):
    
    count_mfd = {'2FT MFD': [0, 0], '3.5FT MFD': [0, 0], '5FT MFD': [0, 0]}
    count_5ft = {'5FT STD': [0, 0], '5FT DSY': [0, 0], '5FT EXT': [0, 0]}
    count_8ft = {'8FT STD': [0, 0], '8FT DSY': [0, 0], '8FT EXT': [0, 0]}
    count_15ft = {'15FT STD': [0, 0], '15FT DSY': [0, 0], '15FT EXT': [0, 0]}
    count_25ft = {'25FT STD': [0, 0], '25FT DSY': [0, 0], '25FT EXT': [0, 0]}
    count_35ft = {'35FT STD': [0, 0], '35FT DSY': [0, 0], '35FT EXT': [0, 0]}
    count_50ft = {'50FT STD': [0, 0], '50FT EXT': [0, 0]}
    count_100ft = [0, 0]
    
    for month, prod in dict.items():
        for hose, val in prod.items():

            if 'MFD' in hose:
                count_mfd[hose][0] += val[0]
                count_mfd[hose][1] += val[1]
            elif hose == '5FT STD' or hose == '5FT DSY' or hose == '5FT EXT':
                count_5ft[hose][0] += val[0]
                count_5ft[hose][1] += val[1]
            elif '8FT' in hose:
                count_8ft[hose][0] += val[0]
                count_8ft[hose][1] += val[1]            
            elif '15FT' in hose:
                count_15ft[hose][0] += val[0]
                count_15ft[hose][1] += val[1]   
            elif '25FT' in hose:
                count_25ft[hose][0] += val[0]
                count_25ft[hose][1] += val[1]   
            elif '35FT' in hose:
                count_35ft[hose][0] += val[0]
                count_35ft[hose][1] += val[1]   
            elif '50FT' in hose:
                count_50ft[hose][0] += val[0]
                count_50ft[hose][1] += val[1]  
            elif '100FT' in hose:
                count_100ft[0] += val[0]
                count_100ft[1] += val[1]
    
    return [count_mfd, count_5ft, count_8ft, count_15ft, count_25ft, count_35ft, count_50ft, count_100ft]




@st.cache_data
def magic_sales(year):

    count = 0
    magic_products = {'MagicFX Commander': [0,0], 'Magic FX Smoke Bubble Blaster': [0,0], 'MagicFX ARM SFX SAFETY TERMINATOR': [0,0], 'MagicFX Device Updater': [0,0], 'MagicFX PSYCO2JET': [0,0], 'MagicFX Red Button': [0,0], 'MagicFX Replacement Keys': [0,0], 'MagicFX SFX Safety ARM Controller': [0,0], 'MagicFX SPARXTAR': [0,0], 'MagicFX Sparxtar powder': [0,0], 'MagicFX StadiumBlaster': [0,0], 'MagicFX StadiumBlower': [0,0], 'MagicFX StadiumShot III': [0,0], 'MagicFX SuperBlaster II': [0,0], 'MagicFX Swirl Fan II': [0,0], 'MagicFX Switchpack II': [0,0], 'MFX-AC-SBRV': [0,0], 'MFX-E2J-230': [0,0], 'MFX-E2J-2LFA': [0,0], 'MFX-E2J-5LFCB': [0,0], 'MFX-E2J-F-ID': [0,0], 'MFX-E2J-F-OD': [0,0], 'MFX-E2J-FC': [0,0], 'MFX-E2J-FEH-1M': [0,0], 'MFX-E2J-FEH-2M': [0,0], 'MFX-E2J-OB': [0,0], 'MFX-ECO2JET-BKT': [0,0], 'MFX-SS3-RB': [0,0]}

    idx = 0

    for sale in df.sales_order:
        if df.iloc[idx].ordered_year == year:
            if df.iloc[idx].line_item[:5] == 'Magic' or df.iloc[idx].line_item[:3] == 'MFX':
                count += df.iloc[idx].total_line_item_spend
                for prod, key in magic_products.items():
                    if df.iloc[idx].line_item[:len(prod)] == prod:
                        key[0] += df.iloc[idx].quantity
                        key[1] += df.iloc[idx].total_line_item_spend

        idx += 1

    return count, magic_products

def display_metrics(sales_dict1, sales_dict2=None, month='All', wvr1=None, wvr2=None, note=None):


    if sales_dict2 == None and note == None:
        
        data = extract_transaction_data(sales_dict1)
        total_sales, total_web_perc, total_fulcrum_perc, avg_month, magic_sales = calc_monthly_totals_v2(sales_dict1)
        
        db1, db2, db3 = st.columns([.3, .4, .3], gap='medium')
        
        db1.metric(label='**Website Sales**', value='${:,}'.format(int(data[3])), delta='')
        db1.metric(label='**Website Transactions**', value='{:,}'.format(data[6]), delta='')
        db1.metric(label='**Website Average Sale**', value='${:,}'.format(int(data[0])), delta='')
    
        db2.metric(label='**Total Sales**', value='${:,}'.format(int(data[5])), delta='')
        db2.metric(label='**Monthly Average**', value='${:,}'.format(int(avg_month)), delta='')
        db2.metric(label='**Total Transactions**', value='{:,}'.format(data[8]), delta='')
        
        db3.metric(label='**Fulcrum Sales**', value='${:,}'.format(int(data[4])), delta='')
        db3.metric(label='**Fulcrum Transactions**', value='{:,}'.format(data[7]), delta='')
        db3.metric(label='**Fulcrum Average Sale**', value='${:,}'.format(int(data[1])), delta='')
        
        style_metric_cards()

    if note != None:
        
        db1, db2, db3 = st.columns([.3, .4, .3], gap='medium')
        
        if sales_dict2 == None:

            sd1_tot, sd1_trans_tot, sd1_avg_month, sd1_avg_trans, sd1_wholesale, sd1_retail, sd1_wholesale_trans, sd1_retail_trans, sd1_avg_wholesale_trans, sd1_avg_retail_trans = calc_hist_metrics(sales_dict1)
            
            db1.metric(label='**Retail Sales**', value='${:,}'.format(int(sd1_retail)), delta='')
            db1.metric(label='**Retail Transactions**', value='{:,}'.format(int(sd1_retail_trans)), delta='')
            db1.metric(label='**Retail Average Sale**', value='${:,}'.format(int(sd1_avg_retail_trans)), delta='')
        
            db2.metric(label='**Total Sales**', value='${:,}'.format(int(sd1_tot)), delta='')
            db2.metric(label='**Monthly Average**', value='${:,}'.format(int(sd1_avg_month)), delta='')
            db2.metric(label='**Total Transactions**', value='{:,}'.format(int(sd1_trans_tot)), delta='')
            db2.metric(label='**Average Sale Amount**', value='${:,}'.format(int(sd1_avg_trans)), delta='')

            db3.metric(label='**Wholesale Sales**', value='${:,}'.format(int(sd1_wholesale)), delta='')
            db3.metric(label='**Wholesale Transactions**', value='{:,}'.format(int(sd1_wholesale_trans)), delta='')
            db3.metric(label='**Wholesale Average Sale**', value='${:,}'.format(int(sd1_avg_wholesale_trans)), delta='')


        else:

            sd1_tot, sd1_trans_tot, sd1_avg_month, sd1_avg_trans, sd1_wholesale, sd1_retail, sd1_wholesale_trans, sd1_retail_trans, sd1_avg_wholesale_trans, sd1_avg_retail_trans, sd2_tot, sd2_trans_tot, sd2_avg_month, sd2_avg_trans, sd2_wholesale, sd2_retail, sd2_wholesale_trans, sd2_retail_trans, sd2_avg_wholesale_trans, sd2_avg_retail_trans = calc_hist_metrics(sales_dict1, sales_dict2)
            
            db1.metric(label='**Retail Sales**', value='${:,}'.format(int(sd1_retail)), delta=percent_of_change(sd2_retail, sd1_retail))
            db1.metric(label='**Retail Transactions**', value='{:,}'.format(int(sd1_retail_trans)), delta=percent_of_change(sd2_retail_trans, sd1_retail_trans))
            db1.metric(label='**Retail Average Sale**', value='${:,}'.format(int(sd1_avg_retail_trans)), delta=percent_of_change(sd2_avg_retail_trans, sd1_avg_retail_trans))
        
            db2.metric(label='**Total Sales**', value='${:,}'.format(int(sd1_tot)), delta=percent_of_change(sd2_tot, sd1_tot))
            db2.metric(label='**Monthly Average**', value='${:,}'.format(int(sd1_avg_month)), delta=percent_of_change(sd2_avg_month, sd1_avg_month))
            db2.metric(label='**Total Transactions**', value='{:,}'.format(int(sd1_trans_tot)), delta=percent_of_change(sd2_trans_tot, sd1_trans_tot))
            db2.metric(label='**Average Sale Amount**', value='${:,}'.format(int(sd1_avg_trans)), delta=percent_of_change(sd2_avg_trans, sd1_avg_trans))

            db3.metric(label='**Wholesale Sales**', value='${:,}'.format(int(sd1_wholesale)), delta=percent_of_change(sd2_wholesale, sd1_wholesale))
            db3.metric(label='**Wholesale Transactions**', value='{:,}'.format(int(sd1_wholesale_trans)), delta=percent_of_change(sd2_wholesale_trans, sd1_wholesale_trans))
            db3.metric(label='**Wholesale Average Sale**', value='${:,}'.format(int(sd1_avg_wholesale_trans)), delta=percent_of_change(sd2_avg_wholesale_trans, sd1_avg_wholesale_trans))   

        style_metric_cards()
    
    elif month == 'All':

        total_sales1, total_web_perc1, total_fulcrum_perc1, avg_month1, magic_sales1 = calc_monthly_totals_v2(sales_dict1)
        total_sales2, total_web_perc2, total_fulcrum_perc2, avg_month2, magic_sales2 = calc_monthly_totals_v2(sales_dict2)

        data1 = extract_transaction_data(sales_dict1)
        data2 = extract_transaction_data(sales_dict2)
        web_sales = percent_of_change(data2[3], data1[3])
        web_trans = percent_of_change(data2[6], data1[6])
        web_avg_sale = percent_of_change(data2[0], data1[0])
        var = percent_of_change(data2[5], data1[5])
        avg_sale = percent_of_change(data2[2], data1[2])
        transaction_ct = percent_of_change(data2[8], data1[8])
        fulcrum_sales = percent_of_change(data2[4], data1[4])
        fulcrum_trans = percent_of_change(data2[7], data1[7])
        fulcrum_avg_sale = percent_of_change(data2[1], data1[1])
        avg_per_month = percent_of_change(avg_month2, avg_month1)

        wholesale_sales1, retail_sales1 = wholesale_retail_totals(wvr1)

        db1, db2, db3 = st.columns([.3, .4, .3], gap='medium')      
        
        if wvr2 == None:

            if data1[5] > 550000:
                
                db1.metric('**Website Sales**', '${:,}'.format(int(data1[3])), web_sales)
                db1.metric('**Website Transactions**', '{:,}'.format(data1[6]), web_trans)
                db1.metric('**Website Average Sale**', '${:,}'.format(int(data1[0])), web_avg_sale)
                db1.metric('**Retail Revenue**', '${:,}'.format(int(retail_sales1)), '')
            
                db2.metric('**Total Sales**', '${:,}'.format(int(data1[5])), var)
                db2.metric('**Monthly Average**', '${:,}'.format(int(avg_month1)), avg_per_month)
                db2.metric('**Total Transactions**', '{:,}'.format(data1[8]), transaction_ct)
                db2.metric('**Gross Profit**', '${:,.0f}'.format(profit_23))
                db2.metric(f':red[**MagicFX Sales**]', '${:,}'.format(int(magic_sales1)))
                
                db3.metric('**Fulcrum Sales**', '${:,}'.format(int(data1[4])), fulcrum_sales)
                db3.metric('**Fulcrum Transactions**', '{:,}'.format(data1[7]), fulcrum_trans)
                db3.metric('**Fulcrum Average Sale**', '${:,}'.format(int(data1[1])), fulcrum_avg_sale)
                db3.metric('**Wholesale Revenue**', '${:,}'.format(int(wholesale_sales1)), '')
                
            else:
                db1.metric('**Website Sales**', '${:,}'.format(int(data1[3])), web_sales)
                db1.metric('**Website Transactions**', '{:,}'.format(data1[6]), web_trans)
                db1.metric('**Website Average Sale**', '${:,}'.format(int(data1[0])), web_avg_sale)
                db1.metric('**Retail Revenue**', '${:,}'.format(int(retail_sales1)), '')
            
                db2.metric('**Total Sales**', '${:,}'.format(int(data1[5])), var)
                if datetime.now().month != 1:
                    db2.metric('**Monthly Average**', '${:,}'.format(int(avg_month1)), avg_per_month)
                db2.metric('**Total Transactions**', '{:,}'.format(data1[8]), transaction_ct)
                #db2.metric('**Gross Profit**', '${:,.0f}'.format(profit_23))
                db2.metric(f':red[**MagicFX Sales**]', '${:,}'.format(int(magic_sales1)))
                
                db3.metric('**Fulcrum Sales**', '${:,}'.format(int(data1[4])), fulcrum_sales)
                db3.metric('**Fulcrum Transactions**', '{:,}'.format(data1[7]), fulcrum_trans)
                db3.metric('**Fulcrum Average Sale**', '${:,}'.format(int(data1[4]/data1[7])), fulcrum_avg_sale)
                db3.metric('**Wholesale Revenue**', '${:,}'.format(int(wholesale_sales1)), '')
                

            style_metric_cards()

        else:

            wholesale_sales2, retail_sales2 = wholesale_retail_totals(wvr2)
            wholesale_delta = percent_of_change(wholesale_sales2, wholesale_sales1)
            retail_delta = percent_of_change(retail_sales2, retail_sales1)
            magic_delta = percent_of_change(magic_sales2, magic_sales1)

            if data1[5] > 550000:
        
                db1.metric('**Website Sales**', '${:,}'.format(int(data1[3])), web_sales)
                db1.metric('**Website Transactions**', '{:,}'.format(data1[6]), web_trans)
                db1.metric('**Website Average Sale**', '${:,}'.format(int(data1[0])), web_avg_sale)
                db1.metric('**Retail Revenue**', '${:,}'.format(int(retail_sales1)), retail_delta)
                
                db2.metric('**Total Sales**', '${:,}'.format(int(data1[5])), var)
                db2.metric('**Monthly Average**', '${:,}'.format(int(avg_month1)), avg_per_month)
                db2.metric('**Total Transactions**', '{:,}'.format(data1[8]), transaction_ct)
                db2.metric('**Gross Profit**', '${:,.0f}'.format(profit_24), percent_of_change(profit_23, profit_24))
                db2.metric(f':red[**MagicFX Sales**]', '${:,}'.format(int(magic_sales1)), magic_delta)
                
                db3.metric('**Fulcrum Sales**', '${:,}'.format(int(data1[4])), fulcrum_sales)
                db3.metric('**Fulcrum Transactions**', '{:,}'.format(data1[7]), fulcrum_trans)
                db3.metric('**Fulcrum Average Sale**', '${:,}'.format(int(data1[1])), fulcrum_avg_sale)
                db3.metric('**Wholesale Revenue**', '${:,}'.format(int(wholesale_sales1)), wholesale_delta)
                
            else:
                
                db1.metric('**Website Sales**', '${:,}'.format(int(data1[3])), web_sales)
                db1.metric('**Website Transactions**', '{:,}'.format(data1[6]), web_trans)
                db1.metric('**Website Average Sale**', '${:,}'.format(int(data1[0])), web_avg_sale)
                db1.metric('**Retail Revenue**', '${:,}'.format(int(retail_sales1)), retail_delta)
                
                db2.metric('**Total Sales**', '${:,}'.format(int(data1[5])), var)
                if datetime.now().month != 1:
                    db2.metric('**Monthly Average**', '${:,}'.format(int(avg_month1)), avg_per_month)
                db2.metric('**Total Transactions**', '{:,}'.format(data1[8]), transaction_ct)
                db2.metric(f':red[**MagicFX Sales**]', '${:,}'.format(int(magic_sales1)), magic_delta)
                
                db3.metric('**Fulcrum Sales**', '${:,}'.format(int(data1[4])), fulcrum_sales)
                db3.metric('**Fulcrum Transactions**', '{:,}'.format(data1[7]), fulcrum_trans)
                db3.metric('**Fulcrum Average Sale**', '${:,}'.format(int(data1[1])), fulcrum_avg_sale)
                db3.metric('**Wholesale Revenue**', '${:,}'.format(int(wholesale_sales1)), wholesale_delta)      
                
            style_metric_cards()
        
    else:

        data1 = extract_transaction_data(sales_dict1, month)
        data2 = extract_transaction_data(sales_dict2, month)
        web_sales = percent_of_change(data2[3], data1[3])
        web_trans = percent_of_change(data2[6], data1[6])
        web_avg_sale = percent_of_change(data2[0], data1[0])
        var = percent_of_change(data2[5], data1[5])
        avg_sale = percent_of_change(data2[2], data1[2])
        transaction_ct = percent_of_change(data2[8], data1[8])
        fulcrum_sales = percent_of_change(data2[4], data1[4])
        fulcrum_trans = percent_of_change(data2[7], data1[7])
        fulcrum_avg_sale = percent_of_change(data2[1], data1[1])
        

        db1, db2, db3 = st.columns([.3, .4, .3], gap='medium')

        if wvr2 == None:

            db1.metric('**Website Sales**', '${:,}'.format(int(data1[3])), web_sales)
            db1.metric('**Website Transactions**', '{:,}'.format(data1[6]), web_trans)
            db1.metric('**Website Average Sale**', '${:,}'.format(int(data1[0])), web_avg_sale)
            db1.metric('**Retail Revenue**', '${:,}'.format(int(wvr1[month][1])), '')
        
            db2.metric('**Total Sales**', '${:,}'.format(int(data1[5])), var)
            db2.metric('**Total Transactions**', '{:,}'.format(data1[8]), transaction_ct)
            db2.metric('**Average Sale**', '${:,}'.format(int(data1[2])), avg_sale)
            
            db3.metric('**Fulcrum Sales**', '${:,}'.format(int(data1[4])), fulcrum_sales)
            db3.metric('**Fulcrum Transactions**', '{:,}'.format(data1[7]), fulcrum_trans)
            db3.metric('**Fulcrum Average Sale**', '${:,}'.format(int(data1[1])), fulcrum_avg_sale)
            db3.metric('**Wholesale Revenue**', '${:,}'.format(int(wvr1[month][0])), '')

            style_metric_cards()
        
        else:

            retail_delta = percent_of_change(wvr2[month][1], wvr1[month][1])
            wholesale_delta = percent_of_change(wvr2[month][0], wvr1[month][0])
            
            db1.metric('**Website Sales**', '${:,}'.format(int(data1[3])), web_sales)
            db1.metric('**Website Transactions**', '{:,}'.format(data1[6]), web_trans)
            db1.metric('**Website Average Sale**', '${:,}'.format(int(data1[0])), web_avg_sale)
            db1.metric('**Retail Revenue**', '${:,}'.format(int(wvr1[month][1])), retail_delta)
        
            db2.metric('**Total Sales**', '${:,}'.format(int(data1[5])), var)
            db2.metric('**Total Transactions**', '{:,}'.format(data1[8]), transaction_ct)
            db2.metric('**Average Sale**', '${:,}'.format(int(data1[2])), avg_sale)
            
            db3.metric('**Fulcrum Sales**', '${:,}'.format(int(data1[4])), fulcrum_sales)
            db3.metric('**Fulcrum Transactions**', '{:,}'.format(data1[7]), fulcrum_trans)
            db3.metric('**Fulcrum Average Sale**', '${:,}'.format(int(data1[1])), fulcrum_avg_sale)
            db3.metric('**Wholesale Revenue**', '${:,}'.format(int(wvr1[month][0])), wholesale_delta)
    
            style_metric_cards()
    
    return None


def wholesale_retail_totals(monthly_sales_wVr):
    
    wholesale_totals = 0
    retail_totals = 0

    for month, sales in monthly_sales_wVr.items():
        wholesale_totals += sales[0]
        retail_totals += sales[1]

    return wholesale_totals, retail_totals




@st.cache_data
def quarterly_sales(year):

    q1_end = datetime(year, 3, 31)
    q2_start = datetime(year, 4, 1)
    q2_end = datetime(year, 6, 30)
    q3_start = datetime(year, 7, 1)
    q3_end = datetime(year, 9, 30)
    q4_start = datetime(year, 10, 1)
    q4_end = datetime(year, 12, 31)
    
    
    q1_count = [0, 0]
    q2_count = [0, 0]
    q3_count = [0, 0]
    q4_count = [0, 0]
    
    idx = 0
    
    for sale in df.sales_order:
        order_date = df.iloc[idx].order_date
        if df.iloc[idx].channel[0] == 'F':
            if q1_end.date() >= order_date >= beginning_of_year(q1_end).date():
                q1_count[0] += df.iloc[idx].total_line_item_spend
            elif q2_end.date() >= order_date >= q2_start.date():
                q2_count[0] += df.iloc[idx].total_line_item_spend
            elif q3_end.date() >= order_date >= q3_start.date():
                q3_count[0] += df.iloc[idx].total_line_item_spend
            elif q4_end.date() >= order_date >= q4_start.date():
                q4_count[0] += df.iloc[idx].total_line_item_spend
        else:
            if q1_end.date() >= order_date >= beginning_of_year(q1_end).date():
                q1_count[1] += df.iloc[idx].total_line_item_spend
            elif q2_end.date() >= order_date >= q2_start.date():
                q2_count[1] += df.iloc[idx].total_line_item_spend
            elif q3_end.date() >= order_date >= q3_start.date():
                q3_count[1] += df.iloc[idx].total_line_item_spend
            elif q4_end.date() >= order_date >= q4_start.date():
                q4_count[1] += df.iloc[idx].total_line_item_spend
    
        idx += 1
    
    return q1_count, q2_count, q3_count, q4_count
    

def to_date_revenue():

    # WEB SALES, FULCRUM SALES

    td_22 = [0,0]
    td_23 = [0,0]
    td_24 = [0,0]
    td_25 = [0,0]

    idx = 0
    
    for sale in df.sales_order:
        order_date = df.iloc[idx].order_date
        if df.iloc[idx].channel[0] == 'F':
            if two_years_ago.date() >= order_date >= beginning_of_year(two_years_ago).date():
                td_23[0] += df.iloc[idx].total_line_item_spend
            elif one_year_ago.date() >= order_date >= beginning_of_year(one_year_ago).date():
                td_24[0] += df.iloc[idx].total_line_item_spend
            elif today.date() >= order_date >= beginning_of_year(today).date():
                td_25[0] += df.iloc[idx].total_line_item_spend
            #elif order_date.year == 2025:
                #td_25[0] += df.iloc[idx].total_line_item_spend   
        else:
            if two_years_ago.date() >= order_date >= beginning_of_year(two_years_ago).date():
                td_23[1] += df.iloc[idx].total_line_item_spend
            elif one_year_ago.date() >= order_date >= beginning_of_year(one_year_ago).date():
                td_24[1] += df.iloc[idx].total_line_item_spend
            elif today.date() >= order_date >= beginning_of_year(today).date():
                td_25[1] += df.iloc[idx].total_line_item_spend
            #elif order_date.year == 2025:
                #td_25[1] += df.iloc[idx].total_line_item_spend            

        idx += 1
        
    return td_22, td_23, td_24, td_25



@st.cache_data
def gen_product_list(prod_bom_list):

    prod_list = []

    for dict in prod_bom_list:
        for key, val in dict.items():
            if key in prod_list:
                pass
            else:
                prod_list.append(key)

    return prod_list
        


@st.cache_data
def profit_by_type(year_list, product_type_list):

    y23 = [0, 3, 6, 9, 12]
    y24 = [1, 4, 7, 10, 13]
    y25 = [2, 5, 8, 11, 14]

    total_profit = 0
    
    if 'Jet' in product_type_list:

        if '2025' in year_list:

            for jet in annual_product_totals[2]:
                total_profit += annual_product_totals[2][jet][1] - (annual_product_totals[2][jet][0] * bom_cost_jet[jet]) 
        
        if '2024' in year_list:

            for jet in annual_product_totals[1]:
                total_profit += annual_product_totals[1][jet][1] - (annual_product_totals[1][jet][0] * bom_cost_jet[jet]) 

        if '2023' in year_list:

            for jet in annual_product_totals[0]:
                total_profit += annual_product_totals[0][jet][1] - (annual_product_totals[0][jet][0] * bom_cost_jet[jet]) 

    if 'Control' in product_type_list:
        
        if '2025' in year_list:
        
            for cntl in annual_product_totals[5]:
                total_profit += annual_product_totals[5][cntl][1] - (annual_product_totals[5][cntl][0] * bom_cost_control[cntl]) 
        
        if '2024' in year_list:
        
            for cntl in annual_product_totals[4]:
                total_profit += annual_product_totals[4][cntl][1] - (annual_product_totals[4][cntl][0] * bom_cost_control[cntl]) 
        
        if '2023' in year_list:
        
            for cntl in annual_product_totals[3]:
                total_profit += annual_product_totals[3][cntl][1] - (annual_product_totals[3][cntl][0] * bom_cost_control[cntl])

    if 'Handheld' in product_type_list:
        
        if '2025' in year_list:
        
            for hh in annual_product_totals[8]:
                total_profit += annual_product_totals[8][hh][1] - (annual_product_totals[8][hh][0] * bom_cost_hh[hh]) 
        
        if '2024' in year_list:
        
            for hh in annual_product_totals[7]:
                total_profit += annual_product_totals[7][hh][1] - (annual_product_totals[7][hh][0] * bom_cost_hh[hh]) 
        
        if '2023' in year_list:
        
            for hh in annual_product_totals[6]:
                total_profit += annual_product_totals[6][hh][1] - (annual_product_totals[6][hh][0] * bom_cost_hh[hh])

    if 'Hose' in product_type_list:
        
        if '2025' in year_list:
        
            for hose in annual_product_totals[11]:
                if hose == 'CUSTOM':
                    pass
                else:
                    total_profit += annual_product_totals[11][hose][1] - (annual_product_totals[11][hose][0] * bom_cost_hose[hose]) 
        
        if '2024' in year_list:
        
            for hose in annual_product_totals[10]:
                if hose == 'CUSTOM':
                    pass
                else:
                    total_profit += annual_product_totals[10][hose][1] - (annual_product_totals[10][hose][0] * bom_cost_hose[hose]) 
        
        if '2023' in year_list:
        
            for hose in annual_product_totals[9]:
                if hose == 'CUSTOM':
                    pass
                else:
                    total_profit += annual_product_totals[9][hose][1] - (annual_product_totals[9][hose][0] * bom_cost_hose[hose])

    if 'Accessory' in product_type_list:
        
        if '2025' in year_list:
        
            for acc in annual_product_totals[14]:
                total_profit += annual_product_totals[14][acc][1] - (annual_product_totals[14][acc][0] * bom_cost_acc[acc]) 
        
        if '2024' in year_list:
        
            for acc in annual_product_totals[13]:
                total_profit += annual_product_totals[13][acc][1] - (annual_product_totals[13][acc][0] * bom_cost_acc[acc]) 
        
        if '2023' in year_list:
        
            for acc in annual_product_totals[12]:
                total_profit += annual_product_totals[12][acc][1] - (annual_product_totals[12][acc][0] * bom_cost_acc[acc])

    
    return total_profit

@st.cache_data
def product_annual_totals(prod_dict_list):

    jet_list = ['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp']
    control_list = ['The Button', 'Shostarter', 'Shomaster']
    
    totals = []
    
    for year_data in prod_dict_list:
        temp_dict = {}
        for month, product in year_data.items():
            for prod, val in product.items():
                if prod == 'CC-RC-2430':
                    temp_dict[prod] = [0,0,0,0,0]
                elif prod in jet_list or prod in control_list:
                    temp_dict[prod] = [0,0,0]
                else:
                    temp_dict[prod] = [0,0]
    
        
        for month, product in year_data.items():
            for prod, val in product.items():
                if prod == 'CC-RC-2430':
                    temp_dict[prod][0] += val[0]
                    temp_dict[prod][1] += val[1]
                    temp_dict[prod][2] += val[2]
                    temp_dict[prod][3] += val[3]
                    temp_dict[prod][4] += val[4]
                elif prod in jet_list or prod in control_list:
                    temp_dict[prod][0] += val[0]
                    temp_dict[prod][1] += val[1]
                    temp_dict[prod][2] += val[2]
                else:
                    temp_dict[prod][0] += val[0]
                    temp_dict[prod][1] += val[1]
            

        totals.append(temp_dict)

    return totals

@st.cache_data
def magic_sales_data():
    
    mfx_list = []

    mfx_profit = 0
    mfx_costs = 0
    mfx_rev = 0

    
    idx = 0
    
    for item in df_cogs.item:

        if item[:3] == 'MFX' or item[:5] == 'Magic':
            mfx_list.append('{} x {} = ${:,.2f} total, ${:,.2f} each. Total Profit = ${:,.2f}'.format(item, df_cogs.iloc[idx].quantity, df_cogs.iloc[idx].total_price, df_cogs.iloc[idx].unit_price, (df_cogs.iloc[idx].total_price - df_cogs.iloc[idx].total_cost)))
            mfx_profit += df_cogs.iloc[idx].total_price - df_cogs.iloc[idx].total_cost
            mfx_costs += df_cogs.iloc[idx].total_cost
            mfx_rev += df_cogs.iloc[idx].total_price


        idx += 1
        
    return mfx_rev, mfx_costs, mfx_profit


mfx_rev, mfx_costs, mfx_profit = magic_sales_data()


def daily_sales(month):

    daily_sales23 = []
    daily_sales24 = []
    daily_sales25 = []
                
    month_num = month_to_num(month)

    for i in range(days_in_month(month)):
        daily_sales23.append(0)
        daily_sales24.append(0)
        daily_sales25.append(0)
        
    idx = 0 
    
    for sale in df.sales_order:
        if df.iloc[idx].order_date.month == int(month_num):
            if df.iloc[idx].order_date.year == 2025:
                daily_sales25[(df.iloc[idx].order_date.day) - 1] += df.iloc[idx].total_line_item_spend
            if df.iloc[idx].order_date.year == 2024:
                daily_sales24[(df.iloc[idx].order_date.day) - 1] += df.iloc[idx].total_line_item_spend
            if df.iloc[idx].order_date.year == 2023:
                daily_sales23[(df.iloc[idx].order_date.day) - 1] += df.iloc[idx].total_line_item_spend

        idx += 1
            
    return daily_sales23, daily_sales24, daily_sales25

def range_sales(num):

    daily_sales23 = []
    daily_sales24 = []
    daily_sales25 = []

    delta_range = timedelta(days=num)
    
    for i in range(num):
        daily_sales23.append(0)
        daily_sales24.append(0)
        daily_sales25.append(0)


        
    idx = 0 
    
    for sale in df.sales_order:
        if today.date() >= df.iloc[idx].order_date >= (today - delta_range).date():
            daily_sales25[-((today.date() - (df.iloc[idx].order_date)).days)] += df.iloc[idx].total_line_item_spend
            
        elif one_year_ago.date() >= df.iloc[idx].order_date >= (one_year_ago - delta_range).date():
            daily_sales24[-((one_year_ago.date() - (df.iloc[idx].order_date)).days)] += df.iloc[idx].total_line_item_spend
            
        elif two_years_ago.date() >= df.iloc[idx].order_date >= (two_years_ago - delta_range).date():
            daily_sales23[-((two_years_ago.date() - (df.iloc[idx].order_date)).days)] += df.iloc[idx].total_line_item_spend


        idx += 1

    daily_sales23.reverse()
    daily_sales24.reverse()
    daily_sales25.reverse()
    
            
    return daily_sales23, daily_sales24, daily_sales25


def range_sales(num):

    daily_sales23 = []
    daily_sales24 = []
    daily_sales25 = []

    delta_range = timedelta(days=num)
    
    for i in range(num):
        daily_sales23.append(0)
        daily_sales24.append(0)
        daily_sales25.append(0)


        
    idx = 0 
    
    for sale in df.sales_order:
        if today.date() >= df.iloc[idx].order_date >= (today - delta_range).date():
            daily_sales25[-((today.date() - (df.iloc[idx].order_date)).days)] += df.iloc[idx].total_line_item_spend
            
        elif one_year_ago.date() >= df.iloc[idx].order_date >= (one_year_ago - delta_range).date():
            daily_sales24[-((one_year_ago.date() - (df.iloc[idx].order_date)).days)] += df.iloc[idx].total_line_item_spend
            
        elif two_years_ago.date() >= df.iloc[idx].order_date >= (two_years_ago - delta_range).date():
            daily_sales23[-((two_years_ago.date() - (df.iloc[idx].order_date)).days)] += df.iloc[idx].total_line_item_spend


        idx += 1

    daily_sales23.reverse()
    daily_sales24.reverse()
    daily_sales25.reverse()
    
            
    return daily_sales23, daily_sales24, daily_sales25


def display_daily_plot(month, years=['All']):
    
    daily23, daily24, daily25 = daily_sales(month)
    col1.write(daily23)

    x = [i for i in range(len(daily24))]

    fig, ax = plt.subplots()

    if years == ['All']:
    
        ax.plot(x, daily23, label='2023', color='darkgreen', linewidth=2)
        ax.plot(x, daily24, label='2024', color='white', linewidth=2)
        ax.plot(x, daily25, label='2025', color='limegreen', linewidth=2)
        ax.set_facecolor('#000000')
        fig.set_facecolor('#000000')
        plt.yticks([1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000])
        plt.tick_params(axis='x', colors='white')
        plt.tick_params(axis='y', colors='white')
        plt.ylim(0, 20000)
        #plt.fill_between(x, daily23, color='darkgreen')
        #plt.fill_between(x, daily24, color='white', alpha=0.7)
        #plt.fill_between(x, daily25, color='limegreen')
        #plt.title('Annual Comparison', color='green')
        plt.figure(figsize=(10,10))
    
        fig.legend()
        
        col2.pyplot(fig)

    elif years == ['2025']:
        
        ax.plot(x, daily25, label='2025', color='limegreen', linewidth=2)
        ax.set_facecolor('#000000')
        fig.set_facecolor('#000000')
        plt.yticks([1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000])
   
        plt.tick_params(axis='x', colors='white')
        plt.tick_params(axis='y', colors='white')
        plt.ylim(0, 20000)
        plt.fill_between(x, daily25, color='limegreen')
        #plt.title('Annual Comparison', color='green')
        plt.figure(figsize=(10,10))
    
        #fig.legend()

        col2.pyplot(fig)
        
    elif years == ['2024']:
        
        ax.plot(x, daily24, label='2024', color='limegreen', linewidth=2)
        ax.set_facecolor('#000000')
        fig.set_facecolor('#000000')
        plt.yticks([1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000])
   
        plt.tick_params(axis='x', colors='white')
        plt.tick_params(axis='y', colors='white')
        plt.ylim(0, 20000)
        plt.fill_between(x, daily24, color='limegreen')
        #plt.title('Annual Comparison', color='green')
        plt.figure(figsize=(10,10))
    
        #fig.legend()

        col2.pyplot(fig)

    elif years == ['2023']:
        
        ax.plot(x, daily23, label='2023', color='limegreen', linewidth=2)
        ax.set_facecolor('#000000')
        fig.set_facecolor('#000000')
        plt.yticks([1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000])
   
        plt.tick_params(axis='x', colors='white')
        plt.tick_params(axis='y', colors='white')
        plt.ylim(0, 20000)
        plt.fill_between(x, daily23, color='limegreen')
        #plt.title('Annual Comparison', color='green')
        plt.figure(figsize=(10,10))
    
        #fig.legend()

        col2.pyplot(fig)
    
    return None

df_hist['order_date'] = pd.to_datetime(df_hist['order_date'])


@st.cache_data
def hist_cust_sales():
    cust_dict = {cust: 0 for cust in master_customer_list}  # Initialize dictionary

    for cust, sale in zip(df_hist.customer, df_hist.total_sale):  # Iterate over rows
        try:
            cust_dict[cust] += float(sale)  # Add sale amount to the correct customer
        except:
            pass  # Skip invalid entries
    
    return cust_dict

@st.cache_data
def hist_annual_sales():

    
    sales13 = {'January': [[0,0],[0,0]], 'February': [[0,0],[0,0]], 'March': [[0,0],[0,0]], 'April': [[0,0],[0,0]], 'May': [[0,0],[0,0]], 'June': [[0,0],[0,0]], 'July': [[0,0],[0,0]], 'August': [[0,0],[0,0]], 'September': [[0,0],[0,0]], 'October': [[0,0],[0,0]], 'November': [[0,0],[0,0]], 'December': [[0,0],[0,0]]}
    sales14 = {'January': [[0,0],[0,0]], 'February': [[0,0],[0,0]], 'March': [[0,0],[0,0]], 'April': [[0,0],[0,0]], 'May': [[0,0],[0,0]], 'June': [[0,0],[0,0]], 'July': [[0,0],[0,0]], 'August': [[0,0],[0,0]], 'September': [[0,0],[0,0]], 'October': [[0,0],[0,0]], 'November': [[0,0],[0,0]], 'December': [[0,0],[0,0]]}
    sales15 = {'January': [[0,0],[0,0]], 'February': [[0,0],[0,0]], 'March': [[0,0],[0,0]], 'April': [[0,0],[0,0]], 'May': [[0,0],[0,0]], 'June': [[0,0],[0,0]], 'July': [[0,0],[0,0]], 'August': [[0,0],[0,0]], 'September': [[0,0],[0,0]], 'October': [[0,0],[0,0]], 'November': [[0,0],[0,0]], 'December': [[0,0],[0,0]]}
    sales16 = {'January': [[0,0],[0,0]], 'February': [[0,0],[0,0]], 'March': [[0,0],[0,0]], 'April': [[0,0],[0,0]], 'May': [[0,0],[0,0]], 'June': [[0,0],[0,0]], 'July': [[0,0],[0,0]], 'August': [[0,0],[0,0]], 'September': [[0,0],[0,0]], 'October': [[0,0],[0,0]], 'November': [[0,0],[0,0]], 'December': [[0,0],[0,0]]}
    sales17 = {'January': [[0,0],[0,0]], 'February': [[0,0],[0,0]], 'March': [[0,0],[0,0]], 'April': [[0,0],[0,0]], 'May': [[0,0],[0,0]], 'June': [[0,0],[0,0]], 'July': [[0,0],[0,0]], 'August': [[0,0],[0,0]], 'September': [[0,0],[0,0]], 'October': [[0,0],[0,0]], 'November': [[0,0],[0,0]], 'December': [[0,0],[0,0]]}
    sales18 = {'January': [[0,0],[0,0]], 'February': [[0,0],[0,0]], 'March': [[0,0],[0,0]], 'April': [[0,0],[0,0]], 'May': [[0,0],[0,0]], 'June': [[0,0],[0,0]], 'July': [[0,0],[0,0]], 'August': [[0,0],[0,0]], 'September': [[0,0],[0,0]], 'October': [[0,0],[0,0]], 'November': [[0,0],[0,0]], 'December': [[0,0],[0,0]]}
    sales19 = {'January': [[0,0],[0,0]], 'February': [[0,0],[0,0]], 'March': [[0,0],[0,0]], 'April': [[0,0],[0,0]], 'May': [[0,0],[0,0]], 'June': [[0,0],[0,0]], 'July': [[0,0],[0,0]], 'August': [[0,0],[0,0]], 'September': [[0,0],[0,0]], 'October': [[0,0],[0,0]], 'November': [[0,0],[0,0]], 'December': [[0,0],[0,0]]}
    sales20 = {'January': [[0,0],[0,0]], 'February': [[0,0],[0,0]], 'March': [[0,0],[0,0]], 'April': [[0,0],[0,0]], 'May': [[0,0],[0,0]], 'June': [[0,0],[0,0]], 'July': [[0,0],[0,0]], 'August': [[0,0],[0,0]], 'September': [[0,0],[0,0]], 'October': [[0,0],[0,0]], 'November': [[0,0],[0,0]], 'December': [[0,0],[0,0]]}
    sales21 = {'January': [[0,0],[0,0]], 'February': [[0,0],[0,0]], 'March': [[0,0],[0,0]], 'April': [[0,0],[0,0]], 'May': [[0,0],[0,0]], 'June': [[0,0],[0,0]], 'July': [[0,0],[0,0]], 'August': [[0,0],[0,0]], 'September': [[0,0],[0,0]], 'October': [[0,0],[0,0]], 'November': [[0,0],[0,0]], 'December': [[0,0],[0,0]]}
    sales22 = {'January': [[0,0],[0,0]], 'February': [[0,0],[0,0]], 'March': [[0,0],[0,0]], 'April': [[0,0],[0,0]], 'May': [[0,0],[0,0]], 'June': [[0,0],[0,0]], 'July': [[0,0],[0,0]], 'August': [[0,0],[0,0]], 'September': [[0,0],[0,0]], 'October': [[0,0],[0,0]], 'November': [[0,0],[0,0]], 'December': [[0,0],[0,0]]}
    
    idx = 0

    
    for sale in df_hist.customer:


        if sale in wholesale_list:

            if df_hist.iloc[idx].order_date.date().year == 2013:
                sales13[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][0] += float(df_hist.iloc[idx].total_sale)
                sales13[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2014:
                sales14[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][0] += float(df_hist.iloc[idx].total_sale)
                sales14[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2015:
                sales15[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][0] += float(df_hist.iloc[idx].total_sale)
                sales15[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2016:
                sales16[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][0] += float(df_hist.iloc[idx].total_sale)
                sales16[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2017:
                sales17[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][0] += float(df_hist.iloc[idx].total_sale)
                sales17[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2018:
                sales18[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][0] += float(df_hist.iloc[idx].total_sale)
                sales18[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2019:
                sales19[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][0] += float(df_hist.iloc[idx].total_sale)
                sales19[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2020:
                sales20[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][0] += float(df_hist.iloc[idx].total_sale)
                sales20[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2021:
                sales21[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][0] += float(df_hist.iloc[idx].total_sale)
                sales21[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][1] += 1
                
            if df_hist.iloc[idx].order_date.date().year == 2022:
                sales22[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][0] += float(df_hist.iloc[idx].total_sale)
                sales22[num_to_month(df_hist.iloc[idx].order_date.date().month)][0][1] += 1

        else:
            
            if df_hist.iloc[idx].order_date.date().year == 2013:
                sales13[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][0] += float(df_hist.iloc[idx].total_sale)
                sales13[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2014:
                sales14[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][0] += float(df_hist.iloc[idx].total_sale)
                sales14[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2015:
                sales15[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][0] += float(df_hist.iloc[idx].total_sale)
                sales15[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2016:
                sales16[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][0] += float(df_hist.iloc[idx].total_sale)
                sales16[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2017:
                sales17[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][0] += float(df_hist.iloc[idx].total_sale)
                sales17[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2018:
                sales18[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][0] += float(df_hist.iloc[idx].total_sale)
                sales18[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2019:
                sales19[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][0] += float(df_hist.iloc[idx].total_sale)
                sales19[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2020:
                sales20[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][0] += float(df_hist.iloc[idx].total_sale)
                sales20[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][1] += 1
    
            if df_hist.iloc[idx].order_date.date().year == 2021:
                sales21[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][0] += float(df_hist.iloc[idx].total_sale)
                sales21[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][1] += 1
                
            if df_hist.iloc[idx].order_date.date().year == 2022:
                sales22[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][0] += float(df_hist.iloc[idx].total_sale)
                sales22[num_to_month(df_hist.iloc[idx].order_date.date().month)][1][1] += 1

        idx += 1
        
    return sales13, sales14, sales15, sales16, sales17, sales18, sales19, sales20, sales21, sales22


@st.cache_data
def hist_quarterly_sales():
    
    qs13 = [(sales13['January'][0][0]+ sales13['February'][0][0] + sales13['March'][0][0] + sales13['January'][1][0] + sales13['February'][1][0] + sales13['March'][1][0]), (sales13['April'][0][0] + sales13['May'][0][0] + sales13['June'][0][0] + sales13['April'][1][0] + sales13['May'][1][0] + sales13['June'][1][0]), (sales13['July'][0][0] + sales13['August'][0][0] + sales13['September'][0][0] + sales13['July'][1][0]+ sales13['August'][1][0] + sales13['September'][1][0]), (sales13['October'][0][0] + sales13['November'][0][0] + sales13['December'][0][0] + sales13['October'][1][0]+ sales13['November'][1][0] + sales13['December'][1][0])]
    qs14 = [(sales14['January'][0][0]+ sales14['February'][0][0] + sales14['March'][0][0] + sales14['January'][1][0] + sales14['February'][1][0] + sales14['March'][1][0]), (sales14['April'][0][0] + sales14['May'][0][0] + sales14['June'][0][0] + sales14['April'][1][0] + sales14['May'][1][0] + sales14['June'][1][0]), (sales14['July'][0][0] + sales14['August'][0][0] + sales14['September'][0][0] + sales14['July'][1][0]+ sales14['August'][1][0] + sales14['September'][1][0]), (sales14['October'][0][0] + sales14['November'][0][0] + sales14['December'][0][0] + sales14['October'][1][0]+ sales14['November'][1][0] + sales14['December'][1][0])]
    qs15 = [(sales15['January'][0][0]+ sales15['February'][0][0] + sales15['March'][0][0] + sales15['January'][1][0] + sales15['February'][1][0] + sales15['March'][1][0]), (sales15['April'][0][0] + sales15['May'][0][0] + sales15['June'][0][0] + sales15['April'][1][0] + sales15['May'][1][0] + sales15['June'][1][0]), (sales15['July'][0][0] + sales15['August'][0][0] + sales15['September'][0][0] + sales15['July'][1][0]+ sales15['August'][1][0] + sales15['September'][1][0]), (sales15['October'][0][0] + sales15['November'][0][0] + sales15['December'][0][0] + sales15['October'][1][0]+ sales15['November'][1][0] + sales15['December'][1][0])]
    qs16 = [(sales16['January'][0][0]+ sales16['February'][0][0] + sales16['March'][0][0] + sales16['January'][1][0] + sales16['February'][1][0] + sales16['March'][1][0]), (sales16['April'][0][0] + sales16['May'][0][0] + sales16['June'][0][0] + sales16['April'][1][0] + sales16['May'][1][0] + sales16['June'][1][0]), (sales16['July'][0][0] + sales16['August'][0][0] + sales16['September'][0][0] + sales16['July'][1][0]+ sales16['August'][1][0] + sales16['September'][1][0]), (sales16['October'][0][0] + sales16['November'][0][0] + sales16['December'][0][0] + sales16['October'][1][0]+ sales16['November'][1][0] + sales16['December'][1][0])]
    qs17 = [(sales17['January'][0][0]+ sales17['February'][0][0] + sales17['March'][0][0] + sales17['January'][1][0] + sales17['February'][1][0] + sales17['March'][1][0]), (sales17['April'][0][0] + sales17['May'][0][0] + sales17['June'][0][0] + sales17['April'][1][0] + sales17['May'][1][0] + sales17['June'][1][0]), (sales17['July'][0][0] + sales17['August'][0][0] + sales17['September'][0][0] + sales17['July'][1][0]+ sales17['August'][1][0] + sales17['September'][1][0]), (sales17['October'][0][0] + sales17['November'][0][0] + sales17['December'][0][0] + sales17['October'][1][0]+ sales17['November'][1][0] + sales17['December'][1][0])]
    qs18 = [(sales18['January'][0][0]+ sales18['February'][0][0] + sales18['March'][0][0] + sales18['January'][1][0] + sales18['February'][1][0] + sales18['March'][1][0]), (sales18['April'][0][0] + sales18['May'][0][0] + sales18['June'][0][0] + sales18['April'][1][0] + sales18['May'][1][0] + sales18['June'][1][0]), (sales18['July'][0][0] + sales18['August'][0][0] + sales18['September'][0][0] + sales18['July'][1][0]+ sales18['August'][1][0] + sales18['September'][1][0]), (sales18['October'][0][0] + sales18['November'][0][0] + sales18['December'][0][0] + sales18['October'][1][0]+ sales18['November'][1][0] + sales18['December'][1][0])]   
    qs19 = [(sales19['January'][0][0]+ sales19['February'][0][0] + sales19['March'][0][0] + sales19['January'][1][0] + sales19['February'][1][0] + sales19['March'][1][0]), (sales19['April'][0][0] + sales19['May'][0][0] + sales19['June'][0][0] + sales19['April'][1][0] + sales19['May'][1][0] + sales19['June'][1][0]), (sales19['July'][0][0] + sales19['August'][0][0] + sales19['September'][0][0] + sales19['July'][1][0]+ sales19['August'][1][0] + sales19['September'][1][0]), (sales19['October'][0][0] + sales19['November'][0][0] + sales19['December'][0][0] + sales19['October'][1][0]+ sales19['November'][1][0] + sales19['December'][1][0])]
    qs20 = [(sales20['January'][0][0]+ sales20['February'][0][0] + sales20['March'][0][0] + sales20['January'][1][0] + sales20['February'][1][0] + sales20['March'][1][0]), (sales20['April'][0][0] + sales20['May'][0][0] + sales20['June'][0][0] + sales20['April'][1][0] + sales20['May'][1][0] + sales20['June'][1][0]), (sales20['July'][0][0] + sales20['August'][0][0] + sales20['September'][0][0] + sales20['July'][1][0]+ sales20['August'][1][0] + sales20['September'][1][0]), (sales20['October'][0][0] + sales20['November'][0][0] + sales20['December'][0][0] + sales20['October'][1][0]+ sales20['November'][1][0] + sales20['December'][1][0])]
    qs21 = [(sales21['January'][0][0]+ sales21['February'][0][0] + sales21['March'][0][0] + sales21['January'][1][0] + sales21['February'][1][0] + sales21['March'][1][0]), (sales21['April'][0][0] + sales21['May'][0][0] + sales21['June'][0][0] + sales21['April'][1][0] + sales21['May'][1][0] + sales21['June'][1][0]), (sales21['July'][0][0] + sales21['August'][0][0] + sales21['September'][0][0] + sales21['July'][1][0]+ sales21['August'][1][0] + sales21['September'][1][0]), (sales21['October'][0][0] + sales21['November'][0][0] + sales21['December'][0][0] + sales21['October'][1][0]+ sales21['November'][1][0] + sales21['December'][1][0])]
    qs22 = [(sales22['January'][0][0]+ sales22['February'][0][0] + sales22['March'][0][0] + sales22['January'][1][0] + sales22['February'][1][0] + sales22['March'][1][0]), (sales22['April'][0][0] + sales22['May'][0][0] + sales22['June'][0][0] + sales22['April'][1][0] + sales22['May'][1][0] + sales22['June'][1][0]), (sales22['July'][0][0] + sales22['August'][0][0] + sales22['September'][0][0] + sales22['July'][1][0]+ sales22['August'][1][0] + sales22['September'][1][0]), (sales22['October'][0][0] + sales22['November'][0][0] + sales22['December'][0][0] + sales22['October'][1][0]+ sales22['November'][1][0] + sales22['December'][1][0])]
    
    return qs13, qs14, qs15, qs16, qs17, qs18, qs19, qs20, qs21, qs22



# HISTORICAL SALES DATA
sales13, sales14, sales15, sales16, sales17, sales18, sales19, sales20, sales21, sales22 = hist_annual_sales()    



# MAKE TO-DATE REV GLOBAL FOR USE WITH PRODUCTS
jet23, jet24, jet25, control23, control24, control25, handheld23, handheld24, handheld25, hose23, hose24, hose25, acc23, acc24, acc25 = collect_product_data(df)
hose_detail25 = organize_hose_data(hose25)
hose_detail24 = organize_hose_data(hose24)
hose_detail23 = organize_hose_data(hose23)


# CALCULATE ANNUAL PRODUCT TOTALS
annual_product_totals = product_annual_totals([jet23, jet24, jet25, control23, control24, control25, handheld23, handheld24, handheld25, hose23, hose24, hose25, acc23, acc24, acc25])

#bom_list = [bom_cost_jet, bom_cost_control, bom_cost_hh, bom_cost_hose, bom_cost_acc]
#prod_list = gen_product_list(bom_list)

td_22, td_23, td_24, td_25 = to_date_revenue()

td_22_tot = td_22[0] + td_22[1]
td_23_tot = td_23[0] + td_23[1]
td_24_tot = td_24[0] + td_24[1]
td_25_tot = td_25[0] + td_25[1]


sales_dict_23 = get_monthly_sales_v2(df, 2023)
total_23, web_23, ful_23, avg_23, magic23 = calc_monthly_totals_v2(sales_dict_23)

sales_dict_24 = get_monthly_sales_v2(df, 2024)
total_24, web_24, ful_24, avg_24, magic24 = calc_monthly_totals_v2(sales_dict_24)

sales_dict_25 = get_monthly_sales_v2(df, 2025)
total_25, web_25, ful_25, avg_25, magic25 = calc_monthly_totals_v2(sales_dict_25)


#profit_25 = profit_by_type(['2025'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory'])
profit_24 = profit_by_type(['2024'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory']) + mfx_profit
profit_23 = profit_by_type(['2023'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory'])




if task_choice == 'Dashboard':

    # QUARTERLY TOTALS
    q1_25, q2_25, q3_25, q4_25 = quarterly_sales(2025)
    q1_24, q2_24, q3_24, q4_24 = quarterly_sales(2024)
    q1_23, q2_23, q3_23, q4_23 = quarterly_sales(2023)
    qs13, qs14, qs15, qs16, qs17, qs18, qs19, qs20, qs21, qs22 = hist_quarterly_sales()
    #q1_22, q2_22, q3_22, q4_22 = [52371, 52371], [222874.37, 222874.38], [246693.76, 246693.76], [219790.14, 219790.14]
    
    ### WHOLESALE VS RETAIL MONTHLY TOTALS
    
    wvr_23_months = get_monthly_sales_wvr(df, 2023)
    wvr_24_months = get_monthly_sales_wvr(df, 2024)
    wvr_25_months = get_monthly_sales_wvr(df, 2025)
    wvr_25_ytd, wvr_24_ytd, wvr_23_ytd = get_monthly_sales_wvr_ytd()
    
    wvr_23_totals = wholesale_retail_totals(wvr_23_months)
    wvr_23_totals_ytd = wholesale_retail_totals(wvr_23_ytd)
    wvr_24_totals = wholesale_retail_totals(wvr_24_months)  
    wvr_23_totals_ytd = wholesale_retail_totals(wvr_24_ytd)
    wvr_24_totals = wholesale_retail_totals(wvr_24_months)
    wvr_25_totals_ytd = wholesale_retail_totals(wvr_25_ytd)

    #sales_dict_23 = get_monthly_sales_v2(df, 2023)
    #total_23, web_23, ful_23, avg_23, magic23 = calc_monthly_totals_v2(sales_dict_23)
    
    #sales_dict_24 = get_monthly_sales_v2(df, 2024)
    #total_24, web_24, ful_24, avg_24, magic_24 = calc_monthly_totals_v2(sales_dict_24)

    #sales_dict_25 = get_monthly_sales_v2(df, 2025)
    #total_25, web_25, ful_25, avg_25, magic_25 = calc_monthly_totals_v2(sales_dict_25)

    td_sales25, td_sales24, td_sales23 = get_monthly_sales_ytd()

    #td_total23, td_web_23, td_ful_23, td_avg_23, td_magic_23 = calc_monthly_totals_v2(td_sales23)
    #td_total24, td_web_24, td_ful_24, td_avg_24, td_magic_24 = calc_monthly_totals_v2(td_sales24)
    
    ### COMPILE DATA FOR SALES REPORTS ###
    total_22 = 1483458.64
    avg_22 = 147581.12
    trans_22 = 1266
    trans_avg_22 = 126.6
    sales_dict_22 = {'January': [[0, 1], [0, 1], [0]], 
                     'February': [[0, 1], [7647.42, 25], [0]], 
                     'March': [[48547.29, 80], [48457.28, 30], [0]], 
                     'April': [[69081.04, 86], [69081.05, 30], [0]], 
                     'May': [[64976.18, 72], [64976.18, 40], [0]], 
                     'June': [[88817.15, 90], [88817.15, 51], [0]], 
                     'July': [[104508.24, 86], [104508.24, 30], [0]], 
                     'August': [[74166.78, 94], [74166.78, 50], [0]], 
                     'September': [[68018.74, 99], [68018.74, 50], [0]], 
                     'October': [[86874.13, 126], [86874.13, 40], [0]], 
                     'November': [[57760.81, 77], [57760.82, 30], [0]], 
                     'December': [[75155.19, 64], [75155.20, 30], [0]]}
    
    x = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    y2022 = []
    y2023 = []
    y2024 = []
    y2025 = []

    for key, val in sales_dict_22.items():
        y2022.append(val[0][0] + val[1][0])
    for key, val in sales_dict_23.items():
        y2023.append(val[0][0] + val[1][0])
    for key, val in sales_dict_24.items():
        y2024.append(val[0][0] + val[1][0])
    for key, val in sales_dict_25.items():
        y2025.append(val[0][0] + val[1][0])
    
    fig, ax = plt.subplots()
    
    ax.plot(x, y2022, label='2022', color='limegreen', linewidth=4.5)
    ax.plot(x, y2023, label='2023', color='white', linewidth=4.5)
    ax.plot(x, y2024, label='2024', color='grey', linewidth=4.5)
    ax.set_facecolor('#000000')
    fig.set_facecolor('#000000')
    plt.yticks([20000, 40000, 60000, 80000, 100000, 120000, 140000, 160000, 180000, 200000, 220000, 240000, 260000, 280000])
    plt.tick_params(axis='x', colors='white')
    plt.tick_params(axis='y', colors='white')
    #plt.title('Annual Comparison', color='green')
    plt.figure(figsize=(12,6))

    fig.legend()

    ### SALES CHANNEL BREAKDOWN ###
    web_avg_perc = (web_23 + web_24)/2
    ful_avg_perc = (ful_23 + ful_24)/2

    col1, col2, col3 = st.columns([.29, .42, .29], gap='medium')
    colx, coly, colz = st.columns([.29, .42, .29], gap='medium')
    
    col1.header('Annual Comparison')
    col1.pyplot(fig)
    
    with colx:
        
        st.header('To-Date Sales')
        
        cola, colb, colc = st.columns(3)

        cola.metric('**2025 Total**', '${:,}'.format(int(td_25[1] + td_25[0])), percent_of_change((td_24[0] + td_24[1]), (td_25[0] + td_25[1])))
        cola.metric('**2025 Web**', '${:,}'.format(int(td_25[0])), percent_of_change(td_24[0], td_25[0]))
        cola.metric('**2025 Fulcrum**', '${:,}'.format(int(td_25[1])), percent_of_change(td_24[1], td_25[1]))
        
        colb.metric('**2024 Total**', '${:,}'.format(int(td_24[1] + td_24[0])), percent_of_change((td_23[0] + td_23[1]), (td_24[0] + td_24[1])))
        colb.metric('**2024 Web**', '${:,}'.format(int(td_24[0])), percent_of_change(td_23[0], td_24[0]))
        colb.metric('**2024 Fulcrum**', '${:,}'.format(int(td_24[1])), percent_of_change(td_23[1], td_24[1]))
        
        colc.metric('**2023 Total**', '${:,}'.format(int(td_23[1] + td_23[0])), '100%')
        colc.metric('**2023 Web**', '${:,}'.format(int(td_23[0])), '100%')
        colc.metric('**2023 Fulcrum**', '${:,}'.format(int(td_23[1])), '100%')

        style_metric_cards()
    
    with col2:
        year_select = ui.tabs(options=[2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013], default_value=2025, key='Year')     
    
        #tot_vs_ytd = ui.tabs(options=['Totals', 'YTD'], default_value='Totals')

    
    ### DISPLAY SALES METRICS ###

        if year_select == 2025:
            
            display_metrics(sales_dict_25, td_sales24, wvr1=wvr_25_months, wvr2=wvr_24_ytd)
    
            with col3:
                
                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales_dict_25))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col6.metric('**Q1 Web Sales**', '${:,}'.format(int(q1_25[0])), percent_of_change(q1_24[0], q1_25[0]))
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(q1_25[0] + q1_25[1])), percent_of_change((q1_24[0] + q1_24[1]), (q1_25[0] + q1_25[1])))
                col8.metric('**Q1 Fulcrum Sales**', '${:,}'.format(int(q1_25[1])), percent_of_change(q1_24[1], q1_25[1]))
                
                col6.metric('**Q2 Web Sales**', '${:,}'.format(int(q2_25[0])), percent_of_change(q2_23[0], q2_24[0]))
                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(q2_25[0] + q2_25[1])), percent_of_change((q2_24[0] + q2_24[1]), (q2_25[0] + q2_25[1])))
                col8.metric('**Q2 Fulcrum Sales**', '${:,}'.format(int(q2_25[1])), percent_of_change(q2_24[1], q2_25[1]))
                
                col6.metric('**Q3 Web Sales**', '${:,}'.format(int(q3_25[0])), percent_of_change(q3_24[0], q3_25[0]))
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(q3_25[0] + q3_25[1])), percent_of_change((q3_24[0] + q3_24[1]), (q3_25[0] + q3_25[1])))
                col8.metric('**Q3 Fulcrum Sales**', '${:,}'.format(int(q3_25[1])), percent_of_change(q3_24[1], q3_25[1]))
    
                col6.metric('**Q4 Web Sales**', '${:,}'.format(int(q4_25[0])), percent_of_change(q4_24[0], q4_25[0]))
                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(q4_25[0] + q4_25[1])), percent_of_change((q4_24[0] + q4_24[1]), (q4_25[0] + q4_25[1])))
                col8.metric('**Q4 Fulcrum Sales**', '${:,}'.format(int(q4_25[1])), percent_of_change(q4_24[1], q4_25[1]))
    
            with coly:
                months[0] = 'Overview'
                focus = st.selectbox('', options=months, key='Focus25')
        
                if focus == 'Overview':
                    display_month_data_x(sales_dict_25, sales_dict_24)
                elif focus == 'January':
                    display_metrics(sales_dict_25, sales_dict_24, 'January', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'February':
                    display_metrics(sales_dict_25, sales_dict_24, 'February', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'March':
                    display_metrics(sales_dict_25, sales_dict_24, 'March', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'April':
                    display_metrics(sales_dict_25, sales_dict_24, 'April', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'May':
                    display_metrics(sales_dict_25, sales_dict_24, 'May', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'June':
                    display_metrics(sales_dict_25, sales_dict_24, 'June', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'July':
                    display_metrics(sales_dict_25, sales_dict_24, 'July', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'August':
                    display_metrics(sales_dict_25, sales_dict_24, 'August', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'September':
                    display_metrics(sales_dict_25, sales_dict_24, 'September', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'October':
                    display_metrics(sales_dict_25, sales_dict_24, 'October', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'November':
                    display_metrics(sales_dict_25, sales_dict_24, 'November', wvr1=wvr_25_months, wvr2=wvr_24_months)
                else:
                    display_metrics(sales_dict_25, sales_dict_24, 'December', wvr1=wvr_25_months, wvr2=wvr_24_months)

        elif year_select == 2024:

            with col2:
                tot_vs_ytd = ui.tabs(options=['Totals', 'YTD'], default_value='Totals')
                
            if tot_vs_ytd == 'Totals':
                display_metrics(sales_dict_24, sales_dict_23, wvr1=wvr_24_months, wvr2=wvr_23_months)
            else:
                display_metrics(td_sales24, td_sales23, wvr1=wvr_24_ytd, wvr2=wvr_23_ytd)
        
            with col3:
                
                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales_dict_24))
                
            with colz:
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col6.metric('**Q1 Web Sales**', '${:,}'.format(int(q1_24[0])), percent_of_change(q1_23[0], q1_24[0]))
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(q1_24[0] + q1_24[1])), percent_of_change((q1_23[0] + q1_23[1]), (q1_24[0] + q1_24[1])))
                col8.metric('**Q1 Fulcrum Sales**', '${:,}'.format(int(q1_24[1])), percent_of_change(q1_23[1], q1_24[1]))
                
                col6.metric('**Q2 Web Sales**', '${:,}'.format(int(q2_24[0])), percent_of_change(q2_23[0], q2_24[0]))
                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(q2_24[0] + q2_24[1])), percent_of_change((q2_23[0] + q2_23[1]), (q2_24[0] + q2_24[1])))
                col8.metric('**Q2 Fulcrum Sales**', '${:,}'.format(int(q2_24[1])), percent_of_change(q2_23[1], q2_24[1]))
                
                col6.metric('**Q3 Web Sales**', '${:,}'.format(int(q3_24[0])), percent_of_change(q3_23[0], q3_24[0]))
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(q3_24[0] + q3_24[1])), percent_of_change((q3_23[0] + q3_23[1]), (q3_24[0] + q3_24[1])))
                col8.metric('**Q3 Fulcrum Sales**', '${:,}'.format(int(q3_24[1])), percent_of_change(q3_23[1], q3_24[1]))
    
                col6.metric('**Q4 Web Sales**', '${:,}'.format(int(q4_24[0])), percent_of_change(q4_23[0], q4_24[0]))
                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(q4_24[0] + q4_24[1])), percent_of_change((q4_23[0] + q4_23[1]), (q4_24[0] + q4_24[1])))
                col8.metric('**Q4 Fulcrum Sales**', '${:,}'.format(int(q4_24[1])), percent_of_change(q4_23[1], q4_24[1]))


            with coly:
                months[0] = 'Overview'
                focus = st.selectbox('', options=months, key='Focus24')
        
                if focus == 'Overview':
                    display_month_data_x(sales_dict_24, sales_dict_23)
                elif focus == 'January':
                    display_metrics(sales_dict_24, sales_dict_23, 'January', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'February':
                    display_metrics(sales_dict_24, sales_dict_23, 'February', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'March':
                    display_metrics(sales_dict_24, sales_dict_23, 'March', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'April':
                    display_metrics(sales_dict_24, sales_dict_23, 'April', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'May':
                    display_metrics(sales_dict_24, sales_dict_23, 'May', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'June':
                    display_metrics(sales_dict_24, sales_dict_23, 'June', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'July':
                    display_metrics(sales_dict_24, sales_dict_23, 'July', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'August':
                    display_metrics(sales_dict_24, sales_dict_23, 'August', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'September':
                    display_metrics(sales_dict_24, sales_dict_23, 'September', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'October':
                    display_metrics(sales_dict_24, sales_dict_23, 'October', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'November':
                    display_metrics(sales_dict_24, sales_dict_23, 'November', wvr1=wvr_24_months, wvr2=wvr_23_months)
                else:
                    display_metrics(sales_dict_24, sales_dict_23, 'December', wvr1=wvr_24_months, wvr2=wvr_23_months)


        elif year_select == 2023:

            with col2:
                tot_vs_ytd = ui.tabs(options=['Totals', 'YTD'], default_value='Totals')

            if tot_vs_ytd == 'Totals':
                display_metrics(sales_dict_23, sales_dict_22, wvr1=wvr_23_months)
            else:
                display_metrics(td_sales23, sales_dict_22, wvr1=wvr_23_ytd)
                
            with col3:
                
                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales_dict_23)) 
                
            with colz:

                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col6.metric('**Q1 Web Sales**', '${:,}'.format(int(q1_23[0])), percent_of_change(q1_22[0], q1_23[0]))
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(q1_23[0] + q1_23[1])), percent_of_change((q1_22[0] + q1_22[1]), (q1_23[0] + q1_23[1])))
                col8.metric('**Q1 Fulcrum Sales**', '${:,}'.format(int(q1_23[1])), percent_of_change(q1_22[1], q1_23[1]))
                
                col6.metric('**Q2 Web Sales**', '${:,}'.format(int(q2_23[0])), percent_of_change(q2_22[0], q2_23[0]))
                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(q2_23[0] + q2_23[1])), percent_of_change((q2_22[0] + q2_22[1]), (q2_23[0] + q2_23[1])))
                col8.metric('**Q2 Fulcrum Sales**', '${:,}'.format(int(q2_23[1])), percent_of_change(q2_22[1], q2_23[1]))
                
                col6.metric('**Q3 Web Sales**', '${:,}'.format(int(q3_23[0])), percent_of_change(q3_22[0], q3_23[0]))
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(q3_23[0] + q3_23[1])), percent_of_change((q3_22[0] + q3_22[1]), (q3_23[0] + q3_23[1])))
                col8.metric('**Q3 Fulcrum Sales**', '${:,}'.format(int(q3_23[1])), percent_of_change(q3_22[1], q3_23[1]))
    
                col6.metric('**Q4 Web Sales**', '${:,}'.format(int(q4_23[0])), percent_of_change(q4_22[0], q4_23[0]))
                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(q4_23[0] + q4_23[1])), percent_of_change((q4_22[0] + q4_22[1]), (q4_23[0] + q4_23[1])))
                col8.metric('**Q4 Fulcrum Sales**', '${:,}'.format(int(q4_23[1])), percent_of_change(q4_22[1], q4_23[1]))

            with coly:
                months[0] = 'Overview'
                focus = st.selectbox('', options=months, key='Focus23')
                
                if focus == 'Overview':
                    display_month_data_x(sales_dict_23, sales_dict_22)
                elif focus == 'January':
                    display_metrics(sales_dict_23, sales_dict_22, 'January', wvr1=wvr_23_months)
                elif focus == 'February':
                    display_metrics(sales_dict_23, sales_dict_22, 'February', wvr1=wvr_23_months)
                elif focus == 'March':
                    display_metrics(sales_dict_23, sales_dict_22, 'March', wvr1=wvr_23_months)
                elif focus == 'April':
                    display_metrics(sales_dict_23, sales_dict_22, 'April', wvr1=wvr_23_months)
                elif focus == 'May':
                    display_metrics(sales_dict_23, sales_dict_22, 'May', wvr1=wvr_23_months)
                elif focus == 'June':
                    display_metrics(sales_dict_23, sales_dict_22, 'June', wvr1=wvr_23_months)
                elif focus == 'July':
                    display_metrics(sales_dict_23, sales_dict_22, 'July', wvr1=wvr_23_months)
                elif focus == 'August':
                    display_metrics(sales_dict_23, sales_dict_22, 'August', wvr1=wvr_23_months)
                elif focus == 'September':
                    display_metrics(sales_dict_23, sales_dict_22, 'September', wvr1=wvr_23_months)
                elif focus == 'October':
                    display_metrics(sales_dict_23, sales_dict_22, 'October', wvr1=wvr_23_months)
                elif focus == 'November':
                    display_metrics(sales_dict_23, sales_dict_22, 'November', wvr1=wvr_23_months)
                else:
                    display_metrics(sales_dict_23, sales_dict_22, 'December', wvr1=wvr_23_months)
                

        if year_select == 2022:
    
            display_metrics(sales22, sales21, note='22')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales22))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs22[0])), percent_of_change(qs21[0], qs22[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs22[1])), percent_of_change(qs21[1], qs22[1]))
        
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs22[2])), percent_of_change(qs21[2], qs22[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs22[3])), percent_of_change(qs21[3], qs22[3]))  
                
            #st.divider()
            with coly:
                display_month_data_x(sales22, sales21)

        if year_select == 2021:
    
            display_metrics(sales21, sales20, note='21')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales21))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs21[0])), percent_of_change(qs20[0], qs21[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs21[1])), percent_of_change(qs20[1], qs21[1]))
        
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs21[2])), percent_of_change(qs20[2], qs21[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs21[3])), percent_of_change(qs20[3], qs21[3]))                

            #st.divider()
            with coly:
                display_month_data_x(sales21, sales20)

        if year_select == 2020:
    
            display_metrics(sales20, sales19, note='20')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales20))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs20[0])), percent_of_change(qs19[0], qs20[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs20[1])), percent_of_change(qs19[1], qs20[1]))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs20[2])), percent_of_change(qs19[2], qs20[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs20[3])), percent_of_change(qs19[3], qs20[3]))
                
            #st.divider()
            with coly:
                display_month_data_x(sales20, sales19)

        if year_select == 2019:
    
            display_metrics(sales19, sales18, note='19')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales19))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs19[0])), percent_of_change(qs18[0], qs19[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs19[1])), percent_of_change(qs18[1], qs19[1]))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs19[2])), percent_of_change(qs18[2], qs19[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs19[3])), percent_of_change(qs18[3], qs19[3]))
                
            #st.divider()
            with coly:
                display_month_data_x(sales19, sales18)

        if year_select == 2018:
    
            display_metrics(sales18, sales17, note='18')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales18))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs18[0])), percent_of_change(qs17[0], qs18[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs18[1])), percent_of_change(qs17[1], qs18[1]))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs18[2])), percent_of_change(qs17[2], qs18[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs18[3])), percent_of_change(qs17[3], qs18[3]))
                
            #st.divider()
            with coly:
                display_month_data_x(sales18, sales17)

        if year_select == 2017:
    
            display_metrics(sales17, sales16, note='17')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales17))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs17[0])), percent_of_change(qs16[0], qs17[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs17[1])), percent_of_change(qs16[1], qs17[1]))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs17[2])), percent_of_change(qs16[2], qs17[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs17[3])), percent_of_change(qs16[3], qs17[3]))
                
            #st.divider()
            with coly:
                display_month_data_x(sales17, sales16)

        if year_select == 2016:
    
            display_metrics(sales16, sales15, note='16')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales16))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs16[0])), percent_of_change(qs15[0], qs16[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs16[1])), percent_of_change(qs15[1], qs16[1]))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs16[2])), percent_of_change(qs15[2], qs16[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs16[3])), percent_of_change(qs15[3], qs16[3]))
                
            #st.divider()
            with coly:
                display_month_data_x(sales16, sales15)

        if year_select == 2015:
    
            display_metrics(sales15, sales14, note='15')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales15))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs15[0])), percent_of_change(qs14[0], qs15[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs15[1])), percent_of_change(qs14[1], qs15[1]))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs15[2])), percent_of_change(qs14[2], qs15[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs15[3])), percent_of_change(qs14[3], qs15[3]))
                
            #st.divider()
            with coly:
                display_month_data_x(sales15, sales14)

        if year_select == 2014:
    
            display_metrics(sales14, sales13, note='14')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales14))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs14[0])), percent_of_change(qs13[0], qs14[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs14[1])), percent_of_change(qs13[1], qs14[1]))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs14[2])), percent_of_change(qs13[2], qs14[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs14[3])), percent_of_change(qs13[3], qs14[3]))
                    
            #st.divider()
            with coly:
                display_month_data_x(sales14, sales13)

        if year_select == 2013:
    
            display_metrics(sales13, note='13')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales13))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs13[0])))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs13[1])))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs13[2])))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs13[3])))
    
            #st.divider()
            with coly:
                display_month_data_x(sales13)





### USE METRIC CARDS TO DISPLAY MONTHLY SALES METRICS ###

def display_month_data_prod(product, sales_dict1, sales_dict2=None, type='Unit'):

    dBoard1 = st.columns(3)
    dBoard2 = st.columns(3)
    dBoard3 = st.columns(3)
    dBoard4 = st.columns(3)
    idx = 0
    idx1 = 0
    idx2 = 0
    idx3 = 0

    for x in months_x:

        if type == 'Currency':

            var = ''
            if sales_dict2 == None:
                description = ''
                diff = 0
            else:
                diff = (sales_dict1[x][product][0]) - (sales_dict2[x][product][0])
            if diff > 0:
                var = '+'
            elif diff < 0:
                var = '-'
                
            if idx < 3:
                with dBoard1[idx]:
                    ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][product][0])), description='{} ${:,} vs. prior year]'.format(var, abs(int(diff))))
            elif idx >=3 and idx < 6:
                with dBoard2[idx1]:
                    ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][product][0])), description='{} ${:,} vs. prior year'.format(var, abs(int(diff))))
                    idx1 += 1
            elif idx >= 6 and idx < 9:
                with dBoard3[idx2]:
                    ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][product][0])), description='{} ${:,} vs. prior year'.format(var, abs(int(diff))))
                    idx2 += 1
            else:
                with dBoard4[idx3]:
                    ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][product][0])), description='{} ${:,} vs. prior year'.format(var, abs(int(diff))))
                    idx3 += 1

        elif type == 'Unit':

            var = ''
            if sales_dict2 == None:
                description = ''
                diff = 0
            else:   
                diff = (sales_dict1[x][product][0]) - (sales_dict2[x][product][0])
            if diff > 0:
                var = '+'
            elif diff < 0:
                var = '-'
                
            if idx < 3:
                with dBoard1[idx]:
                    ui.metric_card(title=x, content='{:,}'.format(sales_dict1[x][product][0]), description='{} {} vs. prior year'.format(var, abs(diff)))
            elif idx >=3 and idx < 6:
                with dBoard2[idx1]:
                    ui.metric_card(title=x, content='{:,}'.format(sales_dict1[x][product][0]), description='{} {} vs. prior year'.format(var, abs(diff)))
                    idx1 += 1
            elif idx >= 6 and idx < 9:
                with dBoard3[idx2]:
                    ui.metric_card(title=x, content='{:,}'.format(sales_dict1[x][product][0]), description='{} {} vs. prior year'.format(var, abs(diff)))
                    idx2 += 1
            else:
                with dBoard4[idx3]:
                    ui.metric_card(title=x, content='{:,}'.format(sales_dict1[x][product][0]), description='{} {} vs. prior year'.format(var, abs(diff)))
                    idx3 += 1

        idx += 1
            

    return None
    



def format_for_pie_chart(dict, key=0):
    
    prods = []
    vals = []
    columns = ['Product', 'Totals']

    for prod, val in dict.items():
        prods.append(prod)
        vals.append(int(val[key]))
        
    df = pd.DataFrame(np.column_stack([prods, vals]), index=[prods], columns=columns)

    return df

def format_for_line_graph(dict1, product, dict2=None, key=0):

    months = []
    units_sold = []
    columns = ['Months', 'Units Sold']

    for month, prod in dict1.items():
        months.append(month)
        units_sold.append(dict1[month][product][key])

    df = pd.DataFrame(np.column_stack([months, units_sold]), columns=columns)

    return df
        
def display_pie_chart_comp(df):
    col1, col2 = st.columns(2)
    colors = ["rgb(115, 255, 165)", "rgb(88, 92, 89)", "rgb(7, 105, 7)", "rgb(0, 255, 0"]
    with col1:
        saleFig = px.pie(format_for_pie_chart(df), values='Totals', names='Product', title='Units', height=400, width=400)
        saleFig.update_layout(margin=dict(l=10, r=10, t=20, b=0))
        saleFig.update_traces(textfont_size=18, marker=dict(colors=colors))
        st.plotly_chart(saleFig, use_container_width=False)
    with col2:
        revFig = px.pie(format_for_pie_chart(df, 1), values='Totals', names='Product', title='Revenue', height=400, width=400)
        revFig.update_layout(margin=dict(l=10, r=10, t=20, b=0))
        revFig.update_traces(textfont_size=18, marker=dict(colors=colors))
        st.plotly_chart(revFig, use_container_width=False)        

    return None

def avg_month_prod(dict):
    
    zero_count = 0
    total_unit = 0
    total_rev = 0

    unit_avg = 0
    rev_avg = 0
    
    for key, value in dict.items():
        
        if value[0] == 0:
            zero_count += 1
        else:
            total += value

    unit_avg = int(total_unit / (len(dict) - zero_count))
    rev_avg = int(total_rev / (len(dict) - zero_count))
    
    return unit_avg, rev_avg




def display_hose_data(hose_details1, hose_details2, hose_details3):

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader('2025')
        idx = 0
        for group in hose_details1[:7]:
            group_units = 0
            group_rev = 0
            with st.container(border=True):
                for hose, vals in group.items():
                    group_units += vals[0]
                    group_rev += vals[1]
                    ui.metric_card(title=hose, content='{} units'.format(int(vals[0])), description='${:,.2f} in rev'.format(vals[1]))
                if idx == 0:
                    st.markdown('**Totals: {} - (${:,})**'.format(int(group_units), int(group_rev)))
                else:
                    st.markdown('**Totals: {} - (${:,})**'.format(int(group_units), int(group_rev)))
                            
            idx += 1
        ui.metric_card(title='100FT STD', content='{} units'.format(int(hose_details1[7][0])), description='${:,.2f} in rev'.format(hose_details1[7][1]), key='2025')
        
    with col2:
        st.subheader('2024')
        idx2 = 0
        for group2 in hose_details2[:7]:
            group2_units = 0
            group2_rev = 0
            with st.container(border=True):
                for hose2, vals2 in group2.items():
                    group2_units += vals2[0]
                    group2_rev += vals2[1]
                    ui.metric_card(title=hose2, content='{} units'.format(int(vals2[0])), description='${:,.2f} in rev'.format(vals2[1]))
                if idx2 == 0:
                    st.markdown('**Totals: {} - (${:,})**'.format(int(group2_units), int(group2_rev)))
                else:
                    st.markdown('**Totals: {} - (${:,})**'.format(int(group2_units), int(group2_rev)))
            idx2 += 1
        ui.metric_card(title='100FT STD', content='{} units'.format(int(hose_details2[7][0])), description='${:,.2f} in rev'.format(hose_details2[7][1]), key='2024')

        with col3:
            st.subheader('2023')
            idx3 = 0
            for group3 in hose_details3[:7]:
                group3_units = 0
                group3_rev = 0
                with st.container(border=True):
                    for hose3, vals3 in group3.items():
                        group3_units += vals3[0]
                        group3_rev += vals3[1]
                        ui.metric_card(title=hose3, content='{} units'.format(int(vals3[0])), description='${:,.2f} in rev'.format(vals3[1]))
                    if idx3 == 0:
                        st.markdown('**Totals: {} - (${:,})**'.format(int(group3_units), int(group3_rev)))
                    else:
                        st.markdown('**Totals: {} - (${:,})**'.format(int(group3_units), int(group3_rev)))
                idx3 += 1
            ui.metric_card(title='100FT STD', content='{} units'.format(int(hose_details3[7][0])), description='${:,.2f} in rev'.format(hose_details3[7][1]), key='2023')
        
    return None

def display_hose_data_profit(hose_details1, hose_details2, hose_details3):

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader('2025')
        idx = 0
        for group in hose_details1[:7]:
            group_profit = 0

            with st.container(border=True):
                for hose, vals in group.items():
                    prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calculate_product_metrics(annual_product_totals, hose, 11, bom_cost_hose)
                    group_profit += prod_profit

                    ui.metric_card(title=hose, content='Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit))
                if idx == 0:
                    st.markdown('**Group Total: ${:,.2f}**'.format(group_profit))
                else:
                    st.markdown('**Group Total: ${:,.2f}**'.format(group_profit))
                            
            idx += 1
        prod_profit100, profit_per_unit100, prod_profit_last100, avg_price100, avg_price_last100 = calculate_product_metrics(annual_product_totals, '100FT STD', 11, bom_cost_hose)
        ui.metric_card(title='100FT STD', content='Profit: ${:,.2f}'.format(prod_profit100), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit100), key='2025')
        
    with col2:
        st.subheader('2024')
        idx2 = 0
        for group2 in hose_details2[:7]:
            group2_profit = 0

            with st.container(border=True):
                for hose2, vals2 in group2.items():
                    prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calculate_product_metrics(annual_product_totals, hose2, 10, bom_cost_hose)
                    group2_profit += prod_profit

                    ui.metric_card(title=hose2, content='Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit))
                if idx2 == 0:
                    st.markdown('**Group Total: ${:,.2f}**'.format(group2_profit))
                else:
                    st.markdown('**Group Total: ${:,.2f}**'.format(group2_profit))
            idx2 += 1
        prod_profit100, profit_per_unit100, prod_profit_last100, avg_price100, avg_price_last100 = calculate_product_metrics(annual_product_totals, '100FT STD', 10, bom_cost_hose)    
        ui.metric_card(title='100FT STD', content='Profit: ${:,.2f}'.format(prod_profit100), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit100), key='2024')

        with col3:
            st.subheader('2023')
            idx3 = 0
            for group3 in hose_details3[:7]:
                group3_profit = 0

                with st.container(border=True):
                    for hose3, vals3 in group3.items():
                        prod_profit, profit_per_unit, avg_price = calculate_product_metrics(annual_product_totals, hose3, 9, bom_cost_hose)
                        group3_profit += prod_profit

                        ui.metric_card(title=hose3, content='Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit))
                    if idx3 == 0:
                        st.markdown('**Group Total: ${:,.2f}**'.format(group3_profit))
                    else:
                        st.markdown('**Group Total: ${:,.2f}**'.format(group3_profit))
                idx3 += 1
            prod_profit100, profit_per_unit100, avg_price100  = calculate_product_metrics(annual_product_totals, '100FT STD', 9, bom_cost_hose)
            ui.metric_card(title='100FT STD', content='Profit: ${:,.2f}'.format(prod_profit100), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit100), key='2023')
        
    return None

def display_acc_data():
    
    with colc:
        for item, value in annual_product_totals[-1].items():
            if item == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item), content='{} (PJ: {}, LA: {}, QJ: {})'.format(int(value[0]), int(value[2]), int(value[3]), int(value[4])), description='${:,.2f} in Revenue'.format(value[1]))
            else:
                value[0] = int(value[0])
                ui.metric_card(title='{}'.format(item), content='{}'.format(value[0]), description='${:,.2f} in Revenue'.format(value[1])) 
    with cold:
        key = 'anvienial23'
        for item_last, value_last in annual_product_totals[-2].items():
            if item_last == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item_last), content='{} (PJ: {}, LA: {}, QJ: {})'.format(int(value_last[0]), int(value_last[2]), int(value_last[3]), int(value_last[4])), description='${:,.2f} in Revenue'.format(value_last[1]), key=key)
            else:
                value_last[0] = int(value_last[0])
                ui.metric_card(title='{}'.format(item_last), content='{}'.format(value_last[0]), description='${:,.2f} in Revenue'.format(value_last[1]), key=key)
            key += '64sdg5as'
    with cole:
        key2 = 'a'
        for item_last2, value_last2 in annual_product_totals[-3].items():
            if item_last2 == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item_last2), content='{} (PJ: {}, LA: {})'.format(int(value_last2[0]), int(value_last2[2]), int(value_last2[3])), description='${:,.2f} in Revenue'.format(value_last2[1]), key=key2)
            else:
                value_last2[0] = int(value_last2[0])
                ui.metric_card(title='{}'.format(item_last2), content='{}'.format(value_last2[0]), description='${:,.2f} in Revenue'.format(value_last2[1]), key=key2)
            key2 += 'niane7'

            
    return None



def calculate_product_metrics(annual_product_totals, prod_select, key, bom_dict):

    jet_list = ['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp']
    control_list = ['The Button', 'Shostarter', 'Shomaster']
    no_prior_list = [0,3,6,9,12]

    prod_profit = (annual_product_totals[key][prod_select][1]) - (annual_product_totals[key][prod_select][0] * bom_dict[prod_select])
    if annual_product_totals[key][prod_select][0] == 0:
        profit_per_unit = 0
        avg_price = 0
    else:
        profit_per_unit = prod_profit / annual_product_totals[key][prod_select][0]
        avg_price = annual_product_totals[key][prod_select][1] / annual_product_totals[key][prod_select][0]
    
    if key not in no_prior_list:
        if annual_product_totals[key-1][prod_select][0] == 0:
            avg_price_last = 0
            prod_profit_last = 0
        else:
            avg_price_last = annual_product_totals[key-1][prod_select][1] / annual_product_totals[key-1][prod_select][0]
            prod_profit_last = (annual_product_totals[key-1][prod_select][1]) - (annual_product_totals[key-1][prod_select][0] * bom_dict[prod_select])

    if (prod_select in jet_list or prod_select in control_list) and (key in [0, 1, 2, 3, 4, 5]):
        wholesale_sales = annual_product_totals[key][prod_select][2]
        if annual_product_totals[key][prod_select][0] == 0:
            wholesale_percentage = 0
        else:
            wholesale_percentage = (annual_product_totals[key][prod_select][2] / annual_product_totals[key][prod_select][0]) * 100
        
        if key not in no_prior_list:
            wholesale_delta = wholesale_percentage - ((annual_product_totals[key-1][prod_select][2] / annual_product_totals[key-1][prod_select][0]) * 100)
            return prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta
        else:
            return prod_profit, profit_per_unit, avg_price, wholesale_sales, wholesale_percentage

    elif key in no_prior_list:
        return prod_profit, profit_per_unit, avg_price
    
    else:
        return prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last

def to_date_product(sku_string):
    
    # 15FT & 8FT HOSES DO NOT INCLUDE HANDHELDS

    prod_cnt_25 = 0
    prod_cnt_24 = 0
    prod_cnt_23 = 0
    prod_cnt_22 = 0

    idx = 0

    for order in df.line_item:
        order_date = df.iloc[idx].order_date
        if order[:len(sku_string)] == sku_string:
            if two_years_ago.date() >= order_date >= beginning_of_year(two_years_ago).date():
                prod_cnt_22 += df.iloc[idx].quantity
            elif one_year_ago.date() >= order_date >= beginning_of_year(one_year_ago).date():
                prod_cnt_23 += df.iloc[idx].quantity
            elif today.date() >= order_date >= beginning_of_year(today).date():
                prod_cnt_24 += df.iloc[idx].quantity
            elif order_date.year == 2025:
                prod_cnt_25 += df.iloc[idx].quantity
                
        idx += 1
            
    return prod_cnt_23, prod_cnt_24


@st.cache_data
def hist_product_data(product_tag):

    cust_dict = {}
    for cust in master_customer_list:
        cust_dict[cust] = 0
        
    annual_dict = {'2022': 0, '2021': 0, '2020': 0, '2019': 0, '2018': 0, '2017': 0, '2016': 0, '2015': 0, '2014': 0, '2013': 0}

    idx = 0
    for line in product_tag:

        if df_hist.iloc[idx].order_date.year in [2023, 2024, 2025, 1970]:
            pass
        else:
            year = str(df_hist.iloc[idx].order_date.year)
            if year == '2104':
                year = '2014'
            else:
                try:
                    annual_dict[year] += int(line)
                    if line > 0:
                        cust_dict[df_hist.iloc[idx].customer] += int(line)
                except:
                    pass
                    
        if idx <= len(df_hist): 
            idx += 1

    return cust_dict, annual_dict



# HISTORICAL HANDHELDS
hhmk1_cust, hhmk1_annual = hist_product_data(df_hist.hh_mk1)
hhmk2_cust, hhmk2_annual = hist_product_data(df_hist.hh_mk2)

# HISTORICAL ACCESSORIES
tc_cust, tc_annual = hist_product_data(df_hist.travel_case)
tcog_cust, tcog_annual = hist_product_data(df_hist.travel_case_og)
bp_cust, bp_annual = hist_product_data(df_hist.backpack)
mfd_cust, mfd_annual = hist_product_data(df_hist.manifold)
ctc_20_cust, ctc_20_annual = hist_product_data(df_hist.ctc_20)
ctc_50_cust, ctc_50_annual = hist_product_data(df_hist.ctc_50)
ledmk1_cust, ledmk1_annual = hist_product_data(df_hist.led_attachment_mk1)
ledmk2_cust, ledmk2_annual = hist_product_data(df_hist.led_attachment_mk2)
pwrpack_cust, pwrpack_annual = hist_product_data(df_hist.power_pack)

# HISTORICAL JETS
jet_og_cust, jet_og_annual = hist_product_data(df_hist.jets_og)
pj_cust, pj_annual = hist_product_data(df_hist.pro_jet)
pwj_cust, pwj_annual = hist_product_data(df_hist.power_jet)
mjmk1_cust, mjmk1_annual = hist_product_data(df_hist.micro_jet_mk1)
mjmk2_cust, mjmk2_annual = hist_product_data(df_hist.micro_jet_mk2)
ccmk1_cust, ccmk1_annual = hist_product_data(df_hist.cryo_clamp_mk1)
ccmk2_cust, ccmk2_annual = hist_product_data(df_hist.cryo_clamp_mk2)
qj_cust, qj_annual = hist_product_data(df_hist.quad_jet)

# HISTORICAL CONTROLLERS
dmx_cntl_cust, dmx_cntl_annual = hist_product_data(df_hist.dmx_controller)
lcd_cntl_cust, lcd_cntl_annual = hist_product_data(df_hist.lcd_controller)
tbmk1_cust, tbmk1_annual = hist_product_data(df_hist.the_button_mk1)
tbmk2_cust, tbmk2_annual = hist_product_data(df_hist.the_button_mk2)
sm_cust, sm_annual = hist_product_data(df_hist.shomaster)
ss_cust, ss_annual = hist_product_data(df_hist.shostarter)
pwr_cntl_cust, pwr_cntl_annual = hist_product_data(df_hist.power_controller)

# HISTORICAL CONFETTI
blwr_cust, blwr_annual = hist_product_data(df_hist.confetti_blower)



if task_choice == 'Product Reports':

    #st.header('Product Reports')
    #st.subheader('')

    # PULL ALL PRODUCT SALES BY MONTH (DICTIONARIES)
    jet23, jet24, jet25, control23, control24, control25, handheld23, handheld24, handheld25, hose23, hose24, hose25, acc23, acc24, acc25 = collect_product_data(df)
    hose_detail25 = organize_hose_data(hose25)
    hose_detail24 = organize_hose_data(hose24)
    hose_detail23 = organize_hose_data(hose23)

    
    # CALCULATE ANNUAL PRODUCT TOTALS
    annual_product_totals = product_annual_totals([jet23, jet24, jet25, control23, control24, control25, handheld23, handheld24, handheld25, hose23, hose24, hose25, acc23, acc24, acc25])

    col1, col2, col3 = st.columns([.25, .5, .25], gap='medium')

    with col2:
        # NAVIGATION TABS
        prod_cat = ui.tabs(options=['Jets', 'Controllers', 'Handhelds', 'Hoses', 'Accessories', 'MagicFX'], default_value='Jets', key='Product Categories')
        #year = ui.tabs(options=[2025, 2024, 2023], default_value=2024, key='Products Year Select')


    
    if prod_cat == 'Jets':

        pj_td23, pj_td24 = to_date_product('CC-PROJ')
        mj_td23, mj_td24 = to_date_product('CC-MJMK')
        qj_td23, qj_td24 = to_date_product('CC-QJ')
        cc_td23, cc_td24 = to_date_product('CC-CC2')

        with col2:
            year = ui.tabs(options=[2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014], default_value=2024, key='Jet Year Select')

        if year == 2025:
            
            total_jet_rev = annual_product_totals[2]['Pro Jet'][1] + annual_product_totals[2]['Quad Jet'][1] + annual_product_totals[2]['Micro Jet'][1] + annual_product_totals[2]['Cryo Clamp'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4, gap='medium')
    
                cola.subheader('Pro Jet')
                cola.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[2]['Pro Jet'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[2]['Pro Jet'][0]), annual_product_totals[2]['Pro Jet'][0] - pj_td24)
    
                colb.subheader('Quad Jet')
                colb.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[2]['Quad Jet'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[2]['Quad Jet'][0]), annual_product_totals[2]['Quad Jet'][0] - qj_td24)
    
                colc.subheader('Micro Jet')
                colc.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[2]['Micro Jet'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[2]['Micro Jet'][0]), annual_product_totals[2]['Micro Jet'][0] - mj_td24)
    
                cold.subheader('Cryo Clamp')
                cold.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[2]['Cryo Clamp'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[2]['Cryo Clamp'][0]), annual_product_totals[2]['Cryo Clamp'][0] - cc_td24)

                prod_profit_PJ, profit_per_unit_PJ, prod_profit_last_PJ, avg_price_PJ, avg_price_last_PJ, wholesale_sales_PJ, wholesale_percentage_PJ, wholesale_delta_PJ = calculate_product_metrics(annual_product_totals, 'Pro Jet', 2, bom_cost_jet)
                prod_profit_QJ, profit_per_unit_QJ, prod_profit_last_QJ, avg_price_QJ, avg_price_last_QJ, wholesale_sales_QJ, wholesale_percentage_QJ, wholesale_delta_QJ = calculate_product_metrics(annual_product_totals, 'Quad Jet', 2, bom_cost_jet)
                prod_profit_MJ, profit_per_unit_MJ, prod_profit_last_MJ, avg_price_MJ, avg_price_last_MJ, wholesale_sales_MJ, wholesale_percentage_MJ, wholesale_delta_MJ = calculate_product_metrics(annual_product_totals, 'Micro Jet', 2, bom_cost_jet)
                prod_profit_CC, profit_per_unit_CC, prod_profit_last_CC, avg_price_CC, avg_price_last_CC, wholesale_sales_CC, wholesale_percentage_CC, wholesale_delta_CC = calculate_product_metrics(annual_product_totals, 'Cryo Clamp', 2, bom_cost_jet)
                
                tot_jet_rev25 = annual_product_totals[2]['Pro Jet'][1] + annual_product_totals[2]['Quad Jet'][1] + annual_product_totals[2]['Micro Jet'][1] + annual_product_totals[2]['Cryo Clamp'][1]
                tot_jet_prof25 = prod_profit_PJ + prod_profit_QJ + prod_profit_MJ + prod_profit_CC
                if tot_jet_rev25 == 0:
                    jet_prof_margin25 = 0
                else:
                    jet_prof_margin25 = (tot_jet_prof25 / tot_jet_rev25) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_jet_rev25)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(jet_prof_margin25))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_jet_prof25)))
    
                style_metric_cards()

                st.divider()
                display_pie_chart_comp(annual_product_totals[2])
                st.divider()

                prod_select = ui.tabs(options=['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp'], default_value='Pro Jet', key='Jets')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calculate_product_metrics(annual_product_totals, prod_select, 2, bom_cost_jet)
    
                col5.metric('**Revenue**', '${:,.2f}'.format(annual_product_totals[2][prod_select][1]), percent_of_change(annual_product_totals[1][prod_select][0], annual_product_totals[2][prod_select][0]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))        
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_jet[prod_select]), '')
                
                display_month_data_prod(prod_select, jet25, jet24)
        
        elif year == 2024:
            
            total_jet_rev = annual_product_totals[1]['Pro Jet'][1] + annual_product_totals[1]['Quad Jet'][1] + annual_product_totals[1]['Micro Jet'][1] + annual_product_totals[1]['Cryo Clamp'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4)
    
                cola.subheader('Pro Jet')
                cola.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[1]['Pro Jet'][1] / total_24) * 100), '{}'.format(annual_product_totals[1]['Pro Jet'][0]), annual_product_totals[1]['Pro Jet'][0] - annual_product_totals[0]['Pro Jet'][0])
    
                colb.subheader('Quad Jet')
                colb.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[1]['Quad Jet'][1] / total_24) * 100), '{}'.format(annual_product_totals[1]['Quad Jet'][0]), annual_product_totals[1]['Quad Jet'][0] - annual_product_totals[0]['Quad Jet'][0])
    
                colc.subheader('Micro Jet')
                colc.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[1]['Micro Jet'][1] / total_24) * 100), '{}'.format(annual_product_totals[1]['Micro Jet'][0]), annual_product_totals[1]['Micro Jet'][0] - annual_product_totals[0]['Micro Jet'][0])
    
                cold.subheader('Cryo Clamp')
                cold.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[1]['Cryo Clamp'][1] / total_24) * 100), '{}'.format(annual_product_totals[1]['Cryo Clamp'][0]), annual_product_totals[1]['Cryo Clamp'][0] - annual_product_totals[0]['Cryo Clamp'][0])

                prod_profit_PJ, profit_per_unit_PJ, prod_profit_last_PJ, avg_price_PJ, avg_price_last_PJ, wholesale_sales_PJ, wholesale_percentage_PJ, wholesale_delta_PJ = calculate_product_metrics(annual_product_totals, 'Pro Jet', 1, bom_cost_jet)
                prod_profit_QJ, profit_per_unit_QJ, prod_profit_last_QJ, avg_price_QJ, avg_price_last_QJ, wholesale_sales_QJ, wholesale_percentage_QJ, wholesale_delta_QJ = calculate_product_metrics(annual_product_totals, 'Quad Jet', 1, bom_cost_jet)
                prod_profit_MJ, profit_per_unit_MJ, prod_profit_last_MJ, avg_price_MJ, avg_price_last_MJ, wholesale_sales_MJ, wholesale_percentage_MJ, wholesale_delta_MJ = calculate_product_metrics(annual_product_totals, 'Micro Jet', 1, bom_cost_jet)
                prod_profit_CC, profit_per_unit_CC, prod_profit_last_CC, avg_price_CC, avg_price_last_CC, wholesale_sales_CC, wholesale_percentage_CC, wholesale_delta_CC = calculate_product_metrics(annual_product_totals, 'Cryo Clamp', 1, bom_cost_jet)
                
                tot_jet_rev24 = annual_product_totals[1]['Pro Jet'][1] + annual_product_totals[1]['Quad Jet'][1] + annual_product_totals[1]['Micro Jet'][1] + annual_product_totals[1]['Cryo Clamp'][1]
                tot_jet_prof24 = prod_profit_PJ + prod_profit_QJ + prod_profit_MJ + prod_profit_CC
                jet_prof_margin24 = (tot_jet_prof24 / tot_jet_rev24) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_jet_rev24)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(jet_prof_margin24))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_jet_prof24)))
                
                style_metric_cards()

                st.divider()
                display_pie_chart_comp(annual_product_totals[1])
                st.divider()
                
                prod_select = ui.tabs(options=['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp'], default_value='Pro Jet', key='Jets')
        
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calculate_product_metrics(annual_product_totals, prod_select, 1, bom_cost_jet)
                
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
        
                col5.metric('**Revenue**', '${:,.2f}'.format(annual_product_totals[1][prod_select][1]), percent_of_change(annual_product_totals[0][prod_select][0], annual_product_totals[1][prod_select][0]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))        
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_jet[prod_select]), '')
            
                    
                display_month_data_prod(prod_select, jet24, jet23)
            
            
        elif year == 2023:
            
            total_jet_rev = annual_product_totals[0]['Pro Jet'][1] + annual_product_totals[0]['Quad Jet'][1] + annual_product_totals[0]['Micro Jet'][1] + annual_product_totals[0]['Cryo Clamp'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4)
        
                cola.subheader('Pro Jet')
                cola.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[0]['Pro Jet'][1] / total_23) * 100), '{}'.format(annual_product_totals[0]['Pro Jet'][0]), '')
    
                colb.subheader('Quad Jet')
                colb.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[0]['Quad Jet'][1] / total_23) * 100), '{}'.format(annual_product_totals[0]['Quad Jet'][0]), '')
    
                colc.subheader('Micro Jet')
                colc.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[0]['Micro Jet'][1] / total_23) * 100), '{}'.format(annual_product_totals[0]['Micro Jet'][0]), '')
    
                cold.subheader('Cryo Clamp')
                cold.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[0]['Cryo Clamp'][1] / total_23) * 100), '{}'.format(annual_product_totals[0]['Cryo Clamp'][0]), '')
    
                prod_profit_PJ, profit_per_unit_PJ, prod_profit_last_PJ, avg_price_PJ, avg_price_last_PJ = calculate_product_metrics(annual_product_totals, 'Pro Jet', 0, bom_cost_jet)
                prod_profit_QJ, profit_per_unit_QJ, prod_profit_last_QJ, avg_price_QJ, avg_price_last_QJ = calculate_product_metrics(annual_product_totals, 'Quad Jet', 0, bom_cost_jet)
                prod_profit_MJ, profit_per_unit_MJ, prod_profit_last_MJ, avg_price_MJ, avg_price_last_MJ = calculate_product_metrics(annual_product_totals, 'Micro Jet', 0, bom_cost_jet)
                prod_profit_CC, profit_per_unit_CC, prod_profit_last_CC, avg_price_CC, avg_price_last_CC = calculate_product_metrics(annual_product_totals, 'Cryo Clamp', 0, bom_cost_jet)
                
                tot_jet_rev23 = annual_product_totals[0]['Pro Jet'][1] + annual_product_totals[0]['Quad Jet'][1] + annual_product_totals[0]['Micro Jet'][1] + annual_product_totals[0]['Cryo Clamp'][1]
                tot_jet_prof23 = prod_profit_PJ + prod_profit_QJ + prod_profit_MJ + prod_profit_CC
                jet_prof_margin23 = (tot_jet_prof23 / tot_jet_rev23) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_jet_rev23)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(jet_prof_margin23))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_jet_prof23)))
         
                style_metric_cards()
                
                st.divider()
                display_pie_chart_comp(annual_product_totals[0])
                st.divider()
                
                prod_select = ui.tabs(options=['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp'], default_value='Pro Jet', key='Jets')
        
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
                
                prod_profit, profit_per_unit, avg_price, wholesale_sales, wholesale_percentage = calculate_product_metrics(annual_product_totals, prod_select, 0, bom_cost_jet)
    
    
                col5.metric('**Revenue**', '${:,.2f}'.format(annual_product_totals[0][prod_select][1]), '')
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), '')
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), '')        
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_jet[prod_select]), '')
                
                display_month_data_prod(prod_select, jet23)  

        elif year == 2022:
            
            with col2:
                cola, colb, colc= st.columns(3)
        
                cola.subheader('Pro Jet')
                cola.metric('', '{}'.format(pj_annual['2022']), 'N/A')
    
                colb.subheader('Quad Jet')
                colb.metric('', '{}'.format(qj_annual['2022']), (qj_annual['2022'] - qj_annual['2021']))

                colc.subheader('Cryo Clamp MK1')
                colc.metric('', '{}'.format(ccmk1_annual['2022']), (ccmk1_annual['2022'] - ccmk1_annual['2021']))
    
                cola.subheader('Micro Jet MK1')
                cola.metric('', '{}'.format(mjmk1_annual['2022']), (mjmk1_annual['2022'] - mjmk1_annual['2021']))
                                        
                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(mjmk1_annual['2022'] + mjmk2_annual['2022'] + ccmk1_annual['2022'] + pj_annual['2022'] + qj_annual['2022']), ((mjmk1_annual['2022'] + mjmk2_annual['2022'] + ccmk1_annual['2022'] + pj_annual['2022'] + qj_annual['2022']) - (mjmk1_annual['2021'] + mjmk2_annual['2021'] + ccmk1_annual['2021'] + jet_og_annual['2021'] + qj_annual['2021'] + pwj_annual['2021'])))
                
                colc.subheader('Micro Jet MK2')
                colc.metric('', '{}'.format(mjmk2_annual['2022']), (mjmk2_annual['2022'] - mjmk2_annual['2021']))

                style_metric_cards()

        elif year == 2021:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2021']), (jet_og_annual['2021'] - jet_og_annual['2020']))
    
                colb.subheader('Quad Jet')
                colb.metric('', '{}'.format(qj_annual['2021']), (qj_annual['2021'] - qj_annual['2020']))

                colc.subheader('Cryo Clamp MK1')
                colc.metric('', '{}'.format(ccmk1_annual['2021']), (ccmk1_annual['2021'] - ccmk1_annual['2020']))
    
                cola.subheader('Micro Jet MK1')
                cola.metric('', '{}'.format(mjmk1_annual['2021']), (mjmk1_annual['2021'] - mjmk1_annual['2020']))

                colb.subheader('Power Jet')
                colb.metric('', '{}'.format(pwj_annual['2021']), (pwj_annual['2021'] - pwj_annual['2020']))
                                        
                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(mjmk1_annual['2021'] + mjmk2_annual['2021'] + ccmk1_annual['2021'] + jet_og_annual['2021'] + qj_annual['2021'] + pwj_annual['2021']), (mjmk1_annual['2021'] + mjmk2_annual['2021'] + ccmk1_annual['2021'] + jet_og_annual['2021'] + qj_annual['2021'] + pwj_annual['2021'] - (mjmk1_annual['2020'] + ccmk1_annual['2020'] + jet_og_annual['2020'] +  pwj_annual['2020'])))
                
                colc.subheader('Micro Jet MK2')
                colc.metric('', '{}'.format(mjmk2_annual['2021']), (mjmk2_annual['2021'] - mjmk2_annual['2020']))

                style_metric_cards()

        elif year == 2020:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2020']), (jet_og_annual['2020'] - jet_og_annual['2019']))
    
                colb.subheader('Micro Jet MK1')
                colb.metric('', '{}'.format(mjmk1_annual['2020']), (mjmk1_annual['2020'] - mjmk1_annual['2019']))

                colc.subheader('Power Jet')
                colc.metric('', '{}'.format(pwj_annual['2020']), (pwj_annual['2020'] - pwj_annual['2019']))

                colb.subheader('Cryo Clamp MK1')
                colb.metric('', '{}'.format(ccmk1_annual['2020']), (ccmk1_annual['2020'] - ccmk1_annual['2019']))

                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(mjmk1_annual['2020'] + ccmk1_annual['2020'] + jet_og_annual['2020'] +  pwj_annual['2020']), ((mjmk1_annual['2020'] + ccmk1_annual['2020'] + jet_og_annual['2020'] +  pwj_annual['2020']) - (mjmk1_annual['2019'] + ccmk1_annual['2019'] + jet_og_annual['2019'] +  pwj_annual['2019'])))
                

                style_metric_cards()

        elif year == 2019:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2019']), (jet_og_annual['2019'] - jet_og_annual['2018']))
    
                colb.subheader('Micro Jet MK1')
                colb.metric('', '{}'.format(mjmk1_annual['2019']), (mjmk1_annual['2019'] - mjmk1_annual['2018']))

                colc.subheader('Power Jet')
                colc.metric('', '{}'.format(pwj_annual['2019']), (pwj_annual['2019'] - pwj_annual['2018']))

                colb.subheader('Cryo Clamp MK1')
                colb.metric('', '{}'.format(ccmk1_annual['2019']), (ccmk1_annual['2019'] - ccmk1_annual['2018']))

                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(mjmk1_annual['2019'] + ccmk1_annual['2019'] + jet_og_annual['2019'] +  pwj_annual['2019']), ((mjmk1_annual['2019'] + ccmk1_annual['2019'] + jet_og_annual['2019'] +  pwj_annual['2019']) - (mjmk1_annual['2018'] + ccmk1_annual['2018'] + jet_og_annual['2018'] +  pwj_annual['2018'])))
                
                style_metric_cards()

        elif year == 2018:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2018']), (jet_og_annual['2018'] - jet_og_annual['2017']))

                colb.subheader('Power Jet')
                colb.metric('', '{}'.format(pwj_annual['2018']), (pwj_annual['2018'] - pwj_annual['2017']))

                colc.subheader('Cryo Clamp MK1')
                colc.metric('', '{}'.format(ccmk1_annual['2018']), (ccmk1_annual['2018'] - ccmk1_annual['2017']))

                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(ccmk1_annual['2018'] + jet_og_annual['2018'] +  pwj_annual['2018']), ((ccmk1_annual['2018'] + jet_og_annual['2018'] +  pwj_annual['2018']) - (ccmk1_annual['2017'] + jet_og_annual['2017'] +  pwj_annual['2017'])))

                style_metric_cards()

        elif year == 2017:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2017']), (jet_og_annual['2017'] - jet_og_annual['2016']))

                colb.subheader('Power Jet')
                colb.metric('', '{}'.format(pwj_annual['2017']), (pwj_annual['2017'] - pwj_annual['2016']))

                colc.subheader('**Total Jets**')
                colc.metric('', '{}'.format(jet_og_annual['2017'] + pwj_annual['2017']), ((jet_og_annual['2017'] +  pwj_annual['2017']) - (jet_og_annual['2016'] +  pwj_annual['2016'])))
            
                style_metric_cards()

        elif year == 2016:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                colb.subheader('DMX Jet')
                colb.metric('', '{}'.format(jet_og_annual['2016']), (jet_og_annual['2016'] - jet_og_annual['2015']))

                style_metric_cards()

        elif year == 2015:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                colb.subheader('DMX Jet')
                colb.metric('', '{}'.format(jet_og_annual['2015']), (jet_og_annual['2015'] - jet_og_annual['2014']))

                style_metric_cards()

        elif year == 2014:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                colb.subheader('DMX Jet')
                colb.metric('', '{}'.format(jet_og_annual['2014']), '')

                style_metric_cards()

            

    elif prod_cat == 'Controllers':

        with col2:
            year = ui.tabs(options=[2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015], default_value=2024, key='Control Year Select')

        if year == 2025:

            total_cntl_rev = annual_product_totals[5]['The Button'][1] + annual_product_totals[5]['Shostarter'][1] + annual_product_totals[5]['Shomaster'][1]
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('The Button')
                cola.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[5]['The Button'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[5]['The Button'][0]), annual_product_totals[5]['The Button'][0] - annual_product_totals[4]['The Button'][0])
                colb.subheader('Shostarter')
                colb.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[5]['Shostarter'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[5]['Shostarter'][0]), annual_product_totals[5]['Shostarter'][0] - annual_product_totals[4]['Shostarter'][0])
                colc.subheader('Shomaster')
                colc.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[5]['Shomaster'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[5]['Shomaster'][0]), annual_product_totals[5]['Shomaster'][0] - annual_product_totals[4]['Shomaster'][0])
    
                prod_profit_TB, profit_per_unit_TB, prod_profit_last_TB, avg_price_TB, avg_price_last_TB, wholesale_sales_TB, wholesale_percentage_TB, wholesale_delta_TB = calculate_product_metrics(annual_product_totals, 'The Button', 5, bom_cost_control)
                prod_profit_SS, profit_per_unit_SS, prod_profit_last_SS, avg_price_SS, avg_price_last_SS, wholesale_sales_SS, wholesale_percentage_SS, wholesale_delta_SS = calculate_product_metrics(annual_product_totals, 'Shostarter', 5, bom_cost_control)
                prod_profit_SM, profit_per_unit_SM, prod_profit_last_SM, avg_price_SM, avg_price_last_SM, wholesale_sales_SM, wholesale_percentage_SM, wholesale_delta_SM = calculate_product_metrics(annual_product_totals, 'Shomaster', 5, bom_cost_control)
    
                tot_cntl_rev25 = annual_product_totals[5]['The Button'][1] + annual_product_totals[5]['Shostarter'][1] + annual_product_totals[5]['Shomaster'][1]
                tot_cntl_prof25 = prod_profit_TB + prod_profit_SS + prod_profit_SM
                if tot_cntl_rev25 == 0:
                    cntl_prof_margin25 = 0
                else:
                    cntl_prof_margin25 = (tot_cntl_prof25 / tot_cntl_rev25) * 100
    
                cola.metric('**Total Revenue**', '${:,}'.format(int(tot_cntl_rev25)))
                colb.metric('**Profit Margin**', '{:,.2f}%'.format(cntl_prof_margin25))
                colc.metric('**Total Profit**', '${:,}'.format(int(tot_cntl_prof25)))
        
                st.divider()
                display_pie_chart_comp(annual_product_totals[5])
                st.divider()
                
                prod_select = ui.tabs(options=['The Button', 'Shostarter', 'Shomaster'], default_value='The Button', key='Controllers')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calculate_product_metrics(annual_product_totals, prod_select, 5, bom_cost_control)
                
                col5.metric('**Revenue**', '${:,.2f}'.format(annual_product_totals[5][prod_select][1]), percent_of_change(annual_product_totals[4][prod_select][0], annual_product_totals[5][prod_select][0]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_control[prod_select]), '')
                
                style_metric_cards()
                
                display_month_data_prod(prod_select, control25, control24) 
        
        elif year == 2024:

            total_cntl_rev = annual_product_totals[4]['The Button'][1] + annual_product_totals[4]['Shostarter'][1] + annual_product_totals[4]['Shomaster'][1]
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('The Button')
                cola.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[4]['The Button'][1] / total_24) * 100), '{}'.format(annual_product_totals[4]['The Button'][0]), annual_product_totals[4]['The Button'][0] - annual_product_totals[3]['The Button'][0])
                colb.subheader('Shostarter')
                colb.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[4]['Shostarter'][1] / total_24) * 100), '{}'.format(annual_product_totals[4]['Shostarter'][0]), annual_product_totals[4]['Shostarter'][0] - annual_product_totals[3]['Shostarter'][0])
                colc.subheader('Shomaster')
                colc.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[4]['Shomaster'][1] / total_24) * 100), '{}'.format(annual_product_totals[4]['Shomaster'][0]), annual_product_totals[4]['Shomaster'][0] - annual_product_totals[3]['Shomaster'][0])
    
                prod_profit_TB, profit_per_unit_TB, prod_profit_last_TB, avg_price_TB, avg_price_last_TB, wholesale_sales_TB, wholesale_percentage_TB, wholesale_delta_TB = calculate_product_metrics(annual_product_totals, 'The Button', 4, bom_cost_control)
                prod_profit_SS, profit_per_unit_SS, prod_profit_last_SS, avg_price_SS, avg_price_last_SS, wholesale_sales_SS, wholesale_percentage_SS, wholesale_delta_SS = calculate_product_metrics(annual_product_totals, 'Shostarter', 4, bom_cost_control)
                prod_profit_SM, profit_per_unit_SM, prod_profit_last_SM, avg_price_SM, avg_price_last_SM, wholesale_sales_SM, wholesale_percentage_SM, wholesale_delta_SM = calculate_product_metrics(annual_product_totals, 'Shomaster', 4, bom_cost_control)
    
                tot_cntl_rev24 = annual_product_totals[4]['The Button'][1] + annual_product_totals[4]['Shostarter'][1] + annual_product_totals[4]['Shomaster'][1]
                tot_cntl_prof24 = prod_profit_TB + prod_profit_SS + prod_profit_SM
                cntl_prof_margin24 = (tot_cntl_prof24 / tot_cntl_rev24) * 100
    
                cola.metric('**Total Revenue**', '${:,}'.format(int(tot_cntl_rev24)))
                colb.metric('**Profit Margin**', '{:,.2f}%'.format(cntl_prof_margin24))
                colc.metric('**Total Profit**', '${:,}'.format(int(tot_cntl_prof24)))
                
                st.divider()
                display_pie_chart_comp(annual_product_totals[4])
                st.divider()
                
                prod_select = ui.tabs(options=['The Button', 'Shostarter', 'Shomaster'], default_value='The Button', key='Controllers')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calculate_product_metrics(annual_product_totals, prod_select, 4, bom_cost_control)
    
                
                col5.metric('**Revenue**', '${:,.2f}'.format(annual_product_totals[4][prod_select][1]), percent_of_change(annual_product_totals[3][prod_select][0], annual_product_totals[4][prod_select][0]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_control[prod_select]), '')
    
                style_metric_cards()
                
                display_month_data_prod(prod_select, control24, control23)

        elif year == 2023:

            total_cntl_rev = annual_product_totals[3]['The Button'][1] + annual_product_totals[3]['Shostarter'][1] + annual_product_totals[3]['Shomaster'][1]
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('The Button')
                cola.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[3]['The Button'][1] / total_23) * 100), '{}'.format(annual_product_totals[3]['The Button'][0]), '')
                colb.subheader('Shostarter')
                colb.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[3]['Shostarter'][1] / total_23) * 100), '{}'.format(annual_product_totals[3]['Shostarter'][0]), '')
                colc.subheader('Shomaster')
                colc.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[3]['Shomaster'][1] / total_23) * 100), '{}'.format(annual_product_totals[3]['Shomaster'][0]), '')
    
                prod_profit_TB, profit_per_unit_TB, prod_profit_last_TB, avg_price_TB, avg_price_last_TB = calculate_product_metrics(annual_product_totals, 'The Button', 3, bom_cost_control)
                prod_profit_SS, profit_per_unit_SS, prod_profit_last_SS, avg_price_SS, avg_price_last_SS = calculate_product_metrics(annual_product_totals, 'Shostarter', 3, bom_cost_control)
                prod_profit_SM, profit_per_unit_SM, prod_profit_last_SM, avg_price_SM, avg_price_last_SM = calculate_product_metrics(annual_product_totals, 'Shomaster', 3, bom_cost_control)
    
                tot_cntl_rev23 = annual_product_totals[3]['The Button'][1] + annual_product_totals[3]['Shostarter'][1] + annual_product_totals[3]['Shomaster'][1]
                tot_cntl_prof23 = prod_profit_TB + prod_profit_SS + prod_profit_SM
                cntl_prof_margin23 = (tot_cntl_prof23 / tot_cntl_rev23) * 100
    
                cola.metric('**Total Revenue**', '${:,}'.format(int(tot_cntl_rev23)))
                colb.metric('**Profit Margin**', '{:,.2f}%'.format(cntl_prof_margin23))
                colc.metric('**Total Profit**', '${:,}'.format(int(tot_cntl_prof23)))
        
                st.divider()
                display_pie_chart_comp(annual_product_totals[3])
                st.divider()
                
                prod_select = ui.tabs(options=['The Button', 'Shostarter', 'Shomaster'], default_value='The Button', key='Controllers')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, avg_price, wholesale_sales, wholesale_percentage = calculate_product_metrics(annual_product_totals, prod_select, 3, bom_cost_control)
    
                col5.metric('**Revenue**', '${:,.2f}'.format(annual_product_totals[3][prod_select][1]), '')
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), '')
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), '')
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_control[prod_select]), '')
    
                style_metric_cards()
                
                display_month_data_prod(prod_select, control23)

        elif year == 2022:

            total_cntl = dmx_cntl_annual['2022'] + lcd_cntl_annual['2022'] + tbmk1_annual['2022'] + tbmk2_annual['2022'] + sm_annual['2022'] + pwr_cntl_annual['2022']
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('Shomaster')
                cola.metric('', '{}'.format(sm_annual['2022']), sm_annual['2022'] - sm_annual['2021'])
                cola.subheader('The Button MK1')
                cola.metric('', '{}'.format(tbmk1_annual['2022']), tbmk1_annual['2022'] - tbmk1_annual['2021'])
                colb.subheader('LCD Controller')
                colb.metric('', '{}'.format(lcd_cntl_annual['2022']), lcd_cntl_annual['2022'] - lcd_cntl_annual['2021'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2021'] + lcd_cntl_annual['2021'] + tbmk1_annual['2021'] + tbmk2_annual['2021'] + sm_annual['2021'] + pwr_cntl_annual['2021']))
                colc.subheader('DMX Controller')
                colc.metric('', '{}'.format(dmx_cntl_annual['2022']), dmx_cntl_annual['2022'] - dmx_cntl_annual['2021'])
                colc.subheader('The Button')
                colc.metric('', '{}'.format(tbmk2_annual['2022']), 'N/A')
    
                style_metric_cards()

        elif year == 2021:

            total_cntl = dmx_cntl_annual['2021'] + lcd_cntl_annual['2021'] + tbmk1_annual['2021'] + tbmk2_annual['2021'] + sm_annual['2021'] + pwr_cntl_annual['2021']
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('Shomaster')
                cola.metric('', '{}'.format(sm_annual['2021']), sm_annual['2021'] - sm_annual['2020'])
                cola.subheader('The Button MK1')
                cola.metric('', '{}'.format(tbmk1_annual['2021']), tbmk1_annual['2021'] - tbmk1_annual['2020'])
                colb.subheader('LCD Controller')
                colb.metric('', '{}'.format(lcd_cntl_annual['2021']), lcd_cntl_annual['2021'] - lcd_cntl_annual['2020'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2020'] + lcd_cntl_annual['2020'] + tbmk1_annual['2020'] + tbmk2_annual['2020'] + sm_annual['2020'] + pwr_cntl_annual['2020']))
                colc.subheader('DMX Controller')
                colc.metric('', '{}'.format(dmx_cntl_annual['2021']), dmx_cntl_annual['2021'] - dmx_cntl_annual['2020'])
                colc.subheader('Power Controller')
                colc.metric('', '{}'.format(pwr_cntl_annual['2021']), pwr_cntl_annual['2021'] - pwr_cntl_annual['2020'])
    
                style_metric_cards()

        elif year == 2020:

            total_cntl = dmx_cntl_annual['2020'] + lcd_cntl_annual['2020'] + tbmk1_annual['2020'] + tbmk2_annual['2020'] + sm_annual['2020'] + pwr_cntl_annual['2020']
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('LCD Controller')
                cola.metric('', '{}'.format(lcd_cntl_annual['2020']), lcd_cntl_annual['2020'] - lcd_cntl_annual['2019'])
                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2020']), dmx_cntl_annual['2020'] - dmx_cntl_annual['2019'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2019'] + lcd_cntl_annual['2019'] + tbmk1_annual['2019'] + tbmk2_annual['2019'] + sm_annual['2019'] + pwr_cntl_annual['2019']))
                colc.subheader('Power Controller')
                colc.metric('', '{}'.format(pwr_cntl_annual['2020']), pwr_cntl_annual['2020'] - pwr_cntl_annual['2019'])
    
                style_metric_cards()

        elif year == 2019:

            total_cntl = dmx_cntl_annual['2019'] + lcd_cntl_annual['2019'] + tbmk1_annual['2019'] + tbmk2_annual['2019'] + sm_annual['2019'] + pwr_cntl_annual['2019']
            
            with col2:
                cola, colb, colc = st.columns(3)

                cola.subheader('LCD Controller')
                cola.metric('', '{}'.format(lcd_cntl_annual['2019']), lcd_cntl_annual['2019'] - lcd_cntl_annual['2018'])
                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2019']), dmx_cntl_annual['2019'] - dmx_cntl_annual['2018'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2018'] + lcd_cntl_annual['2018'] + tbmk1_annual['2018'] + tbmk2_annual['2018'] + sm_annual['2018'] + pwr_cntl_annual['2018']))
                colc.subheader('Power Controller')
                colc.metric('', '{}'.format(pwr_cntl_annual['2019']), pwr_cntl_annual['2019'] - pwr_cntl_annual['2018'])
    
                style_metric_cards()

        elif year == 2018:

            total_cntl = dmx_cntl_annual['2018'] + lcd_cntl_annual['2018'] + tbmk1_annual['2018'] + tbmk2_annual['2018'] + sm_annual['2018'] + pwr_cntl_annual['2018']
            
            with col2:
                cola, colb, colc = st.columns(3)

                cola.subheader('LCD Controller')
                cola.metric('', '{}'.format(lcd_cntl_annual['2018']), lcd_cntl_annual['2018'] - lcd_cntl_annual['2017'])
                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2018']), dmx_cntl_annual['2018'] - dmx_cntl_annual['2017'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2017'] + lcd_cntl_annual['2017'] + tbmk1_annual['2017'] + tbmk2_annual['2017'] + sm_annual['2017'] + pwr_cntl_annual['2017']))
                colc.subheader('Power Controller')
                colc.metric('', '{}'.format(pwr_cntl_annual['2018']), pwr_cntl_annual['2018'] - pwr_cntl_annual['2017'])
    
                style_metric_cards()

        elif year == 2017:

            total_cntl = dmx_cntl_annual['2017'] + lcd_cntl_annual['2017'] + tbmk1_annual['2017'] + tbmk2_annual['2017'] + sm_annual['2017'] + pwr_cntl_annual['2017']
            
            with col2:
                cola, colb, colc = st.columns(3)
            
                cola.subheader('DMX Controller')
                cola.metric('', '{}'.format(dmx_cntl_annual['2017']), dmx_cntl_annual['2017'] - dmx_cntl_annual['2016'])
                colb.subheader('Power Controller')
                colb.metric('', '{}'.format(pwr_cntl_annual['2017']), pwr_cntl_annual['2017'] - pwr_cntl_annual['2016'])
                colc.subheader('Total Controllers')
                colc.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2016'] + lcd_cntl_annual['2016'] + tbmk1_annual['2016'] + tbmk2_annual['2016'] + sm_annual['2016'] + pwr_cntl_annual['2016']))

                style_metric_cards()

        elif year == 2016:

            with col2:
                cola, colb, colc = st.columns(3)

                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2016']), dmx_cntl_annual['2016'] - dmx_cntl_annual['2015'])
    
                style_metric_cards()
                
        elif year == 2015:

            with col2:
                cola, colb, colc = st.columns(3)

                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2015']), '')
    
                style_metric_cards()
            

    elif prod_cat == 'Handhelds':

        with col2:
            year = ui.tabs(options=[2025, 2024, 2023, 'Historical'], default_value=2024, key='Handheld Year Select')

        if year == 2025:

            total_hh_rev = annual_product_totals[8]['8FT - No Case'][1] + annual_product_totals[8]['8FT - Travel Case'][1] + annual_product_totals[8]['15FT - No Case'][1] + annual_product_totals[8]['15FT - Travel Case'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4)
        
                cola.subheader('8FT NC')
                cola.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[8]['8FT - No Case'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[8]['8FT - No Case'][0]), '{}'.format(annual_product_totals[8]['8FT - No Case'][0] - annual_product_totals[7]['8FT - No Case'][0]))
                cola.metric('', '${:,}'.format(int(annual_product_totals[8]['8FT - No Case'][1])), percent_of_change(annual_product_totals[7]['8FT - No Case'][1], annual_product_totals[8]['8FT - No Case'][1]))
                colb.subheader('8FT TC')
                colb.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[8]['8FT - Travel Case'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[8]['8FT - Travel Case'][0]),  '{}'.format(annual_product_totals[5]['8FT - Travel Case'][0] - annual_product_totals[7]['8FT - Travel Case'][0]))
                colb.metric('', '${:,}'.format(int(annual_product_totals[8]['8FT - Travel Case'][1])), percent_of_change(annual_product_totals[7]['8FT - Travel Case'][1], annual_product_totals[8]['8FT - Travel Case'][1]))
                colc.subheader('15FT NC')
                colc.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[8]['15FT - No Case'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[8]['15FT - No Case'][0]),  '{}'.format(annual_product_totals[5]['15FT - No Case'][0] - annual_product_totals[7]['15FT - No Case'][0]))
                colc.metric('', '${:,}'.format(int(annual_product_totals[8]['15FT - No Case'][1])), percent_of_change(annual_product_totals[7]['15FT - No Case'][1], annual_product_totals[8]['15FT - No Case'][1]))
                cold.subheader('15FT TC')
                cold.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[8]['15FT - Travel Case'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[8]['15FT - Travel Case'][0]),  '{}'.format(annual_product_totals[5]['15FT - Travel Case'][0] - annual_product_totals[7]['15FT - Travel Case'][0]))
                cold.metric('', '${:,}'.format(int(annual_product_totals[8]['15FT - Travel Case'][1])), percent_of_change(annual_product_totals[7]['15FT - Travel Case'][1], annual_product_totals[8]['15FT - Travel Case'][1]))
    
    
                prod_profit_8NC, profit_per_unit_8NC, prod_profit_last_8NC, avg_price_8NC, avg_price_last_8NC = calculate_product_metrics(annual_product_totals, '8FT - No Case', 8, bom_cost_hh)
                prod_profit_8TC, profit_per_unit_8TC, prod_profit_last_8TC, avg_price_8TC, avg_price_last_8TC = calculate_product_metrics(annual_product_totals, '8FT - Travel Case', 8, bom_cost_hh)
                prod_profit_15NC, profit_per_unit_15NC, prod_profit_last_15NC, avg_price_15NC, avg_price_last_15NC = calculate_product_metrics(annual_product_totals, '15FT - No Case', 8, bom_cost_hh)
                prod_profit_15TC, profit_per_unit_15TC, prod_profit_last_15TC, avg_price_15TC, avg_price_last_15TC = calculate_product_metrics(annual_product_totals, '15FT - Travel Case', 8, bom_cost_hh)
                
                tot_hh_rev25 = annual_product_totals[8]['8FT - No Case'][1] + annual_product_totals[8]['8FT - Travel Case'][1] + annual_product_totals[8]['15FT - No Case'][1] + annual_product_totals[8]['15FT - Travel Case'][1]
                tot_hh_prof25 = prod_profit_8NC + prod_profit_8TC + prod_profit_15NC + prod_profit_15TC
                if tot_hh_rev25 == 0:
                    prof_margin25 = 0
                else:
                    prof_margin25 = (tot_hh_prof25 / tot_hh_rev25) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_hh_rev25)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(prof_margin25))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_hh_prof25)))
            
                st.divider()
                display_pie_chart_comp(annual_product_totals[8])
                st.divider()
        
                prod_select = ui.tabs(options=['8FT - No Case', '8FT - Travel Case', '15FT - No Case', '15FT - Travel Case'], default_value='8FT - No Case', key='Handhelds')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calculate_product_metrics(annual_product_totals, prod_select, 8, bom_cost_hh)
                
                
                col5.metric('**Revenue**', '${:,}'.format(int(annual_product_totals[8][prod_select][1])), percent_of_change(annual_product_totals[7][prod_select][0], annual_product_totals[8][prod_select][0]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_hh[prod_select]), '')        
    
                style_metric_cards()
                
                display_month_data_prod(prod_select, handheld25, handheld24)
		
        elif year == 2024:

            total_hh_rev = annual_product_totals[7]['8FT - No Case'][1] + annual_product_totals[7]['8FT - Travel Case'][1] + annual_product_totals[7]['15FT - No Case'][1] + annual_product_totals[7]['15FT - Travel Case'][1]
            
            with col2:
                
                cola, colb, colc, cold = st.columns(4)
        
                cola.subheader('8FT NC')
                cola.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[7]['8FT - No Case'][1] / total_24) * 100), '{}'.format(annual_product_totals[7]['8FT - No Case'][0]), '{}'.format(annual_product_totals[7]['8FT - No Case'][0] - annual_product_totals[6]['8FT - No Case'][0]))
                cola.metric('', '${:,}'.format(int(annual_product_totals[7]['8FT - No Case'][1])), percent_of_change(annual_product_totals[6]['8FT - No Case'][1], annual_product_totals[7]['8FT - No Case'][1]))
                colb.subheader('8FT TC')
                colb.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[7]['8FT - Travel Case'][1] / total_24) * 100), '{}'.format(annual_product_totals[7]['8FT - Travel Case'][0]),  '{}'.format(annual_product_totals[7]['8FT - Travel Case'][0] - annual_product_totals[6]['8FT - Travel Case'][0]))
                colb.metric('', '${:,}'.format(int(annual_product_totals[7]['8FT - Travel Case'][1])), percent_of_change(annual_product_totals[6]['8FT - Travel Case'][1], annual_product_totals[7]['8FT - Travel Case'][1]))
                colc.subheader('15FT NC')
                colc.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[7]['15FT - No Case'][1] / total_24) * 100), '{}'.format(annual_product_totals[7]['15FT - No Case'][0]),  '{}'.format(annual_product_totals[7]['15FT - No Case'][0] - annual_product_totals[6]['15FT - No Case'][0]))
                colc.metric('', '${:,}'.format(int(annual_product_totals[7]['15FT - No Case'][1])), percent_of_change(annual_product_totals[6]['15FT - No Case'][1], annual_product_totals[7]['15FT - No Case'][1]))
                cold.subheader('15FT TC')
                cold.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[7]['15FT - Travel Case'][1] / total_24) * 100), '{}'.format(annual_product_totals[7]['15FT - Travel Case'][0]),  '{}'.format(annual_product_totals[7]['15FT - Travel Case'][0] - annual_product_totals[6]['15FT - Travel Case'][0]))
                cold.metric('', '${:,}'.format(int(annual_product_totals[7]['15FT - Travel Case'][1])), percent_of_change(annual_product_totals[6]['15FT - Travel Case'][1], annual_product_totals[7]['15FT - Travel Case'][1]))
    
    
                prod_profit_8NC, profit_per_unit_8NC, prod_profit_last_8NC, avg_price_8NC, avg_price_last_8NC = calculate_product_metrics(annual_product_totals, '8FT - No Case', 7, bom_cost_hh)
                prod_profit_8TC, profit_per_unit_8TC, prod_profit_last_8TC, avg_price_8TC, avg_price_last_8TC = calculate_product_metrics(annual_product_totals, '8FT - Travel Case', 7, bom_cost_hh)
                prod_profit_15NC, profit_per_unit_15NC, prod_profit_last_15NC, avg_price_15NC, avg_price_last_15NC = calculate_product_metrics(annual_product_totals, '15FT - No Case', 7, bom_cost_hh)
                prod_profit_15TC, profit_per_unit_15TC, prod_profit_last_15TC, avg_price_15TC, avg_price_last_15TC = calculate_product_metrics(annual_product_totals, '15FT - Travel Case', 7, bom_cost_hh)
                
                tot_hh_rev24 = annual_product_totals[7]['8FT - No Case'][1] + annual_product_totals[7]['8FT - Travel Case'][1] + annual_product_totals[7]['15FT - No Case'][1] + annual_product_totals[7]['15FT - Travel Case'][1]
                tot_hh_prof24 = prod_profit_8NC + prod_profit_8TC + prod_profit_15NC + prod_profit_15TC
                prof_margin24 = (tot_hh_prof24 / tot_hh_rev24) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_hh_rev24)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(prof_margin24))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_hh_prof24)))
            
                st.divider()
                display_pie_chart_comp(annual_product_totals[7])
                st.divider()
        
                prod_select = ui.tabs(options=['8FT - No Case', '8FT - Travel Case', '15FT - No Case', '15FT - Travel Case'], default_value='8FT - No Case', key='Handhelds')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calculate_product_metrics(annual_product_totals, prod_select, 7, bom_cost_hh)
                
                
                col5.metric('**Revenue**', '${:,}'.format(int(annual_product_totals[7][prod_select][1])), percent_of_change(annual_product_totals[6][prod_select][0], annual_product_totals[7][prod_select][0]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_hh[prod_select]), '')        
    
                style_metric_cards()
                
                display_month_data_prod(prod_select, handheld24, handheld23)
            
        elif year == 2023:

            total_hh_rev = annual_product_totals[6]['8FT - No Case'][1] + annual_product_totals[6]['8FT - Travel Case'][1] + annual_product_totals[6]['15FT - No Case'][1] + annual_product_totals[6]['15FT - Travel Case'][1]
            
            with col2:
                
                cola, colb, colc, cold = st.columns(4)
        
                cola.subheader('8FT NC')
                cola.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[6]['8FT - No Case'][1] / total_23) * 100), '{}'.format(annual_product_totals[6]['8FT - No Case'][0]), '')
                cola.metric('', '${:,}'.format(int(annual_product_totals[6]['8FT - No Case'][1])), '')
                colb.subheader('8FT TC')
                colb.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[6]['8FT - Travel Case'][1] / total_23) * 100), '{}'.format(annual_product_totals[6]['8FT - Travel Case'][0]),  '')
                colb.metric('', '${:,}'.format(int(annual_product_totals[6]['8FT - Travel Case'][1])), '')
                colc.subheader('15FT NC')
                colc.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[6]['15FT - No Case'][1] / total_23) * 100), '{}'.format(annual_product_totals[6]['15FT - No Case'][0]),  '')
                colc.metric('', '${:,}'.format(int(annual_product_totals[6]['15FT - No Case'][1])), '')
                cold.subheader('15FT TC')
                cold.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[6]['15FT - Travel Case'][1] / total_23) * 100), '{}'.format(annual_product_totals[6]['15FT - Travel Case'][0]),  '')
                cold.metric('', '${:,}'.format(int(annual_product_totals[6]['15FT - Travel Case'][1])), '')
    
    
                prod_profit_8NC, profit_per_unit_8NC, avg_price_8NC = calculate_product_metrics(annual_product_totals, '8FT - No Case', 6, bom_cost_hh)
                prod_profit_8TC, profit_per_unit_8TC, avg_price_8TC = calculate_product_metrics(annual_product_totals, '8FT - Travel Case', 6, bom_cost_hh)
                prod_profit_15NC, profit_per_unit_15NC, avg_price_15NC = calculate_product_metrics(annual_product_totals, '15FT - No Case', 6, bom_cost_hh)
                prod_profit_15TC, profit_per_unit_15TC, avg_price_15TC = calculate_product_metrics(annual_product_totals, '15FT - Travel Case', 6, bom_cost_hh)
                
                tot_hh_rev23 = annual_product_totals[6]['8FT - No Case'][1] + annual_product_totals[6]['8FT - Travel Case'][1] + annual_product_totals[6]['15FT - No Case'][1] + annual_product_totals[6]['15FT - Travel Case'][1]
                tot_hh_prof23 = prod_profit_8NC + prod_profit_8TC + prod_profit_15NC + prod_profit_15TC
                prof_margin23 = (tot_hh_prof23 / tot_hh_rev23) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_hh_rev23)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(prof_margin23))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_hh_prof23)))   
    
                st.divider()
                display_pie_chart_comp(annual_product_totals[6])
                st.divider()
        
                prod_select = ui.tabs(options=['8FT - No Case', '8FT - Travel Case', '15FT - No Case', '15FT - Travel Case'], default_value='8FT - No Case', key='Handhelds')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
        
                prod_profit = (annual_product_totals[6][prod_select][1]) - (annual_product_totals[6][prod_select][0] * bom_cost_hh[prod_select])
                avg_price = annual_product_totals[6][prod_select][1] / annual_product_totals[6][prod_select][0]
                profit_per_unit = avg_price - bom_cost_hh[prod_select]
                
                col5.metric('**Revenue**', '${:,.2f}'.format(annual_product_totals[6][prod_select][1]), '')
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), '')
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), '')
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_hh[prod_select]), '')        
                
                style_metric_cards()
                
                display_month_data_prod(prod_select, handheld23)

        elif year == 'Historical':

            mk1_tot = 0
            mk2_tot = 0

            for key, val in hhmk1_annual.items():
                mk1_tot += val
            for key, val in hhmk2_annual.items():
                mk2_tot += val

            with col2:
                
                cola, colb, colc = st.columns(3)
        
                cola.metric('**2022**', '{}'.format(hhmk1_annual['2022'] + hhmk2_annual['2022']), (hhmk1_annual['2022'] + hhmk2_annual['2022']) - (hhmk1_annual['2021'] + hhmk2_annual['2021']))
                cola.metric('**2019**', '{}'.format(hhmk1_annual['2019'] + hhmk2_annual['2019']), (hhmk1_annual['2019'] + hhmk2_annual['2019']) - hhmk1_annual['2018'])
                cola.metric('**2016**', '{}'.format(hhmk1_annual['2016']), hhmk1_annual['2016'] - hhmk1_annual['2015'])
                cola.metric('**Total MKII (Pre 2023)**', '{}'.format(mk2_tot), '')
     
                colb.metric('**2021**', '{}'.format(hhmk1_annual['2021'] + hhmk2_annual['2021']),  (hhmk1_annual['2021'] + hhmk2_annual['2021']) - (hhmk1_annual['2020'] + hhmk2_annual['2020']))
                colb.metric('**2018**', '{}'.format(hhmk1_annual['2018']), hhmk1_annual['2018'] - hhmk1_annual['2017'])
                colb.metric('**2015**', '{}'.format(hhmk1_annual['2015']), hhmk1_annual['2015'] - hhmk1_annual['2014'])
                colb.metric('**2013**', '{}'.format(hhmk1_annual['2013']), '')
                
                colc.metric('**2020**', '{}'.format(hhmk1_annual['2020'] + hhmk2_annual['2020']),  (hhmk1_annual['2020'] + hhmk2_annual['2020']) - (hhmk1_annual['2019'] + hhmk2_annual['2019']))
                colc.metric('**2017**', '{}'.format(hhmk1_annual['2017']), hhmk1_annual['2017'] - hhmk1_annual['2016'])
                colc.metric('**2014**', '{}'.format(hhmk1_annual['2014']), hhmk1_annual['2014'] - hhmk1_annual['2013'])
                colc.metric('**Total MKI (Pre 2023)**', '{}'.format(mk1_tot), '')

                style_metric_cards()

                hh_dict = {}
                
                hh_dict['2025'] = to_date_product('CC-HCCMKII-08-NC') + to_date_product('CC-HCCMKII-08-TC') + to_date_product('CC-HCCMKII-15-NC') + to_date_product('CC-HCCMKII-15-TC')
                hh_dict['2024'] = annual_product_totals[7]['8FT - No Case'][0] + annual_product_totals[7]['8FT - Travel Case'][0] + annual_product_totals[7]['15FT - No Case'][0] + annual_product_totals[7]['15FT - Travel Case'][0]
                hh_dict['2023'] = annual_product_totals[6]['8FT - No Case'][0] + annual_product_totals[6]['8FT - Travel Case'][0] + annual_product_totals[6]['15FT - No Case'][0] + annual_product_totals[6]['15FT - Travel Case'][0]
                
                for year, sales in hhmk1_annual.items():
                    hh_dict[year] = sales

                for year, sales in hhmk2_annual.items():
                    hh_dict[year] += sales


                hh_dict = {key: hh_dict[key] for key in reversed(hh_dict)}

                plot_bar_chart_hh(format_for_chart_hh(hh_dict))

        
    elif prod_cat == 'Hoses':

        with col2:
            hose_scope = ui.tabs(options=['Overview', 'Profit'], default_value='Overview', key='Hose Metric Scope')

        if hose_scope == 'Overview':
            cola, colb, colc = st.columns([.2, .6, .2])
            with colb:
                display_hose_data(hose_detail25, hose_detail24, hose_detail23)
                
        if hose_scope == 'Profit':
            
            cola, colb, colc = st.columns([.2, .6, .2])
            with colb:
                display_hose_data_profit(hose_detail25, hose_detail24, hose_detail23)
          
    elif prod_cat == 'Accessories':

        with col2:
            acc_scope = ui.tabs(options=['Overview', 'Profit'], default_value='Overview', key='Acc Metric Scope')

        cola, colb, colc, cold, cole, colf, colg = st.columns([.1,.1,.2,.2,.2,.1,.1])
        colc.subheader('2025')
        cold.subheader('2024')
        cole.subheader('2023')

        if acc_scope == 'Overview':

            display_acc_data()

        if acc_scope == 'Profit':
            with colc:
                for item, value in annual_product_totals[-1].items():
                    prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calculate_product_metrics(annual_product_totals, item, 14, bom_cost_acc) 
                    if item == 'CC-RC-2430':
                        ui.metric_card(title='{}'.format(item), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit))
                    else:
                        value[0] = int(value[0])
                        ui.metric_card(title='{}'.format(item), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit)) 
            with cold:
                key = '9jasdig'
                for item_last, value_last in annual_product_totals[-2].items():
                    prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calculate_product_metrics(annual_product_totals, item_last, 13, bom_cost_acc)
                    if item_last == 'CC-RC-2430':
                        ui.metric_card(title='{}'.format(item_last), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit))
                    else:
                        value_last[0] = int(value_last[0])
                        ui.metric_card(title='{}'.format(item_last), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit), key=key)
                    key += 'adsg2f'
            with cole:
                key2 = 'a'
                for item_last2, value_last2 in annual_product_totals[-3].items():
                    prod_profit, profit_per_unit, avg_price = calculate_product_metrics(annual_product_totals, item_last2, 12, bom_cost_acc)
                    if item_last2 == 'CC-RC-2430':
                        ui.metric_card(title='{}'.format(item_last2), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit), key=key2)
                    else:
                        value_last2[0] = int(value_last2[0])
                        ui.metric_card(title='{}'.format(item_last2), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit), key=key2)
                    key2 += 'ba'

    elif prod_cat == 'MagicFX':
        
        with col2:
            year = ui.tabs(options=[2025, 2024, 2023], default_value=2024, key='Products Year Select')

        cola, colx, coly, colz, colb = st.columns([.15, .23, .23, .23, .15], gap='medium')

        if year == 2025:

            idx = 0
            
            count, magic_dict = magic_sales('2025')

            
            for key, val in magic_dict.items():
                if val[0] >= 1:
                    if 0 <= idx <= 5:
                        colx.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))
                    elif 5 < idx <= 10:
                        coly.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))    
                    else:
                        colz.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))

                    idx += 1
            
        if year == 2024:

            idx = 0
            
            count, magic_dict = magic_sales('2024')

            
            for key, val in magic_dict.items():
                if val[0] >= 1:
                    if 0 <= idx <= 5:
                        colx.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))
                    elif 5 < idx <= 10:
                        coly.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))    
                    else:
                        colz.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))

                    idx += 1

        if year == 2023:

            idx = 0
            
            count, magic_dict = magic_sales('2023')
            for key, val in magic_dict.items():
                if val[0] >= 1:
                    if 0 <= idx <= 5:
                        colx.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))
                    elif 5 < idx <= 10:
                        coly.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))    
                    else:
                        colz.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))

                    idx += 1
            
        style_metric_cards()

        
        
### SHIPPING REPORTS ###  
    
if task_choice == 'Shipping Reports':

    st.header('Shipping Records')
	
    def get_month_ship_payments(df, month):

        return df[month].iloc[26]

    
    def fulcrum_ship_total(df, month_list):
        fulcrum_ship_charges = 0
    
        
        for month in month_list:
            fulcrum_ship_charges += df[month].iloc[26]
    
        return fulcrum_ship_charges
    
    def shipping_balance_calc(ship_costs, ship_payments):
        
        perc_return = (ship_payments / ship_costs) * 100
        
        return perc_return

    
    shipping_2023 = {'January': [1046.73, 0, 0, 0], 'February': [0, 0, 0, 0], 'March': [570.89, 0, 0, 0], 'April': [605.12, 0, 0, 0], 'May': [383.41, 0, 0, 0], 'June': [0, 0, 0, 0], 'July': [0, 0, 0, 0], 'August': [0, 0, 0, 0], 'September': [0, 0, 0, 0], 'October': [465.49, 0, 0, 0], 'November': [269.76, 0, 0, 0], 'December': [473.38, 0, 0, 0]}
    
    shipping_2024 = {'January': [1220.28, 0, 0, 0], 'February': [704.57, 0, 0, 0], 'March': [535.58, 0, 0, 0], 'April': [150.92, 0, 0, 0], 'May': [974, 0, 0, 0], 'June': [1445.19, 0, 0, 0], 'July': [852.65, 0, 0, 0], 'August': [441.59, 0, 0, 0], 'September': [283.87, 0, 0, 0], 'October': [407.11, 0, 0, 0], 'November': [340.58, 0, 0, 0], 'December': [0, 0, 0, 0]}


    ss_year_select = st.selectbox('Select Year',
                                 options=['2024', '2023'])
    
    fedex_total = 0
    ups_total = 0
    shipstat_cc_charges = 0
    shipstat_cust_pmnts = 0
    fulcrum_ship_charges = 0


    if ss_year_select == '2024':

        fulcrum_ship_charges += 7356.34
        
        fulcrum_ship_pmnts_24 = fulcrum_ship_total(df_ac24_rev, months_x)
        for month in months_x:
            shipping_2024[month][1] += get_month_ship_payments(df_ac24_rev, month)

        idx = 0
        
        for order in df_shipstat_24.order_number:
            
            shipping_2024[num_to_month(df_shipstat_24.iloc[idx].shipdate.month)][0] += df_shipstat_24.iloc[idx].cc_cost
                
            if df_shipstat_24.iloc[idx].order_number[0] == 'F':
                fulcrum_ship_charges += df_shipstat_24.iloc[idx].cc_cost
                if df_shipstat_24.iloc[idx].provider == 'FedEx':
                    fedex_total += df_shipstat_24.iloc[idx].cc_cost
                    shipping_2024[num_to_month(df_shipstat_24.iloc[idx].shipdate.month)][2] += df_shipstat_24.iloc[idx].cc_cost
                elif df_shipstat_24.iloc[idx].provider[:3] == 'UPS':
                    ups_total += df_shipstat_24.iloc[idx].cc_cost
                    shipping_2024[num_to_month(df_shipstat_24.iloc[idx].shipdate.month)][3] += df_shipstat_24.iloc[idx].cc_cost
            else:
                shipstat_cc_charges += df_shipstat_24.iloc[idx].cc_cost
                shipstat_cust_pmnts += df_shipstat_24.iloc[idx].cust_cost
                shipping_2024[num_to_month(df_shipstat_24.iloc[idx].shipdate.month)][1] += df_shipstat_24.iloc[idx].cust_cost
                if df_shipstat_24.iloc[idx].provider == 'FedEx':
                    fedex_total += df_shipstat_24.iloc[idx].cc_cost
                    shipping_2024[num_to_month(df_shipstat_24.iloc[idx].shipdate.month)][2] += df_shipstat_24.iloc[idx].cc_cost
                elif df_shipstat_24.iloc[idx].provider[:3] == 'UPS':
                    ups_total += df_shipstat_24.iloc[idx].cc_cost
                    shipping_2024[num_to_month(df_shipstat_24.iloc[idx].shipdate.month)][3] += df_shipstat_24.iloc[idx].cc_cost
            idx += 1
            
        total_ship_cost = shipstat_cc_charges + fulcrum_ship_charges
        total_ship_pmnts = shipstat_cust_pmnts + fulcrum_ship_pmnts_24

        col1, col2, col3 = st.columns(3)

        with col1:
            ui.metric_card(title='Total Paid', content='${:,.2f}'.format(total_ship_cost), description='')
            ui.metric_card(title='FedEx', content='${:,.2f}'.format(fedex_total), description='({:.2f}%)'.format(percent_of_sales(fedex_total, ups_total)))
        with col2:
            var = ''
            balance = total_ship_pmnts - total_ship_cost
            if balance > 0:
                var = '+'
            elif balance < 0:
                var = '-'
            ui.metric_card(title='Balance', content='{} ${:,.2f}'.format(var, abs(balance)), description='')
            ui.metric_card(title='Freight', content='$6,539.43', description = '65% Air / 35% Motor')   
        with col3:
            ui.metric_card(title='Total Collected', content='${:,.2f}'.format(total_ship_pmnts), description='')
            ui.metric_card(title='UPS', content='${:,.2f}'.format(ups_total), description='({:.2f}%)'.format(percent_of_sales(ups_total, fedex_total)))
    
        #st.write('FedEx Charges: ${:,.2f} - '.format(fedex_total) + '({:.2f}%)'.format(percent_of_sales(fedex_total, ups_total)))
        
        #st.write('UPS Charges: ${:,.2f} - '.format(ups_total) + '({:.2f}%)'.format(percent_of_sales(ups_total, fedex_total)))    
        
        #st.write('Website Cost: ${:,.2f}'.format(shipstat_cc_charges))
        #st.write('Website Payments: ${:,.2f}'.format(shipstat_cust_pmnts))
        
        #st.write('Fulcrum Charges: ${:,.2f}'.format(fulcrum_ship_charges))
        #st.write('Fulcrum Payments: ${:,.2f}'.format(fulcrum_ship_pmnts_24))

        #st.divider()
        
        #st.subheader('Total Charges: ${:,.2f}'.format(total_ship_cost))
        #st.subheader('Total Payments: ${:,.2f}'.format(total_ship_pmnts))

        #st.divider()
        
        idx = 0
        
        for key, val in shipping_2024.items():
            if idx in [0, 3, 6, 9]:
                col1.subheader(key)
                col1.markdown(' - Charges: ${:,.2f}'.format(val[0]))
                col1.markdown(' - Payments: ${:,.2f}'.format(val[1]))
                col1.markdown(' - FedEx Charges: ${:,.2f}'.format(val[2]))
                col1.markdown(' - UPS Charges: ${:,.2f}'.format(val[3]))
            elif idx in [1, 4, 7, 10]:
                col2.subheader(key)
                col2.markdown(' - Charges: ${:,.2f}'.format(val[0]))
                col2.markdown(' - Payments: ${:,.2f}'.format(val[1]))
                col2.markdown(' - FedEx Charges: ${:,.2f}'.format(val[2]))
                col2.markdown(' - UPS Charges: ${:,.2f}'.format(val[3]))
            else:
                col3.subheader(key)
                col3.markdown(' - Charges: ${:,.2f}'.format(val[0]))
                col3.markdown(' - Payments: ${:,.2f}'.format(val[1]))
                col3.markdown(' - FedEx Charges: ${:,.2f}'.format(val[2]))
                col3.markdown(' - UPS Charges: ${:,.2f}'.format(val[3]))

            idx += 1

    
    elif ss_year_select == '2023':

        fulcrum_ship_charges += 4173.37
        
        fulcrum_ship_pmnts_23 = fulcrum_ship_total(df_ac23_rev, months_x)
        for month in months_x:
            shipping_2023[month][1] += get_month_ship_payments(df_ac23_rev, month)
            
        idx = 0
        
        for order in df_shipstat_23.order_number:

            shipping_2023[num_to_month(df_shipstat_23.iloc[idx].shipdate.month)][0] += df_shipstat_23.iloc[idx].cc_cost
        
            if df_shipstat_23.iloc[idx].order_number[0] == 'F':
                fulcrum_ship_charges += df_shipstat_23.iloc[idx].cc_cost
                if df_shipstat_23.iloc[idx].provider == 'FedEx':
                    fedex_total += df_shipstat_23.iloc[idx].cc_cost
                    shipping_2023[num_to_month(df_shipstat_23.iloc[idx].shipdate.month)][2] += df_shipstat_23.iloc[idx].cc_cost
                elif df_shipstat_23.iloc[idx].provider[:3] == 'UPS':
                    ups_total += df_shipstat_23.iloc[idx].cc_cost
                    shipping_2023[num_to_month(df_shipstat_23.iloc[idx].shipdate.month)][3] += df_shipstat_23.iloc[idx].cc_cost
            else:
                shipstat_cc_charges += df_shipstat_23.iloc[idx].cc_cost
                shipstat_cust_pmnts += df_shipstat_23.iloc[idx].cust_cost
                shipping_2023[num_to_month(df_shipstat_23.iloc[idx].shipdate.month)][1] += df_shipstat_23.iloc[idx].cust_cost
                if df_shipstat_23.iloc[idx].provider == 'FedEx':
                    fedex_total += df_shipstat_23.iloc[idx].cc_cost
                    shipping_2023[num_to_month(df_shipstat_23.iloc[idx].shipdate.month)][2] += df_shipstat_23.iloc[idx].cc_cost
                elif df_shipstat_23.iloc[idx].provider[:3] == 'UPS':
                    ups_total += df_shipstat_23.iloc[idx].cc_cost
                    shipping_2023[num_to_month(df_shipstat_23.iloc[idx].shipdate.month)][3] += df_shipstat_23.iloc[idx].cc_cost
                    
            idx += 1
            
        total_ship_cost = shipstat_cc_charges + fulcrum_ship_charges
        total_ship_pmnts = shipstat_cust_pmnts + fulcrum_ship_pmnts_23

        col1, col2, col3 = st.columns(3)

        with col1:
            ui.metric_card(title='Total Paid', content='${:,.2f}'.format(total_ship_cost), description='')
            ui.metric_card(title='FedEx', content='${:,.2f}'.format(fedex_total), description='({:.2f}%)'.format(percent_of_sales(fedex_total, ups_total)))
        with col2:
            var = ''
            balance = total_ship_pmnts - total_ship_cost
            if balance > 0:
                var = '+'
            elif balance < 0:
                var = '-'
            ui.metric_card(title='Balance', content='{} ${:,.2f}'.format(var, abs(balance)), description='')
            ui.metric_card(title='Freight', content='$6,539.43', description = '65% Air / 35% Motor')
        with col3:
            ui.metric_card(title='Total Collected', content='${:,.2f}'.format(total_ship_pmnts), description='')
            ui.metric_card(title='UPS', content='${:,.2f}'.format(ups_total), description='({:.2f}%)'.format(percent_of_sales(ups_total, fedex_total)))
    
        #st.write('FedEx Charges: ${:,.2f} - '.format(fedex_total) + '({:.2f}%)'.format(percent_of_sales(fedex_total, ups_total)))
        
        #st.write('UPS Charges: ${:,.2f} - '.format(ups_total) + '({:.2f}%)'.format(percent_of_sales(ups_total, fedex_total)))    
        
        #st.write('Website Cost: ${:,.2f}'.format(shipstat_cc_charges))
        #st.write('Website Payments: ${:,.2f}'.format(shipstat_cust_pmnts))
        
        #st.write('Fulcrum Charges: ${:,.2f}'.format(fulcrum_ship_charges))
        #st.write('Fulcrum Payments: ${:,.2f}'.format(fulcrum_ship_pmnts_23))

        #st.divider()
        
        #st.subheader('Total Charges: ${:,.2f}'.format(total_ship_cost))
        #st.subheader('Total Payments: ${:,.2f}'.format(total_ship_pmnts))

        #st.divider()
        idx = 0
        for key, val in shipping_2023.items():
            if idx in [0, 3, 6, 9]:
                col1.subheader(key)
                col1.markdown(' - Charges: ${:,.2f}'.format(val[0]))
                col1.markdown(' - Payments: ${:,.2f}'.format(val[1]))
                col1.markdown(' - FedEx Charges: ${:,.2f}'.format(val[2]))
                col1.markdown(' - UPS Charges: ${:,.2f}'.format(val[3]))
            elif idx in [1, 4, 7, 10]:
                col2.subheader(key)
                col2.markdown(' - Charges: ${:,.2f}'.format(val[0]))
                col2.markdown(' - Payments: ${:,.2f}'.format(val[1]))
                col2.markdown(' - FedEx Charges: ${:,.2f}'.format(val[2]))
                col2.markdown(' - UPS Charges: ${:,.2f}'.format(val[3]))
            else:
                col3.subheader(key)
                col3.markdown(' - Charges: ${:,.2f}'.format(val[0]))
                col3.markdown(' - Payments: ${:,.2f}'.format(val[1]))
                col3.markdown(' - FedEx Charges: ${:,.2f}'.format(val[2]))
                col3.markdown(' - UPS Charges: ${:,.2f}'.format(val[3]))

            idx += 1
    
    
    #st.write('{:.2f}%'.format(shipping_balance_calc(total_ship_cost, total_ship_pmnts)))
    
    #st.write(df_ac24_rev)
    #st.write(df_ac24_rev['January'].iloc[26])

### QUOTE REPORTS ###
if task_choice == 'Quote Reports':

    colx, coly, colz = st.columns([.2, .6, .2])

    with coly:
        st.header('Quote Reports')
        
        quote_cust = st.multiselect('Search Customers',
                                options=quote_cust_list, 
                                max_selections=1,
                                placeholder='Start Typing Customer Name')

    if len(quote_cust) >= 1:
        quote_cust = quote_cust[0]
    else:
        quote_cust = ''

    idx = 0
    cust_list_q = []
    cust_won_list = []
    cust_lost_list = []
    cust_won_total = 0
    cust_won_count = 0
    cust_lost_total = 0
    cust_lost_count = 0
    won_total = 0
    lost_total = 0
    won_count = 0
    lost_count = 0

    for customer in df_quotes.customer:
        
        if df_quotes.iloc[idx].status == 'Won':
            won_total += df_quotes.iloc[idx].total
            won_count += 1
        else:
            lost_total += df_quotes.iloc[idx].total
            lost_count += 1 

        if customer.upper() == quote_cust.upper():
    
            if df_quotes.iloc[idx].status == 'Won':
                cust_won_total += df_quotes.iloc[idx].total
                cust_won_count += 1
                cust_won_list.append('({}) - **${:,.2f}**  - {}'.format(
                df_quotes.iloc[idx].number,
                df_quotes.iloc[idx].total,
                df_quotes.iloc[idx].date_created.year))
                
            if df_quotes.iloc[idx].status == 'Lost' or df_quotes.iloc[idx].status == 'Sent' or df_quotes.iloc[idx].status == 'Draft':
                cust_lost_total += df_quotes.iloc[idx].total
                cust_lost_count += 1
                cust_lost_list.append('({}) - **${:,.2f}**  - {}'.format(
                df_quotes.iloc[idx].number,
                df_quotes.iloc[idx].total,
                df_quotes.iloc[idx].date_created.year))
            
            cust_list_q.append('({})  {}  - ${:,.2f}  - {} - {}'.format(
                df_quotes.iloc[idx].number,
                df_quotes.iloc[idx].customer,
                df_quotes.iloc[idx].total,
                df_quotes.iloc[idx].date_created,
                df_quotes.iloc[idx].status))

        idx += 1

    coly.header('')
    coly.header('')

    if len(quote_cust) < 1:
        coly.subheader('Totals:')
        with coly:
            cola, colb, colc, cold = st.columns(4)
    
            cola.metric('**Quotes Won**', str(won_count), '${:,.2f}'.format(won_total))
            colb.metric('**Conversion Percentage**', '{:,.2f}%'.format((won_count / (lost_count + won_count)) * 100))
            colc.metric('**Potential Rev. Collected**', '{:,.2f}%'.format((won_total / (lost_total + won_total)) * 100))
            cold.metric('**Quotes Lost**', str(lost_count), '-${:,.2f}'.format(lost_total))
            style_metric_cards()
    
    if len(quote_cust) > 1:

        with coly:
            col1, col2, col3, col4 = st.columns(4)
            with st.container(border=True):        
                col1.metric('**Quotes Won**', str(cust_won_count), '${:,.2f}'.format(cust_won_total)) 
                
            with st.container(border=True):
                col4.metric('**Quotes Lost / Open**', str(cust_lost_count), '-${:,.2f}'.format(cust_lost_total))
            
            if cust_lost_count >= 1 and cust_won_count >= 1:
                col2.metric('**Conversion Percentage**', '{:,.2f}%'.format((cust_won_count / (cust_lost_count + cust_won_count)) * 100))
                col3.metric('**Potential Rev. Collected**', '{:,.2f}%'.format((cust_won_total / (cust_lost_total + cust_won_total)) * 100))
                
                st.divider()
    
                col1, col2 = st.columns(2)
                col1.subheader('Won')
                col2.subheader('Lost')
                with st.container(border=True):
                    for quote in cust_won_list:
                        col1.markdown(' - {}'.format(quote))
                with st.container(border=True):
                    for quote in cust_lost_list:
                        col2.markdown(' - {}'.format(quote))
                    
    
        style_metric_cards()


if task_choice == 'Customer Details':
    
    
    cola, colb, colc = st.columns([.25, .5, .25])
    
    with colb:
        st.header('Customer Details')

        text_input = st.multiselect('Search Customers', 
                                   options=unique_customer_list, 
                                   max_selections=1,
                                   placeholder='Start Typing Customer Name')
    
    if len(text_input) >= 1:
        text_input = text_input[0]
    else:
        text_input = ''

    
    ### PRODUCT CATEGORY LISTS ###
    sales_order_list = []
    jet_list = []
    controller_list = []
    misc_list = []
    magic_list = []
    hose_list = []
    fittings_accessories_list = []
    handheld_list = []
    
    ### PRODUCT TOTALS SUMMARY DICTS ###
    jet_totals_cust = {'Quad Jet': 0, 
                      'Pro Jet': 0, 
                      'Micro Jet MKII': 0,
                      'Cryo Clamp': 0}
    controller_totals_cust = {'The Button': 0,
                             'Shostarter': 0,
                             'Shomaster': 0}
    cust_handheld_cnt = 0
    cust_LED_cnt = 0
    cust_RC_cnt = 0
    
    ### LISTS OF HISTORICAL SALES FOR CUSTOMER ###
    spend_total = {2023: None, 2024: None, 2025: None}
    spend_total_2023 = 0.0
    spend_total_2024 = 0.0
    spend_total_2025 = 0.0
    sales_order_list = []
    
    idx = 0
    
    for customer in df.customer:
        
        if customer.upper() == text_input.upper():
            
            ### LOCATE AND PULL SPEND TOTALS FOR SELECTED CUSTOMER AND ADD TO LISTS ###
            if df.iloc[idx].ordered_year == '2023':
                spend_total_2023 += df.iloc[idx].total_line_item_spend
            elif df.iloc[idx].ordered_year == '2024':
                spend_total_2024 += df.iloc[idx].total_line_item_spend
    
    
    
            ### LOCATE ALL ITEMS FROM SOLD TO SELECTED CUSTOMER AND ADD TO LISTS ###
            if df.iloc[idx].item_sku[:5] == 'CC-QJ' or df.iloc[idx].item_sku[:5] == 'CC-PR' or df.iloc[idx].item_sku[:5] == 'CC-MJ' or df.iloc[idx].item_sku[:6] == 'CC-CC2':
                jet_list.append('|    {}    |     ( {}x )    {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    df.iloc[idx].quantity,
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
                if df.iloc[idx].item_sku[:5] == 'CC-QJ':
                    jet_totals_cust['Quad Jet'] += df.iloc[idx].quantity
                elif df.iloc[idx].item_sku[:5] == 'CC-PR':
                    jet_totals_cust['Pro Jet'] += df.iloc[idx].quantity
                elif df.iloc[idx].item_sku[:5] == 'CC-MJ':
                    jet_totals_cust['Micro Jet MKII'] += df.iloc[idx].quantity
                elif df.iloc[idx].item_sku[:6] == 'CC-CC2':
                    jet_totals_cust['Cryo Clamp'] += df.iloc[idx].quantity
            elif df.iloc[idx].item_sku[:5] == 'CC-TB' or df.iloc[idx].item_sku[:5] == 'CC-SS' or df.iloc[idx].item_sku[:5] == 'CC-SM':
                controller_list.append('|    {}    |     ( {}x )    {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    df.iloc[idx].quantity,
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
                if df.iloc[idx].item_sku[:5] == 'CC-TB':
                    controller_totals_cust['The Button'] += df.iloc[idx].quantity
                elif df.iloc[idx].item_sku[:5] == 'CC-SS':
                    controller_totals_cust['Shostarter'] += df.iloc[idx].quantity
                elif df.iloc[idx].item_sku[:5] == 'CC-SM':
                    controller_totals_cust['Shomaster'] += df.iloc[idx].quantity
            elif df.iloc[idx].item_sku[:5] == 'Magic' or df.iloc[idx].item_sku[:4] == 'MFX-':
                magic_list.append('|    {}    |     ( {}x )    {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    df.iloc[idx].quantity,
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
            elif df.iloc[idx].item_sku[:5] == 'CC-CH':
                hose_list.append('|    {}    |     ( {}x )    {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    df.iloc[idx].quantity,
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
            elif df.iloc[idx].item_sku[:5] == 'CC-F-' or df.iloc[idx].item_sku[:5] == 'CC-AC' or df.iloc[idx].item_sku[:5] == 'CC-CT' or df.iloc[idx].item_sku[:5] == 'CC-WA':
                fittings_accessories_list.append('|    {}    |     ( {}x )    {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    df.iloc[idx].quantity,
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
                if df.iloc[idx].item_sku[:9] == 'CC-AC-LA2':
                    cust_LED_cnt += df.iloc[idx].quantity                    
            elif df.iloc[idx].item_sku[:6] == 'CC-HCC' or df.iloc[idx].item_sku[:6] == 'Handhe':
                handheld_list.append('|    {}    |     ( {}x )    {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    df.iloc[idx].quantity,
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
                cust_handheld_cnt += df.iloc[idx].quantity
            elif df.iloc[idx].item_sku[:5] == 'Shipp' or df.iloc[idx].item_sku[:5] == 'Overn' or df.iloc[idx].item_sku[:5] == 'CC-NP':
                pass
            else:
                misc_list.append('|    {}    |     ( {}x )     {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    df.iloc[idx].quantity,
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
                if df.iloc[idx].item_sku == 'CC-RC-2430':
                    cust_RC_cnt += df.iloc[idx].quantity

            if df.iloc[idx].sales_order in sales_order_list:
                pass
            else:
                sales_order_list.append(df.iloc[idx].sales_order)
        idx += 1
        
    perc_change = percent_of_change(spend_total_2023, spend_total_2024)   
    perc_change2 = percent_of_change(spend_total_2024, spend_total_2025)
    
    with colb:
        st.header('')
        st.subheader('')
    
        ### DISPLAY PRODUCT PURCHASE SUMMARIES FOR SELECTED CUSTOMER ###
        if len(text_input) > 1:
    
            col3, col4, col5, col6 = st.columns(4)
            
            ### DISPLAY CUSTOMER SPENDING TRENDS AND TOTALS
            with col3:
                st.metric('2023 Spending', '${:,.2f}'.format(spend_total_2023), '')
        
            with col4:
                st.metric('2024 Spending', '${:,.2f}'.format(spend_total_2024), perc_change)

            with col5:
                st.metric('2025 Spending', '${:,.2f}'.format(spend_total_2025), perc_change2)
                
            with col6:
                st.metric('Total Spending', '${:,.2f}'.format(spend_total_2023 + spend_total_2024), '')
    
            style_metric_cards()       
            
            st.subheader('Product Totals:')
            col6, col7, col8 = st.columns(3)
            with col6.container(border=True):
                for jet, totl in jet_totals_cust.items():
                    if totl > 0:
                        st.markdown(' - **{}: {}**'.format(jet, totl))
            with col7.container(border=True):
                for controller, totl in controller_totals_cust.items():
                    if totl > 0:
                        st.markdown(' - **{}: {}**'.format(controller, totl))
                if cust_handheld_cnt > 0:
                    st.markdown(' - **Handhelds: {}**'.format(cust_handheld_cnt))
            with col8.container(border=True):
                if cust_LED_cnt > 0:
                    st.markdown(' - **LED Attachment II: {}**'.format(cust_LED_cnt))
                if cust_RC_cnt > 0:
                    st.markdown(' - **Road Cases: {}**'.format(cust_RC_cnt))
    
### DISPLAY CATEGORIES OF PRODUCTS PURCHASED BY SELECTED CUSTOMER ###
        if len(jet_list) >= 1:
            with st.container(border=True):
                st.subheader('Stationary Jets:')
                for item in jet_list:
                    st.markdown(item)
        if len(controller_list) >= 1:
            with st.container(border=True):
                st.subheader('Controllers:')
                for item in controller_list:
                    st.markdown(item)
        if len(handheld_list) >= 1:
            with st.container(border=True):
                st.subheader('Handhelds:')
                for item in handheld_list:
                    st.markdown(item)
        if len(hose_list) >= 1:
            with st.container(border=True):
                st.subheader('Hoses:')
                for item in hose_list:
                    st.markdown(item)
        if len(fittings_accessories_list) >= 1:
            with st.container(border=True):
                st.subheader('Fittings & Accessories:')
                for item in fittings_accessories_list:
                    st.markdown(item)
        if len(misc_list) >= 1:
            with st.container(border=True):
                st.subheader('Misc:')
                for item in misc_list:
                    st.markdown(item)
        if len(magic_list):
            with st.container(border=True):
                st.subheader('Magic FX:')
                for item in magic_list:
                    st.markdown(item)

    


    
def sort_top_20(dict, number):

    leaderboard_list = []
    
    for key, value in dict.items():
        if value >= 2000:
            leaderboard_list.append((key, value))

    sorted_leaderboard = sorted(leaderboard_list, key=lambda x: x[1], reverse=True)

    return sorted_leaderboard[:number]


if task_choice == 'Leaderboards':

    colx, coly, colz = st.columns([.15, .7, .15])
    coly.header('Customer Leaderboards')
    coly.subheader('')
    #spend_year = st.selectbox('Choose Year', 
                             #['2024', '2023'])
    with coly:
        ranking_number = st.selectbox('Choose Leaderboard Length',
                                 [5, 10, 15, 20, 25, 50])
    
    cust_spend_dict_2023 = {}
    cust_spend_dict_2024 = {}
    cust_spend_dict_2025 = {}
    
    
    for cust in unique_customer_list:
        cust_spend_dict_2023[cust] = 0
        cust_spend_dict_2024[cust] = 0
        cust_spend_dict_2025[cust] = 0
    
    idx = 0
    
    for customer in df.customer:

        if df.iloc[idx].ordered_year == '2023':
            cust_spend_dict_2023[customer] += float(df.iloc[idx].total_line_item_spend)
        elif df.iloc[idx].ordered_year == '2024':
            cust_spend_dict_2024[customer] += float(df.iloc[idx].total_line_item_spend)
        elif df.iloc[idx].ordered_year == '2025':
            cust_spend_dict_2025[customer] += float(df.iloc[idx].total_line_item_spend)
        
        idx += 1

    result25 = sort_top_20(cust_spend_dict_2025, ranking_number)
    result24 = sort_top_20(cust_spend_dict_2024, ranking_number)
    result23 = sort_top_20(cust_spend_dict_2023, ranking_number)

    with coly:
        
        col1, col2, col3 = st.columns(3)

        col1.subheader('2025')
        col2.subheader('2024')
        col3.subheader('2023')
        
        rank = 1    
        for leader in result23:
            #st.subheader(str(rank) + ')  ' + leader[0] + ': ${:,.2f}'.format(leader[1]))
            col3.metric('**${:,.2f}**'.format(leader[1]), '{}) {}'.format(rank, leader[0]), '0%')
            #col2.markdown('**{}) {}  \n  \t${:,.2f}**'.format(rank, leader[0], leader[1]))
            
            rank += 1
            
        rank = 1
        for leader in result24:
            #st.subheader(str(rank) + ')  ' + leader[0] + ': ${:,.2f}'.format(leader[1]))
            col2.metric('**${:,.2f}**'.format(leader[1]), '{}) {}'.format(rank, leader[0]), percent_of_change(cust_spend_dict_2023[leader[0]], cust_spend_dict_2024[leader[0]]))
        
            rank += 1

        rank = 1
        for leader in result25:
            #st.subheader(str(rank) + ')  ' + leader[0] + ': ${:,.2f}'.format(leader[1]))
            col1.metric('**${:,.2f}**'.format(leader[1]), '{}) {}'.format(rank, leader[0]), percent_of_change(cust_spend_dict_2024[leader[0]], cust_spend_dict_2025[leader[0]]))
        
            rank += 1
        
        style_metric_cards()
    


  






















