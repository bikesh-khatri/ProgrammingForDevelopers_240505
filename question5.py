import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import itertools
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ─────────────────── COLOUR PALETTE ───────────────────
BG       = "#1e1e2e"   # dark navy background
PANEL    = "#2a2a3e"   # slightly lighter panel
FG       = "#e0e0f0"   # near-white text
ACCENT   = "#7c9ef5"   # blue accent
GREEN    = "#3ddc84"   # run button
ENTRY_BG = "#12121e"   # entry background
ENTRY_FG = "#ffffff"   # entry text

# ─────────────────── DATASET ──────────────────────────
tourist_spots = [
    {"name": "Pashupatinath Temple", "lat": 27.7104, "lon": 85.3488, "fee": 100,
     "tags": {"culture", "religious"}, "open_time": "06:00", "close_time": "18:00"},
    {"name": "Swayambhunath Stupa",  "lat": 27.7149, "lon": 85.2906, "fee": 200,
     "tags": {"culture", "heritage"}, "open_time": "07:00", "close_time": "17:00"},
    {"name": "Garden of Dreams",     "lat": 27.7125, "lon": 85.3170, "fee": 150,
     "tags": {"nature", "relaxation"}, "open_time": "09:00", "close_time": "21:00"},
    {"name": "Chandragiri Hills",    "lat": 27.6616, "lon": 85.2458, "fee": 700,
     "tags": {"nature", "adventure"}, "open_time": "09:00", "close_time": "17:00"},
    {"name": "Kathmandu Durbar Sq.", "lat": 27.7048, "lon": 85.3076, "fee": 100,
     "tags": {"culture", "heritage"}, "open_time": "10:00", "close_time": "17:00"},
]

VISIT_DURATION = 1  # hours per spot

# ─────────────────── UTILITIES ────────────────────────
def distance(a, b):
    return math.sqrt((a["lat"] - b["lat"])**2 + (a["lon"] - b["lon"])**2)

def time_to_hours(t):
    h, m = map(int, t.split(":"))
    return h + m / 60

def hours_to_hhmm(h):
    hh = int(h)
    mm = int(round((h - hh) * 60))
    return f"{hh:02d}:{mm:02d}"


def greedy_itinerary(budget, interests, start_time, end_time):
    selected, schedule, explanation = [], [], []
    remaining_budget = budget
    current_time = start_time
    candidates = tourist_spots.copy()

    while candidates:
        current = selected[-1] if selected else {"lat": 27.7104, "lon": 85.3488}
        best, best_score = None, -1

        for spot in candidates:
            if spot["fee"] > remaining_budget:
                continue
            spot_open  = time_to_hours(spot["open_time"])
            spot_close = time_to_hours(spot["close_time"])
            if not (spot_open <= current_time and
                    current_time + VISIT_DURATION <= spot_close and
                    current_time + VISIT_DURATION <= end_time):
                continue
            interest_score = len(spot["tags"] & interests) if interests else 1
            score = interest_score / (distance(current, spot) + 0.01)
            if score > best_score:
                best_score, best = score, spot

        if best is None:
            break

        match = best["tags"] & interests if interests else best["tags"]
        explanation.append(
            f"  + {best['name']}: match={match or 'general'}, "
            f"fee=Rs.{best['fee']}, arrives {hours_to_hhmm(current_time)}"
        )
        schedule.append((best, current_time))
        selected.append(best)
        remaining_budget -= best["fee"]
        current_time += VISIT_DURATION
        candidates.remove(best)

    total_cost = sum(s["fee"] for s in selected)
    total_time = len(selected) * VISIT_DURATION
    return selected, schedule, explanation, total_cost, total_time

# ─────────────────── BRUTE FORCE ──────────────────────
def brute_force_itinerary(budget, start_time, end_time):
    best_perm, best_count, best_cost = [], 0, 0

    for r in range(1, len(tourist_spots) + 1):
        for perm in itertools.permutations(tourist_spots, r):
            cost = sum(p["fee"] for p in perm)
            if cost > budget:
                continue
            t, valid = start_time, True
            for spot in perm:
                o = time_to_hours(spot["open_time"])
                c = time_to_hours(spot["close_time"])
                if not (o <= t and t + VISIT_DURATION <= c and t + VISIT_DURATION <= end_time):
                    valid = False
                    break
                t += VISIT_DURATION
            if valid and len(perm) > best_count:
                best_perm, best_count, best_cost = list(perm), len(perm), cost

    return best_perm, best_cost, best_count * VISIT_DURATION

# ─────────────────── MAIN APP ─────────────────────────
class TouristApp:
    def __init__(self, root):
        root.title("Tourist Spot Optimizer – Kathmandu")
        root.configure(bg=BG)
        root.resizable(True, True)

        # ── Full-window scrollable container ──────────
        main_canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
        main_canvas.grid(row=0, column=0, sticky="nsew")
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        v_scroll = tk.Scrollbar(root, orient="vertical",
                                command=main_canvas.yview, bg=PANEL)
        v_scroll.grid(row=0, column=1, sticky="ns")
        main_canvas.configure(yscrollcommand=v_scroll.set)

        # Inner frame holds ALL content
        inner = tk.Frame(main_canvas, bg=BG)
        inner_window = main_canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_configure(e):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        inner.bind("<Configure>", _on_inner_configure)

        def _on_canvas_resize(e):
            main_canvas.itemconfig(inner_window, width=e.width)
        main_canvas.bind("<Configure>", _on_canvas_resize)

        # Mouse wheel scrolling
        def _on_mousewheel(e):
            main_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Now use 'inner' as the parent for all widgets (replaces 'root')
        root = inner

        # ── Input panel ───────────────────────────────
        inp = tk.Frame(root, bg=PANEL, padx=14, pady=12)
        inp.grid(row=0, column=0, columnspan=2, padx=14, pady=(12, 4), sticky="ew")
        tk.Label(inp, text="USER PREFERENCES", bg=PANEL, fg=ACCENT,
                 font=("Helvetica", 11, "bold")).grid(
                 row=0, column=0, columnspan=8, sticky="w", pady=(0, 8))

        fields = [("Max Budget (Rs):", "1000"), ("Start Time (HH:MM):", "09:00"), ("End Time (HH:MM):", "17:00")]
        self.entries = []
        for i, (lbl, val) in enumerate(fields):
            tk.Label(inp, text=lbl, bg=PANEL, fg=FG,
                     font=("Helvetica", 10)).grid(row=1, column=i*2, sticky="e", padx=(10, 4))
            e = tk.Entry(inp, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG,
                         relief="flat", bd=4, width=12, font=("Helvetica", 10))
            e.insert(0, val)
            e.grid(row=1, column=i*2+1, padx=(0, 14))
            self.entries.append(e)
        self.budget_entry, self.start_entry, self.end_entry = self.entries

        tk.Label(inp, text="Available Hours:", bg=PANEL, fg=FG,
                 font=("Helvetica", 10)).grid(row=2, column=0, sticky="e", padx=(10, 4), pady=(8, 0))
        self.hours_label = tk.Label(inp, text="—", bg=PANEL, fg=GREEN,
                                    font=("Helvetica", 10, "bold"))
        self.hours_label.grid(row=2, column=1, sticky="w", pady=(8, 0))
        tk.Button(inp, text="Calc Hours", command=self.update_hours,
                  bg=ACCENT, fg="#000000", relief="flat", padx=8,
                  font=("Helvetica", 9, "bold")).grid(row=2, column=2, sticky="w", pady=(8, 0))

        # ── Interests panel ───────────────────────────
        int_frame = tk.Frame(root, bg=PANEL, padx=14, pady=10)
        int_frame.grid(row=1, column=0, columnspan=2, padx=14, pady=4, sticky="ew")

        tk.Label(int_frame, text="INTERESTS  (select any)", bg=PANEL, fg=ACCENT,
                 font=("Helvetica", 11, "bold")).grid(
                 row=0, column=0, columnspan=7, sticky="w", pady=(0, 6))

        self.interests = {
            "culture": tk.BooleanVar(), "nature": tk.BooleanVar(),
            "adventure": tk.BooleanVar(), "heritage": tk.BooleanVar(),
            "religious": tk.BooleanVar(), "relaxation": tk.BooleanVar(),
        }
        for col, (tag, var) in enumerate(self.interests.items()):
            tk.Checkbutton(int_frame, text=tag.capitalize(), variable=var,
                           bg=PANEL, fg=FG, selectcolor=ENTRY_BG,
                           activebackground=PANEL, activeforeground=FG,
                           font=("Helvetica", 10)).grid(row=1, column=col, padx=10)

        # ── Run button ────────────────────────────────
        tk.Button(root, text="▶   Generate Itinerary", command=self.run,
                  bg=GREEN, fg="#000000", font=("Helvetica", 12, "bold"),
                  relief="flat", padx=20, pady=6).grid(row=2, column=0, columnspan=2, pady=10)

        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)

        # ── Output text (full width, no scroll, auto height) ──
        self.output = tk.Text(root, height=32, width=100,
                              bg=ENTRY_BG, fg=ENTRY_FG,
                              font=("Courier New", 9),
                              insertbackground=ENTRY_FG,
                              relief="flat", bd=6,
                              selectbackground=ACCENT,
                              wrap="none")
        self.output.grid(row=3, column=0, columnspan=2, padx=14, pady=(4, 2), sticky="ew")

        # ── Map image directly in inner frame ────────
        self.image_label = tk.Label(root, bg=BG)
        self.image_label.grid(row=4, column=0, columnspan=2, padx=14, pady=(2, 20), sticky="ew")

    # ── Helpers ───────────────────────────────────────
    def update_hours(self):
        try:
            s = time_to_hours(self.start_entry.get())
            e = time_to_hours(self.end_entry.get())
            self.hours_label.config(text=f"{e - s:.1f} hrs")
        except ValueError:
            self.hours_label.config(text="Invalid")

    # ── Main run ──────────────────────────────────────
    def run(self):
        try:
            budget     = int(self.budget_entry.get())
            start_time = time_to_hours(self.start_entry.get())
            end_time   = time_to_hours(self.end_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Enter valid numbers and HH:MM times.")
            return

        if end_time <= start_time:
            messagebox.showerror("Time Error", "End time must be after start time.")
            return

        self.hours_label.config(text=f"{end_time - start_time:.1f} hrs")
        interests = {k for k, v in self.interests.items() if v.get()}

        h_spots, h_sched, h_expl, h_cost, h_time = greedy_itinerary(
            budget, interests, start_time, end_time)
        bf_spots, bf_cost, bf_time = brute_force_itinerary(budget, start_time, end_time)

        # ── Render output ─────────────────────────────
        self.output.delete("1.0", tk.END)
        W = 100

        def line(txt=""): self.output.insert(tk.END, txt + "\n")
        def sep():        line("─" * W)

        line("  HEURISTIC (Greedy) ITINERARY")
        sep()
        if h_spots:
            for spot, arr in h_sched:
                line(f"  {hours_to_hhmm(arr)} → {hours_to_hhmm(arr + VISIT_DURATION)}"
                     f"   {spot['name']:<32}  Rs.{spot['fee']}")
            line()
            line(f"  Spots: {len(h_spots)}   |   Cost: Rs.{h_cost}   |   Time: {h_time} hr(s)")
        else:
            line("  No spots could be scheduled with these constraints.")

        line()
        line("  DECISION EXPLANATION")
        sep()
        for e in h_expl:
            line(e)

        line()
        line("  BRUTE-FORCE OPTIMAL RESULT")
        sep()
        if bf_spots:
            t = start_time
            for spot in bf_spots:
                line(f"  {hours_to_hhmm(t)} → {hours_to_hhmm(t + VISIT_DURATION)}"
                     f"   {spot['name']:<32}  Rs.{spot['fee']}")
                t += VISIT_DURATION
            line()
            line(f"  Spots: {len(bf_spots)}   |   Cost: Rs.{bf_cost}   |   Time: {bf_time} hr(s)")
        else:
            line("  No valid itinerary found.")

        line()
        line("  COMPARISON: HEURISTIC  vs  BRUTE FORCE")
        sep()
        line(f"  {'Metric':<24} {'Heuristic':>14} {'Brute Force':>14}")
        line(f"  {'─'*24} {'─'*14} {'─'*14}")
        line(f"  {'Spots Visited':<24} {len(h_spots):>14} {len(bf_spots):>14}")
        line(f"  {'Total Cost (Rs.)':<24} {h_cost:>14} {bf_cost:>14}")
        line(f"  {'Total Time (hrs)':<24} {h_time:>14} {bf_time:>14}")
        if bf_spots:
            acc = round(len(h_spots) / len(bf_spots) * 100, 1)
            line()
            line(f"  Heuristic accuracy: {acc}% of brute-force spots.")
            line("  Trade-off: Greedy is O(n^2) vs Brute Force O(n!) — much faster on large datasets.")

        self.plot_path(h_spots, bf_spots)

    # ── Map ───────────────────────────────────────────
    def plot_path(self, h_path, bf_path):
        fig, axes = plt.subplots(1, 2, figsize=(13, 5), facecolor="#1e1e2e")
        fig.suptitle("Itinerary Path Comparison", color="white", fontsize=13, fontweight="bold")

        for ax, path, title, color in [
            (axes[0], h_path,  "Heuristic (Greedy)", "#7c9ef5"),
            (axes[1], bf_path, "Brute Force Optimal", "#f5887c"),
        ]:
            ax.set_facecolor("#12121e")
            ax.tick_params(colors="white")
            for spine in ax.spines.values():
                spine.set_edgecolor("#44445a")

            if path:
                x = [p["lon"] for p in path]
                y = [p["lat"] for p in path]
                ax.plot(x, y, marker="o", linestyle="-", color=color, linewidth=2, markersize=9)
                for i, p in enumerate(path):
                    ax.annotate(f"{i+1}. {p['name']}", (p["lon"], p["lat"]),
                                textcoords="offset points", xytext=(6, 4),
                                fontsize=7, color="white")
            else:
                ax.text(0.5, 0.5, "No path", ha="center", va="center",
                        transform=ax.transAxes, color="gray", fontsize=12)

            ax.set_title(title, color=color, fontweight="bold")
            ax.set_xlabel("Longitude", color="white")
            ax.set_ylabel("Latitude", color="white")
            ax.grid(True, linestyle="--", alpha=0.3, color="#44445a")

        plt.tight_layout()
        plt.savefig("tourist_path.png", dpi=100, facecolor=fig.get_facecolor())
        plt.close()

        img = Image.open("tourist_path.png").resize((1100, 500), Image.LANCZOS)
        self.imgtk = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.imgtk, width=1100, height=500)
        self.image_label.image = self.imgtk

# ─────────────────── MAIN ─────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    TouristApp(root)
    root.mainloop()