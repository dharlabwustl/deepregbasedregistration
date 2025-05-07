import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
import re
# class BiomarkerDB:
class BiomarkerDB:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        # Step 1: Connect to MySQL server (not to a DB yet)
        self.server_conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password
        )
        self.server_cursor = self.server_conn.cursor()
        self.create_database_if_missing()

        # if not self.database_exists():
        #     print(f"Database '{self.database}' does not exist. Aborting connection.")
        #     self.initialized = False
        #     return
        # else:
        #     print(f"Database '{self.database}' exists. Proceeding...")

        # Step 2: Connect to the actual database
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.conn.cursor()
        self.initialized = True
        # self.create_table()
    def create_database_if_missing(self):
        """Create the database if it does not exist."""
        self.server_cursor.execute("SHOW DATABASES;")
        dbs = [row[0] for row in self.server_cursor.fetchall()]
        if self.database not in dbs:
            self.server_cursor.execute(f"CREATE DATABASE `{self.database}`;")
            print(f"Database '{self.database}' created.")
        else:
            print(f"Database '{self.database}' already exists.")

        self.server_cursor.close()
        self.server_conn.close()

    def database_exists(self):
        self.server_cursor.execute("SHOW DATABASES;")
        dbs = [row[0] for row in self.server_cursor.fetchall()]
        self.server_cursor.close()
        self.server_conn.close()
        return self.database in dbs
    def delete_database(self, db_name=None):
        confirm = input("Are you sure you want to delete the database? Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            print("Database deletion cancelled.")
            return
        """Delete the specified database. If none provided, deletes the current database."""
        try:
            target_db = db_name or self.database
            conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password)
            cursor = conn.cursor()
            cursor.execute(f"DROP DATABASE IF EXISTS `{target_db}`;")
            conn.commit()
            print(f"Database '{target_db}' deleted successfully.")
            cursor.close()
            conn.close()
            if target_db == self.database:
                self.initialized = False
        except Exception as e:
            print(f"Failed to delete database '{target_db}': {e}")
    def delete_table(self, table_name):
        """Delete a table from the current database."""
        if not self.initialized:
            print("Database not initialized.")
            return

        try:
            self.cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")
            self.conn.commit()
            print(f"Table '{table_name}' deleted successfully.")
        except Exception as e:
            print(f"Failed to delete table '{table_name}': {e}")
    # def create_table(self):
    #     create_query = f"""
    #     CREATE TABLE IF NOT EXISTS ALL_BIOMARKERS (
    #         id INT AUTO_INCREMENT PRIMARY KEY,
    #         session_id VARCHAR(255) UNIQUE
    #     );
    #     """
    #     self.cursor.execute(create_query)
    #     self.conn.commit()
        # print("Table 'ALL_BIOMARKERS' is ready.")
    def get_row_by_id_across_tables(self, id_value, include_fields=None, exclude_fields=None):
        """Search for the ID in all tables and return row with selected/excluded fields."""
        if not self.initialized:
            print("Database not initialized.")
            return None

        try:
            self.cursor.execute("SHOW TABLES;")
            tables = [row[0] for row in self.cursor.fetchall()]

            for table in tables:
                self.cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE 'ID';")
                if not self.cursor.fetchone():
                    continue

                self.cursor.execute(f"SHOW COLUMNS FROM `{table}`;")
                all_columns = [row[0] for row in self.cursor.fetchall()]

                if include_fields:
                    selected_columns = [col for col in include_fields if col in all_columns]
                elif exclude_fields:
                    selected_columns = [col for col in all_columns if col not in exclude_fields]
                else:
                    selected_columns = all_columns

                if not selected_columns:
                    continue

                select_clause = ", ".join([f"`{col}`" for col in selected_columns])
                query = f"SELECT {select_clause} FROM `{table}` WHERE `ID` = %s;"
                self.cursor.execute(query, (id_value,))
                row = self.cursor.fetchone()

                if row:
                    print(f"Found in table '{table}': {row}")
                    return {"table": table, "columns": selected_columns, "row": row}

            print(f"ID '{id_value}' not found in any table.")
            return None

        except Exception as e:
            print(f"Error while searching for ID across tables: {e}")
            return None


    def insert_session(self, session_id):
        if not self.initialized:
            print("Database not initialized. Cannot insert.")
            return
        try:
            self.cursor.execute(
                "INSERT INTO ALL_BIOMARKERS (session_id) VALUES (%s);", (session_id,)
            )
            self.conn.commit()
            print(f"Inserted session_id: {session_id}")
        except mysql.connector.errors.IntegrityError:
            print(f"Session ID '{session_id}' already exists. Skipping insert.")

    def get_serial_number(self, session_id):
        if not self.initialized:
            return None
        self.cursor.execute(
            "SELECT id FROM ALL_BIOMARKERS WHERE session_id = %s;", (session_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def ensure_column_exists(self, column_name, column_type="VARCHAR(255)"):
        if not self.initialized:
            return
        self.cursor.execute(
            "SHOW COLUMNS FROM ALL_BIOMARKERS LIKE %s;", (column_name,)
        )
        if not self.cursor.fetchone():
            self.cursor.execute(
                f"ALTER TABLE ALL_BIOMARKERS ADD COLUMN {column_name} {column_type};"
            )
            self.conn.commit()
            print(f"Added new column: {column_name}")
        else:
            print(f"Column '{column_name}' already exists.")

    def update_column_value(self, session_id, column_name, value):
        if not self.initialized:
            return
        self.cursor.execute(
            f"UPDATE ALL_BIOMARKERS SET {column_name} = %s WHERE session_id = %s;",
            (value, session_id)
        )
        self.conn.commit()
        print(f"Updated {column_name} = '{value}' for session_id '{session_id}'.")

    def close(self):
        if not self.initialized:
            return
        self.cursor.close()
        self.conn.close()
        print("Connection closed.")

    def create_table_from_csv(self, csv_file_path, table_name, unique_not_null_field=None):
        """Create a new table from a CSV file and insert data using SQLAlchemy."""
        if not self.initialized:
            print("Database not initialized. Cannot create table from CSV.")
            return

        try:
            df = pd.read_csv(csv_file_path)
            print(f"CSV '{csv_file_path}' loaded successfully.")

            # Use SQLAlchemy to create and insert table
            conn_str = f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}/{self.database}"
            engine = create_engine(conn_str)
            df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
            print(f"Table '{table_name}' created and {len(df)} rows inserted using SQLAlchemy.")

            # Apply UNIQUE NOT NULL constraint if requested
            if unique_not_null_field and unique_not_null_field in df.columns:
                alter_query = f"""
                ALTER TABLE `{table_name}` 
                MODIFY `{unique_not_null_field}` VARCHAR(255) UNIQUE NOT NULL;
                """
                self.cursor.execute(alter_query)
                self.conn.commit()
                print(f"Field '{unique_not_null_field}' set as UNIQUE NOT NULL in '{table_name}'.")

        except Exception as e:
            print(f"Failed to create table from CSV: {e}")
    def import_csv_with_alchemy(self, csv_file_path, table_name):
        """Automatically create table from CSV and insert using pandas + SQLAlchemy."""
        if not self.initialized:
            print("Database not initialized. Cannot import CSV with SQLAlchemy.")
            return

        try:
            df = pd.read_csv(csv_file_path)
            print(f"CSV loaded: {csv_file_path}, shape={df.shape}")
        except Exception as e:
            print(f"Failed to read CSV: {e}")
            return

        try:
            conn_str = f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}/{self.database}"
            engine = create_engine(conn_str)
            df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
            print(f"Imported {len(df)} rows into '{table_name}' using SQLAlchemy.")
        except Exception as e:
            print(f"SQLAlchemy import failed: {e}")

    def import_csv_without_alchemy(self, csv_file_path, table_name):
        """Create and populate table from CSV manually (no SQLAlchemy)."""
        if not self.initialized:
            print("Database not initialized. Cannot import CSV without SQLAlchemy.")
            return

        try:
            df = pd.read_csv(csv_file_path)
            print(f"CSV loaded: {csv_file_path}, shape={df.shape}")
        except Exception as e:
            print(f"Failed to read CSV: {e}")
            return

        try:
            # Build table schema as VARCHAR(255)
            columns_sql = ", ".join([f"`{col}` VARCHAR(255)" for col in df.columns])
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                {columns_sql}
            );
            """
            self.cursor.execute(create_sql)
            self.conn.commit()
            print(f"Table '{table_name}' created manually.")

            # Insert each row
            for _, row in df.iterrows():
                placeholders = ", ".join(["%s"] * len(df.columns))
                insert_query = f"""
                INSERT INTO {table_name} ({', '.join(df.columns)})
                VALUES ({placeholders});
                """
                self.cursor.execute(insert_query, tuple(row))

            self.conn.commit()
            print(f"Inserted {len(df)} rows into '{table_name}' manually.")
        except Exception as e:
            print(f"Manual import failed: {e}")
    def export_table_to_csv(self, table_name, output_csv_path):
        """Export a database table to a CSV file using pandas."""
        if not self.initialized:
            print("Database not initialized. Cannot export table.")
            return

        try:
            # Use pandas to load table into DataFrame
            query = f"SELECT * FROM {table_name};"
            df = pd.read_sql(query, self.conn)

            # Write to CSV
            df.to_csv(output_csv_path, index=False)
            print(f"Exported table '{table_name}' to CSV: {output_csv_path}")
        except Exception as e:
            print(f"Failed to export table '{table_name}': {e}")
    def export_selected_fields_to_csv(self, table_name, field_list, output_csv_path):
        """Export selected fields from a table to a CSV file."""
        if not self.initialized:
            print("Database not initialized. Cannot export fields.")
            return

        if not field_list:
            print("Field list is empty. Nothing to export.")
            return

        try:
            # Join the fields for the SELECT query
            selected_fields = ", ".join([f"`{field}`" for field in field_list])
            query = f"SELECT {selected_fields} FROM {table_name};"

            # Execute query and export with pandas
            df = pd.read_sql(query, self.conn)
            df.to_csv(output_csv_path, index=False)
            print(f"Exported selected fields to CSV: {output_csv_path}")
        except Exception as e:
            print(f"Failed to export selected fields: {e}")
    def export_unselected_fields_to_csv(self, table_name, excluded_fields, output_csv_path):
        """Export all fields except those in excluded_fields from a table to a CSV."""
        if not self.initialized:
            print("Database not initialized. Cannot export unselected fields.")
            return

        try:
            # Step 1: Get all columns from the table
            self.cursor.execute(f"SHOW COLUMNS FROM {table_name};")
            all_columns = [row[0] for row in self.cursor.fetchall()]

            # Step 2: Compute fields to include
            included_fields = [col for col in all_columns if col not in excluded_fields]

            if not included_fields:
                print("No fields left after exclusion. Export aborted.")
                return

            # Step 3: Build SELECT query
            selected_fields = ", ".join([f"`{field}`" for field in included_fields])
            query = f"SELECT {selected_fields} FROM {table_name};"

            # Step 4: Execute and write to CSV
            df = pd.read_sql(query, self.conn)
            df.to_csv(output_csv_path, index=False)
            print(f"Exported non-excluded fields to CSV: {output_csv_path}")
        except Exception as e:
            print(f"Failed to export non-selected fields: {e}")
    def make_column_unique(self, table_name, column_name):
        """Make a column UNIQUE in the given table, using key length if needed."""
        if not self.initialized:
            print("Database not initialized.")
            return

        try:
            # Check if it's already UNIQUE
            self.cursor.execute(f"""
                SELECT COUNT(*) FROM information_schema.statistics
                WHERE table_schema = %s AND table_name = %s AND column_name = %s AND non_unique = 0;
            """, (self.database, table_name, column_name))
            is_unique = self.cursor.fetchone()[0] > 0

            if is_unique:
                print(f"Column '{column_name}' is already UNIQUE in '{table_name}'.")
            else:
                # Add unique constraint with prefix length 255
                self.cursor.execute(f"""
                    ALTER TABLE `{table_name}` ADD UNIQUE (`{column_name}`(255));
                """)
                self.conn.commit()
                print(f"Column '{column_name}' is now UNIQUE in '{table_name}' (with key length 255).")
        except Exception as e:
            print(f"Failed to make column '{column_name}' unique: {e}")

    def simple_row_by_row_merge(self, csv_file_path, table_name, id_column_in_csv="ID"):
        """Simple, reliable: First ensure all columns exist, then update each row."""
        if not self.initialized:
            print("Database not initialized. Cannot merge.")
            return

        try:
            import pandas as pd
            import numpy as np

            # Load CSV
            df = pd.read_csv(csv_file_path)
            print(f"Loaded CSV with shape {df.shape}")

            # Basic cleanup
            if '<html>' in df.columns:
                df = df.drop(columns=['<html>'])
                print("Dropped column '<html>'.")

            df.columns = df.columns.astype(str).str.strip()
            df = df.loc[:, (df.columns != "") & (df.columns.str.lower() != "nan")]

            # Rename ID column if needed
            if id_column_in_csv != "ID":
                if id_column_in_csv in df.columns:
                    df = df.rename(columns={id_column_in_csv: "ID"})
                    print(f"Renamed '{id_column_in_csv}' to 'ID'.")
                else:
                    raise Exception(f"ID column '{id_column_in_csv}' not found.")

            if 'ID' not in df.columns:
                raise Exception("Error: 'ID' column missing after cleanup.")

            # ✅ Step 1: Ensure all CSV columns exist in table first
            self.cursor.execute(f"SHOW COLUMNS FROM `{table_name}`;")
            db_columns = [row[0] for row in self.cursor.fetchall()]
            db_columns_set = set(db_columns)

            for col in df.columns:
                if col not in db_columns_set:
                    self.cursor.execute(f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` VARCHAR(255);")
                    print(f"Added missing column to table: {col}")
            self.conn.commit()

            # ✅ Step 2: Now safely row-by-row insert/update
            for idx, row in df.iterrows():
                id_value = row['ID']

                # Check if ID already exists
                self.cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` WHERE `ID` = %s;", (id_value,))
                exists = self.cursor.fetchone()[0] > 0

                if not exists:
                    # Insert just the ID
                    self.cursor.execute(f"INSERT INTO `{table_name}` (`ID`) VALUES (%s);", (id_value,))
                    print(f"Inserted new ID: {id_value}")

                for col_name, col_value in row.items():
                    if col_name == "ID":
                        continue  # Skip ID field

                    if pd.isna(col_value):
                        continue  # Skip NaN values

                    # Now safe to UPDATE
                    update_query = f"""
                    UPDATE `{table_name}`
                    SET `{col_name}` = %s
                    WHERE `ID` = %s;
                    """
                    self.cursor.execute(update_query, (str(col_value), id_value))

                self.conn.commit()

            # print(f"✅ Successfully merged {len(df)} rows into '{table_name}' (safe row-by-row method).")
            print(f"Successfully merged {len(df)} rows into '{table_name}' (safe row-by-row method).")


        except Exception as e:
            print("Simple merge operation failed:")
            print(e)
            pass

    def upsert_single_field_by_id(self, table_name, id_value, column_name, new_value):
        """Upsert a single field into the table by ID. Insert new or update existing."""
        if not self.initialized:
            print("Database not initialized. Cannot upsert single field.")
            return

        try:
            # Step 1: Check if the column exists
            self.cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE %s;", (column_name,))
            column_exists = self.cursor.fetchone()
            if not column_exists:
                # If column doesn't exist, add it
                self.cursor.execute(f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` VARCHAR(255);")
                self.conn.commit()
                print(f"Added new column '{column_name}' to '{table_name}'.")

            # Step 2: Prepare UPSERT query
            insert_query = f"""
            INSERT INTO `{table_name}` (`ID`, `{column_name}`)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE `{column_name}` = VALUES(`{column_name}`);
            """

            # Step 3: Execute
            self.cursor.execute(insert_query, (id_value, new_value))
            self.conn.commit()

            print(f"✅ Upserted ID='{id_value}' and set {column_name}='{new_value}' in '{table_name}'.")

        except Exception as e:
            print("Upsert single field operation failed:")
            print(e)

# ---------------------- MAIN USAGE ---------------------- #
#
# if __name__ == "__main__":
#     db = BiomarkerDB(
#         host="34.58.59.235",             # Replace with your instance IP
#         user="root",                     # Replace if using a different user
#         password="your-root-password",   # Replace with your actual password
#         database="RESULTS"
#     )
#
#     if db.initialized:
#         session_id = "SESSION_ABC123"
#         db.insert_session(session_id)
#
#         serial = db.get_serial_number(session_id)
#         print(f"Serial number for '{session_id}': {serial}")
#
#         db.ensure_column_exists("biomarker_value")
#         db.update_column_value(session_id, "biomarker_value", "Test_Value_123")
#
#         db.close()
