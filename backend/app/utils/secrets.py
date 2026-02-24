"""Secret management utilities."""
import os


def get_secret(key: str, default: str = "") -> str:
    """
    Get secret from file or environment variable.

    Supports Docker secrets pattern (_FILE suffix) and direct environment variables.

    Args:
        key: Environment variable name (e.g., 'GOLDAPI_KEY')
        default: Default value if not found

    Returns:
        Secret value from file or environment variable
    """
    # Check for _FILE variant (Docker secrets pattern)
    file_key = f"{key}_FILE"
    secret_file = os.getenv(file_key)

    if secret_file and os.path.exists(secret_file):
        with open(secret_file, 'r') as f:
            return f.read().strip()

    # Fall back to direct environment variable
    return os.getenv(key, default)
