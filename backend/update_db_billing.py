import asyncio
import sys
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def main():
    try:
        async with AsyncSessionLocal() as session:
            print("Updating database schema for billing...")
            
            # 1. Create consumable table
            print("Creating 'consumable' table...")
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS consumable (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL UNIQUE,
                    category VARCHAR(100),
                    visible BOOLEAN DEFAULT TRUE NOT NULL,
                    price NUMERIC(10, 2) DEFAULT 0.00 NOT NULL
                )
            """))
            await session.commit()
            await session.execute(text("CREATE INDEX IF NOT EXISTS ix_consumable_id ON consumable (id)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS ix_consumable_name ON consumable (name)"))
            await session.commit()
            
            # 2. Create consumable_withdraw table
            print("Creating 'consumable_withdraw' table...")
            # Drop table if exists to ensure clean state
            await session.execute(text("DROP TABLE IF EXISTS consumable_withdraw"))
            await session.commit()
            
            await session.execute(text("""
                CREATE TABLE consumable_withdraw (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    consumable_id INTEGER NOT NULL REFERENCES consumable(id) ON DELETE CASCADE,
                    project_id INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
                    quantity INTEGER DEFAULT 1 NOT NULL,
                    amount NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
                    date TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc') NOT NULL
                )
            """))
            await session.commit()
            await session.execute(text("CREATE INDEX IF NOT EXISTS ix_consumable_withdraw_id ON consumable_withdraw (id)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS ix_consumable_withdraw_user_id ON consumable_withdraw (user_id)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS ix_consumable_withdraw_consumable_id ON consumable_withdraw (consumable_id)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS ix_consumable_withdraw_project_id ON consumable_withdraw (project_id)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS ix_consumable_withdraw_date ON consumable_withdraw (date)"))
            await session.commit()

            # 3. Add columns to tool table
            print("Adding pricing columns to 'tool' table...")
            try:
                await session.execute(text("ALTER TABLE tool ADD COLUMN IF NOT EXISTS price_type INTEGER DEFAULT 1 NOT NULL"))
            except Exception as e:
                print(f"Error adding price_type: {e}")
            try:
                await session.execute(text("ALTER TABLE tool ADD COLUMN IF NOT EXISTS price_per_use NUMERIC(10, 2) DEFAULT 0.00 NOT NULL"))
            except Exception as e:
                print(f"Error adding price_per_use: {e}")
            try:
                await session.execute(text("ALTER TABLE tool ADD COLUMN IF NOT EXISTS price_per_hour NUMERIC(10, 2) DEFAULT 0.00 NOT NULL"))
            except Exception as e:
                print(f"Error adding price_per_hour: {e}")
            await session.commit()
            
            # 4. Add columns to usage_event table
            print("Adding amount column to 'usage_event' table...")
            try:
                await session.execute(text("ALTER TABLE usage_event ADD COLUMN IF NOT EXISTS amount NUMERIC(10, 2) DEFAULT 0.00"))
            except Exception as e:
                print(f"Error adding amount: {e}")
            await session.commit()

            # 3. Add columns to tool table
            print("Adding pricing columns to 'tool' table...")
            await session.execute(text("ALTER TABLE tool ADD COLUMN IF NOT EXISTS price_type INTEGER DEFAULT 1 NOT NULL"))
            await session.execute(text("ALTER TABLE tool ADD COLUMN IF NOT EXISTS price_per_use NUMERIC(10, 2) DEFAULT 0.00 NOT NULL"))
            await session.execute(text("ALTER TABLE tool ADD COLUMN IF NOT EXISTS price_per_hour NUMERIC(10, 2) DEFAULT 0.00 NOT NULL"))
            
            # 4. Add columns to usage_event table
            print("Adding amount column to 'usage_event' table...")
            await session.execute(text("ALTER TABLE usage_event ADD COLUMN IF NOT EXISTS amount NUMERIC(10, 2) DEFAULT 0.00"))

            await session.commit()
            print("Database schema updated successfully.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
