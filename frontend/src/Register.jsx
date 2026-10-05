import React from "react";
import {
  Leaf,
  User,
  Lock,
  ArrowRight,
  ArrowLeft,
  MapPin,
  CalendarDays,
  Sprout,
  Mountain,
} from "lucide-react";

import "./Register.css";

function Register({ onBackToLogin, onAccountCreated }) {
  const [farmerName, setFarmerName] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");

  const [crop, setCrop] = React.useState("");
  const [soilType, setSoilType] = React.useState("");
  const [plantingDate, setPlantingDate] = React.useState("");

  const [placeName, setPlaceName] = React.useState("");
  const [pincode, setPincode] = React.useState("");

  const [error, setError] = React.useState("");
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const soilOptions = [
    {
      label: "Red, loose soil",
      value: "Red Loam",
    },
    {
      label: "Dark, rich soil",
      value: "Black Soil",
    },
    {
      label: "Light, sandy soil",
      value: "Sandy Soil",
    },
    {
      label: "Sticky, heavy soil",
      value: "Clay Soil",
    },
    {
      label: "Light brown, fertile soil",
      value: "Alluvial Soil",
    },
  ];

  const handleRegister = async (event) => {
    event.preventDefault();

    setError("");

    if (
      !farmerName.trim() ||
      !password ||
      !confirmPassword ||
      !crop ||
      !soilType ||
      !plantingDate ||
      !placeName.trim() ||
      !pincode.trim()
    ) {
      setError("Please fill in all fields.");
      return;
    }

    if (password.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (!/^\d{6}$/.test(pincode.trim())) {
      setError("Please enter a valid 6-digit pincode.");
      return;
    }

    setIsSubmitting(true);
    try {
      await onAccountCreated({
        name: farmerName.trim(),
        password,
        crop,
        soil_type: soilType,
        planting_date: plantingDate,
        place_name: placeName.trim(),
        pincode: pincode.trim(),
      });
    } catch (registrationError) {
      setError(
        registrationError.message ||
          "Unable to create the farmer account."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-page">

      <div className="login-card register-card">

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
          <h2>Create your account</h2>

          <p>
            Create your farmer profile to get personalized
            agricultural support.
          </p>
        </div>

        {/* FORM */}
        <form
          className="login-form"
          onSubmit={handleRegister}
        >

          {/* FARMER NAME */}
          <label>Farmer Name</label>

          <div className="login-input">
            <User size={18} />

            <input
              type="text"
              placeholder="Enter your name"
              value={farmerName}
              autoComplete="name"
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
              placeholder="Create a password"
              value={password}
              autoComplete="new-password"
              required
              onChange={(event) =>
                setPassword(event.target.value)
              }
            />
          </div>

          {/* CONFIRM PASSWORD */}
          <label>Confirm Password</label>

          <div className="login-input">
            <Lock size={18} />

            <input
              type="password"
              placeholder="Confirm your password"
              value={confirmPassword}
              autoComplete="new-password"
              required
              onChange={(event) =>
                setConfirmPassword(event.target.value)
              }
            />
          </div>

          {/* PRIMARY CROP */}
          <label>Primary Crop</label>

          <div className="login-input">
            <Sprout size={18} />

            <select
              value={crop}
              required
              onChange={(event) =>
                setCrop(event.target.value)
              }
            >
              <option value="">
                Select your primary crop
              </option>

              <option value="Tomato">Tomato</option>
              <option value="Brinjal">Brinjal</option>
              <option value="Chilli">Chilli</option>
              <option value="Okra">Okra</option>
            </select>
          </div>

          {/* SOIL TYPE */}
          <label>Soil Type</label>

          <div className="login-input">
            <Mountain size={18} />

            <select
              value={soilType}
              required
              onChange={(event) =>
                setSoilType(event.target.value)
              }
            >
              <option value="">
                Select your soil type
              </option>

              {soilOptions.map((soil) => (
                <option
                  key={soil.value}
                  value={soil.value}
                >
                  {soil.label}
                </option>
              ))}
            </select>
          </div>

          {/* PLANTING DATE */}
          <label>Planting Date</label>

          <div className="login-input">
            <CalendarDays size={18} />

            <input
              type="date"
              value={plantingDate}
              required
              onChange={(event) =>
                setPlantingDate(event.target.value)
              }
            />
          </div>

          {/* PLACE / LOCATION */}
          <label>Location / Place</label>

          <div className="login-input">
            <MapPin size={18} />

            <input
              type="text"
              placeholder="Enter your village, town or city"
              value={placeName}
              required
              onChange={(event) =>
                setPlaceName(event.target.value)
              }
            />
          </div>

          {/* PINCODE */}
          <label>Pincode</label>

          <div className="login-input">
            <MapPin size={18} />

            <input
              type="text"
              inputMode="numeric"
              maxLength={6}
              placeholder="Enter 6-digit pincode"
              value={pincode}
              required
              onChange={(event) =>
                setPincode(
                  event.target.value.replace(/\D/g, "")
                )
              }
            />
          </div>

          {/* ERROR */}
          {error && (
            <div
              style={{
                marginTop: "-5px",
                marginBottom: "18px",
                fontSize: "12px",
                color: "#b85c5c",
                textAlign: "center",
              }}
            >
              {error}
            </div>
          )}

          {/* CREATE ACCOUNT */}
          <button
            className="login-button"
            type="submit"
            disabled={isSubmitting}
          >
          {isSubmitting ? "Creating account..." : "Create Account"}
            <ArrowRight size={18} />
          </button>

        </form>

        {/* BACK TO LOGIN */}
        <div className="register-section">

          <span>Already have an account?</span>

          <button
            type="button"
            onClick={onBackToLogin}
          >
            <ArrowLeft
              size={13}
              style={{
                verticalAlign: "middle",
                marginRight: "3px",
              }}
            />
            Sign In
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

export default Register;