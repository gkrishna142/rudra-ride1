import React, { useState } from 'react';
import { FiSearch, FiMessageSquare, FiCheck } from 'react-icons/fi';
import { usePermissions } from '../hooks/usePermissions';
import './Complaints.css';

const Complaints = () => {
  const { hasPermission } = usePermissions();
  const [filter, setFilter] = useState('all');

  const complaints = [
    { 
      id: 'CMP001', 
      user: 'John Doe',
      userType: 'Customer',
      category: 'Ride Issue',
      issue: 'Driver took wrong route',
      status: 'open',
      date: '2024-01-15 10:30',
      priority: 'high'
    },
    { 
      id: 'CMP002', 
      user: 'Raj Kumar',
      userType: 'Driver',
      category: 'Payment Issue',
      issue: 'Payout not received',
      status: 'in-progress',
      date: '2024-01-15 09:15',
      priority: 'medium'
    },
    { 
      id: 'CMP003', 
      user: 'Jane Smith',
      userType: 'Customer',
      category: 'App Issue',
      issue: 'Unable to book ride',
      status: 'closed',
      date: '2024-01-14 18:00',
      priority: 'low'
    },
  ];

  const filteredComplaints = filter === 'all' 
    ? complaints 
    : complaints.filter(c => c.status === filter);

  const getPriorityBadge = (priority) => {
    const classes = {
      high: 'priority-high',
      medium: 'priority-medium',
      low: 'priority-low'
    };
    return classes[priority] || '';
  };

  return (
    <div className="complaints">
      <div className="page-header">
        <h1>Complaints & Support</h1>
      </div>

      <div className="filters-section">
        <div className="search-box">
          <FiSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search complaints..."
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
            className={filter === 'open' ? 'active' : ''}
            onClick={() => setFilter('open')}
          >
            Open
          </button>
          <button 
            className={filter === 'in-progress' ? 'active' : ''}
            onClick={() => setFilter('in-progress')}
          >
            In Progress
          </button>
          <button 
            className={filter === 'closed' ? 'active' : ''}
            onClick={() => setFilter('closed')}
          >
            Closed
          </button>
        </div>
      </div>

      <div className="complaints-list">
        {filteredComplaints.map((complaint) => (
          <div key={complaint.id} className="complaint-card">
            <div className="complaint-header">
              <div className="complaint-id-section">
                <h3>{complaint.id}</h3>
                <span className={`priority-badge ${getPriorityBadge(complaint.priority)}`}>
                  {complaint.priority}
                </span>
              </div>
              <span className={`status-badge ${complaint.status === 'closed' ? 'status-closed' : complaint.status === 'in-progress' ? 'status-in-progress' : 'status-open'}`}>
                {complaint.status === 'in-progress' ? 'In Progress' : complaint.status}
              </span>
            </div>

            <div className="complaint-body">
              <div className="complaint-info">
                <div className="info-item">
                  <span className="info-label">User:</span>
                  <span className="info-value">{complaint.user} ({complaint.userType})</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Category:</span>
                  <span className="info-value">{complaint.category}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Date:</span>
                  <span className="info-value">{complaint.date}</span>
                </div>
              </div>
              <div className="complaint-issue">
                <p><strong>Issue:</strong> {complaint.issue}</p>
              </div>
            </div>

            <div className="complaint-actions">
              {hasPermission('/complaints', 'reply') && (
                <button className="btn-secondary">
                  <FiMessageSquare /> Reply
                </button>
              )}
              {hasPermission('/complaints', 'resolve') && complaint.status !== 'closed' && (
                <button className="btn-secondary">
                  <FiCheck /> Mark Resolved
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Complaints;

