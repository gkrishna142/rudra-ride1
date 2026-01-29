import React, { useState } from 'react';
import { FiSearch, FiEye, FiX, FiCheck } from 'react-icons/fi';
import { usePermissions } from '../hooks/usePermissions';
import './CustomerManagement.css';

const CustomerManagement = () => {
  const { canEdit, canDelete, hasPermission } = usePermissions();
  const [searchTerm, setSearchTerm] = useState('');

  const customers = [
    { 
      id: 'C001', 
      name: 'John Doe', 
      email: 'john@example.com',
      phone: '+91 98765 43210', 
      totalRides: 45,
      totalSpent: '₹12,450',
      status: 'active',
      joinDate: '2023-06-15'
    },
    { 
      id: 'C002', 
      name: 'Jane Smith', 
      email: 'jane@example.com',
      phone: '+91 98765 43211', 
      totalRides: 32,
      totalSpent: '₹8,920',
      status: 'active',
      joinDate: '2023-08-20'
    },
    { 
      id: 'C003', 
      name: 'Mike Johnson', 
      email: 'mike@example.com',
      phone: '+91 98765 43212', 
      totalRides: 12,
      totalSpent: '₹3,240',
      status: 'blocked',
      joinDate: '2023-11-10'
    },
  ];

  const filteredCustomers = customers.filter(customer =>
    customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.phone.includes(searchTerm)
  );

  return (
    <div className="customer-management">
      <div className="page-header">
        <h1>Customer Management</h1>
      </div>

      <div className="filters-section">
        <div className="search-box">
          <FiSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search by name, email, or phone..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="customers-table-container">
        <table className="customers-table">
          <thead>
            <tr>
              <th>Customer ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Total Rides</th>
              <th>Total Spent</th>
              <th>Status</th>
              <th>Join Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredCustomers.map((customer) => (
              <tr key={customer.id}>
                <td><strong>{customer.id}</strong></td>
                <td>{customer.name}</td>
                <td>{customer.email}</td>
                <td>{customer.phone}</td>
                <td>{customer.totalRides}</td>
                <td><strong>{customer.totalSpent}</strong></td>
                <td>
                  <span className={`status-badge ${customer.status === 'active' ? 'status-active' : 'status-blocked'}`}>
                    {customer.status}
                  </span>
                </td>
                <td>{customer.joinDate}</td>
                <td>
                  <div className="action-buttons">
                    <button className="btn-icon" title="View Details">
                      <FiEye />
                    </button>
                    {hasPermission('/customers', 'block') && (
                      <>
                        {customer.status === 'active' ? (
                          <button className="btn-icon btn-danger" title="Block Customer">
                            <FiX />
                          </button>
                        ) : (
                          <button className="btn-icon btn-success" title="Unblock Customer">
                            <FiCheck />
                          </button>
                        )}
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CustomerManagement;

