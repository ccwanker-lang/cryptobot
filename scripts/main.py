import ccxt
import json
import logging

# Logging instellen
logging.basicConfig(
    filename="logs/bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Bot gestart!")

# Config inladen
with open("/home/pi/my_bot/configs/config.json") as f:
    config = json.load(f)

# Binance exchange object
exchange = ccxt.binance({
    'apiKey': config["binance"]["api_key"],
    'secret': config["binance"]["api_secret"],
    'enableRateLimit': True
})

print("CCXT versie:", ccxt.__version__)
print("Exchange naam:", exchange.name)

# Voorbeeld: huidige marktticker ophalen
ticker = exchange.fetch_ticker('BTC/USDT')
print("BTC/USDT:", ticker['last'])
logging.info(f"BTC/USDT prijs: {ticker['last']}")
