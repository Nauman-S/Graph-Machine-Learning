"""
Data loader for the Elliptic dataset.
Handles loading from local files instead of Kaggle's pre-mounted directory.
"""

import os
from pathlib import Path
from typing import Tuple, Optional

import numpy as np
import pandas as pd


class EllipticDataLoader:
    """Load and process the Elliptic dataset from local files."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the data loader.
        
        Args:
            data_dir: Path to the data directory. If None, uses default 'data/elliptic'
        """
        if data_dir is None:
            # Get the project root directory
            project_root = Path(__file__).parent.parent
            data_dir = project_root / "data" / "elliptic"
        
        self.data_dir = Path(data_dir)
        
        # Expected file names
        self.features_file = "elliptic_txs_features.csv"
        self.classes_file = "elliptic_txs_classes.csv"
        self.edgelist_file = "elliptic_txs_edgelist.csv"
        
    def check_files_exist(self) -> bool:
        """Check if all required dataset files exist."""
        required_files = [
            self.data_dir / self.features_file,
            self.data_dir / self.classes_file,
            self.data_dir / self.edgelist_file
        ]
        
        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print("Missing files:")
            for file in missing_files:
                print(f"  - {file}")
            return False
        
        return True
    
    def list_data_files(self) -> None:
        """List all files in the data directory (similar to Kaggle's walk)."""
        print(f"Files in {self.data_dir}:")
        
        if not self.data_dir.exists():
            print(f"Directory {self.data_dir} does not exist!")
            return
        
        for root, dirs, files in os.walk(self.data_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                print(f"  {filepath}")
    
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Load all components of the Elliptic dataset.
        
        Returns:
            Tuple of (features_df, classes_df, edges_df)
        
        Raises:
            FileNotFoundError: If any required files are missing
        """
        if not self.check_files_exist():
            raise FileNotFoundError(
                f"Dataset files not found in {self.data_dir}. "
                "Please download the dataset from Kaggle first."
            )
        
        print("Loading Elliptic dataset...")
        
        # Load features
        features_df = pd.read_csv(self.data_dir / self.features_file, header=None)
        print(f"Loaded features: {features_df.shape}")
        
        # Load classes
        classes_df = pd.read_csv(self.data_dir / self.classes_file)
        print(f"Loaded classes: {classes_df.shape}")
        
        # Load edges
        edges_df = pd.read_csv(self.data_dir / self.edgelist_file)
        print(f"Loaded edges: {edges_df.shape}")
        
        return features_df, classes_df, edges_df
    
    def load_processed_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load and merge features with classes.
        
        Returns:
            Tuple of (merged_data, edges_df)
        """
        features_df, classes_df, edges_df = self.load_data()
        
        # The first column of features is the transaction ID
        features_df.columns = ['txId'] + [f'feature_{i}' for i in range(1, features_df.shape[1])]
        
        # Merge features with classes
        merged_df = pd.merge(features_df, classes_df, on='txId', how='left')
        
        print(f"\nDataset statistics:")
        print(f"Total transactions: {len(merged_df)}")
        print(f"Class distribution:")
        print(merged_df['class'].value_counts())
        
        return merged_df, edges_df


# Example usage
if __name__ == "__main__":
    # Create data loader
    loader = EllipticDataLoader()
    
    # List files in data directory
    loader.list_data_files()
    
    # Try to load the data
    try:
        features_df, classes_df, edges_df = loader.load_data()
        print("\nDataset loaded successfully!")
        
        # Load processed data
        merged_df, edges_df = loader.load_processed_data()
        
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nTo use this dataset:")
        print("1. Download the Elliptic dataset from Kaggle")
        print("2. Extract the CSV files to: data/elliptic/")
