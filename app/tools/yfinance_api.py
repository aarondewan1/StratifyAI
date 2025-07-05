import yfinance as yf
import pandas as pd

from langchain_core.tools import tool

from app.logger import logger

@tool
def fetch_and_summarise_ticker(symbol: str, year: int = 2023, month: int = 1) -> dict:
    """
    Fetches and summarises the ticker data for a given month from Yahoo Finance API.

    Args:
        symbol (str): The stock ticker symbol (e.g., "AAPL" or "MSFT").
        year (int): The year (e.g., 2024).
        month (int): The month (1-12).

    Returns:
        dict: An LLM summary of the ticker data.
    """
    logger.info("🔨 YFINANCE tool | was invoked")
    logger.info(f"symbol: {symbol}, year: {year}, month: {month}")

    prices = fetch_monthly_ticker(symbol, year, month)
    summary = summarise_ticker(prices)
    llm_summary = format_summary_for_llm(summary, symbol, year, month)
    
    logger.info("🔨 YFINANCE tool | result was fetched")
    logger.info(llm_summary)
    return llm_summary

def fetch_monthly_ticker(symbol: str, year: int, month: int) -> pd.DataFrame:
    """
    Fetch daily price data for a given ticker symbol for a specific month.
    
    Args:
        symbol (str): The stock ticker symbol (e.g., "SPY" or "^IRX").
        year (int): The year (e.g., 2024).
        month (int): The month (1-12).

    Returns:
        pd.DataFrame: DataFrame with daily OHLCV data for that month.
    """
    # Compute start and end date for the given month
    start_date = pd.Timestamp(year=year, month=month, day=1)
    if month == 12:
        end_date = pd.Timestamp(year=year + 1, month=1, day=1)
    else:
        end_date = pd.Timestamp(year=year, month=month + 1, day=1)

    # Download data with daily interval
    df = yf.download(
        symbol,
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        interval="5d",
        progress=False,
        auto_adjust=True,
    )

    if df.empty:
        raise ValueError(f"No data returned for {symbol} in {year}-{month:02d}")

    return df


def summarise_ticker(
    df: pd.DataFrame,
    column: str = "Close",
) -> dict:
    """
    Generic summary for any ticker DataFrame.

    Args:
        df (pd.DataFrame): Must have a 'Close' or specified column and Date index.
        column (str): Which column to summarise (default: 'Close').

    Returns:
        dict: Summary stats.
    """
    month_end = df[column].iloc[-1]
    month_avg = df[column].mean()
    month_high = df[column].max()
    month_low = df[column].min()
    month_vol = df[column].std()

    summary = {
        "month_end_value": round(month_end, 4),
        "monthly_average": round(month_avg, 4),
        "high": round(month_high, 4),
        "low": round(month_low, 4),
        "volatility_stdev": round(month_vol, 6),
    }

    return summary

def format_summary_for_llm(summary_dict, ticker_name, year, month):
    """
    Formats the financial summary for LLM ingestion.

    Parameters:
    - summary_dict (dict): A dictionary containing the financial summary with keys:
      'month_end_value', 'monthly_average', 'high', 'low', 'volatility_stdev'.
    - ticker_name (str): The name of the ticker.
    - year (int): The year of the data.
    - month (int): The month of the data.

    Returns:
    - str: A formatted string summarizing the financial data.
    """
    month_end_value = summary_dict['month_end_value'].iloc[0]
    monthly_average = summary_dict['monthly_average'].iloc[0]
    high = summary_dict['high'].iloc[0]
    low = summary_dict['low'].iloc[0]
    volatility_stdev = summary_dict['volatility_stdev'].iloc[0]

    return (f"Summary of {ticker_name} for {pd.Timestamp(year=year, month=month, day=1).strftime('%B %Y')}:\n"
            f"- Month-End Value: {month_end_value:.2f}\n"
            f"- Monthly Average: {monthly_average:.4f}\n"
            f"- Monthly High: {high:.3f}\n"
            f"- Monthly Low: {low:.3f}\n"
            f"- Volatility (Standard Deviation): {volatility_stdev:.4f}")


# Example usage
if __name__ == "__main__":
    symbol = "^IRX"
    year = 2024
    month = 6
    print(fetch_and_summarise_ticker(symbol, year, month))
