"""
Kraken Historical CSV Data Fetcher

Downloads and processes historical OHLCV data from Kraken.
Supports BTC/USD, ETH/USD, SOL/USD pairs.

Data Source Strategy (Agent Alpha recommendation):
- Kraken CSV: 2022-01-01 through Q3 2024 (comprehensive, free)
- Kraken REST API: Q4 2024 - present (recent data)

This module handles the CSV portion.
"""

import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KrakenCSVFetcher:
    """
    Fetches historical OHLCV data from Kraken CSV downloads.

    Note: Kraken provides CSV downloads via their trade history page.
    This fetcher automates download and processing for backtesting.
    """

    # Kraken CSV endpoints (publicly accessible historical data)
    # NOTE: These URLs may need updating based on Kraken's current structure
    BASE_URL = "https://api.kraken.com/0/public/OHLC"

    # Pair mappings (Kraken notation)
    PAIRS = {
        "BTC/USD": "XXBTZUSD",
        "ETH/USD": "XETHZUSD",
        "SOL/USD": "SOLUSD"
    }

    # Timeframe mappings (minutes)
    TIMEFRAMES = {
        "1H": 60,
        "4H": 240,
        "1D": 1440
    }

    def __init__(self, data_dir: str = "data/historical"):
        """
        Initialize Kraken CSV fetcher.

        Args:
            data_dir: Directory to store downloaded CSV files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized KrakenCSVFetcher with data_dir: {self.data_dir}")

    def fetch_ohlcv(
        self,
        pair: str,
        timeframe: str = "1H",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data for a specific pair and timeframe.

        Args:
            pair: Trading pair (e.g., "BTC/USD", "ETH/USD", "SOL/USD")
            timeframe: Candle timeframe ("1H", "4H", "1D")
            start_date: Start date for data (default: 2022-01-01)
            end_date: End date for data (default: today)

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        if pair not in self.PAIRS:
            raise ValueError(f"Unsupported pair: {pair}. Supported: {list(self.PAIRS.keys())}")

        if timeframe not in self.TIMEFRAMES:
            raise ValueError(f"Unsupported timeframe: {timeframe}. Supported: {list(self.TIMEFRAMES.keys())}")

        # Default date range
        if start_date is None:
            start_date = datetime(2022, 1, 1)
        if end_date is None:
            end_date = datetime.utcnow()

        logger.info(f"Fetching {pair} {timeframe} data from {start_date} to {end_date}")

        # Check if cached CSV exists
        cache_file = self._get_cache_filename(pair, timeframe, start_date, end_date)
        if cache_file.exists():
            logger.info(f"Loading cached data from {cache_file}")
            return pd.read_csv(cache_file, parse_dates=['timestamp'])

        # Fetch from Kraken API
        df = self._fetch_from_api(pair, timeframe, start_date, end_date)

        # Save to cache
        if not df.empty:
            logger.info(f"Saving {len(df)} candles to cache: {cache_file}")
            df.to_csv(cache_file, index=False)

        return df

    def _fetch_from_api(
        self,
        pair: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Fetch data from Kraken REST API.

        Kraken API limits: 720 candles per request
        The 'since' parameter returns the next 720 candles after that timestamp.
        We need to batch requests for long date ranges.
        """
        kraken_pair = self.PAIRS[pair]
        interval = self.TIMEFRAMES[timeframe]

        # Calculate number of candles needed
        duration_hours = (end_date - start_date).total_seconds() / 3600
        candles_needed = int(duration_hours / (interval / 60))

        logger.info(f"Need to fetch ~{candles_needed} candles for {pair} {timeframe}")

        all_data = []
        current_since = start_date
        max_batches = int(candles_needed / 720) + 2  # Safety margin

        for batch_num in range(max_batches):
            # Fetch batch starting from current_since
            logger.info(f"Fetching batch {batch_num + 1}: since {current_since}")
            batch_df = self._fetch_batch(kraken_pair, interval, current_since)

            if batch_df.empty:
                logger.info("Empty batch returned, stopping")
                break

            # Add batch to collection
            all_data.append(batch_df)

            # Get last timestamp from this batch
            last_timestamp = batch_df['timestamp'].max()

            # If we've reached the end date, stop
            if last_timestamp >= end_date:
                logger.info(f"Reached end date ({end_date}), stopping")
                break

            # Move 'since' to last timestamp + 1 interval for next batch
            # This ensures no gaps and minimal overlap
            current_since = last_timestamp + timedelta(minutes=interval)

            # Rate limiting (Kraken API limit: ~15 requests per minute)
            time.sleep(4)  # 15 req/min = 4 seconds between requests

        if not all_data:
            logger.warning(f"No data fetched for {pair} {timeframe}")
            return pd.DataFrame()

        # Concatenate all batches
        logger.info(f"Concatenating {len(all_data)} batches")
        df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Total {len(df)} candles before deduplication")

        # Remove duplicates and sort
        df = df.drop_duplicates(subset=['timestamp']).sort_values('timestamp').reset_index(drop=True)
        logger.info(f"After deduplication: {len(df)} candles")

        # Filter to requested date range
        # Ensure all timestamps are timezone-naive for comparison
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_localize(None)

        # Convert datetime to pandas Timestamp for comparison
        start_ts = pd.Timestamp(start_date)
        end_ts = pd.Timestamp(end_date)

        logger.info(f"Filtering to range {start_ts} - {end_ts}")

        df = df[
            (df['timestamp'] >= start_ts) &
            (df['timestamp'] <= end_ts)
        ].copy()

        logger.info(f"After filtering: {len(df)} candles remain")
        if not df.empty:
            logger.info(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

        return df

    def _fetch_batch(
        self,
        kraken_pair: str,
        interval: int,
        since: datetime
    ) -> pd.DataFrame:
        """
        Fetch a single batch from Kraken API (max 720 candles).

        API Endpoint: GET /0/public/OHLC
        Parameters:
            - pair: Asset pair (e.g., XXBTZUSD)
            - interval: Time frame interval in minutes
            - since: Return data since given timestamp
        """
        url = self.BASE_URL
        params = {
            "pair": kraken_pair,
            "interval": interval,
            "since": int(since.timestamp())
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if 'error' in data and data['error']:
                logger.error(f"Kraken API error: {data['error']}")
                return pd.DataFrame()

            if 'result' not in data:
                logger.warning("No result in Kraken API response")
                return pd.DataFrame()

            # Extract OHLCV data
            pair_data = data['result'].get(kraken_pair, [])

            if not pair_data:
                logger.warning(f"No data for {kraken_pair}")
                return pd.DataFrame()

            # Parse into DataFrame
            df = pd.DataFrame(pair_data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'
            ])

            # Convert types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)

            # Keep only required columns
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

            logger.info(f"Fetched batch: {len(df)} candles")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return pd.DataFrame()

    def _get_cache_filename(
        self,
        pair: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime
    ) -> Path:
        """Generate cache filename for data."""
        pair_clean = pair.replace("/", "")
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        filename = f"{pair_clean}_{timeframe}_{start_str}_{end_str}.csv"
        return self.data_dir / filename

    def fetch_all_assets(
        self,
        assets: List[str] = ["BTC/USD", "ETH/USD", "SOL/USD"],
        timeframes: List[str] = ["1H", "4H", "1D"],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """
        Fetch data for all assets and timeframes.

        Args:
            assets: List of asset pairs to fetch
            timeframes: List of timeframes to fetch
            start_date: Start date (default: 2022-01-01)
            end_date: End date (default: today)

        Returns:
            Dictionary mapping (asset, timeframe) -> DataFrame
        """
        results = {}
        total_fetches = len(assets) * len(timeframes)
        current = 0

        for asset in assets:
            for timeframe in timeframes:
                current += 1
                logger.info(f"[{current}/{total_fetches}] Fetching {asset} {timeframe}")

                try:
                    df = self.fetch_ohlcv(
                        pair=asset,
                        timeframe=timeframe,
                        start_date=start_date,
                        end_date=end_date
                    )
                    results[(asset, timeframe)] = df
                    logger.info(f"✓ {asset} {timeframe}: {len(df)} candles")
                except Exception as e:
                    logger.error(f"✗ {asset} {timeframe} failed: {e}")
                    results[(asset, timeframe)] = pd.DataFrame()

        return results

    def get_data_summary(self) -> pd.DataFrame:
        """
        Get summary of all cached data files.

        Returns:
            DataFrame with columns: pair, timeframe, start_date, end_date, candles, file_size_mb
        """
        cache_files = list(self.data_dir.glob("*.csv"))

        if not cache_files:
            logger.info("No cached data files found")
            return pd.DataFrame()

        summaries = []
        for file in cache_files:
            try:
                # Parse filename
                parts = file.stem.split("_")
                if len(parts) < 4:
                    continue

                pair = parts[0]
                timeframe = parts[1]
                start_date = parts[2]
                end_date = parts[3]

                # Load and analyze
                df = pd.read_csv(file, parse_dates=['timestamp'])

                summaries.append({
                    'pair': pair,
                    'timeframe': timeframe,
                    'start_date': df['timestamp'].min(),
                    'end_date': df['timestamp'].max(),
                    'candles': len(df),
                    'file_size_mb': file.stat().st_size / (1024 * 1024)
                })
            except Exception as e:
                logger.warning(f"Could not parse {file}: {e}")

        if not summaries:
            return pd.DataFrame()

        return pd.DataFrame(summaries).sort_values(['pair', 'timeframe'])


# ========================================
# CLI Interface
# ========================================
def main():
    """Command-line interface for Kraken CSV fetcher."""
    import argparse

    parser = argparse.ArgumentParser(description="Fetch Kraken historical OHLCV data")
    parser.add_argument(
        "--assets",
        nargs="+",
        default=["BTC/USD", "ETH/USD", "SOL/USD"],
        help="Asset pairs to fetch (default: BTC/USD ETH/USD SOL/USD)"
    )
    parser.add_argument(
        "--timeframes",
        nargs="+",
        default=["1H"],
        help="Timeframes to fetch (default: 1H)"
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default="2022-01-01",
        help="Start date (YYYY-MM-DD, default: 2022-01-01)"
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=None,
        help="End date (YYYY-MM-DD, default: today)"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/historical",
        help="Directory to store data (default: data/historical)"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary of cached data and exit"
    )

    args = parser.parse_args()

    # Initialize fetcher
    fetcher = KrakenCSVFetcher(data_dir=args.data_dir)

    # Show summary if requested
    if args.summary:
        summary = fetcher.get_data_summary()
        if summary.empty:
            print("No cached data found.")
        else:
            print("\nCached Data Summary:")
            print(summary.to_string(index=False))
        return

    # Parse dates
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else None

    # Fetch data
    logger.info("=" * 60)
    logger.info("Kraken Historical Data Fetcher")
    logger.info("=" * 60)
    logger.info(f"Assets: {args.assets}")
    logger.info(f"Timeframes: {args.timeframes}")
    logger.info(f"Date range: {start_date} to {end_date or 'today'}")
    logger.info("=" * 60)

    results = fetcher.fetch_all_assets(
        assets=args.assets,
        timeframes=args.timeframes,
        start_date=start_date,
        end_date=end_date
    )

    # Summary
    logger.info("=" * 60)
    logger.info("Fetch Complete!")
    logger.info("=" * 60)
    successful = sum(1 for df in results.values() if not df.empty)
    logger.info(f"Successful: {successful}/{len(results)}")

    # Show summary
    summary = fetcher.get_data_summary()
    if not summary.empty:
        print("\nData Summary:")
        print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
