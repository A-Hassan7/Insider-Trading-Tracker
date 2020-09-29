import dash
import json
import pandas as pd
from visualisations import Visualise
from app_components.layout import layout
from app_components.chart_components import ChartComponents
from app_components.control_components import ControlComponents
from dash.dependencies import Input, Output, State


vis = Visualise()
chart_components = ChartComponents()
control_components = ControlComponents()

app = dash.Dash(__name__)
app.layout = layout


# Getting data if submit button clicked
@app.callback(
    [
        Output('stored_transactions', 'children'),
        Output('stored_insider_stats', 'children'),
        Output('stored_volatility_stats', 'children'),
        Output('stored_performence_stats', 'children'),
        Output('stored_price_data', 'children'),
    ],
    [
        Input('submit_button', 'n_clicks'),
        State('input_ticker', 'value'),
        State('date_from', 'date'),
        State('date_to', 'date'),
    ]
)
def get_data(submit, ticker, to_date, from_date):
    '''get data'''
    # log to progress
    control_components.progress('retrieving data...')
    out = []
    from_date, to_date = from_date[:10], to_date[:10]
    # get data from Statistics.py
    data = vis.get_stats(ticker, from_date, to_date)
    [out.append(i) for i in data]

    return [i.to_json(date_format='iso', orient='split') for i in out]


# populate insiders selector
@app.callback(
    [
        Output('insider_filter_dropdown', 'options'),
        Output('insider_filter_dropdown', 'value')
    ],
    [
        Input('stored_insider_stats', 'children'),
        Input('insider_filter_radio', 'value')
    ]
)
def populate_insiders_dropdown(stored_insider_stats, insider_filter_radio):
    '''populate insiders filter dropdown with all insider names'''
    # read transactions
    insiders = pd.read_json(stored_insider_stats, orient='split').insider.values
    options = [{'label': i, 'value': i} for i in insiders]
    select = insiders if insider_filter_radio == 'all' else []

    return options, select


# filter transactions based on filters
@app.callback(
    [
        Output('filtered_transactions', 'children'),
        Output('filtered_insider_stats', 'children'),
        Output('filtered_volatility_stats', 'children'),
        Output('filtered_performence_stats', 'children'),
    ],
    [
        Input('stored_transactions', 'children'),
        Input('insider_filter_dropdown', 'value'),
        Input('filter_market_trades_checkbox', 'value'),
        Input('filter_buys', 'value'),
        Input('filter_sells', 'value'),
        Input('filter_button', 'n_clicks'),
        State('input_ticker', 'value'),
        State('date_from', 'date'),
        State('date_to', 'date'),
        State('filter_transactions_unit', 'value'),
        State('filter_transactions_operator', 'value'),
        State('filter_transactions_value', 'value'),
        State('filter_transactions_value_type', 'value')

    ]
)
def filter(stored_transactions, insider_filter, filter_market_trades,
           filter_buys, filter_sells, filter_button, ticker, to_date,
           from_date, filter_units, filter_operator, filter_value, filter_value_type):
    '''filter transactions and stats based on filter criteria'''

    # log to progress
    control_components.progress('filtering transactions...')

    filter_market_trades = True if 'filter' in filter_market_trades else False

    # if filter button clicked
    ctx = dash.callback_context.triggered[0]['prop_id']
    if ctx == 'filter_button.n_clicks':
        # all filter values must be entered
        filter_size = [filter_units, filter_operator, filter_value, filter_value_type]
        filter_size = None if None in filter_size else filter_size
    else:
        filter_size = None

    # filter buys and sells
    filter_buys = None if not filter_buys else 'P'
    filter_sells = None if not filter_sells else 'S'
    filter_side = [filter_buys, filter_sells]
    if None in filter_side:
        filter_side.remove(None)
    else:
        filter_side = [None]

    # pass filteres
    data = vis.get_stats(
        ticker=ticker,
        from_date=from_date[:10],
        to_date=to_date[:10],
        filter_insiders=insider_filter,
        filter_open_market=filter_market_trades,
        filter_side=filter_side[0],
        filter_size=filter_size,
        filter_only=True)

    jsons = [i.to_json(date_format='iso', orient='split') for i in data[:4]]

    filtered_transactions, filtered_insider_stats, filtered_volatility_stats, filtered_performence_stats = jsons

    # log to progress
    control_components.progress('None')

    out = [
        filtered_transactions,
        filtered_insider_stats,
        filtered_volatility_stats,
        filtered_performence_stats,
    ]

    return [i for i in out]


# Transactions tab
@app.callback(
    [
        Output('ohlc_chart', 'figure'),
        Output('num_transactions', 'children'),
        Output('num_insiders', 'children'),
        Output('total_buy_vol', 'children'),
        Output('total_sell_vol', 'children'),
        Output('spy_chart', 'figure'),
        Output('vix_chart', 'figure'),
        Output('transactions_table', 'children')

    ],
    [
        Input('filtered_transactions', 'children'),
        Input('stored_price_data', 'children'),
        Input('volume_type_radio', 'value'),
        Input('volume_type_spy_radio', 'value'),
        Input('volume_type_vix_radio', 'value'),
        Input('volume_type_details_radio', 'value')
    ]
)
def transaction_charts(filtered_transactions, stored_price_data,
                       volume_type_transactions, volume_type_spy, volume_type_vix,
                       volume_type_details):
    '''draw ohlc chart and update details'''

    # log to progress
    control_components.progress('generating transaction charts...')

    # read stored transactions and price data
    transactions = pd.read_json(filtered_transactions, orient='split')
    price_data = pd.read_json(stored_price_data, orient='split')

    # convert dates to datetime
    transactions['transaction_period'] = pd.to_datetime(transactions.transaction_period)
    transactions['report_period'] = pd.to_datetime(transactions.report_period)
    price_data.index = pd.to_datetime(price_data.index)

    # create ohlc chart
    ohlc_chart, details = vis.ohlc_chart(transactions, price_data, volume_type=volume_type_transactions)

    # ohlc details
    num_transactions = details['num_transactions']
    num_insiders = details['num_insiders']
    if volume_type_details == 'shares':
        total_buy_vol = details['total_buy_vol']
        total_sell_vol = abs(details['total_sell_vol'])
    else:
        total_buy_vol = f"$ {int(details['total_buy_vol_dollar'])}"
        total_sell_vol = f"$ {abs(int(details['total_sell_vol_dollar']))}"

    spy_chart, vix_chart = vis.index_comparison(transactions, volume_type_spy, volume_type_vix)

    # log to progress
    control_components.progress('generating transaction table...')
    transactions_table = chart_components.generate_table(transactions, max_rows=100000000)

    # log to progress
    control_components.progress('None')

    out = [
        ohlc_chart,
        num_transactions,
        num_insiders,
        total_buy_vol,
        total_sell_vol,
        spy_chart,
        vix_chart,
        transactions_table
    ]

    return [i for i in out]


# insider tab
@app.callback(
    [
        Output('total_volume', 'figure'),
        Output('position_delta', 'figure'),
        Output('position_rotation', 'figure'),
        Output('trade_count', 'figure')
    ],
    [
        Input('filtered_insider_stats', 'children'),
        Input('total_volume_radio', 'value'),
        Input('position_delta_radio', 'value')
    ]
)
def get_insider_analysis(filtered_insider_stats, total_volume_radio, position_delta_radio):

    insider_stats = pd.read_json(filtered_insider_stats, orient='split')
    total_volume_col = 'total_volume' if total_volume_radio == 'shares' else 'total_volume_dollar'

    # position delta col
    if position_delta_radio == 'shares':
        position_delta_col = 'position_delta'
    elif position_delta_radio == 'notional':
        position_delta_col = 'position_delta_dollar'
    else:
        position_delta_col = 'position_delta_percentage'

    # log to progress
    control_components.progress('generating insider charts...')

    total_volume = vis.insider_chart(insider_stats, total_volume_col)
    position_delta = vis.insider_chart(insider_stats, position_delta_col)
    position_rotation = vis.insider_chart(insider_stats, 'position_rotation')
    trade_count = vis.insider_chart(insider_stats, 'trade_count')

    # log to progress
    control_components.progress('None')

    return total_volume, position_delta, position_rotation, trade_count


# Analysis tab
@app.callback(
    [
        Output('volatility_chart', 'figure'),
        Output('performance_chart', 'figure')
    ],
    [
        Input('filtered_performence_stats', 'children'),
        Input('filtered_volatility_stats', 'children')
    ]
)
def stats(filtered_performance, filtered_volatility):
    '''get volatility and performance charts'''
    # read in stores stats
    performance_stats = pd.read_json(filtered_performance, orient='split')

    json_ = json.loads(filtered_volatility)
    # create dummy data and index if empty
    if not json_['index']:
        json_['index'].append([(float('NaN'), 'pre'), (float('NaN'), 'post')])
        json_['data'].append([float('NaN')] * len(json_['columns']))
        index = pd.MultiIndex.from_tuples(json_['index'][0])
    else:
        index = pd.MultiIndex.from_tuples(json_['index'])
    volatility_stats = pd.DataFrame(json_['data'], index, json_['columns'])

    # log to progress
    control_components.progress('generating analysis...')

    # get charts
    performance = vis.performance_chart(performance_stats)
    volatility = vis.volatility_chart(volatility_stats)

    # log to progress
    control_components.progress('None')

    return volatility, performance


# Update progress
@app.callback(
    [Output('submit_button', 'children')],
    [Input('interval_componant', 'n_intervals')]
)
def update_progress(n):
    text = control_components.progress(mode='r')
    text = 'Submit' if 'None' in text else text
    return [text]


if __name__ == "__main__":
    app.run_server(debug=True)
