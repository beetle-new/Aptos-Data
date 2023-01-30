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


owner_address = st.text_input("Enter an owner address:", default="0xc739507214d0e1bf9795485299d709e00024e92f7c0d055a4c2c39717882bdfd")
if owner_address:
    df = get_data(owner_address)
    st.write(df,width=800)
