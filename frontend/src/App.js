import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import PermissionRoute from './components/PermissionRoute';
import Login from './pages/Login';
import ForgotPassword from './pages/ForgotPassword';
import VerifyOTP from './pages/VerifyOTP';
import ResetPassword from './pages/ResetPassword';
import Dashboard from './pages/Dashboard';
import UserManagement from './pages/UserManagement';
import RolesPermissions from './pages/RolesPermissions';
import RideManagement from './pages/RideManagement';
import DriverManagement from './pages/DriverManagement';
import CustomerManagement from './pages/CustomerManagement';
import Payments from './pages/Payments';
import Vehicles from './pages/Vehicles';
import Complaints from './pages/Complaints';
import Promotions from './pages/Promotions';
import Notifications from './pages/Notifications';
import Settings from './pages/Settings';
import ZoneManagement from './pages/ZoneManagement';
import './App.css';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/verify-otp" element={<VerifyOTP />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            
            {/* Protected Routes */}
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={
                        <PermissionRoute path="/" action="view">
                          <Dashboard />
                        </PermissionRoute>
                      } />
                      <Route path="/users" element={
                        <PermissionRoute path="/users" action="view">
                          <UserManagement />
                        </PermissionRoute>
                      } />
                      <Route path="/roles" element={
                        <PermissionRoute path="/roles" action="view">
                          <RolesPermissions />
                        </PermissionRoute>
                      } />
                      <Route path="/rides" element={
                        <PermissionRoute path="/rides" action="view">
                          <RideManagement />
                        </PermissionRoute>
                      } />
                      <Route path="/drivers" element={
                        <PermissionRoute path="/drivers" action="view">
                          <DriverManagement />
                        </PermissionRoute>
                      } />
                      <Route path="/customers" element={
                        <PermissionRoute path="/customers" action="view">
                          <CustomerManagement />
                        </PermissionRoute>
                      } />
                      <Route path="/payments" element={
                        <PermissionRoute path="/payments" action="view">
                          <Payments />
                        </PermissionRoute>
                      } />
                      <Route path="/vehicles" element={
                        <PermissionRoute path="/vehicles" action="view">
                          <Vehicles />
                        </PermissionRoute>
                      } />
                      <Route path="/complaints" element={
                        <PermissionRoute path="/complaints" action="view">
                          <Complaints />
                        </PermissionRoute>
                      } />
                      <Route path="/promotions" element={
                        <PermissionRoute path="/promotions" action="view">
                          <Promotions />
                        </PermissionRoute>
                      } />
                      <Route path="/notifications" element={
                        <PermissionRoute path="/notifications" action="view">
                          <Notifications />
                        </PermissionRoute>
                      } />
                      <Route path="/zones" element={
                        <PermissionRoute path="/zones" action="view">
                          <ZoneManagement />
                        </PermissionRoute>
                      } />
                      <Route path="/settings" element={
                        <PermissionRoute path="/settings" action="view">
                          <Settings />
                        </PermissionRoute>
                      } />
                      <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
