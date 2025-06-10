"""
Enterprise Data Processing Pipeline
ETL operations, data validation, and transformation logic.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)

def log_execution_time(func):
    """Decorator to log function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f"{func.__name__} completed in {elapsed:.2f}s")
        return result
    return wrapper

class DataValidator:
    """Validates incoming data quality"""
    
    @staticmethod
    def check_completeness(df: pd.DataFrame, threshold: float = 0.95) -> Dict[str, float]:
        """Check data completeness for each column"""
        completeness = {}
        for col in df.columns:
            non_null_ratio = df[col].notna().sum() / len(df)
            completeness[col] = non_null_ratio
            if non_null_ratio < threshold:
                logger.warning(f"Column '{col}' completeness: {non_null_ratio:.2%}")
        return completeness
    
    @staticmethod
    def check_uniqueness(df: pd.DataFrame, columns: List[str]) -> Dict[str, float]:
        """Check uniqueness of specified columns"""
        uniqueness = {}
        for col in columns:
            if col in df.columns:
                unique_ratio = df[col].nunique() / len(df)
                uniqueness[col] = unique_ratio
        return uniqueness
    
    @staticmethod
    def detect_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.Series:
        """Detect outliers using IQR or Z-score method"""
        if method == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return (df[column] < lower_bound) | (df[column] > upper_bound)
        elif method == 'zscore':
            from scipy import stats
            z_scores = np.abs(stats.zscore(df[column].dropna()))
            return z_scores > 3

class DataTransformer:
    """Applies business logic transformations"""
    
    def __init__(self):
        self.transformations_applied = 0
        self.rows_processed = 0
    
    @log_execution_time
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize dataframe"""
        initial_count = len(df)
        
        # Remove duplicate rows
        df = df.drop_duplicates()
        
        # Strip whitespace from string columns
        string_cols = df.select_dtypes(include=['object']).columns
        for col in string_cols:
            df[col] = df[col].str.strip()
        
        # Standardize date columns
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        for col in date_cols:
            try:
                df[col] = pd.to_datetime(df[col])
            except (ValueError, TypeError):
                pass
        
        self.rows_processed += len(df)
        logger.info(f"Cleaned {initial_count - len(df)} duplicate rows")
        
        return df
    
    def aggregate_data(self, df: pd.DataFrame, 
                       group_by: List[str], 
                       metrics: Dict[str, str]) -> pd.DataFrame:
        """Aggregate data by specified dimensions"""
        result = df.groupby(group_by).agg(metrics).reset_index()
        self.transformations_applied += 1
        return result
    
    def pivot_data(self, df: pd.DataFrame, 
                   index: str, columns: str, values: str) -> pd.DataFrame:
        """Pivot data for cross-tabulation"""
        return df.pivot_table(
            index=index, 
            columns=columns, 
            values=values, 
            aggfunc='sum',
            fill_value=0
        ).reset_index()

class DataPipeline:
    """Main data pipeline orchestrator"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.transformer = DataTransformer()
        self.pipeline_stats = {
            'runs': 0,
            'total_rows_processed': 0,
            'errors': 0,
            'last_run': None
        }
    
    @log_execution_time
    def run(self, df: pd.DataFrame, transformations: Optional[List[Dict]] = None) -> pd.DataFrame:
        """Execute the full data pipeline"""
        try:
            # Validate
            completeness = self.validator.check_completeness(df)
            
            # Transform
            df = self.transformer.clean_dataframe(df)
            
            # Apply custom transformations
            if transformations:
                for transform in transformations:
                    if transform.get('type') == 'aggregate':
                        df = self.transformer.aggregate_data(
                            df, 
                            transform['group_by'], 
                            transform['metrics']
                        )
            
            # Update stats
            self.pipeline_stats['runs'] += 1
            self.pipeline_stats['total_rows_processed'] += len(df)
            self.pipeline_stats['last_run'] = datetime.now().isoformat()
            
            return df
            
        except Exception as e:
            self.pipeline_stats['errors'] += 1
            logger.error(f"Pipeline failed: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return self.pipeline_stats

# Global pipeline instance
pipeline = DataPipeline()
