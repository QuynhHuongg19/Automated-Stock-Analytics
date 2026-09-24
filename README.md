# 📈 Automated Stock Analytics Platform

A Python-based stock analytics and screening platform for Vietnamese equities listed on **HOSE, HNX, and UPCOM**.

The project processes historical market data, calculates technical indicators, applies rule-based stock screening, and presents the results through an interactive **Streamlit dashboard**.

## 🌐 Live Demo

👉 [Open Automated Stock Analytics Platform](https://automated-stock-analytics-bypqh.streamlit.app)

## 🚀 Key Features

- Process and clean historical stock market data
- Support HOSE, HNX, and UPCOM
- Calculate technical indicators:
  - MA20
  - MA50
  - RSI14
  - MACD
  - MACD Signal
  - MACD Histogram
  - 20-session average trading volume
- Rule-based technical stock screening
- Interactive candlestick and volume charts
- RSI and MACD visualization
- Filter stocks by exchange and technical conditions
- Lightweight deployment dataset for the web application

## 🛠️ Tech Stack

- Python
- Pandas
- NumPy
- Plotly
- Streamlit
- Git & GitHub

## 📊 Data

Historical Vietnamese stock market data is processed from CafeF datasets.

The data pipeline standardizes the following fields:

`Ticker`, `Exchange`, `Date`, `Open`, `High`, `Low`, `Close`, `Volume`

The processed dataset contains more than **3.3 million historical observations** before the lightweight web dataset is generated for deployment.

## 🔎 Technical Screening

The screening system evaluates stocks using five technical conditions:

1. Close > MA20
2. MA20 > MA50
3. RSI14 between 50 and 70
4. MACD > MACD Signal
5. Volume > Volume MA20

Stocks are then classified according to the number of conditions satisfied.

> The screening results are designed for technical analysis and educational purposes and should not be interpreted as investment recommendations.

## 🖥️ Dashboard

The Streamlit application allows users to:

- Select an exchange
- Select a stock ticker
- Select a historical time range
- View the latest technical indicators
- Analyze candlestick and volume charts
- View RSI and MACD
- Explore technical screening results

## 📁 Project Structure

```text
Automated-Stock-Analytics/
│
├── data/
│   ├── raw/
│   └── processed/
│       ├── stock_data_web.csv
│       └── stock_screener.csv
│
├── src/
│   ├── data_pipeline.py
│   ├── indicators.py
│   ├── screener.py
│   └── export_web_data.py
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

Large raw and intermediate datasets are excluded from the repository to keep the project suitable for GitHub and cloud deployment.

## ⚙️ Run Locally

Clone the repository:

```bash
git clone https://github.com/QuynhHuongg19/Automated-Stock-Analytics.git
cd Automated-Stock-Analytics
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
streamlit run app.py
```

## 🔗 Links

**Live Application:**  
https://automated-stock-analytics-bypqh.streamlit.app

**Source Code:**  
https://github.com/QuynhHuongg19/Automated-Stock-Analytics