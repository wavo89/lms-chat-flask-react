import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get('DATABASE_URL')
print('Connecting to:', db_url)

try:
    conn = psycopg2.connect(db_url)
    print('✅ Connection successful!')
    conn.close()
except Exception as e:
    print('❌ Connection failed:', e) 