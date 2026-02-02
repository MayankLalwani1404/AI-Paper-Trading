"""
Symbol registry and metadata management for multi-market support.
Handles symbol normalization, validation, and metadata storage.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Set


class MarketType(str, Enum):
    """Supported market types"""
    US = "US"
    NSE = "NSE"  # National Stock Exchange (India)
    BSE = "BSE"  # Bombay Stock Exchange (India)
    CRYPTO = "CRYPTO"
    INDEX = "INDEX"


@dataclass
class SymbolMetadata:
    """Metadata for a trading symbol"""
    symbol: str
    market: MarketType
    name: str
    sector: Optional[str] = None
    country: str = "US"
    asset_class: str = "EQUITY"  # EQUITY | INDEX | FUTURE | OPTION | CRYPTO


class SymbolRegistry:
    """
    Central registry for symbol metadata and normalization.
    Ensures consistent symbol handling across the platform.
    """

    # Symbol metadata mapping
    SYMBOL_METADATA: Dict[str, SymbolMetadata] = {
        # US Stocks
        "AAPL": SymbolMetadata("AAPL", MarketType.US, "Apple Inc.", "Technology", "US"),
        "MSFT": SymbolMetadata("MSFT", MarketType.US, "Microsoft Corp.", "Technology", "US"),
        "GOOGL": SymbolMetadata("GOOGL", MarketType.US, "Alphabet Inc.", "Technology", "US"),
        "AMZN": SymbolMetadata("AMZN", MarketType.US, "Amazon Inc.", "Technology", "US"),
        "TSLA": SymbolMetadata("TSLA", MarketType.US, "Tesla Inc.", "Automotive", "US"),
        
        # Indian Stocks (NSE)
        "ADANIPORTS.NS": SymbolMetadata("ADANIPORTS.NS", MarketType.NSE, "Adani Ports", "Transportation", "IN"),
        "INFY.NS": SymbolMetadata("INFY.NS", MarketType.NSE, "Infosys", "Technology", "IN"),
        "TCS.NS": SymbolMetadata("TCS.NS", MarketType.NSE, "Tata Consultancy Services", "Technology", "IN"),
        "RELIANCE.NS": SymbolMetadata("RELIANCE.NS", MarketType.NSE, "Reliance Industries", "Energy", "IN"),
        "HDFC.NS": SymbolMetadata("HDFC.NS", MarketType.NSE, "HDFC Bank", "Finance", "IN"),
        
        # Crypto
        "BTCUSDT": SymbolMetadata("BTCUSDT", MarketType.CRYPTO, "Bitcoin", "Cryptocurrency", "GLOBAL", "CRYPTO"),
        "ETHUSDT": SymbolMetadata("ETHUSDT", MarketType.CRYPTO, "Ethereum", "Cryptocurrency", "GLOBAL", "CRYPTO"),
        
        # Indices
        "^GSPC": SymbolMetadata("^GSPC", MarketType.INDEX, "S&P 500", None, "US", "INDEX"),
        "^NSEI": SymbolMetadata("^NSEI", MarketType.INDEX, "NIFTY 50", None, "IN", "INDEX"),
    }

    @staticmethod
    def normalize_symbol(symbol: str, market: Optional[MarketType] = None) -> str:
        """
        Normalize symbol to the correct format based on market.
        
        Args:
            symbol: Raw symbol string
            market: Target market type (if known)
            
        Returns:
            Normalized symbol string
        """
        symbol = symbol.upper().strip()
        
        # If market is specified, apply market-specific formatting
        if market == MarketType.NSE:
            if not symbol.endswith(".NS"):
                symbol = f"{symbol}.NS"
        elif market == MarketType.BSE:
            if not symbol.endswith(".BO"):
                symbol = f"{symbol}.BO"
        elif market == MarketType.INDEX:
            if not symbol.startswith("^"):
                symbol = f"^{symbol}"
        
        return symbol

    @staticmethod
    def get_market(symbol: str) -> Optional[MarketType]:
        """
        Infer market type from symbol format.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            MarketType or None
        """
        symbol = symbol.upper().strip()
        
        if symbol.endswith(".NS"):
            return MarketType.NSE
        elif symbol.endswith(".BO"):
            return MarketType.BSE
        elif symbol.startswith("^"):
            return MarketType.INDEX
        elif symbol.endswith("USDT") or symbol in ["BTC", "ETH"]:
            return MarketType.CRYPTO
        else:
            # Default to US for symbols without suffix
            return MarketType.US

    @classmethod
    def get_metadata(cls, symbol: str) -> Optional[SymbolMetadata]:
        """
        Get metadata for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            SymbolMetadata or None if not found
        """
        symbol = symbol.upper().strip()
        return cls.SYMBOL_METADATA.get(symbol)

    @classmethod
    def register_symbol(cls, symbol: str, metadata: SymbolMetadata):
        """Register a new symbol in the registry"""
        symbol = symbol.upper().strip()
        cls.SYMBOL_METADATA[symbol] = metadata

    @classmethod
    def get_all_symbols(cls, market: Optional[MarketType] = None) -> Set[str]:
        """
        Get all registered symbols, optionally filtered by market.
        
        Args:
            market: Optional market filter
            
        Returns:
            Set of symbol strings
        """
        if market is None:
            return set(cls.SYMBOL_METADATA.keys())
        return {
            symbol for symbol, metadata in cls.SYMBOL_METADATA.items()
            if metadata.market == market
        }

    @classmethod
    def get_symbols_by_market(cls) -> Dict[MarketType, Set[str]]:
        """Get all symbols grouped by market type"""
        result = {market: set() for market in MarketType}
        for symbol, metadata in cls.SYMBOL_METADATA.items():
            result[metadata.market].add(symbol)
        return result


# Default instances for convenient access
SYMBOL_REGISTRY = SymbolRegistry()
