# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 10:43:31 2019

@author: raiak
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta, TH

def optionChain (expirydate):

    urlheader = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
      "authority": "www.nseindia.com",
      "scheme":"https"
    }
    
    url="https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?"
    params="segmentLink=17&instrument=OPTIDX&symbol=NIFTY&date="
    expirydate="3OCT2019"
    
    url_encoded=url + params + expirydate
    
    req = requests.get(url_encoded, headers=urlheader)
    soup = BeautifulSoup(req.content, "lxml")
    table = soup.find('table', id="octable")
    
    rows = table.findAll('tr')
    header_text = []
    headers = rows[1]
    
    remove_indices_for_put = [0,1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,18,22]
    remove_indices_for_call = [0,4,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22]
     # Creating an empty Dataframe with column names only
    
    
    # add the header text to array
    for th in headers.findAll('th'):
        header_text.append(th.text)
    
    header_text = [i for j, i in enumerate(header_text) if j not in remove_indices_for_put]
    df_call = pd.DataFrame(columns=header_text)
    df_put = pd.DataFrame(columns=header_text)
    
    #row_text_array = []
    for row in rows[2:-1]:
        row_text = []
        row_text_call = []
        row_text_put = []
        # loop through the elements
        for row_element in row.findAll(['th', 'td']):
            # append the array with the elements inner text
            row_text.append(row_element.text.replace('\n', '').strip())
    
        # append the text array to the row text array
        row_text_put = [i for j, i in enumerate(row_text) if j not in remove_indices_for_put]
        for i in range(len(row_text_put)):
            if (row_text_put[i]=='-'):
                row_text_put[i]=0
            else:
                row_text_put[i]=row_text_put[i].replace(',', '')
                row_text_put[i]=float(row_text_put[i])
        row_text_call = [i for j, i in enumerate(row_text) if j not in remove_indices_for_call]
        row_call_temp=[None] * len(row_text_call)
        for i in range(len(row_text_call)):       
            if (row_text_call[i]=='-'):
                row_call_temp[len(row_text_call)-i-1]=0
            else:
                row_text_call[i]=row_text_call[i].replace(',', '')
                row_text_call[i]=float(row_text_call[i])
                row_call_temp[len(row_text_call)-i-1]=row_text_call[i]
        df_call = df_call.append(pd.Series(dict(zip(df_call.columns, row_call_temp))), ignore_index=True)
        df_put = df_put.append(pd.Series(dict(zip(df_put.columns, row_text_put))), ignore_index=True)    
        
        
    df_call['OI'] = pd.to_numeric(df_call['OI'])
    df_call=df_call.nlargest(3, ['OI'])
    df_call.set_index('Strike Price', inplace=True)
    print("Top 3 Strike price of Call Option based on Open Interest")
    print(df_call)
    print("================================================================================") 
    df_put['OI'] = pd.to_numeric(df_put['OI'])
    df_put=df_put.nlargest(3, ['OI'])
    df_put.set_index('Strike Price', inplace=True)
    print("Top 3 Strike price of Put Option based on Open Interest")
    print(df_put)

       
        
    return(df_call,df_put)

    

def nextThu_and_lastThu_expiry_date ():

    todayte = datetime.today()
    
    cmon = todayte.month
    if_month_next=(todayte + relativedelta(weekday=TH(1))).month
    next_thursday_expiry=todayte + relativedelta(weekday=TH(1))
   
    if (if_month_next!=cmon):
        month_last_thu_expiry= todayte + relativedelta(weekday=TH(5))
        if (month_last_thu_expiry.month!=if_month_next):
            month_last_thu_expiry= todayte + relativedelta(weekday=TH(4))
    else:
        for i in range(1, 7):
            t = todayte + relativedelta(weekday=TH(i))
            if t.month != cmon:
                # since t is exceeded we need last one  which we can get by subtracting -2 since it is already a Thursday.
                t = t + relativedelta(weekday=TH(-2))
                month_last_thu_expiry=t
                break
    str_month_last_thu_expiry=str(int(month_last_thu_expiry.strftime("%d")))+month_last_thu_expiry.strftime("%b").upper()+month_last_thu_expiry.strftime("%Y")
    str_next_thursday_expiry=str(int(next_thursday_expiry.strftime("%d")))+next_thursday_expiry.strftime("%b").upper()+next_thursday_expiry.strftime("%Y")
    return (str_next_thursday_expiry,str_month_last_thu_expiry)


str_next_thursday_expiry,str_month_last_thu_expiry=nextThu_and_lastThu_expiry_date()
print("================================================================================")
print("Call/Put Option data of next Thursday expiry =  "+str_next_thursday_expiry)
df_call_near_expiry,df_put_near_expiry=optionChain(str_next_thursday_expiry)
print("================================================================================")
print("Call/Put Option data of last Thursday of a month expiry =  "+str_month_last_thu_expiry)
df_put_near_expiry,df_put_last_expiry=optionChain(str_month_last_thu_expiry)
print("================================================================================")

