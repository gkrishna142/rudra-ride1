import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';
import { usePermissions } from '../../hooks/usePermissions';
import { 
  FiHome, FiNavigation, FiUsers, FiUser, FiCreditCard, 
  FiTruck, FiMessageSquare, FiTag, FiBell, FiSettings,
  FiMenu, FiX, FiUserCheck, FiShield, FiLogOut, FiMap
} from 'react-icons/fi';
import './Sidebar.css';

const Sidebar = () => {
  const { theme } = useTheme();
  const { logout, user } = useAuth();
  const { canView } = usePermissions();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(theme.sidebarBehavior === 'fixed');
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const allMenuItems = [
    { path: '/', icon: FiHome, label: 'Dashboard', permissionPath: '/' },
    { path: '/users', icon: FiUserCheck, label: 'User Management', permissionPath: '/users' },
    { path: '/roles', icon: FiShield, label: 'Roles & Permissions', permissionPath: '/roles' },
    { path: '/rides', icon: FiNavigation, label: 'Ride Management', permissionPath: '/rides' },
    { path: '/drivers', icon: FiUsers, label: 'Driver Management', permissionPath: '/drivers' },
    { path: '/customers', icon: FiUser, label: 'Customer Management', permissionPath: '/customers' },
    { path: '/zones', icon: FiMap, label: 'Zone Management', permissionPath: '/zones' },
    { path: '/payments', icon: FiCreditCard, label: 'Payments & Transactions', permissionPath: '/payments' },
    { path: '/vehicles', icon: FiTruck, label: 'Vehicles Management', permissionPath: '/vehicles' },
    { path: '/complaints', icon: FiMessageSquare, label: 'Complaints & Support', permissionPath: '/complaints' },
    { path: '/promotions', icon: FiTag, label: 'Promotions & Coupons', permissionPath: '/promotions' },
    { path: '/notifications', icon: FiBell, label: 'Notifications', permissionPath: '/notifications' },
    { path: '/settings', icon: FiSettings, label: 'Admin Settings', permissionPath: '/settings' },
  ];

  // Filter menu items based on permissions
  const menuItems = allMenuItems.filter(item => {
    // Dashboard is always accessible if authenticated
    if (item.path === '/') {
      return true;
    }
    // Check view permission for other routes
    return canView(item.permissionPath);
  });

  return (
    <>
      <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h2>Rudra Ride</h2>
          <button className="toggle-btn" onClick={() => setIsOpen(!isOpen)}>
            {isOpen ? <FiX /> : <FiMenu />}
          </button>
        </div>
        <nav className="sidebar-nav">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item ${isActive ? 'active' : ''}`}
              >
                <Icon className="nav-icon" />
                {isOpen && <span className="nav-label">{item.label}</span>}
              </Link>
            );
          })}
        </nav>
        
        <div className="sidebar-footer">
          {user && isOpen && (
            <div className="user-info">
              <div className="user-avatar">
                {user.name ? user.name.charAt(0).toUpperCase() : 'A'}
              </div>
              <div className="user-details">
                <div className="user-name">{user.name || 'Admin User'}</div>
                <div className="user-email">{user.email}</div>
              </div>
            </div>
          )}
          <button 
            className="nav-item logout-button"
            onClick={handleLogout}
            title="Logout"
          >
            <FiLogOut className="nav-icon" />
            {isOpen && <span className="nav-label">Logout</span>}
          </button>
        </div>
      </div>
      {isOpen && <div className="sidebar-overlay" onClick={() => setIsOpen(false)} />}
    </>
  );
};

export default Sidebar;

