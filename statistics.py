from scraper import Form4Scraper
import pandas as pd
from pandas_datareader import DataReader
from dateutil.relativedelta import relativedelta
import holidays
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


class InsiderStats():
    def __init__(self):
        self.scraper = Form4Scraper()
        self.reset()
        self.us_holidays = holidays.US()
        self.data_check = False

    def reset(self):
        '''reset dictionary'''
        self.insider_stats = {
            "insider": [],
            "total_volume": [],
            "total_volume_dollar": [],
            "position_delta": [],
            "position_delta_dollar": [],
            "position_delta_percentage": [],
            "position_rotation": [],
            "trade_count": []
        }
        self.volatility_stats = {
            "std_1w": [],
            "std_1m": [],
            "std_3m": [],
            "std_6m": [],
            "std_1y": []
        }
        self.performance_stats = {
            "code": [],
            "return_1w": [],
            "return_1m": [],
            "return_3m": [],
            "return_6m": [],
            "return_1y": [],
        }

    def get_commonstock_transactions(self, ticker, from_date, to_date):
        '''get all commonstock transactions from form 4 filings'''
        # getting form4 data for ticker
        self.transactions = self.scraper.form4_data(ticker, from_date, to_date)
        files_searched = len(self.transactions.accession.unique())
        # filter transactions occuring on weekends or us holidays
        # these do not represent an open market transaction
        self.transactions = self.transactions[
            (self.transactions.transaction_period.dt.weekday.isin([5, 6]) == False) &
            ([date not in self.us_holidays for date in self.transactions.transaction_period])
        ]

        # indexing commonstock transactions and creating a copy
        self.commonstock_transactions = self.transactions.loc[
            (self.transactions.code == 'P') | (self.transactions.code == 'S') & self.transactions.price != 0
        ].copy()
        self.commonstock_transactions = self.commonstock_transactions[self.commonstock_transactions.price.map(type) != str]
        self.commonstock_transactions.reset_index(inplace=True, drop=True)
        transactions_found = len(self.commonstock_transactions)
        if transactions_found == 0:
            raise Exception("No commonstock transcation found, try extending the search range")

        # calculating amount, pre_transaction_shares and ownership_percentage
        shares = self.commonstock_transactions.shares
        price = self.commonstock_transactions.price
        post_transaction_shares = self.commonstock_transactions.post_transaction_shares
        self.commonstock_transactions['amount'] = shares * price
        self.commonstock_transactions['pre_transaction_shares'] = post_transaction_shares - shares
        self.commonstock_transactions['ownership_percentage'] = shares / self.commonstock_transactions.pre_transaction_shares * 100

        # list of insiders
        self.insiders = self.commonstock_transactions.name.unique()

        self.data_check = True

    def get_price_data(self, ticker):
        '''get historical price and split data for ticker'''

        # getting price and split data from yahoo finance
        start = self.commonstock_transactions.iloc[-1].transaction_period - relativedelta(weeks=4)
        self.price_data = DataReader(ticker, 'yahoo', start=start)
        self.split_data = DataReader(ticker, "yahoo-actions", start=start)
        self.split_data = self.split_data[self.split_data.action == "SPLIT"]

        # calculating adjusted price if stock split has occurred
        if not self.split_data.empty:
            adj_price = []
            for i, row in self.commonstock_transactions.iterrows():
                price = row.price * self.split_data.value.prod() if row.transaction_period < self.split_data.index[-1] else row.price
                adj_price.append(price)
            self.commonstock_transactions['adj_price'] = adj_price
        else:
            self.commonstock_transactions['adj_price'] = self.commonstock_transactions.price

    def filter_commonstock_transactions(self, filter_insiders=None, filter_side=None,
                                        filter_open_market=None, filter_size=None):
        '''filter commonstock transactions if specified'''
        # if no filter is specified then return
        if filter_insiders == None and filter_side == None and filter_open_market == None and filter_size_g == None:
            self.filtered_transactions = self.commonstock_transactions
            return
        ft = self.commonstock_transactions
        # filter insiders if specified
        if filter_insiders != None:
            [print(f"{insider} not in insiders list") for insider in filter_insiders if insider not in self.insiders]
            ft = ft[ft.name.isin(filter_insiders)]
        # filter buy or sell trades if specified
        if filter_side != None:
            assert filter_side in [None, "P", "S"], "Incorrect transaction filter. Valid filters [None, P, S]"
            ft = ft[ft.code == filter_side]
        # filter open market transactions if specified
        if filter_open_market:
            highs, lows = [], []
            for period in ft.transaction_period:
                highs.append(self.price_data[self.price_data.index == period].High.iloc[0])
                lows.append(self.price_data[self.price_data.index == period].Low.iloc[0])
            ft = ft[(ft.adj_price <= highs) & (ft.adj_price >= lows)]
        # filter transactions based on size
        if filter_size != None:
            assert len(filter_size) == 4, 'Need to specify [size, column, type, operator]'
            column, op, size, type_ = filter_size
            size = float(size)
            if op == '>':
                ft = ft[ft[f'{column}'] > size] if type_ == 'real' else ft[abs(ft[f'{column}']) > size]
            if op == '<':
                ft = ft[ft[f'{column}'] < size] if type_ == 'real' else ft[abs(ft[f'{column}']) < size]

        self.filtered_transactions = ft

    def get_insider_statistics(self):
        '''calculate statistics for each insider found in search
        insider - name of reporting insider
        total_volume - total volume traded
        total_volume_dollar - total value of volume traded
        position_delta - position change in shares
        position_delta_dollar - position change in dollars
        position_delta_percentage - position change in percentage
        position_rotation - amount of shares traded as a percentage of origional position
        trade_count - number of trades made
        '''
        for insider in self.filtered_transactions.name.unique():
            # get all transactions for insider
            transactions = self.filtered_transactions[self.filtered_transactions.name == insider]

            # calculate statistics for insider
            total_volume = abs(transactions.shares).sum()
            total_volume_dollar = abs(transactions.amount).sum()
            position_delta = transactions.shares.sum()
            position_delta_dollar = transactions.amount.sum()
            position_delta_percentage = position_delta / transactions.pre_transaction_shares.iloc[-1] * 100
            position_rotation = total_volume / transactions.pre_transaction_shares.iloc[-1] * 100

            # append statistics to dictionary
            self.insider_stats['insider'].append(insider)
            self.insider_stats['total_volume'].append(total_volume)
            self.insider_stats['total_volume_dollar'].append(total_volume_dollar)
            self.insider_stats['position_delta'].append(position_delta)
            self.insider_stats['position_delta_dollar'].append(position_delta_dollar)
            self.insider_stats['position_delta_percentage'].append(position_delta_percentage)
            self.insider_stats['position_rotation'].append(position_rotation)
            self.insider_stats['trade_count'].append(len(transactions))

        self.insider_stats = pd.DataFrame(self.insider_stats)

    def get_volatility_statistics(self):
        '''calculate volatility statistics for each trade found in search'''

        prices = self.price_data.Close
        std_keys = list(self.volatility_stats.keys())
        perf_keys = list(self.performance_stats.keys())[1:]
        periods = (
            relativedelta(weeks=1),
            relativedelta(months=1),
            relativedelta(months=3),
            relativedelta(months=6),
            relativedelta(years=1)
        )

        transaction_dates = self.filtered_transactions.transaction_period.drop_duplicates()
        for date in transaction_dates:
            # calulate pre and post transaction standard deviation for each transaction
            for key, period in zip(std_keys, periods):
                # appending pre and post transaction statistics to same array (multiindex)
                pre_start = date - period
                pre_end = date - relativedelta(days=1)
                post_start = date + relativedelta(days=1)
                post_end = date + period
                self.volatility_stats[f'{key}'].append(prices.loc[pre_start:pre_end].std())
                # if post transaction period is out of bounds append NaN
                if post_end <= prices.index[-1]:
                    self.volatility_stats[f'{key}'].append(prices.loc[post_start:post_end].std())
                else:
                    self.volatility_stats[f'{key}'].append(float("NaN"))

        for _, transaction in self.filtered_transactions.iterrows():
            date = transaction.transaction_period
            self.performance_stats['code'].append(transaction.code)
            # calculate stock performence after transactions
            for key, period in zip(perf_keys, periods):
                period_end = date + period
                # get the nearest date in prices
                period_end = prices.index[prices.index.get_loc(period_end, method='nearest')]
                if period_end <= prices.index[-1]:
                    # calculate return
                    x = prices[prices.index == date].iloc[0]
                    y = prices[prices.index == period_end].iloc[0]
                    period_return = (y - x) / x * 100
                    self.performance_stats[f'{key}'].append(period_return)
                else:
                    self.performance_stats[f'{key}'].append(float("NaN"))

        # create multiindex
        volatility_stats_index = pd.MultiIndex.from_product(
            [transaction_dates, ['pre', 'post']],
            names=['transaction_date', 'period']
        )
        # create dataframes
        self.volatility_stats = pd.DataFrame(self.volatility_stats, index=volatility_stats_index)
        self.performance_stats = pd.DataFrame(self.performance_stats)

    def get_data(self, ticker, from_date="", to_date="2020-01-01",
                 filter_insiders=None, filter_side=None, filter_open_market=False,
                 filter_size=None, filter_only=False):
        ''' returns commonstock transactions, insider statistics and trade statistics'''

        if not filter_only:
            # get commonstock transactions and price data
            self.get_commonstock_transactions(ticker, from_date, to_date)
            self.get_price_data(ticker)
        else:
            assert self.data_check, 'Get transaction data first, set filter only to False'

        self.reset()
        # calculate statistics using commonstock transactions and price data
        self.filter_commonstock_transactions(
            filter_insiders,
            filter_side,
            filter_open_market,
            filter_size)

        self.get_insider_statistics()
        self.get_volatility_statistics()

        return self.filtered_transactions, self.insider_stats, self.volatility_stats, self.performance_stats, self.price_data
