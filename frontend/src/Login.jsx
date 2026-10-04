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

  const handleLogin = (event) => {
    event.preventDefault();

    const trimmedName = farmerName.trim();

    if (!trimmedName || !password) {
      return;
    }

    /*
     * Backend integration:
     *
     * The backend will use:
     * get_farmer_by_name(name, password)
     *
     * and return the complete farmer profile:
     * id, name, crop, soil_type, planting_date,
     * place_name, pincode, lat, lon, growth_stage
     *
     * The password must never be stored or displayed
     * after successful login.
     */
    if (onLogin) {
      onLogin(trimmedName, password);
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
              onChange={(event) =>
                setPassword(event.target.value)
              }
            />
          </div>

          {/* LOGIN OPTIONS */}
          <div className="login-options">

            <label className="remember">
              <input type="checkbox" />
              <span>Remember me</span>
            </label>

            <button type="button">
              Forgot password?
            </button>

          </div>

          {/* SIGN IN */}
          <button
            className="login-button"
            type="submit"
          >
            Sign In
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