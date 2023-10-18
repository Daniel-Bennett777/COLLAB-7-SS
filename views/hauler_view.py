import sqlite3
import json

def update_hauler(id, hauler_data):
    with sqlite3.connect("./shipping.db") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            UPDATE Hauler
                SET
                    name = ?,
                    dock_id = ?
            WHERE id = ?
            """,
            (hauler_data['name'], hauler_data['dock_id'], id)
        )

        rows_affected = db_cursor.rowcount

    return True if rows_affected > 0 else False


def delete_hauler(pk):
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        DELETE FROM Hauler WHERE id = ?
        """, (pk,)
        )
        number_of_rows_deleted = db_cursor.rowcount

    return True if number_of_rows_deleted > 0 else False


def list_haulers(url):
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        haulers = []  # Initialize a list to hold hauler information with embedded ships

        if "_embed" in url["query_params"] and url["query_params"]["_embed"] == ["ships"]:
            # If _embed is set to "ships," join the Ship table to get haulers and their ships
            db_cursor.execute("""
            SELECT
                h.id hauler_id,
                h.name hauler_name,
                h.dock_id hauler_dock_id,
                s.id ship_id,
                s.name ship_name
            FROM Hauler h
            LEFT JOIN Ship s ON h.id = s.hauler_id
            """)

            query_results = db_cursor.fetchall()

            # Initialize a dictionary to store hauler information with ships
            haulers_data = {}

            for row in query_results:
                hauler_id = row['hauler_id']

                if hauler_id not in haulers_data:
                    # Initialize the hauler's information
                    haulers_data[hauler_id] = {
                        "id": hauler_id,
                        "name": row['hauler_name'],
                        "dock_id": row['hauler_dock_id'],
                        "ships": []  # Initialize an empty list for the hauler's ships
                    }

                if row['ship_id']:
                    ship = {
                        "id": row['ship_id'],
                        "name": row['ship_name']
                    }
                    haulers_data[hauler_id]["ships"].append(ship)

            # Extract hauler data from the dictionary and convert it to a list
            haulers = list(haulers_data.values())
        else:
            # If not embedding, select only hauler information
            db_cursor.execute("""
            SELECT
                h.id hauler_id,
                h.name hauler_name,
                h.dock_id hauler_dock_id
            FROM Hauler h
            """)

            query_results = db_cursor.fetchall()

            for row in query_results:
                hauler = {
                    "id": row['hauler_id'],
                    "name": row['hauler_name'],
                    "dock_id": row['hauler_dock_id'],
                }
                haulers.append(hauler)

        serialized_haulers = json.dumps(haulers)
        return serialized_haulers

def retrieve_hauler(pk):
    # Open a connection to the database
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        SELECT
            h.id,
            h.name,
            h.dock_id
        FROM Hauler h
        WHERE h.id = ?
        """, (pk,))
        query_results = db_cursor.fetchone()

        # Serialize Python list to JSON encoded string
        serialized_hauler = json.dumps(dict(query_results))

    return serialized_hauler

def insert_hauler(hauler_data):
    with sqlite3.connect("./shipping.db") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            INSERT INTO Hauler VALUES (NULL, ?, ?)
            """,
            (hauler_data['name'], hauler_data['dock_id'])
        )

        hauler = db_cursor.fetchone()
        serialized_hauler = json.dumps(hauler)

    return serialized_hauler
