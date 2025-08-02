"""Command-line interface for the crack project."""

import sys
from typing import Optional

import click

from crack.config import get_config


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config-file', '-c', help='Path to configuration file')
def main(verbose: bool, config_file: Optional[str]) -> None:
    """Crack - Software License Tools
    
    A collection of tools for generating and managing software licenses.
    """
    config = get_config()
    
    if verbose:
        config.log_level = "DEBUG"
    
    if config_file:
        # TODO: Implement config file loading
        click.echo(f"Config file loading not yet implemented: {config_file}")


@main.group()
def jetbrains() -> None:
    """JetBrains related commands."""
    pass


@jetbrains.command()
@click.option('--license-id', help='Custom license ID')
@click.option('--license-name', help='Custom license name')
@click.option('--no-patch', is_flag=True, help='Skip patch generation')
def generate(license_id: Optional[str], license_name: Optional[str], no_patch: bool) -> None:
    """Generate JetBrains license."""
    try:
        from crack.jetbrains.jetbrains import JetbrainsKeyGen
        
        keygen = JetbrainsKeyGen()
        keygen.run(patch=not no_patch, license_id=license_id, license_name=license_name)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@jetbrains.command()
@click.option('--host', default='0.0.0.0', help='Server host')
@click.option('--port', default=5000, help='Server port')
def server(host: str, port: int) -> None:
    """Start JetBrains license server."""
    try:
        import uvicorn
        from crack.jetbrains.server import app
        
        click.echo(f"Starting JetBrains license server on {host}:{port}")
        uvicorn.run(app, host=host, port=port)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@jetbrains.command()
def update_plugins() -> None:
    """Update JetBrains plugins database."""
    try:
        from crack.jetbrains.plugins import JetBrainPlugin
        
        click.echo("Updating JetBrains plugins database...")
        plugin_manager = JetBrainPlugin()
        plugin_manager.update().make_licenses()
        click.echo("Plugins database updated successfully!")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def dbeaver() -> None:
    """DBeaver related commands."""
    pass


@dbeaver.command()
@click.option('--no-patch', is_flag=True, help='Skip patch generation')
def generate(no_patch: bool) -> None:
    """Generate DBeaver license."""
    try:
        from crack.dbeaver.dbeaver import DBeaverKeyGen
        
        keygen = DBeaverKeyGen()
        keygen.run(patch=not no_patch)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def typora() -> None:
    """Typora related commands."""
    pass


@typora.command()
def generate() -> None:
    """Generate Typora license."""
    try:
        from crack.typora.typora import TyporaKeyGen
        
        keygen = TyporaKeyGen()
        keygen.run()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
def list_modules() -> None:
    """List all available modules."""
    modules = [
        ("jetbrains", "JetBrains IDEs and plugins"),
        ("dbeaver", "DBeaver database tool"),
        ("typora", "Typora markdown editor"),
        ("xmind", "XMind mind mapping"),
        ("atlassian", "Atlassian products"),
        ("gitlab", "GitLab Enterprise Edition"),
        ("finalshell", "FinalShell terminal"),
        ("surely", "Surely application"),
    ]
    
    click.echo("Available modules:")
    for module, description in modules:
        click.echo(f"  {module:<12} - {description}")


@main.command()
@click.argument('module')
def info(module: str) -> None:
    """Show information about a specific module."""
    module_info = {
        "jetbrains": {
            "description": "JetBrains IDEs and plugins license generator",
            "commands": ["generate", "server", "update-plugins"],
            "files": ["licenses.json", "plugins.json", "cert.crt", "key.pem"],
        },
        "dbeaver": {
            "description": "DBeaver database tool license generator",
            "commands": ["generate"],
            "files": ["dbeaver-ue-public.key", "key.pem"],
        },
        "typora": {
            "description": "Typora markdown editor license generator",
            "commands": ["generate"],
            "files": ["key.pem"],
        },
    }
    
    if module not in module_info:
        click.echo(f"Unknown module: {module}", err=True)
        sys.exit(1)
    
    info_data = module_info[module]
    click.echo(f"Module: {module}")
    click.echo(f"Description: {info_data['description']}")
    click.echo(f"Commands: {', '.join(info_data['commands'])}")
    click.echo(f"Required files: {', '.join(info_data['files'])}")


if __name__ == '__main__':
    main()
