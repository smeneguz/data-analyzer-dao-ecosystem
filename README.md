# DAO Ecosystem Analyzer

A tool for analyzing Decentralized Autonomous Organizations (DAOs) across multiple platforms including Aragon, DAOhaus, and DAOstack.

## Overview

This project provides a scalable and modular framework for analyzing DAO metrics and activities across different platforms. It currently supports:

- Aragon
- DAOhaus
- DAOstack

## Features

- Organization activity analysis

## Getting Started

### Prerequisites

- Python 3.8+
- Kaggle API credentials (open)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/smeneguz/data-analyzer-dao-ecosystem.git
cd data-analyzer-dao-ecosystem
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage
Just for example considering that we want information inside aragon datasets: 
```bash
python -m src.presentation.cli.main active-organizations --platform aragon
```

Other possible commands: 

```bash
Show Structure (Basic)

python -m src.presentation.cli.main show-structure

python -m src.presentation.cli.main show-structure --platform aragon
python -m src.presentation.cli.main show-structure --platform daohaus
python -m src.presentation.cli.main show-structure --platform daostack

Show Detailed Structure

python -m src.presentation.cli.main show-structure --platform aragon --output detailed


Find Column

python -m src.presentation.cli.main find-column --platform aragon --column address
python -m src.presentation.cli.main find-column --platform daohaus --column member
python -m src.presentation.cli.main find-column --platform daostack --column dao

Purpose: Searches for a specific column across all files in a platform


Show Active Organizations:

python -m src.presentation.cli.main active-organizations --platform aragon
python -m src.presentation.cli.main active-organizations --platform daohaus
python -m src.presentation.cli.main active-organizations --platform daostack

```

Legenda: 

Activity Categories
Organizations are categorized based on their activity levels:

Highly Active: Recent and frequent activity
Moderately Active: Regular activity within the last 90 days
Minimally Active: Occasional activity
Inactive: No recent activity
Test/Potential Test: Organizations showing characteristics of test deployments

