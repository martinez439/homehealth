import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { login } from '../api/auth';

function EyeIcon({ hidden }) {
  if (hidden) {
    return (
      <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20C7 20 2.73 16.89 1 12a18.45 18.45 0 0 1 5.06-6.94" />
        <path d="M9.9 4.24A10.45 10.45 0 0 1 12 4c5 0 9.27 3.11 11 8a18.5 18.5 0 0 1-2.16 3.19" />
        <path d="M14.12 14.12a3 3 0 0 1-4.24-4.24" />
        <path d="m1 1 22 22" />
      </svg>
    );
  }

  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

export default function LoginPage() {
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);
    try {
      const result = await login(email, password);
      const target = location.state?.from?.pathname || (result.user.role === 'caregiver' ? '/caregiver' : result.user.role === 'family' ? `/family/${result.user.client_id || 1}` : '/admin');
      navigate(target, { replace: true });
    } catch {
      setError('Unable to sign in with those credentials. Please check your email and password.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="auth-page">
      <div className="auth-card polished-auth-card">
        <div className="auth-card__intro">
          <span className="secure-label">Secure Access</span>
          <h2>Welcome back to CLHS HomeCare</h2>
          <p className="auth-lede">Concierge care coordination for families, caregivers, and administrators.</p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="field-group">
            <span>Email address</span>
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" autoComplete="email" required />
          </label>

          <div className="password-row">
            <label className="field-group password-field">
              <span>Password</span>
              <div className="password-input-shell">
                <input
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                />
                <button
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="password-toggle"
                  type="button"
                  onClick={() => setShowPassword((visible) => !visible)}
                >
                  <EyeIcon hidden={showPassword} />
                </button>
              </div>
            </label>
            <Link className="forgot-link" to="/forgot-password">Forgot password?</Link>
          </div>

          {error && <div className="error-box auth-error" role="alert">{error}</div>}

          <button className="primary-button premium-signin-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Signing in…' : 'Sign in securely'}
          </button>
        </form>

        <div className="demo-account-card" aria-label="Demo account credentials">
          <p className="demo-title">Demo accounts</p>
          <p>Use <strong>admin@example.com</strong>, <strong>caregiver@example.com</strong>, or <strong>family@example.com</strong>.</p>
          <p>Password for all demo accounts: <strong>password123</strong></p>
        </div>
      </div>
    </section>
  );
}
