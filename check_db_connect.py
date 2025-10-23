import os, asyncio, asyncpg
from dotenv import load_dotenv
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
print("=============")
print(DATABASE_URL)
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    ASYNCPG_DSN = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
else:
    ASYNCPG_DSN = DATABASE_URL

async def test_connect():
    conn = await asyncpg.connect(dsn=ASYNCPG_DSN)
    print("connected")
    await conn.close()
asyncio.run(test_connect())
