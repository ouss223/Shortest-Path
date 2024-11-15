import React, { useEffect, useState } from "react";
import "./App.css";

const App = () => {
  const n = 10;
  const [button, setButton] = useState(false);

  // Initialize grid state with separate rows to avoid shared references
  const [grid, setGrid] = useState(
    Array.from({ length: n }, () => Array(n).fill(false))
  );
  const [path, setPath] = useState([]);

  // Toggle the blocked state of a grid cell
  const toggleBlock = (row, col) => {
    if ((row === 0 && col === 0) || (row === n - 1 && col === n - 1)) {
      return;
    }
    const newGrid = grid.map((r, rowIndex) =>
      rowIndex === row
        ? r.map((cell, colIndex) => {
            if (colIndex === col) {
              return !cell;
            }
            return cell;
          })
        : r
    );

    const isPath = path.some(
      ([pathRow, pathCol]) => pathRow === row && pathCol === col
    );

    if (isPath) {
      setPath([]); // Clear the path if the cell is part of the path
    }

    setGrid(newGrid); // Update the state with the new grid
    console.log(newGrid);
  };

  const getOptimalPath = () => {
    const blockedCells = [];
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (grid[i][j]) {
          blockedCells.push([i, j]);
        }
      }
    }

    fetch("http://127.0.0.1:8000/optimal_path", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ blocked: blockedCells }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Optimal path:", data.path);
        // Handle the optimal path data here
        if(data.error)
        {
          alert("No path exists");
          return
        }
        setPath(data.path);
      })
      .catch((error) => {
        console.error("Error fetching optimal path:", error);
      });
  };

  useEffect(() => {
    getOptimalPath();
  }, [button]);

  return (
    <div className="main">
      <div className="grid-container">
        {grid.map((row, rowIndex) =>
          row.map((cell, colIndex) => {
            const isPath = path.some(
              ([pathRow, pathCol]) => pathRow === rowIndex && pathCol === colIndex
            );
            return (
              <div
                key={`${rowIndex}-${colIndex}`}
                className={`grid-item ${cell ? "blocked" : ""} ${isPath ? "path" : ""}`}
                onClick={() => toggleBlock(rowIndex, colIndex)}
              />
            );
          })
        )}
      </div>
      <button className="bt" onClick={() => setButton(!button)}>
        Draw Optimal Path
      </button>

    </div>

  );
};


export default App;
