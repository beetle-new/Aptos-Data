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


def get_data(owner_address):
    query = f"""
    query MyQuery {{
      coin_activities(
         where: {{owner_address: {{_eq: "{owner_address}"}}, is_transaction_success: {{_eq: true}}, activity_type: {{_neq: "0x1::aptos_coin::GasFeeEvent"}}}}
         order_by: {{transaction_timestamp: desc}}
      ) {{
        transaction_timestamp
        amount
        activity_type
        coin_type
      }}
    }}
    """
    data = query_api(query)
    df = pd.DataFrame(data['data']['coin_activities'])
    df = df.rename(columns={"transaction_timestamp": "Date",
                            "amount": "amount"})

    df['amount'] = round(df['amount'] / 100000000,2)
    df['amount'] = df['amount'].apply(lambda x: "{:,.2f}".format(x))
    df['coin_type'] = df['coin_type'].str.split("::").str[-1]
    df['coin_type'] = df['coin_type'].str.rsplit("Event", 1).str[0]
    df['activity_type'] = df['activity_type'].str.split("::").str[-1]
    df['activity_type'] = df['activity_type'].str.rsplit("Event", 1).str[0]
    return df

owner_address = "0xc739507214d0e1bf9795485299d709e00024e92f7c0d055a4c2c39717882bdfd"
owner_address = st.text_input("Enter an owner address:", value=owner_address)

query = """
query MyQuery {
  current_coin_balances(
    where: {owner_address: {_eq: "%s"}}
  ) {
    owner_address
    amount
    coin_info {
      symbol
    }
  }
}
""" % owner_address

if owner_address:
    data = query_api(query)
    df = pd.DataFrame(data['data']['current_coin_balances'])
    df = df.rename(columns={"owner_address": "owner_address",
                            "amount": "amount",
                            "coin_info": "coin_info"})
    df = pd.concat([df.drop(['coin_info'], axis=1),df['coin_info'].apply(pd.Series)], axis=1)
    ### NOT SURE WHY I HAVE TO DIVIDE BY THIS NUMBER TO GET THE CORRECT VALUE ####
    df['amount'] = round(df['amount'] / 100000000,2)
    df['amount'] = df['amount'].apply(lambda x: "{:,.2f}".format(x))

if owner_address:
    st.table(df)


data = query_api(query)
df2 = pd.DataFrame(data['data']['current_coin_balances'])
df2 = df2.rename(columns={"owner_address": "owner_address",
                        "amount": "amount",
                        "coin_info": "coin_info"})
df2 = pd.concat([df2.drop(['coin_info'], axis=1), df2['coin_info'].apply(pd.Series)], axis=1)
df2['amount'] = round(df2['amount'] / 100000000, 2)
df2['amount'] = df2['amount'].apply(lambda x: "{:,.2f}".format(x))
st.table(df2)
