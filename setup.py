import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database.models import create_tables
from database.setup_db import seed_data

if __name__ == '__main__':
    create_tables()
    seed_data()
