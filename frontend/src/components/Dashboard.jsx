import React from 'react';

function Dashboard({ summary }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatPercent = (value) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  return (
    <div className="dashboard">
      <div className="stat-card">
        <div className="label">Total Cost Basis</div>
        <div className="value">{formatCurrency(summary.total_cost)}</div>
      </div>

      <div className="stat-card">
        <div className="label">Current Value</div>
        <div className="value">{formatCurrency(summary.current_value)}</div>
      </div>

      <div className="stat-card">
        <div className="label">Total Profit/Loss</div>
        <div className={`value ${summary.total_profit_loss >= 0 ? 'positive' : 'negative'}`}>
          {formatCurrency(summary.total_profit_loss)}
        </div>
      </div>

      <div className="stat-card">
        <div className="label">Return</div>
        <div className={`value ${summary.total_profit_loss_percent >= 0 ? 'positive' : 'negative'}`}>
          {formatPercent(summary.total_profit_loss_percent)}
        </div>
      </div>

      <div className="stat-card">
        <div className="label">Holdings</div>
        <div className="value">{summary.holdings_count}</div>
      </div>
    </div>
  );
}

export default Dashboard;
