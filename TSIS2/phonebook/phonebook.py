from connect import get_connection

conn = get_connection()
cur = conn.cursor()
def add_contact():
    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    cur.execute("""
        INSERT INTO contacts(name, email, birthday)
        VALUES (%s, %s, %s)
    """, (name, email, birthday))
    conn.commit()
    print("Contact added!")
def add_phone():
    name = input("Contact name: ")
    phone = input("Phone: ")
    type_ = input("Type (home/work/mobile): ")

    cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, type_))
    conn.commit()
    print("Phone added!")
def move_group():
    name = input("Contact name: ")
    group = input("Group name: ")

    cur.execute("CALL move_to_group(%s, %s)", (name, group))
    conn.commit()
    print("Moved to group!")
def search():
    q = input("Search: ")

    cur.execute("SELECT * FROM search_contacts(%s)", (q,))
    rows = cur.fetchall()
    for r in rows:
        print(r)
def menu():
    while True:
        print("""
        1. Add contact
        2. Add phone
        3. Move to group
        4. Search
        5. Exit
        """)
        choice = input("Choose: ")
        if choice == "1":
            add_contact()
        elif choice == "2":
            add_phone()
        elif choice == "3":
            move_group()
        elif choice == "4":
            search()
        elif choice == "5":
            break
menu()