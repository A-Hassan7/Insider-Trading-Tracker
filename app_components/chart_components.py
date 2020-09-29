'''
Components that compose the charts, tables and radios
'''
import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .styles import styles


class ChartComponents():
    def __init__(self):

        self.ohlc_chart = html.Div([
            # select volume type on ohlc chart and details
            html.Div([
                html.Label('Units:'),
                dcc.RadioItems(
                    id='volume_type_radio',
                    options=[
                        {'label': 'Shares', 'value': 'shares'},
                        {'label': 'Notional', 'value': 'notional'},
                    ],
                    value='shares',
                    style={'display': 'flex'})
            ], style=styles['radio']),

            # ohlc chart
            html.Div([dcc.Graph(id='ohlc_chart', style=styles['chart'])])
        ], style={'display': 'block'})

        self.total_volume_chart = html.Div([
            html.Div([
                html.Label('Units:'),
                # unit selector
                dcc.RadioItems(
                    id='total_volume_radio',
                    options=[
                        {'label': 'Shares', 'value': 'shares'},
                        {'label': 'Notional', 'value': 'notional'},
                    ],
                    value='shares',
                    style={'display': 'flex'}
                ),
            ], style=styles['radio']),
            # chart
            html.Div([dcc.Graph(id='total_volume', style=styles['chart'])])
        ])

        self.position_delta_chart = html.Div([
            html.Div([
                # unit selector
                html.Label('Units:'),
                dcc.RadioItems(
                    id='position_delta_radio',
                    options=[
                        {'label': 'Shares', 'value': 'shares'},
                        {'label': 'Notional', 'value': 'notional'},
                        {'label': 'Percentage', 'value': 'percentage'}
                    ],
                    value='shares',
                    style={'display': 'flex'}
                ),
            ], style=styles['radio']),
            # chart
            html.Div([dcc.Graph(id='position_delta', style=styles['chart'])])
        ])

        self.position_rotation_chart = html.Div([dcc.Graph(id='position_rotation', style=styles['chart'])])

        self.trade_count_chart = html.Div([dcc.Graph(id='trade_count', style=styles['chart'])])

        self.spy_chart = html.Div([
            html.Div([
                html.Label('Units:'),
                # unit selector
                dcc.RadioItems(
                    id='volume_type_spy_radio',
                    options=[
                        {'label': 'Shares', 'value': 'shares'},
                        {'label': 'Notional', 'value': 'notional'},
                    ],
                    value='shares',
                    style={'display': 'flex'}
                ),
            ], style=styles['radio']),

            dcc.Graph(id='spy_chart', style=styles['chart'])
        ])

        self.vix_chart = html.Div([
            html.Div([
                html.Label('Units:'),
                # unit selector
                dcc.RadioItems(
                    id='volume_type_vix_radio',
                    options=[
                        {'label': 'Shares', 'value': 'shares'},
                        {'label': 'Notional', 'value': 'notional'},
                    ],
                    value='shares',
                    style={'display': 'flex'}
                ),
            ], style=styles['radio']),

            dcc.Graph(id='vix_chart', style=styles['chart'])

        ])

        self.volatility_chart = html.Div([dcc.Graph(id='volatility_chart', style=styles['chart'])])

        self.performance_chart = html.Div([dcc.Graph(id='performance_chart', style=styles['chart'])])

        self.transactions_table = html.Div(id='transactions_table', style=styles['table'])

    def generate_table(self, dataframe, max_rows=10):
        return html.Table([
            html.Thead(
                html.Tr([html.Th(col.replace('_', ' ').upper()) for col in dataframe.columns])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
                ]) for i in range(min(len(dataframe), max_rows))
            ])
        ])
