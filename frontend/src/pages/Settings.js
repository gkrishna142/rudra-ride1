import React, { useState } from 'react';
import { FiSave, FiUsers, FiDollarSign, FiMap, FiSettings, FiDroplet } from 'react-icons/fi';
import { usePermissions } from '../hooks/usePermissions';
import ThemeSettings from '../components/ThemeSettings/ThemeSettings';
import './Settings.css';

const Settings = () => {
  const { hasPermission } = usePermissions();
  const [activeTab, setActiveTab] = useState('admins');

  const tabs = [
    { id: 'theme', label: 'Theme Settings', icon: FiDroplet },
    { id: 'admins', label: 'Admin Management', icon: FiUsers },
    { id: 'fare', label: 'Fare Settings', icon: FiDollarSign },
    { id: 'surge', label: 'Surge Pricing', icon: FiDollarSign },
    { id: 'zones', label: 'Zones Management', icon: FiMap },
    { id: 'app', label: 'App Settings', icon: FiSettings },
  ];

  return (
    <div className="settings">
      <div className="page-header">
        <h1>Admin Settings</h1>
      </div>

      <div className="settings-container">
        <div className="settings-sidebar">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                className={`settings-tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <Icon />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        <div className="settings-content">
          {activeTab === 'theme' && (
            <div className="settings-section">
              <ThemeSettings />
            </div>
          )}

          {activeTab === 'admins' && (
            <div className="settings-section">
              <h2>Admin Management</h2>
              <div className="settings-card">
                <div className="form-group">
                  <label>Add New Admin</label>
                  <div className="form-row">
                    <input type="text" placeholder="Name" />
                    <input type="email" placeholder="Email" />
                    <select>
                      <option>Super Admin</option>
                      <option>Admin</option>
                      <option>Moderator</option>
                    </select>
                    <button className="btn-primary">Add Admin</button>
                  </div>
                </div>
                <div className="admins-list">
                  <h3>Existing Admins</h3>
                  <table className="admins-table">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>Admin User</td>
                        <td>admin@rudraride.com</td>
                        <td>Super Admin</td>
                        <td>
                          <button className="btn-secondary">Edit</button>
                          <button className="btn-secondary btn-danger">Remove</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'fare' && (
            <div className="settings-section">
              <h2>Fare Settings</h2>
              <div className="settings-card">
                <div className="form-group">
                  <label>Base Fare (₹)</label>
                  <input type="number" placeholder="50" />
                </div>
                <div className="form-group">
                  <label>Per Kilometer Rate (₹)</label>
                  <input type="number" placeholder="12" />
                </div>
                <div className="form-group">
                  <label>Per Minute Rate (₹)</label>
                  <input type="number" placeholder="2" />
                </div>
                <div className="form-group">
                  <label>Minimum Fare (₹)</label>
                  <input type="number" placeholder="80" />
                </div>
                <button className="btn-primary">
                  <FiSave /> Save Changes
                </button>
              </div>
            </div>
          )}

          {activeTab === 'surge' && (
            <div className="settings-section">
              <h2>Surge Pricing</h2>
              <div className="settings-card">
                <div className="form-group">
                  <label>Enable Surge Pricing</label>
                  <label className="toggle-switch">
                    <input type="checkbox" />
                    <span className="slider"></span>
                  </label>
                </div>
                <div className="form-group">
                  <label>Surge Multiplier (1x - 5x)</label>
                  <input type="range" min="1" max="5" step="0.1" defaultValue="2" />
                  <span className="range-value">2.0x</span>
                </div>
                <div className="form-group">
                  <label>Trigger Conditions</label>
                  <div className="checkbox-group">
                    <label>
                      <input type="checkbox" /> High Demand
                    </label>
                    <label>
                      <input type="checkbox" /> Low Driver Availability
                    </label>
                    <label>
                      <input type="checkbox" /> Peak Hours
                    </label>
                  </div>
                </div>
                <button className="btn-primary">
                  <FiSave /> Save Changes
                </button>
              </div>
            </div>
          )}

          {activeTab === 'zones' && (
            <div className="settings-section">
              <h2>Zones Management</h2>
              <div className="settings-card">
                <div className="form-group">
                  <label>Add New Zone</label>
                  <div className="form-row">
                    <input type="text" placeholder="Zone Name" />
                    <input type="text" placeholder="City" />
                    <button className="btn-primary">Add Zone</button>
                  </div>
                </div>
                <div className="zones-list">
                  <h3>Active Zones</h3>
                  <div className="zones-grid">
                    <div className="zone-card">
                      <h4>Central Delhi</h4>
                      <p>Delhi</p>
                      <button className="btn-secondary">Edit</button>
                    </div>
                    <div className="zone-card">
                      <h4>South Delhi</h4>
                      <p>Delhi</p>
                      <button className="btn-secondary">Edit</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'app' && (
            <div className="settings-section">
              <h2>App Settings</h2>
              <div className="settings-card">
                <div className="form-group">
                  <label>App Name</label>
                  <input type="text" defaultValue="Rudra Ride" />
                </div>
                <div className="form-group">
                  <label>Support Email</label>
                  <input type="email" defaultValue="support@rudraride.com" />
                </div>
                <div className="form-group">
                  <label>Support Phone</label>
                  <input type="tel" defaultValue="+91 1800-123-4567" />
                </div>
                <div className="form-group">
                  <label>Maintenance Mode</label>
                  <label className="toggle-switch">
                    <input type="checkbox" />
                    <span className="slider"></span>
                  </label>
                </div>
                <button className="btn-primary">
                  <FiSave /> Save Changes
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;

