import os
import asyncpg
import json
from pgvector.asyncpg import register_vector
from google.cloud import secretmanager, aiplatform
from vertexai.language_models import TextEmbeddingModel

class VectorService:
    def __init__(self):
        self.project_id = os.getenv("PROJECT_ID", "transit-flow-my")
        # Embeddings are regional! Always lock to us-central1 for text-multilingual-embedding-002 🎬📈 🇲🇾🚆stack
        self.location = "us-central1"
        self.db_user = None
        self.db_pass = None
        self.db_name = None
        self.db_host = None
        self.model_name = "text-multilingual-embedding-002"
        self._model = None
        self._pool = None

    async def _get_secret(self, secret_id: str) -> str:
        try:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8").strip()
        except Exception as e:
            # Fallback to env
            val = os.getenv(secret_id)
            if not val:
                print(f"Warning: Secret {secret_id} not found in Secret Manager or Env.")
            return val

    async def get_pool(self):
        if not self._pool:
            # Lazy load secrets
            if not self.db_user:
                self.db_user = await self._get_secret("DB_USER")
                self.db_pass = await self._get_secret("DB_PASS")
                self.db_name = await self._get_secret("DB_NAME")
                self.db_host = await self._get_secret("DB_HOST")

            try:
                # Detect Cloud SQL Auth Proxy (Unix Socket)
                # Format: /cloudsql/PROJECT_ID:REGION:INSTANCE_ID
                unix_socket = f"/cloudsql/{os.getenv('CLOUD_SQL_CONNECTION_NAME', 'transit-flow-my:us-central1:transitflow-db-instance')}"
                
                connect_kwargs = {
                    "user": self.db_user,
                    "password": self.db_pass,
                    "database": self.db_name,
                    "min_size": 1,
                    "max_size": 10,
                    "timeout": 5.0
                }

                if os.path.exists(unix_socket):
                    print(f"VectorService: Using Cloud SQL Auth Proxy ({unix_socket})")
                    connect_kwargs["host"] = unix_socket
                else:
                    print(f"VectorService: Using TCP Connection ({self.db_host})")
                    connect_kwargs["host"] = self.db_host

                self._pool = await asyncpg.create_pool(**connect_kwargs)
                
                # Register pgvector type
                async with self._pool.acquire() as conn:
                    await register_vector(conn)
                print(f"VectorService: Connected to Database")
            except Exception as e:
                print(f"VectorService Error: Connection Refused. Entering Degraded Mode. ({e})")
                self._pool = "FAILED" # Sentinel value to prevent constant re-attempts
        return self._pool if self._pool != "FAILED" else None

    def _get_model(self):
        if not self._model:
            aiplatform.init(project=self.project_id, location=self.location)
            self._model = TextEmbeddingModel.from_pretrained(self.model_name)
        return self._model

    async def get_embedding(self, text: str):
        model = self._get_model()
        embeddings = model.get_embeddings([text])
        return embeddings[0].values

    async def search_transit_knowledge(self, query_text: str, limit: int = 5):
        try:
            pool = await self.get_pool()
            if not pool:
                return []
            embedding = await self.get_embedding(query_text)
            async with pool.acquire() as conn:
                results = await conn.fetch(
                    """
                    SELECT content, metadata, 1 - (embedding <=> $1) as similarity
                    FROM transit_knowledge
                    ORDER BY embedding <=> $1
                    LIMIT $2
                    """,
                    embedding,
                    limit
                )
                return results
        except Exception as e:
            print(f"VectorService Knowledge Search Error: {e}")
            return []

    async def cache_api_response(self, api_name: str, params: dict, response_data: dict, ttl_seconds: int = 3600):
        try:
            pool = await self.get_pool()
            if not pool:
                return
            param_str = json.dumps(params, sort_keys=True)
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO api_cache (api_name, params, response_data, expires_at)
                    VALUES ($1, $2, $3, NOW() + interval '1 second' * $4)
                    ON CONFLICT (api_name, params) 
                    DO UPDATE SET response_data = EXCLUDED.response_data, expires_at = EXCLUDED.expires_at
                    """,
                    api_name, param_str, json.dumps(response_data), ttl_seconds
                )
        except Exception as e:
            print(f"VectorService Cache Write Error: {e}")

    async def get_cached_api_response(self, api_name: str, params: dict):
        try:
            pool = await self.get_pool()
            if not pool:
                return None
            param_str = json.dumps(params, sort_keys=True)
            async with pool.acquire() as conn:
                result = await conn.fetchrow(
                    """
                    SELECT response_data FROM api_cache
                    WHERE api_name = $1 AND params = $2 AND expires_at > NOW()
                    """,
                    api_name, param_str
                )
                return json.loads(result['response_data']) if result else None
        except Exception as e:
            print(f"VectorService Cache Read Error: {e}")
            return None

    async def add_transit_knowledge(self, content: str, metadata: dict = None):
        try:
            pool = await self.get_pool()
            if not pool:
                return
            embedding = await self.get_embedding(content)
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO transit_knowledge (content, metadata, embedding)
                    VALUES ($1, $2, $3)
                    """,
                    content, json.dumps(metadata) if metadata else None, embedding
                )
                print(f"VectorService: Ingested knowledge: {content[:50]}...")
        except Exception as e:
            print(f"VectorService Ingestion Error: {e}")
