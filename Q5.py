import tkinter as tk
from tkinter import messagebox
import itertools
import math
import matplotlib.pyplot as plt

# ---------------------------
# Tourist Spot Dataset
# ---------------------------

spots = [
    {"name": "Pashupatinath Temple", "lat": 27.7104, "lon": 85.3488, "fee": 100, "tags": ["culture","religious"]},
    {"name": "Swayambhunath Stupa", "lat": 27.7149, "lon": 85.2906, "fee": 200, "tags": ["culture","heritage"]},
    {"name": "Garden of Dreams", "lat": 27.7125, "lon": 85.3170, "fee": 150, "tags": ["nature","relaxation"]},
    {"name": "Chandragiri Hills", "lat": 27.6616, "lon": 85.2458, "fee": 700, "tags": ["nature","adventure"]},
    {"name": "Kathmandu Durbar Square", "lat": 27.7048, "lon": 85.3076, "fee": 100, "tags": ["culture","heritage"]}
]

VISIT_TIME = 1   # each spot takes 1 hour

# ---------------------------
# Distance Function
# ---------------------------

def distance(a,b):
    return math.sqrt((a["lat"]-b["lat"])**2 + (a["lon"]-b["lon"])**2)

# ---------------------------
# Greedy Heuristic
# ---------------------------

def greedy_plan(time_limit,budget,interest):

    remaining_time = time_limit
    remaining_budget = budget

    available = spots.copy()
    route = []
    explanation = []

    current = available[0]

    while available and remaining_time > 0:

        best = None
        best_score = -1

        for s in available:

            if s["fee"] > remaining_budget:
                continue

            score = 0

            if interest in s["tags"]:
                score += 5

            score -= distance(current,s)

            if score > best_score:
                best_score = score
                best = s

        if best is None:
            break

        route.append(best)
        explanation.append(f"{best['name']} selected due to interest match and low travel distance")

        remaining_budget -= best["fee"]
        remaining_time -= VISIT_TIME

        current = best
        available.remove(best)

    return route, explanation

# ---------------------------
# Brute Force (for small set)
# ---------------------------

def brute_force_plan(time_limit,budget):

    best_route = []
    best_count = 0

    small_set = spots[:4]

    for r in range(1,len(small_set)+1):

        for perm in itertools.permutations(small_set,r):

            cost = sum(s["fee"] for s in perm)
            time_needed = len(perm)*VISIT_TIME

            if cost <= budget and time_needed <= time_limit:

                if len(perm) > best_count:
                    best_count = len(perm)
                    best_route = perm

    return best_route

# ---------------------------
# Map Visualization
# ---------------------------

def draw_map(route):

    x = [s["lon"] for s in route]
    y = [s["lat"] for s in route]

    plt.figure()

    plt.plot(x,y,marker='o')

    for i,s in enumerate(route):
        plt.text(s["lon"],s["lat"],s["name"])

    plt.title("Tourist Path")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    plt.show()

# ---------------------------
# GUI Function
# ---------------------------

def run_optimizer():

    try:
        time_limit = int(time_entry.get())
        budget = int(budget_entry.get())
        interest = interest_var.get()

    except:
        messagebox.showerror("Error","Enter valid values")
        return

    route, explanation = greedy_plan(time_limit,budget,interest)

    result_box.delete(1.0,tk.END)

    total_cost = sum(s["fee"] for s in route)

    result_box.insert(tk.END,"Suggested Itinerary\n\n")

    for i,s in enumerate(route):
        result_box.insert(tk.END,f"{i+1}. {s['name']} (Fee {s['fee']})\n")

    result_box.insert(tk.END,f"\nTotal Cost: {total_cost}\n")
    result_box.insert(tk.END,f"Total Time: {len(route)} hours\n\n")

    result_box.insert(tk.END,"Decision Explanation\n")

    for e in explanation:
        result_box.insert(tk.END,e+"\n")

    brute = brute_force_plan(time_limit,budget)

    result_box.insert(tk.END,"\nBrute Force Comparison\n")

    result_box.insert(tk.END,f"Heuristic visited: {len(route)} spots\n")
    result_box.insert(tk.END, f"Brute force best: {len(brute)} spots\n")

    if route:
        draw_map(route)

# ---------------------------
# Tkinter GUI
# ---------------------------

root = tk.Tk()
root.title("Tourist Spot Optimizer")
root.geometry("600x500")

title = tk.Label(root,text="Tourist Itinerary Planner",font=("Arial",16))
title.pack(pady=10)

frame = tk.Frame(root)
frame.pack()

tk.Label(frame,text="Available Time (hours)").grid(row=0,column=0)
time_entry = tk.Entry(frame)
time_entry.grid(row=0,column=1)

tk.Label(frame,text="Maximum Budget").grid(row=1,column=0)
budget_entry = tk.Entry(frame)
budget_entry.grid(row=1,column=1)

tk.Label(frame,text="Interest").grid(row=2,column=0)

interest_var = tk.StringVar()
interest_menu = tk.OptionMenu(frame,interest_var,"culture","nature","adventure","heritage")
interest_menu.grid(row=2,column=1)

run_btn = tk.Button(root,text="Generate Itinerary",command=run_optimizer)
run_btn.pack(pady=10)

result_box = tk.Text(root,height=20,width=70)
result_box.pack()

root.mainloop()