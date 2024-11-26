# src/presentation/cli/main.py
import click
from ...application.services.dao_analyzer_service import DAOAnalyzerService
from ...infrastructure.persistence.csv_dao_repository import CSVDAORepository

@click.group()
def cli():
    """DAO Analyzer - A tool for analyzing DAO platforms data."""
    pass

@cli.command()
@click.option('--platform', 
              type=click.Choice(['aragon', 'daohaus', 'daostack'], case_sensitive=False),
              required=True, 
              help='DAO platform to analyze')
def active_organizations(platform):
    """Show organization statistics for a platform."""
    try:
        repository = CSVDAORepository()
        service = DAOAnalyzerService(repository)
        result = service.get_active_organizations(platform)
        
        click.echo(f"\nPlatform: {platform.upper()}")
        click.echo("=" * 40)
        click.echo(f"Total Organizations: {result['total_organizations']}")
        click.echo(f"Active Organizations: {result['active_organizations']}")
        click.echo(f"Inactive Organizations: {result['inactive_organizations']}")
        if result['total_organizations'] > 0:
            activity_rate = (result['active_organizations'] / result['total_organizations']) * 100
            click.echo(f"Activity Rate: {activity_rate:.2f}%")
        
    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)

if __name__ == '__main__':
    cli()