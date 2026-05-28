import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { login } from '../api/auth';

export default function LoginPage() {
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    try {
      const result = await login(email, password);
      const target = location.state?.from?.pathname || (result.user.role === 'caregiver' ? '/caregiver' : result.user.role === 'family' ? `/family/${result.user.client_id || 1}` : '/admin');
      navigate(target, { replace: true });
    } catch {
      setError('Unable to sign in with those credentials.');
    }
  }

  return (
    <section className="page-card auth-card">
      <div>
        <p className="eyebrow">Secure access</p>
        <h2>Sign in to CLHS HomeCare</h2>
        <p className="muted">Use a demo account: admin@example.com, caregiver@example.com, or family@example.com with password123.</p>
      </div>
      <form className="form-grid" onSubmit={handleSubmit}>
        <label>Email<input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required /></label>
        <label>Password<input value={password} onChange={(event) => setPassword(event.target.value)} type="password" required /></label>
        {error && <div className="error-box">{error}</div>}
        <button className="primary-button" type="submit">Sign in</button>
      </form>
    </section>
  );
}
