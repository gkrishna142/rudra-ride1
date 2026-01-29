import React, { useState } from 'react';
import { FiSearch, FiDownload } from 'react-icons/fi';
import { usePermissions } from '../hooks/usePermissions';
import './Payments.css';

const Payments = () => {
  const { hasPermission } = usePermissions();
  const [filter, setFilter] = useState('all');

  const transactions = [
    { id: 'T001', type: 'Ride Payment', customer: 'John Doe', amount: '₹450', method: 'Online', date: '2024-01-15 10:30', status: 'completed' },
    { id: 'T002', type: 'Driver Payout', driver: 'Raj Kumar', amount: '₹380', method: 'Bank Transfer', date: '2024-01-15 09:15', status: 'completed' },
    { id: 'T003', type: 'Refund', customer: 'Jane Smith', amount: '₹320', method: 'Online', date: '2024-01-15 08:00', status: 'pending' },
    { id: 'T004', type: 'Ride Payment', customer: 'Mike Johnson', amount: '₹280', method: 'Cash', date: '2024-01-14 18:30', status: 'completed' },
  ];

  const stats = [
    { label: 'Total Revenue (Today)', value: '₹1,23,456', color: '#10b981' },
    { label: 'Online Payments', value: '₹98,765', color: '#3b82f6' },
    { label: 'Cash Payments', value: '₹24,691', color: '#f59e0b' },
    { label: 'Driver Payouts', value: '₹87,234', color: '#8b5cf6' },
    { label: 'Refunds', value: '₹1,230', color: '#ef4444' },
  ];

  return (
    <div className="payments">
      <div className="page-header">
        <h1>Payments & Transactions</h1>
        <button className="btn-primary">
          <FiDownload /> Export Report
        </button>
      </div>

      <div className="payment-stats">
        {stats.map((stat, index) => (
          <div key={index} className="payment-stat-card">
            <p className="stat-label">{stat.label}</p>
            <h3 style={{ color: stat.color }}>{stat.value}</h3>
          </div>
        ))}
      </div>

      <div className="filters-section">
        <div className="search-box">
          <FiSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search transactions..."
          />
        </div>
        <div className="filter-buttons">
          <button 
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button 
            className={filter === 'payments' ? 'active' : ''}
            onClick={() => setFilter('payments')}
          >
            Payments
          </button>
          <button 
            className={filter === 'payouts' ? 'active' : ''}
            onClick={() => setFilter('payouts')}
          >
            Payouts
          </button>
          <button 
            className={filter === 'refunds' ? 'active' : ''}
            onClick={() => setFilter('refunds')}
          >
            Refunds
          </button>
        </div>
      </div>

      <div className="transactions-table-container">
        <table className="transactions-table">
          <thead>
            <tr>
              <th>Transaction ID</th>
              <th>Type</th>
              <th>User</th>
              <th>Amount</th>
              <th>Payment Method</th>
              <th>Date & Time</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((transaction) => (
              <tr key={transaction.id}>
                <td><strong>{transaction.id}</strong></td>
                <td>{transaction.type}</td>
                <td>{transaction.customer || transaction.driver}</td>
                <td><strong>{transaction.amount}</strong></td>
                <td>{transaction.method}</td>
                <td>{transaction.date}</td>
                <td>
                  <span className={`status-badge ${transaction.status === 'completed' ? 'status-completed' : 'status-pending'}`}>
                    {transaction.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Payments;

