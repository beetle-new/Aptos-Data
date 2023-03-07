import requests
import pandas as pd
import streamlit as st

def query_api(query):
    url = "https://indexer.mainnet.aptoslabs.com/v1/graphql"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "query": query
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None
# Left column for balance and transaction table
with st.container():
      st.header("Enter owner address")
      owner_address = st.text_input("Owner address", "0xc739507214d0e1bf9795485299d709e00024e92f7c0d055a4c2c39717882bdfd")
      query_balances = f"""
      query {{
        current_coin_balances(
          where: {{owner_address: {{_eq: "{owner_address}"}}}}
        ) {{
          owner_address
          amount
          coin_info {{
            symbol
          }}
        }}
      }}
      """
      data_balances = query_api(query_balances)
      if data_balances:
          df_balances = pd.DataFrame(data_balances['data']['current_coin_balances'])
          df_balances = df_balances.rename(columns={"owner_address": "Owner Address",
                                                  "amount": "Amount",
                                                  "coin_info": "Coin Info"})
          df_balances = pd.concat([df_balances.drop(['Coin Info'], axis=1), df_balances['Coin Info'].apply(pd.Series)], axis=1)
          df_balances['Amount'] = round(df_balances['Amount'] / 100000000, 2)
          df_balances['Amount'] = df_balances['Amount'].apply(lambda x: "{:,.2f}".format(x))
          st.write("Balance Table")
          st.dataframe(df_balances.style.set_table_styles([{'selector': 'th', 'props': [('background-color', '#2F4F4F'),('color', 'white')]}]).set_properties(**{'font-size': '10pt', 'width': '100%', 'overflow-x': 'auto'}))

      query_activities = f"""
      query {{
        coin_activities(
          where: {{owner_address: {{_eq: "{owner_address}"}}, is_transaction_success: {{_eq: true}}}}
        ) {{
          transaction_timestamp
          owner_address
          amount
          activity_type
        }}
      }}
      """
      data_activities = query_api(query_activities)
      if data_activities:
          df_activities = pd.DataFrame(data_activities['data']['coin_activities'])
          df_activities = df_activities.rename(columns={"transaction_timestamp": "Date",
                                                      "owner_address": "Address",
                                                      "amount": "Amount"})
          df_activities['Amount'] = round(df_activities['Amount'] / 100000000, 2)
          df_activities['Amount'] = df_activities['Amount'].apply(lambda x: "{:,.2f}".format(x))
          df_activities['activity_type'] = df_activities['activity_type'].str.split("::").str[-1]
          df_activities['activity_type'] = df_activities['activity_type'].str.rsplit("Event", 1).str[0]
          st.write("Transaction Table")
          st.dataframe(df_activities.style.set_table_styles([{'selector': 'th', 'props': [('background-color', '#2F4F4F'),('color', 'white')]}]).set_properties(**{'font-size': '10pt', 'width': '100%', 'overflow-x': 'auto'}))

# Right column for name search
with st.container():
  st.header("Search for names in sanctions list")
  first_name = st.text_input("First Name", "")
  last_name = st.text_input("Last Name", "")
  sanctions_df = pd.read_csv('consolidated.csv')
  sanctions_df = sanctions_df[(sanctions_df['firstName'].str.contains(first_name, case=False)) &
                              (sanctions_df['lastName'].str.contains(last_name, case=False))]
  sanctions_table = pd.DataFrame(sanctions_df, columns=['firstName', 'lastName', 'sdnType',
  'akaList/aka/0/category','akaList/aka/0/lastName', 'akaList/aka/0/firstName', 
  'akaList/aka/1/category', 'akaList/aka/1/lastName', 'akaList/aka/1/firstName',
  'dateOfBirthList/dateOfBirthItem/dateOfBirth','placeOfBirthList/placeOfBirthItem/placeOfBirth',  'addressList/address/0/stateOrProvince', 'addressList/address/0/country',
  'addressList/address/0/city', 'programList/program/','remarks'])
  st.dataframe(sanctions_table.style.set_table_styles([{'selector': 'th', 'props': [('background-color', '#2F4F4F'),('color', 'white')]}]).set_properties(**{'font-size': '10pt', 'width': '100%', 'overflow-x': 'auto'}))
