# src/presentation/cli/main.py
import click
from ...application.services.dao_analyzer_service import DAOAnalyzerService
from ...infrastructure.persistence.csv_dao_repository import CSVDAORepository

@click.group()
def cli():
    """DAO Analyzer - A tool for analyzing DAO platforms data."""
    pass

# src/presentation/cli/main.py

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
        
        click.echo(f"\n{click.style(f'Platform: {platform.upper()}', fg='green', bold=True)}")
        click.echo("=" * 50)
        
        # Basic statistics
        click.echo(f"\n{click.style('Overview:', fg='blue', bold=True)}")
        click.echo(f"Total Organizations: {result['total_organizations']}")
        click.echo(f"Active Organizations: {result['active_organizations']}")
        click.echo(f"Inactive Organizations: {result['inactive_organizations']}")
        
        # Activity breakdown
        click.echo(f"\n{click.style('Activity Breakdown:', fg='blue', bold=True)}")
        click.echo(f"Highly Active: {result['highly_active']}")
        click.echo(f"Moderately Active: {result['moderately_active']}")
        click.echo(f"Minimally Active: {result['minimally_active']}")
        click.echo(f"Potential Test Organizations: {result['potential_test']}")
        
        # Detailed DAO information
        if 'detailed_activity' in result:
            # Highly active DAOs
            if result['detailed_activity']['highly_active_daos']:
                click.echo(f"\n{click.style('Highly Active DAOs:', fg='green', bold=True)}")
                for dao in result['detailed_activity']['highly_active_daos']:
                    click.echo("-" * 40)
                    click.echo(f"Name: {dao['name']}")
                    click.echo(f"Address: {dao['address']}")
                    if 'tx_count' in dao:
                        click.echo(f"Transactions: {dao['tx_count']}")
                    if 'proposal_count' in dao:
                        click.echo(f"Proposals: {dao['proposal_count']}")
                    if 'vote_count' in dao:
                        click.echo(f"Votes: {dao['vote_count']}")
                    if 'member_count' in dao:
                        click.echo(f"Members: {dao['member_count']}")
                    click.echo(f"Last Activity: {dao['last_activity'].strftime('%Y-%m-%d')}")
            
            # Moderately active DAOs
            if result['detailed_activity']['moderately_active_daos']:
                click.echo(f"\n{click.style('Moderately Active DAOs:', fg='yellow', bold=True)}")
                for dao in result['detailed_activity']['moderately_active_daos']:
                    click.echo("-" * 40)
                    click.echo(f"Name: {dao['name']}")
                    click.echo(f"Address: {dao['address']}")
                    if 'tx_count' in dao:
                        click.echo(f"Transactions: {dao['tx_count']}")
                    if 'proposal_count' in dao:
                        click.echo(f"Proposals: {dao['proposal_count']}")
                    if 'vote_count' in dao:
                        click.echo(f"Votes: {dao['vote_count']}")
                    if 'member_count' in dao:
                        click.echo(f"Members: {dao['member_count']}")
                    click.echo(f"Last Activity: {dao['last_activity'].strftime('%Y-%m-%d')}")
        
        # Calculate and display activity rate
        if result['total_organizations'] > 0:
            activity_rate = (result['active_organizations'] / result['total_organizations']) * 100
            click.echo(f"\n{click.style('Overall Activity Rate:', fg='blue', bold=True)} {activity_rate:.2f}%")
        
    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)


    
@cli.command()
@click.option('--platform', 
              type=click.Choice(['aragon', 'daohaus', 'daostack'], case_sensitive=False),
              help='Specific platform to analyze (optional)')
@click.option('--output', 
              type=click.Choice(['text', 'detailed']), 
              default='text',
              help='Output format')
def show_structure(platform, output):
    """Display the structure of DAO platform files and their columns."""
    try:
        repository = CSVDAORepository()
        service = DAOAnalyzerService(repository)
        structure = service.get_file_structure(platform)
        
        for platform_name, files in structure.items():
            click.echo(f"\n{click.style(f'Platform: {platform_name.upper()}', fg='green', bold=True)}")
            click.echo("=" * 50)
            
            for file_name, file_info in files.items():
                click.echo(f"\n{click.style(f'File: {file_name}', fg='yellow', bold=True)}")
                click.echo(f"Total columns: {file_info['total_columns']}")
                
                if output == 'detailed':
                    click.echo("\nColumns:")
                    for col_name, col_info in file_info['columns'].items():
                        click.echo(f"\n  {click.style(col_name, fg='blue', bold=True)}:")
                        click.echo(f"  Description: {col_info['description']}")
                        if col_info['sample_values']:
                            sample_str = ', '.join(col_info['sample_values'][:3])
                            click.echo(f"  Sample values: {sample_str}")
                else:
                    # Simple column list
                    columns = list(file_info['columns'].keys())
                    click.echo("\nColumns:")
                    for col in columns:
                        click.echo(f"  - {col}")
                
                click.echo("-" * 50)
                
    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)

@cli.command()
@click.option('--platform', 
              type=click.Choice(['aragon', 'daohaus', 'daostack'], case_sensitive=False),
              required=True,
              help='Platform to search')
@click.option('--column', 
              required=True,
              help='Column name to search for')
def find_column(platform, column):
    """Search for a specific column across all files in a platform."""
    try:
        repository = CSVDAORepository()
        service = DAOAnalyzerService(repository)
        structure = service.get_file_structure(platform)
        
        found = False
        platform_data = structure[platform]
        
        click.echo(f"\nSearching for column '{column}' in {platform.upper()}:")
        click.echo("=" * 50)
        
        for file_name, file_info in platform_data.items():
            for col_name, col_info in file_info['columns'].items():
                if column.lower() in col_name.lower():
                    found = True
                    click.echo(f"\nFile: {click.style(file_name, fg='yellow', bold=True)}")
                    click.echo(f"Column: {click.style(col_name, fg='blue', bold=True)}")
                    click.echo(f"Description: {col_info['description']}")
                    if col_info['sample_values']:
                        sample_str = ', '.join(col_info['sample_values'][:3])
                        click.echo(f"Sample values: {sample_str}")
                    click.echo("-" * 30)
        
        if not found:
            click.echo(f"No columns found matching '{column}'")
            
    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)

if __name__ == '__main__':
    cli()