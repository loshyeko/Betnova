import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
from datetime import datetime
from market_engine import ( generate_draw_no_bet, generate_match_result, generate_correct_score, generate_double_chance, generate_btts, generate_over_under, generate_odd_even, generate_first_half, generate_second_half)
DB_NAME = "betnova"
DB_USER = "betnova_user"
DB_PASSWORD = "Dean234@devlin2025"
DB_HOST = "localhost"
DB_PORT = "5432"


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def create_users_table():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id SERIAL PRIMARY KEY,

            country VARCHAR(50) NOT NULL,

            phone VARCHAR(20) UNIQUE NOT NULL,

            password VARCHAR(255) NOT NULL,

            balance DECIMAL(12,2) DEFAULT 0,

            status VARCHAR(20) DEFAULT 'Active',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conn.commit()

    cur.close()
    conn.close()

def create_matches_table():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS matches (

            id SERIAL PRIMARY KEY,

            league VARCHAR(100) NOT NULL,

            home_team VARCHAR(100) NOT NULL,

            away_team VARCHAR(100) NOT NULL,

            match_date TIMESTAMP NOT NULL,

            home_odds DECIMAL(6,2) NOT NULL,

            draw_odds DECIMAL(6,2) NOT NULL,

            away_odds DECIMAL(6,2) NOT NULL,

            status VARCHAR(20) DEFAULT 'Upcoming',

            result VARCHAR(20),

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conn.commit()

    cur.close()
    conn.close()

def create_bet_tickets_table():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bet_tickets (

            id SERIAL PRIMARY KEY,

            phone VARCHAR(20) NOT NULL,

            total_stake DECIMAL(12,2) NOT NULL,

            total_odds DECIMAL(10,2) NOT NULL,

            potential_win DECIMAL(12,2) NOT NULL,

            status VARCHAR(20) DEFAULT 'Pending',

            placed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conn.commit()

    cur.close()
    conn.close() 

def create_transactions_table():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (

            id SERIAL PRIMARY KEY,

            phone VARCHAR(20) NOT NULL,

            transaction_type VARCHAR(30) NOT NULL,

            amount DECIMAL(12,2) NOT NULL,

            balance_after DECIMAL(12,2) NOT NULL,

            description TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conn.commit()

    cur.close()
    conn.close() 

def save_transaction(phone, transaction_type, amount, balance_after, description):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO transactions
        (phone, transaction_type, amount, balance_after, description)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        phone,
        transaction_type,
        amount,
        balance_after,
        description
    ))

    conn.commit()

    cur.close()
    conn.close()

def get_transactions(phone):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT transaction_type,
               amount,
               balance_after,
               description,
               created_at
        FROM transactions
        WHERE phone=%s
        ORDER BY created_at DESC
    """, (phone,))

    transactions = cur.fetchall()

    cur.close()
    conn.close()

    return transactions 

def create_user(country, language, full_phone, password):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO users (country, language, phone, password)
            VALUES (%s, %s, %s, %s)
        """, (country, language, full_phone, password))

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        return False

    finally:
        cur.close()
        conn.close()


def get_user(full_phone):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT country, language, phone, password, balance
        FROM users
        WHERE phone=%s
    """, (full_phone,))

    user = cur.fetchone()

    cur.close()
    conn.close()

    return user  

def add_match(
    league,
    home_team,
    away_team,
    match_date,
    home_odds,
    draw_odds,
    away_odds
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO matches
        (
            league,
            home_team,
            away_team,
            match_date,
            home_odds,
            draw_odds,
            away_odds
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        league,
        home_team,
        away_team,
        match_date,
        home_odds,
        draw_odds,
        away_odds
    ))

    conn.commit()

    cur.close()
    conn.close()


def get_all_matches():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM matches
        ORDER BY kickoff ASC
    """)

    matches = cur.fetchall()

    cur.close()
    conn.close()

    return matches

def get_match(match_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM matches
        WHERE id=%s
    """, (match_id,))

    match = cur.fetchone()

    cur.close()
    conn.close()

    return match  

def get_matches():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            league,
            home_team,
            away_team,
            kickoff,
            home_odds,
            draw_odds,
            away_odds
        FROM matches
        ORDER BY kickoff;
    """)

    matches = cur.fetchall()

    cur.close()
    conn.close()

    return matches


def get_markets(match_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            mt.name,
            ms.selection_name,
            ms.odds
        FROM market_selections ms
        JOIN market_types mt
            ON ms.market_type_id = mt.id
        WHERE ms.match_id = %s
        ORDER BY mt.display_order, ms.display_order
    """, (match_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    grouped = {}

    for market_name, selection, odds in rows:
        grouped.setdefault(market_name, []).append({
            "name": selection,
            "odds": float(odds)
        })

    return grouped

def save_bet(phone, match_id, market, odds, stake, potential_win):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO bets
        (phone, match_id, market, odds, stake, potential_win, status, placed_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        phone,
        match_id,
        market,
        odds,
        stake,
        potential_win,
        "Pending",
        datetime.now()
    ))

    conn.commit()
    cur.close()
    conn.close()

def update_balance(phone, amount):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET balance = balance - %s
        WHERE phone = %s
    """, (amount, phone))

    conn.commit()
    cur.close()
    conn.close()

def get_balance(phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT balance FROM users WHERE phone = %s",
        (phone,)
    )

    result = cur.fetchone()

    cur.close()
    conn.close()

    if result:
        return float(result[0])

    return 0.0 

def save_deposit(
    phone,
    reference,
    order_tracking_id,
    amount,
    payment_status
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO deposits
        (
            phone,
            reference,
            order_tracking_id,
            amount,
            payment_status
        )
        VALUES (%s,%s,%s,%s,%s)
        ON CONFLICT (order_tracking_id)
        DO NOTHING
    """, (
        phone,
        reference,
        order_tracking_id,
        amount,
        payment_status
    ))

    conn.commit()
    cur.close()
    conn.close()

def deposit_exists(order_tracking_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT 1 FROM deposits WHERE order_tracking_id=%s",
        (order_tracking_id,)
    )

    exists = cur.fetchone() is not None

    cur.close()
    conn.close()

    return exists

def generate_match_markets(match_id):
    conn = get_connection()
    cur = conn.cursor()

    # Get match odds
    cur.execute("""
        SELECT home_odds, draw_odds, away_odds
        FROM matches
        WHERE id = %s
    """, (match_id,))
    match = cur.fetchone()

    if not match:
        cur.close()
        conn.close()
        return

    home_odds, draw_odds, away_odds = map(float, match)

    # Remove old markets
    cur.execute(
        "DELETE FROM match_markets WHERE match_id = %s",
        (match_id,)
    )

    markets = []

    markets.extend(generate_match_result(home_odds, draw_odds, away_odds))
    markets.extend(generate_double_chance(home_odds, draw_odds, away_odds))
    markets.extend(generate_draw_no_bet(home_odds, away_odds))
    markets.extend(generate_correct_score
    (
        home_odds,
        draw_odds,
        away_odds
    ))
    markets.extend(generate_btts(home_odds, away_odds))
    markets.extend(generate_over_under())
    markets.extend(generate_odd_even())
    markets.extend(generate_first_half(
        home_odds,
        draw_odds,
        away_odds
    ))
    markets.extend(generate_second_half(
        home_odds,
        draw_odds,
        away_odds
    ))

    cur.executemany("""
        INSERT INTO match_markets
        (match_id, market_name, selection, odds)
        VALUES (%s, %s, %s, %s)
    """, [(match_id, m, s, o) for m, s, o in markets])

    conn.commit()
    cur.close()
    conn.close()
