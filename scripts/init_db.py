import asyncio
import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def init_db():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    database = os.getenv("DB_NAME")
    host = os.getenv("DB_HOST")

    if not all([user, password, database, host]):
        print("❌ Error: Missing required database environment variables in .env")
        return

    print(f"Connecting to {host} as {user}...")
    try:
        conn = await asyncpg.connect(
            user=user,
            password=password,
            database=database,
            host=host
        )
        
        print("Enabling pgvector extension...")
        # Note: In Cloud SQL, extensions must be enabled by a superuser (postgres) or a user with specific permissions.
        # transit_admin should have enough permissions if created correctly, but let's see.
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        print("Creating transit_knowledge table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS transit_knowledge (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                metadata JSONB,
                embedding vector(768)
            );
        """)
        
        print("Creating api_cache table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS api_cache (
                api_name TEXT NOT NULL,
                params TEXT NOT NULL,
                response_data JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                PRIMARY KEY (api_name, params)
            );
        """)
        
        print("Database initialized successfully!")
        await conn.close()
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    asyncio.run(init_db())
