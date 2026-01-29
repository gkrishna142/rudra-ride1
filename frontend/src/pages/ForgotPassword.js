import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FiMail, FiArrowLeft, FiAlertCircle, FiSmartphone } from 'react-icons/fi';
import './ForgotPassword.css';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const { sendOTP } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    if (!email) {
      setError('Please enter your email address');
      setLoading(false);
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      setLoading(false);
      return;
    }

    const result = await sendOTP(email);
    setLoading(false);

    if (result.success) {
      setSuccess(true);
      // Store email in sessionStorage for OTP verification
      sessionStorage.setItem('resetEmail', email);
      setTimeout(() => {
        navigate('/verify-otp');
      }, 2000);
    } else {
      setError(result.error || 'Failed to send OTP. Please try again.');
    }
  };

  if (success) {
    return (
      <div className="forgot-password-page">
        <div className="forgot-password-container">
          <div className="forgot-password-card">
            <div className="success-icon">
              <FiSmartphone />
            </div>
            <h2 className="success-title">OTP Sent Successfully</h2>
            <p className="success-message">
              We've sent a 6-digit OTP to <strong>{email}</strong>
            </p>
            <p className="success-submessage">
              Please check your email/SMS and enter the OTP to reset your password.
            </p>
            <div className="success-footer">
              <p className="text-muted mb-3">
                Redirecting to OTP verification...
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="forgot-password-page">
      <div className="forgot-password-container">
        <div className="forgot-password-card">
          <div className="forgot-password-header">
            <h2 className="forgot-password-title">Forgot Password?</h2>
            <p className="forgot-password-subtitle">
              No worries! Enter your email address and we'll send you an OTP to reset your password.
            </p>
          </div>

          {error && (
            <div className="alert alert-danger d-flex align-items-center" role="alert">
              <FiAlertCircle className="me-2" />
              <div>{error}</div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="forgot-password-form">
            <div className="mb-4">
              <label htmlFor="email" className="form-label">
                Email Address
              </label>
              <div className="input-group">
                <span className="input-group-text">
                  <FiMail />
                </span>
                <input
                  type="email"
                  className="form-control"
                  id="email"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary w-100 forgot-password-button"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Sending OTP...
                </>
              ) : (
                <>
                  <FiSmartphone className="me-2" />
                  Send OTP
                </>
              )}
            </button>
          </form>

          <div className="forgot-password-footer">
            <Link to="/login" className="back-to-login-link">
              <FiArrowLeft className="me-2" />
              Back to Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;

