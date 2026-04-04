"""
PROFESSIONAL EXCHANGE CONFIGURATION MANAGEMENT
AI Arbitrage Bot v7.0

Purpose: Centralized configuration for all exchanges (Binance, Bybit, etc.)
         Supports seamless switching between testnet and production
         Validates credentials on startup
"""

import os
from dotenv import load_dotenv
from enum import Enum
from typing import Optional, Dict

load_dotenv()


class Environment(str, Enum):
    """Supported environments"""
    TESTNET = "testnet"
    PRODUCTION = "production"


class ExchangeConfig:
    """
    Centralized exchange configuration management
    Handles credentials, URLs, and settings for all exchanges
    Automatically switches between testnet and production based on .env
    """

    # ========== ENVIRONMENT SELECTION ==========
    ENVIRONMENT = os.getenv("ENVIRONMENT", "testnet").lower()

    # Validate environment
    if ENVIRONMENT not in [e.value for e in Environment]:
        raise ValueError(
            f"❌ Invalid ENVIRONMENT: '{ENVIRONMENT}' in .env\n"
            f"   Valid options: 'testnet' or 'production'"
        )

    # ========== BINANCE CONFIGURATION ==========
    if ENVIRONMENT == "testnet":
        BINANCE_API_URL = "https://testnet.binance.vision"  # ✅ FIXED TYPO
        BINANCE_API_KEY = os.getenv("BINANCE_TESTNET_API_KEY", "")
        BINANCE_SECRET = os.getenv("BINANCE_TESTNET_SECRET", "")
        BINANCE_LABEL = "Binance Testnet"
    else:
        BINANCE_API_URL = "https://api.binance.com"
        BINANCE_API_KEY = os.getenv("BINANCE_PRODUCTION_API_KEY", "")
        BINANCE_SECRET = os.getenv("BINANCE_PRODUCTION_SECRET", "")
        BINANCE_LABEL = "Binance Production"

    # ========== BYBIT CONFIGURATION ==========
    if ENVIRONMENT == "testnet":
        BYBIT_API_URL = "https://api-testnet.bybit.com"  # ✅ CORRECT ENDPOINT
        BYBIT_API_KEY = os.getenv("BYBIT_TESTNET_API_KEY", "")
        BYBIT_SECRET = os.getenv("BYBIT_TESTNET_SECRET", "")
        BYBIT_LABEL = "Bybit Testnet"
    else:
        BYBIT_API_URL = "https://api.bybit.com"
        BYBIT_API_KEY = os.getenv("BYBIT_PRODUCTION_API_KEY", "")
        BYBIT_SECRET = os.getenv("BYBIT_PRODUCTION_SECRET", "")
        BYBIT_LABEL = "Bybit Production"

    # ========== ADDITIONAL EXCHANGES (Future Support) ==========
    # Kraken
    if ENVIRONMENT == "testnet":
        KRAKEN_API_URL = "https://api.kraken.com"
        KRAKEN_API_KEY = os.getenv("KRAKEN_TESTNET_API_KEY", "")
        KRAKEN_SECRET = os.getenv("KRAKEN_TESTNET_SECRET", "")
    else:
        KRAKEN_API_URL = "https://api.kraken.com"
        KRAKEN_API_KEY = os.getenv("KRAKEN_PRODUCTION_API_KEY", "")
        KRAKEN_SECRET = os.getenv("KRAKEN_PRODUCTION_SECRET", "")

    # Coinbase
    if ENVIRONMENT == "testnet":
        COINBASE_API_URL = "https://api-sandbox.exchange.coinbase.com"
        COINBASE_API_KEY = os.getenv("COINBASE_TESTNET_API_KEY", "")
        COINBASE_SECRET = os.getenv("COINBASE_TESTNET_SECRET", "")
    else:
        COINBASE_API_URL = "https://api.exchange.coinbase.com"
        COINBASE_API_KEY = os.getenv("COINBASE_PRODUCTION_API_KEY", "")
        COINBASE_SECRET = os.getenv("COINBASE_PRODUCTION_SECRET", "")

    # ========== PROXY CONFIGURATION ==========
    HTTP_PROXY = os.getenv("HTTP_PROXY", "")
    HTTPS_PROXY = os.getenv("HTTPS_PROXY", "")
    ENABLE_PROXY_FALLBACK = (
        os.getenv("ENABLE_PROXY_FALLBACK", "true").lower() == "true"
    )

    # ========== API SETTINGS ==========
    API_REQUEST_TIMEOUT = int(os.getenv("API_REQUEST_TIMEOUT", "10"))
    API_RATE_LIMIT_ENABLED = (
        os.getenv("API_RATE_LIMIT_ENABLED", "true").lower() == "true"
    )
    API_RETRY_ATTEMPTS = int(os.getenv("API_RETRY_ATTEMPTS", "3"))
    API_RETRY_DELAY = float(os.getenv("API_RETRY_DELAY", "1.0"))

    # ========== AI & SECURITY ==========
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")

    @classmethod
    def validate(cls) -> bool:
        """
        Validate all required credentials are set for current environment
        Returns: True if valid, False if errors found
        """
        errors = []

        # Check Binance credentials
        if not cls.BINANCE_API_KEY:
            errors.append(
                f"❌ BINANCE_{cls.ENVIRONMENT.upper()}_API_KEY not set in .env"
            )
        if not cls.BINANCE_SECRET:
            errors.append(
                f"❌ BINANCE_{cls.ENVIRONMENT.upper()}_SECRET not set in .env"
            )

        # Check Bybit credentials
        if not cls.BYBIT_API_KEY:
            errors.append(
                f"❌ BYBIT_{cls.ENVIRONMENT.upper()}_API_KEY not set in .env"
            )
        if not cls.BYBIT_SECRET:
            errors.append(
                f"❌ BYBIT_{cls.ENVIRONMENT.upper()}_SECRET not set in .env"
            )

        # Check JWT Secret
        if not cls.JWT_SECRET_KEY:
            errors.append("⚠️  JWT_SECRET_KEY not set in .env (optional for dev)")

        if errors:
            print("\n" + "=" * 70)
            print("⚠️  CONFIGURATION VALIDATION FAILED")
            print("=" * 70)
            for error in errors:
                print(f"  {error}")
            print("\nPlease update your .env file before starting the bot.\n")
            return False

        return True

    @classmethod
    def print_config(cls) -> None:
        """Print current configuration in a readable format"""
        print("\n" + "=" * 70)
        print("📋 ARBPRO CONFIGURATION")
        print("=" * 70)
        print(f"\n🌍 Environment: {cls.ENVIRONMENT.upper()}")

        print(f"\n🟡 Binance")
        print(f"   URL: {cls.BINANCE_API_URL}")
        print(f"   Status: {'✅ Configured' if cls.BINANCE_API_KEY else '❌ Not configured'}")

        print(f"\n⚫ Bybit")
        print(f"   URL: {cls.BYBIT_API_URL}")
        print(f"   Status: {'✅ Configured' if cls.BYBIT_API_KEY else '❌ Not configured'}")

        print(f"\n⚙️  API Settings")
        print(f"   Timeout: {cls.API_REQUEST_TIMEOUT}s")
        print(f"   Rate Limit: {'✅ Enabled' if cls.API_RATE_LIMIT_ENABLED else '❌ Disabled'}")
        print(f"   Retry Attempts: {cls.API_RETRY_ATTEMPTS}")
        print(f"   Proxy Fallback: {'✅ Enabled' if cls.ENABLE_PROXY_FALLBACK else '❌ Disabled'}")

        if cls.HTTPS_PROXY or cls.HTTP_PROXY:
            print(f"\n🔧 Proxy Configuration")
            print(
                f"   HTTPS: {cls.HTTPS_PROXY or 'Not set'}"
            )
            print(f"   HTTP: {cls.HTTP_PROXY or 'Not set'}")

        print("\n" + "=" * 70 + "\n")

    @classmethod
    def get_exchange_config(cls, exchange: str) -> Dict:
        """
        Get configuration dictionary for a specific exchange
        Usage: config_dict = ExchangeConfig.get_exchange_config('binance')
        """
        exchange = exchange.lower()

        if exchange == "binance":
            return {
                "apiKey": cls.BINANCE_API_KEY,
                "secret": cls.BINANCE_SECRET,
                "urls": {"api": cls.BINANCE_API_URL},
                "enableRateLimit": cls.API_RATE_LIMIT_ENABLED,
                "timeout": cls.API_REQUEST_TIMEOUT,
                "proxies": {},  # Binance doesn't need proxy usually
                "options": {
                    "adjustForTimeDifference": True,
                    "recvWindow": 10000,
                },
            }

        elif exchange == "bybit":
            config = {
                "apiKey": cls.BYBIT_API_KEY,
                "secret": cls.BYBIT_SECRET,
                "urls": {"api": cls.BYBIT_API_URL},
                "enableRateLimit": cls.API_RATE_LIMIT_ENABLED,
                "timeout": cls.API_REQUEST_TIMEOUT,
                "options": {
                    "adjustForTimeDifference": True,
                },
            }
            # Add proxy if available
            if cls.HTTPS_PROXY or cls.HTTP_PROXY:
                config["proxies"] = {
                    "http": cls.HTTP_PROXY or cls.HTTPS_PROXY,
                    "https": cls.HTTPS_PROXY or cls.HTTP_PROXY,
                }
            return config

        elif exchange == "kraken":
            return {
                "apiKey": cls.KRAKEN_API_KEY,
                "secret": cls.KRAKEN_SECRET,
                "urls": {"api": cls.KRAKEN_API_URL},
                "enableRateLimit": cls.API_RATE_LIMIT_ENABLED,
                "timeout": cls.API_REQUEST_TIMEOUT,
            }

        elif exchange == "coinbase":
            return {
                "apiKey": cls.COINBASE_API_KEY,
                "secret": cls.COINBASE_SECRET,
                "urls": {"api": cls.COINBASE_API_URL},
                "enableRateLimit": cls.API_RATE_LIMIT_ENABLED,
                "timeout": cls.API_REQUEST_TIMEOUT,
            }

        else:
            raise ValueError(f"Unknown exchange: {exchange}")

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return cls.ENVIRONMENT == "production"

    @classmethod
    def is_testnet(cls) -> bool:
        """Check if running in testnet mode"""
        return cls.ENVIRONMENT == "testnet"


# Validate configuration when module is imported
if __name__ != "__main__":
    ExchangeConfig.validate()
