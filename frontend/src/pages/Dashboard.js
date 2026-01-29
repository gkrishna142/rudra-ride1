import React from 'react';
import { 
  FiNavigation, FiCheckCircle, FiClock, FiXCircle, 
  FiUsers, FiUser, FiDollarSign, FiMap
} from 'react-icons/fi';
import './Dashboard.css';

const Dashboard = () => {
  const stats = [
    { label: 'Total Rides Today', value: '1,234', icon: FiNavigation, color: '#3b82f6' },
    { label: 'Completed Rides', value: '1,089', icon: FiCheckCircle, color: '#10b981' },
    { label: 'Pending Rides', value: '89', icon: FiClock, color: '#f59e0b' },
    { label: 'Cancelled Rides', value: '56', icon: FiXCircle, color: '#ef4444' },
    { label: 'Active Drivers', value: '342', icon: FiUsers, color: '#8b5cf6' },
    { label: 'Active Customers', value: '5,678', icon: FiUser, color: '#ec4899' },
    { label: 'Revenue Today', value: '₹1,23,456', icon: FiDollarSign, color: '#14b8a6' },
  ];

  const serviceTypeStats = [
    { type: 'Cab', rides: 456, drivers: 142, revenue: '₹45,678' },
    { type: 'Bike', rides: 523, drivers: 125, revenue: '₹32,456' },
    { type: 'Auto', rides: 255, drivers: 75, revenue: '₹45,322' },
    { type: 'Driver', rides: 0, drivers: 342, revenue: '₹0', description: 'Direct driver service' },
  ];

  const recentActivities = [
    { id: 1, type: 'New Ride', user: 'John Doe', time: '2 mins ago', status: 'pending' },
    { id: 2, type: 'Ride Completed', user: 'Jane Smith', time: '5 mins ago', status: 'completed' },
    { id: 3, type: 'New Driver', user: 'Mike Johnson', time: '10 mins ago', status: 'new' },
    { id: 4, type: 'Payment Received', user: 'Sarah Williams', time: '15 mins ago', status: 'payment' },
    { id: 5, type: 'Ride Cancelled', user: 'Tom Brown', time: '20 mins ago', status: 'cancelled' },
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard Overview</h1>
        <p>Welcome back! Here's what's happening with Rudra Ride today.</p>
      </div>

      <div className="stats-grid">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="stat-card">
              <div className="stat-icon" style={{ backgroundColor: `${stat.color}20`, color: stat.color }}>
                <Icon />
              </div>
              <div className="stat-content">
                <h3>{stat.value}</h3>
                <p>{stat.label}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="service-type-stats">
        <h2>Service Types Overview</h2>
        <div className="service-stats-grid">
          {serviceTypeStats.map((stat, index) => (
            <div key={index} className="service-stat-card">
              <h3>{stat.type}</h3>
              {stat.description && <p className="service-description">{stat.description}</p>}
              <div className="service-stat-details">
                <div className="stat-row">
                  <span>Rides:</span>
                  <strong>{stat.rides}</strong>
                </div>
                <div className="stat-row">
                  <span>Drivers:</span>
                  <strong>{stat.drivers}</strong>
                </div>
                <div className="stat-row">
                  <span>Revenue:</span>
                  <strong className="revenue">{stat.revenue}</strong>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="card-header">
            <h2>Live Ride Tracking</h2>
            <button className="view-all-btn">View All</button>
          </div>
          <div className="map-placeholder">
            <FiMap className="map-icon" />
            <p>Live Map View</p>
            <span>Active Rides: 89</span>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h2>Recent Activities</h2>
            <button className="view-all-btn">View All</button>
          </div>
          <div className="activities-list">
            {recentActivities.map((activity) => (
              <div key={activity.id} className="activity-item">
                <div className="activity-icon" data-status={activity.status}>
                  {activity.status === 'completed' && <FiCheckCircle />}
                  {activity.status === 'pending' && <FiClock />}
                  {activity.status === 'cancelled' && <FiXCircle />}
                  {activity.status === 'new' && <FiUsers />}
                  {activity.status === 'payment' && <FiDollarSign />}
                </div>
                <div className="activity-content">
                  <h4>{activity.type}</h4>
                  <p>{activity.user}</p>
                </div>
                <span className="activity-time">{activity.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

