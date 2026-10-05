import React from "react";
import {
  Leaf,
  Lock,
  User,
  ArrowRight,
} from "lucide-react";

import "./Login.css";

function Login({ onLogin, onCreateAccount }) {
  const [farmerName, setFarmerName] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [rememberMe, setRememberMe] = React.useState(true);
  const [error, setError] = React.useState("");
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const handleLogin = async (event) => {
    event.preventDefault();

    const trimmedName = farmerName.trim();

    if (!trimmedName || !password) {
      setError("Enter your farmer name and password.");
      return;
    }

    setError("");
    setIsSubmitting(true);
    try {
      await onLogin(trimmedName, password, rememberMe);
    } catch (loginError) {
      setError(loginError.message || "Unable to sign in.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-page">

      <div className="login-card">

        {/* BRAND */}
        <div className="login-brand">
          <div className="login-brand-icon">
            <Leaf size={26} />
          </div>

          <div>
            <h1>
              AGRI <span>Agent</span>
            </h1>

            <p>AI for Better Harvests</p>
          </div>
        </div>

        {/* HEADING */}
        <div className="login-heading">
          <h2>Welcome back</h2>

          <p>
            Sign in to continue to your farming assistant.
          </p>
        </div>

        {/* FORM */}
        <form
          className="login-form"
          onSubmit={handleLogin}
        >

          {/* FARMER NAME */}
          <label>Farmer Name</label>

          <div className="login-input">
            <User size={18} />

            <input
              type="text"
              placeholder="Enter your name"
              value={farmerName}
              autoComplete="username"
              required
              onChange={(event) =>
                setFarmerName(event.target.value)
              }
            />
          </div>

          {/* PASSWORD */}
          <label>Password</label>

          <div className="login-input">
            <Lock size={18} />

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              autoComplete="current-password"
              required
              onChange={(event) =>
                setPassword(event.target.value)
              }
            />
          </div>

          {/* LOGIN OPTIONS */}
          <div className="login-options">

            <label className="remember">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(event) =>
                  setRememberMe(event.target.checked)
                }
              />
              <span>Remember me</span>
            </label>

            <button type="button">
              Forgot password?
            </button>

          </div>

          {error && (
            <div className="login-error" role="alert">
              {error}
            </div>
          )}

          {/* SIGN IN */}
          <button
            className="login-button"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Signing in..." : "Sign In"}
            <ArrowRight size={18} />
          </button>

        </form>

        {/* REGISTER */}
        <div className="register-section">

          <span>New to AGRI Agent?</span>

          <button
            type="button"
            onClick={onCreateAccount}
          >
            Create Farmer Account
          </button>

        </div>

        {/* FOOTER */}
        <div className="login-footer">
          Secure farmer decision support
        </div>

      </div>

    </div>
  );
}

export default Login;