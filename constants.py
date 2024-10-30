from util import AssetType

DEFAULT_DATA_PATH = './data/market'
DEFAULT_FIAT = 'USD'

DEFAULT_DIGITAL_ASSETS = [
    'BTC', 'ETH', 'USDT', 'XRP', 'SOL', 'USDC', 'ADA', 'AVAX', 'DOGE', 'DOT',
    'TRX', 'LINK', 'MATIC', 'WBTC', 'SHIB', 'LTC', 'DAI', 'ICP', 'UNI', 'BCH',
    'XLM', 'ATOM', 'XMR', 'ETC', 'FIL', 'IMX', 'APT', 'INJ', 'TUSD', 'NEAR',
    'OP', 'TIA', 'LDO', 'RUNE', 'QNT', 'EGLD', 'ALGO', 'AAVE', 'GRT',
    'STX', 'ARB', 'SNX', 'MKR', 'BTT', 'FLOW', 'FTM', 'SAND', 'LUNA', 'AXS',
    'MANA', 'GALA', 'EOS', 'XTZ', 'KAVA', 'DYDX', 'MINA', 'WOO', 'FET', 'FXS'
]
DIGITAL_ASSET_DATA_API = 'https://api.kraken.com/0/public/OHLC'

DEFAULT_CORRELATION_WINDOW = 10
DEFAULT_SMOOTHING_WINDOW = 4

DEFAULT_DISCRETIZATION_THRESHOLD = 0.5
DEFAULT_GAP_THRESHOLD = 0.1

DEFAULT_MARKET_PREFIXES = {
    AssetType.DIGITAL: 'digital',
    AssetType.SNP500: 'snp500',
    AssetType.OTHER: 'other'
}