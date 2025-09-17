# Dataset Directory

This directory is intended for storing datasets used in this Graph Machine Learning project.

## Elliptic Dataset

The Elliptic dataset is a graph network dataset of Bitcoin transactions (nodes) and payment flows (edges). It's used for detecting illicit transactions in cryptocurrency networks.

### Dataset Structure
- **elliptic_txs_features.csv**: Transaction features (200 features per transaction)
- **elliptic_txs_classes.csv**: Transaction labels (licit, illicit, unknown)
- **elliptic_txs_edgelist.csv**: Edge list showing payment flows between transactions

### Obtaining the Dataset
1. Download from Kaggle: https://www.kaggle.com/datasets/ellipticco/elliptic-data-set
2. Extract the files into this directory
3. The data files should be placed directly in `data/elliptic/`

### Git Submodule Alternative
If you have the dataset in a separate git repository, you can add it as a submodule.
