import csv
import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = "fitness_logs.csv"
FIELDNAMES = [
    "Date", "Category", "Exercise", "Weight (lbs)", "Reps",
    "Distance (mi)", "Time (min)", "Speed (mph)", "Notes"
]

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()

def add_log():
    print("\n--- Add New Workout Log ---")
    date = input("Date (YYYY-MM-DD) [leave blank for today]: ") or datetime.now().strftime("%Y-%m-%d")
    category = input("Category (Strength/Cardio/Other): ").capitalize()
    exercise = input("Exercise name: ")
    weight = input("Weight (lbs): ")
    reps = input("Reps: ")
    distance = input("Distance (mi): ")
    time = input("Time (min): ")
    speed = input("Speed (mph): ")
    notes = input("Notes: ")

    log = {
        "Date": date,
        "Category": category,
        "Exercise": exercise,
        "Weight (lbs)": weight,
        "Reps": reps,
        "Distance (mi)": distance,
        "Time (min)": time,
        "Speed (mph)": speed,
        "Notes": notes
    }

    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(log)

    print("✅ Log saved!")

def view_logs():
    print("\n--- Workout Logs ---")
    try:
        with open(CSV_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                print(row)
    except FileNotFoundError:
        print("No logs found yet. Add a workout first.")

def weekly_summary():
    print("\n--- Weekly Summary ---")
    today = datetime.now().date()
    one_week_ago = today - timedelta(days=7)
    total_workouts = 0
    total_weight = 0
    total_distance = 0

    try:
        with open(CSV_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    row_date = datetime.strptime(row["Date"], "%Y-%m-%d").date()
                    if row_date >= one_week_ago:
                        total_workouts += 1
                        weight = float(row["Weight (lbs)"]) if row["Weight (lbs)"] else 0
                        reps = int(row["Reps"]) if row["Reps"] else 0
                        total_weight += weight * reps
                        distance = float(row["Distance (mi)"]) if row["Distance (mi)"] else 0
                        total_distance += distance
                except:
                    continue

        print(f"📅 Workouts in last 7 days: {total_workouts}")
        print(f"🏋️ Total weight lifted: {total_weight} lbs")
        print(f"🏃 Total distance run: {total_distance} miles")

    except FileNotFoundError:
        print("No logs found yet.")

def filter_by_category():
    category = input("\nEnter category to filter (Strength/Cardio/Other): ").capitalize()
    print(f"\n--- Logs in Category: {category} ---")
    try:
        with open(CSV_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            filtered = [row for row in reader if row["Category"] == category]
            for row in filtered:
                print(row)
            if not filtered:
                print("No logs found in that category.")
    except FileNotFoundError:
        print("No logs found yet.")

def calculate_one_rep_max():
    print("\n--- 1-Rep Max Estimator ---")
    exercise = input("Exercise name: ").lower()
    best_1rm = 0
    best_entry = None

    try:
        with open(CSV_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Exercise"].lower() == exercise:
                    try:
                        weight = float(row["Weight (lbs)"])
                        reps = int(row["Reps"])
                        one_rm = weight * (1 + reps / 30)
                        if one_rm > best_1rm:
                            best_1rm = one_rm
                            best_entry = row
                    except:
                        continue
        if best_entry:
            print(f"💪 Best estimated 1-Rep Max for '{exercise.title()}': {best_1rm:.1f} lbs")
            print(f"  → Based on: {best_entry['Weight (lbs)']} lbs x {best_entry['Reps']} reps on {best_entry['Date']}")
        else:
            print("No valid logs found for that exercise.")

    except FileNotFoundError:
        print("No logs found yet.")

# === 📊 Visualization Functions ===

def plot_weight_lifted(df):
    df["Date"] = pd.to_datetime(df["Date"])
    df["Total Weight"] = pd.to_numeric(df["Weight (lbs)"], errors="coerce") * pd.to_numeric(df["Reps"], errors="coerce")
    summary = df.groupby("Date")["Total Weight"].sum()

    plt.figure(figsize=(10, 5))
    summary.plot(kind="line", marker="o")
    plt.title("Total Weight Lifted Over Time")
    plt.xlabel("Date")
    plt.ylabel("Weight (lbs)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_workout_frequency(df):
    df["Date"] = pd.to_datetime(df["Date"])
    weekly = df["Date"].dt.to_period("W").value_counts().sort_index()

    plt.figure(figsize=(10, 5))
    weekly.plot(kind="bar")
    plt.title("Workout Frequency by Week")
    plt.xlabel("Week")
    plt.ylabel("Sessions")
    plt.tight_layout()
    plt.show()

def plot_exercise_breakdown(df):
    count = df["Exercise"].value_counts()

    plt.figure(figsize=(8, 6))
    count.plot(kind="pie", autopct="%1.1f%%", startangle=140)
    plt.title("Exercise Breakdown")
    plt.ylabel("")
    plt.tight_layout()
    plt.show()

def plot_one_rep_max_trend(df):
    df["Date"] = pd.to_datetime(df["Date"])
    df["Weight (lbs)"] = pd.to_numeric(df["Weight (lbs)"], errors="coerce")
    df["Reps"] = pd.to_numeric(df["Reps"], errors="coerce")
    df = df.dropna(subset=["Weight (lbs)", "Reps", "Date"])

    df["1RM"] = df["Weight (lbs)"] * (1 + df["Reps"] / 30)
    trend = df.groupby("Date")["1RM"].max()

    plt.figure(figsize=(10, 5))
    trend.plot(marker="o")
    plt.title("Estimated 1-Rep Max Trend")
    plt.xlabel("Date")
    plt.ylabel("1RM (lbs)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def show_visualizations():
    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    while True:
        print("\n📊 Visualization Menu:")
        print("1. Total weight lifted over time")
        print("2. Workout frequency by week")
        print("3. Exercise breakdown (pie chart)")
        print("4. 1-Rep Max trend")
        print("5. Return to main menu")
        choice = input("Choose an option: ")

        if choice == "1":
            plot_weight_lifted(df)
        elif choice == "2":
            plot_workout_frequency(df)
        elif choice == "3":
            plot_exercise_breakdown(df)
        elif choice == "4":
            plot_one_rep_max_trend(df)
        elif choice == "5":
            break
        else:
            print("Invalid option. Try again.")

# === 🏁 Main App Loop ===

def main():
    init_csv()
    while True:
        print("\n======= Fitness Tracker =======")
        print("1. Add new workout log")
        print("2. View all logs")
        print("3. View weekly summary")
        print("4. Filter logs by category")
        print("5. Calculate 1-Rep Max")
        print("6. Show Visualizations")
        print("7. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_log()
        elif choice == "2":
            view_logs()
        elif choice == "3":
            weekly_summary()
        elif choice == "4":
            filter_by_category()
        elif choice == "5":
            calculate_one_rep_max()
        elif choice == "6":
            show_visualizations()
        elif choice == "7":
            print("👋 Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
