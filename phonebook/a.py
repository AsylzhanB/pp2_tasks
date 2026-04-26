import psycopg2
from psycopg2 import sql, OperationalError
import sys

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "phonebook_db",
    "user":     "postgres",
    "password": "your_password",
}

def get_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except OperationalError as e:
        print(f"\n[ERROR] Could not connect to PostgreSQL: {e}")
        sys.exit(1)

def initialize_db(conn):
    """Create the contacts table if it does not exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id          SERIAL PRIMARY KEY,
                first_name  VARCHAR(100) NOT NULL,
                last_name   VARCHAR(100) NOT NULL,
                phone       VARCHAR(30)  NOT NULL UNIQUE,
                email       VARCHAR(150),
                group_name  VARCHAR(50)  DEFAULT 'General',
                created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
            );
        """)
    conn.commit()
    print("[OK] Database ready.")
def add_contact(conn):
    """Insert a new contact."""
    print("\n--- Add Contact ---")
    first = input("First name : ").strip()
    last  = input("Last name  : ").strip()
    phone = input("Phone      : ").strip()
    email = input("Email      : ").strip() or None
    group = input("Group      : ").strip() or "General"
    if not first or not last or not phone:
        print("[ERROR] First name, last name, and phone are required.")
        return
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO contacts (first_name, last_name, phone, email, group_name)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (first, last, phone, email, group),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        print(f"[OK] Contact added with ID {new_id}.")
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print("[ERROR] A contact with that phone number already exists.")

def list_contacts(conn):
    """Display all contacts in a formatted table."""
    print("\n--- All Contacts ---")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, first_name, last_name, phone, email, group_name
            FROM contacts
            ORDER BY last_name, first_name;
        """)
        rows = cur.fetchall()
    if not rows:
        print("  (no contacts found)")
        return
    header = f"{'ID':<5} {'Name':<25} {'Phone':<18} {'Email':<28} {'Group'}"
    print(header)
    print("-" * len(header))
    for id_, fn, ln, phone, email, group in rows:
        name  = f"{fn} {ln}"
        email = email or ""
        print(f"{id_:<5} {name:<25} {phone:<18} {email:<28} {group}")


def search_contacts(conn):
    """Search contacts by name, phone, or email."""
    print("\n--- Search Contacts ---")
    term = input("Search term: ").strip()
    if not term:
        print("[ERROR] Enter a search term.")
        return
    pattern = f"%{term}%"
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, first_name, last_name, phone, email, group_name
            FROM contacts
            WHERE first_name ILIKE %s
               OR last_name  ILIKE %s
               OR phone      ILIKE %s
               OR email      ILIKE %s
            ORDER BY last_name, first_name;
        """, (pattern, pattern, pattern, pattern))
        rows = cur.fetchall()
    if not rows:
        print("  (no matches found)")
        return
    for id_, fn, ln, phone, email, group in rows:
        print(f"  [{id_}] {fn} {ln} | {phone} | {email or '—'} | {group}")


def update_contact(conn):
    """Update an existing contact's details."""
    print("\n--- Update Contact ---")
    try:
        contact_id = int(input("Contact ID to update: ").strip())
    except ValueError:
        print("[ERROR] Invalid ID.")
        return
    with conn.cursor() as cur:
        cur.execute(
            "SELECT first_name, last_name, phone, email, group_name FROM contacts WHERE id = %s;",
            (contact_id,),
        )
        row = cur.fetchone()
    if not row:
        print("[ERROR] Contact not found.")
        return
    fn, ln, phone, email, group = row
    print(f"  Editing: {fn} {ln} | {phone} | {email or '—'} | {group}")
    print("  (press Enter to keep current value)")
    new_first = input(f"  First name [{fn}]: ").strip() or fn
    new_last  = input(f"  Last name  [{ln}]: ").strip() or ln
    new_phone = input(f"  Phone      [{phone}]: ").strip() or phone
    new_email = input(f"  Email      [{email or ''}]: ").strip() or email
    new_group = input(f"  Group      [{group}]: ").strip() or group

    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE contacts
                SET first_name = %s, last_name = %s, phone = %s,
                    email = %s, group_name = %s
                WHERE id = %s;
            """, (new_first, new_last, new_phone, new_email or None, new_group, contact_id))
        conn.commit()
        print("[OK] Contact updated.")
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print("[ERROR] That phone number is already used by another contact.")


def delete_contact(conn):
    """Delete a contact by ID."""
    print("\n--- Delete Contact ---")
    try:
        contact_id = int(input("Contact ID to delete: ").strip())
    except ValueError:
        print("[ERROR] Invalid ID.")
        return

    with conn.cursor() as cur:
        cur.execute("SELECT first_name, last_name FROM contacts WHERE id = %s;", (contact_id,))
        row = cur.fetchone()

    if not row:
        print("[ERROR] Contact not found.")
        return

    confirm = input(f"  Delete '{row[0]} {row[1]}'? (y/N): ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return

    with conn.cursor() as cur:
        cur.execute("DELETE FROM contacts WHERE id = %s;", (contact_id,))
    conn.commit()
    print("[OK] Contact deleted.")


def list_groups(conn):
    """Show contacts organised by group."""
    print("\n--- Contacts by Group ---")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT group_name, COUNT(*) AS total
            FROM contacts
            GROUP BY group_name
            ORDER BY group_name;
        """)
        groups = cur.fetchall()

    if not groups:
        print("  (no contacts found)")
        return

    for group, total in groups:
        print(f"\n  [{group}]  ({total} contact{'s' if total != 1 else ''})")
        with conn.cursor() as cur:
            cur.execute("""
                SELECT first_name, last_name, phone
                FROM contacts
                WHERE group_name = %s
                ORDER BY last_name;
            """, (group,))
            for fn, ln, phone in cur.fetchall():
                print(f"    {fn} {ln:<22} {phone}")



MENU = """
╔══════════════════════════════╗
║           PHONEBOOK          ║
╠══════════════════════════════╣
║  1. List all contacts        ║
║  2. Add contact              ║
║  3. Search contacts          ║
║  4. Update contact           ║
║  5. Delete contact           ║
║  6. Contacts by group        ║
║  0. Exit                     ║
╚══════════════════════════════╝
"""

ACTIONS = {
    "1": list_contacts,
    "2": add_contact,
    "3": search_contacts,
    "4": update_contact,
    "5": delete_contact,
    "6": list_groups,
}


def main():
    conn = get_connection()
    initialize_db(conn)

    try:
        while True:
            print(MENU)
            choice = input("Choice: ").strip()
            if choice == "0":
                print("Goodbye!")
                break
            action = ACTIONS.get(choice)
            if action:
                action(conn)
            else:
                print("[ERROR] Invalid choice. Enter 0–6.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()