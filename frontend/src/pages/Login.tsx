/**
 * StartupOS AI — Login / Register Page
 * 
 * Glassmorphism card on dark background, matches Landing page aesthetic.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function Login() {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register, error, clearError } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (isRegister) {
        await register(email, password, name || undefined);
      } else {
        await login(email, password);
      }
      navigate('/dashboard');
    } catch {
      // Error is set in auth context
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0f 0%, #12121f 50%, #0a0a0f 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: "'Inter', system-ui, sans-serif",
      padding: '2rem',
    }}>
      <div style={{
        width: '100%',
        maxWidth: '440px',
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            fontSize: '1.8rem',
            fontWeight: 800,
            background: 'linear-gradient(135deg, #7c3aed, #06b6d4)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '-0.02em',
          }}>
            StartupOS
          </div>
          <div style={{ color: '#64748b', fontSize: '0.85rem', marginTop: '0.25rem' }}>
            AI-Powered Business Planning
          </div>
        </div>

        {/* Card */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '1.25rem',
          padding: '2.5rem',
          backdropFilter: 'blur(20px)',
        }}>
          <h2 style={{
            color: '#f1f5f9',
            fontSize: '1.5rem',
            fontWeight: 700,
            margin: '0 0 0.5rem 0',
          }}>
            {isRegister ? 'Create Account' : 'Welcome Back'}
          </h2>
          <p style={{ color: '#64748b', fontSize: '0.9rem', margin: '0 0 2rem 0' }}>
            {isRegister
              ? 'Start building your startup blueprint'
              : 'Sign in to your StartupOS dashboard'
            }
          </p>

          {error && (
            <div style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '0.75rem',
              padding: '0.75rem 1rem',
              marginBottom: '1.5rem',
              color: '#fca5a5',
              fontSize: '0.85rem',
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {isRegister && (
              <div style={{ marginBottom: '1.25rem' }}>
                <label style={labelStyle}>Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder="John Doe"
                  style={inputStyle}
                />
              </div>
            )}

            <div style={{ marginBottom: '1.25rem' }}>
              <label style={labelStyle}>Email</label>
              <input
                type="email"
                value={email}
                onChange={e => { setEmail(e.target.value); clearError(); }}
                placeholder="you@example.com"
                required
                style={inputStyle}
              />
            </div>

            <div style={{ marginBottom: '2rem' }}>
              <label style={labelStyle}>Password</label>
              <input
                type="password"
                value={password}
                onChange={e => { setPassword(e.target.value); clearError(); }}
                placeholder={isRegister ? 'Min 8 chars, 1 letter, 1 number' : '••••••••'}
                required
                minLength={8}
                style={inputStyle}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '0.9rem',
                background: loading
                  ? 'rgba(124, 58, 237, 0.3)'
                  : 'linear-gradient(135deg, #7c3aed, #6d28d9)',
                color: '#fff',
                border: 'none',
                borderRadius: '0.75rem',
                fontSize: '0.95rem',
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                letterSpacing: '0.02em',
              }}
            >
              {loading
                ? '...'
                : isRegister ? 'Create Account' : 'Sign In'
              }
            </button>
          </form>

          <div style={{
            textAlign: 'center',
            marginTop: '1.5rem',
            color: '#64748b',
            fontSize: '0.85rem',
          }}>
            {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              onClick={() => { setIsRegister(!isRegister); clearError(); }}
              style={{
                background: 'none',
                border: 'none',
                color: '#7c3aed',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '0.85rem',
                textDecoration: 'underline',
                textUnderlineOffset: '2px',
              }}
            >
              {isRegister ? 'Sign In' : 'Sign Up'}
            </button>
          </div>
        </div>

        {/* Back to landing */}
        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <button
            onClick={() => navigate('/')}
            style={{
              background: 'none',
              border: 'none',
              color: '#475569',
              cursor: 'pointer',
              fontSize: '0.8rem',
            }}
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}

const labelStyle: React.CSSProperties = {
  display: 'block',
  color: '#94a3b8',
  fontSize: '0.8rem',
  fontWeight: 500,
  marginBottom: '0.4rem',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.8rem 1rem',
  background: 'rgba(255, 255, 255, 0.04)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '0.6rem',
  color: '#f1f5f9',
  fontSize: '0.95rem',
  outline: 'none',
  transition: 'border-color 0.2s',
  boxSizing: 'border-box',
};
