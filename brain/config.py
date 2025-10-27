import configparser
import os
import sys


# Configuration file path
CONFIG_FILE = 'C:\\Users\\HP\\Documents\\takneev5\\config\\config.ini'

def create_default_config():
    """Create a default config.ini file if it doesn't exist"""
    config = configparser.ConfigParser()
    config['DATABASE'] = {
        'host': 'localhost',
        'user': '',
        'password': '',
        'database': 'takneev5'
    }
    config['API'] = {
        'gemini_api_key': ''
    }
    
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    
    print(f"\n{'='*60}")
    print(f"CONFIGURATION FILE CREATED: {CONFIG_FILE}")
    print(f"{'='*60}")
    print("\nPlease edit the config.ini file and add the following:")
    print("\n[DATABASE]")
    print("  - user: Your MySQL username (e.g., root)")
    print("  - password: Your MySQL password")
    print("  - host: MySQL server host (default: localhost)")
    print("  - database: Database name (default: takneev5)")
    print("\n[API]")
    print("  - gemini_api_key: Your Google Gemini API key")
    print(f"\n{'='*60}")
    print("After editing config.ini, restart the application.")
    print(f"{'='*60}\n")
    sys.exit(1)

def load_config():
    """Load configuration from config.ini file"""
    if not os.path.exists(CONFIG_FILE):
        print(f"Configuration file '{CONFIG_FILE}' not found.")
        create_default_config()
    
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    
    # Validate database configuration
    if not config.has_section('DATABASE'):
        print("ERROR: [DATABASE] section missing in config.ini")
        sys.exit(1)
    
    db_user = config.get('DATABASE', 'user', fallback='').strip()
    db_password = config.get('DATABASE', 'password', fallback='').strip()
    
    if not db_user:
        print("\nERROR: Database user is not configured in config.ini")
        print("Please edit config.ini and set the 'user' value under [DATABASE]")
        sys.exit(1)
    
    # Validate API configuration
    if not config.has_section('API'):
        print("ERROR: [API] section missing in config.ini")
        sys.exit(1)
    
    api_key = config.get('API', 'gemini_api_key', fallback='').strip()
    if not api_key:
        print("\nWARNING: Gemini API key is not configured in config.ini")
    
    return config

