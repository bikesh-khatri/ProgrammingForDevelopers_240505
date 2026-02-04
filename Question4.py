from dataclasses import dataclass
from collections import defaultdict


# TASK 1: MODEL THE INPUT DATA (2 Marks)


@dataclass
class EnergySource:
    id: str
    type: str
    capacity: int          # Max kWh per hour
    start_hour: int
    end_hour: int
    cost: float            # Rs per kWh

    # Check source availability for a given hour
    def is_available(self, hour: int) -> bool:
        return self.start_hour <= hour <= self.end_hour


# Hourly demand for each district (kWh)
hourly_demand = {
    6: {"A": 20, "B": 15, "C": 25},
    7: {"A": 22, "B": 16, "C": 28}
}

# Energy source definitions
sources = [
    EnergySource("S1", "Solar", 50, 6, 18, 1.0),
    EnergySource("S2", "Hydro", 40, 0, 24, 1.5),
    EnergySource("S3", "Diesel", 60, 17, 23, 3.0)
]


# TASK 4: HANDLE APPROXIMATE DEMAND (±10%) (3 Marks)


def within_tolerance(supplied, required):
    return 0.9 * required <= supplied <= 1.1 * required


results = {}                 # Stores final allocation per hour
total_cost = 0               # Total cost (Task 6)
total_energy = 0             # Total supplied energy
renewable_energy = 0         # Solar + Hydro usage
diesel_usage = []            # Diesel usage log (Task 6)

for hour, districts in hourly_demand.items():

    #  Task 2: DP-style feasibility setup 
    total_demand = sum(districts.values())
    remaining = total_demand

    # Identify available sources for this hour
    available_sources = [s for s in sources if s.is_available(hour)]

    #Task 3: Greedy Strategy

    available_sources.sort(key=lambda s: s.cost)

    allocation = defaultdict(int)

    for src in available_sources:
        if remaining <= 0:
            break

        # Allocate energy without exceeding capacity
        used = min(src.capacity, remaining)
        allocation[src.type] += used
        remaining -= used

        # Cost and energy accounting (Task 6)
        total_cost += used * src.cost
        total_energy += used

        if src.type in ["Solar", "Hydro"]:
            renewable_energy += used

        if src.type == "Diesel" and used > 0:
            diesel_usage.append((hour, used))

    supplied = total_demand - remaining

    # ---- Task 4: ±10% Demand Validation ----
    if not within_tolerance(supplied, total_demand):
        print(f"⚠ Hour {hour}: Demand not met within ±10%")

    # ---- Task 5: Store results for output table ----
    results[hour] = {
        "Demand": total_demand,
        "Supplied": supplied,
        "Allocation": dict(allocation)
    }


# TASK 5: DISPLAY OUTPUT TABLE 


print("\nENERGY DISTRIBUTION RESULT\n")
print("Hour | Solar | Hydro | Diesel | Demand | Supplied | %Fulfilled")
print("--------------------------------------------------------------")

for hour, data in results.items():
    solar = data["Allocation"].get("Solar", 0)
    hydro = data["Allocation"].get("Hydro", 0)
    diesel = data["Allocation"].get("Diesel", 0)
    demand = data["Demand"]
    supplied = data["Supplied"]
    percent = round((supplied / demand) * 100, 2)

    print(f"{hour:>4} | {solar:>5} | {hydro:>5} | {diesel:>6} |"
          f" {demand:>6} | {supplied:>8} | {percent:>10}%")

# TASK 6: ANALYZE COST & RESOURCE USAGE 

renewable_percent = round((renewable_energy / total_energy) * 100, 2)

print("\nANALYSIS\n")
print(f"Total Cost: Rs. {total_cost}")
print(f"Total Energy Supplied: {total_energy} kWh")
print(f"Renewable Energy Usage: {renewable_percent}%")

if diesel_usage:
    print("Diesel used in the following hours:")
    for h, amt in diesel_usage:
        print(f"  Hour {h}: {amt} kWh (high demand or solar unavailable)")
else:
    print("Diesel was not used.")







total_cost = 0
total_energy = 0
renewable_energy = 0
diesel_usage = []

for hour, data in results.items():
    for src in sources:
        used = data["Allocation"].get(src.type, 0)
        total_cost += used * src.cost
        total_energy += used

        if src.type in ["Solar", "Hydro"]:
            renewable_energy += used

        if src.type == "Diesel" and used > 0:
            diesel_usage.append((hour, used))

renewable_percent = round((renewable_energy / total_energy) * 100, 2)

print("Total Cost:", total_cost)
print("Renewable Energy %:", renewable_percent)

if diesel_usage:
    print("Diesel used in hours:", diesel_usage)
else:
    print("No diesel usage")
