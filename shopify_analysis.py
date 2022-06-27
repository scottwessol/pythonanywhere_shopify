import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, dash_table
from datetime import date, datetime
import os
import sys

# Create analysis for part numbers/orders as a whole and then filter by tags
# interactive charts with plotly?

pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None

# def dash_plotly(top_sku, sprayer_selection, data):
#     app = Dash(__name__)

#     selection = ['Top 5', 'Top 10', 'Top 20']

#     app.layout = html.Div(children=[
#         html.Div([
#             html.H2('Warranty Claims'),
#             dcc.Graph(id='graph_1'),
#             dcc.Checklist(id='checklist',
#                           options=top_sku,
#                           value=top_sku[:10],
#                           inline=True),
#             ]),
#         html.Div([
#             html.H2('YoY Comparison'),
#             dcc.Graph(id='graph_comp'),
#             dcc.RadioItems(id='radio_1',
#                       options=top_sku,
#                       value=top_sku[0],
#                       inline=True)
#         ]),
#         html.Div([
#             html.H2('Sprayers Warranteed'),
#             dcc.Graph(id='graph_3'),
#             dcc.Checklist(id='checklist_2',
#                           options=sprayer_selection,
#                           value=sprayer_selection,
#                           inline=True),
#         ]),
#         html.Div([
#             html.H2('Total Claims'),
#             dcc.Graph(id='graph_2'),
#             dcc.RadioItems(id='radio',
#                           options=['Top 5', 'Top 10', 'Top 20'],
#                           value='Top 10',
#                           inline=True)
#         ]),
#         html.Div([
#             html.H2('Data'),
#             html.H4('Sorted by top 20 claimed part numbers in the previous month'),
#             html.P('All time highest claimed part numbers shown along with top 20 from the previous month'),
#             dash_table.DataTable(data=data.to_dict('records'),
#                                  sort_action='native')
#         ])

#     ])

#     @app.callback(
#         Output('graph_1', 'figure'),
#         Input('checklist', 'value'))
#     def update_line_chart(top_sku):
#         df = parse_line_chart(20)
#         mask = df.SKU.isin(top_sku)
#         # print(df)
#         fig = px.line(df[mask], x='Date', y='Quantity', color='SKU', markers=True)
#         return fig

#     @app.callback(
#         Output('graph_3', 'figure'),
#         Input('checklist_2', 'value'))
#     def update_sprayer_chart(sprayer_selection):
#         df = parse_sprayers_only(sprayer_selection)
#         mask = df.SKU.isin(sprayer_selection)
#         fig = px.line(df[mask], x='Date', y='Quantity', color='SKU', markers=True)
#         return fig

#     @app.callback(
#         Output('graph_2', 'figure'),
#         Input('radio', 'value'))
#     def update_bar_chart(selection):
#         if selection == 'Top 10':
#             num = 10
#         elif selection == 'Top 5':
#             num = 5
#         else: num = 20
#         df, line_df = parse_bar_chart(num)

#         fig = make_subplots(specs=[[{"secondary_y": True}]])
#         fig.add_trace(go.Bar(x=df.index, y=df.values))
#         fig.add_trace(go.Scatter(x=line_df.index, y=line_df.values), secondary_y=True)

#         return fig

#     @app.callback(
#         Output('graph_comp', 'figure'),
#         Input('radio_1', 'value'))
#     def update_comparison_chart(sku):
#         # parse by entered sku
#         df = parse_line_chart(20)
#         today = date.today().year
#         #print(today)
#         #
#         df_prev = df.loc[df['Year'] == today-1]
#         df_curr = df.loc[df['Year'] == today]
#         #print(df_prev)
#         mask_prev = df_prev.SKU.isin([sku])
#         mask = df_curr.SKU.isin([sku])

#         #print(df_prev[mask_prev])
#         #print(df_curr[mask])

#         fig = make_subplots(specs=[[{"secondary_y": True}]])
#         fig.add_trace(go.Scatter(x=df_prev[mask_prev].Month, y=df_prev[mask_prev].Quantity, name=today-1))
#         fig.add_trace(go.Scatter(x=df_curr[mask].Month, y=df_curr[mask].Quantity, name=today))
#         return fig


#     app.run_server(debug=True)


def parse_bar_chart(num, main_df):
    # Plot total warranty shipments
    #main_df = read_data()

    warranty_df = main_df[main_df['Tags'].str.contains('warr|Warr|WARR', na=False)]

    # Group data by SKU
    warranty_df['SKU'] = warranty_df['SKU'].str[:6]

    all_claims = warranty_df.groupby('SKU')['Quantity'].sum()
    all_claims = all_claims.sort_values(ascending=False)
    claims = all_claims[:num]
    trunc_total = claims.sum()
    line_df = claims.divide(trunc_total)
    cum_sum = 0
    i = 0
    while i < num:
        cum_sum += line_df[i] * 100
        line_df[i] = cum_sum
        i += 1
    #print(line_df)
    return claims, line_df

def parse_line_chart(num, main_df):
    # Plot total warranty shipments
    # main_df = read_data()

    warranty_df = main_df[main_df['Tags'].str.contains('warr|Warr|WARR', na=False)]

    # Group data by month
    warranty_df['Date'] = warranty_df['Date'].str[:7]
    print(warranty_df['Date'])
    warranty_df['Date'] = pd.to_datetime(warranty_df['Date'])
    warranty_df['SKU'] = warranty_df['SKU'].str[:6]

    total_claims = warranty_df.groupby('SKU')['Quantity'].sum()

    # this gives creates the key for descending qty of total claims - can change to top xx value
    total_claims = total_claims.sort_values(ascending=False)
    keys = list(total_claims[:num].keys())
    key_string = ''
    # Build string in right format for contains() function - use OR operator
    for key in keys:
        key_string = key_string + '|' + key
    key_string = key_string[1:]


    df = warranty_df[warranty_df['SKU'].str.contains(key_string)==True]

    # Create group sorted first by date and then by SKU of shipments each month
    groups = df.groupby(['SKU', 'Date'])['Quantity'].sum()

    dfs = []
    # Create line plot including each of the top xx part numbers
    for key in keys:
        df_temp = groups[key].to_frame()
        df_temp['SKU'] = key
        df_temp = df_temp.rename(columns={0:'Quantity'})
        df_temp = df_temp.reset_index(level=['Date'])
        dfs.append(df_temp)
        # plt.plot(groups[key], label=key)
    result_df = pd.concat(dfs)
    result_df['Year'] = pd.DatetimeIndex(result_df['Date']).year
    result_df['Month'] = pd.DatetimeIndex(result_df['Date']).month

    return result_df

def cumulative_line_chart(main_df):
    # Plot total warranty shipments not separated by SKU

    # Add dummy claim so that there is a claim in Jan 2021
    jan_claim = ['325527679815','FZ242102','certifiedoutdoors@gmail.com','8722 A D Mims Rd','Orlando','FL','32818','US','2021-01-10','0','Warranty','0','0.0','FZRABZ,Battery Cover',1,'6.49']
    main_df.iloc[0] = jan_claim

    warranty_df = main_df[main_df['Tags'].str.contains('warr|Warr|WARR', na=False)]

    # Group data by month
    warranty_df['Date'] = warranty_df['Date'].str[:7]
    print(warranty_df)
    warranty_df['Date'] = pd.to_datetime(warranty_df['Date'])

    total_claims = warranty_df.groupby('Date')['Quantity'].sum()

    if len(total_claims) > 24:
    # reduce to max of 2 years of data
        slice_loc = len(total_claims) - 24
        total_claims = total_claims[slice_loc:]
    prev_year = pd.Series(data=total_claims[:12].values, index=total_claims[:12].index)
    this_year = total_claims[12:]


    return prev_year, this_year

def parse_sprayers_only(sprayer_selection, main_df):
    # Plot total warranty shipments
    # main_df = read_data()

    warranty_df = main_df[main_df['Tags'].str.contains('warr|Warr|WARR', na=False)]

    # Group data by month
    warranty_df['Date'] = warranty_df['Date'].str[:7]
    warranty_df['Date'] = pd.to_datetime(warranty_df['Date'])
    warranty_df['SKU'] = warranty_df['SKU'].str[:6]
    skus = sprayer_selection

    # Build string in right format for contains() function - use OR operator
    sku_string = ''
    for sku in skus:
        sku_string = sku_string + '|' + sku
    sku_string = sku_string[1:]


    df = warranty_df[warranty_df['SKU'].str.contains(sku_string)==True]

    # Create group sorted first by date and then by SKU of shipments each month
    groups = df.groupby(['SKU', 'Date'])['Quantity'].sum()

    dfs = []
    # Create line plot including each of the top xx part numbers
    for sku in skus:
        df_temp = groups[sku].to_frame()
        df_temp['SKU'] = sku
        df_temp = df_temp.rename(columns={0:'Quantity'})
        df_temp = df_temp.reset_index(level=['Date'])
        dfs.append(df_temp)
        # plt.plot(groups[key], label=key)
    result_df = pd.concat(dfs)
    # print(result_df)
    return result_df
    #fig = px.line(result_df, x='Date', y='Quantity', color='SKU', markers=True)
    #fig.show()

    # plt.xticks(rotation=90)
    # plt.legend()
    # plt.show()

def parse_month(main_df):
    # Look at total sales on website
    # main_df = read_data()

    #warranty_df = main_df[main_df['Tags'].str.contains('warr|Warr|WARR', na=False)]

    # Group data by month
    main_df['Date'] = main_df['Date'].str[:7]
    main_df['Date'] = pd.to_datetime(main_df['Date'])

    total_claims = main_df.groupby('SKU')['Quantity'].sum()

    # this gives creates the key for descending qty of total claims
    total_claims = total_claims.sort_values(ascending=False)

    keys = list(total_claims[:10].keys())
    key_string = ''
    for key in keys:
        key_string = key_string + '|' + key

    key_string = key_string[1:]
    # print(key_string)

    df = main_df[main_df['SKU'].str.contains(key_string) == True]

    # print(df)

    # Create group sorted first by date and then by SKU of shipments each month
    groups = df.groupby(['SKU', 'Date']).size()

    # print(len(groups))
    # groups = groups[:40]

    for key in keys:
        #fig = px.line(key, x='Date', y='Count')
        plt.plot(groups[key], label=key)
    plt.xticks(rotation=90)
    plt.legend()
    #plt.show()

def get_skus(num, main_df):

    warranty_df = main_df[main_df['Tags'].str.contains('warr|Warr|WARR', na=False)]
    warranty_df['SKU'] = warranty_df['SKU'].str[:6]
    #print(warranty_df['Date'])
    warranty_df['Date'] = pd.to_datetime(warranty_df['Date'])

    total_claims = warranty_df.groupby('SKU')['Quantity'].sum()
    total_claims = total_claims.sort_values(ascending=False)
    total_claims = total_claims[:num]

    month = datetime.now().month - 1
    if month == 0:
        month = 12
        year = datetime.now().year - 1
    else:
        year = datetime.now().year
    last_month = datetime.now().replace(day=1, month=month, year=year)
    this_month = datetime.now().replace(day=1)
    # print(last_month)
    last_month_claims = warranty_df.loc[warranty_df['Date'] > last_month]
    last_month_claims = last_month_claims.loc[last_month_claims['Date'] < this_month]
    last_month_claims = last_month_claims.groupby('SKU')['Quantity'].sum()
    last_month_claims = last_month_claims.sort_values(ascending=False)
    last_month_claims = last_month_claims[:num]
    last_month_claims = pd.concat([last_month_claims, total_claims], axis=1)
    last_month_claims.columns = ['Last Month', 'Total']
    last_month_claims.reset_index(inplace=True)
    # print(last_month_claims)
    # Cross reference part names

    name_df = pd.read_csv(u'/home/scottwessol/mysite/part_names.csv')
    name_df.columns = ['SKU', 'Description']
    # print(name_df)
    descriptions = []

    #last_month_claims= last_month_claims.rename(columns={'index':'SKU'})
    for index, row in last_month_claims.iterrows():
        #print(row['SKU'])

        name_row = name_df.loc[name_df['SKU']==row['SKU']]

        try:
            descriptions.append(name_row['Description'].values[0])
        except IndexError:
            descriptions.append('***Part Name not in database')

    last_month_claims['Description'] = descriptions
    last_month_claims = last_month_claims[['SKU', 'Description', 'Last Month', 'Total']]
    return list(total_claims.keys()), last_month_claims
