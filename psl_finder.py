# import os
# import sys
# import sqlite3
# import tkinter as tk
# from tkinter import ttk, messagebox
# import webbrowser
#
# # === CONFIGURATION ===
# # Correctly locate games.db inside PyInstaller bundle or source folder
# if getattr(sys, 'frozen', False):
#     BASE_DIR = sys._MEIPASS  # Folder where PyInstaller extracts the bundle
# else:
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#
# DB_PATH = os.path.join(BASE_DIR, "games.db")
#
#
# # === DATABASE FUNCTIONS ===
# def get_tables_with_columns(db_path, required_columns=("GameId", "GameTitle", "Link")):
#     """Return all tables that contain the required columns."""
#     try:
#         conn = sqlite3.connect(db_path)
#     except Exception as e:
#         messagebox.showerror("Database Error", f"Could not open database:\n{e}")
#         sys.exit(1)
#
#     cursor = conn.cursor()
#     cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables = [row[0] for row in cursor.fetchall()]
#     valid_tables = []
#     for table in tables:
#         try:
#             cursor.execute(f"PRAGMA table_info({table});")
#             columns = [row[1] for row in cursor.fetchall()]
#             if all(col in columns for col in required_columns):
#                 valid_tables.append(table)
#         except Exception:
#             continue
#     conn.close()
#     return valid_tables
#
#
# def search_games_across_tables(query, tables):
#     """Search for GameTitle in all matching tables and return (table, gameid, title, link)."""
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     results = []
#     for table in tables:
#         try:
#             cursor.execute(f"""
#                 SELECT ?, GameId, GameTitle, Link
#                 FROM {table}
#                 WHERE GameTitle LIKE ?
#             """, (table, f"%{query}%"))
#             results.extend(cursor.fetchall())
#         except sqlite3.OperationalError:
#             continue
#     conn.close()
#     return results
#
#
# # === GUI CALLBACKS ===
# def on_search():
#     query = search_entry.get().strip()
#     if not query:
#         messagebox.showinfo("Info", "Please enter a search term.")
#         return
#
#     results_list.delete(*results_list.get_children())
#     results = search_games_across_tables(query, TABLES_WITH_LINKS)
#
#     if not results:
#         messagebox.showinfo("No Results", "No matching games found.")
#         return
#
#     for table, gameid, title, link in results:
#         results_list.insert("", "end", values=(table, gameid, title, link if link else "—"))
#
#
# def on_open_link(event=None):
#     selected = results_list.focus()
#     if not selected:
#         messagebox.showwarning("Warning", "Select a game first.")
#         return
#     item = results_list.item(selected)
#     link = item["values"][3]
#     if link == "—" or not link:
#         messagebox.showinfo("Info", "No link available for this game.")
#         return
#     webbrowser.open(link)
#
#
# # === INITIAL SETUP ===
# if not os.path.exists(DB_PATH):
#     messagebox.showerror("Missing Database", f"games.db not found:\n{DB_PATH}")
#     sys.exit(1)
#
# TABLES_WITH_LINKS = get_tables_with_columns(DB_PATH)
# if not TABLES_WITH_LINKS:
#     messagebox.showerror("Error", "No tables with GameId, GameTitle, and Link columns found.")
#     sys.exit(1)
#
#
# # === GUI SETUP ===
# root = tk.Tk()
# root.title("Game Link Finder — Search Across All Tables")
# root.geometry("950x450")
# root.resizable(False, False)
#
# # Search bar
# frame_top = ttk.Frame(root, padding=10)
# frame_top.pack(fill="x")
#
# search_label = ttk.Label(frame_top, text="Search Game Title:")
# search_label.pack(side="left")
#
# search_entry = ttk.Entry(frame_top, width=40)
# search_entry.pack(side="left", padx=5)
# search_entry.bind("<Return>", lambda e: on_search())
#
# search_button = ttk.Button(frame_top, text="Search", command=on_search)
# search_button.pack(side="left", padx=5)
#
# open_button = ttk.Button(frame_top, text="Open Link", command=on_open_link)
# open_button.pack(side="left")
#
# # Results table
# columns = ("Table", "GameId", "GameTitle", "Link")
# results_list = ttk.Treeview(root, columns=columns, show="headings", height=15)
# results_list.heading("Table", text="Table")
# results_list.heading("GameId", text="GameId")
# results_list.heading("GameTitle", text="Game Title")
# results_list.heading("Link", text="Link")
# results_list.column("Table", width=120)
# results_list.column("GameId", width=100)
# results_list.column("GameTitle", width=300)
# results_list.column("Link", width=400)
# results_list.pack(fill="both", expand=True, padx=10, pady=5)
#
# # Double-click to open link
# results_list.bind("<Double-1>", on_open_link)
#
# # Run app
# root.mainloop()
import os
import sys
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

# === CONFIGURATION ===
# Correctly locate games.db inside PyInstaller bundle or source folder
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS  # Folder where PyInstaller extracts the bundle
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "games.db")


# === DATABASE FUNCTIONS ===
def get_tables_with_columns(db_path, required_columns=("GameId", "GameTitle", "Link")):
    """Return all tables that contain the required columns."""
    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not open database:\n{e}")
        sys.exit(1)

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    valid_tables = []
    for table in tables:
        try:
            cursor.execute(f"PRAGMA table_info({table});")
            columns = [row[1] for row in cursor.fetchall()]
            if all(col in columns for col in required_columns):
                valid_tables.append(table)
        except Exception:
            continue
    conn.close()
    return valid_tables


def search_games_across_tables(query, tables):
    """Search for GameTitle in all matching tables and return (table, gameid, title, link)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    results = []
    for table in tables:
        try:
            cursor.execute(f"""
                SELECT ?, GameId, GameTitle, Link
                FROM {table}
                WHERE GameTitle LIKE ?
            """, (table, f"%{query}%"))
            results.extend(cursor.fetchall())
        except sqlite3.OperationalError:
            continue
    conn.close()
    return results


def search_games_in_table(query, table):
    """Search only in a specific table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    results = []
    try:
        cursor.execute(f"""
            SELECT ?, GameId, GameTitle, Link
            FROM {table}
            WHERE GameTitle LIKE ?
        """, (table, f"%{query}%"))
        results.extend(cursor.fetchall())
    except sqlite3.OperationalError:
        pass
    conn.close()
    return results


# === GUI CALLBACKS ===
def on_search():
    query = search_entry.get().strip()
    if not query:
        messagebox.showinfo("Info", "Please enter a search term.")
        return

    selected_table = table_filter.get()
    results_list.delete(*results_list.get_children())

    if selected_table == "All Tables":
        results = search_games_across_tables(query, TABLES_WITH_LINKS)
    else:
        results = search_games_in_table(query, selected_table)

    if not results:
        messagebox.showinfo("No Results", "No matching games found.")
        return

    for table, gameid, title, link in results:
        results_list.insert("", "end", values=(table, gameid, title, link if link else "—"))


def on_open_link(event=None):
    selected = results_list.focus()
    if not selected:
        messagebox.showwarning("Warning", "Select a game first.")
        return
    item = results_list.item(selected)
    link = item["values"][3]
    if link == "—" or not link:
        messagebox.showinfo("Info", "No link available for this game.")
        return
    webbrowser.open(link)


# === INITIAL SETUP ===
if not os.path.exists(DB_PATH):
    messagebox.showerror("Missing Database", f"games.db not found:\n{DB_PATH}")
    sys.exit(1)

TABLES_WITH_LINKS = get_tables_with_columns(DB_PATH)
if not TABLES_WITH_LINKS:
    messagebox.showerror("Error", "No tables with GameId, GameTitle, and Link columns found.")
    sys.exit(1)


# === GUI SETUP ===
root = tk.Tk()
root.title("Game Link Finder — Search Across Tables")
root.geometry("950x480")
root.resizable(False, False)

# --- Top frame (Search bar + table filter) ---
frame_top = ttk.Frame(root, padding=10)
frame_top.pack(fill="x")

search_label = ttk.Label(frame_top, text="Search Game Title:")
search_label.pack(side="left")

search_entry = ttk.Entry(frame_top, width=40)
search_entry.pack(side="left", padx=5)
search_entry.bind("<Return>", lambda e: on_search())

# Dropdown menu to filter tables
table_filter_label = ttk.Label(frame_top, text="Table:")
table_filter_label.pack(side="left", padx=(15, 2))

table_filter = ttk.Combobox(frame_top, values=["All Tables"] + TABLES_WITH_LINKS, state="readonly", width=25)
table_filter.set("All Tables")
table_filter.pack(side="left", padx=5)

search_button = ttk.Button(frame_top, text="Search", command=on_search)
search_button.pack(side="left", padx=5)

open_button = ttk.Button(frame_top, text="Open Link", command=on_open_link)
open_button.pack(side="left")

# --- Results table ---
columns = ("Table", "GameId", "GameTitle", "Link")
results_list = ttk.Treeview(root, columns=columns, show="headings", height=15)
results_list.heading("Table", text="Table")
results_list.heading("GameId", text="GameId")
results_list.heading("GameTitle", text="Game Title")
results_list.heading("Link", text="Link")
results_list.column("Table", width=120)
results_list.column("GameId", width=100)
results_list.column("GameTitle", width=300)
results_list.column("Link", width=400)
results_list.pack(fill="both", expand=True, padx=10, pady=5)

# Double-click to open link
results_list.bind("<Double-1>", on_open_link)

# --- Run app ---
root.mainloop()
