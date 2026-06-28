from dotenv import load_dotenv
import os

load_dotenv()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")

if not ODDS_API_KEY:
    raise ValueError("ODDS_API_KEY não encontrada")
if not FOOTBALL_API_KEY:
    raise ValueError("FOOTBALL_API_KEY não encontrada")