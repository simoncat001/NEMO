from sqlalchemy import create_engine, inspect
import os

# Database connection parameters
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "nemo_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def inspect_table(table_name):
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    if not inspector.has_table(table_name):
        print(f"Table '{table_name}' does not exist.")
        return

    columns = inspector.get_columns(table_name)
    print(f"Columns in table '{table_name}':")
    for column in columns:
        print(f"  - {column['name']} ({column['type']}) - Nullable: {column['nullable']}")

if __name__ == "__main__":
    inspect_table("area")
