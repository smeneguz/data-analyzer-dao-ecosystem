# DAO Ecosystem Analyzer

A comprehensive tool for analyzing Decentralized Autonomous Organizations (DAOs) across multiple platforms including Aragon, DAOhaus, and DAOstack.

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