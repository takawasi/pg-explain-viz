"""CLI interface for pg-explain-viz."""

import sys
import click
from pathlib import Path
from rich.console import Console

from .executor import run_explain, PSYCOPG2_AVAILABLE
from .parser import parse_explain_json
from .renderer import render_plan

console = Console()


@click.command()
@click.argument('query', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Read query from file')
@click.option('--dsn', help='Connection string (postgresql://...)')
@click.option('--host', '-h', default='localhost', help='Database host')
@click.option('--port', '-p', default=5432, type=int, help='Database port')
@click.option('--database', '-d', default='postgres', help='Database name')
@click.option('--user', '-U', default='postgres', help='Database user')
@click.option('--password', '-W', default='', help='Database password')
@click.option('--json-input', type=click.Path(exists=True), help='Parse existing EXPLAIN JSON file')
@click.version_option()
def main(query, file, dsn, host, port, database, user, password, json_input):
    """Visualize PostgreSQL EXPLAIN ANALYZE as ASCII tree.

    Examples:

        pg-explain "SELECT * FROM users" -d mydb
        pg-explain -f query.sql --dsn postgresql://localhost/mydb
        pg-explain --json-input explain.json
    """
    # Get query
    if json_input:
        # Parse existing JSON
        json_str = Path(json_input).read_text()
    else:
        if file:
            query = Path(file).read_text()
        elif not query:
            console.print("[red]Error:[/red] Provide a query or --file")
            sys.exit(1)

        if not PSYCOPG2_AVAILABLE:
            console.print("[red]Error:[/red] psycopg2 not installed.")
            console.print("Run: pip install psycopg2-binary")
            console.print("\nOr use --json-input with pre-generated EXPLAIN output.")
            sys.exit(1)

        # Run EXPLAIN
        console.print(f"[dim]Running EXPLAIN ANALYZE...[/dim]", file=sys.stderr)

        try:
            json_str = run_explain(
                query=query,
                dsn=dsn,
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
            )
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)

    # Parse and render
    try:
        plan = parse_explain_json(json_str)
        render_plan(plan, console)
    except Exception as e:
        console.print(f"[red]Parse error:[/red] {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
