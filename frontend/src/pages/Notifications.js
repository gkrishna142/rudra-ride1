import React, { useState } from 'react';
import { FiPlus, FiSend, FiMail, FiPhone, FiBell } from 'react-icons/fi';
import { usePermissions } from '../hooks/usePermissions';
import './Notifications.css';

const Notifications = () => {
  const { canCreate, hasPermission } = usePermissions();
  const [showModal, setShowModal] = useState(false);
  const [notificationType, setNotificationType] = useState('push');

  const notifications = [
    { 
      id: 'N001', 
      title: 'New Ride Available',
      message: 'You have a new ride request nearby',
      type: 'Push',
      target: 'Drivers',
      sent: '2024-01-15 10:30',
      status: 'sent'
    },
    { 
      id: 'N002', 
      title: 'Ride Completed',
      message: 'Your ride has been completed successfully',
      type: 'SMS',
      target: 'Customers',
      sent: '2024-01-15 09:15',
      status: 'sent'
    },
    { 
      id: 'N003', 
      title: 'Payment Received',
      message: 'Your payment of ₹450 has been received',
      type: 'Email',
      target: 'Customers',
      sent: '2024-01-15 08:00',
      status: 'sent'
    },
  ];

  return (
    <div className="notifications">
      <div className="page-header">
        <h1>Notifications</h1>
        {hasPermission('/notifications', 'send') && (
          <button className="btn-primary" onClick={() => setShowModal(true)}>
            <FiPlus /> Send Notification
          </button>
        )}
      </div>

      <div className="notification-types">
        <button 
          className={`type-card ${notificationType === 'push' ? 'active' : ''}`}
          onClick={() => setNotificationType('push')}
        >
          <FiBell />
          <span>Push Notifications</span>
        </button>
        <button 
          className={`type-card ${notificationType === 'sms' ? 'active' : ''}`}
          onClick={() => setNotificationType('sms')}
        >
          <FiPhone />
          <span>SMS</span>
        </button>
        <button 
          className={`type-card ${notificationType === 'email' ? 'active' : ''}`}
          onClick={() => setNotificationType('email')}
        >
          <FiMail />
          <span>Email</span>
        </button>
      </div>

      <div className="notifications-list">
        {notifications.map((notification) => (
          <div key={notification.id} className="notification-card">
            <div className="notification-header">
              <div>
                <h3>{notification.title}</h3>
                <p className="notification-id">ID: {notification.id}</p>
              </div>
              <span className="status-badge status-sent">
                {notification.status}
              </span>
            </div>

            <div className="notification-body">
              <p className="notification-message">{notification.message}</p>
              <div className="notification-meta">
                <span className="meta-item">
                  <strong>Type:</strong> {notification.type}
                </span>
                <span className="meta-item">
                  <strong>Target:</strong> {notification.target}
                </span>
                <span className="meta-item">
                  <strong>Sent:</strong> {notification.sent}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Send Notification</h2>
            <form>
              <div className="form-group">
                <label>Notification Type</label>
                <select>
                  <option>Push Notification</option>
                  <option>SMS</option>
                  <option>Email</option>
                </select>
              </div>
              <div className="form-group">
                <label>Target Audience</label>
                <select>
                  <option>All Users</option>
                  <option>Drivers Only</option>
                  <option>Customers Only</option>
                  <option>Specific Users</option>
                </select>
              </div>
              <div className="form-group">
                <label>Title</label>
                <input type="text" placeholder="Notification title" />
              </div>
              <div className="form-group">
                <label>Message</label>
                <textarea rows="4" placeholder="Notification message"></textarea>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  <FiSend /> Send Notification
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Notifications;

