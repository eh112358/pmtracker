import React, { useState, useEffect } from 'react';

function AddHoldingModal({ products, holding, onClose, onSave }) {
  const [formData, setFormData] = useState({
    product_id: '',
    quantity: 1,
    purchase_date: new Date().toISOString().split('T')[0],
    purchase_price_per_oz: '',
    premium_paid: '',
    dealer: '',
    storage_location: '',
    notes: '',
  });

  const isEditing = !!holding;

  useEffect(() => {
    if (holding) {
      setFormData({
        product_id: holding.product_id,
        quantity: holding.quantity,
        purchase_date: holding.purchase_date,
        purchase_price_per_oz: holding.purchase_price_per_oz,
        premium_paid: holding.premium_paid || '',
        dealer: holding.dealer || '',
        storage_location: holding.storage_location || '',
        notes: holding.notes || '',
      });
    }
  }, [holding]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? (value === '' ? '' : Number(value)) : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const data = {
      ...formData,
      product_id: Number(formData.product_id),
      quantity: Number(formData.quantity),
      purchase_price_per_oz: Number(formData.purchase_price_per_oz),
      premium_paid: formData.premium_paid ? Number(formData.premium_paid) : 0,
    };

    onSave(data);
  };

  // Group products by metal
  const groupedProducts = products.reduce((acc, product) => {
    const metalName = product.metal?.name || 'Other';
    if (!acc[metalName]) {
      acc[metalName] = [];
    }
    acc[metalName].push(product);
    return acc;
  }, {});

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{isEditing ? 'Edit Holding' : 'Add New Holding'}</h3>
          <button className="modal-close" onClick={onClose}>
            &times;
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label htmlFor="product_id">Product</label>
              <select
                id="product_id"
                name="product_id"
                value={formData.product_id}
                onChange={handleChange}
                required
              >
                <option value="">Select a product...</option>
                {Object.entries(groupedProducts).map(([metal, metalProducts]) => (
                  <optgroup key={metal} label={metal}>
                    {metalProducts.map((product) => (
                      <option key={product.id} value={product.id}>
                        {product.name} ({product.weight_oz} oz)
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="quantity">Quantity</label>
                <input
                  type="number"
                  id="quantity"
                  name="quantity"
                  value={formData.quantity}
                  onChange={handleChange}
                  min="1"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="purchase_date">Purchase Date</label>
                <input
                  type="date"
                  id="purchase_date"
                  name="purchase_date"
                  value={formData.purchase_date}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="purchase_price_per_oz">Price per oz ($)</label>
                <input
                  type="number"
                  id="purchase_price_per_oz"
                  name="purchase_price_per_oz"
                  value={formData.purchase_price_per_oz}
                  onChange={handleChange}
                  step="0.01"
                  min="0"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="premium_paid">Premium Paid ($)</label>
                <input
                  type="number"
                  id="premium_paid"
                  name="premium_paid"
                  value={formData.premium_paid}
                  onChange={handleChange}
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="dealer">Dealer</label>
                <input
                  type="text"
                  id="dealer"
                  name="dealer"
                  value={formData.dealer}
                  onChange={handleChange}
                  placeholder="e.g., APMEX, JM Bullion"
                />
              </div>

              <div className="form-group">
                <label htmlFor="storage_location">Storage Location</label>
                <input
                  type="text"
                  id="storage_location"
                  name="storage_location"
                  value={formData.storage_location}
                  onChange={handleChange}
                  placeholder="e.g., Home safe, Bank vault"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="notes">Notes</label>
              <textarea
                id="notes"
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                rows="3"
                placeholder="Any additional notes..."
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              {isEditing ? 'Update' : 'Add Holding'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddHoldingModal;
