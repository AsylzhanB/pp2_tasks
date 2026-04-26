import psycopg2
import psycopg2.extras
from Config import DB_CONFIG

def _connect():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    ddl = """
    CREATE TABLE IF NOT EXISTS players (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS game_sessions (
        id SERIAL PRIMARY KEY,
        player_id INTEGER REFERENCES players(id),
        score INTEGER NOT NULL,
        level_reached INTEGER NOT NULL,
        played_at TIMESTAMP DEFAULT NOW()
    );
    """
    try:
        conn = _connect()
        with conn:
            with conn.cursor() as cur:
                cur.execute(ddl)
        conn.close()
        return True
    except Exception as e:
        print(f"[DB] init_db error: {e}")
        return False

def get_or_create_player(username):
    try:
        conn = _connect()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO players (username)
                    VALUES (%s)
                    ON CONFLICT (username) DO NOTHING;
                """, (username,))
                cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
                row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"[DB] get_or_create_player error: {e}")
        return None

def save_session(player_id, score, level_reached):
    try:
        conn = _connect()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO game_sessions (player_id, score, level_reached)
                    VALUES (%s, %s, %s);
                """, (player_id, score, level_reached))
        conn.close()
        return True
    except Exception as e:
        print(f"[DB] save_session error: {e}")
        return False

def get_personal_best(player_id):
    try:
        conn = _connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COALESCE(MAX(score), 0)
                FROM game_sessions
                WHERE player_id = %s;
            """, (player_id,))
            row = cur.fetchone()
        conn.close()
        return row[0] if row else 0
    except Exception as e:
        print(f"[DB] get_personal_best error: {e}")
        return 0

def get_leaderboard(limit=10):
    try:
        conn = _connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    ROW_NUMBER() OVER (ORDER BY gs.score DESC) AS rank,
                    p.username,
                    gs.score,
                    gs.level_reached,
                    gs.played_at
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT %s;
            """, (limit,))
            rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        print(f"[DB] get_leaderboard error: {e}")
        return []