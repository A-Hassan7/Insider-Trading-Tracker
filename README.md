# Insider Trading Tracker
 
***Extract, filter and visualise insider trading transactions scraped directly from the SEC's archives***

![demonstration](demo/demo.gif)


## Features
* Visualise insider transactions on a price chart.
  
* Compare insider transaction volume to SPY (S&P500 ETF) and VIX (volatility index). Are transactions more likely during market drawdowns and increased volatility?
  
* Explore statistics including total volume, position delta, position rotation (```transaction volume/initial position```) and trade count for each insider.
  
* Analyse pre vs post transaction volatility. Does volatility increase after transactions?
  
* Analyse post transaction performance. How did the stock perform after the transactions?


## Data
The US Securities and Exchange Commission requires directors, officers and significant owners of publicly listed companies to report changes in ownership. These changes are recorded in Form 4 filings which is where this app scrapes data from.

The ```scraper.py``` module is responsible for scraping the data from the SEC's archives and can be used separately from the app:

```python
from scraper import Form4Scraper

form4 = Form4Scraper()
df = form4.form4_data('AAPL', '2019-01-01', '2020-09-01')
```

## Installation
```bash
git clone https://github.com/A-Hassan7/Insider-Trading-Tracker.git

cd Insider-Trading-Tracker

pip install -r requirements.txt
```

## Usage
run ```python app.py``` from the terminal then navitage to ```http://127.0.0.1:8050/``` in your browser.

## Libraries Used
*  The front end was built entirely using [Dash](https://github.com/plotly/dash)
*  Charts were created using [Plotly](https://github.com/plotly/plotly.py)
*  Data manipulation and analysis was done using [Pandas](https://github.com/pandas-dev/pandas)
*  Webscraping was done using [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## Future Improvements
* Currently, only commonstock transactions are supported. A future release will support derivitive transactions aswell.
* Add links to filings for each transaction.
* Enable filtering of insiders by relationship (e.g. director, owner etc.)


