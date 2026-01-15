import React, { useState, useEffect, useCallback } from 'react';
import { api } from './services/api';
import Dashboard from './components/Dashboard';
import HoldingsTable from './components/HoldingsTable';
import AddHoldingModal from './components/AddHoldingModal';
import AllocationChart from './components/AllocationChart';

function App() {
  const [prices, setPrices] = useState(null);
  const [summary, setSummary] = useState(null);
  const [holdings, setHoldings] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingHolding, setEditingHolding] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = useCallback(async (showRefreshing = false) => {
    if (showRefreshing) setRefreshing(true);
    try {
      const [pricesData, summaryData, holdingsData, productsData] = await Promise.all([
        api.getPrices(),
        api.getPortfolioSummary(),
        api.getHoldingsWithValues(),
        api.getProducts(),
      ]);

      setPrices(pricesData);
      setSummary(summaryData);
      setHoldings(holdingsData);
      setProducts(productsData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleRefreshPrices = () => {
    fetchData(true);
  };

  const handleAddHolding = async (data) => {
    try {
      await api.createHolding(data);
      setShowAddModal(false);
      fetchData();
    } catch (error) {
      console.error('Failed to add holding:', error);
      alert('Failed to add holding: ' + error.message);
    }
  };

  const handleUpdateHolding = async (data) => {
    try {
      await api.updateHolding(editingHolding.id, data);
      setEditingHolding(null);
      fetchData();
    } catch (error) {
      console.error('Failed to update holding:', error);
      alert('Failed to update holding: ' + error.message);
    }
  };

  const handleDeleteHolding = async (id) => {
    if (!window.confirm('Are you sure you want to delete this holding?')) {
      return;
    }

    try {
      await api.deleteHolding(id);
      fetchData();
    } catch (error) {
      console.error('Failed to delete holding:', error);
      alert('Failed to delete holding: ' + error.message);
    }
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="app">
      <header>
        <h1>PM Tracker</h1>
        {prices && (
          <div className="spot-prices">
            <div className="spot-price">
              <div className="metal">Gold</div>
              <div className="price">${prices.gold.toFixed(2)}</div>
            </div>
            <div className="spot-price">
              <div className="metal">Silver</div>
              <div className="price">${prices.silver.toFixed(2)}</div>
            </div>
            <div className="spot-price">
              <div className="metal">Platinum</div>
              <div className="price">${prices.platinum.toFixed(2)}</div>
            </div>
            <div className="spot-price">
              <div className="metal">Palladium</div>
              <div className="price">${prices.palladium.toFixed(2)}</div>
            </div>
            <button
              className="btn btn-refresh"
              onClick={handleRefreshPrices}
              disabled={refreshing}
            >
              {refreshing ? 'Refreshing...' : 'Refresh Prices'}
            </button>
          </div>
        )}
      </header>

      {summary && <Dashboard summary={summary} />}

      {summary && summary.holdings_count > 0 && (
        <div className="section">
          <div className="section-header">
            <h2>Allocation</h2>
          </div>
          <AllocationChart allocation={summary.allocation_by_metal} />
        </div>
      )}

      <div className="section">
        <div className="section-header">
          <h2>Holdings</h2>
          <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
            Add Holding
          </button>
        </div>
        <HoldingsTable
          holdings={holdings}
          onEdit={setEditingHolding}
          onDelete={handleDeleteHolding}
        />
      </div>

      {showAddModal && (
        <AddHoldingModal
          products={products}
          onClose={() => setShowAddModal(false)}
          onSave={handleAddHolding}
        />
      )}

      {editingHolding && (
        <AddHoldingModal
          products={products}
          holding={editingHolding}
          onClose={() => setEditingHolding(null)}
          onSave={handleUpdateHolding}
        />
      )}
    </div>
  );
}

export default App;
