'''
Components that compose the controls section
'''

import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .styles import styles


class ControlComponents():
    def __init__(self):

        self.search_heading = html.Div([
            html.H3('Search Insider Transactions', style={'textAlign': 'center', 'fontSize': 20})
        ])

        self.input_form = html.Div([
            html.Div([
                # input box
                html.Label('Ticker', className='control_label'),
                dcc.Input(
                    id='input_ticker',
                    value="AAPL",
                    type='text',
                    style={'width': 130, 'fontSize': 15},
                )
            ], style=styles['input_form']),

            html.Div([
                # from date
                html.Label('From', className='control_label'),
                dcc.DatePickerSingle(
                    id='date_from',
                    date=datetime.today() - relativedelta(years=1),
                    display_format='YYYY-MM-DD',
                ),
            ], style=styles['input_form']),
            html.Div([
                # to date
                html.Label('To'),
                dcc.DatePickerSingle(
                    id='date_to',
                    date=datetime.today(),
                    display_format='YYYY-MM-DD',
                )
            ], style=styles['input_form'])
        ], style=styles['search_criteria'])

        self.filter_insiders = html.Div([
            html.P('Filter by insiders:'),
            dcc.RadioItems(
                id='insider_filter_radio',
                options=[
                    {'label': 'All', 'value': 'all'},
                    {'label': 'Customize', 'value': 'custom'}
                ],
                value='all',
                style={'display': 'flex'}
            ),
            dcc.Dropdown(id='insider_filter_dropdown', multi=True, style={'width': '95%'})

        ], style={'display': 'block', 'paddingLeft': '20px'})

        self.filter_transactions = html.Div([
            html.P('Filter by transactions:'),
            html.Div([
                dcc.Checklist(
                    id='filter_market_trades_checkbox',
                    options=[{'label': 'Open Market Transactions', 'value': 'filter'}],
                    value=['filter'],
                    style={'paddingRight': '15px'}
                ),
                dcc.Checklist(
                    id='filter_buys',
                    options=[{'label': 'Buys', 'value': 'P'}],
                    value=['P'],
                    style={'paddingRight': '15px'}
                ),
                dcc.Checklist(
                    id='filter_sells',
                    options=[{'label': 'Sells', 'value': 'S'}],
                    value=['S'],
                    style={'paddingRight': '15px'}
                )
            ], style={'display': 'flex'})
        ], style={'paddingLeft': '20px'})

        self.submit = html.Div([
            html.Button(
                'Submit',
                id='submit_button',
                style={'background': '#119dff8c', 'width': '90%', 'margin': 'auto'}
            ),
            dcc.Interval('interval_componant', interval=1000, n_intervals=0)
        ])

        self.details = html.Div([
            html.Div([
                html.Label('Units:'),
                dcc.RadioItems(
                    id='volume_type_details_radio',
                    options=[
                        {'label': 'Shares', 'value': 'shares'},
                        {'label': 'Notional', 'value': 'notional'},
                    ],
                    value='shares',
                    style={'display': 'flex'})
            ], style={'display': 'flex', 'float': 'left', 'paddingTop': '10px', 'fontSize': '14px'}),
            # chart details
            # number of transactions found
            html.Div([
                html.Div([
                    html.H6(id='num_transactions', style=styles['details_label']),
                    html.P('# Transactions', style=styles['paragraph'])
                ], style=styles['details']),

                # number of insiders found
                html.Div([
                    html.H6(id='num_insiders', style=styles['details_label']),
                    html.P('# Insiders', style=styles['paragraph'])
                ], style=styles['details']),

                # total buy volume
                html.Div([
                    html.H6(id='total_buy_vol', style=styles['details_label']),
                    html.P('Buy Volume', style=styles['paragraph'])
                ], style=styles['details']),

                # total sell volume
                html.Div([
                    html.H6(id='total_sell_vol', style=styles['details_label']),
                    html.P('Sell Volume', style=styles['paragraph'])
                ], style=styles['details'])
            ], style={'display': 'inline-flex'})
        ], style={'display': 'grid', 'position': 'absolute', 'bottom': '20px'})

        self.filter_transactions_size = html.Div([
            # select units
            dcc.Dropdown(
                id='filter_transactions_unit',
                options=[
                    {'label': 'Shares', 'value': 'shares'},
                    {'label': 'Notional', 'value': 'amount'},
                    {'label': 'Ownership %', 'value': 'ownership_percentage'}
                ],
                placeholder='Units',
                style={'paddingLeft': '5px', 'width': '130px'}
            ),
            # select operator
            dcc.Dropdown(
                id='filter_transactions_operator',
                options=[
                    {'label': '>', 'value': '>'},
                    {'label': '<', 'value': '<'}
                ],
                placeholder='Op',
                style={'paddingLeft': '5px', 'width': '77px', 'paddingRight': '4px'}
            ),
            # enter value
            dcc.Input(
                id='filter_transactions_value',
                placeholder='Value',
                style={'width': '80px', 'paddingLeft': '5px', 'height': '36px'}
            ),
            # select value type
            dcc.Dropdown(
                id='filter_transactions_value_type',
                options=[
                    {'label': 'Real', 'value': 'real'},
                    {'label': 'ABS', 'value': 'absolute'}
                ],
                placeholder='Type',
                style={'paddingLeft': '5px', 'width': '73px'}
            ),

            html.Div([
                html.Button(
                    'Filter',
                    id='filter_button',
                    style=styles['filter_button']
                )
            ])

        ], style=styles['filter_transactions'])

        self.stored_data = html.Div([
            html.Div(id='stored_transactions'),
            html.Div(id='stored_insider_stats'),
            html.Div(id='stored_volatility_stats'),
            html.Div(id='stored_performence_stats'),
            html.Div(id='stored_price_data'),
            html.Div(id='stored_spy_data'),
            html.Div(id='stored_vix_data'),
        ], style={'display': 'none'})

        self.filtered_data = html.Div([
            html.Div(id='filtered_transactions'),
            html.Div(id='filtered_insider_stats'),
            html.Div(id='filtered_volatility_stats'),
            html.Div(id='filtered_performence_stats')
        ], style={'display': 'none'})

    def progress(self, text=None, path='app_components/progress.txt', mode='w'):
        '''helper function to read/write from progress.txt'''
        if mode == 'r':
            with open(path, mode) as file:
                text = file.read()
                file.close()
                return text

        with open(path, mode) as file:
            assert text != None, 'text required'
            file.write(text)
            file.close()
