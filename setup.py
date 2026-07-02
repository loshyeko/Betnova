from database import (
    create_users_table,
    create_matches_table,
    create_bet_tickets_table,
    create_transactions_table
)

create_users_table()
create_matches_table()
create_bet_tickets_table()
create_transactions_table()

print("Database setup completed successfully!")