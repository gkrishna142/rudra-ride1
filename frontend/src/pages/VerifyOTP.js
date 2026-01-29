import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FiArrowLeft, FiAlertCircle, FiCheckCircle, FiRefreshCw } from 'react-icons/fi';
import './VerifyOTP.css';

const VerifyOTP = () => {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [timer, setTimer] = useState(60);
  const [canResend, setCanResend] = useState(false);
  const { verifyOTP, sendOTP } = useAuth();
  const navigate = useNavigate();
  const inputRefs = useRef([]);

  const email = sessionStorage.getItem('resetEmail') || '';

  useEffect(() => {
    if (!email) {
      navigate('/forgot-password');
    }
  }, [email, navigate]);

  useEffect(() => {
    if (timer > 0) {
      const interval = setInterval(() => {
        setTimer((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(interval);
    } else {
      setCanResend(true);
    }
  }, [timer]);

  const handleChange = (index, value) => {
    if (value.length > 1) return;
    
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);
    setError('');

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').trim();
    if (pastedData.length === 6 && /^\d+$/.test(pastedData)) {
      const newOtp = pastedData.split('');
      setOtp(newOtp);
      inputRefs.current[5]?.focus();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    const otpString = otp.join('');
    if (otpString.length !== 6) {
      setError('Please enter the complete 6-digit OTP');
      return;
    }

    if (!/^\d+$/.test(otpString)) {
      setError('OTP should contain only numbers');
      return;
    }

    setLoading(true);
    const result = await verifyOTP(email, otpString);
    setLoading(false);

    if (result.success) {
      navigate('/reset-password');
    } else {
      setError(result.error || 'Invalid OTP. Please try again.');
      setOtp(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    }
  };

  const handleResendOTP = async () => {
    setResendLoading(true);
    setError('');
    const result = await sendOTP(email);
    setResendLoading(false);

    if (result.success) {
      setTimer(60);
      setCanResend(false);
      setOtp(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    } else {
      setError(result.error || 'Failed to resend OTP. Please try again.');
    }
  };

  return (
    <div className="verify-otp-page">
      <div className="verify-otp-container">
        <div className="verify-otp-card">
          <div className="verify-otp-header">
            <h2 className="verify-otp-title">Verify OTP</h2>
            <p className="verify-otp-subtitle">
              Enter the 6-digit OTP sent to <strong>{email}</strong>
            </p>
          </div>

          {error && (
            <div className="alert alert-danger d-flex align-items-center" role="alert">
              <FiAlertCircle className="me-2" />
              <div>{error}</div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="verify-otp-form">
            <div className="otp-input-container">
              {otp.map((digit, index) => (
                <input
                  key={index}
                  ref={(el) => (inputRefs.current[index] = el)}
                  type="text"
                  inputMode="numeric"
                  maxLength="1"
                  className="otp-input"
                  value={digit}
                  onChange={(e) => handleChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  onPaste={handlePaste}
                  autoFocus={index === 0}
                />
              ))}
            </div>

            <button
              type="submit"
              className="btn btn-primary w-100 verify-otp-button"
              disabled={loading || otp.join('').length !== 6}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Verifying...
                </>
              ) : (
                <>
                  <FiCheckCircle className="me-2" />
                  Verify OTP
                </>
              )}
            </button>
          </form>

          <div className="resend-otp-section">
            {canResend ? (
              <button
                type="button"
                className="btn btn-link resend-button"
                onClick={handleResendOTP}
                disabled={resendLoading}
              >
                {resendLoading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Sending...
                  </>
                ) : (
                  <>
                    <FiRefreshCw className="me-2" />
                    Resend OTP
                  </>
                )}
              </button>
            ) : (
              <p className="resend-timer">
                Resend OTP in <strong>{timer}s</strong>
              </p>
            )}
          </div>

          <div className="verify-otp-footer">
            <Link to="/forgot-password" className="back-link">
              <FiArrowLeft className="me-2" />
              Change Email
            </Link>
            <Link to="/login" className="back-link">
              <FiArrowLeft className="me-2" />
              Back to Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerifyOTP;

