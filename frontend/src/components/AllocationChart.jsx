import React from 'react';

function AllocationChart({ allocation }) {
  const metals = Object.entries(allocation).sort((a, b) => b[1] - a[1]);

  if (metals.length === 0) {
    return null;
  }

  return (
    <div className="allocation-chart">
      <div className="allocation-bars">
        {metals.map(([metal, percentage]) => (
          <div className="allocation-bar" key={metal}>
            <div className="bar-label">
              <span>{metal}</span>
              <span>{percentage.toFixed(1)}%</span>
            </div>
            <div className="bar-track">
              <div
                className={`bar-fill ${metal.toLowerCase()}`}
                style={{ width: `${percentage}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AllocationChart;
