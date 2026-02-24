import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

function Login() {
  const { needsSetup, login, setup } = useAuth();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (needsSetup) {
        if (password.length < 8) {
          setError('Password must be at least 8 characters');
          setLoading(false);
          return;
        }
        if (password !== confirmPassword) {
          setError('Passwords do not match');
          setLoading(false);
          return;
        }
        await setup(password);
      } else {
        await login(password);
      }
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>PM Tracker</h1>
        <h2>{needsSetup ? 'Create Password' : 'Login'}</h2>

        {needsSetup && (
          <p className="setup-notice">
            Welcome! Please create a password to secure your portfolio data.
          </p>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={needsSetup ? 'Create password (min 8 chars)' : 'Enter password'}
              required
              autoFocus
            />
          </div>

          {needsSetup && (
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm password"
                required
              />
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? 'Please wait...' : needsSetup ? 'Create Password' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
