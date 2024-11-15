from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Tuple
import gurobipy as gp
from gurobipy import GRB
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GRID_SIZE = 10  # 10x10 grid

class BlockedSquares(BaseModel):
    blocked: List[Tuple[int, int]]


# Function to calculate the optimal path
def solve_shortest_path(n: int, blocked: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    m = gp.Model("shortest_path")
    m.setParam("OutputFlag", 0)

    nodes = [(i, j) for i in range(n) for j in range(n)]
    edges = []
    for i in range(n):
        for j in range(n):
            if j < n - 1:
                edges.append(((i, j), (i, j + 1)))
            if i < n - 1:
                edges.append(((i, j), (i + 1, j)))
            if j > 0:
                edges.append(((i, j), (i, j - 1)))
            if i > 0:
                edges.append(((i, j), (i - 1, j)))

    edges = [e for e in edges if e[0] not in blocked and e[1] not in blocked]

    x = m.addVars(edges, vtype=GRB.BINARY, name="x")

    m.setObjective(gp.quicksum(x[e] for e in edges), GRB.MINIMIZE)

    for node in nodes:
        if node == (0, 0):
            m.addConstr(
                gp.quicksum(x[e] for e in edges if e[0] == node) -
                gp.quicksum(x[e] for e in edges if e[1] == node) == 1, f"flow_out_{node}")
        elif node == (n - 1, n - 1):
            m.addConstr(
                gp.quicksum(x[e] for e in edges if e[1] == node) -
                gp.quicksum(x[e] for e in edges if e[0] == node) == 1, f"flow_in_{node}")
        else:
            m.addConstr(
                gp.quicksum(x[e] for e in edges if e[0] == node) -
                gp.quicksum(x[e] for e in edges if e[1] == node) == 0, f"flow_{node}")

    m.optimize()

    if m.status == GRB.OPTIMAL:
        path_edges = [e for e in edges if x[e].x > 0.5]
        path = [(0, 0)]
        current = (0, 0)

        while current != (n - 1, n - 1):
            for e in path_edges:
                if e[0] == current:
                    path.append(e[1])
                    current = e[1]
                    break

        return path
    else:
        return None


@app.options("/optimal_path")
async def options_optimal_path():
    return {"detail": "OK"}


@app.post("/optimal_path")
async def get_optimal_path(data: BlockedSquares):
    blocked = [(x[0], x[1]) for x in data.blocked]
    path = solve_shortest_path(GRID_SIZE, blocked)
    if path:
        return {"path": path}
    else:
        return {"error": "No optimal path found"}


# Instructions to run the server
# Save this file as `main.py` and run:
# uvicorn main:app --reload
