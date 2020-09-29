from statistics import InsiderStats
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta

from pandas_datareader import DataReader
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


class Visualise():
    def __init__(self):
        self.stats = InsiderStats()
        self.data_check = False
        self.ohlc_details = {
            'total_buy_vol': None,
            'total_sell_vol': None,
            'total_buy_vol_dollar': None,
            'total_sell_vol_dollar': None,
            'num_transactions': None,
            'num_insiders': None,
        }
        self.chart_template = 'plotly'

    def get_stats(self, ticker, from_date="", to_date="2020-01-01",
                  filter_insiders=None, filter_side=None, filter_open_market=False,
                  filter_size=None, filter_only=False):
        '''get statistics from InsiderStats class'''
        self.ticker = ticker
        # insider statistics data
        data = self.stats.get_data(
            ticker=ticker,
            to_date=to_date,
            filter_insiders=filter_insiders,
            filter_side=filter_side,
            filter_open_market=filter_open_market,
            filter_size=filter_size,
            filter_only=filter_only
        )

        self.transactions, self.insider_stats, self.volatility_stats, self.performance_stats, self.price_data = data
        self.data_check = True

        # get spy, vix data if new data is required
        if not filter_only:
            tickers = ['SPY', '^VIX']
            self.spy_data, self.vix_data = [DataReader(_ticker, 'yahoo', to_date, from_date) for _ticker in tickers]

        return data

    def update_ohlc_details(self, buys=None, sells=None, transactions=None, zeros=False):
        '''details displayed above ohlc chart'''
        # update details
        self.ohlc_details['total_buy_vol'] = buys.shares.sum() if not zeros else 0
        self.ohlc_details['total_sell_vol'] = sells.shares.sum() if not zeros else 0
        self.ohlc_details['total_buy_vol_dollar'] = buys.amount.sum() if not zeros else 0
        self.ohlc_details['total_sell_vol_dollar'] = sells.amount.sum() if not zeros else 0
        self.ohlc_details['num_transactions'] = len(transactions) if not zeros else 0
        self.ohlc_details['num_insiders'] = len(transactions.name.unique()) if not zeros else 0

        return self.ohlc_details

    def get_ohlc(self, price_data, ticker):
        '''return go.Ohlc object '''
        return go.Ohlc(
            x=price_data.index,
            open=price_data.Open,
            high=price_data.High,
            close=price_data.Close,
            low=price_data.Low,
            increasing_line_color="Black",
            decreasing_line_color="Black",
            name=f"{ticker.upper()}",
        )

    def price_chart(self, price_data, ticker=None):
        ''' create OHLC chart with no transactions'''
        ticker = self.ticker if ticker == None else ticker

        ohlc = self.get_ohlc(price_data, ticker)
        fig = go.Figure()
        fig.add_trace(ohlc)
        fig.update_layout(
            title=f'{ticker.upper()} Commonstock Transactions',
            title_x=0.5,
            xaxis_rangeslider_visible=False,
            template=self.chart_template,
            transition_duration=500,
            paper_bgcolor='rgba(0,0,0,0)',
        )

        return fig, self.update_ohlc_details(zeros=True)

    def index_comparison(self, transactions, volume_type_spy='shares', volume_type_vix='shares'):
        '''compare transaction volumes against indexes'''
        transaction_volume = transactions.groupby('transaction_period').sum()
        transaction_volume_spy = transaction_volume.shares if volume_type_spy == 'shares' else transaction_volume.amount
        transaction_volume_vix = transaction_volume.shares if volume_type_vix == 'shares' else transaction_volume.amount
        buy_volume_spy = transaction_volume_spy[transaction_volume_spy > 0]
        sell_volume_spy = transaction_volume_spy[transaction_volume_spy < 0]
        buy_volume_vix = transaction_volume_vix[transaction_volume_vix > 0]
        sell_volume_vix = transaction_volume_vix[transaction_volume_vix < 0]

        # create buy and sell volume bars
        buy_volume_bars_spy = go.Bar(
            x=buy_volume_spy.index,
            y=buy_volume_spy,
            marker_color='green',
            name='Buy Volume',
            opacity=0.6
        )
        sell_volume_bars_spy = go.Bar(
            x=sell_volume_spy.index,
            y=abs(sell_volume_spy),
            marker_color='red',
            name='Sell Volume',
            opacity=0.6
        )

        buy_volume_bars_vix = go.Bar(
            x=buy_volume_vix.index,
            y=buy_volume_vix,
            marker_color='green',
            name='Buy Volume',
            opacity=0.6
        )
        sell_volume_bars_vix = go.Bar(
            x=sell_volume_vix.index,
            y=abs(sell_volume_vix),
            marker_color='red',
            name='Sell Volume',
            opacity=0.6
        )

        spy_data = [self.spy_data, 'SPY', buy_volume_bars_spy, sell_volume_bars_spy]
        vix_data = [self.vix_data, 'VIX', buy_volume_bars_vix, sell_volume_bars_vix]
        figs = []
        for data in [spy_data, vix_data]:
            index, ticker, b_vol, s_vol = data
            ohlc = self.get_ohlc(index, ticker)
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(ohlc)
            fig.add_trace(b_vol, secondary_y=True)
            fig.add_trace(s_vol, secondary_y=True)
            fig.update_yaxes(title_text='Price', secondary_y=False)
            fig.update_yaxes(title_text='Transaction Volume', secondary_y=True)
            fig.update_layout(
                title=f'Insider Trading Vs {ticker.upper()}',
                title_x=0.5,
                xaxis_rangeslider_visible=False,
                transition_duration=50,
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
            figs.append(fig)

        return [fig for fig in figs]

    def ohlc_chart(self, transactions, price_data, filter_market_trades=False, volume_type='shares'):
        '''create OHLC chart with insider transactions scattered'''
        assert self.data_check == True, "Must first get statistics using get_data"
        # filter for open market transactions
        if filter_market_trades:
            highs, lows = [], []
            for period in transactions.transaction_period:
                highs.append(price_data[price_data.index == period].High.iloc[0])
                lows.append(price_data[price_data.index == period].Low.iloc[0])
            transactions = transactions[
                (transactions.adj_price <= highs) &
                (transactions.adj_price >= lows)
            ]
        else:
            transactions = transactions

        if len(transactions) == 0:
            return self.price_chart(price_data)

        # separate buys and sells
        buys = transactions[transactions.shares > 0]
        sells = transactions[transactions.shares < 0]

        # update ohlc details
        details = self.update_ohlc_details(buys, sells, transactions)

        # get range of prices
        transaction_range = transactions.transaction_period.iloc[-1], transactions.transaction_period.iloc[0]
        price_range = price_data.loc[transaction_range[0]: transaction_range[1]]

        # determine max/min for axis
        ymax, ymin = price_range.max() * 1.2, price_range.min() * 0.8
        xmin = transactions.iloc[-1].transaction_period - timedelta(weeks=4)
        xmax = transactions.iloc[0].transaction_period + timedelta(weeks=4)

        # crate ohlc bars and buy/sell scatter points
        ohlc = self.get_ohlc(price_data, self.ticker)
        scatter_buys = go.Scatter(
            x=buys.transaction_period,
            y=buys.adj_price,
            mode="markers",
            marker_color="green",
            marker_size=12,
            name="Buys"
        )
        scatter_sells = go.Scatter(
            x=sells.transaction_period,
            y=sells.adj_price,
            mode="markers",
            marker_color="red",
            marker_size=12,
            name="Sells",
        )

        # separate buy and sell volume
        transaction_volume = transactions.groupby('transaction_period').sum()
        transaction_volume = transaction_volume.shares if volume_type == 'shares' else transaction_volume.amount
        buy_volume = transaction_volume[transaction_volume > 0]
        sell_volume = transaction_volume[transaction_volume < 0]
        # create buy and sell volume bars
        buy_volume_bars = go.Bar(
            x=buy_volume.index,
            y=buy_volume,
            marker_color='green',
            name='Buy Volume',
        )
        sell_volume_bars = go.Bar(
            x=sell_volume.index,
            y=abs(sell_volume),
            marker_color='red',
            name='Sell Volume',
        )

        # make subplots
        fig = make_subplots(
            rows=2,
            cols=1,
            row_heights=[0.8, 0.2],
            shared_xaxes=True,
            subplot_titles=['', f'Transaction Volume {volume_type.title()}'],
            vertical_spacing=0.1
        )
        # add traces
        [fig.add_trace(data, row=1, col=1) for data in [ohlc, scatter_buys, scatter_sells]]
        [fig.add_trace(data, row=2, col=1) for data in [sell_volume_bars, buy_volume_bars]]
        # customize layout
        fig.update_layout(
            title=f'{self.ticker.upper()} Commonstock Transactions',
            title_x=0.5,
            xaxis_rangeslider_visible=False,
            template=self.chart_template,
            xaxis=dict(range=[xmin, xmax]),
            yaxis=dict(range=[ymin, ymax]),
            transition_duration=50,
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )

        # edit subplot font
        for i in fig['layout']['annotations']:
            i['font'] = dict(size=12, color='black')
        return fig, details

    def volatility_chart(self, volatility_stats):
        '''create box plot comparing pre/post transaction volatility'''
        data = []
        # adding pre and post boxes for each period
        for i, col in enumerate(volatility_stats.columns):
            # labels need to be provided for each data point in y
            x = [col.upper()] * int(len(volatility_stats) / 2)
            y = volatility_stats.unstack()[f'{col}']
            # show legend on first iterration
            showlegend = True if i == 0 else False
            for period, colour in [('pre', 'blue'), ('post', 'red')]:
                data.append(
                    go.Box(
                        x=x,
                        y=y[f'{period}'] if not y.empty else [],
                        name=period,
                        marker_color=colour,
                        showlegend=showlegend,
                    )
                )
        # add traces to fig and customize
        fig = go.Figure()
        [fig.add_trace(i) for i in data]
        fig.update_layout(
            title='Pre vs Post Transaction Volatility',
            title_x=0.5,
            template=self.chart_template,
            boxmode='group',  # group together different traces for each value of x
            boxgroupgap=0.2,
            boxgap=0.1,
            paper_bgcolor='rgba(0,0,0,0)',
        )
        return fig

    def performance_chart(self, performance_stats):
        '''create box plot comparing performance of buy/sell transactions'''
        data = []
        for i, col in enumerate(performance_stats.columns[1:]):
            # labels need to be provided for each data point in y
            x = [col.upper()] * int(len(performance_stats))
            y = performance_stats
            # show legend on first iterration
            showlegend = True if i == 0 else False
            for code, colour in [("P", "green"), ("S", "red")]:
                data.append(
                    go.Box(
                        x=x,
                        y=y[y.code == code][f'{col}'],
                        marker_color=colour,
                        showlegend=showlegend,
                        name='Buy' if code == 'P' else 'Sell'
                    )
                )
        # add traces to fig and customize
        fig = go.Figure()
        [fig.add_trace(i) for i in data]
        fig.update_layout(
            title='Post Transaction Performance',
            title_x=0.5,
            template=self.chart_template,
            boxmode='group',  # group together different traces for each value of x
            boxgroupgap=0.0,
            boxgap=0.0,
            paper_bgcolor='rgba(0,0,0,0)',
        )
        return fig

    def insider_chart(self, insider_stats, column):
        '''create chart of required insiders statistic'''
        '''insider - name of reporting insider
        total_volume - total volume traded
        total_volume_dollar - total value of volume traded
        position_delta - position change in shares
        position_delta_dollar - position change in dollars
        position_delta_percentage - position change in percentage
        position_rotation - amount of shares traded as a percentage of origional position
        trade_count - number of trades made
        '''
        fig = go.Figure()
        # bar chart
        data = go.Bar(
            x=insider_stats.insider,
            y=insider_stats[f'{column}']
        )
        # add trace to fig and customize
        fig.add_trace(data)
        fig.update_layout(
            title=column.replace('_', ' ').title(),
            title_x=0.5,
            template=self.chart_template,
            paper_bgcolor='rgba(0,0,0,0)',
        )
        return fig
