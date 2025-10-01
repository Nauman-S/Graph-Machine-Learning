import polars as pl #Much more effective for large datasets
import numpy as np
from typing import Optional, Tuple, Dict, Any
from pathlib import Path


class FraudDataLoader:
    """Data loader for IBM TabFormer credit card fraud dataset.
    
    This class handles loading, preprocessing, and preparing the synthetic
    credit card transaction data for graph machine learning visualization.
    """
    
    def __init__(self, data_path: str = "data/credit_card/card_transaction.v1.csv") -> None:
        """Initialize the data loader.
        
        Args:
            data_path: Path to the CSV file containing transaction data
        """
        self.data_path = Path(data_path)
        self.data: Optional[pl.DataFrame] = None
        self._validate_path()
        self.size: Optional[int] = None
    
    def _validate_path(self) -> None:
        """Validate that the data file exists."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found at {self.data_path}")
    
    def load_data(self, sample_size: Optional[int] = None, random_state: int = 42) -> pl.DataFrame:
        """Load the transaction data from CSV file.
        
        Args:
            sample_size: Number of rows to sample (None for full dataset)
            random_state: Random seed for reproducible sampling
            
        Returns:
            Polars DataFrame containing transaction data
        """
        print(f"Loading data from {self.data_path}...")
        

        if sample_size is not None:
            print(f"Sampling {sample_size:,}")
            
            self.data = (
                pl.scan_csv(self.data_path) # lazy scan (doesn't load into memory yet)
                .collect()
                .sample(n=sample_size, seed=random_state)
            )
        else:
            self.data = pl.read_csv(self.data_path) # Load full dataset with lazy evaluation
        
        print(f"Loaded {len(self.data):,} transactions")
        return self.data
    
    def preprocess_data(self) -> pl.DataFrame:
        """Preprocess the loaded data for analysis.
        
        Returns:
            Preprocessed Polars DataFrame
        """
        if self.data is None:
            raise ValueError("Data must be loaded first. Call load_data() before preprocessing.")
        
        # Polars efficient preprocessing with lazy evaluation
        self.data = (
            self.data
            .with_columns([
                # Parse datetime from separate columns
                pl.concat_str([
                    pl.col("Year").cast(pl.Utf8),
                    pl.lit("-"),
                    pl.col("Month").cast(pl.Utf8),
                    pl.lit("-"),
                    pl.col("Day").cast(pl.Utf8),
                    pl.lit(" "),
                    pl.col("Time")
                ]).str.strptime(pl.Datetime, "%Y-%m-%d %H:%M").alias("datetime"),
                
                # Clean amount column: strip currency symbols/commas then convert to float
                # Use a regex to remove any non-numeric characters except sign and decimal point
                pl.col("Amount")
                .cast(pl.Utf8)
                .str.replace_all(r"[^0-9.\-]", "")
                .str.strip_chars()
                .cast(pl.Float64, strict=False)
                .fill_null(0.0)
                .alias("Amount_clean"),
                
                # Create unique transaction ID
                pl.int_range(pl.len()).alias("transaction_id"),
                
                # Convert fraud label to binary
                pl.when(pl.col("Is Fraud?") == "Yes")
                .then(1)
                .otherwise(0)
                .alias("is_fraud_binary")
            ])
            .with_columns([
                # Add temporal features
                pl.col("datetime").dt.hour().alias("hour"),
                pl.col("datetime").dt.strftime("%A").alias("day_of_week"),
                pl.col("datetime").dt.strftime("%B").alias("month")
            ])
        )
        
        print(f"Preprocessing complete. Shape: {self.data.shape}")
        return self.data
    
    def get_basic_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the dataset.
        
        Returns:
            Dictionary containing dataset statistics
        """
        if self.data is None:
            raise ValueError("Data must be loaded first. Call load_data() before getting stats.")
        
        # Get stats efficiently with Polars
        stats_df = (
            self.data
            .select([
                pl.len().alias("total_transactions"),
                pl.col("User").n_unique().alias("unique_users"),
                pl.col("Merchant Name").n_unique().alias("unique_merchants"),
                pl.col("is_fraud_binary").mean().alias("fraud_rate"),
                pl.col("datetime").min().alias("date_start"),
                pl.col("datetime").max().alias("date_end"),
                pl.col("Amount_clean").mean().alias("amount_mean"),
                pl.col("Amount_clean").median().alias("amount_median"),
                pl.col("Amount_clean").std().alias("amount_std")
            ])
        )
        
        row = stats_df.row(0)
        
        stats = {
            'total_transactions': row[0],
            'unique_users': row[1],
            'unique_merchants': row[2],
            'fraud_rate': row[3] if row[3] is not None else 0,
            'date_range': {
                'start': row[4],
                'end': row[5]
            },
            'amount_stats': {
                'mean': row[6] if row[6] is not None else 0,
                'median': row[7] if row[7] is not None else 0,
                'std': row[8] if row[8] is not None else 0
            }
        }
        
        return stats
    
    def prepare_for_graph_visualization(self) -> Tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
        """Prepare data specifically for graph visualization.
        
        Returns:
            Tuple of (edges_df, nodes_df, metadata_df) for graph construction
        """
        if self.data is None:
            raise ValueError("Data must be loaded and preprocessed first.")
        
        print("Preparing data for graph visualization...")
        
        # Create edges DataFrame (transactions)
        edges_df = (
            self.data
            .select([
                pl.col("User").alias("source"),
                pl.col("Merchant Name").alias("target"),
                pl.col("Amount_clean").alias("amount"),
                pl.col("is_fraud_binary").alias("is_fraud"),
                pl.col("datetime").alias("timestamp"),
                pl.col("transaction_id"),
                pl.col("MCC").alias("mcc"),
                pl.col("Merchant City").alias("merchant_city"),
                pl.col("Merchant State").alias("merchant_state")
            ])
        )
        

        user_nodes = (
            self.data
            .select([
                pl.col("User").alias("node_id"),
                pl.lit("user").alias("node_type"),
            ])
            .unique()
            .with_columns([
                pl.lit(None).cast(pl.Utf8).alias("city"),
                pl.lit(None).cast(pl.Utf8).alias("state"),
                pl.lit(None).cast(pl.Utf8).alias("mcc")
            ])
        )
        
        # Create merchant nodes
        merchant_nodes = (
            self.data
            .select([
                pl.col("Merchant Name").alias("node_id"),
                pl.lit("merchant").alias("node_type"),
                pl.col("Merchant City").cast(pl.Utf8).alias("city"),
                pl.col("Merchant State").cast(pl.Utf8).alias("state"),
                pl.col("MCC").cast(pl.Utf8).alias("mcc")
            ])
            .unique()
        )
        
        # Combine node types
        nodes_df = pl.concat([user_nodes, merchant_nodes], how="vertical")
        
        
        # Create metadata for visualization
        metadata_df = (
            self.data
            .select([
                pl.col("transaction_id"),
                pl.col("datetime"),
                pl.col("hour"),
                pl.col("day_of_week"),
                pl.col("month")
            ])
        )
        
        print(f"Graph preparation complete:")
        print(f"  - Edges: {len(edges_df):,}")
        print(f"  - Nodes: {len(nodes_df):,} (Users: {len(user_nodes):,}, Merchants: {len(merchant_nodes):,})")
        
        return edges_df, nodes_df, metadata_df
    
    def get_sample_for_visualization(self, n_transactions: int = 10000, 
                                   fraud_ratio: Optional[float] = None) -> Tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
        """Get a balanced sample for visualization purposes.
        
        Args:
            n_transactions: Number of transactions to sample
            fraud_ratio: Desired ratio of fraudulent transactions (None for natural ratio)
            
        Returns:
            Tuple of (edges_df, nodes_df, metadata_df) for visualization
        """
        if self.data is None:
            raise ValueError("Data must be loaded and preprocessed first.")
        
        if fraud_ratio is None:
            # Use natural fraud ratio
            sample = self.data.sample(n=min(n_transactions, len(self.data)), seed=42)
        else:
            # Create balanced sample with Polars
            fraud_data = self.data.filter(pl.col("is_fraud_binary") == 1)
            normal_data = self.data.filter(pl.col("is_fraud_binary") == 0)
            
            n_fraud = int(n_transactions * fraud_ratio)
            n_normal = n_transactions - n_fraud
            
            fraud_sample = fraud_data.sample(n=min(n_fraud, len(fraud_data)), seed=42)
            normal_sample = normal_data.sample(n=min(n_normal, len(normal_data)), seed=42)
            
            sample = pl.concat([fraud_sample, normal_sample])
        
        # Temporarily replace self.data with sample for graph preparation
        original_data = self.data
        self.data = sample
        
        edges_df, nodes_df, metadata_df = self.prepare_for_graph_visualization()
        
        # Restore original data
        self.data = original_data
        
        return edges_df, nodes_df, metadata_df