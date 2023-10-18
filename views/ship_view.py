import sqlite3
import json

def update_ship(id, ship_data):
    with sqlite3.connect("./shipping.db") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            UPDATE Ship
                SET
                    name = ?,
                    hauler_id = ?
            WHERE id = ?
            """,
            (ship_data['name'], ship_data['hauler_id'], id)
        )

        rows_affected = db_cursor.rowcount

    return True if rows_affected > 0 else False

def delete_ship(pk):
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        DELETE FROM Ship WHERE id = ?
        """, (pk,)
        )
        number_of_rows_deleted = db_cursor.rowcount

    return True if number_of_rows_deleted > 0 else False


def list_ships(url):
    # Open a connection to the database
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        if "_expand" in url["query_params"] and url["query_params"]["_expand"][0] == "hauler":
            # If the _expand parameter is present and is "hauler," join the Hauler table
            db_cursor.execute("""
            SELECT
                s.id,
                s.name,
                s.hauler_id,
                h.id haulerId,
                h.name haulerName,
                h.dock_id
            FROM Ship s
            JOIN Hauler h ON h.id = s.hauler_id
            """)
        else:
            # If there's no _expand parameter, simply add each ship to the list
            db_cursor.execute("""
            SELECT
                s.id,
                s.name,
                s.hauler_id
            FROM Ship s
            """)

        query_results = db_cursor.fetchall()

        # Initialize an empty list for ships
        ships = []

        for row in query_results:
            ship = {
                "id": row['id'],
                "name": row['name'],
                "hauler_id": row['hauler_id'],
            }
            if "_expand" in url["query_params"] and url["query_params"]["_expand"][0] == "hauler":
                hauler = {
                    "id": row['haulerId'],
                    "name": row['haulerName'],
                    "dock_id": row["dock_id"]
                }
                ship["hauler"] = hauler

            ships.append(ship)

        # Serialize the list of ships to a JSON-encoded string
        serialized_ships = json.dumps(ships)

    return serialized_ships

def retrieve_ship(pk, url):
    # Open a connection to the database
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        if "_expand" in url["query_params"] and url["query_params"]["_expand"][0] == "hauler":
            # Write the SQL query to get expanded ship information
            db_cursor.execute("""
            SELECT
                s.id,
                s.name,
                s.hauler_id,
                h.id haulerId,
                h.name haulerName,
                h.dock_id
            FROM Ship s
            JOIN Hauler h
                ON h.id = s.hauler_id
            WHERE s.id = ?
            """, (pk,))
        else:
            # Write the SQL query to get the information you want for a single ship
            db_cursor.execute("""
            SELECT
                s.id,
                s.name,
                s.hauler_id
            FROM Ship s
            WHERE s.id = ?
            """, (pk,))

        query_results = db_cursor.fetchone()

        # Serialize Python list to JSON encoded string
        if query_results:
            if "_expand" in url["query_params"] and url["query_params"]["_expand"][0] == "hauler":
                ship = {
                    "id": query_results['id'],
                    "name": query_results['name'],
                    "hauler_id": query_results['hauler_id'],
                    "hauler": {
                        "id": query_results['haulerId'],
                        "name": query_results['haulerName'],
                        "dock_id": query_results['dock_id']
                    }
                }
            else:
                ship = dict(query_results) 
            serialized_ship = json.dumps(ship)
        else:
            serialized_ship = json.dumps({})  # Return an empty JSON object if ship not found

    return serialized_ship

def insert_ship(ship_data):
    with sqlite3.connect("./shipping.db") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            INSERT INTO "Ship" VALUES (NULL, ?, ?)
            """,
            (ship_data['name'], ship_data['hauler_id'])
        )

        ship = db_cursor.fetchone()
        serialized_ship = json.dumps(ship)

    return serialized_ship
