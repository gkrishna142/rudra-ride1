import React from 'react';
import { useTheme } from '../../context/ThemeContext';
import Sidebar from './Sidebar';
import './Layout.css';

const Layout = ({ children }) => {
  const { theme } = useTheme();

  return (
    <div className={`layout layout-${theme.layout}`}>
      <Sidebar />
      <div className="layout-container">
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;

