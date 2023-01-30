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

# Add user input for the filter owner_address
owner_address = st.text_input("Enter an owner_address:", "0xc739507214d0e1bf9795485299d709e00024e92f7c0d055a4c2c39717882bdfd")

# Replace the fixed filter value with the user input
query = f"""
query MyQuery {{
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

data = query_api(query)
df = pd.DataFrame(data['data']['current_coin_balances'])
df = df.rename(columns={"owner_address": "owner_address",
                        "amount": "amount",
                        "coin_info": "coin_info"})
df = pd.concat([df.drop(['coin_info'], axis=1), df['coin_info'].apply(pd.Series)], axis=1)

### NOT SURE WHY I HAVE TO DIVIDE BY THIS NUMBER TO GET THE CORRECT VALUE ####
df['amount'] = round(df['amount'] / 100000000,2)
df['amount'] = df['amount'].apply(lambda x: "{:,.2f}".format(x))
st.write(df)


# Replace the fixed filter value with the user input
query = f"""
query MyQuery {{
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

data = query_api(query)
df = pd.DataFrame(data['data']['coin_activities'])
df = df.rename(columns={"transaction_timestamp": "Date",
                        "owner_address": "Address",
                        "amount": "amount"})

df['amount'] = round((df['amount'] / 100000000),2)
df['amount'] = df['amount'].apply(lambda x: "{:,.2f}".format(x))
df['activity_type'] = df['activity_type'].str.split("::").str[-1]
df['activity_type'] = df['activity_type'].str.rsplit("Event", 1).str[0]

owner_address = st.text_input("Enter the owner address: ")

query = f"""
query MyQuery {{
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

data = query_api(query)
df = pd.DataFrame(data['data']['coin_activities'])
df = df.rename(columns={"transaction_timestamp": "Date",
"owner_address": "Address",
"amount": "txn_amount"})

df['txn_amount'] = round((df['txn_amount'] / 100000000),2)
df['txn_amount'] = df['txn_amount'].apply(lambda x: "{:,.2f}".format(x))
df['activity_type'] = df['activity_type'].str.split("::").str[-1]
df['activity_type'] = df['activity_type'].str.rsplit("Event", 1).str[0]
st.table(df)
