import React from 'react';

function HoldingsTable({ holdings, onEdit, onDelete }) {
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

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (holdings.length === 0) {
    return (
      <div className="empty-state">
        <h3>No holdings yet</h3>
        <p>Add your first precious metal holding to get started</p>
      </div>
    );
  }

  return (
    <table className="holdings-table">
      <thead>
        <tr>
          <th>Product</th>
          <th>Metal</th>
          <th>Qty</th>
          <th>Weight (oz)</th>
          <th>Purchase Date</th>
          <th>Cost Basis</th>
          <th>Current Value</th>
          <th>P/L</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {holdings.map((holding) => (
          <tr key={holding.id}>
            <td>{holding.product?.name}</td>
            <td>
              <span className={`metal-badge ${holding.product?.metal?.symbol}`}>
                {holding.product?.metal?.name}
              </span>
            </td>
            <td>{holding.quantity}</td>
            <td>{holding.total_weight_oz.toFixed(3)}</td>
            <td>{formatDate(holding.purchase_date)}</td>
            <td>{formatCurrency(holding.total_cost)}</td>
            <td>{formatCurrency(holding.current_value)}</td>
            <td className={holding.profit_loss >= 0 ? 'positive' : 'negative'}>
              {formatCurrency(holding.profit_loss)}
              <br />
              <small>{formatPercent(holding.profit_loss_percent)}</small>
            </td>
            <td>
              <div className="actions">
                <button
                  className="btn btn-secondary"
                  onClick={() => onEdit(holding)}
                >
                  Edit
                </button>
                <button
                  className="btn btn-danger"
                  onClick={() => onDelete(holding.id)}
                >
                  Delete
                </button>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default HoldingsTable;
