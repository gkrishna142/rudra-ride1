import React, { useState } from 'react';
import { FiSearch, FiPlus, FiAlertCircle, FiEdit } from 'react-icons/fi';
import { usePermissions } from '../hooks/usePermissions';
import './Vehicles.css';

const Vehicles = () => {
  const { canCreate, canEdit, canDelete } = usePermissions();
  const [searchTerm, setSearchTerm] = useState('');

  const vehicles = [
    { 
      id: 'V001', 
      number: 'DL-01-AB-1234', 
      type: 'Cab',
      model: 'Maruti Swift',
      driver: 'Raj Kumar',
      fuelType: 'Petrol',
      capacity: 4,
      rcExpiry: '2024-06-15',
      insuranceExpiry: '2024-08-20',
      status: 'active'
    },
    { 
      id: 'V002', 
      number: 'DL-01-CD-5678', 
      type: 'Bike',
      model: 'Honda Activa',
      driver: 'Amit Singh',
      fuelType: 'Petrol',
      capacity: 2,
      rcExpiry: '2024-03-10',
      insuranceExpiry: '2024-05-15',
      status: 'active'
    },
    { 
      id: 'V003', 
      number: 'DL-01-EF-9012', 
      type: 'Auto',
      model: 'Bajaj Auto Rickshaw',
      driver: 'Vikash Yadav',
      fuelType: 'CNG',
      capacity: 3,
      rcExpiry: '2024-12-20',
      insuranceExpiry: '2024-11-30',
      status: 'active'
    },
    { 
      id: 'V004', 
      number: 'DL-01-GH-3456', 
      type: 'Bike',
      model: 'Yamaha FZ',
      driver: 'Ravi Kumar',
      fuelType: 'Petrol',
      capacity: 2,
      rcExpiry: '2024-09-25',
      insuranceExpiry: '2024-10-10',
      status: 'active'
    },
    { 
      id: 'V005', 
      number: 'DL-01-IJ-7890', 
      type: 'Auto',
      model: 'TVS King',
      driver: 'Suresh Patel',
      fuelType: 'CNG',
      capacity: 3,
      rcExpiry: '2024-07-15',
      insuranceExpiry: '2024-08-30',
      status: 'active'
    },
  ];

  const filteredVehicles = vehicles.filter(vehicle =>
    vehicle.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    vehicle.model.toLowerCase().includes(searchTerm.toLowerCase()) ||
    vehicle.driver.toLowerCase().includes(searchTerm.toLowerCase()) ||
    vehicle.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const isExpiringSoon = (date) => {
    const expiryDate = new Date(date);
    const today = new Date();
    const daysUntilExpiry = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry <= 30 && daysUntilExpiry > 0;
  };

  const isExpired = (date) => {
    const expiryDate = new Date(date);
    const today = new Date();
    return expiryDate < today;
  };

  return (
    <div className="vehicles">
      <div className="page-header">
        <h1>Vehicles Management</h1>
        {canCreate('/vehicles') && (
          <button className="btn-primary">
            <FiPlus /> Add Vehicle
          </button>
        )}
      </div>

      <div className="filters-section">
        <div className="search-box">
          <FiSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search by vehicle number, model, or driver..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="vehicles-grid">
        {filteredVehicles.map((vehicle) => (
          <div key={vehicle.id} className="vehicle-card">
            <div className="vehicle-header">
              <div>
                <h3>{vehicle.number}</h3>
                <p className="vehicle-model">{vehicle.model}</p>
                <span className={`service-type-badge service-type-${vehicle.type.toLowerCase()}`}>
                  {vehicle.type}
                </span>
              </div>
              <span className={`status-badge ${vehicle.status === 'active' ? 'status-active' : 'status-inactive'}`}>
                {vehicle.status}
              </span>
            </div>

            <div className="vehicle-details">
              <div className="detail-item">
                <span className="detail-label">Driver:</span>
                <span className="detail-value">{vehicle.driver}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Fuel Type:</span>
                <span className="detail-value">{vehicle.fuelType}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Capacity:</span>
                <span className="detail-value">{vehicle.capacity} seats</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">RC Expiry:</span>
                <span className={`detail-value ${isExpired(vehicle.rcExpiry) ? 'expired' : isExpiringSoon(vehicle.rcExpiry) ? 'expiring-soon' : ''}`}>
                  {vehicle.rcExpiry}
                  {(isExpired(vehicle.rcExpiry) || isExpiringSoon(vehicle.rcExpiry)) && (
                    <FiAlertCircle className="alert-icon" />
                  )}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Insurance Expiry:</span>
                <span className={`detail-value ${isExpired(vehicle.insuranceExpiry) ? 'expired' : isExpiringSoon(vehicle.insuranceExpiry) ? 'expiring-soon' : ''}`}>
                  {vehicle.insuranceExpiry}
                  {(isExpired(vehicle.insuranceExpiry) || isExpiringSoon(vehicle.insuranceExpiry)) && (
                    <FiAlertCircle className="alert-icon" />
                  )}
                </span>
              </div>
            </div>

            <div className="vehicle-actions">
              {canEdit('/vehicles') && (
                <button className="btn-secondary">
                  <FiEdit /> Edit
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Vehicles;

