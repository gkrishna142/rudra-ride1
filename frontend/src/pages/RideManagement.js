import React, { useState } from 'react';
import { FiSearch, FiEye, FiEdit, FiX, FiPlus } from 'react-icons/fi';
import { usePermissions } from '../hooks/usePermissions';
import './RideManagement.css';

const RideManagement = () => {
  const { canCreate, canEdit, canDelete, hasPermission } = usePermissions();
  const [filter, setFilter] = useState('all');
  const [vehicleFilter, setVehicleFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const rides = [
    { id: 'R001', customer: 'John Doe', driver: 'Raj Kumar', vehicleType: 'Cab', vehicle: 'DL-01-AB-1234', pickup: 'Airport', drop: 'City Center', fare: '₹450', status: 'completed', date: '2024-01-15 10:30' },
    { id: 'R002', customer: 'Jane Smith', driver: 'Amit Singh', vehicleType: 'Bike', vehicle: 'DL-01-CD-5678', pickup: 'Mall', drop: 'Home', fare: '₹120', status: 'pending', date: '2024-01-15 11:00' },
    { id: 'R003', customer: 'Mike Johnson', driver: 'Vikash Yadav', vehicleType: 'Auto', vehicle: 'DL-01-EF-9012', pickup: 'Station', drop: 'Office', fare: '₹180', status: 'upcoming', date: '2024-01-15 12:00' },
    { id: 'R004', customer: 'Sarah Williams', driver: '-', vehicleType: 'Cab', vehicle: '-', pickup: 'Hotel', drop: 'Airport', fare: '₹550', status: 'cancelled', date: '2024-01-15 09:15' },
    { id: 'R005', customer: 'Tom Brown', driver: 'Ravi Kumar', vehicleType: 'Bike', vehicle: 'DL-01-GH-3456', pickup: 'Park', drop: 'Restaurant', fare: '₹95', status: 'completed', date: '2024-01-15 08:30' },
    { id: 'R006', customer: 'Lisa White', driver: 'Suresh Patel', vehicleType: 'Auto', vehicle: 'DL-01-IJ-7890', pickup: 'Market', drop: 'Home', fare: '₹150', status: 'completed', date: '2024-01-15 07:15' },
  ];

  const filteredRides = rides.filter(ride => {
    const matchesFilter = filter === 'all' || ride.status === filter;
    const matchesVehicle = vehicleFilter === 'all' || ride.vehicleType.toLowerCase() === vehicleFilter.toLowerCase();
    const matchesSearch = ride.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         ride.customer.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         ride.vehicleType.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesVehicle && matchesSearch;
  });

  const getStatusBadge = (status) => {
    const statusClasses = {
      completed: 'status-completed',
      pending: 'status-pending',
      upcoming: 'status-upcoming',
      cancelled: 'status-cancelled'
    };
    return statusClasses[status] || '';
  };

  return (
    <div className="ride-management">
      <div className="page-header">
        <div>
          <h1>Ride Management</h1>
        </div>
        {canCreate('/rides') && (
          <button className="btn-primary">
            <FiPlus /> New Ride
          </button>
        )}
      </div>

      <div className="filters-section">
        <div className="search-box">
          <FiSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search by ride ID or customer name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="filter-section">
          <div className="filter-group">
            <label>Status:</label>
            <div className="filter-buttons">
              <button 
                className={filter === 'all' ? 'active' : ''}
                onClick={() => setFilter('all')}
              >
                All Rides
              </button>
              <button 
                className={filter === 'today' ? 'active' : ''}
                onClick={() => setFilter('today')}
              >
                Today
              </button>
              <button 
                className={filter === 'upcoming' ? 'active' : ''}
                onClick={() => setFilter('upcoming')}
              >
                Upcoming
              </button>
              <button 
                className={filter === 'completed' ? 'active' : ''}
                onClick={() => setFilter('completed')}
              >
                Completed
              </button>
              <button 
                className={filter === 'cancelled' ? 'active' : ''}
                onClick={() => setFilter('cancelled')}
              >
                Cancelled
              </button>
            </div>
          </div>
          <div className="filter-group">
            <label>Service Type:</label>
            <div className="filter-buttons">
              <button 
                className={vehicleFilter === 'all' ? 'active' : ''}
                onClick={() => setVehicleFilter('all')}
              >
                All Services
              </button>
              <button 
                className={vehicleFilter === 'cab' ? 'active' : ''}
                onClick={() => setVehicleFilter('cab')}
              >
                Cab
              </button>
              <button 
                className={vehicleFilter === 'bike' ? 'active' : ''}
                onClick={() => setVehicleFilter('bike')}
              >
                Bike
              </button>
              <button 
                className={vehicleFilter === 'auto' ? 'active' : ''}
                onClick={() => setVehicleFilter('auto')}
              >
                Auto
              </button>
              <button 
                className={vehicleFilter === 'driver' ? 'active' : ''}
                onClick={() => setVehicleFilter('driver')}
              >
                Driver Service
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="rides-table-container">
        <table className="rides-table">
          <thead>
            <tr>
              <th>Ride ID</th>
              <th>Customer</th>
              <th>Driver</th>
              <th>Service Type</th>
              <th>Vehicle</th>
              <th>Pickup</th>
              <th>Drop</th>
              <th>Fare</th>
              <th>Status</th>
              <th>Date & Time</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredRides.map((ride) => (
              <tr key={ride.id}>
                <td><strong>{ride.id}</strong></td>
                <td>{ride.customer}</td>
                <td>{ride.driver}</td>
                <td>
                  <span className={`service-type-badge service-type-${ride.vehicleType.toLowerCase()}`}>
                    {ride.vehicleType}
                  </span>
                </td>
                <td>{ride.vehicle}</td>
                <td>{ride.pickup}</td>
                <td>{ride.drop}</td>
                <td><strong>{ride.fare}</strong></td>
                <td>
                  <span className={`status-badge ${getStatusBadge(ride.status)}`}>
                    {ride.status}
                  </span>
                </td>
                <td>{ride.date}</td>
                <td>
                  <div className="action-buttons">
                    <button className="btn-icon" title="View Details">
                      <FiEye />
                    </button>
                    {(canEdit('/rides') || hasPermission('/rides', 'assign')) && (
                      <button className="btn-icon" title="Edit/Assign Driver">
                        <FiEdit />
                      </button>
                    )}
                    {canDelete('/rides') && ride.status !== 'cancelled' && (
                      <button className="btn-icon btn-danger" title="Cancel Ride">
                        <FiX />
                      </button>
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

export default RideManagement;

