import logging

from supabase import Client, create_client

from app.config.settings import Settings
from app.utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)

_client: Client | None = None


def get_supabase_client(settings: Settings) -> Client:
    global _client

    if _client is not None:
        return _client

    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise DatabaseError("Supabase credentials are not configured.")

    try:
        _client = create_client(settings.supabase_url, settings.supabase_service_role_key)
        return _client
    except Exception as exc:
        logger.exception("Failed to initialize Supabase client")
        raise DatabaseError("Unable to initialize Supabase client.") from exc
