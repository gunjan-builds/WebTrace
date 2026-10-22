import React, { useState } from 'react';
import { Bot, ArrowRight, Lock, Mail, ShieldCheck, Eye, EyeOff } from 'lucide-react';

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('gauri@webtrace.ai');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      onLogin(); // Dashboard par redirect karega
    }, 800);
  };

  return (
    <div className="app-shell" style={{ display: 'grid', placeItems: 'center', minHeight: '100vh', padding: '20px' }}>
      <div className="panel" style={{ width: '100%', maxWidth: '420px', padding: '32px' }}>
        
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div className="brand-icon" style={{ width: '48px', height: '48px', margin: '0 auto 12px' }}>
            <Bot size={28} color="#ffffff" />
          </div>
          <h2 style={{ fontSize: '24px', margin: '0 0 6px', color: '#ffffff' }}>WebTrace AI</h2>
          <span className="eyebrow">AUTONOMOUS QA CONTROL CENTER</span>
        </div>

        {/* Sign In with Google Button */}
        <button 
          type="button" 
          onClick={onLogin}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '10px',
            padding: '10px 14px',
            background: '#07152b',
            border: '1px solid #1a355e',
            borderRadius: '8px',
            color: '#ffffff',
            fontSize: '13px',
            fontWeight: '500',
            cursor: 'pointer',
            marginBottom: '20px'
          }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24">
            <path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.6l3.1-3.1C17.3 1.7 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.2 9 5 12 5z"/>
            <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.8z"/>
            <path fill="#FBBC05" d="M5.6 14.8c-.2-.7-.4-1.5-.4-2.3s.2-1.6.4-2.3L1.9 7.3C.7 9.7 0 10.8 0 12s.7 2.3 1.9 4.7l3.7-2.9z"/>
            <path fill="#34A853" d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2.2-6.4-5.2L1.9 16c1.8 3.7 5.6 7 10.1 7z"/>
          </svg>
          Sign in with Google
        </button>

        {/* Divider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
          <div style={{ flex: 1, height: '1px', background: '#162e52' }}></div>
          <span style={{ fontSize: '11px', color: '#516b90', textTransform: 'uppercase', letterSpacing: '1px' }}>or continue with</span>
          <div style={{ flex: 1, height: '1px', background: '#162e52' }}></div>
        </div>

        {/* Login Form */}
        <form className="test-form" onSubmit={handleSubmit}>
          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <Mail size={13} color="#62a5ff" /> Email Address
            </label>
            <input 
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              required 
            />
          </div>

          <div style={{ marginTop: '12px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <Lock size={13} color="#62a5ff" /> Password
            </label>
            
            {/* Password Input with Eye Icon Toggle */}
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
              <input 
                type={showPassword ? 'text' : 'password'} 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                required 
                style={{ paddingRight: '40px' }}
              />
              <button 
                type="button" 
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '10px',
                  background: 'transparent',
                  border: 'none',
                  color: '#62a5ff',
                  display: 'flex',
                  alignItems: 'center',
                  padding: '4px'
                }}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button type="submit" className="primary-button" style={{ width: '100%', marginTop: '20px' }} disabled={isLoading}>
            {isLoading ? 'Authenticating...' : 'Sign In to Workspace'}
            {!isLoading && <ArrowRight size={16} />}
          </button>
        </form>

        {/* Footer Note */}
        <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid #162e52', textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: '#64e4c0', fontSize: '11px' }}>
            <ShieldCheck size={14} /> Enterprise Single Sign-On Active
          </div>
        </div>

      </div>
    </div>
  );
}