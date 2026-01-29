import React, { useState } from 'react';
import { FiSearch, FiPlus, FiEye, FiEdit, FiMapPin, FiDollarSign, FiStar } from 'react-icons/fi';
import { usePermissions } from '../hooks/usePermissions';
import './DriverManagement.css';

const DriverManagement = () => {
  const { canCreate, canEdit, canDelete, hasPermission } = usePermissions();
  const [searchTerm, setSearchTerm] = useState('');
  const [serviceFilter, setServiceFilter] = useState('all');

  const drivers = [
    { 
      id: 'D001', 
      name: 'Raj Kumar', 
      phone: '+91 98765 43210', 
      vehicleType: 'Cab',
      vehicle: 'DL-01-AB-1234',
      status: 'active',
      rating: 4.8,
      totalRides: 234,
      earnings: '₹45,678',
      location: 'Online'
    },
    { 
      id: 'D002', 
      name: 'Amit Singh', 
      phone: '+91 98765 43211', 
      vehicleType: 'Bike',
      vehicle: 'DL-01-CD-5678',
      status: 'active',
      rating: 4.6,
      totalRides: 189,
      earnings: '₹38,920',
      location: 'Online'
    },
    { 
      id: 'D003', 
      name: 'Vikash Yadav', 
      phone: '+91 98765 43212', 
      vehicleType: 'Auto',
      vehicle: 'DL-01-EF-9012',
      status: 'inactive',
      rating: 4.9,
      totalRides: 312,
      earnings: '₹62,450',
      location: 'Offline'
    },
    { 
      id: 'D004', 
      name: 'Ravi Kumar', 
      phone: '+91 98765 43213', 
      vehicleType: 'Bike',
      vehicle: 'DL-01-GH-3456',
      status: 'active',
      rating: 4.7,
      totalRides: 156,
      earnings: '₹28,450',
      location: 'Online'
    },
    { 
      id: 'D005', 
      name: 'Suresh Patel', 
      phone: '+91 98765 43214', 
      vehicleType: 'Auto',
      vehicle: 'DL-01-IJ-7890',
      status: 'active',
      rating: 4.5,
      totalRides: 201,
      earnings: '₹35,670',
      location: 'Online'
    },
  ];

  const filteredDrivers = drivers.filter(driver => {
    const matchesService = serviceFilter === 'all' || 
                          serviceFilter === 'driver' || 
                          driver.vehicleType.toLowerCase() === serviceFilter.toLowerCase();
    const matchesSearch = driver.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         driver.phone.includes(searchTerm) ||
                         driver.vehicle.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesService && matchesSearch;
  });

  return (
    <div className="driver-management">
      <div className="page-header">
        <h1>Driver Management</h1>
        {canCreate('/drivers') && (
          <button className="btn-primary">
            <FiPlus /> Add New Driver
          </button>
        )}
      </div>

      <div className="filters-section">
        <div className="search-box">
          <FiSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search by name, phone, or vehicle number..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="filter-section">
          <div className="filter-group">
            <label>Service Type:</label>
            <div className="filter-buttons">
              <button 
                className={serviceFilter === 'all' ? 'active' : ''}
                onClick={() => setServiceFilter('all')}
              >
                All Services
              </button>
              <button 
                className={serviceFilter === 'cab' ? 'active' : ''}
                onClick={() => setServiceFilter('cab')}
              >
                Cab
              </button>
              <button 
                className={serviceFilter === 'bike' ? 'active' : ''}
                onClick={() => setServiceFilter('bike')}
              >
                Bike
              </button>
              <button 
                className={serviceFilter === 'auto' ? 'active' : ''}
                onClick={() => setServiceFilter('auto')}
              >
                Auto
              </button>
              <button 
                className={serviceFilter === 'driver' ? 'active' : ''}
                onClick={() => setServiceFilter('driver')}
              >
                Driver Service
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="drivers-grid">
        {filteredDrivers.map((driver) => (
          <div key={driver.id} className="driver-card">
            <div className="driver-header">
              <div className="driver-info">
                <h3>{driver.name}</h3>
                <p className="driver-id">ID: {driver.id}</p>
              </div>
              <span className={`status-badge ${driver.status === 'active' ? 'status-active' : 'status-inactive'}`}>
                {driver.status}
              </span>
            </div>
            
            <div className="driver-details">
              <div className="detail-item">
                <span className="detail-label">Phone:</span>
                <span className="detail-value">{driver.phone}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Service Type:</span>
                <span className="detail-value">
                  <span className={`service-type-badge service-type-${driver.vehicleType.toLowerCase()}`}>
                    {driver.vehicleType}
                  </span>
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Vehicle:</span>
                <span className="detail-value">{driver.vehicle}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Rating:</span>
                <span className="detail-value">
                  <FiStar className="star-icon" /> {driver.rating}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Total Rides:</span>
                <span className="detail-value">{driver.totalRides}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Earnings:</span>
                <span className="detail-value earnings">{driver.earnings}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Location:</span>
                <span className={`detail-value ${driver.location === 'Online' ? 'online' : 'offline'}`}>
                  {driver.location}
                </span>
              </div>
            </div>

            <div className="driver-actions">
              <button className="btn-secondary">
                <FiEye /> View Details
              </button>
              {canEdit('/drivers') && (
                <button className="btn-secondary">
                  <FiEdit /> Edit
                </button>
              )}
              {hasPermission('/drivers', 'approve') && (
                <button className="btn-primary">
                  Approve
                </button>
              )}
              <button className="btn-secondary">
                <FiMapPin /> Track Location
              </button>
              <button className="btn-secondary">
                <FiDollarSign /> Wallet
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DriverManagement;

