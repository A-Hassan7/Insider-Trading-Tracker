'''
Consolidating individual app Components into a layout
'''

import dash
import dash_core_components as dcc
import dash_html_components as html

from .control_components import ControlComponents
from .chart_components import ChartComponents
from .styles import styles

control_components = ControlComponents()
chart_components = ChartComponents()

layout = html.Div([

    # heading (top)
    html.Div([
        html.H1('Insider Trading Tracker'),
        html.H6(
            'Analyse insider transactions for equities listed on major US exchanges'
        ),
    ], style={'hight': '10%', 'textAlign': 'center'}),

    # controls (left)
    html.Div([
        # inputs
        html.Div([
            control_components.search_heading,
            html.Hr(),
            control_components.input_form,
            control_components.submit,
            html.Br(),
            control_components.filter_insiders,
            html.Br(),
            control_components.filter_transactions,
            control_components.filter_transactions_size,
            control_components.stored_data,
            control_components.filtered_data
        ], style=styles['controls_style']),
        # details
        html.Div([
            control_components.details,
        ])
    ]),

    html.Div([
        # data (right)
        dcc.Tabs([
            # tab one
            dcc.Tab([
                # mini tabs
                dcc.Tabs([
                    # mini tab one
                    dcc.Tab([
                        html.Div([chart_components.ohlc_chart], style=styles['tab_content_style'])
                    ], style=styles['tab_style'], selected_style=styles['tab_selected_style'], label='Equity'),
                    # mini tab two
                    dcc.Tab([
                        html.Div([chart_components.spy_chart], style=styles['tab_content_style'])
                    ], style=styles['tab_style'], selected_style=styles['tab_selected_style'], label='SPY'),
                    # mini tab three
                    dcc.Tab([
                        html.Div([chart_components.vix_chart], style=styles['tab_content_style']),
                    ], style=styles['tab_style'], selected_style=styles['tab_selected_style'], label='VIX'),
                    # mini tab four
                    dcc.Tab([
                        html.Div([chart_components.transactions_table], style=styles['tab_content_style'])
                    ], style=styles['tab_style'], selected_style=styles['tab_selected_style'], label='Table')
                ], style=styles['mini_tab_style'])
            ], label='Transactions'),
            # tab two
            dcc.Tab([
                # mini tabs
                dcc.Tabs([
                    # mini tab one
                    dcc.Tab([
                        html.Div([chart_components.total_volume_chart], style=styles['tab_content_style'])
                    ], style=styles['tab_style'], selected_style=styles['tab_selected_style'], label='Total Volume'),
                    # mini tab two
                    dcc.Tab([
                        html.Div([chart_components.position_delta_chart], style=styles['tab_content_style'])
                    ], style=styles['tab_style'], selected_style=styles['tab_selected_style'], label='Position Delta'),
                    # mini tab two
                    dcc.Tab([
                        html.Div([chart_components.position_rotation_chart], style=styles['tab_content_style'])
                    ], style=styles['tab_style'], selected_style=styles['tab_selected_style'], label='Position Rotation'),
                    # mini tab two
                    dcc.Tab([
                        html.Div([chart_components.trade_count_chart], style=styles['tab_content_style'])
                    ], style=styles['tab_style'], selected_style=styles['tab_selected_style'], label='Trade Count'),
                ], style=styles['mini_tab_style'])
            ], label='Inisiders'),
            # Tab three
            dcc.Tab([
                # mini tabs
                dcc.Tabs([
                    # mini tab one
                    dcc.Tab([
                         html.Div([chart_components.volatility_chart], style=styles['tab_content_style'])
                         ], style=styles['tab_style'], selected_style=styles['tab_selected_style'], label='Volatility'),
                    # mini tab two
                    dcc.Tab([
                        html.Div([chart_components.performance_chart], style=styles['tab_content_style'])
                    ], style=styles['tab_style'], selected_style=styles['tab_selected_style'], label='Performance')
                ], style=styles['mini_tab_style'])
            ], label='Analysis')
        ], style={'paddingBottom': '15px'})
    ], style=styles['main_tab_style']),
])
