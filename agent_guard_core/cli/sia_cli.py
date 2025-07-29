import asyncio
import logging
from typing import Optional
from urllib.parse import quote_plus

import click

from agent_guard_core.api.identity.handler import IdentityConfig, IdentityHandler
from agent_guard_core.api.sia.handler import SecureInfraAccessHandler
from agent_guard_core.cli.mcp_proxy_cli import ProxyCapability, _stdio_mcp_proxy_async
from agent_guard_core.utils.env import CYBERARK_DOMAIN

logger = logging.getLogger(__name__)

@click.group(name="sia", help="Connect to PostgreSQL databases using SIA")
def sia():
    """Commands for managing Secure Infrastructure Access PostgreSQL connections."""
    pass

@sia.group(name="postgres", help="PostgreSQL connectivity using sia")
def sia_postgresdb():
    """Commands for managing Secure Infrastructure Access PostgreSQL connections."""
    pass

@sia_postgresdb.command(name="generate", help="Generate a connection string for PostgreSQL using SIA credentials")
@click.option(
    '--username',
    '-u',
    required=True,
    help="Username for database access (e.g., myuser@cyberark.cloud)"
)
@click.option(
    '--tenant-id',
    '-t',
    required=True,
    help="Tenant ID (e.g., acmeinc)"
)
@click.option(
    '--db-host',
    '-h',
    required=True,
    help="Database host FQDN"
)
@click.option(
    '--database',
    '-d',
    default='postgres',
    help="Database name (default: postgres)"
)
@click.option(
    '--debug',
    is_flag=True,
    help="Enable debug logging"
)
def generate(username: str, tenant_id: str, db_host: str, database: str, debug: bool = False):
    """Connect to a PostgreSQL database using Secure Infrastructure Access authentication."""
    if debug:
        logging.disable(logging.NOTSET)
        
    identity_handler = IdentityHandler()
    if identity_handler.access_token is None:
        raise click.ClickException(
            "No valid login session found. Please run 'agc idp login' first."
        )
    
    try:
        # Initialize SIA handler and get credentials
        sia_handler = SecureInfraAccessHandler(tenant_id=tenant_id, 
                                               access_token=identity_handler.access_token)
        
        password = sia_handler.get_short_lived_password()
        # Construct the connection string
        # Format: postgresql://<username>#<tenant_id>@<host>:<password>@<host>/<database>
        sia_username = f"{username}#{tenant_id}@{db_host}"
        target_host = f"{tenant_id}.postgres.{CYBERARK_DOMAIN}"

        connection_string = f"postgresql://{target_host}:5432/{database}?user={quote_plus(sia_username)}&password={quote_plus(password)}&sslmode=require"
        #connection_string = f"postgresql://{quote_plus(sia_username)}:{quote_plus(password)}@{target_host}:5432/{database}"
        print(connection_string)
        
    except Exception as e:
        raise click.ClickException(f"Failed to generate postgres connection string: {str(e)}")
