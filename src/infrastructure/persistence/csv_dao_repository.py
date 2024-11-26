import os
import pandas as pd
import kagglehub
from typing import List, Dict
from ...domain.interfaces.dao_repository import DAORepository
from ...domain.entities.dao_platform import DAOPlatform
from ...domain.entities.dao_file import DAOFile


ARAGON_DESCRIPTIONS = {
    "basic_info": {
        "name": "Organization name",
        "address": "Smart contract address of the organization",
        "created_at": "Creation timestamp",
        "network": "Blockchain network (e.g., mainnet)",
        "recovery_vault": "Address of recovery mechanism"
    },
    "apps": {
        "total_apps": "Total installed applications",
        "forwarder_apps": "Apps that can forward actions",
        "upgradeable_apps": "Apps that can be upgraded",
        "installed_apps": "List of installed Aragon apps"
    },
    "transactions": {
        "total_transactions": "Total number of transactions",
        "incoming_transactions": "Number of received transactions",
        "outgoing_transactions": "Number of sent transactions",
        "recent_transactions": "Last 5 transactions with details"
    },
    "votes": {
        "total_votes": "Total number of votes created",
        "executed_votes": "Number of executed votes",
        "recent_votes": "Last 5 votes with results"
    },
    "tokens": {
        "total_tokens": "Number of organization tokens",
        "token_details": "Information about each token",
        "holder_count": "Total token holders",
        "unique_holders": "Unique addresses holding tokens"
    }
}

class CSVDAORepository(DAORepository):
    """Implementation of DAORepository for CSV files."""
    
    def __init__(self):
        # Download dataset and get path
        self.base_path = kagglehub.dataset_download("daviddavo/dao-analyzer")
        print(f"Dataset path: {self.base_path}")
        self.platforms = ['aragon', 'daohaus', 'daostack']
        
        # Column descriptions for each file and platform
        self.column_descriptions = {
            'aragon': {
                'apps.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the app',
                    'isForwarder': 'Boolean indicating if app can forward actions',
                    'isUpgradeable': 'Boolean indicating if app can be upgraded',
                    'repoAddress': 'Repository address for the app',
                    'repoName': 'Name of the app repository',
                    'organizationId': 'ID of the organization owning the app'
                },
                'casts.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the vote cast',
                    'createdAt': 'Timestamp when vote was cast',
                    'stake': 'Amount staked in the vote',
                    'supports': 'Boolean indicating support for the proposal',
                    'appAddress': 'Address of the voting app',
                    'voteId': 'ID of the vote',
                    'orgAddress': 'Address of the organization',
                    'voter': 'Address of the voter'
                },
                'miniMeTokens.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the token',
                    'address': 'Token contract address',
                    'appAddress': 'Address of the app using the token',
                    'lastUpdateAt': 'Timestamp of last update',
                    'name': 'Token name',
                    'orgAddress': 'Organization address',
                    'symbol': 'Token symbol',
                    'totalSupply': 'Total supply of tokens',
                    'transferable': 'Boolean indicating if token is transferable'
                },
                'organizations.csv': {
                    'createdAt': 'Timestamp of organization creation',
                    'id': 'Unique identifier for the organization',
                    'recoveryVault': 'Address of recovery vault',
                    'network': 'Blockchain network identifier',
                    'name': 'Organization name',
                    'orgAddress': 'Organization contract address'
                },
                'repos.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the repository',
                    'address': 'Repository contract address',
                    'appCount': 'Number of apps in repository',
                    'name': 'Repository name',
                    'node': 'ENS node identifier'
                },
                'tokenHolders.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the token holding',
                    'address': 'Address of token holder',
                    'balance': 'Token balance',
                    'lastUpdateAt': 'Timestamp of last balance update',
                    'tokenAddress': 'Address of the token contract',
                    'organizationAddress': 'Address of the organization'
                },
                'transactions.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the transaction',
                    'amount': 'Transaction amount',
                    'appAddress': 'Address of the app executing transaction',
                    'date': 'Transaction timestamp',
                    'entity': 'Address of entity involved',
                    'isIncoming': 'Boolean indicating if transaction is incoming',
                    'orgAddress': 'Organization address',
                    'reference': 'Transaction reference/description',
                    'token': 'Address of token used in transaction'
                },
                'votes.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the vote',
                    'appAddress': 'Address of voting app',
                    'creator': 'Address of vote creator',
                    'executed': 'Boolean indicating if vote was executed',
                    'executedAt': 'Timestamp of execution',
                    'metadata': 'Additional vote metadata',
                    'minAcceptQuorum': 'Minimum acceptance quorum',
                    'nay': 'Number of negative votes',
                    'orgAddress': 'Organization address',
                    'originalCreator': 'Original creator address',
                    'startDate': 'Vote start timestamp',
                    'supportRequiredPct': 'Required support percentage',
                    'voteNum': 'Vote number',
                    'votingPower': 'Total voting power',
                    'yea': 'Number of positive votes'
                }
            },
            'daohaus': {
                'members.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the member',
                    'createdAt': 'Timestamp of membership creation',
                    'didRagequit': 'Boolean indicating if member has ragequit',
                    'exists': 'Boolean indicating if membership is active',
                    'loot': 'Amount of loot tokens held',
                    'memberAddress': 'Member\'s wallet address',
                    'molochAddress': 'Address of the Moloch DAO',
                    'shares': 'Number of shares held',
                    'tokenTribute': 'Amount of tribute tokens'
                },
                'moloches.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the Moloch DAO',
                    'createdAt': 'Timestamp of DAO creation',
                    'guildBankAddress': 'Address of guild bank',
                    'summoner': 'Address of DAO creator',
                    'summoningTime': 'Timestamp of DAO summoning',
                    'totalLoot': 'Total loot tokens',
                    'totalShares': 'Total shares issued',
                    'version': 'Moloch version',
                    'molochAddress': 'DAO contract address',
                    'name': 'Name of the DAO'
                },
                'proposals.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the proposal',
                    'createdAt': 'Timestamp of proposal creation',
                    'details': 'Proposal details in JSON format',
                    'didPass': 'Boolean indicating if proposal passed',
                    'lootRequested': 'Amount of loot requested',
                    'memberAddress': 'Address of proposing member',
                    'molochAddress': 'DAO address',
                    'noShares': 'Number of shares voting no',
                    'noVotes': 'Number of no votes',
                    'paymentRequested': 'Payment amount requested',
                    'processed': 'Boolean indicating if proposal was processed',
                    'processedAt': 'Timestamp of processing',
                    'proposalId': 'Proposal identifier',
                    'proposer': 'Address of proposer',
                    'sharesRequested': 'Number of shares requested',
                    'sponsored': 'Boolean indicating if proposal was sponsored',
                    'sponsoredAt': 'Timestamp of sponsorship',
                    'tributeOffered': 'Amount of tribute offered',
                    'yesShares': 'Number of shares voting yes',
                    'yesVotes': 'Number of yes votes'
                },
                'rageQuits.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the ragequit',
                    'createdAt': 'Timestamp of ragequit',
                    'loot': 'Amount of loot burned',
                    'memberAddress': 'Address of ragequitting member',
                    'molochAddress': 'DAO address',
                    'shares': 'Number of shares burned'
                },
                'tokenBalances.csv': {
                    'id': 'Unique identifier for the balance record',
                    'balance': 'Raw balance amount',
                    'molochAddress': 'DAO address',
                    'decimals': 'Token decimals',
                    'symbol': 'Token symbol',
                    'tokenAddress': 'Token contract address',
                    'network': 'Blockchain network identifier',
                    'bank': 'Bank type (e.g., guild)',
                    'balanceFloat': 'Normalized balance with decimals',
                    'usdValue': 'USD value of balance',
                    'ethValue': 'ETH value of balance',
                    'eurValue': 'EUR value of balance'
                },
                'votes.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the vote',
                    'createdAt': 'Timestamp of vote',
                    'memberAddress': 'Address of voting member',
                    'memberPower': 'Voting power of member',
                    'molochAddress': 'DAO address',
                    'uintVote': 'Vote choice as integer',
                    'proposalAddress': 'Address of proposal'
                }
            },
            'daostack': {
                'daos.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the DAO',
                    'name': 'Name of the DAO',
                    'register': 'Registration status',
                    'nativeReputation': 'Native reputation token address',
                    'nativeToken': 'Native token address',
                    'dao': 'DAO contract address'
                },
                'proposals.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the proposal',
                    'proposer': 'Address of proposer',
                    'stage': 'Current stage of proposal',
                    'createdAt': 'Timestamp of creation',
                    'preBoostedAt': 'Timestamp of pre-boost',
                    'boostedAt': 'Timestamp of boost',
                    'quietEndingPeriodBeganAt': 'Start of quiet ending period',
                    'closingAt': 'Scheduled closing time',
                    'executedAt': 'Timestamp of execution',
                    'title': 'Proposal title',
                    'description': 'Proposal description',
                    'url': 'Related URL',
                    'dao': 'DAO address'
                },
                'reputationBurns.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the burn',
                    'address': 'Address of reputation holder',
                    'amount': 'Amount of reputation burned',
                    'contract': 'Contract address',
                    'createdAt': 'Timestamp of burn',
                    'dao': 'DAO address'
                },
                'reputationHolders.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the holder',
                    'address': 'Address of reputation holder',
                    'balance': 'Reputation balance',
                    'contract': 'Contract address',
                    'createdAt': 'Timestamp of first holding',
                    'dao': 'DAO address'
                },
                'reputationMints.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the mint',
                    'address': 'Address receiving reputation',
                    'amount': 'Amount of reputation minted',
                    'contract': 'Contract address',
                    'createdAt': 'Timestamp of mint',
                    'dao': 'DAO address'
                },
                'stakes.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the stake',
                    'amount': 'Amount staked',
                    'createdAt': 'Timestamp of stake',
                    'outcome': 'Outcome of stake',
                    'staker': 'Address of staker',
                    'dao': 'DAO address',
                    'proposal': 'Proposal identifier'
                },
                'votes.csv': {
                    'network': 'Blockchain network identifier',
                    'id': 'Unique identifier for the vote',
                    'createdAt': 'Timestamp of vote',
                    'outcome': 'Vote outcome',
                    'reputation': 'Amount of reputation used',
                    'voter': 'Address of voter',
                    'dao': 'DAO address',
                    'proposal': 'Proposal identifier'
                }
            }
        }

    def get_all_platforms(self) -> List[DAOPlatform]:
        """Retrieve all DAO platforms and their associated files."""
        platforms = []
        
        for platform_name in self.platforms:
            platform_path = os.path.join(self.base_path, platform_name)
            if not os.path.exists(platform_path):
                print(f"Warning: Platform directory not found: {platform_path}")
                continue
                
            files = []
            for file_name in os.listdir(platform_path):
                if not file_name.endswith('.csv'):
                    continue
                    
                file_path = os.path.join(platform_path, file_name)
                try:
                    df = pd.read_csv(file_path)
                    
                    dao_file = DAOFile(
                        name=file_name,
                        folder=platform_name,
                        columns=list(df.columns),
                        column_descriptions=self.column_descriptions.get(platform_name, {}).get(file_name, {}),
                        sample_data=df.head().to_dict('records')
                    )
                    files.append(dao_file)
                except Exception as e:
                    print(f"Warning: Could not read file {file_path}: {str(e)}")
            
            platforms.append(DAOPlatform(name=platform_name, files=files))
        
        return platforms