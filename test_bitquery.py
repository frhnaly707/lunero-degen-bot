import requests

BITQUERY_API_KEY = "ory_at_fDDG4jB4ZV8x542HC6DeJ9ijcI9P_Y27PqpsLafsnGk.szuP3Y-2GuFzqlSHvlIBSW0Ux91UH1lSEjqNgjM5Gy0"
query = """
{
  solana {
    dexTrades(limit: {count: 5}, orderBy: {descending: Block_Time}) {
      Trade { AmountIn Currency { Symbol Name MintAddress } }
      Block { Time }
      Transaction { Hash }
    }
  }
}
"""

response = requests.post(
    "https://graphql.bitquery.io/",
    json={"query": query},
    headers={"X-API-KEY": BITQUERY_API_KEY}
)
print(response.json())
