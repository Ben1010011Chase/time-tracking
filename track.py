import sqlite3
import time
import re

def create_table():
    conn = sqlite3.connect('task_times.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS task_times
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  task_time INTEGER,
                  task_date DATE DEFAULT (datetime('now', 'localtime')))''')
    conn.commit()
    conn.close()

def insert_task_time(task_time):
    conn = sqlite3.connect('task_times.db')
    c = conn.cursor()
    c.execute("INSERT INTO task_times (task_time) VALUES (?)", (task_time,))
    conn.commit()
    conn.close()

def delete_last_task_time():
    conn = sqlite3.connect('task_times.db')
    c = conn.cursor()
    c.execute("SELECT id FROM task_times ORDER BY id DESC LIMIT 1")
    last_id = c.fetchone()
    if last_id is not None:
        c.execute("DELETE FROM task_times WHERE id = ?", (last_id[0],))
        conn.commit()
        print("Last entry deleted successfully")
    else:
        print("No entries to delete")
    conn.close()

def parse_time(time_str):
    try:
        d, h, m, s = time_str.split(':')
        time_val = int(s) + int(m) * 60 + int(h) * 3600 + int(d) * 86400
    except ValueError:
        try:
            m, s = time_str.split(':')
            time_val = int(s) + int(m) * 60
        except ValueError:
            time_val = int(time_str)
    return time_val

def format_time(time_val):
    if time_val >= 86400:
        days = time_val // 86400
        time_val -= days * 86400
        time_str = f"{days}:{time.strftime('%H:%M:%S', time.gmtime(time_val))}"
    else:
        time_str = time.strftime('%M:%S', time.gmtime(time_val))
    return time_str

def get_today_task_times():
    conn = sqlite3.connect('task_times.db')
    c = conn.cursor()
    c.execute("SELECT task_time FROM task_times WHERE task_date >= date('now', 'localtime', 'start of day') AND task_date < date('now', 'localtime', 'start of day', '+1 day')")
    task_times = c.fetchall()
    conn.close()
    return [format_time(t[0]) for t in task_times]

def get_week_task_times():
    conn = sqlite3.connect('task_times.db')
    c = conn.cursor()
    c.execute("SELECT task_time FROM task_times WHERE task_date >= date('now', 'localtime', 'start of day', '-6 days') AND task_date < date('now', 'localtime', 'start of day', '+1 day')")
    task_times = c.fetchall()
    conn.close()
    return [format_time(t[0]) for t in task_times]

create_table()
default_task_time = 80  # seconds

def print_task_time_stats():
    today_task_times = get_today_task_times()
    today_total_time = sum([parse_time(t) for t in today_task_times])
    week_task_times = get_week_task_times()
    week_total_time = sum([parse_time(t) for t in week_task_times])
    print(f"Total time today: {format_time(today_total_time)}")
    print(f"Total time this week: {format_time(week_total_time)}")
    print()

while True:
    try:
        task_time_str = input(f"Enter task time in MM:SS format (default {default_task_time//60}:{default_task_time%60:02d}): ")
        if not task_time_str:
            task_time = default_task_time
        elif task_time_str.lower() == 'undo':
            delete_last_task_time()
            print("Last task time deleted")
            print_task_time_stats()
            continue
        else:
            # Validate input format
            if not re.match(r'^\d{1,2}:\d{2}$', task_time_str):
                raise ValueError("Invalid input format, please enter time in MM:SS format")
            # Convert to seconds
            m, s = task_time_str.split(':')
            task_time = int(s) + int(m) * 60
    except ValueError as e:
        print(e)
        continue
    except KeyboardInterrupt:
        print("\nEnding program...")
        break

    insert_task_time(task_time)
    print_task_time_stats()


 