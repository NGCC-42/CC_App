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




### LOAD FILES
#sod_ss = 'MASTER DATA 2.17.25.xlsx'
sod_ss = 'SOD 2.21.25.xlsx'

# Replace with your GitHub raw URL
#url = "https://raw.githubusercontent.com/NGCC-42/CC_App/SOD_Master.csv"

# Read the CSV into a DataFrame
#df = pd.read_csv(url)

# Display the first few rows
#print(df.head())

hist_ss = 'CC Historical Sales 2.7.xlsx'

hsd_ss = 'HSD 11.8.24.xlsx'

quote_ss = 'Quote Report 1.28.25.xlsx'

#sales_sum_csv = 'Total Summary-2022 - Present.csv'

shipstat_ss_24 = '2024 SR 11.01.24.xlsx'
shipstat_ss_23 = '2023 SR.xlsx'

#prod_sales = 'Product Sales Data.xlsx'

wholesale_cust = 'wholesale_customers.xlsx'

cogs_ss = 'COGS 1.29.25a.xlsx'

qb_ss = 'QB Transactions.xlsx'

### LOAD SHEETS FROM PRODUCT SUMMARY

#acc_2024 = 'Accessories 2024'
#cntl_2024 = 'Controllers Sales 2024'
#jet_2024 = 'Jet Sales 2024'
#hh_2024 = 'Handheld Sales 2024'
#hose_2024 = 'Hose Sales 2024'

#acc_2023 = 'Accessories 2023'
#cntl_2023 = 'Controllers Sales 2023'
#jet_2023 = 'Jet Sales 2023'
#hh_2023 = 'Handheld Sales 2023'
#hose_2023 = 'Hose Sales 2023'

### LOAD SHEETS FROM SALES SUMMARY

#total_sum = 'Total Summary'

### LOAD DATAFRAME(S) (RETAIN FORMATTING IN XLSX)

@st.cache_data
def create_dataframe(ss):

	df = pd.read_excel(ss,
					  dtype=object,
					  header=0, 
                      keep_default_na=False)
	return df


df = create_dataframe(sod_ss)

df_hist = pd.read_excel(hist_ss, dtype=object, header=0)
df_hist.fillna(0, inplace=True)

df_quotes = create_dataframe(quote_ss)

df_shipstat_24 = create_dataframe(shipstat_ss_24)

df_shipstat_23 = create_dataframe(shipstat_ss_23)

df_hsd = create_dataframe(hsd_ss)

df_wholesale = create_dataframe(wholesale_cust)

df_cogs = create_dataframe(cogs_ss)

df_qb = pd.read_excel(qb_ss,
                      #dtype=object,
                      header=0,
                      keep_default_na=True)

@st.cache_data
def gen_ws_list():
    wholesale_list = []
    for ws in df_wholesale.name:
        wholesale_list.append(ws)
    return wholesale_list

wholesale_list = gen_ws_list()

### STRIP UNUSED COLUMN ###

missing_cols = [col for col in ['Ordered Week', 'Customer Item Name'] if col not in df.columns]
if missing_cols:
    print(f"Warning: The following columns are missing and cannot be dropped: {missing_cols}")
else:
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
df['total_line_item_spend'] = df['total_line_item_spend'].astype('float32')
#df['customer'] = df['customer'].str.title()
#df_hist['customer'] = df_hist['customer'].str.title()
df_hist = df_hist[~df_hist['customer'].str.contains('AMAZON SALES', na=False)]
df_hist = df_hist[~df_hist['customer'].str.contains('AMAZON', na=False)]
df_hist = df_hist[~df_hist['customer'].str.contains('Amazon', na=False)]

df_qb['customer'] = df_qb['customer'].str.title()
df_qb = df_qb[~df_qb['customer'].str.contains('Total', na=False)]
df_qb = df_qb[~df_qb["order_num"].str.contains("F", na=False)]
df_qb = df_qb[~df_qb["order_num"].str.contains("CF", na=False)]
df_qb = df_qb[~df_qb["order_num"].str.contains("(I2G)", na=False)]
df_qb = df_qb[~df_qb["order_num"].str.contains("ch_", na=False)]
df_qb['customer'] = df_qb['customer'].ffill()
df_qb.dropna(subset=['date'], inplace=True)
df_qb.dropna(subset=['total'], inplace=True)
df_qb.reset_index(drop=True, inplace=True)

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

df_cogs.rename(columns={
                    'Item Number/Revision':'item',
                    'Invoice Number':'invoice',
                    'Status':'status',
                    'Source':'sales_order',
                    'Customer':'customer',
                    'Invoice Issue Date':'issue_date',
                    'Invoice Paid Date':'paid_date',
                    'Invoice Quantity':'quantity',
                    'Material Value':'material_value',
                    'Labor Value': 'labor_value',
                    'Outside Processing Value': 'processing_value',
                    'Machine Value': 'machine_value',
                    'Total Cost': 'total_cost',
                    'Total Price': 'total_price',
                    'Unit Price': 'unit_price'},
                    inplace=True)  

df_cogs['total_cost'] = df_cogs['total_cost'].astype('float32')
df_cogs['total_price'] = df_cogs['total_price'].astype('float32')
df_cogs['unit_price'] = df_cogs['unit_price'].astype('float32')




### DEFINE A FUNCTION TO CORRECT NAME DISCRPANCIES IN SOD
@st.cache_data
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
    df.replace('Adam Stipe', 'Special Event Services (SES)', inplace=True)
    df.replace('Michael Brammer', 'Special Event Services (SES)', inplace=True)
    df.replace('ffp effects inc c/o Third Encore', 'FFP FX', inplace=True)
    df.replace('Disney Worldwide Services, Inc', 'Disney Cruise Line', inplace=True)
    df.replace('Jeff Meuzelaar', 'Jeff Meuzelaar / Pinnacle Productions', inplace=True)
    df.replace('Ernesto Blanco', 'Ernesto Koncept Systems', inplace=True)
    df.replace('Justin Jenkins', 'Justin Jenkins / Creative Production & Design', inplace=True)
    df.replace('Creative Production & Design', 'Justin Jenkins / Creative Production & Design', inplace=True)
    df.replace('Andrew Pla / Rock The House', 'Steve Tanruther / Rock The House', inplace=True)
    df.replace('Ryan Konikoff / ROCK THE HOUSE', 'Steve Tanruther / Rock The House', inplace=True)
    df.replace('Cole M. Blessinger', 'Cole Blessinger', inplace=True)
    df.replace('Parti Line International, LLC', 'Fluttter Feti', inplace=True)
    df.replace('MICHAEL MELICE', 'Michael Melice', inplace=True)
    df.replace('Michael Brammer / Special Event Services', 'Special Event Services (SES)', inplace=True)
    df.replace('Dios Vazquez ', 'Dios Vazquez', inplace=True)
    df.replace('Brilliant Stages Ltd T/A TAIT', 'Brilliant Stages', inplace=True)
    df.replace('San Clemente High School Attn Matt Reid', 'San Clemente High School', inplace=True)
    df.replace('Anita Chandra / ESP Gaming', 'Anita Chandra', inplace=True)
    df.replace('randy hood', 'Randy Hood', inplace=True)
    df.replace('Randy Hood / Hood And Associates / talent', 'Randy Hood', inplace=True)
    df.replace('Steve VanderHeyden (Band Ayd Event Group)', 'Steve Vanderheyden / Band Ayd Event Group', inplace=True)
    df.replace('Steve VanderHeyden', 'Steve Vanderheyden / Band Ayd Event Group', inplace=True)
    df.replace('Kyle Kelly', 'Special FX Rentals', inplace=True)
    df.replace('MARIE COVELLI', 'Marie Covelli', inplace=True)
    df.replace('Frank Brown', 'Frank Brown / Night Nation Run', inplace=True)
    df.replace('Matt Spencer / SDCM', 'Matt Spencer', inplace=True)
    df.replace('Solotech U.S. Corporation', 'Solotech', inplace=True)
    df.replace('Michael Bedkowski', 'POSH DJs', inplace=True)
    df.replace('Kyle Jonas', 'POSH DJs', inplace=True)
    df.replace('Evan Ruga', 'POSH DJs', inplace=True)
    df.replace('Sean Devaney', 'POSH DJs', inplace=True)
    df.replace('Brian Uychich', 'POSH DJs', inplace=True)
    df.replace('Omar Sánchez Jiménez / Pyrofetti FX', 'Pyrofetti Efectos Especiales SA de CV', inplace=True)
    df.replace('Omar Sánchez Jiménez / Pyrofetti Fx', 'Pyrofetti Efectos Especiales SA de CV', inplace=True)
    df.replace('Omar Jimenez / Pyrofetti efectos especiales', 'Pyrofetti Efectos Especiales SA de CV', inplace=True)
    df.replace('Oscar Jimenez / Pyrofetti Fx', 'Pyrofetti Efectos Especiales SA de CV', inplace=True)
    df.replace('Gilbert / Pyrotec Sa', 'Pyrofetti Efectos Especiales SA de CV', inplace=True)
    df.replace('Gilbert / Pyrotec S.A.', 'Pyrofetti Efectos Especiales SA de CV', inplace=True)
    df.replace('Gilbert Salazar / Pyrotec S.A.', 'Pyrofetti Efectos Especiales SA de CV', inplace=True)
    df.replace('Image SFX (Gordo)', 'Image SFX', inplace=True)
    df.replace('Image SFX (Drake 6 Jets)', 'Image SFX', inplace=True)
    df.replace('Image SFX (Drake 18 Jets)', 'Image SFX', inplace=True)
    df.replace('Image SFX (Water Cannon Deposit)', 'Image SFX', inplace=True)
    df.replace('Image SFX (Water Cannon Deposit)', 'Image SFX', inplace=True)
    df.replace('Shadow Mountain Productions', 'Tanner Valerio', inplace=True)
    df.replace('Tanner Valerio / Shadow Mountain Productions', 'Tanner Valerio', inplace=True)
    df.replace('Tanner Valero', 'Tanner Valerio', inplace=True)
    df.replace('Tanner Valerio / Shadow Mountain Productions (GEAR TO RETURN)', 'Tanner Valerio', inplace=True)
    df.replace('Tanner Valerio / Shadow Mountain productions (GEAR TO RETURN)', 'Tanner Valerio', inplace=True)
    df.replace('Tanner Valerio / Shadow Mountain productions', 'Tanner Valerio', inplace=True)
    df.replace('Blast Pyrotechnics', 'Blaso Pyrotechnics', inplace=True)
    df.replace('Pyrotecnico ', 'Pyrotecnico', inplace=True)
    df.replace('PYROTECNICO ', 'PYROTECNICO', inplace=True)
    df.replace('Pyrotecnico', 'PYROTECNICO', inplace=True)
    df.replace('Pyrotek FX ', 'Pyrotek FX', inplace=True)
    df.replace('Pyrotek Fx ', 'Pyrotek Fx', inplace=True)
    df.replace('Pyro Spectacular Industries', 'Pyro Spectaculars Industries, Inc.', inplace=True)
    df.replace('SK PYRO SPECIAL EFFECTS', 'SK Pyro Special Effects', inplace=True)
    df.replace('Illuminated Integration / Nashville Live', 'Illuminated Integration', inplace=True)
    df.replace('edgar guerrero', 'Edgar Guerrero', inplace=True)
    df.replace('HEDGER SANCHEZ', 'Hedger Sanchez', inplace=True)
    df.replace('Gear Club Direct Pro - Luis Garcia', 'Gear Club Direct', inplace=True)
    df.replace('edgar Rojas', 'Edgar Rojas', inplace=True)
    df.replace('Grant ashling', 'Grant Ashling', inplace=True)
    df.replace('Sebastian Gomez', 'Sebastian Gómez', inplace=True)
    df.replace('Ravinder singh', 'Ravinder Singh', inplace=True)
    df.replace('Eric Swanson / Slightly Stoopid', 'Slightly Stoopid', inplace=True)
    df.replace('the bouffants / David Griffin', 'David Griffin', inplace=True)
    df.replace('Anthony Mendoza (Infusion Lounge)', 'Anthony Mendoza', inplace=True)
    df.replace('The Party Stage Company / Ryan Smith', 'Ryan Smith', inplace=True)
    df.replace('Rafael Urban (Re-ship charge)', 'Rafael Urban', inplace=True)
    df.replace('California Pro Sound And Light', 'California Pro Sound and Light', inplace=True)
    df.replace('Max Moussier / Sound Miami Nightclub', 'Max Moussier', inplace=True)
    df.replace('Tony Tannous (Sound Agents Australia)', 'Tony Tannous', inplace=True)
    df.replace('Carlos BURGOS', 'Carlos Burgos', inplace=True)
    df.replace('Jonathan / Visual Edge', 'Visual Edge', inplace=True)
    df.replace('Justin Jenkins / Creative Production & Design', 'Justin Jenkins', inplace=True)
    df.replace('David Belogolovsky (6 solenoids)', 'David Belogolovsky', inplace=True)
    df.replace('amar gill', 'Amar Gill', inplace=True)
    df.replace('ARIEL MARTINEZ', 'Ariel Martinez', inplace=True)
    df.replace('JOSE ANTONIO MAR HERNANDEZ', 'Jose Antonio Mar Hernandez', inplace=True)
    df.replace('Alma Delia Rivero Sánchez', 'Alma Delia Rivero Sanchez', inplace=True)
    df.replace('PROMEDSA', 'Promedsa', inplace=True)
    df.replace('JABARI JOHNSON', 'Jabari Johnson', inplace=True)
    df.replace('Paul Klassenn / Laird FX', 'Paul Klaassen / Laird FX', inplace=True)
    df.replace('Parag Enterprises / Divine FX', 'Divine FX', inplace=True)
    df.replace('Romin Zandi ', 'Romin Zandi', inplace=True)
    df.replace('Romin Zandi (Personal)', 'Romin Zandi', inplace=True)
    df.replace('cesar palomino', 'Cesar Palomino', inplace=True)
    df.replace('zcibeiro Medina', 'Zcibeiro Medina', inplace=True)
    df.replace('Gregory Lomangino', 'Greg Lomangino', inplace=True)
    df.replace('Rory McElroy ', 'Rory McElroy', inplace=True)
    df.replace('Ronald Michel ', 'Ronald Michel', inplace=True)
    df.replace('Roland Mendoza', 'Rolando Mendoza', inplace=True)
    df.replace('rolando mendoza', 'Rolando Mendoza', inplace=True)
    df.replace('Rochester Red Wings / Morrie', 'Morrie Silver', inplace=True)
    df.replace('ROBERT SIMPSON', 'Robert Simpson', inplace=True)
    df.replace('ER Prouctions (Device programmer)', 'ER Productions', inplace=True)
    df.replace('University of Wyoming / Shelley', 'University of Wyoming', inplace=True)
    df.replace('Mario moreno', 'Mario Moreno', inplace=True)
    df.replace('gregory morris', 'Gregory Morris', inplace=True)
    df.replace('preston M Murray', 'Preston M Murray', inplace=True)
    df.replace('Jorge Pulido Ayala / MIA Eventos', 'Jorge Ayala', inplace=True)
    df.replace('Jorge Pulido Ayala', 'Jorge Ayala', inplace=True)
    df.replace('Jorge Ayala / MIA Eventos', 'Jorge Ayala', inplace=True)
    df.replace('Garth Hoffmann ', 'Garth Hoffmann', inplace=True)
    df.replace('Ernesto Koncept Systems / Khalil', 'Ernesto Koncept Systems', inplace=True)
    df.replace('jose ramos', 'Jose Ramos', inplace=True)
    df.replace('RAMON', 'Ramon', inplace=True)
    df.replace('4WALL ENTERTAINMENT, INC. ', '4WALL ENTERTAINMENT, INC.', inplace=True)
    df.replace('alex allen', 'Alex Allen', inplace=True)
    df.replace('Advanced Entertainment Services ', 'Advanced Entertainment Services', inplace=True)
    df.replace('adrian zerla', 'Adrian Zerla', inplace=True)
    
    
    
    return df

df = fix_names(df)
df_hist = fix_names(df_hist)
df_qb = fix_names(df_qb)

### CREATE A LIST OF UNIQUE CUSTOMERS ###
unique_customer_list = df.customer.unique().tolist()
hist_customer_list = df_hist['customer'].unique()
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

### DEFINE A FUNCTION TO CONVERT MONTH STRING TO NUMERICAL 
def month_to_num(month):
    months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
    ]
    return (months.index(month) + 1)
        

def num_to_month(month_num):
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    return months[month_num - 1]


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
    # Ensure 'order_date' is in datetime format
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    # Initialize sales dictionary
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    sales_dict = {month: [0, 0] for month in months}
    
    # Filter dataset to the required year
    df = df[df["order_date"].dt.year == year]

    # Convert order_date to month names
    df["month"] = df["order_date"].dt.month.map(lambda x: months[x - 1])

    # Determine if the customer is wholesale
    df["is_wholesale"] = df["customer"].isin(wholesale_list)

    # Group by month
    grouped = df.groupby("month")

    for month, group in grouped:
        # Sum of sales for wholesale customers
        sales_dict[month][0] = group.loc[group["is_wholesale"], "total_line_item_spend"].sum()
        # Sum of sales for non-wholesale customers
        sales_dict[month][1] = group.loc[~group["is_wholesale"], "total_line_item_spend"].sum()

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
    
        if two_years_ago.date() >= order_date.date() >= beginning_of_year(two_years_ago).date():
            if cust in wholesale_list:
                sales_dict_minus2[month][0] += df.iloc[idx].total_line_item_spend
            else:
                sales_dict_minus2[month][1] += df.iloc[idx].total_line_item_spend 
                
        elif one_year_ago.date() >= order_date.date() >= beginning_of_year(one_year_ago).date():
            if cust in wholesale_list:
                sales_dict_minus1[month][0] += df.iloc[idx].total_line_item_spend
            else:
                sales_dict_minus1[month][1] += df.iloc[idx].total_line_item_spend 
                
        elif today.date() >= order_date.date() >= beginning_of_year(today).date():
            if cust in wholesale_list:
                sales_dict[month][0] += df.iloc[idx].total_line_item_spend
            else:
                sales_dict[month][1] += df.iloc[idx].total_line_item_spend 
                
        idx += 1
	
    return sales_dict, sales_dict_minus1, sales_dict_minus2

	
### FOR DASHBOARD ###  
@st.cache_data
def get_monthly_sales_v2(df, year):
    # Ensure 'order_date' is in datetime format
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    # Initialize sales dictionary
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    sales_dict = {month: [[0, 0], [0, 0], [0]] for month in months}
    
    # Filter dataset to the required year
    df = df[df["order_date"].dt.year == year]
    
    # Convert order_date to month names
    df["month"] = df["order_date"].dt.month.map(lambda x: months[x - 1])
    
    # Determine if the sale is from channel "F"
    df["is_F"] = df["channel"].str.startswith("F")

    # Identify Magic/MFX items
    df["is_magic"] = df["line_item"].str.startswith(("Magic", "MFX")) | df["item_sku"].str.startswith(("Magic", "MFX"))

    # Group by month
    for month, group in df.groupby("month"):
        # Total spend for channel "F"
        sales_dict[month][0][0] = group.loc[group["is_F"], "total_line_item_spend"].sum()
        # Count of unique sales orders for channel "F"
        sales_dict[month][0][1] = group.loc[group["is_F"], "sales_order"].nunique()
        
        # Total spend for non-"F" channels
        sales_dict[month][1][0] = group.loc[~group["is_F"], "total_line_item_spend"].sum()
        # Count of unique sales orders for non-"F" channels
        sales_dict[month][1][1] = group.loc[~group["is_F"], "sales_order"].nunique()
        
        # Total spend for Magic/MFX items
        sales_dict[month][2][0] = group.loc[group["is_magic"], "total_line_item_spend"].sum()

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
            if two_years_ago.date() >= order_date.date() >= beginning_of_year(two_years_ago).date():
                sales_dict_minus2[month][0][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders_minus2:
                    sales_dict_minus2[month][0][1] += 1
                    unique_sales_orders_minus2.append(sale)
                    
            elif one_year_ago.date() >= order_date.date() >= beginning_of_year(one_year_ago).date():
                sales_dict_minus1[month][0][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders_minus1:
                    sales_dict_minus1[month][0][1] += 1
                    unique_sales_orders_minus1.append(sale)
                    
            elif today.date() >= order_date.date() >= beginning_of_year(today).date():
                sales_dict[month][0][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders:
                    sales_dict[month][0][1] += 1
                    unique_sales_orders.append(sale)

        else:
            if two_years_ago.date() >= order_date.date() >= beginning_of_year(two_years_ago).date():
                sales_dict_minus2[month][1][0] += df.iloc[idx].total_line_item_spend 
                if df.iloc[idx].line_item[:5] == 'Magic' or df.iloc[idx].line_item[:3] == 'MFX':
                    sales_dict_minus2[month][2][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders_minus2:
                    sales_dict_minus2[month][1][1] += 1
                    unique_sales_orders_minus2.append(sale)
                    
            elif one_year_ago.date() >= order_date.date() >= beginning_of_year(one_year_ago).date():
                sales_dict_minus1[month][1][0] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].line_item[:5] == 'Magic' or df.iloc[idx].line_item[:3] == 'MFX':
                    sales_dict_minus1[month][2][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders_minus1:
                    sales_dict_minus1[month][1][1] += 1
                    unique_sales_orders_minus1.append(sale)
                    
            elif today.date() >= order_date.date() >= beginning_of_year(today).date():
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
    magic_sales = 0
    num_months = 0

    # Determine which months to iterate over
    if months == ['All']:
        selected_items = sales_dict.items()
    else:
        selected_items = ((m, sales) for m, sales in sales_dict.items() if m in months)

    # Loop over the selected months
    for m, sales in selected_items:
        web      = sales[0][0]
        fulcrum  = sales[1][0]
        magic    = sales[2][0]
        month_total = web + fulcrum

        total_sales   += month_total
        total_web     += web
        total_fulcrum += fulcrum
        magic_sales   += magic

        # Only count the month if total sales are at least 100
        if month_total >= 100:
            num_months += 1

    # Compute average monthly sales (if no month qualifies, set average to 0)
    avg_month = total_sales / num_months if num_months else 0

    # Compute percentages using your helper function (assumed to be defined elsewhere)
    total_web_perc     = percent_of_sales(total_web, total_fulcrum)
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
	).properties(height=500, width=700).configure_mark(
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
    if month == 'All':
        # Sum the wholesale and non-wholesale values over all months using generator expressions.
        sales_sum_web      = sum(sales[0][0] for sales in sales_dict.values())
        sales_sum_fulcrum  = sum(sales[1][0] for sales in sales_dict.values())
        total_trans_web    = sum(sales[0][1] for sales in sales_dict.values())
        total_trans_fulcrum= sum(sales[1][1] for sales in sales_dict.values())
    else:
        # For a specific month, extract values directly
        sales_sum_web       = sales_dict[month][0][0]
        sales_sum_fulcrum   = sales_dict[month][1][0]
        total_trans_web     = sales_dict[month][0][1]
        total_trans_fulcrum = sales_dict[month][1][1]
    
    sales_sum   = sales_sum_web + sales_sum_fulcrum
    total_trans = total_trans_web + total_trans_fulcrum

    # Calculate averages using inline conditional expressions
    avg_order         = sales_sum / total_trans if total_trans else 0
    avg_order_web     = sales_sum_web / total_trans_web if total_trans_web else 0
    avg_order_fulcrum = sales_sum_fulcrum / total_trans_fulcrum if total_trans_fulcrum else 0

    return [avg_order_web, avg_order_fulcrum, avg_order,
            sales_sum_web, sales_sum_fulcrum, sales_sum,
            total_trans_web, total_trans_fulcrum, total_trans]
            
            





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
    for line in df.item_sku:

        if df.iloc[idx].order_date.year == 2025:
            if line[:16] == 'CC-HCCMKII-08-NC':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_25[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-08-TC':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_25[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-NC':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_25[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-TC':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_25[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
                
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

    # DEFINE TARGET YEARS
    target_years = [2023, 2024, 2025]

    # DEFINE TARGET PRODUCTS    
    products = ['2FT MFD', '3.5FT MFD', '5FT MFD', '5FT STD', '5FT DSY', '5FT EXT', '8FT STD', '8FT DSY', '8FT EXT', '15FT STD', '15FT DSY', '15FT EXT', '25FT STD', '25FT DSY', '25FT EXT', '35FT STD', '35FT DSY', '35FT EXT', '50FT STD', '50FT EXT', '100FT STD', 'CUSTOM']

    # DEFINE TARGET PRODUCT SKUS
    conditions = [
        df['item_sku'].str.startswith('CC-CH-02', na=False),
        df['item_sku'].str.startswith('CC-CH-03', na=False),
        df['item_sku'].str.startswith('CC-CH-05-M', na=False),
        df['item_sku'].str.startswith('CC-CH-05-S', na=False),
        df['item_sku'].str.startswith('CC-CH-05-D', na=False),
        df['item_sku'].str.startswith('CC-CH-05-E', na=False),
        df['item_sku'].str.startswith('CC-CH-08-S', na=False),
        df['item_sku'].str.startswith('CC-CH-08-D', na=False),
        df['item_sku'].str.startswith('CC-CH-08-E', na=False),
        df['item_sku'].str.startswith('CC-CH-15-S', na=False),
        df['item_sku'].str.startswith('CC-CH-15-D', na=False),
        df['item_sku'].str.startswith('CC-CH-15-E', na=False),
        df['item_sku'].str.startswith('CC-CH-25-S', na=False),
        df['item_sku'].str.startswith('CC-CH-25-D', na=False),
        df['item_sku'].str.startswith('CC-CH-25-E', na=False),
        df['item_sku'].str.startswith('CC-CH-35-S', na=False),
        df['item_sku'].str.startswith('CC-CH-35-D', na=False),
        df['item_sku'].str.startswith('CC-CH-35-E', na=False),
        df['item_sku'].str.startswith('CC-CH-50-S', na=False),
        df['item_sku'].str.startswith('CC-CH-50-E', na=False),
        df['item_sku'].str.startswith('CC-CH-100-S', na=False),
        df['item_sku'].str.startswith('CC-CH-XX', na=False),
    ]

    # GENERATE A NEW COLUMN 'PRODUCT' BASED ON CONDITIONS IN A COPY OF THE DATAFRAME
    df = df.copy()
    df['product'] = np.select(conditions, products, default=None)

    # REMOVE ROWS THAT DON'T MEET CONDITIONS
    df = df[df['product'].notnull()]

    # ENSURE ORDER_DATE IS DATETIME, CREATE YEAR AND MONTH COLUMNS
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df['year'] = df['order_date'].dt.year
    df['month'] = df['order_date'].dt.month.apply(lambda m: months_x[m - 1])

    # CREATE A WHOLESALE FLAG COLUMN
    df['wholesale'] = df['customer'].isin(wholesale_list)

    # GROUP BY YEAR, MONTH, AND PRODUCT FOR OVERALL TOTALS
    overall = df.groupby(['year', 'month', 'product']).agg(qty_sum=('quantity', 'sum'), 
                                                           spend_sum=('total_line_item_spend', 'sum')
                                                          ).reset_index()

    # GROUP BY YEAR, MONTH AND PRODUCT FOR WHOLESALE RESULTS
    #ws_group = df[df['wholesale']].groupby(['year', 'month', 'product'])['quantity'].sum().reset_index()
    #ws_group = ws_group.rename(columns={'quantity': 'wholesale_qty'})

    # MERGE OVERALL AND WHOLESALE RESULTS
    #merged = pd.merge(overall, ws_group, on=['year', 'month', 'product'], how='left')
    #merged['wholesale_qty'] = merged['wholesale_qty'].fillna(0)

    # BUILD A RESULT DICT FOR EACH TARGET YEAR
    result = {}

    for year in target_years:
        # PREFILL WITH DEFAULT VALUES FOR EACH MONTH AND PRODUCT
        year_dict = {month: {'2FT MFD': [0,0], '3.5FT MFD': [0,0], '5FT MFD': [0,0], '5FT STD': [0,0], '5FT DSY': [0,0], 
                            '5FT EXT': [0,0], '8FT STD': [0,0], '8FT DSY': [0,0], '8FT EXT': [0,0], '15FT STD': [0,0], 
                            '15FT DSY': [0,0], '15FT EXT': [0,0], '25FT STD': [0,0], '25FT DSY': [0,0], '25FT EXT': [0,0], 
                            '35FT STD': [0,0], '35FT DSY': [0,0], '35FT EXT': [0,0], '50FT STD': [0,0], '50FT EXT': [0,0],
                            '100FT STD': [0,0], 'CUSTOM': [0,0]}
                    for month in months_x}
        
        sub = overall[overall['year'] == year]
        for _, row in sub.iterrows():
            month = row['month']
            product = row['product']
            year_dict[month][product] = [row['qty_sum'], row['spend_sum']]
        result[year] = year_dict

    return result.get(2023), result.get(2024), result.get(2025)


@st.cache_data
def extract_acc_data(df):
    # Define month names.
    months_x = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]
    target_years = [2023, 2024, 2025]
    
    # Define the products that are handled uniformly (their keys and the expected substring lengths).
    # For these, the default accumulator is a list: [quantity, total_line_item_spend]
    simple_products = {
        'CC-AC-CCL': 9,
        'CC-AC-CTS': 9,
        'CC-F-DCHA': 9,
        'CC-F-HEA': 8,
        'CC-AC-RAA': 9,
        'CC-AC-4PM': 9,
        'CC-F-MFDCGAJIC': 14,
        ' CC-AC-CGAJIC-SET': 17,  # note the leading space if that is intentional
        'CC-CTC-20': 9,
        'CC-CTC-50': 9,
        'CC-AC-TC': 8,
        'CC-VV-KIT': 9,
        'CC-AC-LA2': 9,
        'CC-SW-05': 8,
        'CC-NPTC-06-STD': 14,
        'CC-NPTC-10-DSY': 14,
        'CC-NPTC-15-DSY': 14,
        'CC-NPTC-25-DSY': 14
    }
    # For "CC-RC-2430", we need a 5-element list:
    rc_key = 'CC-RC-2430'
    # For rc, the base case will update indices 0 (qty) and 1 (spend). 
    # Then there are special cases for:
    #   - 'CC-RC-2430-PJI'  -> index 2 (quantity)
    #   - 'CC-RC-2430-LAI'  -> index 3 (quantity)
    #   - 'CC-RC-2430-QJF'  -> index 4 (quantity)
    
    # Preinitialize dictionaries for each target year.
    results = {yr: {month: {} for month in months_x} for yr in target_years}
    for yr in target_years:
        for m in months_x:
            # Fill in simple product keys with [0,0]
            for prod in simple_products.keys():
                results[yr][m][prod] = [0, 0]
            # Initialize the special product "CC-RC-2430" with a 5-element list.
            results[yr][m][rc_key] = [0, 0, 0, 0, 0]
    
    # Ensure order_date is datetime and create year and month columns.
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month.apply(lambda m: months_x[m - 1])
    
    # Process each target year separately.
    for yr in target_years:
        df_year = df[df["year"] == yr]
        
        # Process simple products.
        for prod, sig_len in simple_products.items():
            # Create a boolean mask: rows where the line_item starts with prod (using sig_len)
            mask = df_year["item_sku"].str[:sig_len] == prod
            if mask.sum() == 0:
                continue
            # Group by month
            grp = df_year.loc[mask].groupby("month").agg({
                "quantity": "sum",
                "total_line_item_spend": "sum"
            })
            for month, row in grp.iterrows():
                results[yr][month][prod][0] = row["quantity"]
                results[yr][month][prod][1] = row["total_line_item_spend"]
        
        # Process the special product "CC-RC-2430".
        df_rc = df_year[df_year["item_sku"].str.startswith("CC-RC", na=False)]
        if not df_rc.empty:
            # Base mask for rows related to "CC-RC-2430" (we assume they start with that string)
            base_mask = df_rc["line_item"].str.startswith(rc_key, na=False)
            grp_base = df_rc.loc[base_mask].groupby("month").agg({
                "quantity": "sum",
                "total_line_item_spend": "sum"
            })
            for month, row in grp_base.iterrows():
                # For the base case, update indices 0 and 1.
                results[yr][month][rc_key][0] = row["quantity"]
                results[yr][month][rc_key][1] = row["total_line_item_spend"]
            
            # Now handle special cases:
            # PJI, LAI, QJF - these are based on line_item starting with these exact strings.
            for suffix, idx_to_update in [('CC-RC-2430-PJI', 2),
                                          ('CC-RC-2430-LAI', 3),
                                          ('CC-RC-2430-QJF', 4)]:
                mask_special = df_rc["item_sku"].str.startswith(suffix, na=False)
                grp_special = df_rc.loc[mask_special].groupby("month")["quantity"].sum()
                for month, qty in grp_special.items():
                    results[yr][month][rc_key][idx_to_update] = qty
                    
    # Return dictionaries for each year: 2023, 2024, 2025.
    return results[2023], results[2024], results[2025]

@st.cache_data
def extract_control_data(df):
    # Define month names if not already defined
    months_x = ["January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"]
    
    # Define product mapping using the prefixes in line_item.
    conditions = [
        df["item_sku"].str.startswith("CC-TB-3", na=False),
        df["item_sku"].str.startswith("CC-SS-3", na=False),
        df["item_sku"].str.startswith("CC-SM", na=False),
    ]
    choices = ["The Button", "Shostarter", "Shomaster"]
    
    # Create a new column "product" based on the above conditions.
    df = df.copy()
    df["product"] = np.select(conditions, choices, default=None)
    # Remove rows that are not one of our desired product types.
    df = df[df["product"].notnull()]
    
    # Ensure order_date is datetime and add year and month columns.
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month.apply(lambda m: months_x[m - 1])
    
    # Create a wholesale flag column.
    df["wholesale"] = df["customer"].isin(wholesale_list)
    
    # Group by year, month, and product for overall totals.
    overall = df.groupby(["year", "month", "product"]).agg(
        qty_sum=("quantity", "sum"),
        spend_sum=("total_line_item_spend", "sum")
    ).reset_index()
    
    # Group by year, month, and product for wholesale only quantities.
    wholesale_grp = df[df["wholesale"]].groupby(["year", "month", "product"])["quantity"].sum().reset_index()
    wholesale_grp = wholesale_grp.rename(columns={"quantity": "wholesale_qty"})
    
    # Merge the overall and wholesale results.
    merged = pd.merge(overall, wholesale_grp, on=["year", "month", "product"], how="left")
    merged["wholesale_qty"] = merged["wholesale_qty"].fillna(0)
    
    # Build a result dictionary for each target year.
    result = {}
    # Target years: 2023, 2024, and 2025.
    for y in [2023, 2024, 2025]:
        # Pre-fill with default values for every month and each product.
        year_dict = {month: {"The Button": [0, 0, 0], "Shostarter": [0, 0, 0],
                             "Shomaster": [0, 0, 0]}
                     for month in months_x}
        sub = merged[merged["year"] == y]
        for _, row in sub.iterrows():
            month = row["month"]
            product = row["product"]
            # Update the values: [total_quantity, total_spend, wholesale_quantity]
            year_dict[month][product] = [row["qty_sum"], row["spend_sum"], row["wholesale_qty"]]
        result[y] = year_dict
    
    # Return dictionaries for the target years.
    return result.get(2023), result.get(2024), result.get(2025)



@st.cache_data
def extract_jet_data(df):
    # Define month names if not already defined
    months_x = ["January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"]
    
    # Define product mapping using the prefixes in line_item.
    conditions = [
        df["item_sku"].str.startswith("CC-PRO", na=False),
        df["item_sku"].str.startswith("CC-QJ", na=False),
        df["item_sku"].str.startswith("CC-MJM", na=False),
        df["item_sku"].str.startswith("CC-CC2", na=False)
    ]
    choices = ["Pro Jet", "Quad Jet", "Micro Jet", "Cryo Clamp"]
    
    # Create a new column "product" based on the above conditions.
    df = df.copy()
    df["product"] = np.select(conditions, choices, default=None)
    # Remove rows that are not one of our desired product types.
    df = df[df["product"].notnull()]
    
    # Ensure order_date is datetime and add year and month columns.
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month.apply(lambda m: months_x[m - 1])
    
    # Create a wholesale flag column.
    df["wholesale"] = df["customer"].isin(wholesale_list)
    
    # Group by year, month, and product for overall totals.
    overall = df.groupby(["year", "month", "product"]).agg(
        qty_sum=("quantity", "sum"),
        spend_sum=("total_line_item_spend", "sum")
    ).reset_index()
    
    # Group by year, month, and product for wholesale only quantities.
    wholesale_grp = df[df["wholesale"]].groupby(["year", "month", "product"])["quantity"].sum().reset_index()
    wholesale_grp = wholesale_grp.rename(columns={"quantity": "wholesale_qty"})
    
    # Merge the overall and wholesale results.
    merged = pd.merge(overall, wholesale_grp, on=["year", "month", "product"], how="left")
    merged["wholesale_qty"] = merged["wholesale_qty"].fillna(0)
    
    # Build a result dictionary for each target year.
    result = {}
    # Target years: 2023, 2024, and 2025.
    for y in [2023, 2024, 2025]:
        # Pre-fill with default values for every month and each product.
        year_dict = {month: {"Pro Jet": [0, 0, 0], "Quad Jet": [0, 0, 0],
                             "Micro Jet": [0, 0, 0], "Cryo Clamp": [0, 0, 0]}
                     for month in months_x}
        sub = merged[merged["year"] == y]
        for _, row in sub.iterrows():
            month = row["month"]
            product = row["product"]
            # Update the values: [total_quantity, total_spend, wholesale_quantity]
            year_dict[month][product] = [row["qty_sum"], row["spend_sum"], row["wholesale_qty"]]
        result[y] = year_dict
    
    # Return dictionaries for the target years.
    return result.get(2023), result.get(2024), result.get(2025)

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

    # Filter for rows that match the given year.
    #mask_year = df["ordered_year"] == year
    
    # Force conversion of order_date to datetime
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    
    # Debugging: Check if conversion worked
    print(df[['order_date']].head())  # Should display datetime values
    print(df['order_date'].dtype)  # Should be 'datetime64[ns]'
    
    # Now, extract the year safely
    mask_year = df['order_date'].dt.year == int(year)

    # Build a mask for rows where either 'line_item' or 'item_sku' starts with "Magic" or "MFX"
    mask_magic = (
        df["line_item"].str.startswith("Magic", na=False) |
        df["line_item"].str.startswith("MFX", na=False) |
        df["item_sku"].str.startswith("Magic", na=False) |
        df["item_sku"].str.startswith("MFX", na=False)
    )
    
    # Combined mask: only consider rows from the given year that mention Magic/MFX
    mask = mask_year & mask_magic

    # Sum total_line_item_spend for these rows
    total_spend = df.loc[mask, "total_line_item_spend"].sum()
    
    # Create (or copy) the magic_products dictionary
    magic_products = {
        'MagicFX Commander': [0, 0],
        'Magic FX Smoke Bubble Blaster': [0, 0],
        'MagicFX ARM SFX SAFETY TERMINATOR': [0, 0],
        'MagicFX Device Updater': [0, 0],
        'MagicFX PSYCO2JET': [0, 0],
        'MagicFX Red Button': [0, 0],
        'MagicFX Replacement Keys': [0, 0],
        'MagicFX SFX Safety ARM Controller': [0, 0],
        'MagicFX SPARXTAR': [0, 0],
        'MagicFX Sparxtar powder': [0, 0],
        'MagicFX StadiumBlaster': [0, 0],
        'MagicFX StadiumBlower': [0, 0],
        'MagicFX StadiumShot III': [0, 0],
        'MagicFX SuperBlaster II': [0, 0],
        'MagicFX Swirl Fan II': [0, 0],
        'MagicFX Switchpack II': [0, 0],
        'MFX-AC-SBRV': [0, 0],
        'MFX-E2J-230': [0, 0],
        'MFX-E2J-2LFA': [0, 0],
        'MFX-E2J-5LFCB': [0, 0],
        'MFX-E2J-F-ID': [0, 0],
        'MFX-E2J-F-OD': [0, 0],
        'MFX-E2J-FC': [0, 0],
        'MFX-E2J-FEH-1M': [0, 0],
        'MFX-E2J-FEH-2M': [0, 0],
        'MFX-E2J-OB': [0, 0],
        'MFX-ECO2JET-BKT': [0, 0],
        'MFX-E2J-BKT': [0, 0],
        'MFX-SS3-RB': [0, 0]
    }

    #for prod in magic_products:
        #mask_prod = mask_year & df["line_item"].str.lower().str.startswith(prod.lower(), na=False)
        #st.write(f"Checking {prod}: {mask_prod.sum()} rows matched")
    
    # For each magic product, create a mask (using the line_item column) and aggregate quantity and sales.
    for prod in magic_products:
        # Check if the beginning of line_item matches the product name.
        mask_prod = mask_year & df["item_sku"].str.contains(prod, na=False)
        qty_sum   = df.loc[mask_prod, "quantity"].sum()
        spend_sum = df.loc[mask_prod, "total_line_item_spend"].sum()
        magic_products[prod] = [qty_sum, spend_sum]
        
    magic_products['MFX-E2J-BKT'][0] = magic_products['MFX-ECO2JET-BKT'][0] + magic_products['MFX-E2J-BKT'][0]
    magic_products['MFX-E2J-BKT'][1] = magic_products['MFX-ECO2JET-BKT'][1] + magic_products['MFX-E2J-BKT'][1]
    
    return total_spend, magic_products

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
            if q1_end.date() >= order_date.date() >= beginning_of_year(q1_end).date():
                q1_count[0] += df.iloc[idx].total_line_item_spend
            elif q2_end.date() >= order_date.date() >= q2_start.date():
                q2_count[0] += df.iloc[idx].total_line_item_spend
            elif q3_end.date() >= order_date.date() >= q3_start.date():
                q3_count[0] += df.iloc[idx].total_line_item_spend
            elif q4_end.date() >= order_date.date() >= q4_start.date():
                q4_count[0] += df.iloc[idx].total_line_item_spend
        else:
            if q1_end.date() >= order_date.date() >= beginning_of_year(q1_end).date():
                q1_count[1] += df.iloc[idx].total_line_item_spend
            elif q2_end.date() >= order_date.date() >= q2_start.date():
                q2_count[1] += df.iloc[idx].total_line_item_spend
            elif q3_end.date() >= order_date.date() >= q3_start.date():
                q3_count[1] += df.iloc[idx].total_line_item_spend
            elif q4_end.date() >= order_date.date() >= q4_start.date():
                q4_count[1] += df.iloc[idx].total_line_item_spend
    
        idx += 1
    
    return q1_count, q2_count, q3_count, q4_count
    

def to_date_revenue():
    # td_22 remains unused in the original code; keeping it as [0, 0]
    td_22 = [0, 0]
    
    # Ensure the order_date column is in datetime format.
    # (This will convert any strings or non-datetime values to datetime, with errors coerced to NaT.)
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    
    # Create a boolean flag: True if the channel starts with 'F'
    cond_F = df["channel"].str.startswith("F")
    
    # Create masks for each date range.
    # For td_23: orders between beginning_of_year(two_years_ago) and two_years_ago (inclusive)
    cond_td23 = (
        (df["order_date"].dt.date >= beginning_of_year(two_years_ago).date()) &
        (df["order_date"].dt.date <= two_years_ago.date())
    )
    # For td_24: orders between beginning_of_year(one_year_ago) and one_year_ago
    cond_td24 = (
        (df["order_date"].dt.date >= beginning_of_year(one_year_ago).date()) &
        (df["order_date"].dt.date <= one_year_ago.date())
    )
    # For td_25: orders between beginning_of_year(today) and today
    cond_td25 = (
        (df["order_date"].dt.date >= beginning_of_year(today).date()) &
        (df["order_date"].dt.date <= today.date())
    )
    
    # Sum total_line_item_spend for each combination of date range and channel type:
    td_23 = [
        df.loc[cond_td23 & cond_F, "total_line_item_spend"].sum(),
        df.loc[cond_td23 & (~cond_F), "total_line_item_spend"].sum()
    ]
    td_24 = [
        df.loc[cond_td24 & cond_F, "total_line_item_spend"].sum(),
        df.loc[cond_td24 & (~cond_F), "total_line_item_spend"].sum()
    ]
    td_25 = [
        df.loc[cond_td25 & cond_F, "total_line_item_spend"].sum(),
        df.loc[cond_td25 & (~cond_F), "total_line_item_spend"].sum()
    ]
    
    return td_22, td_23, td_24, td_25


# HISTORICAL TO-DATE REVENUE -- NEEDS ANNUAL UPDATE
def hist_td_rev(year):

    td24 = today - timedelta(days=366)
    td23 = today - timedelta(days=731)
    td22 = today - timedelta(days=1096)
    td21 = today - timedelta(days=1461)
    td20 = today - timedelta(days=1826)
    td19 = today - timedelta(days=2191)
    td18 = today - timedelta(days=2557)
    td17 = today - timedelta(days=2922)
    td16 = today - timedelta(days=3287)
    td15 = today - timedelta(days=3652)
    td14 = today - timedelta(days=4018)
    td13 = today - timedelta(days=4383)

    date_dict = {2013: td13, 2014: td14, 2015: td15, 2016: td16, 2017: td17, 2018: td18, 2019: td19, 2020: td20, 2021: td21, 2022: td22, 2023: td23, 2024: td24}
    
    td_sales = 0

    idx = 0

    for so in df_hist.customer:
        if df_hist.iloc[idx].order_date.date().year == year:
            if date_dict[year].date() >= df_hist.iloc[idx].order_date.date() >= beginning_of_year(df_hist.iloc[idx].order_date).date():
                td_sales += df_hist.iloc[idx].total_sale
            
        idx += 1


    return td_sales



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


def hist_cust_data(customer):
    
    target_years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
    
    spending_dict = {2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}
    spending_total = 0

    jets = ['DMX Jet', 'Pro Jet', 'Power Jet', 'Micro Jet MKI', 'Micro Jet MKII', 'Cryo Clamp MKI', 'Cryo Clamp', 'Quad Jet']
    handhelds = ['Handheld MKI', 'Handheld MKII']
    controllers = ['DMX Controller', 'LCD Controller', 'The Button MKI', 'The Button', 'Shomaster', 'Shostarter', 'Power Controller']
    accessories = ['Travel Case', 'Original Travel Case', 'Back Pack', 'Manifold', '20LB Tank Cover', '50LB Tank Cover', 'LED Attachment I', 'LED Attachment II', 'Power Pack', 'Confetti Blower']
    
    hist_products = {
        'hh_mk2': 'Handheld MKII',
        'hh_mk1': 'Handheld MKI', 
        'travel_case': 'Travel Case',
        'travel_case_og': 'Original Travel Case', 
        'backpack': 'Back Pack',
        'jets_og': 'DMX Jet',
        'pro_jet': 'Pro Jet',
        'power_jet': 'Power Jet',
        'micro_jet_mk1': 'Micro Jet MKI',
        'micro_jet_mk2': 'Micro Jet MKII',
        'cryo_clamp_mk1': 'Cryo Clamp MKI',
        'cryo_clamp_mk2': 'Cryo Clamp',
        'quad_jet': 'Quad Jet',
        'dmx_controller': 'DMX Controller',
        'lcd_controller': 'LCD Controller',
        'the_button_mk1': 'The Button MKI',
        'the_button_mk2': 'The Button',
        'shomaster': 'Shomaster',
        'shostarter': 'Shostarter',
        'power_controller': 'Power Controller',
        'hoses': 'Hoses',
        'manifold': 'Manifold',
        'ctc_20': '20LB Tank Cover',
        'ctc_50': '50LB Tank Cover',
        'led_attachment_mk1': 'LED Attachment I', 
        'led_attachment_mk2': 'LED Attachment II',
        'power_pack': 'Power Pack',
        'confetti_blower': 'Confetti Blower',
        
    }
    
    cust_products = {
        'hh_mk2': [0, []],
        'hh_mk1': [0, []], 
        'travel_case': [0, []],
        'travel_case_og': [0, []], 
        'backpack': [0, []],
        'jets_og': [0, []],
        'pro_jet': [0, []],
        'power_jet': [0, []],
        'micro_jet_mk1': [0, []],
        'micro_jet_mk2': [0, []],
        'cryo_clamp_mk1': [0, []],
        'cryo_clamp_mk2': [0, []],
        'quad_jet': [0, []],
        'dmx_controller': [0, []],
        'lcd_controller': [0, []],
        'the_button_mk1': [0, []],
        'the_button_mk2': [0, []],
        'shomaster': [0, []],
        'shostarter': [0, []],
        'power_controller': [0, []],
        'hoses': [0, []],
        'manifold': [0, []],
        'ctc_20': [0, []],
        'ctc_50': [0, []],
        'led_attachment_mk1': [0, []], 
        'led_attachment_mk2': [0, []],
        'power_pack': [0, []],
        'confetti_blower': [0, []],
        
    }
            
    cust_rows = df_hist.loc[df_hist['customer'] == customer].reset_index()
    
    cust_filtered = cust_rows[cust_rows['order_date'].dt.year.isin(target_years)]
    
    cust_filtered['year'] = cust_filtered['order_date'].dt.year
    spending_dict = cust_filtered.groupby('year')['total_spend'].sum().to_dict()
    
    spending_total = sum(spending_dict.values())

    idx = 0 
    for sale in cust_filtered.order_date:
        for prod in cust_products.keys():
            #st.write(cust_filtered.iloc[idx][prod])
            if cust_filtered.iloc[idx][prod] not in [0, None, 'NaN']:
                
                cust_products[prod][0] += int(cust_filtered.iloc[idx][prod])
                cust_products[prod][1].append((int(cust_filtered.iloc[idx][prod]), str(cust_filtered.iloc[idx].order_date.date())))
                

        idx += 1

    # CONVERT TO READABLE NAMES
    keyed_cust_products = dict(zip(hist_products.values(), cust_products.values()))

    # SPLIT DICT INTO CATEGORY DICTS
    jet_dict = {key: keyed_cust_products[key] for key in jets}
    handheld_dict = {key: keyed_cust_products[key] for key in handhelds}
    controller_dict = {key: keyed_cust_products[key] for key in controllers}
    acc_dict = {key: keyed_cust_products[key] for key in accessories}

    return spending_dict, spending_total, jet_dict, handheld_dict, controller_dict, acc_dict





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
    # Define month names
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    
    # Template dictionary for a year: for each month, a list of two lists:
    # index 0: [wholesale_total, wholesale_order_count]
    # index 1: [non_wholesale_total, non_wholesale_order_count]
    empty_year_dict = {month: [[0, 0], [0, 0]] for month in months}
    
    # Work on a copy of df_hist
    #df = df_hist.copy()
    
    # Ensure 'order_date' is datetime
    df_hist["order_date"] = pd.to_datetime(df_hist["order_date"], errors="coerce")
    
    # Create new columns for year and month (as month names)
    df_hist["year"] = df_hist["order_date"].dt.year
    df_hist["month"] = df_hist["order_date"].dt.month.apply(lambda m: months[int(m)-1] if pd.notnull(m) else None)
    
    # Convert 'total_sale' to numeric (if not already) and fill invalid values with 0
    df_hist["total_sale"] = pd.to_numeric(df_hist["total_sale"], errors="coerce").fillna(0)
    
    # Create a wholesale flag column (True if customer is in wholesale_list)
    df_hist["wholesale"] = df_hist["customer"].isin(wholesale_list)
    
    # Group by year, month, and wholesale flag.
    # For each group, compute:
    #   - Sum of total_sale.
    #   - Count of orders (each row is one order).
    grouped = df_hist.groupby(["year", "month", "wholesale"]).agg(
        total_sale_sum=("total_sale", "sum"),
        order_count=("total_sale", "size")
    ).reset_index()
    
    # Prepare a dictionary to hold results for years 2013 to 2022.
    yearly_results = {yr: {month: [[0, 0], [0, 0]] for month in months} for yr in range(2013, 2023)}
    
    # Populate the results dictionary using the grouped data.
    for _, row in grouped.iterrows():
        yr = row["year"]
        month = row["month"]
        # Wholesale orders go in index 0; non-wholesale in index 1.
        idx = 0 if row["wholesale"] else 1
        if yr in yearly_results:
            yearly_results[yr][month][idx][0] = row["total_sale_sum"]
            yearly_results[yr][month][idx][1] = row["order_count"]
    
    # Extract results for each year. If a particular year has no data, use the empty template.
    sales13 = yearly_results.get(2013, empty_year_dict)
    sales14 = yearly_results.get(2014, empty_year_dict)
    sales15 = yearly_results.get(2015, empty_year_dict)
    sales16 = yearly_results.get(2016, empty_year_dict)
    sales17 = yearly_results.get(2017, empty_year_dict)
    sales18 = yearly_results.get(2018, empty_year_dict)
    sales19 = yearly_results.get(2019, empty_year_dict)
    sales20 = yearly_results.get(2020, empty_year_dict)
    sales21 = yearly_results.get(2021, empty_year_dict)
    sales22 = yearly_results.get(2022, empty_year_dict)
    
    return sales13, sales14, sales15, sales16, sales17, sales18, sales19, sales20, sales21, sales22


@st.cache_data
def hist_quarterly_sales():
    # Define the quarters as lists of month names
    quarters = {
        1: ["January", "February", "March"],
        2: ["April", "May", "June"],
        3: ["July", "August", "September"],
        4: ["October", "November", "December"]
    }
    
    def compute_quarterly_sales(sales):
        """
        Given a sales dictionary (e.g., sales13) where each month maps to
        [[wholesale_total, wholesale_order_count], [non_wholesale_total, non_wholesale_order_count]],
        compute a list of quarterly totals by summing the wholesale and non-wholesale totals.
        """
        return [
            sum(sales[month][0][0] + sales[month][1][0] for month in quarters[q])
            for q in range(1, 5)
        ]
    
    # Compute quarterly sales for each year
    qs13 = compute_quarterly_sales(sales13)
    qs14 = compute_quarterly_sales(sales14)
    qs15 = compute_quarterly_sales(sales15)
    qs16 = compute_quarterly_sales(sales16)
    qs17 = compute_quarterly_sales(sales17)
    qs18 = compute_quarterly_sales(sales18)
    qs19 = compute_quarterly_sales(sales19)
    qs20 = compute_quarterly_sales(sales20)
    qs21 = compute_quarterly_sales(sales21)
    qs22 = compute_quarterly_sales(sales22)
    
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

def plot_annual_comparison(x, year_select, col1, line_width=4.5, fig_width=12, fig_height=8):
    # Define year series mapping
    year_series = {
        '2025': ['2022', '2023', '2024'],
        '2024': ['2022', '2023', '2024'],
        '2023': ['2022', '2023', '2024'],
        '2022': ['2021', '2022', '2023'],
        '2021': ['2020', '2021', '2022'],
        '2020': ['2019', '2020', '2021'],
        '2019': ['2018', '2019', '2020'],
        '2018': ['2017', '2018', '2019'],
        '2017': ['2016', '2017', '2018'],
        '2016': ['2015', '2016', '2017'],
        '2015': ['2014', '2015', '2016'],
        '2014': ['2013', '2014', '2015'],
        '2013': ['2013', '2014', '2015']
    }

    # Define corresponding colors
    colors = ['limegreen', 'white', 'grey']

    # Retrieve year labels based on selection
    selected_years = year_series.get(year_select, ['2022', '2023', '2024'])

    # Create figure and axis with dynamic size
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=100)

    # Plot data dynamically with adjustable line width
    for idx, year in enumerate(selected_years):
        ax.plot(x, globals().get(f"y{year}", []), label=year, color=colors[idx], linewidth=line_width)

    # Set background colors
    ax.set_facecolor('#000000')
    fig.patch.set_facecolor('#000000')

    # Customize tick labels for responsiveness
    ax.tick_params(axis='x', labelsize=25, colors='white')
    ax.tick_params(axis='y', labelsize=25, colors='white')

    # Set dynamic y-ticks based on data range
    #all_y_values = [globals().get(f"y{year}", []) for year in selected_years if globals().get(f"y{year}") is not None]
    #if all_y_values:
        #y_min = min(map(min, all_y_values))
        #y_max = max(map(max, all_y_values))
        #y_ticks = range(int(y_min // 20000) * 20000, int(y_max // 20000 + 2) * 20000, 20000)
        #ax.set_yticks(y_ticks)
    plt.yticks([20000, 40000, 60000, 80000, 100000, 120000, 140000, 160000, 180000, 200000, 220000, 240000, 260000, 280000])
    plt.tick_params(axis='x', colors='white')
    plt.tick_params(axis='y', colors='white')
    # Customize legend
    #ax.legend(fontsize=16, loc="upper right", frameon=False)
    fig.legend(fontsize=25)
    # Ensure proper figure scaling for Streamlit
    col1.pyplot(fig, use_container_width=True)


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
    y2013 = []
    y2014 = []
    y2015 = []
    y2016 = []
    y2017 = []
    y2018 = []
    y2019 = []
    y2020 = []
    y2021 = []
    y2022 = []
    y2023 = []
    y2024 = []
    y2025 = []

    for key, val in sales13.items():
        y2013.append(val[0][0] + val[1][0])
    for key, val in sales14.items():
        y2014.append(val[0][0] + val[1][0])
    for key, val in sales15.items():
        y2015.append(val[0][0] + val[1][0])
    for key, val in sales16.items():
        y2016.append(val[0][0] + val[1][0])
    for key, val in sales17.items():
        y2017.append(val[0][0] + val[1][0])
    for key, val in sales18.items():
        y2018.append(val[0][0] + val[1][0])
    for key, val in sales19.items():
        y2019.append(val[0][0] + val[1][0])
    for key, val in sales20.items():
        y2020.append(val[0][0] + val[1][0])
    for key, val in sales21.items():
        y2021.append(val[0][0] + val[1][0])
    for key, val in sales_dict_22.items():
        y2022.append(val[0][0] + val[1][0])
    for key, val in sales_dict_23.items():
        y2023.append(val[0][0] + val[1][0])
    for key, val in sales_dict_24.items():
        y2024.append(val[0][0] + val[1][0])
    for key, val in sales_dict_25.items():
        y2025.append(val[0][0] + val[1][0])

    ### SALES CHANNEL BREAKDOWN ###
    web_avg_perc = (web_23 + web_24)/2
    ful_avg_perc = (ful_23 + ful_24)/2

    col1, col2, col3 = st.columns([.28, .44, .28], gap='medium')
    colx, coly, colz = st.columns([.28, .44, .28], gap='medium')
    
    with col2:
        
        year_select = ui.tabs(options=['2025', '2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013'], default_value='2025')    
        
        #tot_vs_ytd = ui.tabs(options=['Totals', 'YTD'], default_value='Totals')

    col1.header('Annual Comparison')
    
    plot_annual_comparison(x, year_select, col1, line_width=11, fig_width=18, fig_height=13)
    
    with colx:
        
        st.header('To-Date Sales')
        
        cola, colb, colc = st.columns(3)

        cola.metric('**2025 Total**', '${:,}'.format(int(td_25[1] + td_25[0])), percent_of_change((td_24[0] + td_24[1]), (td_25[0] + td_25[1])))
        cola.metric('**2025 Web**', '${:,}'.format(int(td_25[0])), percent_of_change(td_24[0], td_25[0]))
        cola.metric('**2025 Fulcrum**', '${:,}'.format(int(td_25[1])), percent_of_change(td_24[1], td_25[1]))
        
        colb.metric('**2024 Total**', '${:,}'.format(int(td_24[1] + td_24[0])), percent_of_change((td_23[0] + td_23[1]), (td_24[0] + td_24[1])))
        colb.metric('**2024 Web**', '${:,}'.format(int(td_24[0])), percent_of_change(td_23[0], td_24[0]))
        colb.metric('**2024 Fulcrum**', '${:,}'.format(int(td_24[1])), percent_of_change(td_23[1], td_24[1]))
        
        colc.metric('**2023 Total**', '${:,}'.format(int(td_23[1] + td_23[0])), percent_of_change(hist_td_rev(2022), (td_23[1] + td_23[0])))
        colc.metric('**2023 Web**', '${:,}'.format(int(td_23[0])), percent_of_change(hist_td_rev(2022), (td_23[1] + td_23[0])))
        colc.metric('**2023 Fulcrum**', '${:,}'.format(int(td_23[1])), percent_of_change(hist_td_rev(2022), (td_23[1] + td_23[0])))

        style_metric_cards()


    with col2:
        
        if year_select == '2025':
            
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

        elif year_select == '2024':

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


        elif year_select == '2023':

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
                
                col6.metric('**Q1 Web Sales**', '${:,}'.format(int(q1_23[0])), percent_of_change((qs22[0] * .4), q1_23[0]))
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(q1_23[0] + q1_23[1])), percent_of_change((qs22[0]), (q1_23[0] + q1_23[1])))
                col8.metric('**Q1 Fulcrum Sales**', '${:,}'.format(int(q1_23[1])), percent_of_change((qs22[0] * .6), q1_23[1]))
                
                col6.metric('**Q2 Web Sales**', '${:,}'.format(int(q2_23[0])), percent_of_change((qs22[1] * .4), q2_23[0]))
                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(q2_23[0] + q2_23[1])), percent_of_change((qs22[1]), (q2_23[0] + q2_23[1])))
                col8.metric('**Q2 Fulcrum Sales**', '${:,}'.format(int(q2_23[1])), percent_of_change((qs22[1] * .6), q2_23[1]))
                
                col6.metric('**Q3 Web Sales**', '${:,}'.format(int(q3_23[0])), percent_of_change((qs22[2] * .4), q3_23[0]))
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(q3_23[0] + q3_23[1])), percent_of_change((qs22[2]), (q3_23[0] + q3_23[1])))
                col8.metric('**Q3 Fulcrum Sales**', '${:,}'.format(int(q3_23[1])), percent_of_change((qs22[2] * .6), q3_23[1]))

                col6.metric('**Q4 Web Sales**', '${:,}'.format(int(q4_23[0])), percent_of_change((qs22[3] * .4), q4_23[0]))
                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(q4_23[0] + q4_23[1])), percent_of_change((qs22[3]), (q4_23[0] + q4_23[1])))
                col8.metric('**Q4 Fulcrum Sales**', '${:,}'.format(int(q4_23[1])), percent_of_change((qs22[3] * .6), q4_23[1]))

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
                

        if year_select == '2022':
    
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

        if year_select == '2021':
    
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

        if year_select == '2020':
    
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

        if year_select == '2019':
    
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

        if year_select == '2018':
    
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

        if year_select == '2017':
    
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

        if year_select == '2016':
    
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

        if year_select == '2015':
    
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

        if year_select == '2014':
    
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

        if year_select == '2013':
    
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
    # Filter rows where the line_item starts with sku_string.
    mask_sku = df["item_sku"].str.startswith(sku_string)
    df_sku = df[mask_sku].copy()
    
    # Ensure order_date is a datetime and create a date-only column.
    df_sku["order_date"] = pd.to_datetime(df_sku["order_date"], errors="coerce")
    df_sku["order_date_date"] = df_sku["order_date"].dt.date
    
    # Convert our reference datetime values to dates.
    two_years_ago_date = two_years_ago.date()
    one_year_ago_date   = one_year_ago.date()
    today_date          = today.date()
    
    begin_two = beginning_of_year(two_years_ago).date()
    begin_one = beginning_of_year(one_year_ago).date()
    begin_today = beginning_of_year(today).date()
    
    # Build boolean masks for the different time ranges.
    mask_23 = (df_sku["order_date_date"] >= begin_two) & (df_sku["order_date_date"] <= two_years_ago_date)
    mask_24 = (df_sku["order_date_date"] >= begin_one) & (df_sku["order_date_date"] <= one_year_ago_date)
    #mask_24 = (df_sku["order_date_date"] >= begin_today) & (df_sku["order_date_date"] <= today_date)
    #mask_25 = (df_sku["order_date"].dt.year == 2025)  # 2025 comparison can remain on timestamps.
    
    # Sum the quantities for each date range.
    #prod_cnt_22 = df_sku.loc[mask_22, "quantity"].sum()
    prod_cnt_23 = df_sku.loc[mask_23, "quantity"].sum()
    prod_cnt_24 = df_sku.loc[mask_24, "quantity"].sum()
    #prod_cnt_25 = df_sku.loc[mask_25, "quantity"].sum()
    
    # (Return only the counts you need. In your example, you returned prod_cnt_23 and prod_cnt_24.)
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


def format_for_chart_product(data_dict, prod_label):
    temp_dict = {'Years': [], prod_label: []}

    for year, sales in data_dict.items():
        temp_dict['Years'].append(year)
              
        temp_dict[prod_label].append(sales)
                
    df = pd.DataFrame(temp_dict)
    
    return df

    

def plot_bar_chart_product(df, prod_label):
    st.write(alt.Chart(df).mark_bar().encode(
        x=alt.X('Years', sort=None).title('Year'),
        y=prod_label,
    ).properties(height=800, width=1400).configure_mark(
        color='limegreen'
    ))


def format_for_chart_product_seg(data_dict, prod_label):
    """
    Format data for a segmented bar chart.
    
    Args:
        data_dict (dict): A dictionary where keys are years and values are dictionaries of product sales.
                         Example: {2021: {'Product A': 100, 'Product B': 200}}
    
    Returns:
        pd.DataFrame: A DataFrame suitable for a segmented bar chart.
    """
    temp_dict = {'Years': [], 'Product': [], 'Sales': []}

    for year, product_sales in data_dict.items():
        for product, sales in product_sales.items():
            temp_dict['Years'].append(year)
            temp_dict['Product'].append(product)
            temp_dict['Sales'].append(sales)
    
    return pd.DataFrame(temp_dict)

def plot_bar_chart_product_seg(df, prod_label):
    """
    Plot a segmented bar chart using Altair.

    Args:
        df (pd.DataFrame): A DataFrame with columns 'Years', 'Product', and 'Sales'.
    """
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X('Years:O', title='Year'),
            y=alt.Y('sum(Sales):Q', title='Total Sales'),
            color=alt.Color('Product:N', title='Product', scale=alt.Scale(scheme='tableau10')),
            tooltip=['Years', 'Product', 'Sales'],
        )
        .properties(height=800, width=1400)
    )
    st.altair_chart(chart, use_container_width=True)


def hist_annual_prod_totals(prod_annual_dict, prod_list, year_list):

    for year in year_list:
        for prod in prod_list:
            prod_annual_dict[year] += prod[year]

    prod_annual_dict = dict(reversed(list(prod_annual_dict.items())))
    
    return prod_annual_dict



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
            year = ui.tabs(options=[2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 'Historical'], default_value=2025, key='Jet Year Select')

        if year == 2025:
            
            total_jet_rev = annual_product_totals[2]['Pro Jet'][1] + annual_product_totals[2]['Quad Jet'][1] + annual_product_totals[2]['Micro Jet'][1] + annual_product_totals[2]['Cryo Clamp'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4, gap='medium')
    
                cola.subheader('Pro Jet')
                cola.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[2]['Pro Jet'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[2]['Pro Jet'][0]), (annual_product_totals[2]['Pro Jet'][0] - pj_td24))
    
                colb.subheader('Quad Jet')
                colb.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[2]['Quad Jet'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[2]['Quad Jet'][0]), (annual_product_totals[2]['Quad Jet'][0] - qj_td24))
    
                colc.subheader('Micro Jet')
                colc.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[2]['Micro Jet'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[2]['Micro Jet'][0]), (annual_product_totals[2]['Micro Jet'][0] - mj_td24))
    
                cold.subheader('Cryo Clamp')
                cold.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[2]['Cryo Clamp'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[2]['Cryo Clamp'][0]), (annual_product_totals[2]['Cryo Clamp'][0] - cc_td24))

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

        elif year == 'Historical':

            pj_tot_unit = annual_product_totals[2]['Pro Jet'][0] + annual_product_totals[1]['Pro Jet'][0] + annual_product_totals[0]['Pro Jet'][0] + pj_annual['2022']
            pj_tot_rev = annual_product_totals[2]['Pro Jet'][1] + annual_product_totals[1]['Pro Jet'][1] + annual_product_totals[0]['Pro Jet'][1] + (pj_annual['2022'] * 1174)

            qj_tot_unit = annual_product_totals[2]['Quad Jet'][0] + annual_product_totals[1]['Quad Jet'][0] + annual_product_totals[0]['Quad Jet'][0] + qj_annual['2022']
            qj_tot_rev = annual_product_totals[2]['Quad Jet'][1] + annual_product_totals[1]['Quad Jet'][1] + annual_product_totals[0]['Quad Jet'][1] + (qj_annual['2022'] * 1800)

            mj2_tot_unit = annual_product_totals[2]['Micro Jet'][0] + annual_product_totals[1]['Micro Jet'][0] + annual_product_totals[0]['Micro Jet'][0] + mjmk2_annual['2022'] + mjmk2_annual['2021']
            mj2_tot_rev = annual_product_totals[2]['Micro Jet'][1] + annual_product_totals[1]['Micro Jet'][1] + annual_product_totals[0]['Micro Jet'][1] + (mjmk2_annual['2022'] * 778) + (mjmk2_annual['2021'] * 778)

            mj1_tot_unit = mjmk1_annual['2022'] + mjmk1_annual['2021'] + mjmk1_annual['2020'] + mjmk1_annual['2019']
            mj1_tot_rev = (mjmk1_annual['2022'] * 778.63) + (mjmk1_annual['2021'] * 778.99) + (mjmk1_annual['2020'] * 778.52) + (mjmk1_annual['2019'] * 778)

            cc2_tot_unit = annual_product_totals[2]['Cryo Clamp'][0] + annual_product_totals[1]['Cryo Clamp'][0] + annual_product_totals[0]['Cryo Clamp'][0]
            cc2_tot_rev = annual_product_totals[2]['Cryo Clamp'][1] + annual_product_totals[1]['Cryo Clamp'][1] + annual_product_totals[0]['Cryo Clamp'][1] 

            cc1_tot_unit = ccmk1_annual['2022'] + ccmk1_annual['2021'] + ccmk1_annual['2020'] + ccmk1_annual['2019'] + ccmk1_annual['2018']
            cc1_tot_rev = (ccmk1_annual['2022'] * 387.91) + (ccmk1_annual['2021'] * 387.91) + (ccmk1_annual['2020'] * 387.91) + (ccmk1_annual['2019'] * 387.91) + (ccmk1_annual['2018'] * 387.91)

            dmx_jet_tot_unit = jet_og_annual['2021'] + jet_og_annual['2020'] + jet_og_annual['2019'] + jet_og_annual['2018'] + jet_og_annual['2017'] + jet_og_annual['2016'] + jet_og_annual['2015'] + jet_og_annual['2014']
            dmx_jet_tot_rev = (jet_og_annual['2021'] * 1098.54) + (jet_og_annual['2020'] * 1098.54) + (jet_og_annual['2019'] * 1098.54) + (jet_og_annual['2018'] * 1098.54) + (jet_og_annual['2017'] * 1098.54) + (jet_og_annual['2016'] * 1098.54) + (jet_og_annual['2015'] * 1098.54) + (jet_og_annual['2014'] * 1098.54)
            
            pwj_tot_unit = pwj_annual['2021'] + pwj_annual['2020'] + pwj_annual['2019'] + pwj_annual['2018'] + pwj_annual['2017'] 
            pwj_tot_rev = (pwj_annual['2021'] * 948.53) + (pwj_annual['2020'] * 948.53) + (pwj_annual['2019'] * 948.53) + (pwj_annual['2018'] * 948.53) + (pwj_annual['2017'] * 948.53)


            cola, colb, colc, cold, cole = st.columns(5)

            colb.subheader('Pro Jet')
            colb.metric('**${:,.2f}**'.format(pj_tot_rev), '{}'.format(pj_tot_unit))
            colb.subheader('Cryo Clamp MKII')
            colb.metric('**${:,.2f}**'.format(cc2_tot_rev), '{}'.format(cc2_tot_unit))
            colb.subheader('Cryo Clamp MKI')
            colb.metric('**${:,.2f}**'.format(cc1_tot_rev), '{}'.format(cc1_tot_unit))

            colc.subheader('Quad Jet')
            colc.metric('**${:,.2f}**'.format(qj_tot_rev), '{}'.format(qj_tot_unit))
            colc.subheader('Power Jet')
            colc.metric('**${:,.2f}**'.format(pwj_tot_rev), '{}'.format(pwj_tot_unit))
            colc.subheader('Total Jets')
            colc.metric('**${:,.2f}**'.format(pwj_tot_rev + dmx_jet_tot_rev + cc1_tot_rev + cc2_tot_rev + mj1_tot_rev + mj2_tot_rev + qj_tot_rev + pj_tot_rev), '{}'.format(pwj_tot_unit + dmx_jet_tot_unit + cc1_tot_unit + cc2_tot_unit + mj1_tot_unit + mj2_tot_unit + qj_tot_unit + pj_tot_unit))

            cold.subheader('DMX Jet')
            cold.metric('**${:,.2f}**'.format(dmx_jet_tot_rev), '{}'.format(dmx_jet_tot_unit))
            cold.subheader('Micro Jet MKII')
            cold.metric('**${:,.2f}**'.format(mj2_tot_rev), '{}'.format(mj2_tot_unit))
            cold.subheader('Micro Jet MKI')
            cold.metric('**${:,.2f}**'.format(mj1_tot_rev), '{}'.format(mj1_tot_unit))

            style_metric_cards()

            jet_annual_dict = {'2025': 0, '2024': 0, '2023': 0, '2022': 0, '2021': 0, '2020': 0, '2019': 0, '2018': 0, '2017': 0, '2016': 0, '2015': 0, '2014': 0}
            jet_annual_dict_seg = {'2025': {'Pro Jet': annual_product_totals[2]['Pro Jet'][0], 'Quad Jet': annual_product_totals[2]['Quad Jet'][0], 'Micro Jet MKII': annual_product_totals[2]['Micro Jet'][0], 'Cryo Clamp': annual_product_totals[2]['Cryo Clamp'][0]}, '2024': {'Pro Jet': annual_product_totals[1]['Pro Jet'][0], 'Quad Jet': annual_product_totals[1]['Quad Jet'][0], 'Micro Jet MKII': annual_product_totals[1]['Micro Jet'][0], 'Cryo Clamp': annual_product_totals[1]['Cryo Clamp'][0]}, '2023': {'Pro Jet': annual_product_totals[0]['Pro Jet'][0], 'Quad Jet': annual_product_totals[0]['Quad Jet'][0], 'Micro Jet MKII': annual_product_totals[0]['Micro Jet'][0], 'Cryo Clamp': annual_product_totals[0]['Cryo Clamp'][0]}, '2022': {'Pro Jet': pj_annual['2022'], 'Quad Jet': qj_annual['2022'], 'Micro Jet MKII': mjmk2_annual['2022'], 'Micro Jet MKI': mjmk1_annual['2022'], 'Cryo Clamp MKI': ccmk1_annual['2022']}, '2021': {'Micro Jet MKII': mjmk2_annual['2021'], 'Micro Jet MKI': mjmk1_annual['2021'], 'Cryo Clamp MKI': ccmk1_annual['2021'], 'Quad Jet': qj_annual['2021'], 'DMX Jet': jet_og_annual['2021'], 'Power Jet': pwj_annual['2021']}, '2020': {'Micro Jet MKI': mjmk1_annual['2020'], 'Cryo Clamp MKI': ccmk1_annual['2020'], 'DMX Jet': jet_og_annual['2020'], 'Power Jet': pwj_annual['2020']}, '2019': {'Micro Jet MKI': mjmk1_annual['2019'], 'Cryo Clamp MKI': ccmk1_annual['2019'], 'DMX Jet': jet_og_annual['2019'], 'Power Jet': pwj_annual['2019']}, '2018': {'Cryo Clamp MKI': ccmk1_annual['2018'], 'DMX Jet': jet_og_annual['2018'], 'Power Jet': pwj_annual['2018']}, '2017': {'DMX Jet': jet_og_annual['2017'], 'Power Jet': pwj_annual['2017']}, '2016': {'DMX Jet': jet_og_annual['2016']}, '2015': {'DMX Jet': jet_og_annual['2015']}, '2014': {'DMX Jet': jet_og_annual['2014']}}
            jet_annual_dict['2025'] += annual_product_totals[2]['Pro Jet'][0] + annual_product_totals[2]['Quad Jet'][0] + annual_product_totals[2]['Micro Jet'][0] + annual_product_totals[2]['Cryo Clamp'][0] 
            jet_annual_dict['2024'] += annual_product_totals[1]['Pro Jet'][0] + annual_product_totals[1]['Quad Jet'][0] + annual_product_totals[1]['Micro Jet'][0] + annual_product_totals[1]['Cryo Clamp'][0]
            jet_annual_dict['2023'] += annual_product_totals[0]['Pro Jet'][0] + annual_product_totals[0]['Quad Jet'][0] + annual_product_totals[0]['Micro Jet'][0] + annual_product_totals[0]['Cryo Clamp'][0]

            jet_list = [pj_annual, pwj_annual, jet_og_annual, ccmk1_annual, mjmk1_annual, mjmk2_annual, qj_annual]
            year_list = ['2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014']
            
            colx, coly, colz = st.columns([.2, .6, .2])
            with coly:
                plot_bar_chart_product_seg(format_for_chart_product_seg(jet_annual_dict_seg, 'Total Jet Sales'), 'Total Jet Sales')


            

    elif prod_cat == 'Controllers':

        with col2:
            year = ui.tabs(options=[2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 'Historical'], default_value=2025, key='Control Year Select')

        if year == 2025:

            tb_td23, tb_td24 = to_date_product('CC-TB-35')
            ss_td23, ss_td24 = to_date_product('CC-SS-35')
            sm_td23, sm_td24 = to_date_product('CC-SM')
            
            total_cntl_rev = annual_product_totals[5]['The Button'][1] + annual_product_totals[5]['Shostarter'][1] + annual_product_totals[5]['Shomaster'][1]
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('The Button')
                cola.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[5]['The Button'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[5]['The Button'][0]), (annual_product_totals[5]['The Button'][0] - tb_td24))
                colb.subheader('Shostarter')
                colb.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[5]['Shostarter'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[5]['Shostarter'][0]), (annual_product_totals[5]['Shostarter'][0] - ss_td24))
                colc.subheader('Shomaster')
                colc.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[5]['Shomaster'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[5]['Shomaster'][0]), (annual_product_totals[5]['Shomaster'][0] - sm_td24))
    
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

        elif year == 'Historical':

            tb_tot_unit = annual_product_totals[5]['The Button'][0] + annual_product_totals[4]['The Button'][0] + annual_product_totals[3]['The Button'][0] + tbmk2_annual['2022']
            tb_tot_rev = annual_product_totals[5]['The Button'][1] + annual_product_totals[4]['The Button'][1] + annual_product_totals[3]['The Button'][1] + (tbmk2_annual['2022'] * 383)

            ss_tot_unit = annual_product_totals[5]['Shostarter'][0] + annual_product_totals[4]['Shostarter'][0] + annual_product_totals[3]['Shostarter'][0]
            ss_tot_rev = annual_product_totals[5]['Shostarter'][1] + annual_product_totals[4]['Shostarter'][1] + annual_product_totals[3]['Shostarter'][1] 

            sm_tot_unit = annual_product_totals[5]['Shomaster'][0] + annual_product_totals[4]['Shomaster'][0] + annual_product_totals[3]['Shomaster'][0] + sm_annual['2022'] + sm_annual['2021']
            sm_tot_rev = annual_product_totals[5]['Shomaster'][1] + annual_product_totals[4]['Shomaster'][1] + annual_product_totals[3]['Shomaster'][1] + (sm_annual['2022'] * 2880) + (sm_annual['2021'] * 2880)

            dmx_cntl_tot_unit = dmx_cntl_annual['2022'] + dmx_cntl_annual['2021'] + dmx_cntl_annual['2020'] + dmx_cntl_annual['2019'] + dmx_cntl_annual['2018'] + dmx_cntl_annual['2017'] + dmx_cntl_annual['2016'] + dmx_cntl_annual['2015']
            dmx_cntl_tot_rev = (dmx_cntl_annual['2022'] * 450) + (dmx_cntl_annual['2021'] * 450) + (dmx_cntl_annual['2020'] * 450) + (dmx_cntl_annual['2019'] * 450) + (dmx_cntl_annual['2018'] * 450) + (dmx_cntl_annual['2017'] * 450) + (dmx_cntl_annual['2016'] * 450) + (dmx_cntl_annual['2015'] * 450)

            lcd_tot_unit = lcd_cntl_annual['2022'] + lcd_cntl_annual['2021'] + lcd_cntl_annual['2020'] + lcd_cntl_annual['2019'] + lcd_cntl_annual['2018']
            lcd_tot_rev = (lcd_cntl_annual['2022'] * 450) + (lcd_cntl_annual['2021'] * 450) + (lcd_cntl_annual['2020'] * 450) + (lcd_cntl_annual['2019'] * 450) + (lcd_cntl_annual['2018'] * 450)

            pwr_cntl_tot_unit = pwr_cntl_annual['2021'] + pwr_cntl_annual['2020'] + pwr_cntl_annual['2019'] + pwr_cntl_annual['2018'] + pwr_cntl_annual['2017']
            pwr_cntl_tot_rev = (pwr_cntl_annual['2021'] * 260) + (pwr_cntl_annual['2020'] * 260) + (pwr_cntl_annual['2019'] * 260) + (pwr_cntl_annual['2018'] * 260) + (pwr_cntl_annual['2017'] * 260)
            
            tbmk1_tot_unit = tbmk1_annual['2022'] + tbmk1_annual['2021']
            tbmk1_tot_rev = (tbmk1_annual['2022'] * 360) + (tbmk1_annual['2021'] * 360) 


            cola, colb, colc, cold, cole = st.columns(5)

            colb.subheader('The Button')
            colb.metric('**${:,.2f}**'.format(tb_tot_rev), '{}'.format(tb_tot_unit))
            colb.subheader('The Button MKI')
            colb.metric('**${:,.2f}**'.format(tbmk1_tot_rev), '{}'.format(tbmk1_tot_unit))
            colb.subheader('Power Controller')
            colb.metric('**${:,.2f}**'.format(pwr_cntl_tot_rev), '{}'.format(pwr_cntl_tot_unit))

            colc.subheader('Shostarter')
            colc.metric('**${:,.2f}**'.format(ss_tot_rev), '{}'.format(ss_tot_unit))
            colc.subheader('LCD Controller')
            colc.metric('**${:,.2f}**'.format(lcd_tot_rev), '{}'.format(lcd_tot_unit))

            cold.subheader('Shomaster')
            cold.metric('**${:,.2f}**'.format(sm_tot_rev), '{}'.format(sm_tot_unit))
            cold.subheader('DMX Controller')
            cold.metric('**${:,.2f}**'.format(dmx_cntl_tot_rev), '{}'.format(dmx_cntl_tot_unit))
            cold.subheader('Total Controllers')
            cold.metric('**${:,.2f}**'.format(tbmk1_tot_rev + pwr_cntl_tot_rev + lcd_tot_rev + dmx_cntl_tot_rev + sm_tot_rev + ss_tot_rev + tb_tot_rev), '{}'.format(tbmk1_tot_unit + pwr_cntl_tot_unit + lcd_tot_unit + dmx_cntl_tot_unit + sm_tot_unit + ss_tot_unit + tb_tot_unit))

            style_metric_cards()

            cntl_annual_dict = {'2025': 0, '2024': 0, '2023': 0, '2022': 0, '2021': 0, '2020': 0, '2019': 0, '2018': 0, '2017': 0, '2016': 0, '2015': 0, '2014': 0}
            cntl_annual_dict_seg = {'2025': {'The Button': annual_product_totals[5]['The Button'][0], 'Shostarter': annual_product_totals[5]['Shostarter'][0], 'Shomaster': annual_product_totals[5]['Shomaster'][0]}, '2024': {'The Button': annual_product_totals[4]['The Button'][0], 'Shostarter': annual_product_totals[4]['Shostarter'][0], 'Shomaster': annual_product_totals[4]['Shomaster'][0]}, '2023': {'The Button': annual_product_totals[3]['The Button'][0], 'Shostarter': annual_product_totals[3]['Shostarter'][0], 'Shomaster': annual_product_totals[3]['Shomaster'][0]}, '2022': {'The Button': tbmk2_annual['2022'], 'The Button MKI': tbmk1_annual['2022'], 'Shomaster': sm_annual['2022'], 'LCD Controller': lcd_cntl_annual['2022'], 'DMX Controller': dmx_cntl_annual['2022']}, '2021': {'Power Controller': pwr_cntl_annual['2021'], 'The Button MKI': tbmk1_annual['2021'], 'Shomaster': sm_annual['2021'], 'LCD Controller': lcd_cntl_annual['2021'], 'DMX Controller': dmx_cntl_annual['2021']}, '2020': {'Power Controller': pwr_cntl_annual['2020'], 'LCD Controller': lcd_cntl_annual['2020'], 'DMX Controller': dmx_cntl_annual['2020']}, '2019': {'Power Controller': pwr_cntl_annual['2019'], 'LCD Controller': lcd_cntl_annual['2019'], 'DMX Controller': dmx_cntl_annual['2019']}, '2018': {'Power Controller': pwr_cntl_annual['2018'], 'LCD Controller': lcd_cntl_annual['2018'], 'DMX Controller': dmx_cntl_annual['2018']}, '2017': {'Power Controller': pwr_cntl_annual['2017'], 'DMX Controller': dmx_cntl_annual['2017']}, '2016': {'DMX Controller': dmx_cntl_annual['2016']}, '2015': {'DMX Controller': dmx_cntl_annual['2015']}}
            cntl_annual_dict['2025'] += annual_product_totals[5]['The Button'][0] + annual_product_totals[5]['Shostarter'][0] + annual_product_totals[5]['Shomaster'][0] 
            cntl_annual_dict['2024'] += annual_product_totals[4]['The Button'][0] + annual_product_totals[4]['Shostarter'][0] + annual_product_totals[4]['Shomaster'][0]
            cntl_annual_dict['2023'] += annual_product_totals[3]['The Button'][0] + annual_product_totals[3]['Shostarter'][0] + annual_product_totals[3]['Shomaster'][0]

            cntl_list = [tbmk1_annual, pwr_cntl_annual, lcd_cntl_annual, dmx_cntl_annual, tbmk2_annual, sm_annual]
            year_list = ['2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014']
            
            colx, coly, colz = st.columns([.2, .6, .2])
            with coly:
                plot_bar_chart_product_seg(format_for_chart_product_seg(cntl_annual_dict_seg, 'Total Controller Sales'), 'Total Controller Sales')
            

    elif prod_cat == 'Handhelds':

        td_8nc23, td_8nc24 = to_date_product('CC-HCCMKII-08-NC')
        td_8tc23, td_8tc24 = to_date_product('CC-HCCMKII-08-TC')
        td_15nc23, td_15nc24 = to_date_product('CC-HCCMKII-15-NC')
        td_15tc23, td_15tc24 = to_date_product('CC-HCCMKII-15-TC')

        with col2:
            year = ui.tabs(options=[2025, 2024, 2023, 'Historical'], default_value=2025, key='Handheld Year Select')

        if year == 2025:

            total_hh_rev = annual_product_totals[8]['8FT - No Case'][1] + annual_product_totals[8]['8FT - Travel Case'][1] + annual_product_totals[8]['15FT - No Case'][1] + annual_product_totals[8]['15FT - Travel Case'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4)
        
                cola.subheader('8FT NC')
                cola.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[8]['8FT - No Case'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[8]['8FT - No Case'][0]), '{}'.format(annual_product_totals[8]['8FT - No Case'][0] - td_8nc24))
                cola.metric('', '${:,}'.format(int(annual_product_totals[8]['8FT - No Case'][1])), percent_of_change(annual_product_totals[7]['8FT - No Case'][1], annual_product_totals[8]['8FT - No Case'][1]))
                colb.subheader('8FT TC')
                colb.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[8]['8FT - Travel Case'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[8]['8FT - Travel Case'][0]),  '{}'.format(annual_product_totals[8]['8FT - Travel Case'][0] - td_8tc24))
                colb.metric('', '${:,}'.format(int(annual_product_totals[8]['8FT - Travel Case'][1])), percent_of_change(annual_product_totals[7]['8FT - Travel Case'][1], annual_product_totals[8]['8FT - Travel Case'][1]))
                colc.subheader('15FT NC')
                colc.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[8]['15FT - No Case'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[8]['15FT - No Case'][0]),  '{}'.format(annual_product_totals[8]['15FT - No Case'][0] - td_15nc24))
                colc.metric('', '${:,}'.format(int(annual_product_totals[8]['15FT - No Case'][1])), percent_of_change(annual_product_totals[7]['15FT - No Case'][1], annual_product_totals[8]['15FT - No Case'][1]))
                cold.subheader('15FT TC')
                cold.metric('{:.1f}% of Total Revenue'.format((annual_product_totals[8]['15FT - Travel Case'][1] / td_25_tot) * 100), '{}'.format(annual_product_totals[8]['15FT - Travel Case'][0]),  '{}'.format(annual_product_totals[8]['15FT - Travel Case'][0] - td_15tc24))
                cold.metric('', '${:,}'.format(int(annual_product_totals[8]['15FT - Travel Case'][1])), percent_of_change(annual_product_totals[7]['15FT - Travel Case'][1], annual_product_totals[8]['15FT - Travel Case'][1]))
    
    
                prod_profit_8NC, profit_per_unit_8NC, prod_profit_last_8NC, avg_price_8NC, avg_price_last_8NC = calculate_product_metrics(annual_product_totals, '8FT - No Case', 8, bom_cost_hh)
                prod_profit_8TC, profit_per_unit_8TC, prod_profit_last_8TC, avg_price_8TC, avg_price_last_8TC = calculate_product_metrics(annual_product_totals, '8FT - Travel Case', 8, bom_cost_hh)
                prod_profit_15NC, profit_per_unit_15NC, prod_profit_last_15NC, avg_price_15NC, avg_price_last_15NC = calculate_product_metrics(annual_product_totals, '15FT - No Case', 8, bom_cost_hh)
                prod_profit_15TC, profit_per_unit_15TC, prod_profit_last_15TC, avg_price_15TC, avg_price_last_15TC = calculate_product_metrics(annual_product_totals, '15FT - Travel Case', 8, bom_cost_hh)
                
                tot_hh_rev25 = annual_product_totals[8]['8FT - No Case'][1] + annual_product_totals[8]['8FT - Travel Case'][1] + annual_product_totals[8]['15FT - No Case'][1] + annual_product_totals[8]['15FT - Travel Case'][1]
                tot_hh_prof25 = prod_profit_8NC + prod_profit_8TC + prod_profit_15NC + prod_profit_15TC
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
                
                
                col5.metric('**Revenue**', '${:,.2f}'.format(int(annual_product_totals[8][prod_select][1])), percent_of_change(annual_product_totals[7][prod_select][0], annual_product_totals[8][prod_select][0]))
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
                
                
                col5.metric('**Revenue**', '${:,.2f}'.format(int(annual_product_totals[7][prod_select][1])), percent_of_change(annual_product_totals[6][prod_select][0], annual_product_totals[7][prod_select][0]))
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
            mk2_tot = annual_product_totals[8]['8FT - No Case'][0] + annual_product_totals[8]['8FT - Travel Case'][0] + annual_product_totals[8]['15FT - No Case'][0] + annual_product_totals[8]['15FT - Travel Case'][0] + annual_product_totals[7]['8FT - No Case'][0] + annual_product_totals[7]['8FT - Travel Case'][0] + annual_product_totals[7]['15FT - No Case'][0] + annual_product_totals[7]['15FT - Travel Case'][0] + annual_product_totals[6]['8FT - No Case'][0] + annual_product_totals[6]['8FT - Travel Case'][0] + annual_product_totals[6]['15FT - No Case'][0] + annual_product_totals[6]['15FT - Travel Case'][0]

            for key, val in hhmk1_annual.items():
                mk1_tot += val
            for key, val in hhmk2_annual.items():
                mk2_tot += val

            with col2:
                
                cola, colb, colc = st.columns(3)
        
                cola.metric('**2022**', '{}'.format(hhmk1_annual['2022'] + hhmk2_annual['2022']), (hhmk1_annual['2022'] + hhmk2_annual['2022']) - (hhmk1_annual['2021'] + hhmk2_annual['2021']))
                cola.metric('**2019**', '{}'.format(hhmk1_annual['2019'] + hhmk2_annual['2019']), (hhmk1_annual['2019'] + hhmk2_annual['2019']) - hhmk1_annual['2018'])
                cola.metric('**2016**', '{}'.format(hhmk1_annual['2016']), hhmk1_annual['2016'] - hhmk1_annual['2015'])
                cola.metric('**Total MKII**', '{}'.format(mk2_tot), '')
     
                colb.metric('**2021**', '{}'.format(hhmk1_annual['2021'] + hhmk2_annual['2021']),  (hhmk1_annual['2021'] + hhmk2_annual['2021']) - (hhmk1_annual['2020'] + hhmk2_annual['2020']))
                colb.metric('**2018**', '{}'.format(hhmk1_annual['2018']), hhmk1_annual['2018'] - hhmk1_annual['2017'])
                colb.metric('**2015**', '{}'.format(hhmk1_annual['2015']), hhmk1_annual['2015'] - hhmk1_annual['2014'])
                colb.metric('**2013**', '{}'.format(hhmk1_annual['2013']), '')
                colb.metric('**Total Handhelds Sold**', '{}'.format(mk1_tot + mk2_tot), '')
                
                colc.metric('**2020**', '{}'.format(hhmk1_annual['2020'] + hhmk2_annual['2020']),  (hhmk1_annual['2020'] + hhmk2_annual['2020']) - (hhmk1_annual['2019'] + hhmk2_annual['2019']))
                colc.metric('**2017**', '{}'.format(hhmk1_annual['2017']), hhmk1_annual['2017'] - hhmk1_annual['2016'])
                colc.metric('**2014**', '{}'.format(hhmk1_annual['2014']), hhmk1_annual['2014'] - hhmk1_annual['2013'])
                colc.metric('**Total MKI**', '{}'.format(mk1_tot), '')

                style_metric_cards()

                hh_dict = {}
                
                hh_dict['2025'] = annual_product_totals[8]['8FT - No Case'][0] + annual_product_totals[8]['8FT - Travel Case'][0] + annual_product_totals[8]['15FT - No Case'][0] + annual_product_totals[8]['15FT - Travel Case'][0]
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
            year = ui.tabs(options=[2025, 2024, 2023], default_value=2025, key='Products Year Select')

        cola, colx, coly, colz, colb = st.columns([.15, .23, .23, .23, .15], gap='medium')

        if year == 2025:

            idx = 0
            
            count, magic_dict = magic_sales('2025')

            group1 = [1, 4, 7, 10]
            group2 = [2, 5, 8, 11]
            group3 = [3, 6, 9, 12]
            
            for key, val in magic_dict.items():
                if val[0] >= 1 and key != 'MFX-ECO2JET-BKT':
                    if idx in group1:
                        colx.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))
                    elif idx in group2:
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
                                   options=master_customer_list, 
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
                       'Micro Jet MKI': 0,
                       'Cryo Clamp': 0,
                       'Cryo Clamp MKI': 0,
                       'DMX Jet': 0,
                       'Power Jet': 0, 
                      }
    
    controller_totals_cust = {'The Button': 0,
                              'Shostarter': 0,
                              'Shomaster': 0,
                              'DMX Controller': 0,
                              'LCD Controller': 0,
                              'The Button MKI': 0,
                              'Power Controller': 0,                         
                             }
    
    cust_handheld_mk2_cnt = 0
    cust_handheld_mk1_cnt = 0
    cust_LED_mk2_cnt = 0
    cust_LED_mk1_cnt = 0
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
            elif df.iloc[idx].ordered_year == '2025':
                spend_total_2025 += df.iloc[idx].total_line_item_spend
    
    
    
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
                    cust_LED_mk2_cnt += df.iloc[idx].quantity                    
            elif df.iloc[idx].item_sku[:6] == 'CC-HCC' or df.iloc[idx].item_sku[:6] == 'Handhe':
                handheld_list.append('|    {}    |     ( {}x )    {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    df.iloc[idx].quantity,
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
                cust_handheld_mk2_cnt += df.iloc[idx].quantity
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


    spending_dict, spending_total, cust_jet, cust_hh, cust_cntl, cust_acc = hist_cust_data(text_input)

    df_qb['date'] = df_qb['date'].dt.strftime('%Y-%m-%d')

    
    # ADD IN HISTORICAL PRODUCTS
    for hh, tot in cust_hh.items():
        for sale in tot[1]:
            match = df_qb.loc[(df_qb['customer'] == text_input) & (df_qb['date'] == sale[1])]
            try:
                order_num = match['order_num'].iloc[0]
                handheld_list.append('| {} | {} | ( {}x ) {}'.format(order_num, sale[1], sale[0], hh))
            except:
                handheld_list.append('| {} | ( {}x ) {}'.format(sale[1], sale[0], hh))
    
    for jet, tot in cust_jet.items():
        jet_totals_cust[jet] += tot[0]
        for sale in tot[1]:
            match = df_qb.loc[(df_qb['customer'] == text_input) & (df_qb['date'] == sale[1])]
            try:
                order_num = match['order_num'].iloc[0]
                jet_list.append('| {} | {} | ( {}x ) {}'.format(order_num, sale[1], sale[0], jet))
            except:
                jet_list.append('| {} | ( {}x ) {}'.format(sale[1], sale[0], jet))

    for cntl, tot in cust_cntl.items():
        controller_totals_cust[cntl] += tot[0]
        for sale in tot[1]:
            match = df_qb.loc[(df_qb['customer'] == text_input) & (df_qb['date'] == sale[1])]
            try:
                order_num = match['order_num'].iloc[0]
                controller_list.append('| {} | {} | ( {}x ) {}'.format(order_num, sale[1], sale[0], cntl))
            except:
                controller_list.append('| {} | ( {}x ) {}'.format(sale[1], sale[0], cntl))

    for acc, tot in cust_acc.items():
        for sale in tot[1]:
            match = df_qb.loc[(df_qb['customer'] == text_input) & (df_qb['date'] == sale[1])]
            try:
                order_num = match['order_num'].iloc[0]
                fittings_accessories_list.append('| {} | {} | ( {}x ) {}'.format(order_num, sale[1], sale[0], acc))
            except:
                fittings_accessories_list.append('| {} | ( {}x ) {}'.format(sale[1], sale[0], acc))

    cust_handheld_mk2_cnt += cust_hh['Handheld MKII'][0]
    cust_handheld_mk1_cnt = cust_hh['Handheld MKI'][0]

    cust_LED_mk2_cnt += cust_acc['LED Attachment II'][0]
    cust_LED_mk1_cnt = cust_acc['LED Attachment I'][0]
    
        
    # CALCULATE SPENDING TREANDS
    if 2022 in spending_dict.keys():
        perc_change = percent_of_change(spending_dict[2022], spend_total_2023)
    else:
        perc_change = '100%'
    perc_change1 = percent_of_change(spend_total_2023, spend_total_2024) 
    perc_change2 = percent_of_change(spend_total_2024, spend_total_2025)

    
    with colb:
        st.header('')
        st.subheader('')
    
        ### DISPLAY PRODUCT PURCHASE SUMMARIES FOR SELECTED CUSTOMER ###
        if len(text_input) > 1:
    
            col3, col4, col5 = st.columns(3)
            
            ### DISPLAY CUSTOMER SPENDING TRENDS AND TOTALS
            with col3:
                st.metric('2023 Spending', '${:,.2f}'.format(spend_total_2023), perc_change)
        
            with col4:
                st.metric('2024 Spending', '${:,.2f}'.format(spend_total_2024), perc_change1)
                st.metric('**Total Spending**', '${:,.2f}'.format(spend_total_2023 + spend_total_2024 + spend_total_2025 + spending_total), '')
                
            with col5:
                st.metric('2025 Spending', '${:,.2f}'.format(spend_total_2025), perc_change2)
    
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
                    
            with col8.container(border=True):
                if cust_LED_mk2_cnt > 0:
                    st.markdown(' - **LED Attachment II: {}**'.format(cust_LED_mk2_cnt))
                if cust_LED_mk1_cnt > 0:
                    st.markdown(' - **LED Attachment I: {}**'.format(cust_LED_mk1_cnt))
                if cust_RC_cnt > 0:
                    st.markdown(' - **Road Cases: {}**'.format(cust_RC_cnt))
                if cust_handheld_mk2_cnt > 0:
                    st.markdown(' - **Handheld MKII: {}**'.format(cust_handheld_mk2_cnt))
                if cust_handheld_mk1_cnt > 0:
                    st.markdown(' - **Handheld MKI: {}**'.format(cust_handheld_mk1_cnt))
    
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

        if df.iloc[idx].ordered_year == '2023' or df.iloc[idx].order_date.year == 2023:
            cust_spend_dict_2023[customer] += float(df.iloc[idx].total_line_item_spend)
        elif df.iloc[idx].ordered_year == '2024' or df.iloc[idx].order_date.year == 2024:
            cust_spend_dict_2024[customer] += float(df.iloc[idx].total_line_item_spend)
        elif df.iloc[idx].ordered_year == '2025' or df.iloc[idx].order_date.year == 2025:
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
    


  






















