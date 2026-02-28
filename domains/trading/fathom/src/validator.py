"""
Fathom Input Validator
Validates tool inputs for safety and correctness.
"""

from typing import Any, Optional
from decimal import Decimal, InvalidOperation


class Validator:
    """
    Input validation for Fathom tools.

    Validates:
    - Trading pair formats
    - Order sizes and prices
    - Safety limits (max order size during learning phase)
    - Numeric precision
    """

    # Safety limits (can be adjusted per phase)
    MAX_ORDER_USD = 50.0  # Maximum order size during learning phase
    MIN_ORDER_USD = 1.0   # Minimum order size (Kraken minimum)

    # Kraken pair format validation
    VALID_QUOTE_CURRENCIES = {"USD", "USDT", "USDC", "EUR"}
    VALID_BASE_CURRENCIES = {"BTC", "ETH", "XBT", "ETH", "ADA", "SOL", "DOT", "MATIC"}

    def __init__(self, max_order_usd: Optional[float] = None):
        """
        Initialize validator.

        Args:
            max_order_usd: Override default max order size
        """
        if max_order_usd is not None:
            self.MAX_ORDER_USD = max_order_usd

    def validate_pair(self, pair: str) -> tuple[bool, Optional[str]]:
        """
        Validate trading pair format.

        Args:
            pair: Trading pair (e.g., "BTC/USD", "XBTUSD")

        Returns:
            (is_valid, error_message)
        """
        if not pair:
            return False, "Pair cannot be empty"

        # Normalize to Kraken format
        normalized = pair.upper().replace("/", "").replace("-", "")

        # Check if it looks like a valid pair (at least 6 chars, mix of base/quote)
        if len(normalized) < 6:
            return False, f"Invalid pair format: {pair}"

        return True, None

    def validate_order_size(
        self,
        volume: float,
        price: Optional[float] = None,
        side: str = "buy"
    ) -> tuple[bool, Optional[str]]:
        """
        Validate order size against safety limits.

        Args:
            volume: Order volume (in base currency)
            price: Price per unit (if None, assumes market order estimation needed)
            side: "buy" or "sell"

        Returns:
            (is_valid, error_message)
        """
        if volume <= 0:
            return False, "Volume must be positive"

        # If price is provided, check USD value
        if price is not None:
            usd_value = volume * price

            if usd_value > self.MAX_ORDER_USD:
                return False, (
                    f"Order size ${usd_value:.2f} exceeds safety limit of ${self.MAX_ORDER_USD:.2f}. "
                    f"Reduce volume or request Captain approval for larger orders."
                )

            if usd_value < self.MIN_ORDER_USD:
                return False, (
                    f"Order size ${usd_value:.2f} below Kraken minimum of ${self.MIN_ORDER_USD:.2f}"
                )

        return True, None

    def validate_price(self, price: float) -> tuple[bool, Optional[str]]:
        """
        Validate price value.

        Args:
            price: Price value

        Returns:
            (is_valid, error_message)
        """
        if price <= 0:
            return False, "Price must be positive"

        # Check for reasonable precision (max 8 decimals for crypto)
        try:
            decimal_price = Decimal(str(price))
            if abs(decimal_price.as_tuple().exponent) > 8:
                return False, "Price has too many decimal places (max 8)"
        except InvalidOperation:
            return False, "Invalid price format"

        return True, None

    def validate_order_type(self, order_type: str) -> tuple[bool, Optional[str]]:
        """
        Validate order type.

        Args:
            order_type: Order type string

        Returns:
            (is_valid, error_message)
        """
        valid_types = {"market", "limit"}
        order_type_lower = order_type.lower()

        if order_type_lower not in valid_types:
            return False, f"Invalid order type: {order_type}. Must be one of {valid_types}"

        return True, None

    def validate_side(self, side: str) -> tuple[bool, Optional[str]]:
        """
        Validate order side.

        Args:
            side: Order side string

        Returns:
            (is_valid, error_message)
        """
        valid_sides = {"buy", "sell"}
        side_lower = side.lower()

        if side_lower not in valid_sides:
            return False, f"Invalid side: {side}. Must be 'buy' or 'sell'"

        return True, None

    def validate_interval(self, interval: int) -> tuple[bool, Optional[str]]:
        """
        Validate OHLC interval.

        Args:
            interval: Interval in minutes

        Returns:
            (is_valid, error_message)
        """
        valid_intervals = {1, 5, 15, 30, 60, 240, 1440, 10080, 21600}

        if interval not in valid_intervals:
            return False, (
                f"Invalid interval: {interval}. "
                f"Must be one of {sorted(valid_intervals)}"
            )

        return True, None

    def validate_book_depth(self, depth: int) -> tuple[bool, Optional[str]]:
        """
        Validate order book depth.

        Args:
            depth: Number of levels to return

        Returns:
            (is_valid, error_message)
        """
        valid_depths = {10, 25, 100, 500, 1000}

        if depth not in valid_depths:
            return False, f"Invalid depth: {depth}. Must be one of {valid_depths}"

        return True, None

    def check_requires_confirmation(
        self,
        volume: float,
        price: Optional[float] = None
    ) -> bool:
        """
        Check if order requires Captain confirmation.

        Args:
            volume: Order volume
            price: Price per unit

        Returns:
            True if confirmation needed
        """
        # Require confirmation for orders > $20
        CONFIRMATION_THRESHOLD = 20.0

        if price is not None:
            usd_value = volume * price
            return usd_value > CONFIRMATION_THRESHOLD

        # If no price, assume confirmation needed (safety)
        return True

    def sanitize_pair(self, pair: str) -> str:
        """
        Normalize pair to Kraken format.

        Args:
            pair: Trading pair (any format)

        Returns:
            Normalized pair (e.g., "BTC/USD" -> "XBTUSD")
        """
        # Remove common separators
        normalized = pair.upper().replace("/", "").replace("-", "")

        # Handle BTC -> XBT conversion (Kraken uses XBT)
        if normalized.startswith("BTC"):
            normalized = "XBT" + normalized[3:]

        return normalized
