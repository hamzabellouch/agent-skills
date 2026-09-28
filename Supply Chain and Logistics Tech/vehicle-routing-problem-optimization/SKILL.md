---
name: vehicle-routing-problem-optimization
metadata:
  category: Supply Chain and Logistics Tech
description: Solve complex fleet dispatch and delivery routing challenges using Capacitated Vehicle Routing Problem with Time Windows (CVRPTW) algorithms and Google OR-Tools. Model vehicle capacities, customer service time windows, pickup-and-delivery pairs, driver shifts, and distance/duration matrices. Trigger when optimizing fleet logistics, dispatch systems, or courier delivery routes.
compatibility: Python 3.10+, Google OR-Tools 9.8+, NumPy
---

# Vehicle Routing Problem (VRP) Optimization Skill Guide

This skill standardizes mathematical modeling and programmatic resolution of delivery fleet route optimization using Google OR-Tools constraint programming.

---

## 1. CVRPTW Constraint Hierarchy

```text
[ Input Problem Data ]
  |-- Customer Coordinates & Delivery Demands (e.g. packages/weight)
  |-- Service Time Windows [Earliest Arrival, Latest Departure]
  |-- Fleet Vehicle Capacities & Maximum Shift Durations
  |-- Distance / Travel Time Matrix (from OSRM / Google Maps API)
          |
          v
[ Google OR-Tools Routing Model ]
  |-- RoutingIndexManager (Node <-> Index Mapping)
  |-- AddDimension(Distance / Capacity / Time)
  |-- AddDisjunction (Penalized Dropped Visits if overconstrained)
          |
          v (Guided Local Search / Tabu Search)
[ Optimized Multi-Vehicle Dispatch Schedules ]
```

---

## 2. Production Code Implementation (Python / OR-Tools)

```python
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def create_data_model():
    """Builds sample input data for 4 vehicles and 10 delivery locations."""
    data = {}
    # Time/distance matrix in minutes (10 locations + 1 depot at index 0)
    data["time_matrix"] = [
        [0, 12, 20, 15, 18, 25, 22, 10, 14, 16, 20],
        [12, 0, 10, 8, 15, 18, 20, 14, 16, 12, 18],
        [20, 10, 0, 12, 14, 15, 16, 18, 20, 14, 10],
        [15, 8, 12, 0, 10, 12, 14, 16, 18, 10, 15],
        [18, 15, 14, 10, 0, 8, 10, 12, 14, 16, 18],
        [25, 18, 15, 12, 8, 0, 6, 10, 12, 14, 16],
        [22, 20, 16, 14, 10, 6, 0, 8, 10, 12, 14],
        [10, 14, 18, 16, 12, 10, 8, 0, 6, 8, 10],
        [14, 16, 20, 18, 14, 12, 10, 6, 0, 5, 8],
        [16, 12, 14, 10, 16, 14, 12, 8, 5, 0, 6],
        [20, 18, 10, 15, 18, 16, 14, 10, 8, 6, 0],
    ]
    # Time windows: [earliest_start_min, latest_start_min]
    data["time_windows"] = [
        (0, 480),  # 0: Depot open 8 hours
        (30, 120), # 1
        (60, 180), # 2
        (90, 240), # 3
        (120, 300),# 4
        (150, 360),# 5
        (180, 400),# 6
        (60, 200), # 7
        (120, 300),# 8
        (180, 360),# 9
        (240, 450),# 10
    ]
    # Customer delivery demands (e.g., packages)
    data["demands"] = [0, 1, 2, 1, 3, 2, 1, 2, 1, 2, 1]
    data["vehicle_capacities"] = [8, 8, 8, 8]
    data["num_vehicles"] = 4
    data["depot"] = 0
    return data


def solve_cvrptw():
    data = create_data_model()

    # 1. Routing Index Manager
    manager = pywrapcp.RoutingIndexManager(
        len(data["time_matrix"]),
        data["num_vehicles"],
        data["depot"],
    )
    routing = pywrapcp.RoutingModel(manager)

    # 2. Transit Callback (Travel Time)
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["time_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # 3. Add Time Window Dimension
    time_dimension_name = "Time"
    routing.AddDimension(
        transit_callback_index,
        60,   # Allow waiting time up to 60 mins
        480,  # Max vehicle shift 8 hours
        False,# Don't force start cumul to zero
        time_dimension_name,
    )
    time_dimension = routing.GetDimensionOrDie(time_dimension_name)

    # Add time window constraints for each customer
    for location_idx, time_window in enumerate(data["time_windows"]):
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # 4. Add Demand / Capacity Dimension
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data["demands"][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data["vehicle_capacities"],
        True,  # start cumul to zero
        "Capacity",
    )

    # 5. Search Parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = 5

    # Solve
    solution = routing.SolveWithParameters(search_parameters)
    return solution is not None
```

---

## 3. Best Practices Checklist

- [ ] **Triangle Inequality:** Verify that the distance matrix satisfies the triangle inequality ($D(A, C) \le D(A, B) + D(B, C)$); violating this can break heuristic solvers.
- [ ] **Disjunctions for Dropped Visits:** Add `routing.AddDisjunction([manager.NodeToIndex(node)], penalty)` so the solver can drop impossible deliveries instead of returning null when overconstrained.
- [ ] **Service Duration:** Add loading/unloading buffer times at each stop into the transit callback to prevent unrealistic driver schedules.
