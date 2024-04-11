"""
Tests for Data Processing Pipeline
"""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_processor import DataValidator, DataTransformer, DataPipeline


@pytest.fixture
def sample_dataframe():
    """Create sample dataframe for testing"""
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    
    df = pd.DataFrame({
        'date': dates,
        'revenue': np.random.normal(10000, 2000, 100),
        'users': np.random.randint(100, 1000, 100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 100),
        'satisfaction': np.random.uniform(3.0, 5.0, 100).round(2)
    })
    
    # Add some nulls
    df.loc[0, 'revenue'] = np.nan
    df.loc[50, 'users'] = np.nan
    
    # Add a duplicate
    df = pd.concat([df, df.iloc[:1]], ignore_index=True)
    
    return df


class TestDataValidator:
    """Test data validation"""
    
    def test_completeness_check(self, sample_dataframe):
        validator = DataValidator()
        completeness = validator.check_completeness(sample_dataframe)
        
        assert isinstance(completeness, dict)
        assert len(completeness) > 0
        
        # Some columns should have less than 100% completeness
        assert completeness['revenue'] < 1.0
        assert completeness['users'] < 1.0
    
    def test_uniqueness_check(self, sample_dataframe):
        validator = DataValidator()
        uniqueness = validator.check_uniqueness(sample_dataframe, ['category', 'region'])
        
        assert 'category' in uniqueness
        assert uniqueness['category'] < 1.0  # Categories repeat
    
    def test_outlier_detection_iqr(self, sample_dataframe):
        validator = DataValidator()
        outliers = validator.detect_outliers(sample_dataframe, 'revenue', method='iqr')
        
        assert isinstance(outliers, pd.Series)
        assert len(outliers) == len(sample_dataframe)
    
    def test_outlier_detection_zscore(self, sample_dataframe):
        validator = DataValidator()
        try:
            outliers = validator.detect_outliers(sample_dataframe, 'revenue', method='zscore')
            assert isinstance(outliers, pd.Series)
        except ImportError:
            pytest.skip("scipy not available")


class TestDataTransformer:
    """Test data transformation"""
    
    def test_clean_dataframe(self, sample_dataframe):
        transformer = DataTransformer()
        original_len = len(sample_dataframe)
        
        cleaned = transformer.clean_dataframe(sample_dataframe)
        
        # Should remove duplicates
        assert len(cleaned) < original_len
        assert isinstance(cleaned, pd.DataFrame)
    
    def test_aggregate_data(self, sample_dataframe):
        transformer = DataTransformer()
        
        result = transformer.aggregate_data(
            sample_dataframe,
            group_by=['category'],
            metrics={'revenue': 'sum', 'users': 'mean'}
        )
        
        assert len(result) == sample_dataframe['category'].nunique()
        assert 'revenue' in result.columns
        assert 'users' in result.columns
    
    def test_pivot_data(self, sample_dataframe):
        transformer = DataTransformer()
        
        result = transformer.pivot_data(
            sample_dataframe,
            index='region',
            columns='category',
            values='revenue'
        )
        
        assert len(result) == sample_dataframe['region'].nunique()


class TestDataPipeline:
    """Test full pipeline"""
    
    def test_pipeline_run(self, sample_dataframe):
        pipeline = DataPipeline()
        
        result = pipeline.run(sample_dataframe)
        
        assert isinstance(result, pd.DataFrame)
        assert pipeline.pipeline_stats['runs'] == 1
        assert pipeline.pipeline_stats['total_rows_processed'] > 0
        assert pipeline.pipeline_stats['last_run'] is not None
    
    def test_pipeline_stats(self, sample_dataframe):
        pipeline = DataPipeline()
        pipeline.run(sample_dataframe)
        
        stats = pipeline.get_stats()
        
        assert 'runs' in stats
        assert 'total_rows_processed' in stats
        assert 'errors' in stats
        assert 'last_run' in stats
    
    def test_pipeline_empty_dataframe(self):
        pipeline = DataPipeline()
        empty_df = pd.DataFrame()
        
        result = pipeline.run(empty_df)
        assert isinstance(result, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
