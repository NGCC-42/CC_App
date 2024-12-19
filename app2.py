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

### SET WEB APP CONFIGURATIONS
st.set_page_config(page_title='Club Cannon Database', 
		   page_icon='club-cannon-icon-black.png',
                   layout='centered',
		   initial_sidebar_state='collapsed')

### SET HEADER IMAGE
#image = 'club-cannon-logo-bbb.png'
st.image('logo.png', use_column_width=True)

st.divider()


### LOAD FILES
sod_ss = 'SOD 12.19.24.xlsx'

hsd_ss = 'HSD 11.8.24.xlsx'

quote_ss = 'Quote Report 10.23.24.xlsx'

sales_sum_csv = 'Total Summary-2022 - Present.csv'

shipstat_ss_24 = '2024 SR 11.01.24.xlsx'
shipstat_ss_23 = '2023 SR.xlsx'

prod_sales = 'Product Sales Data.xlsx'

wholesale_cust = 'wholesale_customers.xlsx'

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

df_quotes = create_dataframe(quote_ss)

df_shipstat_24 = create_dataframe(shipstat_ss_24)

df_shipstat_23 = create_dataframe(shipstat_ss_23)

df_hsd = create_dataframe(hsd_ss)

df_wholesale = create_dataframe(wholesale_cust)

wholesale_list = []
for ws in df_wholesale.name:
    wholesale_list.append(ws)

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

    return df

df = fix_names(df)

### CREATE A LIST OF UNIQUE CUSTOMERS ###
unique_customer_list = df.customer.unique().tolist()

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



df_acc_2024 = gen_product_df_from_excel(prod_sales, acc_2024, cols='a:m')

df_cntl_2024 = gen_product_df_from_excel(prod_sales, cntl_2024, cols='a:m')

df_jet_2024 = gen_product_df_from_excel(prod_sales, jet_2024, cols='a:m')

df_hh_2024 = gen_product_df_from_excel(prod_sales, hh_2024, cols='a:m')

df_hose_2024 = gen_product_df_from_excel(prod_sales, hose_2024, cols='a:m')

df_acc_2023 = gen_product_df_from_excel(prod_sales, acc_2023, cols='a:m')

df_cntl_2023 = gen_product_df_from_excel(prod_sales, cntl_2023, cols='a:m')

df_jet_2023 = gen_product_df_from_excel(prod_sales, jet_2023, cols='a:m')

df_hh_2023 = gen_product_df_from_excel(prod_sales, hh_2023, cols='a:m')

df_hose_2023 = gen_product_df_from_excel(prod_sales, hose_2023, cols='a:m')

### READ IN SALES SUMMARY CSV ###
@st.cache_data
def create_dataframe_csv(file):
	df = pd.read_csv(file, 
					usecols=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
	return df

df_csv = create_dataframe_csv(sales_sum_csv)

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


### SEPARATE SALES AND REVENUE ###

df_jet2023_unt = clean_df_std(df_jet_2023, 0, 4)
df_jet2023_rev = clean_df_std(df_jet_2023, 13, 17)
df_jet2023_prof = clean_df_prof(df_jet_2023, 20, 24)

df_cntl23_unt = clean_df_std(df_cntl_2023, 0, 3)
df_cntl23_rev = clean_df_std(df_cntl_2023, 11, 14)
df_cntl23_prof = clean_df_prof(df_cntl_2023, 17, 20)

df_h23_unt = clean_df_std(df_hose_2023, 0, 22)
df_h23_rev = clean_df_std(df_hose_2023, 48, 70)

df_ac23_unt = clean_df_std(df_acc_2023, 0, 30)
df_ac23_rev = clean_df_std(df_acc_2023, 58, 85)

df_hh23_unt = clean_df_std(df_hh_2023, 0, 4)
df_hh23_rev = clean_df_std(df_hh_2023, 13, 17)

df_jet2024_unt = clean_df_std(df_jet_2024, 0, 4)
df_jet2024_rev = clean_df_std(df_jet_2024, 13, 17)
df_jet2024_prof = clean_df_prof(df_jet_2024, 20, 24)

df_cntl24_unt = clean_df_std(df_cntl_2024, 0, 3)
df_cntl24_rev = clean_df_std(df_cntl_2024, 11, 14)
df_cntl24_prof = clean_df_prof(df_cntl_2024, 17, 20)
                                        
df_h24_unt = clean_df_std(df_hose_2024, 0, 22)
df_h24_rev = clean_df_std(df_hose_2024, 48, 70)

df_ac24_unt = clean_df_std(df_acc_2024, 0, 30)
df_ac24_rev = clean_df_std(df_acc_2024, 59, 86)

df_hh24_unt = clean_df_std(df_hh_2024, 0, 4)
df_hh24_rev = clean_df_std(df_hh_2024, 13, 17)


### CREATE LISTS OF CATEGORIES FROM DATAFRAME ###

@st.cache_data
def create_product_list(df):
	prod_list = df['Product'].unique().tolist()
	return prod_list

jets = create_product_list(df_jet2023_unt)
controllers = create_product_list(df_cntl23_unt)
hoses = create_product_list(df_h23_unt)
acc = create_product_list(df_ac23_unt)
hh = create_product_list(df_hh23_unt)


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


### MAKE DICTIONARIES OF PRODUCT SALES FOR CHARTING ###

#jet_dict_2023 = {'Pro Jet': 0,
#                'Quad Jet': 0,
#               'Micro Jet': 0,
#               'Cryo Clamp': 0}
#jet_dict_2024 = {'Pro Jet': 0,
#                'Quad Jet': 0,
#                'Micro Jet': 0,
#                'Cryo Clamp': 0}
#control_dict_2023 = {'The Button': 0,
#                     'Shostarter': 0,
#                     'Shomaster': 0}
#control_dict_2024 = {'The Button': 0,
#                     'Shostarter': 0,
#                     'Shomaster': 0}
#handheld_dict_2023 = {'8FT - No Case': 0,
#                     '8FT - Travel Case': 0,
#                     '15FT - No Case': 0,
#                     '15FT - Travel Case': 0}
#handheld_dict_2024 = {'8FT - No Case': 0,
#                     '8FT - Travel Case': 0,
#                     '15FT - No Case': 0,
#                     '15FT - Travel Case': 0}

#idx = 0
#for line_item in df.line_item:
#    if line_item[:6] == 'CC-PRO':
#        if df.iloc[idx].ordered_year == '2023':
#            jet_dict_2023['Pro Jet'] += df.iloc[idx].quantity
#        elif df.iloc[idx].ordered_year == '2024':
#            jet_dict_2024['Pro Jet'] += df.iloc[idx].quantity
#        else:
#            pass
#    idx += 1





### GENERATE SIDEBAR MENU ###
task_select = ''
#task_choice = ''
with st.sidebar:
    task_choice = st.radio('**Select Task**', options=['Dashboard', 'Customer Details', 'Product Sales Reports', 'Shipping Reports', 'Quote Reports', 'Leaderboards'])


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


### TESTING ###

bom_cost_jet = {'Pro Jet': 290.86, 'Micro Jet': 243.57, 'Quad Jet': 630.43, 'Quad Jet WP': 651.80, 'Cryo Clamp': 166.05}
bom_cost_control = {'The Button': 141.07, 'ShoStarter': 339.42, 'ShoMaster': 667.12}
bom_cost_hh = {'8FT NC': 143.62, '8FT TC': 219.06, '15FT NC': 153.84, '15FT TC': 231.01}
bom_cost_hose = {'2FT MFD': 20.08, '3.5FT MFD': 22.50, '5FT MFD': 24.25, '5FT STD': 31.94, '5FT DSY': 31.84, '5FT EXT': 33.24, '8FT STD': 32.42, '8FT DSY': 34.52, '8FT EXT': 34.82, '15FT STD': 43.55, '15FT DSY': 46.47, '15FT EXT': 46.77, '25FT STD': 59.22, '25FT DSY': 61.87, '25FT EXT': 62.17, '35FT STD': 79.22, '35FT DSY': 81.32, '35FT EXT': 81.62, '50FT STD': 103.57, '50FT EXT': 105.97, '100FT STD': 183.39}
bom_cost_acc = {'CC-AC-CCL': 29.17, 'CC-AC-CTS': 6.70, 'CC-F-DCHA': 7.15, 'CC-F-HEA': 6.86, 'CC-AC-RAA': 11.94, 'CC-AC-4PM': 48.12, 'CC-F-MFDCGAJIC': 7.83, 'CC-AC-CGAJIC-SET': 5.16, 'CC-AC-CTC-20': 10.92, 'CC-AC-CTC-50': 19.36, 'CC-AC-TC': 89.46, 'CC-VV-KIT': 29.28, 
                'CC-RC-2430': 847, 'CC-AC-LA2': 248.10}

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

	
### FOR DASHBOARD ###  
@st.cache_data
def get_monthly_sales_v2(df, year):

    unique_sales_orders = []

    sales_dict = {'January': [[0, 0], [0, 0]], 'February': [[0, 0], [0, 0]], 'March': [[0, 0], [0, 0]], 'April': [[0, 0], [0, 0]], 'May': [[0, 0], [0, 0]], 'June': [[0, 0], [0, 0]], 'July': [[0, 0], [0, 0]], 'August': [[0, 0], [0, 0]], 'September': [[0, 0], [0, 0]], 'October': [[0, 0], [0, 0]], 'November': [[0, 0], [0, 0]], 'December': [[0, 0], [0, 0]]}

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
                if sale not in unique_sales_orders:
                    sales_dict[month][1][1] += 1
                    unique_sales_orders.append(sale)

        idx += 1
    
    return sales_dict
	
@st.cache_data
def calc_monthly_totals_v2(sales_dict, months=['All']):

    total_sales = 0
    total_web = 0
    total_fulcrum = 0
    num_months = 0
    
    for month, sales in sales_dict.items():
        if months == ['All']:
            total_sales += (sales[0][0] + sales[1][0])
            total_web += sales[0][0]
            total_fulcrum += sales[1][0]
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
                        
    avg_month = total_sales / num_months                
    total_web_perc = percent_of_sales(total_web, total_fulcrum)
    total_fulcrum_perc = percent_of_sales(total_fulcrum, total_web)
    
    return total_sales, total_web_perc, total_fulcrum_perc, avg_month

### FUNCTIONS FOR PLOTTING CHARTS ###
def format_for_chart_ms(dict):
	
	temp_dict = {'Months': months_x,
				'Total Sales': []}
	
	for month, sales in dict.items():
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
def display_month_data_x(sales_dict1, sales_dict2=None):

    dBoard1 = st.columns(3)
    dBoard2 = st.columns(3)
    dBoard3 = st.columns(3)
    dBoard4 = st.columns(3)
    idx = 0
    idx1 = 0
    idx2 = 0
    idx3 = 0
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
	

def display_metrics(sales_dict1, sales_dict2=None, month='All', wvr1=None, wvr2=None):


    if sales_dict2 == None:
        
        data = extract_transaction_data(sales_dict1)
        total_sales, total_web_perc, total_fulcrum_perc, avg_month = calc_monthly_totals_v2(sales_dict1)
        
        db1, db2, db3 = st.columns(3)
        
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
        
    
    elif month == 'All':

        total_sales1, total_web_perc1, total_fulcrum_perc1, avg_month1 = calc_monthly_totals_v2(sales_dict1)
        total_sales2, total_web_perc2, total_fulcrum_perc2, avg_month2 = calc_monthly_totals_v2(sales_dict2)

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

        db1, db2, db3 = st.columns(3)      
        
        if wvr2 == None:

            db1.metric('**Website Sales**', '${:,}'.format(int(data1[3])), web_sales)
            db1.metric('**Website Transactions**', '{:,}'.format(data1[6]), web_trans)
            db1.metric('**Website Average Sale**', '${:,}'.format(int(data1[0])), web_avg_sale)
            db1.metric('**Retail Revenue**', '${:,}'.format(int(retail_sales1)), '')
        
            db2.metric('**Total Sales**', '${:,}'.format(int(data1[5])), var)
            db2.metric('**Monthly Average**', '${:,}'.format(int(avg_month1)), avg_per_month)
            db2.metric('**Total Transactions**', '{:,}'.format(data1[8]), transaction_ct)
            
            db3.metric('**Fulcrum Sales**', '${:,}'.format(int(data1[4])), fulcrum_sales)
            db3.metric('**Fulcrum Transactions**', '{:,}'.format(data1[7]), fulcrum_trans)
            db3.metric('**Fulcrum Average Sale**', '${:,}'.format(int(data1[1])), fulcrum_avg_sale)
            db3.metric('**Wholesale Revenue**', '${:,}'.format(int(wholesale_sales1)), '')

            style_metric_cards()

        else:

            wholesale_sales2, retail_sales2 = wholesale_retail_totals(wvr2)
            wholesale_delta = percent_of_change(wholesale_sales2, wholesale_sales1)
            retail_delta = percent_of_change(retail_sales2, retail_sales1)
        
            db1.metric('**Website Sales**', '${:,}'.format(int(data1[3])), web_sales)
            db1.metric('**Website Transactions**', '{:,}'.format(data1[6]), web_trans)
            db1.metric('**Website Average Sale**', '${:,}'.format(int(data1[0])), web_avg_sale)
            db1.metric('**Retail Revenue**', '${:,}'.format(int(retail_sales1)), retail_delta)
        
            db2.metric('**Total Sales**', '${:,}'.format(int(data1[5])), var)
            db2.metric('**Monthly Average**', '${:,}'.format(int(avg_month1)), avg_per_month)
            db2.metric('**Total Transactions**', '{:,}'.format(data1[8]), transaction_ct)
            
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
        

        db1, db2, db3 = st.columns(3)

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


def beginning_of_year(dt: datetime) -> datetime:
    return datetime(dt.year, 1, 1)



    
today = datetime.now()
#today = datetime(2024, 3, 5)
one_year_ago = today - timedelta(days=365)
two_years_ago = today - timedelta(days=730)
three_years_ago = today - timedelta(days=1095)



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
                td_22[0] += df.iloc[idx].total_line_item_spend
            elif one_year_ago.date() >= order_date >= beginning_of_year(one_year_ago).date():
                td_23[0] += df.iloc[idx].total_line_item_spend
            elif today.date() >= order_date >= beginning_of_year(today).date():
                td_24[0] += df.iloc[idx].total_line_item_spend
            elif order_date.year == 2025:
                td_25[0] += df.iloc[idx].total_line_item_spend   
        else:
            if two_years_ago.date() >= order_date >= beginning_of_year(two_years_ago).date():
                td_22[1] += df.iloc[idx].total_line_item_spend
            elif one_year_ago.date() >= order_date >= beginning_of_year(one_year_ago).date():
                td_23[1] += df.iloc[idx].total_line_item_spend
            elif today.date() >= order_date >= beginning_of_year(today).date():
                td_24[1] += df.iloc[idx].total_line_item_spend
            elif order_date.year == 2025:
                td_25[1] += df.iloc[idx].total_line_item_spend            

        idx += 1
        
    return td_22, td_23, td_24, td_25

# MAKE TO-DATE REV GLOBAL FOR USE WITH PRODUCTS

td_22, td_23, td_24, td_25 = to_date_revenue()

td_22_tot = td_22[0] + td_22[1]
td_23_tot = td_23[0] + td_23[1]
td_24_tot = td_24[0] + td_24[1]
td_25_tot = td_25[0] + td_25[1]



if task_choice == 'Dashboard':


    ### WHOLESALE VS RETAIL MONTHLY TOTALS
    
    wvr_23_months = get_monthly_sales_wvr(df, 2023)
    wvr_24_months = get_monthly_sales_wvr(df, 2024)
    wvr_23_totals = wholesale_retail_totals(wvr_23_months)
    wvr_24_totals = wholesale_retail_totals(wvr_24_months)    
    
    ### COMPILE DATA FOR SALES REPORTS ###
    total_22 = 1483458.64
    avg_22 = 147581.12
    trans_22 = 1266
    trans_avg_22 = 126.6
    sales_dict_22 = {'January': [[0, 1], [0, 1]], 
                     'February': [[0, 1], [7647.42, 25]], 
                     'March': [[48547.29, 80], [48457.28, 30]], 
                     'April': [[69081.04, 86], [69081.05, 30]], 
                     'May': [[64976.18, 72], [64976.18, 40]], 
                     'June': [[88817.15, 90], [88817.15, 51]], 
                     'July': [[104508.24, 86], [104508.24, 30]], 
                     'August': [[74166.78, 94], [74166.78, 50]], 
                     'September': [[68018.74, 99], [68018.74, 50]], 
                     'October': [[86874.13, 126], [86874.13, 40]], 
                     'November': [[57760.81, 77], [57760.82, 30]], 
                     'December': [[75155.19, 64], [75155.20, 30]]}
    
    sales_dict_23 = get_monthly_sales_v2(df, 2023)
    #transaction_data_23 = extract_transaction_data(sales_dict_23)
    total_23, web_23, ful_23, avg_23 = calc_monthly_totals_v2(sales_dict_23)
    
    sales_dict_24 = get_monthly_sales_v2(df, 2024)
    #transaction_data_24 = extract_transaction_data(sales_dict_24)
    total_24, web_24, ful_24, avg_24 = calc_monthly_totals_v2(sales_dict_24)

    ### SALES CHANNEL BREAKDOWN ###
    web_avg_perc = (web_23 + web_24)/2
    ful_avg_perc = (ful_23 + ful_24)/2

    year_select = ui.tabs(options=[2024, 2023, 2022], default_value=2024, key='Year')

    
    ### DISPLAY SALES METRICS ###

    if year_select == 2024:

        display_metrics(sales_dict_24, sales_dict_23, wvr1=wvr_24_months, wvr2=wvr_23_months)
        
        st.header('')
        plot_bar_chart_ms(format_for_chart_ms(sales_dict_24))
        
        st.divider()
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


        
    if year_select == 2023:

        display_metrics(sales_dict_23, sales_dict_22, wvr1=wvr_23_months)

        st.header('')
        plot_bar_chart_ms(format_for_chart_ms(sales_dict_23))
        
        st.divider()
        months[0] = 'Overview'
        focus = st.selectbox('', options=months, key='Focus23')
        
        st.divider()

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

        display_metrics(sales_dict_22)

        st.header('')
        plot_bar_chart_ms(format_for_chart_ms(sales_dict_22))

        st.divider()

        display_month_data_x(sales_dict_22)


### REVISED PRODUCT REPORTS

@st.cache_data
def extract_handheld_data(df):

    dict_23 = {}
    dict_24 = {}
    hose_count_23 = {}
    hose_count_24 = {}
    
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
        
        hose_count_23[month] = [0,0]
        hose_count_24[month] = [0,0]
    
    idx = 0
    for line in df.line_item:
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
    
    return dict_23, dict_24, hose_count_23, hose_count_24



@st.cache_data
def extract_hose_data(df):

    dict_23 = {}
    dict_24 = {}

    # CREATE DATA DICTS 
    for month in months_x:
        dict_23[month] = {'2FT MFD': [0,0], '3.5FT MFD': [0,0], '5FT MFD': [0,0], '5FT STD': [0,0], '5FT DSY': [0,0], '5FT EXT': [0,0], '8FT STD': [0,0], '8FT DSY': [0,0], '8FT EXT': [0,0], '15FT STD': [0,0], '15FT DSY': [0,0], '15FT EXT': [0,0], '25FT STD': [0,0], '25FT DSY': [0,0], '25FT EXT': [0,0], '35FT STD': [0,0], '35FT DSY': [0,0], '35FT EXT': [0,0], '50FT STD': [0,0], '50FT EXT': [0,0], '100FT STD': [0,0], 'CUSTOM': [0,0]}
        dict_24[month] = {'2FT MFD': [0,0], '3.5FT MFD': [0,0], '5FT MFD': [0,0], '5FT STD': [0,0], '5FT DSY': [0,0], '5FT EXT': [0,0], '8FT STD': [0,0], '8FT DSY': [0,0], '8FT EXT': [0,0], '15FT STD': [0,0], '15FT DSY': [0,0], '15FT EXT': [0,0], '25FT STD': [0,0], '25FT DSY': [0,0], '25FT EXT': [0,0], '35FT STD': [0,0], '35FT DSY': [0,0], '35FT EXT': [0,0], '50FT STD': [0,0], '50FT EXT': [0,0], '100FT STD': [0,0], 'CUSTOM': [0,0]}
    
    idx = 0
    for line in df.line_item:
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
    
    return dict_23, dict_24


@st.cache_data
def extract_acc_data(df):

    dict_23 = {}
    dict_24 = {}

    # CREATE DATA DICTS 
    for month in months_x:
        dict_23[month] = {'CC-AC-CCL': [0,0], 'CC-AC-CTS': [0,0], 'CC-F-DCHA': [0,0], 'CC-F-HEA': [0,0], 'CC-AC-RAA': [0,0], 'CC-AC-4PM': [0,0], 'CC-F-MFDCGAJIC': [0,0], ' CC-AC-CGAJIC-SET': [0,0], 'CC-CTC-20': [0,0], 'CC-CTC-50': [0,0], 'CC-AC-TC': [0,0], 'CC-VV-KIT': [0,0], 
                'CC-RC-2430': [0,0,0,0,0], 'CC-AC-LA2': [0,0]}
        dict_24[month] = {'CC-AC-CCL': [0,0], 'CC-AC-CTS': [0,0], 'CC-F-DCHA': [0,0], 'CC-F-HEA': [0,0], 'CC-AC-RAA': [0,0], 'CC-AC-4PM': [0,0], 'CC-F-MFDCGAJIC': [0,0], ' CC-AC-CGAJIC-SET': [0,0], 'CC-CTC-20': [0,0], 'CC-CTC-50': [0,0], 'CC-AC-TC': [0,0], 'CC-VV-KIT': [0,0], 
                'CC-RC-2430': [0,0,0,0,0], 'CC-AC-LA2': [0,0]}
    
    idx = 0
    for line in df.line_item:
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
    
    return dict_23, dict_24



@st.cache_data
def extract_control_data(df):

    dict_23 = {}
    dict_24 = {}

    # CREATE DATA DICTS 
    for month in months_x:
        dict_23[month] = {'The Button': [0,0,0],
                     'Shostarter': [0,0,0],
                     'Shomaster': [0,0,0]}
        dict_24[month] = {'The Button': [0,0,0],
                     'Shostarter': [0,0,0],
                     'Shomaster': [0,0,0]}
    
    idx = 0
    for line in df.line_item:
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
    
    return dict_23, dict_24
    



@st.cache_data
def extract_jet_data(df):

    dict_23 = {}
    dict_24 = {}

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
    
    idx = 0
    for line in df.line_item:
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
    
    return dict_23, dict_24
    
   
@st.cache_data
def collect_product_data(df, prod='All', years=[2023, 2024]):


    jet23, jet24 = extract_jet_data(df)
    control23, control24 = extract_control_data(df)
    handheld23, handheld24, hh_hose_count_23, hh_hose_count_24 = extract_handheld_data(df)
    hose23, hose24 = extract_hose_data(df)
    acc23, acc24 = extract_acc_data(df)

    # INCLUDE HANDHELD HOSES IN COUNTS
    for key, val in hose23.items():
        hose23[key]['8FT STD'][0] += hh_hose_count_23[key][0]
        hose23[key]['15FT STD'][0] += hh_hose_count_23[key][1]
    for key, val in hose24.items():
        hose24[key]['8FT STD'][0] += hh_hose_count_24[key][0]
        hose24[key]['15FT STD'][0] += hh_hose_count_24[key][1]        

    return jet23, jet24, control23, control24, handheld23, handheld24, hose23, hose24, acc23, acc24

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
    

bom_cost_jet = {'Pro Jet': 290.86, 'Micro Jet': 243.57, 'Quad Jet': 630.43, 'Quad Jet WP': 651.80, 'Cryo Clamp': 166.05}
bom_cost_control = {'The Button': 141.07, 'Shostarter': 339.42, 'Shomaster': 667.12}
bom_cost_hh = {'8FT - No Case': 143.62, '8FT - Travel Case': 219.06, '15FT - No Case': 153.84, '15FT - Travel Case': 231.01}
bom_cost_hose = {'2FT MFD': 20.08, '3.5FT MFD': 22.50, '5FT MFD': 24.25, '5FT STD': 31.94, '5FT DSY': 31.84, '5FT EXT': 33.24, '8FT STD': 32.42, '8FT DSY': 34.52, '8FT EXT': 34.82, '15FT STD': 43.55, '15FT DSY': 46.47, '15FT EXT': 46.77, '25FT STD': 59.22, '25FT DSY': 61.87, '25FT EXT': 62.17, '35FT STD': 79.22, '35FT DSY': 81.32, '35FT EXT': 81.62, '50FT STD': 103.57, '50FT EXT': 105.97, '100FT STD': 183.39}
bom_cost_acc = {'CC-AC-CCL': 29.17, 'CC-AC-CTS': 6.70, 'CC-F-DCHA': 7.15, 'CC-F-HEA': 6.86, 'CC-AC-RAA': 11.94, 'CC-AC-4PM': 48.12, 'CC-F-MFDCGAJIC': 7.83, ' CC-AC-CGAJIC-SET': 5.16, 'CC-CTC-20': 10.92, 'CC-CTC-50': 19.36, 'CC-AC-TC': 89.46, 'CC-VV-KIT': 29.28, 
                'CC-RC-2430': 847, 'CC-AC-LA2': 248.10}

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


def display_hose_data(hose_details1, hose_details2):

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('2024')
        idx = 0
        for group in hose_details1[:7]:
            group_units = 0
            group_rev = 0
            with st.container(border=True):
                for hose, vals in group.items():
                    group_units += vals[0]
                    group_rev += vals[1]
                    ui.metric_card(title=hose, content='{} units'.format(vals[0]), description='${:,.2f} in revenue'.format(vals[1]))
                if idx == 0:
                    st.markdown('**Manifold Totals: {} - (${:,.2f})**'.format(group_units, group_rev))
                else:
                    st.markdown('**{} Totals: {} - (${:,.2f})**'.format(hose[:4], group_units, group_rev))
                            
            idx += 1
        ui.metric_card(title='100FT STD', content='{} units'.format(hose_details1[7][0]), description='${:,.2f} in revenue'.format(hose_details1[7][1]), key='2024')
        
    with col2:
        st.subheader('2023')
        idx2 = 0
        for group2 in hose_details2[:7]:
            group2_units = 0
            group2_rev = 0
            with st.container(border=True):
                for hose2, vals2 in group2.items():
                    group2_units += vals2[0]
                    group2_rev += vals2[1]
                    ui.metric_card(title=hose2, content='{} units'.format(vals2[0]), description='${:,.2f} in revenue'.format(vals2[1]))
                if idx2 == 0:
                    st.markdown('**Manifold Totals: {} - (${:,.2f})**'.format(group2_units, group2_rev))
                else:
                    st.markdown('**{} Totals: {} - (${:,.2f})**'.format(hose2[:4], group2_units, group2_rev))
            idx2 += 1
        ui.metric_card(title='100FT STD', content='{} units'.format(hose_details2[7][0]), description='${:,.2f} in revenue'.format(hose_details2[7][1]), key='2023')
        
    return None

def calculate_product_metrics(annual_product_totals, prod_select, key, bom_dict):

    jet_list = ['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp']
    control_list = ['The Button', 'Shostarter', 'Shomaster']
    no_prior_list = [0,2,4,6,8]

    prod_profit = (annual_product_totals[key][prod_select][1]) - (annual_product_totals[key][prod_select][0] * bom_dict[prod_select])
    profit_per_unit = prod_profit / annual_product_totals[key][prod_select][0]
    avg_price = annual_product_totals[key][prod_select][1] / annual_product_totals[key][prod_select][0]
    
    if key not in no_prior_list:
        avg_price_last = annual_product_totals[key-1][prod_select][1] / annual_product_totals[key-1][prod_select][0]
        prod_profit_last = (annual_product_totals[key-1][prod_select][1]) - (annual_product_totals[key-1][prod_select][0] * bom_dict[prod_select])

    if (prod_select in jet_list or prod_select in control_list) and (key in [0, 1, 2, 3]):
        wholesale_sales = annual_product_totals[key][prod_select][2]
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
            
    return prod_cnt_23, prod_cnt_24, prod_cnt_25



if task_choice == 'Product Sales Reports':

    st.header('Product Sales')
    #st.subheader('')

    # PULL ALL PRODUCT SALES BY MONTH (DICTIONARIES)
    jet23, jet24, control23, control24, handheld23, handheld24, hose23, hose24, acc23, acc24 = collect_product_data(df)
    hose_detail24 = organize_hose_data(hose24)
    hose_detail23 = organize_hose_data(hose23)

    
    # CALCULATE ANNUAL PRODUCT TOTALS
    annual_product_totals = product_annual_totals([jet23, jet24, control23, control24, handheld23, handheld24, hose23, hose24, acc23, acc24])

    # NAVIGATION TABS
    prod_cat = ui.tabs(options=['Jets', 'Controllers', 'Handhelds', 'Hoses', 'Accessories'], default_value='Jets', key='Product Categories')
    year = ui.tabs(options=[2024, 2023], default_value=2024, key='Products Year Select')
    st.divider()
    
    if prod_cat == 'Jets':
        if year == 2024:
            
            total_jet_rev = annual_product_totals[1]['Pro Jet'][1] + annual_product_totals[1]['Quad Jet'][1] + annual_product_totals[1]['Micro Jet'][1] + annual_product_totals[1]['Cryo Clamp'][1]
            
            col1, col2, col3, col4 = st.columns(4)

            col1.subheader('Pro Jet')
            col1.metric('{:.1f}% of Total Rev'.format((annual_product_totals[1]['Pro Jet'][1] / td_24_tot) * 100), '{}'.format(annual_product_totals[1]['Pro Jet'][0]), annual_product_totals[1]['Pro Jet'][0] - annual_product_totals[0]['Pro Jet'][0])
            #col1.metric('', '${:,}'.format(annual_product_totals[1]['Pro Jet'][1]), percent_of_change(annual_product_totals[0]['Pro Jet'][0], annual_product_totals[1]['Pro Jet'][0]))
            col2.subheader('Quad Jet')
            col2.metric('{:.1f}% of Total Rev'.format((annual_product_totals[1]['Quad Jet'][1] / td_24_tot) * 100), '{}'.format(annual_product_totals[1]['Quad Jet'][0]), annual_product_totals[1]['Quad Jet'][0] - annual_product_totals[0]['Quad Jet'][0])
            #col2.metric('', '${:,}'.format(annual_product_totals[1]['Quad Jet'][1]), percent_of_change(annual_product_totals[0]['Quad Jet'][0], annual_product_totals[1]['Quad Jet'][0]))
            col3.subheader('Micro Jet')
            col3.metric('{:.1f}% of Total Rev'.format((annual_product_totals[1]['Micro Jet'][1] / td_24_tot) * 100), '{}'.format(annual_product_totals[1]['Micro Jet'][0]), annual_product_totals[1]['Micro Jet'][0] - annual_product_totals[0]['Micro Jet'][0])
            #col3.metric('', '${:,}'.format(annual_product_totals[1]['Micro Jet'][1]), percent_of_change(annual_product_totals[0]['Micro Jet'][0], annual_product_totals[1]['Micro Jet'][0]))
            col4.subheader('Cryo Clamp')
            col4.metric('{:.1f}% of Total Rev'.format((annual_product_totals[1]['Cryo Clamp'][1] / td_24_tot) * 100), '{}'.format(annual_product_totals[1]['Cryo Clamp'][0]), annual_product_totals[1]['Cryo Clamp'][0] - annual_product_totals[0]['Cryo Clamp'][0])
            #col4.metric('', '${:,}'.format(annual_product_totals[1]['Cryo Clamp'][1]), percent_of_change(annual_product_totals[0]['Cryo Clamp'][0], annual_product_totals[1]['Cryo Clamp'][0]))
            style_metric_cards()
            st.divider()
            display_pie_chart_comp(annual_product_totals[1])
            #fig1 = px.line(format_for_line_graph(jet24, 'Pro Jet'), x='Months', y='Units Sold')
            #fig1.show()
            st.divider()
            
            prod_select = ui.tabs(options=['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp'], default_value='Pro Jet', key='Jets')
    
    
            ### DISPLAY PRODUCT DETAILS 
            col5, col6, col7 = st.columns(3)

            prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calculate_product_metrics(annual_product_totals, prod_select, 1, bom_cost_jet)
            
            #prod_profit = int((annual_product_totals[1][prod_select][1]) - (annual_product_totals[1][prod_select][0] * bom_cost_jet[prod_select]))
            #prod_profit_last = int((annual_product_totals[0][prod_select][1]) - (annual_product_totals[0][prod_select][0] * bom_cost_jet[prod_select]))
            #avg_price = annual_product_totals[1][prod_select][1] / annual_product_totals[1][prod_select][0]
            #avg_price_last = annual_product_totals[0][prod_select][1] / annual_product_totals[0][prod_select][0]
    
            col5.metric('**Revenue**', '${:,.2f}'.format(annual_product_totals[1][prod_select][1]), percent_of_change(annual_product_totals[0][prod_select][0], annual_product_totals[1][prod_select][0]))
            col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
            col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
            col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
            col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))        
            col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_jet[prod_select]), '')
    
            
            display_month_data_prod(prod_select, jet24, jet23)
            
            
        elif year == 2023:
            
            total_jet_rev = annual_product_totals[0]['Pro Jet'][1] + annual_product_totals[0]['Quad Jet'][1] + annual_product_totals[0]['Micro Jet'][1] + annual_product_totals[0]['Cryo Clamp'][1]
            
            col1, col2, col3, col4 = st.columns(4)
    
            col1.subheader('Pro Jet')
            col1.metric('{:.1f}% of Total Rev'.format((annual_product_totals[0]['Pro Jet'][1] / td_23_tot) * 100), '{}'.format(annual_product_totals[0]['Pro Jet'][0]), '')
            #col1.metric('', '${:,}'.format(annual_product_totals[1]['Pro Jet'][1]), percent_of_change(annual_product_totals[0]['Pro Jet'][0], annual_product_totals[1]['Pro Jet'][0]))
            col2.subheader('Quad Jet')
            col2.metric('{:.1f}% of Total Rev'.format((annual_product_totals[0]['Quad Jet'][1] / td_23_tot) * 100), '{}'.format(annual_product_totals[0]['Quad Jet'][0]), '')
            #col2.metric('', '${:,}'.format(annual_product_totals[1]['Quad Jet'][1]), percent_of_change(annual_product_totals[0]['Quad Jet'][0], annual_product_totals[1]['Quad Jet'][0]))
            col3.subheader('Micro Jet')
            col3.metric('{:.1f}% of Total Rev'.format((annual_product_totals[0]['Micro Jet'][1] / td_23_tot) * 100), '{}'.format(annual_product_totals[0]['Micro Jet'][0]), '')
            #col3.metric('', '${:,}'.format(annual_product_totals[1]['Micro Jet'][1]), percent_of_change(annual_product_totals[0]['Micro Jet'][0], annual_product_totals[1]['Micro Jet'][0]))
            col4.subheader('Cryo Clamp')
            col4.metric('{:.1f}% of Total Rev'.format((annual_product_totals[0]['Cryo Clamp'][1] / td_23_tot) * 100), '{}'.format(annual_product_totals[0]['Cryo Clamp'][0]), '')
            #col4.metric('', '${:,}'.format(annual_product_totals[1]['Cryo Clamp'][1]), percent_of_change(annual_product_totals[0]['Cryo Clamp'][0], annual_product_totals[1]['Cryo Clamp'][0]))
            style_metric_cards()
            st.divider()
            display_pie_chart_comp(annual_product_totals[0])
            st.divider()
            
            prod_select = ui.tabs(options=['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp'], default_value='Pro Jet', key='Jets')
    
    
            ### DISPLAY PRODUCT DETAILS 
            col5, col6, col7 = st.columns(3)
    
            prod_profit, profit_per_unit, avg_price, wholesale_sales, wholesale_percentage = calculate_product_metrics(annual_product_totals, prod_select, 0, bom_cost_jet)
            #prod_profit = (annual_product_totals[0][prod_select][1]) - (annual_product_totals[0][prod_select][0] * bom_cost_jet[prod_select])
            #avg_price = annual_product_totals[0][prod_select][1] / annual_product_totals[0][prod_select][0]
            #profit_per_unit = avg_price - bom_cost_jet[prod_select]

            col5.metric('**Revenue**', '${:,.2f}'.format(annual_product_totals[0][prod_select][1]), '')
            col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
            col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), '')
            col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
            col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), '')        
            col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_jet[prod_select]), '')
    
            
            display_month_data_prod(prod_select, jet23)            
            

    elif prod_cat == 'Controllers':
        if year == 2024:

            total_cntl_rev = annual_product_totals[3]['The Button'][1] + annual_product_totals[3]['Shostarter'][1] + annual_product_totals[3]['Shomaster'][1]
            
            col1, col2, col3 = st.columns(3)
            
            col1.subheader('The Button')
            col1.metric('{:.1f}% of Total Rev'.format((annual_product_totals[3]['The Button'][1] / td_24_tot) * 100), '{}'.format(annual_product_totals[3]['The Button'][0]), annual_product_totals[3]['The Button'][0] - annual_product_totals[2]['The Button'][0])
            col2.subheader('Shostarter')
            col2.metric('{:.1f}% of Total Rev'.format((annual_product_totals[3]['Shostarter'][1] / td_24_tot) * 100), '{}'.format(annual_product_totals[3]['Shostarter'][0]), annual_product_totals[3]['Shostarter'][0] - annual_product_totals[2]['Shostarter'][0])
            col3.subheader('Shomaster')
            col3.metric('{:.1f}% of Total Rev'.format((annual_product_totals[3]['Shomaster'][1] / td_24_tot) * 100), '{}'.format(annual_product_totals[3]['Shomaster'][0]), annual_product_totals[3]['Shomaster'][0] - annual_product_totals[2]['Shomaster'][0])
    
            st.divider()
            display_pie_chart_comp(annual_product_totals[3])
            st.divider()
            
            prod_select = ui.tabs(options=['The Button', 'Shostarter', 'Shomaster'], default_value='The Button', key='Controllers')
    
            ### DISPLAY PRODUCT DETAILS 
            col5, col6, col7 = st.columns(3)

            prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calculate_product_metrics(annual_product_totals, prod_select, 3, bom_cost_control)
    
            #prod_profit = int((annual_product_totals[3][prod_select][1]) - (annual_product_totals[3][prod_select][0] * bom_cost_control[prod_select]))
            #prod_profit_last = int((annual_product_totals[2][prod_select][1]) - (annual_product_totals[2][prod_select][0] * bom_cost_control[prod_select]))
            #avg_price = annual_product_totals[3][prod_select][1] / annual_product_totals[3][prod_select][0]
            #avg_price_last = annual_product_totals[2][prod_select][1] / annual_product_totals[2][prod_select][0]
            
            col5.metric('**Revenue**', '${:,.2f}'.format(annual_product_totals[3][prod_select][1]), percent_of_change(annual_product_totals[2][prod_select][0], annual_product_totals[3][prod_select][0]))
            col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
            col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
            col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
            col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
            col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_control[prod_select]), '')

            style_metric_cards()
            
            display_month_data_prod(prod_select, control24, control23)

        elif year == 2023:

            total_cntl_rev = annual_product_totals[2]['The Button'][1] + annual_product_totals[2]['Shostarter'][1] + annual_product_totals[2]['Shomaster'][1]
            
            col1, col2, col3 = st.columns(3)
            
            col1.subheader('The Button')
            col1.metric('{:.1f}% of Total Rev'.format((annual_product_totals[2]['The Button'][1] / td_23_tot) * 100), '{}'.format(annual_product_totals[2]['The Button'][0]), '')
            col2.subheader('Shostarter')
            col2.metric('{:.1f}% of Total Rev'.format((annual_product_totals[2]['Shostarter'][1] / td_23_tot) * 100), '{}'.format(annual_product_totals[2]['Shostarter'][0]), '')
            col3.subheader('Shomaster')
            col3.metric('{:.1f}% of Total Rev'.format((annual_product_totals[2]['Shomaster'][1] / td_23_tot) * 100), '{}'.format(annual_product_totals[2]['Shomaster'][0]), '')
    
            st.divider()
            display_pie_chart_comp(annual_product_totals[2])
            st.divider()
            
            prod_select = ui.tabs(options=['The Button', 'Shostarter', 'Shomaster'], default_value='The Button', key='Controllers')
    
            ### DISPLAY PRODUCT DETAILS 
            col5, col6, col7 = st.columns(3)
    
            prod_profit, profit_per_unit, avg_price, wholesale_sales, wholesale_percentage = calculate_product_metrics(annual_product_totals, prod_select, 2, bom_cost_control)
            #prod_profit = (annual_product_totals[2][prod_select][1]) - (annual_product_totals[2][prod_select][0] * bom_cost_control[prod_select])
            #avg_price = annual_product_totals[2][prod_select][1] / annual_product_totals[2][prod_select][0]
            #profit_per_unit = avg_price - bom_cost_control[prod_select]
            
            col5.metric('**Revenue**', '${:,.2f}'.format(annual_product_totals[2][prod_select][1]), '')
            col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
            col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), '')
            col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
            col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), '')
            col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_control[prod_select]), '')

            style_metric_cards()
            
            display_month_data_prod(prod_select, control23)
            

    elif prod_cat == 'Handhelds':
		
        if year == 2024:

            total_hh_rev = annual_product_totals[5]['8FT - No Case'][1] + annual_product_totals[5]['8FT - Travel Case'][1] + annual_product_totals[5]['15FT - No Case'][1] + annual_product_totals[5]['15FT - Travel Case'][1]
            
            col1, col2, col3, col4 = st.columns(4)
    
            col1.subheader('8FT NC')
            col1.metric('{:.1f}% of Total Rev'.format((annual_product_totals[5]['8FT - No Case'][1] / td_24_tot) * 100), '{}'.format(annual_product_totals[5]['8FT - No Case'][0]), '{}'.format(annual_product_totals[5]['8FT - No Case'][0] - annual_product_totals[4]['8FT - No Case'][0]))
            col1.metric('', '${:,}'.format(int(annual_product_totals[5]['8FT - No Case'][1])), percent_of_change(annual_product_totals[4]['8FT - No Case'][1], annual_product_totals[5]['8FT - No Case'][1]))
            col2.subheader('8FT TC')
            col2.metric('{:.1f}% of Total Rev'.format((annual_product_totals[5]['8FT - Travel Case'][1] / td_24_tot) * 100), '{}'.format(annual_product_totals[5]['8FT - Travel Case'][0]),  '{}'.format(annual_product_totals[5]['8FT - Travel Case'][0] - annual_product_totals[4]['8FT - Travel Case'][0]))
            col2.metric('', '${:,}'.format(int(annual_product_totals[5]['8FT - Travel Case'][1])), percent_of_change(annual_product_totals[4]['8FT - Travel Case'][1], annual_product_totals[5]['8FT - Travel Case'][1]))
            col3.subheader('15FT NC')
            col3.metric('{:.1f}% of Total Rev'.format((annual_product_totals[5]['15FT - No Case'][1] / td_24_tot) * 100), '{}'.format(annual_product_totals[5]['15FT - No Case'][0]),  '{}'.format(annual_product_totals[5]['15FT - No Case'][0] - annual_product_totals[4]['15FT - No Case'][0]))
            col3.metric('', '${:,}'.format(int(annual_product_totals[5]['15FT - No Case'][1])), percent_of_change(annual_product_totals[4]['15FT - No Case'][1], annual_product_totals[5]['15FT - No Case'][1]))
            col4.subheader('15FT TC')
            col4.metric('{:.1f}% of Total Rev'.format((annual_product_totals[5]['15FT - Travel Case'][1] / td_24_tot) * 100), '{}'.format(annual_product_totals[5]['15FT - Travel Case'][0]),  '{}'.format(annual_product_totals[5]['15FT - Travel Case'][0] - annual_product_totals[4]['15FT - Travel Case'][0]))
            col4.metric('', '${:,}'.format(int(annual_product_totals[5]['15FT - Travel Case'][1])), percent_of_change(annual_product_totals[4]['15FT - Travel Case'][1], annual_product_totals[5]['15FT - Travel Case'][1]))
        
            st.divider()
            display_pie_chart_comp(annual_product_totals[5])
            st.divider()
    
            prod_select = ui.tabs(options=['8FT - No Case', '8FT - Travel Case', '15FT - No Case', '15FT - Travel Case'], default_value='8FT - No Case', key='Handhelds')
    
            ### DISPLAY PRODUCT DETAILS 
            col5, col6, col7 = st.columns(3)

            prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calculate_product_metrics(annual_product_totals, prod_select, 5, bom_cost_hh)
    
            #prod_profit = int((annual_product_totals[5][prod_select][1]) - (annual_product_totals[5][prod_select][0] * bom_cost_hh[prod_select]))
            #prod_profit_last = int((annual_product_totals[4][prod_select][1]) - (annual_product_totals[4][prod_select][0] * bom_cost_hh[prod_select]))
            #avg_price = annual_product_totals[5][prod_select][1] / annual_product_totals[5][prod_select][0]
            #avg_price_last = annual_product_totals[4][prod_select][1] / annual_product_totals[4][prod_select][0]
            
            col5.metric('**Revenue**', '${:,.2f}'.format(annual_product_totals[5][prod_select][1]), percent_of_change(annual_product_totals[4][prod_select][0], annual_product_totals[5][prod_select][0]))
            col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
            col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
            col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
            col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_hh[prod_select]), '')       

            style_metric_cards()       
            
            display_month_data_prod(prod_select, handheld24, handheld23)
            
        elif year == 2023:

            total_hh_rev = annual_product_totals[5]['8FT - No Case'][1] + annual_product_totals[5]['8FT - Travel Case'][1] + annual_product_totals[5]['15FT - No Case'][1] + annual_product_totals[5]['15FT - Travel Case'][1]
            
            col1, col2, col3, col4 = st.columns(4)
    
            col1.subheader('8FT NC')
            col1.metric('{:.1f}% of Total Rev'.format((annual_product_totals[4]['8FT - No Case'][1] / td_23_tot) * 100), '{}'.format(annual_product_totals[4]['8FT - No Case'][0]), '')
            col1.metric('', '${:,}'.format(int(annual_product_totals[4]['8FT - No Case'][1])), '')
            col2.subheader('8FT TC')
            col2.metric('{:.1f}% of Total Rev'.format((annual_product_totals[4]['8FT - Travel Case'][1] / td_23_tot) * 100), '{}'.format(annual_product_totals[4]['8FT - Travel Case'][0]),  '')
            col2.metric('', '${:,}'.format(int(annual_product_totals[4]['8FT - Travel Case'][1])), '')
            col3.subheader('15FT NC')
            col3.metric('{:.1f}% of Total Rev'.format((annual_product_totals[4]['15FT - No Case'][1] / td_23_tot) * 100), '{}'.format(annual_product_totals[4]['15FT - No Case'][0]),  '')
            col3.metric('', '${:,}'.format(int(annual_product_totals[4]['15FT - No Case'][1])), '')
            col4.subheader('15FT TC')
            col4.metric('{:.1f}% of Total Rev'.format((annual_product_totals[4]['15FT - Travel Case'][1] / td_23_tot) * 100), '{}'.format(annual_product_totals[4]['15FT - Travel Case'][0]),  '')
            col4.metric('', '${:,}'.format(int(annual_product_totals[4]['15FT - Travel Case'][1])), '')
        
            st.divider()
            display_pie_chart_comp(annual_product_totals[5])
            st.divider()
    
            prod_select = ui.tabs(options=['8FT - No Case', '8FT - Travel Case', '15FT - No Case', '15FT - Travel Case'], default_value='8FT - No Case', key='Handhelds')
    
            ### DISPLAY PRODUCT DETAILS 
            col5, col6, col7 = st.columns(3)
    
            prod_profit = (annual_product_totals[4][prod_select][1]) - (annual_product_totals[4][prod_select][0] * bom_cost_hh[prod_select])
            avg_price = annual_product_totals[4][prod_select][1] / annual_product_totals[4][prod_select][0]
            profit_per_unit = avg_price - bom_cost_hh[prod_select]
            
            col5.metric('**Revenue**', '${:,.2f}'.format(annual_product_totals[4][prod_select][1]), '')
            col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
            col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), '')
            col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), '')
            col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_hh[prod_select]), '')             
            
            style_metric_cards()     
            
            display_month_data_prod(prod_select, handheld23)
        
    elif prod_cat == 'Hoses':

        display_hose_data(hose_detail24, hose_detail23)
        
          
    elif prod_cat == 'Accessories':


        col1, col2 = st.columns(2)
        col1.subheader('2024')               
        col2.subheader('2023')
        with col1:
            for item, value in annual_product_totals[-1].items():
                if item == 'CC-RC-2430':
                    ui.metric_card(title='{}'.format(item), content='{} (PJ: {}, LA: {}, QJ: {})'.format(value[0], value[2], value[3], value[4]), description='${:,.2f} in Revenue'.format(value[1]))
                else:
                    ui.metric_card(title='{}'.format(item), content='{}'.format(value[0]), description='${:,.2f} in Revenue'.format(value[1])) 
        with col2:
            for item_last, value_last in annual_product_totals[-2].items():
                if item_last == 'CC-RC-2430':
                    ui.metric_card(title='{}'.format(item_last), content='{} (PJ: {}, LA: {})'.format(value_last[0], value_last[2], value_last[3]), description='${:,.2f} in Revenue'.format(value_last[1]))
                else:
                    ui.metric_card(title='{}'.format(item_last), content='{}'.format(value_last[0]), description='${:,.2f} in Revenue'.format(value_last[1]))

        
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

    for customer in df_quotes.customer:

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

    if len(quote_cust) > 1:
        st.header('')
        st.header('')
        
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


elif task_choice == 'Customer Details':
    

    st.header('Customer Details')
    #text_input = st.text_input('Search Customers')
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
    spend_total = {2023: None, 2024: None}
    spend_total_2023 = 0.0
    spend_total_2024 = 0.0
    sales_order_list = []
    
    idx = 0
    
    for customer in df.customer:
        
        if customer.upper() == text_input.upper():
            #sales_order_list.append(df.iloc[idx].sales_order)
            
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
        
    #st.write(sales_order_list)
    st.header('')
    st.subheader('')
    st.subheader('')
    col3, col4, col5 = st.columns(3)
    

    
    ### DISPLAY PRODUCT PURCHASE SUMMARIES FOR SELECTED CUSTOMER ###
    if len(text_input) > 1:

        ### DISPLAY CUSTOMER SPENDING TRENDS AND TOTALS
        with col3:
            st.metric('2023 Spending', '${:,.2f}'.format(spend_total_2023), '')
    
        with col4:
            st.metric('2024 Spending', '${:,.2f}'.format(spend_total_2024), percent_of_change(spend_total_2023, spend_total_2024))
            
        with col5:
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

    
    ### CREATE LISTS OF CATEGORIES FROM DATAFRAME ###
    
    jets = df_jet2023_unt['Product'].unique().tolist()
    controllers = df_cntl23_unt['Product'].unique().tolist()
    hoses = df_h23_unt['Product'].unique().tolist()
    acc = df_ac23_unt['Product'].unique().tolist()
    hh = df_hh23_unt['Product'].unique().tolist()
    
    
    
    ### CREATE DATE LISTS ###
    
    months = ['All', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    months_x = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    years = ['2022', '2023', '2024']
        
    
    


######################################################################### PRODUCT SALES DATABASE ###########################################################################


elif task_choice == 'Product Sales Reports v1':
    st.header('Product Sales')
    
    
    ### INSERT SELECTION MENU FOR CATEGORY ###
    
    year_select_prod = st.selectbox('Select Year:', 
                                   options=['All', '2023', '2024'])
    
    date_range = st.multiselect('Months:',
                                placeholder='Select Months',
                                options=months,
                                help='If ALL is selected do not add other months.')
    
    if date_range == ['All']:
        date_range = months_x
    
    
    product_type_selection = st.selectbox('Select Product Type:', 
                                         options=product_types)
    
    ### INSERT SELECTION MENU FOR PRODUCT TYPE ###
    
    if product_type_selection == 'Jets':
    
        
        jet_selection = st.selectbox('Jets:',
                                      options=jets,
                                      placeholder='Select Product')
        
    ### REVENUE CHECKBOX ###
    
        revenue_view = st.checkbox('Show Revenue Data')
        
        
        
    ### FILTER DATAFRAME BY SELECTION
    
        mask_jet_23 = df_jet2023_unt.loc[df_jet2023_unt['Product'] == jet_selection][date_range]
        mask_jet_24 = df_jet2024_unt.loc[df_jet2024_unt['Product'] == jet_selection][date_range]
        
        
    ### ASSIGN INDEX NUMBERS FOR ROWS ###
        j_idx = 0
    
        ct_j = 0
        for z in jets:
            if jet_selection == z:
                j_idx = ct_j
            ct_j +=1
    
    ### LOCATE AND DISPLAY RESULTS ###
    
        if year_select_prod == 'All':
            
            st.subheader(sum(mask_jet_23.loc[j_idx][date_range])+sum(mask_jet_24.loc[j_idx][date_range]))  
    
            if revenue_view == True and date_range == months_x:
                prod_rev_share, prod_rev, type_rev = multiyear_product_revenue([df_jet2023_rev, df_jet2024_rev])
                st.write(' - Total Revenue:  $' + '{:,.2f}'.format(prod_rev[jet_selection]) + ' - ' + '{:,.2f}'.format(prod_rev_share[jet_selection]) + '% of revenue from jets')
     
                
                #st.write(dataframe_from_dict(multiyear_product_revenue([df_jet2023_rev, df_jet2024_rev])))
                
            
        elif year_select_prod == '2023':
            avg_per_month = {}
            mbd_display_jet = st.checkbox('Display Monthly Breakdown')
            st.subheader(sum(mask_jet_23.loc[j_idx][date_range]))
            if revenue_view == True and date_range == months_x:
                prod_rev_share, prod_rev, type_rev = multiyear_product_revenue([df_jet2023_rev])
                st.write(' - 2023 Revenue:  $' + '{:,.2f}'.format(prod_rev[jet_selection]) + ' - ' + '{:,.2f}'.format(prod_rev_share[jet_selection]) + '% of revenue from jets')
                display_profit_data(df_jet2023_prof, jet_selection)
            if mbd_display_jet == True:
                for month in date_range:
                    avg_per_month[month] = mask_jet_23.loc[j_idx][month]
                    st.write(month + ' - ' + str(mask_jet_23.loc[j_idx][month]))
                st.write('( - Average per month: ' + str(avg_month(avg_per_month)) + ' - )')
                plot_bar_chart(format_for_chart(df_jet2023_unt.iloc[j_idx]))
    
        else:
            avg_per_month = {}
            mbd_display_jet = st.checkbox('Display Monthly Breakdown')
            st.subheader(sum(mask_jet_24.loc[j_idx][date_range]))
            if revenue_view == True and date_range == months_x:
                prod_rev_share, prod_rev, type_rev = multiyear_product_revenue([df_jet2024_rev])
                st.write(' - 2024 Revenue:  $' + '{:,.2f}'.format(prod_rev[jet_selection]) + ' - ' + '{:,.2f}'.format(prod_rev_share[jet_selection]) + '% of revenue from jets')
                display_profit_data(df_jet2024_prof, jet_selection)
            if mbd_display_jet == True:
                for month in date_range:
                    avg_per_month[month] = mask_jet_24.loc[j_idx][month]
                    st.write(month + ' - ' + str(mask_jet_24.loc[j_idx][month]))
                st.write('( - Average per month: ' + str(avg_month(avg_per_month)) + ' - )')
                plot_bar_chart(format_for_chart(df_jet2024_unt.iloc[j_idx]))
    
            
    elif product_type_selection == 'Controllers':
    
        control_selection = st.selectbox('Controllers:',
                                      options=controllers,
                                      placeholder='Choose an Option')
    ### REVENUE CHECKBOX ###
    
        revenue_view = st.checkbox('Show Revenue Data')
        
        mask_cntl_23 = df_cntl23_unt.loc[df_cntl23_unt['Product'] == control_selection][date_range]
        mask_cntl_24 = df_cntl24_unt.loc[df_cntl24_unt['Product'] == control_selection][date_range]
    
        
        cntl_idx = 0
        if control_selection == 'ShoStarter':
            cntl_idx += 1
        if control_selection == 'ShoMaster':
            cntl_idx += 2
            
        if year_select_prod == '2023':
            avg_per_month = {}
            mbd_display = st.checkbox('Display Monthly Breakdown')
            st.subheader(sum(mask_cntl_23.loc[cntl_idx][date_range]))
            if revenue_view == True and date_range == months_x:
                prod_rev_share, prod_rev, type_rev = multiyear_product_revenue([df_cntl23_rev])
                st.write(' - 2023 Revenue:  $' + '{:,.2f}'.format(prod_rev[control_selection]) + ' - ' + '{:,.2f}'.format(prod_rev_share[control_selection]) + '% of revenue from controllers')
                display_profit_data(df_cntl23_prof, control_selection)
    
    
            if mbd_display == True:
                for month in date_range:
                    avg_per_month[month] = mask_cntl_23.loc[cntl_idx][month]
                    st.write(month + ' - ' + str(mask_cntl_23.loc[cntl_idx][month]))
                st.write('( - Average per month: ' + str(avg_month(avg_per_month)) + ' - )')
                plot_bar_chart(format_for_chart(df_cntl23_unt.iloc[cntl_idx]))
    
            
        elif year_select_prod == '2024':
            avg_per_month = {}
            mbd_display_cntl = st.checkbox('Display Monthly Breakdown')
            st.subheader(sum(mask_cntl_24.loc[cntl_idx][date_range]))
            if revenue_view == True and date_range == months_x:
                prod_rev_share, prod_rev, type_rev = multiyear_product_revenue([df_cntl24_rev])
                st.write(' - 2024 Revenue:  $' + '{:,.2f}'.format(prod_rev[control_selection]) + ' - ' + '{:,.2f}'.format(prod_rev_share[control_selection]) + '% of revenue from controllers')
                display_profit_data(df_cntl24_prof, control_selection)
    
    
            if mbd_display_cntl == True:
                for month in date_range:
                    avg_per_month[month] = mask_cntl_24.loc[cntl_idx][month]
                    st.write(month + ' - ' + str(mask_cntl_24.loc[cntl_idx][month]))
                st.write('( - Average per month: ' + str(avg_month(avg_per_month)) + ' - )')
                plot_bar_chart(format_for_chart(df_cntl24_unt.iloc[cntl_idx]))
    
        
        else:
            st.subheader(sum(mask_cntl_23.loc[cntl_idx][date_range])+sum(mask_cntl_24.loc[cntl_idx][date_range]))
            if revenue_view == True and date_range == months_x:
                prod_rev_share, prod_rev, type_rev = multiyear_product_revenue([df_cntl23_rev, df_cntl24_rev])
                st.write(' - Total Revenue:  $' + '{:,.2f}'.format(prod_rev[control_selection]) + ' - ' + '{:,.2f}'.format(prod_rev_share[control_selection]) + '% of revenue from controllers')
    
    
            
    
        
    elif product_type_selection == 'Hoses':   
        
        hose_selection = st.multiselect('Hoses:',
                                      options=hoses,
                                      placeholder='Choose an Option')
            
        hose_sum = 0
        
        if len(hose_selection) < 1:
            pass
        else:
            if year_select_prod == '2023':
                for x in hose_selection:
    
                    mask_hose = df_h23_unt.loc[df_h23_unt['Product'] == x][date_range]
                    
                    for y in mask_hose:
                        hose_sum += int(mask_hose[y])
                        
            elif year_select_prod == '2024':
                for x in hose_selection:
                    
                    mask_hose = df_h24_unt.loc[df_h24_unt['Product'] == x][date_range]
                    
                    for y in mask_hose:
                        hose_sum += int(mask_hose[y])
                        
            else:
                for x in hose_selection:
                    
                    mask_hose_23 = df_h23_unt.loc[df_h23_unt['Product'] == x][date_range]
                    mask_hose_24 = df_h24_unt.loc[df_h24_unt['Product'] == x][date_range]
                    
                    for y in mask_hose_23:
                        hose_sum += int(mask_hose_23[y]) + int(mask_hose_24[y])
                        
                    
                
            st.subheader(hose_sum)
    
    
        
    elif product_type_selection == 'Accessories':
        
        acc_selection = st.selectbox('Accessories:',
                                      options=acc,
                                      placeholder='Choose an Option')
    
        
    
        mask_acc_23 = df_ac23_unt.loc[df_ac23_unt['Product'] == acc_selection][date_range]
        mask_acc_24 = df_ac24_unt.loc[df_ac24_unt['Product'] == acc_selection][date_range]
        
        ac_idx = 0
    
        ct_ac = 0
        
        for y in acc:
            if acc_selection == y:
                ac_idx = ct_ac
            else:
                ct_ac += 1
    
        if year_select_prod == '2023':
            avg_per_month = {}
            mbd_display_acc = st.checkbox('Display Monthly Breakdown')
            if mbd_display_acc == True:
                for month in date_range:
                    avg_per_month[month] = mask_acc_23.loc[ac_idx][month]
                    st.write(month + ' - ' + str(mask_acc_23.loc[ac_idx][month]))
                st.write('( - Average per month: ' + str(avg_month(avg_per_month)) + ' - )')
            st.subheader(sum(mask_acc_23.loc[ac_idx][date_range]))     
            
        elif year_select_prod == '2024':
            avg_per_month = {}
            mbd_display_acc = st.checkbox('Display Monthly Breakdown')
            if mbd_display_acc == True:
                for month in date_range:
                    avg_per_month[month] = mask_acc_24.loc[ac_idx][month]
                    st.write(month + ' - ' + str(mask_acc_24.loc[ac_idx][month]))
                st.write('( - Average per month: ' + str(avg_month(avg_per_month)) + ' - )')
            st.subheader(sum(mask_acc_24.loc[ac_idx][date_range]))
        
        else:
            st.subheader(sum(mask_acc_23.loc[ac_idx][date_range])+sum(mask_acc_24.loc[ac_idx][date_range]))
            
    elif product_type_selection == 'Handhelds':
    
        hh_selection = st.multiselect('Handhelds:',
                                      options=hh,
                                      placeholder='Choose an Option')
            
        hh_sum = 0
        
        if len(hh_selection) < 1:
            pass
        else:
            if year_select_prod == '2023':
                for x in hh_selection:
    
                    mask_hh = df_hh23_unt.loc[df_hh23_unt['Product'] == x][date_range]
                    
                    for y in mask_hh:
                        hh_sum += int(mask_hh[y])
                        
            elif year_select_prod == '2024':
                for x in hh_selection:
                    
                    mask_hh = df_hh24_unt.loc[df_hh24_unt['Product'] == x][date_range]
                    
                    for y in mask_hh:
                        hh_sum += int(mask_hh[y])
                        
            else:
                for x in hh_selection:
                    
                    mask_hh_23 = df_hh23_unt.loc[df_hh23_unt['Product'] == x][date_range]
                    mask_hh_24 = df_hh24_unt.loc[df_hh24_unt['Product'] == x][date_range]
                    
                    for y in mask_hh_23:
                        hh_sum += int(mask_hh_23[y]) + int(mask_hh_24[y])
                                      
                
            st.subheader(hh_sum)
            
    
    st.divider()

    

	

elif task_choice == 'Leaderboards':
	
	st.header('Customer Leaderboards')	
	
	def sort_top_20(dict, number):

		leaderboard_list = []
	    
		for key, value in dict.items():
			if value >= 2500:
				leaderboard_list.append((key, value))
	
		sorted_leaderboard = sorted(leaderboard_list, key=lambda x: x[1], reverse=True)
		
		return sorted_leaderboard[:number]
	
	
	spend_year = st.selectbox('Choose Year', 
			     ['2024', '2023'])
	
	ranking_number = st.selectbox('Choose Leaderboard Length',
				 [5, 10, 15, 20, 25, 50])
	
	cust_spend_dict_2023 = {}
	cust_spend_dict_2024 = {}
	
	
	for cust in unique_customer_list:
		cust_spend_dict_2023[cust] = 0
		cust_spend_dict_2024[cust] = 0
	
	idx = 0
	
	for customer in df.customer:
	
		if df.iloc[idx].ordered_year == '2023':
			cust_spend_dict_2023[customer] += float(df.iloc[idx].total_line_item_spend)
		elif df.iloc[idx].ordered_year == '2024':
			cust_spend_dict_2024[customer] += float(df.iloc[idx].total_line_item_spend)
		idx += 1
	
	rank = 1
	if spend_year == '2023':
	
		result = sort_top_20(cust_spend_dict_2023, ranking_number)
		for leader in result:
			st.subheader(str(rank) + ')  ' + leader[0] + ' : $' + '{:,.2f}'.format(leader[1]))
		    
			rank += 1
		    
	elif spend_year == '2024':
	
		result = sort_top_20(cust_spend_dict_2024, ranking_number)
		for leader in result:
			st.subheader(str(rank) + ')  ' + leader[0] + ' : $' + '{:,.2f}'.format(leader[1]))
		
			rank += 1
	    
	    
    
  






















