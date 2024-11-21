import pandas as pd
import streamlit as st
#import plotly.express as px
from PIL import Image
import numpy as np
from collections import ChainMap, defaultdict
import difflib
import altair as alt
#import matplotlib.pyplot as plt
from operator import itemgetter
from datetime import datetime

### SET WEB APP CONFIGURATIONS
st.set_page_config(page_title='Club Cannon Database', 
                  layout='centered')

### SET HEADER IMAGE
image = Image.open('club-cannon-logo-bbb.png')
st.image(image, 
        use_column_width=True)

st.divider()
### LOAD FILES
sod_ss = 'SOD 11.18.24.xlsx'

hsd_ss = 'HSD 11.8.24.xlsx'

quote_ss = 'Quote Report 10.23.24.xlsx'

sales_sum_csv = 'Fulcrum Sales Summary/Total Summary-2022 - Present.csv'

shipstat_ss_24 = '2024 SR 11.01.24.xlsx'
shipstat_ss_23 = '2023 SR.xlsx'

prod_sales = 'Product Sales Data.xlsx'

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

df = pd.read_excel(sod_ss,
                   dtype=object,
                   header=0)

df_quotes = pd.read_excel(quote_ss, 
                          dtype=object,
                          header=0)

df_shipstat_24 = pd.read_excel(shipstat_ss_24, 
                               dtype=object,
                               header=0)
df_shipstat_23 = pd.read_excel(shipstat_ss_23,
                               dtype=object,
                               header=0)

df_hsd = pd.read_excel(hsd_ss,
                       dtype=object,
                       header=0)


### DEFINE FUNCTION TO CREATE PRODUCT DATAFRAME FROM EXCEL SPREADSHEET ###

def gen_product_df_from_excel(ss, sheet_name, cols=None):

    df_product_year = pd.read_excel(ss,
                                   usecols=cols,
                                   names=['Product', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total'],
                                   sheet_name=sheet_name,
                                    dtype=object,
                                    header=1)
    return df_product_year


df_csv = pd.read_csv(sales_sum_csv,
                    usecols=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])


df_acc_2024 = pd.read_excel(prod_sales,
                   usecols='a:m',
                   names=['Product', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total'],
                   sheet_name=acc_2024,
                   dtype=object,
                   header=1)
df_cntl_2024 = pd.read_excel(prod_sales,
                   usecols='a:m',
                   names=['Product', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total'],
                   sheet_name=cntl_2024,
                   dtype=object,
                   header=1)
df_jet_2024 = pd.read_excel(prod_sales,
                   usecols='a:m',
                   names=['Product', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total'],
                   sheet_name=jet_2024,
                   dtype=object,
                   header=1)
df_hh_2024 = pd.read_excel(prod_sales,
                   usecols='a:m',
                   names=['Product', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total'],
                   sheet_name=hh_2024,
                   dtype=object,
                   header=1)
df_hose_2024 = pd.read_excel(prod_sales,
                   usecols='a:m',
                   names=['Product', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total'],
                   sheet_name=hose_2024,
                   dtype=object,
                   header=1)

df_acc_2023 = pd.read_excel(prod_sales,
                   usecols='a:m',
                   names=['Product', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total'],
                   sheet_name=acc_2023,
                   dtype=object,
                   header=1)
df_cntl_2023 = pd.read_excel(prod_sales,
                   names=['Product', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total'],
                   sheet_name=cntl_2023,
                   dtype=object,
                   header=1)
df_jet_2023 = pd.read_excel(prod_sales,
                   usecols='a:m',
                   names=['Product', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total'],
                   sheet_name=jet_2023,
                   dtype=object,
                   header=1)
df_hh_2023 = pd.read_excel(prod_sales,
                   usecols='a:m',
                   names=['Product', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total'],
                   sheet_name=hh_2023,
                   dtype=object,
                   header=1)
df_hose_2023 = pd.read_excel(prod_sales,
                   usecols='a:m',
                   names=['Product', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Total'],
                   sheet_name=hose_2023,
                   dtype=object,
                   header=1)


### CREATE DATE LISTS ###

months = ['All', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
months_x = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
years = ['2022', '2023', '2024']
    
    
### DEFINE FUNCTION TO RENAME COLUMNS FOR CHART AXIS SORTING ###

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

def dataframe_from_dict(dict):

    dict_of_lists = {'Products': [], 
                    'Share': []}

    for key, value in dict.items():
        dict_of_lists['Products'].append(key)
        dict_of_lists['Share'].append(value)

    df = pd.DataFrame(dict_of_lists)
    
    return df

### DEFINE A FUNCTION TO COMBINE MULTIPLE YEARS OF PRODUCT REVENUE DATA ###

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


def get_sales_orders(customer, dataFrame):

    temp_list = []

    ct = 0
    while df.iloc[idx + ct]['Sales Order'] == df.iloc[idx + ct + 1]['Sales Order']:
        
        temp_list.append(df.iloc[idx + ct]['Line Item Name'] + ' x ' + str(df.iloc[idx + ct]['Order Quantity']))
        ct += 1
            
    temp_dict[df.iloc[idx]['Sales Order']] = temp_list

    return temp_dict

### MAKE LIST OF PRODUCT TYPES ###

product_types = ['Jets', 'Controllers', 'Hoses', 'Accessories', 'Handhelds']


### SEPARATE SALES AND REVENUE ###

df_jet2023_unt = df_jet_2023[0:4].fillna(0)
df_jet2023_rev = df_jet_2023[13:17].fillna(0)
df_jet2023_prof = df_jet_2023[20:24].fillna(0).rename({'March': 'Cost', 'April': 'Avg Price', 'May': 'Net Profit / Unit', 'June': 'Total Net Profit'}, axis=1).drop(['January', 'February', 'July', 'August', 'September', 'October', 'November', 'December'], axis=1).reset_index()

df_cntl23_unt = df_cntl_2023[0:3].fillna(0)
df_cntl23_rev = df_cntl_2023[11:14].fillna(0)
df_cntl23_prof = df_cntl_2023[17:20].fillna(0).rename({'March': 'Cost', 'April': 'Avg Price', 'May': 'Net Profit / Unit', 'June': 'Total Net Profit'}, axis=1).drop(['January', 'February', 'July', 'August', 'September', 'October', 'November', 'December'], axis=1).reset_index()

df_h23_unt = df_hose_2023[0:22].fillna(0)
df_h23_rev = df_hose_2023[48:70].fillna(0)

df_ac23_unt = df_acc_2023[0:30].fillna(0)
df_ac23_rev = df_acc_2023[58:85].fillna(0)

df_hh23_unt = df_hh_2023[0:4].fillna(0)
df_hh23_rev = df_hh_2023[13:17].fillna(0)

df_jet2024_unt = df_jet_2024[0:4].fillna(0)
df_jet2024_rev = df_jet_2024[13:17].fillna(0)
df_jet2024_prof = df_jet_2024[20:24].fillna(0).rename({'March': 'Cost', 'April': 'Avg Price', 'May': 'Net Profit / Unit', 'June': 'Total Net Profit'}, axis=1).drop(['January', 'February', 'July', 'August', 'September', 'October', 'November', 'December'], axis=1).reset_index()

df_cntl24_unt = df_cntl_2024[0:3].fillna(0)
df_cntl24_rev = df_cntl_2024[11:14].fillna(0)
df_cntl24_prof = df_cntl_2024[17:20].fillna(0).rename({'March': 'Cost', 'April': 'Avg Price', 'May': 'Net Profit / Unit', 'June': 'Total Net Profit'}, axis=1).drop(['January', 'February', 'July', 'August', 'September', 'October', 'November', 'December'], axis=1).reset_index()
                                        
df_h24_unt = df_hose_2024[0:22].fillna(0)
df_h24_rev = df_hose_2024[48:70].fillna(0)

df_ac24_unt = df_acc_2024[0:30].fillna(0)
df_ac24_rev = df_acc_2024[59:86].fillna(0)
#st.write(df_ac24_rev)

df_hh24_unt = df_hh_2024[0:4].fillna(0)
df_hh24_rev = df_hh_2024[13:17].fillna(0)


### CREATE LISTS OF CATEGORIES FROM DATAFRAME ###

jets = df_jet2023_unt['Product'].unique().tolist()
controllers = df_cntl23_unt['Product'].unique().tolist()
hoses = df_h23_unt['Product'].unique().tolist()
acc = df_ac23_unt['Product'].unique().tolist()
hh = df_hh23_unt['Product'].unique().tolist()


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

#st.write(website_rev_dict_23)
#st.write(website_rev_dict_24)
#st.write(fulcrum_rev_dict_23)
#st.write(fulcrum_rev_dict_24)

#st.subheader('Woocommerce 2023: ' + '(${:,.2f})'.format(website_rev_23) + ' in revenue, ' + percent_of_sales(website_rev_23, fulcrum_rev_23))
#st.subheader('Fulcrum 2023: ' + '(${:,.2f})'.format(fulcrum_rev_23) + ' in revenue, ' + percent_of_sales(fulcrum_rev_23, website_rev_23))
#st.subheader('Woocommerce 2024: ' + '(${:,.2f})'.format(website_rev_24) + ' in revenue, ' + percent_of_sales(website_rev_24, fulcrum_rev_24))
#st.subheader('Fulcrum 2024: ' + '(${:,.2f})'.format(fulcrum_rev_24) + ' in revenue, ' + percent_of_sales(fulcrum_rev_24, website_rev_24))


### MAKE DICTIONARIES OF PRODUCT SALES FOR CHARTING ###

jet_dict_2023 = {'Pro Jet': 0,
                'Quad Jet': 0,
                'Micro Jet': 0,
                'Cryo Clamp': 0}
jet_dict_2024 = {'Pro Jet': 0,
                'Quad Jet': 0,
                'Micro Jet': 0,
                'Cryo Clamp': 0}
control_dict_2023 = {'The Button': 0,
                     'Shostarter': 0,
                     'Shomaster': 0}
control_dict_2024 = {'The Button': 0,
                     'Shostarter': 0,
                     'Shomaster': 0}
handheld_dict_2023 = {'8FT - No Case': 0,
                     '8FT - Travel Case': 0,
                     '15FT - No Case': 0,
                     '15FT - Travel Case': 0}
handheld_dict_2024 = {'8FT - No Case': 0,
                     '8FT - Travel Case': 0,
                     '15FT - No Case': 0,
                     '15FT - Travel Case': 0}

idx = 0
for line_item in df.line_item:
    if line_item[:6] == 'CC-PRO':
        if df.iloc[idx].ordered_year == '2023':
            jet_dict_2023['Pro Jet'] += df.iloc[idx].quantity
        elif df.iloc[idx].ordered_year == '2024':
            jet_dict_2024['Pro Jet'] += df.iloc[idx].quantity
        else:
            pass
    idx += 1



### CREATE A LIST OF UNIQUE CUSTOMERS ###
unique_customer_list = df.customer.unique().tolist()

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


task_select = st.selectbox('Choose Widget Task', 
                          options=[' - Choose an Option - ', 'Customer Details', 'Customer Spending Leaders', 'Product Sales', 'Monthly Sales', 'Customer Quote Reports', 'Shipping Reports'])

st.divider()

### TESTING ###

bom_cost_jet = {'Pro Jet': 290.86, 'Micro Jet': 243.57, 'Quad Jet': 630.43, 'Quad Jet WP': 651.80, 'Cryo Clamp': 166.05}
bom_cost_control = {'The Button': 141.07, 'ShoStarter': 339.42, 'ShoMaster': 667.12}
bom_cost_hh = {'8FT NC': 143.62, '8FT TC': 219.06, '15FT NC': 153.84, '15FT TC': 231.01}
bom_cost_hose = {'2FT MFD': 20.08, '3.5FT MFD': 22.50, '5FT MFD': 24.25, '5FT STD': 31.94, '5FT DSY': 31.84, '5FT EXT': 33.24, '8FT STD': 32.42, '8FT DSY': 34.52, '8FT EXT': 34.82, '15FT STD': 43.55, '15FT DSY': 46.47, '15FT EXT': 46.77, 
                 '25FT STD': 59.22, '25FT DSY': 61.87, '25FT EXT': 62.17, '35FT STD': 79.22, '35FT DSY': 81.32, '35FT EXT': 81.62, '50FT STD': 103.57, '50FT EXT': 105.97, '100FT STD': 183.39}
bom_cost_acc = {'CC-AC-CCL': 29.17, 'CC-AC-CTS': 6.70, 'CC-F-DCHA': 7.15, 'CC-F-HEA': 6.86, 'CC-AC-RAA': 11.94, 'CC-AC-4PM': 48.12, 'CC-F-MFDCGAJIC': 7.83, 'CC-AC-CGAJIC-SET': 5.16, 'CC-AC-CTC-20': 10.92, 'CC-AC-CTC-50': 19.36, 'CC-AC-TC': 89.46, 'CC-VV-KIT': 29.28, 
                'CC-RC-2430': 847, 'CC-AC-LA2': 248.10}

### DEFINE A FUNCTION TO CALCULATE TOTAL ITEM SALES ANNUALLY ###

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
        

jet_23 = {'January': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'February': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'March': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'April': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'May': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'June': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'July': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'August': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'September': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'October': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'November': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'December': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}}

jet_24 = {'January': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'February': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'March': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'April': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'May': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'June': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'July': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'August': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'September': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'October': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'November': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}, 
           'December': {'Pro Jet': [0,0], 'Micro Jet': [0,0], 'Quad Jet': [0,0], 'Cryo Clamp': [0,0]}}

handheld_23 = {'January': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'February': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'March': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'April': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'May': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'June': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'July': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'August': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'September': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'October': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'November': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'December': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}}
handheld_24 = {'January': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'February': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'March': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'April': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'May': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'June': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'July': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'August': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'September': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'October': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'November': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}, 
               'December': {'8FT No Case': 0, '8FT Travel Case': 0, '15FT No Case': 0, '15FT Travel Case': 0}}

control_23 = {'January': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'February': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'March': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'April': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'May': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'June': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'July': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'August': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'September': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'October': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'November': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'December': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}}
control_24 = {'January': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'February': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'March': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'April': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'May': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'June': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'July': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'August': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'September': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'October': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'November': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}, 
               'December': {'The Button': 0, 'ShoStarter': 0, 'ShoMaster': 0}}

hose_23 = {'January': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 
           0, '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'February': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'March': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'April': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'May': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'June': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'July': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'August': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'September': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'October': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'November': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'December': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0}}
hose_24 = {'January': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'February': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'March': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'April': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'May': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'June': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'July': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'August': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'September': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'October': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'November': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0},
           'December': {'2FT MFD': 0, '3.5FT MFD': 0, '5FT MFD': 0, '5FT STD': 0, '5FT DSY': 0, '5FT EXT': 0, '8FT STD': 0, '8FT DSY': 0, '8FT EXT': 0, '15FT STD': 0, '15FT DSY': 0, '15FT EXT': 0, 
                      '25FT STD': 0, '25FT DSY': 0, '25FT EXT': 0, '35FT STD': 0, '35FT DSY': 0, '35FT EXT': 0, '50FT STD': 0, '50FT EXT': 0, '100FT STD': 0, 'XX': 0}}
idx = 0

for line in df.sales_order:
    year = df.iloc[idx].order_date.year
    month = num_to_month(df.iloc[idx].order_date.month)
    if df.iloc[idx].item_sku[:5] == 'CC-PR':
        if year == 2023:
            jet_23[month]['Pro Jet'][0] += df.iloc[idx].quantity
            jet_23[month]['Pro Jet'][1] += df.iloc[idx].total_line_item_spend
        elif year == 2024:
            jet_24[month]['Pro Jet'][0] += df.iloc[idx].quantity
            jet_24[month]['Pro Jet'][1] += df.iloc[idx].total_line_item_spend
    elif df.iloc[idx].item_sku[:5] == 'CC-MJ':
        if year == 2023:
            jet_23[month]['Micro Jet'][0] += df.iloc[idx].quantity
            jet_23[month]['Micro Jet'][1] += df.iloc[idx].total_line_item_spend
        elif year == 2024:
            jet_24[month]['Micro Jet'][0] += df.iloc[idx].quantity 
            jet_24[month]['Micro Jet'][1] += df.iloc[idx].total_line_item_spend
    elif df.iloc[idx].item_sku[:5] == 'CC-QJ':
        if year == 2023:
            jet_23[month]['Quad Jet'][0] += df.iloc[idx].quantity
            jet_23[month]['Quad Jet'][1] += df.iloc[idx].total_line_item_spend
        elif year == 2024:
            jet_24[month]['Quad Jet'][0] += df.iloc[idx].quantity
            jet_24[month]['Quad Jet'][1] += df.iloc[idx].total_line_item_spend
    elif df.iloc[idx].item_sku[:6] == 'CC-CC2':
        if year == 2023:
            jet_23[month]['Cryo Clamp'][0] += df.iloc[idx].quantity
            jet_23[month]['Cryo Clamp'][1] += df.iloc[idx].total_line_item_spend
        elif year == 2024:
            jet_24[month]['Cryo Clamp'][0] += df.iloc[idx].quantity 
            jet_24[month]['Cryo Clamp'][1] += df.iloc[idx].total_line_item_spend
            
    elif df.iloc[idx].item_sku[:8] == 'CC-TB-35':
        if year == 2023:
            control_23[month]['The Button'] += df.iloc[idx].quantity
        elif year == 2024:
            control_24[month]['The Button'] += df.iloc[idx].quantity
    elif df.iloc[idx].item_sku[:8] == 'CC-SS-35':
        if year == 2023:
            control_23[month]['ShoStarter'] += df.iloc[idx].quantity
        elif year == 2024:
            control_24[month]['ShoStarter'] += df.iloc[idx].quantity
    elif df.iloc[idx].item_sku[:5] == 'CC-SM':
        if year == 2023:
            control_23[month]['ShoMaster'] += df.iloc[idx].quantity
        elif year == 2024:
            control_24[month]['ShoMaster'] += df.iloc[idx].quantity
            
    elif df.iloc[idx].item_sku[11:] == '08-NC':
        if year == 2023:
            handheld_23[month]['8FT No Case'] += df.iloc[idx].quantity
            hose_23[month]['8FT STD'] += 1
        elif year == 2024:
            handheld_24[month]['8FT No Case'] += df.iloc[idx].quantity
            hose_24[month]['8FT STD'] += 1
    elif df.iloc[idx].item_sku[11:] == '08-TC':
        if year == 2023:
            handheld_23[month]['8FT Travel Case'] += df.iloc[idx].quantity
            hose_23[month]['8FT STD'] += 1
        elif year == 2024:
            handheld_24[month]['8FT Travel Case'] += df.iloc[idx].quantity
            hose_24[month]['8FT STD'] += 1
    elif df.iloc[idx].item_sku[11:] == '15-NC':
        if year == 2023:
            handheld_23[month]['15FT No Case'] += df.iloc[idx].quantity
            hose_23[month]['15FT STD'] += 1
        elif year == 2024:
            handheld_24[month]['15FT No Case'] += df.iloc[idx].quantity
            hose_24[month]['15FT STD'] += 1
    elif df.iloc[idx].item_sku[11:] == '15-TC':
        if year == 2023:
            handheld_23[month]['15FT Travel Case'] += df.iloc[idx].quantity
            hose_23[month]['15FT STD'] += 1
        elif year == 2024:
            handheld_24[month]['15FT Travel Case'] += df.iloc[idx].quantity
            hose_24[month]['15FT STD'] += 1
            
    elif df.iloc[idx].item_sku[:8] == 'CC-CH-XX':
        if year == 2023:
            hose_23[month]['XX'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['XX'] += df.iloc[idx].quantity   
    elif df.iloc[idx].item_sku[:8] == 'CC-CH-02':
        if year == 2023:
            hose_23[month]['2FT MFD'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['2FT MFD'] += df.iloc[idx].quantity
    elif df.iloc[idx].item_sku[:8] == 'CC-CH-03':
        if year == 2023:
            hose_23[month]['3.5FT MFD'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['3.5FT MFD'] += df.iloc[idx].quantity
    elif df.iloc[idx].item_sku == 'CC-CH-05-MFD':
        if year == 2023:
            hose_23[month]['5FT MFD'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['5FT MFD'] += df.iloc[idx].quantity
    elif df.iloc[idx].item_sku == 'CC-CH-05-STD' or df.iloc[idx].item_sku == 'CC-CH-05-STD-1':
        if year == 2023:
            hose_23[month]['5FT STD'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['5FT STD'] += df.iloc[idx].quantity 
    elif df.iloc[idx].item_sku == 'CC-CH-05-DSY':
        if year == 2023:
            hose_23[month]['5FT DSY'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['5FT DSY'] += df.iloc[idx].quantity   
    elif df.iloc[idx].item_sku == 'CC-CH-05-EXT':
        if year == 2023:
            hose_23[month]['5FT EXT'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['5FT EXT'] += df.iloc[idx].quantity   
    elif df.iloc[idx].item_sku == 'CC-CH-08-STD':
        if year == 2023:
            hose_23[month]['8FT STD'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['8FT STD'] += df.iloc[idx].quantity   
    elif df.iloc[idx].item_sku == 'CC-CH-08-DSY':
        if year == 2023:
            hose_23[month]['8FT DSY'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['8FT DSY'] += df.iloc[idx].quantity   
    elif df.iloc[idx].item_sku == 'CC-CH-08-EXT':
        if year == 2023:
            hose_23[month]['8FT EXT'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['8FT EXT'] += df.iloc[idx].quantity   
    elif df.iloc[idx].item_sku == 'CC-CH-15-STD':
        if year == 2023:
            hose_23[month]['15FT STD'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['15FT STD'] += df.iloc[idx].quantity   
    elif df.iloc[idx].item_sku == 'CC-CH-15-DSY':
        if year == 2023:
            hose_23[month]['15FT DSY'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['15FT DSY'] += df.iloc[idx].quantity   
    elif df.iloc[idx].item_sku == 'CC-CH-15-EXT':
        if year == 2023:
            hose_23[month]['15FT EXT'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['15FT EXT'] += df.iloc[idx].quantity 
    elif df.iloc[idx].item_sku == 'CC-CH-25-STD':
        if year == 2023:
            hose_23[month]['25FT STD'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['25FT STD'] += df.iloc[idx].quantity   
    elif df.iloc[idx].item_sku == 'CC-CH-25-DSY':
        if year == 2023:
            hose_23[month]['25FT DSY'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['25FT DSY'] += df.iloc[idx].quantity   
    elif df.iloc[idx].item_sku == 'CC-CH-25-EXT':
        if year == 2023:
            hose_23[month]['25FT EXT'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['25FT EXT'] += df.iloc[idx].quantity 
    elif df.iloc[idx].item_sku == 'CC-CH-35-STD':
        if year == 2023:
            hose_23[month]['35FT STD'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['35FT STD'] += df.iloc[idx].quantity   
    elif df.iloc[idx].item_sku == 'CC-CH-35-DSY':
        if year == 2023:
            hose_23[month]['35FT DSY'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['35FT DSY'] += df.iloc[idx].quantity   
    elif df.iloc[idx].item_sku == 'CC-CH-35-EXT':
        if year == 2023:
            hose_23[month]['35FT EXT'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['35FT EXT'] += df.iloc[idx].quantity 
    elif df.iloc[idx].item_sku == 'CC-CH-50-STD':
        if year == 2023:
            hose_23[month]['50FT STD'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['50FT STD'] += df.iloc[idx].quantity 
    elif df.iloc[idx].item_sku == 'CC-CH-50-EXT':
        if year == 2023:
            hose_23[month]['50FT EXT'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['50FT EXT'] += df.iloc[idx].quantity 
    elif df.iloc[idx].item_sku == 'CC-CH-100-STD':
        if year == 2023:
            hose_23[month]['100FT STD'] += df.iloc[idx].quantity
        elif year == 2024:
            hose_24[month]['100FT STD'] += df.iloc[idx].quantity 
            
    idx += 1


def display_data(dict_sales, dict_bom):

	for key, val in dict_sales.items():
		st.subheader('{}:  \n'.format(key))
		for k, v in val.items():
			avg_price = 0
			avg_profit = 0
			if v[0] == 0:
				pass
			else:
				avg_price = (v[1]/v[0])	
				if avg_price == 0:
					avg_profit = 0
				else:
					avg_profit = abs(avg_price - dict_bom[k])
				
			st.markdown(f' - **{k}** - **{v[0]}**  \n')
			st.write('  :green[         Average Price: ${:,.2f}]'.format(avg_price))
			st.write('  :green[        Average Profit: ${:,.2f}]'.format(avg_profit))


	return None
	
#st.write(jet_24)
#display_data(jet_24, bom_cost_jet)

#product_category = st.selectbox('Choose a Product Type',
                                #options=['Jets', 'Controllers', 'Handhelds', 'Hoses'])
#year_choice = st.selectbox('Select Year',
                           #options=[2023, 2024], 
                           #placeholder='Select an Option')


#if product_category == 'Jets':
    #if year_choice == 2023:
        #display_category_totals(jet_23)
    #elif year_choice == 2024:
        #display_category_totals(jet_24)
    

#st.subheader('Total: {}'.format(product_totals(handheld_23, '15FT Travel Case')))


### TESTING ###


### REVISED MONTHLY SALES REPORTING ###

if task_select == 'Monthly Sales':

    st.header('Monthly Sales')


### DEFINE FUNCTION TO GATHER MONTHLY SALES INTO DICTIONARY FROM DATAFRAME ###    
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
            st.write('{}: ${:,.2f}  \n({:.2f}% Web, {:.2f}% Fulcrum)'.format(month, month_sales, woo, fulcrum))
    
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

### FUNCTIONS FOR PLOTTING CHARTS ###
    def format_for_chart_ms(dict):
        
        temp_dict = {'Months': months_x,
                    'Total Sales': []}
        
        for month, sales in dict.items():
            if len(temp_dict['Total Sales']) >= 12:
                pass
            else:
                temp_dict['Total Sales'].append(sales[0] + sales[1])
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

    
    comp_col = st.checkbox('Comparison Column')

    ### DISPLAY SALES REPORTS ###
    if comp_col == False:
  
        year_select = st.selectbox('Choose Year',
                                   options=[2023, 2024])
        
        if year_select == 2023:
            monthly_sales = get_monthly_sales(df, 2023)
            display_monthly_sales(monthly_sales)
            total_sales, web_percent, fulcrum_percent, avg_month = calc_monthly_totals(monthly_sales)
            st.subheader('{} Total: ${:,.2f}  \n({:.2f}% Web, {:.2f}% Fulcrum)  \n(${:,.2f} / Month)'.format(year_select, total_sales, web_percent, fulcrum_percent, avg_month))
            plot_bar_chart_ms(format_for_chart_ms(monthly_sales))
            
        elif year_select == 2024:
            monthly_sales = get_monthly_sales(df, 2024)
            display_monthly_sales(monthly_sales)
            total_sales, web_percent, fulcrum_percent, avg_month = calc_monthly_totals(monthly_sales)
            st.subheader('{} Total: ${:,.2f}  \n({:.2f}% Web, {:.2f}% Fulcrum)  \n${:,.2f} / Month'.format(year_select, total_sales, web_percent, fulcrum_percent, avg_month))
            plot_bar_chart_ms(format_for_chart_ms(monthly_sales))

    if comp_col == True:
        col20, col21 = st.columns(2)
        with col20:
            year_select = st.selectbox('Choose Year',
                           options=[2023, 2024])
            
            if year_select == 2023:
                display_monthly_sales(get_monthly_sales(df, 2023))
                total_sales, web_percent, fulcrum_percent, avg_month = calc_monthly_totals(get_monthly_sales(df, year_select))
                st.subheader('{} Total: ${:,.2f}  \n({:.2f}% Web, {:.2f}% Fulcrum)  \n${:,.2f} / Month'.format(year_select, total_sales, web_percent, fulcrum_percent, avg_month))
            elif year_select == 2024:
                display_monthly_sales(get_monthly_sales(df, 2024))
                total_sales, web_percent, fulcrum_percent, avg_month = calc_monthly_totals(get_monthly_sales(df, year_select))
                st.subheader('{} Total: ${:,.2f}  \n({:.2f}% Web, {:.2f}% Fulcrum)  \n${:,.2f} / Month'.format(year_select, total_sales, web_percent, fulcrum_percent, avg_month))
            
        with col21:
            year_select_2 = st.selectbox('Select Year', 
                                       options=[2024, 2023])

            if year_select_2 == 2023:
                display_monthly_sales(get_monthly_sales(df, 2023))
                total_sales, web_percent, fulcrum_percent, avg_month = calc_monthly_totals(get_monthly_sales(df, year_select_2))
                st.subheader('{} Total: ${:,.2f}  \n({:.2f}% Web, {:.2f}% Fulcrum)  \n${:,.2f} / Month'.format(year_select_2, total_sales, web_percent, fulcrum_percent, avg_month))
            elif year_select_2 == 2024:
                display_monthly_sales(get_monthly_sales(df, 2024))
                total_sales, web_percent, fulcrum_percent, avg_month = calc_monthly_totals(get_monthly_sales(df, year_select_2))
                st.subheader('{} Total: ${:,.2f}  \n({:.2f}% Web, {:.2f}% Fulcrum)  \n${:,.2f} / Month'.format(year_select_2, total_sales, web_percent, fulcrum_percent, avg_month))


        
### SHIPPING REPORTS ###  
    
if task_select == 'Shipping Reports':


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
                                 options=['2023', '2024'])
    
    fedex_total = 0
    ups_total = 0
    shipstat_cc_charges = 0
    shipstat_cust_pmnts = 0
    fulcrum_ship_charges = 0


    if ss_year_select == '2024':
        
        st.header('2024 Shipping Record') 

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
    
        st.write('FedEx Charges: ${:,.2f} - '.format(fedex_total) + '({:.2f}%)'.format(percent_of_sales(fedex_total, ups_total)))
        
        st.write('UPS Charges: ${:,.2f} - '.format(ups_total) + '({:.2f}%)'.format(percent_of_sales(ups_total, fedex_total)))    
        
        st.write('Website Cost: ${:,.2f}'.format(shipstat_cc_charges))
        st.write('Website Payments: ${:,.2f}'.format(shipstat_cust_pmnts))
        
        st.write('Fulcrum Charges: ${:,.2f}'.format(fulcrum_ship_charges))
        st.write('Fulcrum Payments: ${:,.2f}'.format(fulcrum_ship_pmnts_24))

        st.divider()
        
        st.subheader('Total Charges: ${:,.2f}'.format(total_ship_cost))
        st.subheader('Total Payments: ${:,.2f}'.format(total_ship_pmnts))

        st.divider()
        
        for key, val in shipping_2024.items():
            st.subheader(key)
            st.write('Charges: ${:,.2f}'.format(val[0]))
            st.write('Payments: ${:,.2f}'.format(val[1]))
            st.write('FedEx Charges: ${:,.2f}'.format(val[2]))
            st.write('UPS Charges: ${:,.2f}'.format(val[3]))

    
    elif ss_year_select == '2023':
        
        st.header('2023 Shipping Record')

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
    
        st.write('FedEx Charges: ${:,.2f} - '.format(fedex_total) + '({:.2f}%)'.format(percent_of_sales(fedex_total, ups_total)))
        
        st.write('UPS Charges: ${:,.2f} - '.format(ups_total) + '({:.2f}%)'.format(percent_of_sales(ups_total, fedex_total)))    
        
        st.write('Website Cost: ${:,.2f}'.format(shipstat_cc_charges))
        st.write('Website Payments: ${:,.2f}'.format(shipstat_cust_pmnts))
        
        st.write('Fulcrum Charges: ${:,.2f}'.format(fulcrum_ship_charges))
        st.write('Fulcrum Payments: ${:,.2f}'.format(fulcrum_ship_pmnts_23))

        st.divider()
        
        st.subheader('Total Charges: ${:,.2f}'.format(total_ship_cost))
        st.subheader('Total Payments: ${:,.2f}'.format(total_ship_pmnts))

        st.divider()
        
        for key, val in shipping_2023.items():
            st.subheader(key)
            st.write('Charges: ${:,.2f}'.format(val[0]))
            st.write('Payments: ${:,.2f}'.format(val[1]))
            st.write('FedEx Charges: ${:,.2f}'.format(val[2]))
            st.write('UPS Charges: ${:,.2f}'.format(val[3]))

    
    
    #st.write('{:.2f}%'.format(shipping_balance_calc(total_ship_cost, total_ship_pmnts)))
    
    #st.write(df_ac24_rev)
    #st.write(df_ac24_rev['January'].iloc[26])


if task_select == 'Customer Quote Reports':

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
    cust_won_total = 0
    cust_won_count = 0
    cust_lost_total = 0
    cust_lost_count = 0
    
    
    
    for customer in df_quotes.customer:

        if customer.upper() == quote_cust.upper():
    
            if df_quotes.iloc[idx].status == 'Won':
                cust_won_total += df_quotes.iloc[idx].total
                cust_won_count += 1
            if df_quotes.iloc[idx].status == 'Lost' or df_quotes.iloc[idx].status == 'Sent' or df_quotes.iloc[idx].status == 'Draft':
                cust_lost_total += df_quotes.iloc[idx].total
                cust_lost_count += 1
            
            cust_list_q.append('({})  {}  - ${:,.2f}  - {} - {}'.format(
                df_quotes.iloc[idx].number,
                df_quotes.iloc[idx].customer,
                df_quotes.iloc[idx].total,
                df_quotes.iloc[idx].date_created,
                df_quotes.iloc[idx].status))

        idx += 1

    
    col11, col12 = st.columns(2)
    if cust_won_count >= 1:
    
        with col11:
            st.header('')
            st.header('')
            st.header('')
            st.subheader('Quotes Won: ' + str(cust_won_count)) 
        with col11:
         
            st.subheader('For a Total of: ' + '${:,.2f}'.format(cust_won_total))
    if cust_lost_count >= 1:
        with col12:
            st.header('')
            st.header('')
            st.header('')
            st.subheader('Quotes Lost or Pending: ' + str(cust_lost_count))
        with col12:
    
            st.subheader('For a Total of: ' + '${:,.2f}'.format(cust_lost_total))

    if cust_lost_count >= 1 and cust_won_count >= 1:
        st.write('Conversion Percentage: ' + '{:,.2f}'.format((cust_won_count / (cust_lost_count + cust_won_count)) * 100) + '% of Quotes ' + '( {:,.2f}'.format((cust_won_total / (cust_lost_total + cust_won_total)) * 100) + '% of Potential Revenue )')
        st.divider()
        st.header('')
        
        for quote in cust_list_q:
            st.write(quote)


elif task_select == 'Customer Details':
    
    with st.container():
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
    
        
        #st.write(text_input)
        #text_input = text_input.lower()
    
        #if text_input.upper() not in df.customer.str.upper() and len(text_input) > 1:
            #possible_cust = []
        
            #for cust in df.customer:
                #if cust[:9].upper() == text_input[:9].upper() and cust[:10].upper() == text_input[:10].upper():
                    #text_input = cust
                    #break
                #if cust[:1].upper() == text_input[:1].upper() or cust[:2].lower() == text_input[:2].lower():
                    #if cust in possible_cust:
                        #pass
                    #else:
                        #possible_cust.append(cust)
            #if text_input == cust:
                #pass
            #else:
                #possible_cust = sort_by_match(possible_cust, text_input)
                #for custs in possible_cust:
                    #if custs[:2] == text_input[:2]:
                        #possible_cust.remove(custs)
                        #possible_cust.insert(0, custs)
                #for customer in possible_cust[:14]:
                    #st.write('Are you searching for - {} - ?'.format(customer))
        #st.write(text_input)
        
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
                    jet_list.append('|    {}    |     ({}x)    {}  --  {}'.format(
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
                    controller_list.append('|    {}    |     ({}x)    {}  --  {}'.format(
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
                    magic_list.append('|    {}    |     ({}x)    {}  --  {}'.format(
                        df.iloc[idx].sales_order, 
                        df.iloc[idx].quantity,
                        df.iloc[idx].item_sku,
                        df.iloc[idx].line_item))
                elif df.iloc[idx].item_sku[:5] == 'CC-CH':
                    hose_list.append('|    {}    |     ({}x)    {}  --  {}'.format(
                        df.iloc[idx].sales_order, 
                        df.iloc[idx].quantity,
                        df.iloc[idx].item_sku,
                        df.iloc[idx].line_item))
                elif df.iloc[idx].item_sku[:5] == 'CC-F-' or df.iloc[idx].item_sku[:5] == 'CC-AC' or df.iloc[idx].item_sku[:5] == 'CC-CT' or df.iloc[idx].item_sku[:5] == 'CC-WA':
                    fittings_accessories_list.append('|    {}    |     ({}x)    {}  --  {}'.format(
                        df.iloc[idx].sales_order, 
                        df.iloc[idx].quantity,
                        df.iloc[idx].item_sku,
                        df.iloc[idx].line_item))
                    if df.iloc[idx].item_sku[:9] == 'CC-AC-LA2':
                        cust_LED_cnt += df.iloc[idx].quantity                    
                elif df.iloc[idx].item_sku[:6] == 'CC-HCC' or df.iloc[idx].item_sku[:6] == 'Handhe':
                    handheld_list.append('|    {}    |     ({}x)    {}  --  {}'.format(
                        df.iloc[idx].sales_order, 
                        df.iloc[idx].quantity,
                        df.iloc[idx].item_sku,
                        df.iloc[idx].line_item))
                    cust_handheld_cnt += df.iloc[idx].quantity
                elif df.iloc[idx].item_sku[:5] == 'Shipp' or df.iloc[idx].item_sku[:5] == 'Overn' or df.iloc[idx].item_sku[:5] == 'CC-NP':
                    pass
                else:
                    misc_list.append('|    {}    |     ({}x)     {}  --  {}'.format(
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
        
        ### DISPLAY CUSTOMER SPENDING TRENDS AND TOTALS ###
        with col3:
            if spend_total_2023 + spend_total_2024 > 0:
                st.subheader('2023 Spending:')
                st.write('${:,.2f}'.format(spend_total_2023))
        with col4:
            if spend_total_2023 + spend_total_2024 > 0:
                st.subheader('2024 Spending:')
                st.write('${:,.2f}'.format(spend_total_2024))
        with col5:
            if spend_total_2023 + spend_total_2024 > 0:
                st.subheader('Total Spending:')
                total_spending = spend_total_2023 + spend_total_2024
                st.write('${:,.2f}'.format(total_spending))
        
        ### DISPLAY PRODUCT PURCHASE SUMMARIES FOR SELECTED CUSTOMER ###
        if len(text_input) > 1:
            st.subheader('Product Totals:')
            col6, col7, col8 = st.columns(3)
            with col6:
                for jet, totl in jet_totals_cust.items():
                    if totl > 0:
                        st.write(jet + ': ' + str(totl))
            with col7:
                for controller, totl in controller_totals_cust.items():
                    if totl > 0:
                        st.write(controller + ': ' + str(totl))
                if cust_handheld_cnt > 0:
                    st.write('Handhelds: ' + str(cust_handheld_cnt))
            with col8:
                if cust_LED_cnt > 0:
                    st.write('LED Attachment II: ' + str(cust_LED_cnt))
                if cust_RC_cnt > 0:
                    st.write('Road Cases: ' + str(cust_RC_cnt))
        
        ### DISPLAY CATEGORIES OF PRODUCTS PURCHASED BY SELECTED CUSTOMER ###
        if len(jet_list) >= 1:
            st.subheader('Stationary Jets:')
            for item in jet_list:
                st.write(item)
        if len(controller_list) >= 1:
            st.subheader('Controllers:')
            for item in controller_list:
                st.write(item)
        if len(handheld_list) >= 1:
            st.subheader('Handhelds:')
            for item in handheld_list:
                st.write(item)
        if len(hose_list) >= 1:
            st.subheader('Hoses:')
            for item in hose_list:
                st.write(item)
        if len(fittings_accessories_list) >= 1:
            st.subheader('Fittings & Accessories:')
            for item in fittings_accessories_list:
                st.write(item)
        if len(misc_list) >= 1:
            st.subheader('Misc:')
            for item in misc_list:
                st.write(item)
        if len(magic_list):
            st.subheader('Magic FX:')
            for item in magic_list:
                st.write(item)
    
    
    
    st.divider()
    
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


elif task_select == 'Product Sales':
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


###################################################################### MONTHLY SALES REPORTS ##############################################################################

elif task_select == 'Monthly Sales - V1':
    st.header('Monthly Sales')    
    mbd_display_sales = st.checkbox('Display Sales by Month')
    comp_display = st.checkbox('Show Comparison Column')
            
    ### REPLACE NULL VALUES WITH ZERO ###
        
    df_csv = df_csv.fillna(0)
    #st.write(df_csv)
    
    ### DEFINE A FUNCTION TO FORMAT MONTHLY SALES FOR CHART PLOTTING ###
    def format_for_chart_ms(dict):
        
        temp_dict = {'Months': months_x,
                    'Total Sales': []}
        
        for month, sales in dict.items():
            if len(temp_dict['Total Sales']) >= 12:
                pass
            else:
                temp_dict['Total Sales'].append(sales)
        df = pd.DataFrame(temp_dict)
        
        return df
    
    #st.write(format_for_chart(df_cntl23_unt.iloc[0]))
    
    
    ### SCRIPT TO PLOT BAR GRAPH FOR MONTHLY SALES ###
    
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
    
    
    col1, col2 = st.columns(2)
    
    ### CREATE YEAR SELECTION ###
    with col1:
        year_select = st.selectbox('Select Year:',
                         placeholder='Select Year',
                         options=['2023', '2024'])
    
    ### CREATE MONTHLY MULTISELECT ###
    
        month_range_sales = st.multiselect('Month Select:',
                                   placeholder='Select Months',
                                   options=months)
    
        #mbd_display_sales = st.checkbox('Display Sales by Month')
        
            
    ### CREATE LIST OF SELECTIONS ###
    
        df_csv_ts = df_csv.drop([1, 2, 4, 5, 7, 8])
        df_csv_ts = df_csv_ts.rename(index={0: '2022', 3: '2023', 6: '2024'})
        #st.write(df_csv_ts)
        #st.write(df_csv_ts['January'].iloc[2])
    
        idx_select = 0
        if year_select == '2023':
            idx_select += 1
        elif year_select == '2024':
            idx_select += 2
            
        s_tot = 0
    
        if month_range_sales == ['All']:
            month_range_sales = months_x
        avg_sales_per_month = {}
        for month in month_range_sales:
            try:
                avg_sales_per_month[month] = float(df_csv_ts[month].iloc[idx_select].strip('$'))
                #st.write(float(df_csv_ts[month].iloc[idx_select].strip('$')))
            except:
                avg_sales_per_month[month] = 0.0
            if df_csv_ts.at[year_select, month] == 0:
                pass
            else:
                if mbd_display_sales == True:
                    web_sales, web_percent, fulcrum_sales, fulcrum_percent = sales_channel(year_select, [month])
                    st.write(month + ': ' + '$' + '{:,.2f} - ({:.2f}% vs {:.2f}%)'.format(float(df_csv_ts.at[year_select, month].strip('$')), web_percent, fulcrum_percent))
                    
                s_tot += float(df_csv_ts.at[year_select, month].strip('$'))
        if len(month_range_sales) >= 1:
            s_tot_st = '{:,.2f}'.format(s_tot)

            
            if len(month_range_sales) > 1:
                web_sales, web_percent, fulcrum_sales, fulcrum_percent = sales_channel(year_select, month_range_sales)
                st.write('( - {:.2f}% Woocommerce vs {:.2f}% Fulcrum - )'.format(web_percent, fulcrum_percent))
                st.write('( - Average per month: ' + '$' + '{:,.2f}'.format(avg_month(avg_sales_per_month)) + ' - )')
            st.subheader('$' + s_tot_st)
            
            
            if month_range_sales == months_x:
                sales_per_month = format_for_chart_ms(avg_sales_per_month)
                if comp_display == False:
                    plot_bar_chart_ms(sales_per_month)
                else:
                    plot_bar_chart_ms_comp(sales_per_month)
    
        #s_tot_st = '{:,.2f}'.format(s_tot)
        
        #st.subheader('$' + s_tot_st)
        
    if comp_display == True:
        with col2:
        ### DUPLICATE SALES REPORTER FOR COMPARISON ###
        
            year_select_x = st.selectbox('Select Years:',
                             placeholder='Select Year',
                             options=years)
        
        ### CREATE MONTHLY MULTISELECT
        
            month_range_sales_x = st.multiselect('Month Selection:',
                                       placeholder='Select Months',
                                       options=months)
        
            #mbd_display_sales_x = st.checkbox('Display Sales by Months')
            
                
        ### CREATE LIST OF SELECTIONS ###
        
            df_csv_ts = df_csv.drop([1, 2, 4, 5, 7, 8])
            df_csv_ts = df_csv_ts.rename(index={0: '2022', 3: '2023', 6: '2024'})
        
            idx_select = 0
            if year_select_x == '2023':
                idx_select += 1
            elif year_select_x == '2024':
                idx_select += 2
                
            s_tot = 0
        
            if month_range_sales_x == ['All']:
                month_range_sales_x = months_x
            avg_sales_per_month = {}
            for month in month_range_sales_x:
                try:
                    avg_sales_per_month[month] = float(df_csv_ts[month].iloc[idx_select].strip('$'))
                    #st.write(float(df_csv_ts[month].iloc[idx_select].strip('$')))
                except:
                    avg_sales_per_month[month] = 0.0
    
                if df_csv_ts.at[year_select_x, month] == 0:
                    pass
                else:
                    if mbd_display_sales == True:
                        web_sales, web_percent, fulcrum_sales, fulcrum_percent = sales_channel(year_select_x, [month])
                        st.write(month + ': ' + '$' + '{:,.2f} - ({:.2f}% vs {:.2f}%)'.format(float(df_csv_ts.at[year_select_x, month].strip('$')), web_percent, fulcrum_percent))
                    s_tot += float(df_csv_ts.at[year_select_x, month].strip('$'))
            
            if len(month_range_sales_x) >= 1:
                
                s_tot_st = '{:,.2f}'.format(s_tot)
                
                if len(month_range_sales_x) > 1:
                    web_sales, web_percent, fulcrum_sales, fulcrum_percent = sales_channel(year_select_x, month_range_sales_x)
                    st.write('( - {:.2f}% Woocommerce vs {:.2f}% Fulcrum - )'.format(web_percent, fulcrum_percent))
                    st.write('( - Average per month: ' + '$' + '{:,.2f}'.format(avg_month(avg_sales_per_month)) + ' - )')
                st.subheader('$' + s_tot_st)
                if month_range_sales_x == months_x:
                    sales_per_month = format_for_chart_ms(avg_sales_per_month)
                    plot_bar_chart_ms_comp(sales_per_month)
                    
        

    

######################################################### CUSTOMER SPEND RANKINGS #######################################################################

### DEFINE A FUNCTION TO MAKE A LIST OF TUPLES OF A CUSTOMER AND THEIR SPENDING, LIMIT TO TOP 20 ###

    
def sort_top_20(dict, number):

    leaderboard_list = []
    
    for key, value in dict.items():
        if value >= 2500:
            leaderboard_list.append((key, value))
    

    sorted_leaderboard = sorted(leaderboard_list, key=itemgetter(1), reverse=True)

    return sorted_leaderboard[:number]


if task_select == 'Customer Spending Leaders':
    st.header('Customer Spending Leaderboards')
    
    spend_year = st.selectbox('Choose Year', 
                             ['2023', '2024'])
    
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
    
    
    
  













