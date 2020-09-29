import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from tqdm import tqdm
import os.path


class Form4Scraper():
    def __init__(self):
        self.search_endpoint = "https://www.sec.gov/cgi-bin/browse-edgar"
        self.archive_endpoint = "https://www.sec.gov/Archives/edgar/data"
        self.reset()
        # create saved_transactions folder
        if not os.path.exists("saved_transactions"):
            os.mkdir("saved_transactions")
        # create progress file for dash
        with open('app_components/progress.txt', 'w+') as file:
            file.write('None')

    def reset(self):
        '''reset attributes to original state'''
        self.params_dict = {
            'action': 'getcompany',
            'ticker': 'AAPL',
            'type': '4',
            'dateb': '',
            'owner': 'only',
            'start': '0',
            'count': '100',
            'output': 'atom'
        }
        self.transaction_information = {
            'accession': [],
            'report_period': [],
            'transaction_period': [],
            'name': [],
            'isDirector': [],
            'isOfficer': [],
            'isTenPercentOwner': [],
            'officerTitle': [],
            'security': [],
            'code': [],
            'shares': [],
            'price': [],
            'post_transaction_shares': [],
            'ownership_nature': [],
        }
        self.xml_links = []
        self.accessions = []
        self.filing_dates = []
        self.existing_data = False
        self.search_complete = False

    def get_search_page(self):
        '''get filings on the search page'''
        # get search response for current params
        self.search_response = requests.get(url=self.search_endpoint, params=self.params_dict)
        print(f"Searching SEC Edgar for {self.ticker} filings | Start: {self.params_dict['start']}")
        print("url: ", self.search_response.url, "\n")

    def get_accessions(self):
        '''get file accession numbers from the search page'''
        self.get_search_page()
        soup = BeautifulSoup(self.search_response.content, 'lxml')
        # each entry tag represents a file and contains an accession element
        entries = soup.find_all('entry')
        # if no entries exist then either the ticker was incorrect or no filings were found
        if len(entries) == 0:
            if len(self.accessions) > 0:
                # if no more filings exist then the search is complete
                print(f"{self.ticker} only has {len(self.accessions)} filings\n")
                self.search_complete = True
                return
            else:
                raise ValueError(f"No files found for {self.ticker}. Either ticker does not exist or has no filings.")
        self.cik = soup.find("cik").text
        for entry in entries:
            # get accession number and filing date for each entry
            self.accessions.append(str(entry.find("accession-number").text.replace("-", "")))
            self.filing_dates.append(datetime.strptime(entry.find("filing-date").text, "%Y-%m-%d"))

    def check_search_complete(self, to_date):
        '''check if accessions from requested periods have been acquired'''
        to_date = to_date + timedelta(days=1)
        while self.filing_dates[-1] > to_date and not self.search_complete:
            # add current count to start in params_dict and extract new accessions, next page
            new_start = int(self.params_dict['start']) + int(self.params_dict['count'])
            self.params_dict['start'] = str(new_start)
            self.get_accessions()
        # find index at which filing_date > to_date
        # index all accessions up to that date
        if self.filing_dates[-1] < to_date:
            end_index = [i for i, date in enumerate(self.filing_dates) if date <= to_date][0]
        elif len(self.accessions) == 1:
            end_index = 1
        else:
            end_index = -1
        self.accessions = self.accessions[:end_index]
        # if no filings within search range raise error
        if len(self.accessions) == 0:
            raise ValueError(
                f"Last filing found on {self.filing_dates[end_index].date()}. Try extending the search range."
            )
        self.last_accession = self.accessions[-1]

    def find_xml(self, accession):
        '''find xml file in archive directory for given accession'''
        link = f"{self.archive_endpoint}/{self.cik}/{accession}"
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "lxml")
        # getting the xml file link from table in SEC archives
        table = soup.find("table").find_all('a', href=True)
        for element in table:
            element = str(element)
            if 'xml' in element.split('>')[0]:
                xml = element.split()[1].split('href=')[1].split('>')[0][1:-1].split("/")[-1]
                return f"{link}/{xml}"

    def extract_from_xml(self):
        '''extract relevent data from xml file for each accession entry'''
        print(f"Extracting data from {len(self.accessions)} files...\n")
        for i, accession in enumerate(tqdm(self.accessions, desc='Extracting Data')):
            # output progress to progress.txt for dash
            with open('app_components/progress.txt', 'w') as file:
                progress = int(i/len(self.accessions)*100) if i < len(self.accessions)-1 else None
                file.write(f'Extracting Data... {progress}%')
                file.close()

            link = self.find_xml(accession)
            response = requests.get(url=link)
            soup = BeautifulSoup(response.content, 'xml')
            # if no non derivitive transactions then append accession, report_period and fill rest with Nan
            if len(soup.find_all('nonDerivativeTransaction')) == 0:
                self.transaction_information['accession'].append(accession)
                self.transaction_information['report_period'].append(datetime.strptime(soup.find('periodOfReport').text[:10], '%Y-%m-%d'))
                [self.transaction_information[f"{key}"].append(np.nan) for key in list(self.transaction_information.keys())[2:]]

            # non derivitive transactions
            for transaction in soup.find_all('nonDerivativeTransaction'):
                self.transaction_information['accession'].append(accession)
                self.transaction_information['report_period'].append(datetime.strptime(soup.find('periodOfReport').text[:10], '%Y-%m-%d'))
                self.transaction_information['transaction_period'].append(datetime.strptime(transaction.find('transactionDate').value.text[:10], '%Y-%m-%d'))
                self.transaction_information['name'].append(soup.find('rptOwnerName').text)
                self.transaction_information['security'].append(transaction.find('securityTitle').value.text)
                self.transaction_information['code'].append(transaction.find('transactionCode').text)
                self.transaction_information['post_transaction_shares'].append(float(transaction.find('sharesOwnedFollowingTransaction').value.text))
                self.transaction_information['ownership_nature'].append(transaction.find('directOrIndirectOwnership').value.text)
                # if tag not found, append 0
                for tag in ['isDirector', 'isOfficer', 'isTenPercentOwner', 'officerTitle']:
                    if soup.find(tag) != None:
                        self.transaction_information[f'{tag}'].append(soup.find(tag).text)
                    else:
                        self.transaction_information[f'{tag}'].append(0)
                # if price per share not available, append footnote
                try:
                    self.transaction_information['price'].append(float(transaction.find('transactionPricePerShare').value.text))
                except:
                    # self.transaction_information['price'].append(transaction.find('transactionPricePerShare').find('footnoteId').get('id'))
                    self.transaction_information['price'].append(np.nan)
                # if securities desposed append negitive amount
                if transaction.find('transactionAcquiredDisposedCode').value.text == "D":
                    self.transaction_information['shares'].append(-float(transaction.find('transactionShares').value.text))
                else:
                    self.transaction_information['shares'].append(float(transaction.find('transactionShares').value.text))

    def form4_data(self, ticker='AAPL', from_date='', to_date=''):
        '''get form 4 data from sec edgar'''
        # TODO: handle invalid from_date format
        self.ticker = ticker.upper()
        self.reset()
        from_date = datetime.strptime(from_date, "%Y-%m-%d") if from_date != "" else from_date
        to_date = datetime.strptime(to_date, "%Y-%m-%d")
        self.params_dict['ticker'] = self.ticker
        self.params_dict['dateb'] = from_date.strftime("%Y%m%d") if from_date != "" else from_date
        self.get_accessions()
        self.check_search_complete(to_date)

        # check if data for current ticker exists and remove accessions that already exist
        if os.path.exists(f"saved_transactions\{self.ticker}.pkl"):
            print(f"Found saved data for {self.ticker}...\n")
            self.existing_data = True
            saved_data = pd.read_pickle(f"saved_transactions\{self.ticker}.pkl")
            duplicates = []
            for accession in self.accessions:
                if accession in saved_data.accession.unique():
                    duplicates.append(accession)
            [self.accessions.remove(accession) for accession in duplicates]

        # extract data for each accession and update saved data if required
        if len(self.accessions) > 0:
            self.extract_from_xml()
            # if saved file exists then update file
            if self.existing_data:
                print("\nUpdating existing file...\n")
                update = pd.DataFrame(self.transaction_information)
                transactions = pd.concat([saved_data, update])
            else:
                transactions = pd.DataFrame(self.transaction_information)
            # sorting and saving transactions
            transactions.report_period = pd.to_datetime(transactions.report_period)
            transactions.transaction_period = pd.to_datetime(transactions.transaction_period)
            transactions.sort_values('report_period', ascending=False, inplace=True)
            transactions.reset_index(drop=True, inplace=True)
            transactions.to_pickle(f"saved_transactions\{self.ticker}.pkl")
            # return number of files requested, finding the index value of the last accession number
            start_index = transactions[transactions.report_period <= from_date].index[0] if from_date != "" else 0
            end_index = transactions[transactions.accession == self.last_accession].index[-1] + 1
            data = transactions.iloc[start_index:end_index]
            return data
        # return number of files requested, finding the index value of the last accession number
        start_index = saved_data[saved_data.report_period <= from_date].index[0] if from_date != "" else 0
        end_index = saved_data[saved_data.accession == self.last_accession].index[-1] + 1
        return saved_data.iloc[start_index:end_index]
