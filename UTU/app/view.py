from app import app
from flask import render_template, url_for, request, jsonify, flash, redirect, session
import pandas as pd
import numpy as np
import os
import json
from pymongo import MongoClient
from app.connect import Connect

## Global variable

client = Connect.get_connection()

mydb = client["cryptocurrency"]

mycol = mydb["currencydata"]

# read from mongoDB
df = pd.DataFrame(list(mycol.find()))

# replace ','
df = df.apply(lambda x: x.str.replace(r',', ''))

# get all the date
date_list = df['Date'].unique().tolist()


@app.route('/')
def home():

    #make a copy of original data file and set data types
    df2 = set_data_type(df.copy())
    
    # create a new DataFrame to contain the list for display.
    df_displayList_copy = copy_DataFrame()

    #set current date
    current_date = date_list[0]

    # list of currency names, no repeat
    session["currency_list"] = df2["Currency"].unique().tolist()
    currency_list = session["currency_list"]

    # loop through the list and get the results by calling the calculation method.
    for i in range(len(currency_list)):
        result = calculation(df2, currency_list[i], current_date)
        df_displayList_copy = df_displayList_copy.append(result, ignore_index=True)

    # call sort method to sort the data in descending order
    sorted_result = sort(df_displayList_copy, 'Mkt Cap', False)

    # return the web page with a 'list' like dictionary.
    return render_template('home.html', lists=sorted_result.to_dict('records'), date_list=date_list)


@app.route('/datepicker', methods=['POST'])
def datepicker():

    #make a copy of original data file and set data types
    df2 = set_data_type(df.copy())

    selected_date = ''

    if request.method == 'POST':

        # getting the data than comes from JS
        req = request.get_json() 

        # store the selected date
        selected_date = req['selected_date']

        # date_list = session["date_list"]
        df_displayList_copy = copy_DataFrame()

        # retrieve currency list from session variable
        currency_list = session["currency_list"]

        # loop through the list and get the results by calling the calculation method.
        for i in range(len(currency_list)):
            result = calculation(df2, currency_list[i], selected_date)
            df_displayList_copy = df_displayList_copy.append(result, ignore_index=True)
            df_displayList_copy['dateofdata'] = selected_date

        sorted_result = sort(df_displayList_copy, 'Mkt Cap', False)

    return sorted_result.to_dict()


def copy_DataFrame():
    df_displayList = pd.DataFrame(columns = ["currency", "price", "24h", "7d", "30d", "24h Volume", "Mkt Cap", "24h color", "7d color", "30d color"])
    df = df_displayList.copy()
    return df


def set_data_type(df):

    # setting data type of each column
    df['Date'] = pd.to_datetime(df['Date'])
    df['Open'] = df['Open'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['Volume'] = df['Volume'].astype(int)
    df['Market Cap'] = df['Market Cap'].astype(int)

    return df


def calculation(df, name, current_date):

    # getting all results with the 'name'
    df_calculation = df[df['Currency'] == name]

    # filter result with the date
    df_calculation = df_calculation[df_calculation["Date"] <= current_date]

    # make it as dictionary
    df_calculation = df_calculation.to_dict('list')

    color_24h = ""
    color_7d = ""
    color_30d = ""
    tfh = 0.0 # 24h
    sd = 0.0 # 7d
    td = 0.0 # 30d

    #### Calculated by Close Market Value.

    # using try method to avoid error for 24h Vloume, Market Cap and Price
    # as there might no data for that date.
    try:
        tfhV = f"${df_calculation['Volume'][0]:,}" # 24h Volume
        cap = df_calculation['Market Cap'][0] # Market Cap
        price = f"${df_calculation['Close'][0]}" # Price
    except Exception as e:
        tfhV = f"-"
        cap = f"-"
        price = f"-"

    # 24h difference
    try:
        # check if there is 24 hours
        if pd.Timedelta(df_calculation['Date'][0] - df_calculation['Date'][1]) / pd.Timedelta(hours=1) == 24:
            # the Close value of the selected date - the Close value 24 hours before / the Close value 24 hours before * 100
            tfh = round(((df_calculation['Close'][0] - df_calculation['Close'][1]) / df_calculation['Close'][1]) * 100, 1)
            if tfh < 0:
                color_24h = "red"
            elif tfh > 0:
                color_24h = "green"

            tfh = f"{tfh}%"
    except Exception as e:
        tfh = f"-"

    # 7d difference
    try:
        # check if there is 7 days
        if pd.Timedelta(df_calculation['Date'][0] - df_calculation['Date'][7]).days == 7:
            # the Close value of the selected date - the Close value 7 days before / the Close value 7 days before * 100
            sd = round(((df_calculation['Close'][0] - df_calculation['Close'][7]) / df_calculation['Close'][7]) * 100, 1)
            if sd < 0:
                color_7d = "red"
            elif sd > 0:
                color_7d = "green"
            
            sd = f"{sd}%"

    except Exception as e:
        sd = f"-"

    # 30d difference
    try:
        # check if there is 30 days
        if pd.Timedelta(df_calculation['Date'][0] - df_calculation['Date'][30]).days == 30:
            # the Close value of the selected date - the Close value 30 days before / the Close value 30 days before * 100
            td = round(((df_calculation['Close'][0] - df_calculation['Close'][30]) / df_calculation['Close'][30]) * 100, 1)
            if td < 0:
                color_30d = "red"
            elif td > 0:
                color_30d = "green"

            td = f"{td}%"
    except Exception as e:
        td = f"-"

    return pd.Series({"currency":name, "price":price, "24h":tfh, "7d":sd, "30d":td, "24h Volume":tfhV, "Mkt Cap":cap, "24h color": color_24h, "7d color":color_7d, "30d color":color_30d})


def sort(df, by, ascending_order):
    # drop rows that has "-" in Market Cap
    df = df[df[by] != '-']

    # re-ordering by Market Cap in ascending order
    df = df.sort_values(by=[by], ascending=ascending_order)

    # put the '$' and ',' into the number and make it a string.
    df[by] = df[by].apply(lambda x: "${:,}".format(x))

    # re-assigning the index
    df = df.reset_index(drop=True)

    # increase the current index by 1
    df.index += 1

    # assigning index number to a variable
    new_index = df.index

    # adding a new column call index as the current index cannot be used in html for loop
    df.insert(0, column='index', value=new_index)

    return df

