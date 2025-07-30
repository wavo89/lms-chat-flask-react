import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.environ.get('DATABASE_URL')
print('Connecting to:', db_url)

try:
    conn = psycopg2.connect(db_url)
    print('✅ Connection successful!')
    conn.close()
except Exception as e:
    print('❌ Connection failed:', e) 