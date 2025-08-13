import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Checkbox,
  FormControlLabel,
  InputAdornment,
  IconButton,
  Link,
  CircularProgress,
  Alert,
  Avatar,
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  Email,
  Phone,
  Lock,
  Favorite,
  Person,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { API_ENDPOINTS, makeApiRequest } from "../config/api";

const isEmail = (value) => /\S+@\S+\.\S+/.test(value);
const isPhone = (value) => /^\+?\d{10,15}$/.test(value);

export default function PatientLogin() {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [touched, setTouched] = useState({
    identifier: false,
    password: false,
  });
  const [success, setSuccess] = useState(false);

  // Validation
  const identifierValid = isEmail(identifier) || isPhone(identifier);
  const passwordValid = password.length >= 6;
  const formValid = identifierValid && passwordValid;

  const handleLogin = async (e) => {
    e.preventDefault();
    setTouched({ identifier: true, password: true });
    setError("");
    if (!formValid) return;

    setLoading(true);

    try {
      const loginData = {
        email: identifier, // Backend expects email field
        password: password,
      };

      const result = await makeApiRequest(
        API_ENDPOINTS.PATIENT_LOGIN,
        loginData,
        "POST"
      );

      setLoading(false);

      if (result.success) {
        // Store token if provided
        if (result.data.token || result.data.access_token) {
          localStorage.setItem(
            "patient_token",
            result.data.token || result.data.access_token
          );
        }
        setSuccess(true);
      } else {
        setError(result.error || "Invalid credentials. Please try again.");
      }
    } catch (err) {
      setLoading(false);
      setError("Network error. Please try again.");
    }
  };

  if (success) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          background: "linear-gradient(135deg, #e0f2fe 0%, #f0fdf4 100%)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Card
          sx={{
            p: 4,
            minWidth: 320,
            maxWidth: 400,
            boxShadow: 3,
            borderRadius: 3,
          }}
        >
          <CardContent>
            <Typography
              variant="h5"
              color="primary"
              fontWeight="bold"
              align="center"
              gutterBottom
            >
              Welcome!
            </Typography>
            <Typography align="center" sx={{ mb: 2 }}>
              Login successful. Redirecting to your dashboard...
            </Typography>
            <Box sx={{ display: "flex", justifyContent: "center", mt: 2 }}>
              <CircularProgress color="primary" />
            </Box>
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #e0f2fe 0%, #f0fdf4 100%)",
      }}
    >
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          pt: 4,
        }}
      >
        <Avatar sx={{ bgcolor: "#3b82f6", width: 56, height: 56, mb: 1 }}>
          <Favorite sx={{ color: "#fff", fontSize: 32 }} />
        </Avatar>
        <Typography variant="h4" fontWeight="bold" color="#3b82f6" gutterBottom>
          Patient Login
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Welcome back! Please sign in to your account.
        </Typography>
      </Box>
      <Box sx={{ display: "flex", justifyContent: "center", mt: 2, mb: 4 }}>
        <Card
          sx={{
            minWidth: 320,
            maxWidth: 400,
            width: "100%",
            boxShadow: 3,
            borderRadius: 3,
          }}
        >
          <CardContent>
            <form autoComplete="on" onSubmit={handleLogin}>
              <TextField
                fullWidth
                label="Email or Phone Number"
                placeholder="e.g. john@email.com or +1234567890"
                margin="normal"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                onBlur={() => setTouched((t) => ({ ...t, identifier: true }))}
                error={touched.identifier && !identifierValid}
                helperText={
                  touched.identifier && !identifierValid
                    ? "Enter a valid email or phone number"
                    : " "
                }
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      {isEmail(identifier) ? <Email /> : <Phone />}
                    </InputAdornment>
                  ),
                  inputProps: {
                    "aria-label": "Email or Phone Number",
                    autoComplete: "username",
                  },
                }}
                required
              />
              <TextField
                fullWidth
                label="Password"
                placeholder="Enter your password"
                margin="normal"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onBlur={() => setTouched((t) => ({ ...t, password: true }))}
                error={touched.password && !passwordValid}
                helperText={
                  touched.password && !passwordValid
                    ? "Password must be at least 6 characters"
                    : " "
                }
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label={
                          showPassword ? "Hide password" : "Show password"
                        }
                        onClick={() => setShowPassword((s) => !s)}
                        edge="end"
                        tabIndex={-1}
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                  inputProps: {
                    "aria-label": "Password",
                    autoComplete: "current-password",
                  },
                }}
                required
              />
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  mb: 1,
                }}
              >
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      color="primary"
                      inputProps={{ "aria-label": "Remember Me" }}
                    />
                  }
                  label="Remember Me"
                />
                <Link
                  component="button"
                  variant="body2"
                  tabIndex={0}
                  underline="hover"
                  sx={{ color: "#10b981", fontWeight: 500 }}
                >
                  Forgot Password?
                </Link>
              </Box>
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{
                  mt: 1,
                  mb: 2,
                  height: 48,
                  fontWeight: "bold",
                  fontSize: 16,
                  background: "#3b82f6",
                  "&:hover": { background: "#2563eb" },
                }}
                aria-label="Login"
                disabled={!formValid || loading}
              >
                {loading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  "Login"
                )}
              </Button>
            </form>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <Link
                component="button"
                variant="body2"
                tabIndex={0}
                underline="hover"
                sx={{ color: "#3b82f6", fontWeight: 500 }}
              >
                New patient? Register
              </Link>
              <Link
                href="#"
                variant="body2"
                underline="hover"
                sx={{ color: "text.secondary" }}
              >
                Need Help?
              </Link>
            </Box>
            <Box sx={{ textAlign: "center", mt: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Your privacy and security are our top priority.
                <br />
                &copy; {new Date().getFullYear()} Healthcare Platform
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}
