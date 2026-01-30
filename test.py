from dotenv import load_dotenv
import os

load_dotenv()

print("Endpoint:", os.getenv("ASTRA_DB_API_ENDPOINT"))
print("Keyspace:", os.getenv("ASTRA_DB_KEYSPACE"))

assert os.getenv("ASTRA_DB_API_ENDPOINT"), "Missing ASTRA_DB_API_ENDPOINT"
assert os.getenv("ASTRA_DB_APPLICATION_TOKEN"), "Missing ASTRA_DB_APPLICATION_TOKEN"

print("✅ Env vars loaded correctly")

