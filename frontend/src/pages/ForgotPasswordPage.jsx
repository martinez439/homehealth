import { useState } from 'react';
import { Link } from 'react-router-dom';
import { forgotPassword } from '../api/auth';

const RESET_MESSAGE = 'If an account exists, password reset instructions will be sent.';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage('');
    setError('');
    setIsSubmitting(true);

    try {
      const result = await forgotPassword(email);
      setMessage(result?.message || RESET_MESSAGE);
    } catch {
      setError('We could not start a reset right now. Please try again in a few minutes.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="auth-page">
      <div className="auth-card polished-auth-card reset-card">
        <div className="auth-card__intro">
          <span className="secure-label">Password Reset</span>
          <h2>Reset your CLHS HomeCare password</h2>
          <p className="auth-lede">Enter the email connected to your account and we’ll prepare reset instructions.</p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="field-group">
            <span>Email address</span>
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" autoComplete="email" required />
          </label>

          {message && <div className="success-message reset-success" role="status">{message}</div>}
          {error && <div className="error-box auth-error" role="alert">{error}</div>}

          <button className="primary-button premium-signin-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Sending…' : 'Send reset instructions'}
          </button>
        </form>

        <Link className="back-to-login" to="/login">Back to sign in</Link>
      </div>
    </section>
  );
}
