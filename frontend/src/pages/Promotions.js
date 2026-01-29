import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { FiPlus, FiEdit, FiTrash2, FiTag } from 'react-icons/fi';
import { usePermissions } from '../hooks/usePermissions';
import './Promotions.css';

const Promotions = () => {
  const { canCreate, canEdit, canDelete } = usePermissions();
  const [showModal, setShowModal] = useState(false);
  const [promotions, setPromotions] = useState([]);
  const [formData, setFormData] = useState({
    code: '',
    discount_type: 'percentage',
    discount_value: '',
    start_date: '',
    expire_date: '',
    max_usage: 1,
    status: 'active'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

 const fetchPromotions = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/auth/promo-codes/');
    setPromotions(Array.isArray(response.data.data) ? response.data.data : []);
  } catch (error) {
    console.error('Failed to fetch promotions:', error);
  }
 };
 
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));
  };
 


  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Convert form data to match API expectations
      const submitData = {
        ...formData,
        code: formData.code.toUpperCase(),
        discount_type: formData.discount_type === 'Fixed Amount' ? 'fixed' : 'percentage',
        discount_value: parseFloat(formData.discount_value),
        max_usage: parseInt(formData.max_usage) || 1,
        start_date: formData.start_date ? new Date(formData.start_date).toISOString() : new Date().toISOString(),
        expire_date: new Date(formData.expire_date).toISOString()
      };

      const response = await axios.post('http://127.0.0.1:8000/api/auth/promo-codes/create/', submitData);
      
      if (response.data.message_type === 'success') {
        // Refresh the promotions list
        await fetchPromotions();
        // Reset form and close modal
        setFormData({
          code: '',
          discount_type: 'percentage',
          discount_value: '',
          start_date: '',
          expire_date: '',
          max_usage: 1,
          status: 'active'
        });
        setShowModal(false);
        alert('Promo code created successfully!');
      } else {
        alert('Error creating promo code: ' + JSON.stringify(response.data.errors));
      }
    } catch (error) {
      console.error('Error creating promo code:', error);
      alert('Error creating promo code. Please check the console for details.');
    } finally {
      setIsSubmitting(false);
    }
  };
 
  useEffect(() => {
    fetchPromotions();
  }, []);
    //   maxUsage: 1000,
    //   status: 'active'
    // },
    // { 
    //   id: 'PROMO002', 
    //   code: 'SUMMER20',
    //   discount: '20%',
    //   discountType: 'Percentage',
    //   expiry: '2024-03-20',
    //   usage: 567,
    //   maxUsage: 2000,
    //   status: 'active'
    // },
    // { 
    //   id: 'PROMO003', 
    //   code: 'FIRST100',
    //   discount: '₹100',
    //   discountType: 'Fixed',
    //   expiry: '2024-01-10',
    //   usage: 890,
    //   maxUsage: 1000,
    //   status: 'expired'
    // },
    


  return (
    <div className="promotions">
      <div className="page-header">
        <h1>Promotions & Coupons</h1>
        {canCreate('/promotions') && (
          <button className="btn-primary" onClick={() => setShowModal(true)}>
            <FiPlus /> Create Promo Code
          </button>
        )}
      </div>

      <div className="promotions-grid">
        {promotions.map((promo) => (
          <div key={promo.id} className="promo-card">
            <div className="promo-header">
              <div className="promo-code-section">
                <FiTag className="promo-icon" />
                <div>
                  <h3>{promo.code}</h3>
                   <p className="promo-id">ID: {promo.id}</p> 
                </div>
              </div>
              <span className={`status-badge ${promo.status === 'active' ? 'status-active' : 'status-expired'}`}>
                {promo.status}
              </span>
            </div>

            <div className="promo-details">
              <div className="detail-item">
                <span className="detail-label">Discount:</span>
                <span className="detail-value discount">{promo.discount_value}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Type:</span>
                <span className="detail-value">{promo.discount_type}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Expiry:</span>
                <span className="detail-value">{promo.expire_date}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Usage:</span>
                <span className="detail-value">{promo.current_usage} / {promo.max_usage}</span>
              </div>
              <div className="usage-bar">
                <div 
                  className="usage-progress" 
                  style={{ width: `${(promo.current_usage / promo.max_usage) * 100}%` }}
                />
              </div>
            </div>

            <div className="promo-actions">
              {canEdit('/promotions') && (
                <button className="btn-secondary">
                  <FiEdit /> Edit
                </button>
              )}
              {canDelete('/promotions') && (
                <button className="btn-secondary btn-danger">
                  <FiTrash2 /> Delete
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Promo Code</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Promo Code</label>
                <input 
                  type="text" 
                  name="code"
                  value={formData.code}
                  onChange={handleInputChange}
                  placeholder="e.g., WELCOME50" 
                  required
                />
              </div>
              <div className="form-group">
                <label>Discount Type</label>
                <select 
                  name="discount_type"
                  value={formData.discount_type}
                  onChange={handleInputChange}
                >
                  <option value="percentage">Percentage</option>
                  <option value="fixed">Fixed Amount</option>
                </select>
              </div>
              <div className="form-group">
                <label>Discount Value</label>
                <input 
                  type="number" 
                  name="discount_value"
                  value={formData.discount_value}
                  onChange={handleInputChange}
                  placeholder="Enter amount or percentage" 
                  step="0.01"
                  min="0"
                  required
                />
              </div>
              <div className="form-group">
                <label>Start Date</label>
                <input 
                  type="datetime-local" 
                  name="start_date"
                  value={formData.start_date}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Expiry Date</label>
                <input 
                  type="datetime-local" 
                  name="expire_date"
                  value={formData.expire_date}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Max Usage</label>
                <input 
                  type="number" 
                  name="max_usage"
                  value={formData.max_usage}
                  onChange={handleInputChange}
                  placeholder="Maximum number of uses" 
                  min="1"
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)} disabled={isSubmitting}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={isSubmitting}>
                  {isSubmitting ? 'Creating...' : 'Create Promo Code'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Promotions;

