#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------ Environment (inline or use .env) --------------------------
import os

import os
import pandas as pd
from dateutil import parser as dtparser
# ------------------ Imports ---------------------------------------------------
import argparse
import pandas as pd
from sqlalchemy import create_engine, text
from dateutil import parser as dtparser
import re
import inspect
import traceback
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

LOG_FILE = "railway_db_errors.log"
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import inspect
from datetime import datetime
import traceback

LOG_FILE = "railway_db_errors.log"
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import inspect
from datetime import datetime
import traceback

LOG_FILE = "railway_db_errors.log"
def build_engine():
    host = os.environ["MYSQL_HOST"]
    port = os.environ.get("MYSQL_PORT", "3306")
    db   = os.environ["MYSQL_DB"]
    user = os.environ["MYSQL_USER"]
    pwd  = os.environ["MYSQL_PASSWORD"]
    url = f"mysql+mysqlconnector://{user}:{pwd}@{host}:{port}/{db}?charset=utf8mb4"
    return create_engine(url, pool_pre_ping=True)
engine = build_engine()
def download_table_as_csv(engine, table_name, csv_path):
    """
    Download a MySQL table as a CSV file.
    """
    func_name = inspect.currentframe().f_code.co_name

    try:
        query = text(f"SELECT * FROM `{table_name}`")
        print("I AM HERE ATUL")
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)

        df.to_csv(csv_path, index=False)
        return {
            "status": "success",
            "table": table_name,
            "rows": len(df),
            "csv": csv_path
        }

    except SQLAlchemyError as e:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = (
            f"[{ts}] Function: {func_name}\n"
            f"Table: {table_name}\n"
            f"CSV: {csv_path}\n"
            f"Error: {e}\n"
            f"Traceback:\n{traceback.format_exc()}\n"
            f"{'-'*80}\n"
        )
        with open(LOG_FILE, "a") as f:
            f.write(msg)
        raise
def download_as_csv(table_name,csv_path):
    # engine = build_engine()
    res = download_table_as_csv(
        engine,
        table_name=table_name,
        csv_path=csv_path
    )

    print(res)
def make_column_not_null_and_unique(engine, table_name, column_name, col_type="VARCHAR(64)"):
    """
    Make a column NOT NULL and UNIQUE in MySQL.
    """
    func_name = inspect.currentframe().f_code.co_name

    try:
        with engine.begin() as conn:
            # Step 1: enforce NOT NULL
            conn.execute(text(f"""
                ALTER TABLE `{table_name}`
                MODIFY `{column_name}` {col_type} NOT NULL
            """))

            # Step 2: add UNIQUE constraint
            conn.execute(text(f"""
                ALTER TABLE `{table_name}`
                ADD UNIQUE KEY `uniq_{column_name}` (`{column_name}`)
            """))

        return True

    except SQLAlchemyError as e:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = (
            f"[{ts}] Function: {func_name}\n"
            f"Table: {table_name}\n"
            f"Column: {column_name}\n"
            f"Error: {e}\n"
            f"Traceback:\n{traceback.format_exc()}\n"
            f"{'-'*80}\n"
        )
        with open(LOG_FILE, "a") as f:
            f.write(msg)
        raise

def _safe_ident(name: str) -> str:
    """
    MySQL identifier safety: only letters/numbers/underscore, cannot start with number.
    Also runs through clean_col() from your base script. :contentReference[oaicite:1]{index=1}
    """
    name = clean_col(str(name))
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise ValueError(f"Unsafe identifier: {name!r}")
    return name

def update_table_value_by_identifier(
    engine,
    table_name: str,
    identifier_col: str,
    identifier_val,
    target_col: str,
    target_val,
    insert_if_missing: bool = True,
    create_target_col_if_missing: bool = True,
    target_col_type: str = "VARCHAR(255) NULL",
):
    """
    Update one column value for the row identified by identifier_col=identifier_val.
    - Raises ValueError if table does not exist.
    - Raises ValueError if identifier column does not exist.
    - If target column does not exist and create_target_col_if_missing=True, creates it.
    - If no row exists and insert_if_missing=True, inserts a new row.
    """
    func_name = inspect.currentframe().f_code.co_name

    try:
        db = os.environ["MYSQL_DB"]

        table = _safe_ident(table_name)
        id_col = _safe_ident(identifier_col)
        tgt_col = _safe_ident(target_col)

        with engine.begin() as conn:
            # 1) Table exists?
            table_exists = conn.execute(
                text("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = :db AND table_name = :t
                """),
                {"db": db, "t": table},
            ).scalar()

            if not table_exists:
                raise ValueError(f"Table does not exist: `{table}` (schema `{db}`)")

            # 2) Columns in table
            cols = conn.execute(
                text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = :db AND table_name = :t
                """),
                {"db": db, "t": table},
            ).fetchall()
            colset = {r[0].lower() for r in cols}

            if id_col.lower() not in colset:
                raise ValueError(f"Identifier column does not exist: `{id_col}` in `{table}`")

            # 3) Target column exists? If not, create it (optional)
            if tgt_col.lower() not in colset:
                if not create_target_col_if_missing:
                    raise ValueError(f"Target column does not exist: `{tgt_col}` in `{table}`")

                # Create the missing column
                conn.execute(
                    text(f"ALTER TABLE `{table}` ADD COLUMN `{tgt_col}` {target_col_type}")
                )

                # Refresh column set (optional but nice)
                colset.add(tgt_col.lower())

            # 4) Update
            upd = conn.execute(
                text(f"UPDATE `{table}` SET `{tgt_col}` = :v WHERE `{id_col}` = :idv"),
                {"v": target_val, "idv": identifier_val},
            )

            if upd.rowcount and upd.rowcount > 0:
                return {"status": "updated", "rowcount": int(upd.rowcount)}

            # 5) Insert if missing
            if insert_if_missing:
                conn.execute(
                    text(f"INSERT INTO `{table}` (`{id_col}`, `{tgt_col}`) VALUES (:idv, :v)"),
                    {"idv": identifier_val, "v": target_val},
                )
                return {"status": "inserted", "rowcount": 1}

            return {"status": "not_found", "rowcount": 0}

    except (SQLAlchemyError, Exception) as e:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = (
            f"[{ts}] Function: {func_name}\n"
            f"table={table_name}, identifier=({identifier_col}={identifier_val}), "
            f"target=({target_col}={target_val}), insert_if_missing={insert_if_missing}, "
            f"create_target_col_if_missing={create_target_col_if_missing}, target_col_type={target_col_type}\n"
            f"Error: {e}\n"
            f"Traceback:\n{traceback.format_exc()}\n"
            f"{'-'*80}\n"
        )
        with open(LOG_FILE, "a") as f:
            f.write(msg)
        raise

# ------------------ Helpers ---------------------------------------------------
def clean_col(c: str) -> str:
    c = c.strip()
    for ch in [' ', '-', '/', '\\', '.', '(', ')', '[', ']', ':', ';', ',']:
        c = c.replace(ch, '_')
    if c.lower() in {"key","order","select","group","index","primary","table","from","to"}:
        c = f"{c}_col"
    return c

def rename_id_to_session_id(df: pd.DataFrame) -> pd.DataFrame:
    # case-insensitive rename: 'id' -> 'SESSION_ID'
    df.rename(columns=lambda c: "SESSION_ID" if c.strip().lower() == "id" else c, inplace=True)
    return df


def drop_table_if_exists(engine, table: str):
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS `{table}`"))

def ensure_table(engine, df, table):
    """
    Create table if missing with exactly df.columns (TEXT NULL).
    Add any newly seen columns (case-insensitive).
    Assumes df.columns are already cleaned and ID->SESSION_ID applied.
    """
    cols = [str(c) for c in df.columns]

    # Guard: case-insensitive duplicates in df
    seen = {}
    dups = []
    for c in cols:
        lc = c.lower()
        seen[lc] = seen.get(lc, 0) + 1
        if seen[lc] > 1:
            dups.append(c)
    if dups:
        raise ValueError(f"Duplicate column names (case-insensitive) in DataFrame: {sorted(dups)}")

    col_defs = ", ".join([f"`{c}` TEXT NULL" for c in cols])
    with engine.begin() as conn:
        conn.execute(text(f"CREATE TABLE IF NOT EXISTS `{table}` ({col_defs})"))
        existing = conn.execute(text(f"SHOW COLUMNS FROM `{table}`")).fetchall()
        existing_lc = {row[0].lower() for row in existing}
        missing = [c for c in cols if c.lower() not in existing_lc]
        if missing:
            alter_sql = "ALTER TABLE `{}` ".format(table) + ", ".join(
                f"ADD COLUMN `{c}` TEXT NULL" for c in missing
            )
            conn.execute(text(alter_sql))

def add_unique_key_if_needed(engine, table, key_col):
    if not key_col:
        return
    with engine.begin() as conn:
        idx_name = f"uniq_{table}_{key_col}"
        try:
            conn.execute(text(f"ALTER TABLE `{table}` ADD UNIQUE `{idx_name}` (`{key_col}`)"))
        except Exception:
            # likely already exists; ignore
            pass

def upsert_chunk(engine, df, table, key_col):
    # Build ON DUPLICATE KEY UPDATE
    cols = [f"`{c}`" for c in df.columns]
    placeholders = ", ".join(["%s"] * len(cols))
    col_list = ", ".join(cols)
    updates = ", ".join([f"{c}=VALUES({c})" for c in cols if c.strip("`") != key_col])

    # Convert to tuples; keep None for NULL
    rows = [tuple(None if pd.isna(v) else str(v) for v in row) for row in df.to_numpy()]
    sql = f"INSERT INTO `{table}` ({col_list}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {updates}"
    with engine.raw_connection() as raw:
        cur = raw.cursor()
        cur.executemany(sql, rows)
        raw.commit()


def load_csv_to_mysql(
    csv_path,
    table=None,
    chunksize=5000,
    key_col=None,
    infer_dates=False,
    drop_first=True
):
    """
    Load a CSV into Railway MySQL (or any SQLAlchemy-compatible MySQL engine).

    Parameters
    ----------
    csv_path : str
        Path to the CSV file to load.
    table : str, optional
        Table name to write to (default: CSV filename without extension).
    chunksize : int, optional
        Number of rows per chunk to process (default: 5000).
    key_col : str, optional
        Column to use as UNIQUE key for upserts (optional).
    infer_dates : bool, optional
        Try to parse obvious date columns (default: False).
    drop_first : bool, optional
        DROP TABLE IF EXISTS before (re)creating (default: True).

    Returns
    -------
    dict
        Summary containing total rows inserted and target table name.
    """
    # --- Derive table name ---
    table = table or os.path.splitext(os.path.basename(csv_path))[0]
    table = clean_col(table)

    # --- Connect to DB ---
    # engine = build_engine()

    # ========== Branch 1: Drop & recreate ==========
    if drop_first:
        print(f"[INFO] Dropping table `{table}` (if exists)...")
        drop_table_if_exists(engine, table)

        # Read CSV in chunks
        reader = pd.read_csv(csv_path, chunksize=chunksize)
        try:
            first_chunk = next(reader)
        except StopIteration:
            print("[WARN] CSV is empty. Nothing to load.")
            return {"table": table, "total_rows": 0}

        # --- Clean columns ---
        first_chunk.columns = [clean_col(c) for c in first_chunk.columns]
        rename_id_to_session_id(first_chunk)

        if infer_dates:
            for c in first_chunk.columns:
                try:
                    first_chunk[c] = pd.to_datetime(first_chunk[c], errors="ignore")
                except Exception:
                    pass

        # --- Create table schema ---
        first_chunk.head(0).to_sql(name=table, con=engine, if_exists="replace", index=False)
        if key_col:
            if key_col not in first_chunk.columns:
                raise ValueError(f"key_col '{key_col}' not found in CSV columns after cleaning/renaming.")
            add_unique_key_if_needed(engine, table, key_col)
            upsert_chunk(engine, first_chunk.fillna(pd.NA).astype(object), table, key_col)
        else:
            first_chunk.to_sql(name=table, con=engine, if_exists="append", index=False, method="multi")

        # --- Append remaining chunks ---
        total = len(first_chunk)
        for chunk in reader:
            chunk.columns = [clean_col(c) for c in chunk.columns]
            rename_id_to_session_id(chunk)
            if infer_dates:
                for c in chunk.columns:
                    try:
                        chunk[c] = pd.to_datetime(chunk[c], errors="ignore")
                    except Exception:
                        pass

            if key_col:
                if key_col not in chunk.columns:
                    raise ValueError(f"key_col '{key_col}' not found in CSV columns.")
                upsert_chunk(engine, chunk.fillna(pd.NA).astype(object), table, key_col)
            else:
                chunk.to_sql(
                    name=table,
                    con=engine,
                    if_exists="append",
                    index=False,
                    method="multi",
                    chunksize=chunksize
                )

            total += len(chunk)
            print(f"[INFO] Inserted {total} rows...", flush=True)

        print(f"✅ Done. Loaded ~{total} rows into `{table}`.")
        return {"table": table, "total_rows": total}

    # ========== Branch 2: Keep existing table ==========
    print(f"[INFO] Keeping existing table `{table}`; ensuring schema...")

    first = pd.read_csv(csv_path, nrows=200)
    first.columns = [clean_col(c) for c in first.columns]
    rename_id_to_session_id(first)

    if infer_dates:
        for c in first.columns:
            try:
                _ = first[c].dropna().head(10).map(lambda x: dtparser.parse(str(x)))
                first[c] = pd.to_datetime(first[c], errors="ignore")
            except Exception:
                pass

    ensure_table(engine, first, table)
    if key_col:
        if key_col not in first.columns:
            raise ValueError(f"key_col '{key_col}' not found in CSV columns after cleaning/renaming.")
        add_unique_key_if_needed(engine, table, key_col)

    reader = pd.read_csv(csv_path, chunksize=chunksize)
    total = 0
    for chunk in reader:
        chunk.columns = [clean_col(c) for c in chunk.columns]
        rename_id_to_session_id(chunk)
        if infer_dates:
            for c in chunk.columns:
                try:
                    chunk[c] = pd.to_datetime(chunk[c], errors="ignore")
                except Exception:
                    pass

        if key_col:
            if key_col not in chunk.columns:
                raise ValueError(f"key_col '{key_col}' not found in CSV columns.")
            upsert_chunk(engine, chunk.fillna(pd.NA).astype(object), table, key_col)
        else:
            chunk.to_sql(
                name=table,
                con=engine,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=chunksize
            )

        total += len(chunk)
        print(f"[INFO] Inserted {total} rows...", flush=True)

    print(f"✅ Done. Loaded ~{total} rows into `{table}`.")
    return {"table": table, "total_rows": total}

# ------------------ Main ------------------------------------------------------
def create_table(csvfilenamefortable):
    # ap = argparse.ArgumentParser(description="Load a CSV into Railway MySQL.")
    # ap.add_argument("csv", help="Path to CSV file")
    # # ap.add_argument("--table", help="Table name to write to (default: CSV filename)", default=None)
    # ap.add_argument("--chunksize", type=int, default=5000, help="Rows per chunk")
    # ap.add_argument("--key-col", default=None, help="Column to use as UNIQUE key for upserts (optional)")
    # ap.add_argument("--infer-dates", action="store_true", help="Try to parse obvious date columns")
    # ap.add_argument("--drop-first", action="store_true", default=True,
    #                 help="DROP TABLE IF EXISTS before (re)creating (default: true)")
    # args = ap.parse_args()

    # table = args.table or os.path.splitext(os.path.basename(args.csv))[0]
    # table = clean_col(table)
    # reader = pd.read_csv(args.csv, chunksize=args.chunksize)
    # table=
    args=argparse.Namespace()
    args.csv=csvfilenamefortable
    reader1 = pd.read_csv(args.csv)
    table = reader1['project'].iloc[0] #.item()
    # engine = build_engine()
    args.drop_first=True
    args.infer_dates=False
    args.key_col=False
    args.infer_dates=False
    args.chunksize=5000
    # ---------- Branch 1: Drop & recreate ----------
    if args.drop_first:
        print(f"[INFO] Dropping table `{table}` (if exists)...")
        drop_table_if_exists(engine, table)

        reader = pd.read_csv(args.csv, chunksize=args.chunksize)
        try:
            first_chunk = next(reader)
        except StopIteration:
            print("[WARN] CSV is empty. Nothing to load.")
            return

        # Clean + rename
        first_chunk.columns = [clean_col(c) for c in first_chunk.columns]
        rename_id_to_session_id(first_chunk)

        if args.infer_dates:
            for c in first_chunk.columns:
                try:
                    first_chunk[c] = pd.to_datetime(first_chunk[c], errors="ignore")
                except Exception:
                    pass

        # Create table schema from first chunk
        # If using upserts, we still need the table created:
        first_chunk.head(0).to_sql(name=table, con=engine, if_exists="replace", index=False)
        if args.key_col:
            if args.key_col not in first_chunk.columns:
                raise SystemExit(f"--key-col '{args.key_col}' not found in CSV columns after cleaning/renaming.")
            add_unique_key_if_needed(engine, table, args.key_col)
            # upsert first chunk
            upsert_chunk(engine, first_chunk.fillna(pd.NA).astype(object), table, args.key_col)
        else:
            # simple append for first chunk
            first_chunk.to_sql(name=table, con=engine, if_exists="append", index=False, method="multi")

        # Append remaining chunks
        total = len(first_chunk)
        for chunk in reader:
            chunk.columns = [clean_col(c) for c in chunk.columns]
            rename_id_to_session_id(chunk)
            if args.infer_dates:
                for c in chunk.columns:
                    try:
                        chunk[c] = pd.to_datetime(chunk[c], errors="ignore")
                    except Exception:
                        pass

            if args.key_col:
                if args.key_col not in chunk.columns:
                    raise SystemExit(f"--key-col '{args.key_col}' not found in CSV columns.")
                upsert_chunk(engine, chunk.fillna(pd.NA).astype(object), table, args.key_col)
            else:
                chunk.to_sql(
                    name=table,
                    con=engine,
                    if_exists="append",
                    index=False,
                    method="multi",
                    chunksize=args.chunksize
                )

            total += len(chunk)
            print(f"[INFO] Inserted {total} rows...", flush=True)

        print(f"✅ Done. Loaded ~{total} rows into `{table}`.")
        return

    # ---------- Branch 2: Keep table; ensure columns; then load ----------
    # Peek to prep columns for ensuring schema
    first = pd.read_csv(args.csv, nrows=200)
    first.columns = [clean_col(c) for c in first.columns]
    rename_id_to_session_id(first)
    if args.infer_dates:
        for c in first.columns:
            try:
                _ = first[c].dropna().head(10).map(lambda x: dtparser.parse(str(x)))
                first[c] = pd.to_datetime(first[c], errors="ignore")
            except Exception:
                pass

    ensure_table(engine, first, table)
    if args.key_col:
        if args.key_col not in first.columns:
            raise SystemExit(f"--key-col '{args.key_col}' not found in CSV columns after cleaning/renaming.")
        add_unique_key_if_needed(engine, table, args.key_col)

    # Stream insert
    reader = pd.read_csv(args.csv, chunksize=args.chunksize)
    total = 0
    for chunk in reader:
        chunk.columns = [clean_col(c) for c in chunk.columns]
        rename_id_to_session_id(chunk)
        if args.infer_dates:
            for c in chunk.columns:
                try:
                    chunk[c] = pd.to_datetime(chunk[c], errors="ignore")
                except Exception:
                    pass

        if args.key_col:
            if args.key_col not in chunk.columns:
                raise SystemExit(f"--key-col '{args.key_col}' not found in CSV columns.")
            upsert_chunk(engine, chunk.fillna(pd.NA).astype(object), table, args.key_col)
        else:
            chunk.to_sql(
                name=table,
                con=engine,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=args.chunksize
            )

        total += len(chunk)
        print(f"[INFO] Inserted {total} rows...", flush=True)

    print(f"✅ Done. Loaded ~{total} rows into `{table}`.")
import pandas as pd
import inspect

def apply_single_row_csv_to_table(
    csv_file: str,
    table_name: str,
    session_id: str,
    insert_if_missing: bool = True,
    create_target_col_if_missing: bool = True,
    default_target_col_type: str = "VARCHAR(255) NULL",
):
    """
    Read a single-row CSV and apply each column value to the database table
    using update_table_value_by_identifier().
    """
    func_name = inspect.currentframe().f_code.co_name

    # Load CSV
    df = pd.read_csv(csv_file)

    if df.shape[0] != 1:
        raise ValueError(
            f"{func_name}: CSV must contain exactly ONE row, found {df.shape[0]}"
        )

    row = df.iloc[0]

    # if identifier_col not in df.columns:
    #     raise ValueError(
    #         f"{func_name}: Identifier column '{identifier_col}' not found in CSV"
    #     )

    identifier_val =  session_id ##row[identifier_col]

    results = []

    for col in df.columns:
        # Skip identifier column itself
        # if col == identifier_col:
        #     continue

        val = row[col]

        # Skip NaN values (optional but usually desired)
        if pd.isna(val):
            continue

        res = update_table_value_by_identifier(
            engine=engine,
            table_name=table_name,
            identifier_col="SESSION_ID",
            identifier_val=identifier_val,
            target_col=col,
            target_val=val,
            insert_if_missing=insert_if_missing,
            create_target_col_if_missing=create_target_col_if_missing,
            target_col_type=default_target_col_type,
        )

        results.append({
            "column": col,
            "value": val,
            "result": res,
        })

    return {
        "status": "completed",
        "table": table_name,
        "identifier": {"SESSION_ID": identifier_val},
        "updates": results,
    }

# def main():
# #     # create_table('/home/atul/Downloads/sessions_COLI_BEFORE_SORTING_STEP1_20231208210754.csv')
# #     # make_column_not_null_and_unique(engine, "COLI", "SESSION_ID") #, col_type="VARCHAR(64)")
# #     # # download_as_csv('COLI',"COLI_2.csv")
# #     # # update_table_value_by_identifier(engine,"COLI","SESSION_ID","SNIPR01_E00001","ANY_NON_NUMERICAL_PARAMETER",'AJGH392847',insert_if_missing=True)
#     download_as_csv('COLI', "COLI_2.csv")
# #     return 1
# #
# if __name__ == "__main__":
#     main()
