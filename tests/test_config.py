import pytest
import os
from unittest.mock import patch
from config import Config, DevelopmentConfig, ProductionConfig

class TestConfig:
    """Test per la configurazione dell'applicazione"""
    
    def test_development_config(self):
        """Test configurazione sviluppo"""
        with patch.dict(os.environ, {
            'FLASK_ENV': 'development',
            'SECRET_KEY': 'test-secret',
            'OPENAI_API_KEY': 'test-api-key'
        }):
            config = DevelopmentConfig()
            assert config.DEBUG is True
            assert config.FLASK_ENV == 'development'
            # SECRET_KEY viene hashata, quindi non possiamo testare il valore esatto
            assert config.SECRET_KEY is not None
    
    def test_production_config(self):
        """Test configurazione produzione"""
        with patch.dict(os.environ, {
            'FLASK_ENV': 'production',
            'SECRET_KEY': 'test-secret',
            'OPENAI_API_KEY': 'test-api-key'
        }):
            config = ProductionConfig()
            assert config.DEBUG is False
            assert config.FLASK_ENV == 'production'
    
    def test_validate_success(self):
        """Test validazione con tutte le variabili richieste"""
        with patch.dict(os.environ, {
            'SECRET_KEY': 'test-secret',
            'OPENAI_API_KEY': 'test-api-key'
        }):
            assert Config.validate() is True
    
    def test_config_attributes(self):
        """Test attributi di configurazione"""
        config = Config()
        # Test che gli attributi esistono
        assert hasattr(config, 'MODEL')
        assert hasattr(config, 'TOP_K')
        assert hasattr(config, 'MIN_OVERLAP')
        assert hasattr(config, 'SECRET_KEY')
        assert hasattr(config, 'OPENAI_API_KEY')
        
        # Test valori numerici
        assert isinstance(config.TOP_K, int)
        assert isinstance(config.MIN_OVERLAP, float)
        assert config.TOP_K > 0
        assert config.MIN_OVERLAP >= 0 