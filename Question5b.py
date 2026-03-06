
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import time
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageTk


API_KEY = "fb9624ee51c4809a9be17ddcc6e9501a"   


BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Five Nepali cities to query
CITIES = ["Kathmandu", "Pokhara", "Biratnagar", "Nepalgunj", "Dhangadhi"]

# ── Colour palette (dark theme) ───────────────────────────────
BG       = "#1e1e2e"
PANEL    = "#2a2a3e"
FG       = "#e0e0f0"
ACCENT   = "#7c9ef5"
GREEN    = "#3ddc84"
RED      = "#f5887c"
YELLOW   = "#f9e04b"
ENTRY_BG = "#12121e"
ENTRY_FG = "#ffffff"


# ─────────────────────────────────────────────────────────────
#  WEATHER FETCH FUNCTION  (used by both sequential & threads)
# ─────────────────────────────────────────────────────────────
def fetch_weather(city: str) -> dict:
    """
    Call the OpenWeatherMap current-weather endpoint for one city.
    Returns a dict with city, temperature, humidity, pressure, or
    an error string if the request fails.
    """
    try:
        # Add country code NP to avoid city name ambiguity
        params = {"q": f"{city},NP", "appid": API_KEY, "units": "metric"}
        response = requests.get(BASE_URL, params=params, timeout=10)

        # Manually check status for better error messages
        if response.status_code == 401:
            return {"city": city, "temp": "—", "humidity": "—",
                    "pressure": "—", "error": "401: Invalid API key"}
        if response.status_code == 404:
            return {"city": city, "temp": "—", "humidity": "—",
                    "pressure": "—", "error": "404: City not found"}
        if response.status_code != 200:
            return {"city": city, "temp": "—", "humidity": "—",
                    "pressure": "—", "error": f"HTTP {response.status_code}"}

        data = response.json()
        return {
            "city":     city,
            "temp":     data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "error":    None,
        }
    except requests.exceptions.ConnectionError:
        return {"city": city, "temp": "—", "humidity": "—",
                "pressure": "—", "error": "No internet"}
    except requests.exceptions.Timeout:
        return {"city": city, "temp": "—", "humidity": "—",
                "pressure": "—", "error": "Timeout"}
    except Exception as e:
        return {"city": city, "temp": "—", "humidity": "—",
                "pressure": "—", "error": str(e)[:20]}


# ─────────────────────────────────────────────────────────────
#  SEQUENTIAL FETCH  – one city at a time
# ─────────────────────────────────────────────────────────────
def fetch_sequential(cities: list) -> tuple[list, float]:
    """
    Fetch weather for each city one after another.
    Returns (results_list, elapsed_seconds).
    """
    start = time.time()
    results = [fetch_weather(city) for city in cities]
    elapsed = time.time() - start
    return results, elapsed


# ─────────────────────────────────────────────────────────────
#  WORKER THREAD  – fetches one city and puts result in queue
# ─────────────────────────────────────────────────────────────
def thread_worker(city: str, result_queue: queue.Queue):
    """
    Run in a separate thread.
    Fetches weather for `city` and posts the result dict to
    the thread-safe queue so the GUI thread can read it.
    """
    result = fetch_weather(city)
    result_queue.put(result)   # thread-safe put


# ─────────────────────────────────────────────────────────────
#  MULTITHREADED FETCH  – one thread per city, all in parallel
# ─────────────────────────────────────────────────────────────
def fetch_multithreaded(cities: list) -> tuple[list, float]:
    """
    Spawn one daemon thread per city.
    Collect all results from the shared queue.
    Returns (results_list, elapsed_seconds).
    """
    result_queue = queue.Queue()   # thread-safe FIFO queue
    threads = []

    start = time.time()

    # Create and start one thread for each city
    for city in cities:
        t = threading.Thread(
            target=thread_worker,
            args=(city, result_queue),
            daemon=True            # dies automatically if main program exits
        )
        threads.append(t)
        t.start()

    # Wait for every thread to finish
    for t in threads:
        t.join()

    elapsed = time.time() - start

    # Drain the queue into a list (order may differ from input)
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    return results, elapsed


# ─────────────────────────────────────────────────────────────
#  BAR CHART  – sequential vs multithreaded time comparison
# ─────────────────────────────────────────────────────────────
def build_chart(seq_time: float, mt_time: float) -> Image.Image:
    """
    Draw a dark-themed bar chart comparing the two execution times.
    Returns a PIL Image object.
    """
    fig, ax = plt.subplots(figsize=(5, 3.6), facecolor=PANEL)
    ax.set_facecolor(ENTRY_BG)

    labels = ["Sequential", "Multithreaded"]
    values = [seq_time, mt_time]
    colors = ["#f5887c", "#3ddc84"]

    bars = ax.bar(labels, values, color=colors, width=0.45,
                  edgecolor="#44445a", linewidth=1.2)

    # Value labels on top of bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.02,
                f"{val:.2f}s",
                ha="center", va="bottom",
                color=ENTRY_FG, fontsize=11, fontweight="bold")

    speedup = seq_time / mt_time if mt_time > 0 else 0
    ax.set_title(f"Execution Time Comparison  (speedup: {speedup:.1f}×)",
                 color=FG, fontsize=10, fontweight="bold", pad=10)
    ax.set_ylabel("Time (seconds)", color=FG, fontsize=9)
    ax.tick_params(colors=FG, labelsize=10)
    for spine in ax.spines.values():
        spine.set_edgecolor("#44445a")
    ax.yaxis.label.set_color(FG)
    ax.set_ylim(0, max(values) * 1.35)
    ax.grid(axis="y", linestyle="--", alpha=0.25, color="#7c9ef5")

    plt.tight_layout()
    path = "/tmp/weather_chart.png"
    plt.savefig(path, dpi=110, facecolor=fig.get_facecolor())
    plt.close()
    return Image.open(path)


# ─────────────────────────────────────────────────────────────
#  MAIN GUI APPLICATION
# ─────────────────────────────────────────────────────────────
class WeatherApp:
    def __init__(self, root: tk.Tk):
        root.title("Multi-threaded Weather Data Collector")
        root.configure(bg=BG)
        root.resizable(True, True)

        self._build_header(root)
        self._build_table(root)
        self._build_stats(root)
        self._build_chart_area(root)
        self._build_footer(root)

    # ── Header ────────────────────────────────────────────────
    def _build_header(self, root):
        hdr = tk.Frame(root, bg=PANEL, pady=14)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(12, 4))

        tk.Label(hdr, text="🌤  Multi-threaded Weather Data Collector",
                 bg=PANEL, fg=ACCENT, font=("Helvetica", 15, "bold")).pack(side="left", padx=14)

        # API key status indicator
        self.key_status = tk.Label(hdr, text="● API key not set", bg=PANEL,
                                   fg=RED, font=("Helvetica", 9))
        self.key_status.pack(side="right", padx=14)
        if API_KEY and API_KEY != "your_api_key_here":
            self.key_status.config(text="● API key set", fg=GREEN)

        tk.Button(hdr, text="▶  Fetch Weather", command=self._on_fetch,
                  bg=GREEN, fg="#000000", font=("Helvetica", 11, "bold"),
                  relief="flat", padx=16, pady=5).pack(side="right", padx=8)

    # ── Data table ────────────────────────────────────────────
    def _build_table(self, root):
        tbl_frame = tk.Frame(root, bg=PANEL, padx=12, pady=10)
        tbl_frame.grid(row=1, column=0, padx=14, pady=6, sticky="nsew")

        tk.Label(tbl_frame, text="WEATHER DATA", bg=PANEL, fg=ACCENT,
                 font=("Helvetica", 10, "bold")).grid(
                 row=0, column=0, sticky="w", pady=(0, 6))

        # Treeview styled table
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Custom.Treeview",
                         background=ENTRY_BG, foreground=ENTRY_FG,
                         fieldbackground=ENTRY_BG, rowheight=28,
                         font=("Helvetica", 10))
        style.configure("Custom.Treeview.Heading",
                         background=PANEL, foreground=ACCENT,
                         font=("Helvetica", 10, "bold"), relief="flat")
        style.map("Custom.Treeview",
                  background=[("selected", "#3a3a5a")],
                  foreground=[("selected", ENTRY_FG)])

        cols = ("City", "Temperature (°C)", "Humidity (%)", "Pressure (hPa)", "Status")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                                 height=6, style="Custom.Treeview")

        col_widths = [140, 150, 130, 150, 120]
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        self.tree.grid(row=1, column=0, sticky="ew")

        # Alternate row colours
        self.tree.tag_configure("odd",  background="#1a1a2e", foreground=ENTRY_FG)
        self.tree.tag_configure("even", background=ENTRY_BG,  foreground=ENTRY_FG)
        self.tree.tag_configure("err",  background="#3a1a1a", foreground=RED)

        # Pre-fill rows with placeholders
        for i, city in enumerate(CITIES):
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", iid=city,
                             values=(city, "—", "—", "—", "waiting..."),
                             tags=(tag,))

    # ── Timing stats ──────────────────────────────────────────
    def _build_stats(self, root):
        stats = tk.Frame(root, bg=PANEL, padx=12, pady=10)
        stats.grid(row=2, column=0, padx=14, pady=4, sticky="ew")

        tk.Label(stats, text="EXECUTION TIMES", bg=PANEL, fg=ACCENT,
                 font=("Helvetica", 10, "bold")).grid(
                 row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))

        # Sequential time
        tk.Label(stats, text="Sequential:", bg=PANEL, fg=FG,
                 font=("Helvetica", 10)).grid(row=1, column=0, sticky="e", padx=(0, 6))
        self.seq_label = tk.Label(stats, text="— s", bg=PANEL, fg=RED,
                                  font=("Helvetica", 11, "bold"), width=10)
        self.seq_label.grid(row=1, column=1, sticky="w")

        # Multithreaded time
        tk.Label(stats, text="Multithreaded:", bg=PANEL, fg=FG,
                 font=("Helvetica", 10)).grid(row=1, column=2, sticky="e", padx=(20, 6))
        self.mt_label = tk.Label(stats, text="— s", bg=PANEL, fg=GREEN,
                                 font=("Helvetica", 11, "bold"), width=10)
        self.mt_label.grid(row=1, column=3, sticky="w")

        # Speedup label
        tk.Label(stats, text="Speedup:", bg=PANEL, fg=FG,
                 font=("Helvetica", 10)).grid(row=1, column=4, sticky="e", padx=(20, 6))
        self.speedup_label = tk.Label(stats, text="—×", bg=PANEL, fg=YELLOW,
                                      font=("Helvetica", 11, "bold"), width=8)
        self.speedup_label.grid(row=1, column=5, sticky="w")

        # Status bar
        self.status_var = tk.StringVar(value="Ready. Click 'Fetch Weather' to start.")
        tk.Label(stats, textvariable=self.status_var, bg=PANEL, fg=FG,
                 font=("Helvetica", 9, "italic")).grid(
                 row=2, column=0, columnspan=6, sticky="w", pady=(8, 0))

    # ── Chart placeholder ─────────────────────────────────────
    def _build_chart_area(self, root):
        self.chart_label = tk.Label(root, bg=ENTRY_BG,
                                    text="Chart will appear here after fetching data.",
                                    fg="#555577", font=("Helvetica", 10, "italic"),
                                    width=54, height=16)
        self.chart_label.grid(row=1, column=1, rowspan=2, padx=(4, 14), pady=6, sticky="nsew")
        root.columnconfigure(1, weight=1)

    # ── Footer ────────────────────────────────────────────────
    def _build_footer(self, root):
        tk.Label(root,
                 text="Each thread fetches one city in parallel  •  Results collected via thread-safe Queue  •  GUI stays responsive via threading",
                 bg=BG, fg="#555577", font=("Helvetica", 8)).grid(
                 row=3, column=0, columnspan=2, pady=(2, 10))

    # ─────────────────────────────────────────────────────────
    #  FETCH HANDLER  – runs in a background thread so GUI
    #  never freezes while HTTP requests are in flight
    # ─────────────────────────────────────────────────────────
    def _on_fetch(self):
        if API_KEY == "your_api_key_here" or not API_KEY:
            messagebox.showerror(
                "API Key Missing",
                "Please open weather_collector.py and replace\n"
                "  API_KEY = \"your_api_key_here\"\n"
                "with your actual OpenWeatherMap API key."
            )
            return

        # Disable button while fetching to prevent double-clicks
        self._set_button_state("disabled")
        self.status_var.set("⏳  Fetching data — please wait…")
        self._clear_table()

        # Run the heavy work in a background thread so Tkinter
        # event loop (GUI) remains fully responsive
        threading.Thread(target=self._fetch_worker, daemon=True).start()

    def _fetch_worker(self):
        """
        Background thread: runs sequential then multithreaded fetch,
        then schedules GUI updates back on the main thread via after().
        """
        # ── 1. Sequential fetch ───────────────────────────────
        self._gui(self.status_var.set, "⏳  Running sequential fetch…")
        seq_results, seq_time = fetch_sequential(CITIES)

        # ── 2. Multithreaded fetch ────────────────────────────
        self._gui(self.status_var.set, "⚡  Running multithreaded fetch…")
        mt_results, mt_time = fetch_multithreaded(CITIES)

        # ── 3. Push updates to GUI thread ─────────────────────
        # Use multithreaded results for the table (they are fresher
        # and demonstrate the thread architecture)
        self._gui(self._populate_table, mt_results)
        self._gui(self._update_stats, seq_time, mt_time)
        self._gui(self._update_chart, seq_time, mt_time)
        self._gui(self.status_var.set,
                  f"✅  Done.  Sequential: {seq_time:.2f}s  |  Multithreaded: {mt_time:.2f}s")
        self._gui(self._set_button_state, "normal")

    # ─────────────────────────────────────────────────────────
    #  GUI HELPERS  (must only touch widgets from main thread)
    # ─────────────────────────────────────────────────────────
    def _gui(self, fn, *args):
        """Schedule a GUI function call on the main Tkinter thread."""
        self.chart_label.after(0, fn, *args)

    def _set_button_state(self, state: str):
        # Re-find the button widget to enable/disable it
        for widget in self.chart_label.master.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, tk.Button) and "Fetch" in str(child.cget("text")):
                    child.config(state=state)

    def _clear_table(self):
        for city in CITIES:
            self.tree.item(city, values=(city, "—", "—", "—", "fetching…"))

    def _populate_table(self, results: list):
        """Fill the Treeview with fresh weather data."""
        # Build a lookup dict so we can match by city name
        lookup = {r["city"]: r for r in results}
        for i, city in enumerate(CITIES):
            r = lookup.get(city)
            if r is None:
                continue
            tag = "err" if r["error"] else ("odd" if i % 2 else "even")
            status = r["error"] if r["error"] else "✓ OK"
            temp = f"{r['temp']:.1f}" if isinstance(r["temp"], float) else r["temp"]
            self.tree.item(city, values=(city, temp, r["humidity"], r["pressure"], status),
                           tags=(tag,))

    def _update_stats(self, seq_time: float, mt_time: float):
        """Update the timing labels."""
        self.seq_label.config(text=f"{seq_time:.3f} s")
        self.mt_label.config(text=f"{mt_time:.3f} s")
        speedup = seq_time / mt_time if mt_time > 0 else 0
        self.speedup_label.config(text=f"{speedup:.1f}×")

    def _update_chart(self, seq_time: float, mt_time: float):
        """Render the bar chart and display it in the right panel."""
        img = build_chart(seq_time, mt_time)
        img = img.resize((520, 370), Image.LANCZOS)
        self.chart_photo = ImageTk.PhotoImage(img)
        self.chart_label.config(image=self.chart_photo, text="",
                                 bg=PANEL, width=520, height=370)
        self.chart_label.image = self.chart_photo


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()