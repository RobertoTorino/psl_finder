from __future__ import annotations

import os
import sqlite3
import sys
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox


# === PATH RESOLUTION (source vs PyInstaller) ===
def get_base_dir() -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # noinspection PyProtectedMember
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()
DB_PATH = os.path.join(BASE_DIR, "games.db")


def get_tables_with_columns(
        db_path: str,
        required_columns: tuple[str, ...] = ("GameId", "GameTitle", "Link", "Region"),
) -> list[str]:
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables: list[str] = [row[0] for row in cursor.fetchall()]

        valid_tables: list[str] = []
        for table in tables:
            try:
                cursor.execute(f"PRAGMA table_info({table});")
                table_columns: list[str] = [row[1] for row in cursor.fetchall()]
                if all(req in table_columns for req in required_columns):
                    valid_tables.append(table)
            except sqlite3.Error:
                # Skip tables that cannot be inspected
                continue

        return valid_tables

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Could not open/read database:\n{e}")
        return []  # Always return list[str] as declared
    finally:
        if conn is not None:
            conn.close()


def get_all_regions(db_path: str, tables: list[str]) -> list[str]:
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        regions: set[str] = set()
        for table in tables:
            try:
                cursor.execute(
                    f"""
                    SELECT DISTINCT Region
                    FROM {table}
                    WHERE Region IS NOT NULL AND Region != ''
                    """
                )
                # Force str to keep the set typed as set[str]
                regions.update(str(row[0]) for row in cursor.fetchall() if row[0] is not None)
            except sqlite3.Error:
                continue

        return sorted(regions)

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Could not query regions:\n{e}")
        return []
    finally:
        if conn is not None:
            conn.close()


def search_games(
        query: str,
        tables: list[str],
        table_filter: str,
        region_filter: str,
) -> list[tuple]:
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        results: list[tuple] = []
        search_tables = tables if table_filter == "All" else [table_filter]

        for table in search_tables:
            try:
                if region_filter != "All":
                    cursor.execute(
                        f"""
                        SELECT ?, GameId, GameTitle, Link, Region
                        FROM {table}
                        WHERE GameTitle LIKE ? AND Region = ?
                        """,
                        (table, f"%{query}%", region_filter),
                    )
                else:
                    cursor.execute(
                        f"""
                        SELECT ?, GameId, GameTitle, Link, Region
                        FROM {table}
                        WHERE GameTitle LIKE ?
                        """,
                        (table, f"%{query}%",),
                    )

                results.extend(cursor.fetchall())
            except sqlite3.Error:
                continue

        return results

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Search failed:\n{e}")
        return []
    finally:
        if conn is not None:
            conn.close()


# === STARTUP VALIDATION ===
if not os.path.exists(DB_PATH):
    messagebox.showerror("Missing Database", f"games.db not found:\n{DB_PATH}")
    raise SystemExit(1)

TABLES_WITH_LINKS = get_tables_with_columns(DB_PATH)
if not TABLES_WITH_LINKS:
    messagebox.showerror("Error", "No tables with GameId, GameTitle, Link, and Region columns found.")
    raise SystemExit(1)

REGIONS = ["All"] + get_all_regions(DB_PATH, TABLES_WITH_LINKS)
TABLE_OPTIONS = ["All"] + TABLES_WITH_LINKS


# === GUI CALLBACKS ===
def on_search() -> None:
    query = search_entry.get().strip()
    if not query:
        messagebox.showinfo("Info", "Please enter a search term.")
        return

    table_choice = table_var.get()
    region_choice = region_var.get()

    results_list.delete(*results_list.get_children())
    results = search_games(query, TABLES_WITH_LINKS, table_choice, region_choice)

    if not results:
        messagebox.showinfo("No Results", "No matching games found.")
        return

    for table, gameid, title, link, region in results:
        results_list.insert(
            "",
            "end",
            values=(table, gameid, title, link if link else "—", region if region else "—"),
        )


def on_open_link(_event=None) -> None:
    selected = results_list.focus()
    if not selected:
        messagebox.showwarning("Warning", "Select a game first.")
        return

    item = results_list.item(selected)
    link = item["values"][3]

    if link == "—" or not link:
        messagebox.showinfo("Info", "No link available for this game.")
        return

    webbrowser.open(str(link))


# === GUI SETUP ===
root = tk.Tk()
root.title("PS Link Finder — Search by Title, Table and Region")
root.geometry("1100x500")
root.resizable(False, False)

frame_top = ttk.Frame(root, padding=10)
frame_top.pack(fill="x")

ttk.Label(frame_top, text="Search Game Title:").pack(side="left")
search_entry = ttk.Entry(frame_top, width=35)
search_entry.pack(side="left", padx=5)
search_entry.bind("<Return>", lambda e: on_search())

ttk.Label(frame_top, text="Table:").pack(side="left", padx=(10, 2))
table_var = tk.StringVar(value="All")
table_dropdown = ttk.Combobox(
    frame_top, textvariable=table_var, values=TABLE_OPTIONS, width=20, state="readonly"
)
table_dropdown.pack(side="left")

ttk.Label(frame_top, text="Region:").pack(side="left", padx=(10, 2))
region_var = tk.StringVar(value="All")
region_dropdown = ttk.Combobox(
    frame_top, textvariable=region_var, values=REGIONS, width=15, state="readonly"
)
region_dropdown.pack(side="left")

ttk.Button(frame_top, text="Search", command=on_search).pack(side="left", padx=5)
ttk.Button(frame_top, text="Open Link", command=on_open_link).pack(side="left")

tree_columns = ("Table", "GameId", "GameTitle", "Link", "Region")
results_list = ttk.Treeview(root, columns=tree_columns, show="headings", height=15)

for col_name, heading_text, width in [
    ("Table", "Table", 120),
    ("GameId", "GameId", 100),
    ("GameTitle", "Game Title", 300),
    ("Link", "Link", 400),
    ("Region", "Region", 100),
]:
    results_list.heading(col_name, text=heading_text)
    results_list.column(col_name, width=width)

results_list.pack(fill="both", expand=True, padx=10, pady=5)
results_list.bind("<Double-1>", on_open_link)

root.mainloop()
