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
  MenuItem,
  Avatar,
  CircularProgress,
  Alert,
  Grid,
  Link,
  Divider,
} from "@mui/material";
import {
  Lock,
  Person,
  Email,
  Phone,
  Favorite,
  Home,
  Wc,
  CalendarToday,
  PhotoCamera,
  ContactPhone,
} from "@mui/icons-material";
import { API_ENDPOINTS, makeApiRequest } from "../config/api";

const GENDERS = ["Male", "Female", "Other", "Prefer not to say"];
const RELATIONSHIPS = ["Spouse", "Parent", "Sibling", "Friend", "Other"];
const COUNTRIES = [
  "United States",
  "Canada",
  "United Kingdom",
  "India",
  "Other",
];

function validateEmail(email) {
  return /\S+@\S+\.\S+/.test(email);
}
function validatePhone(phone) {
  return /^\+?\d{10,15}$/.test(phone);
}
function validatePassword(password) {
  return /^(?=.*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{8,}$/.test(password);
}
function calculateAge(dob) {
  if (!dob) return 0;
  const diff = Date.now() - new Date(dob).getTime();
  return Math.abs(new Date(diff).getUTCFullYear() - 1970);
}

export default function PatientRegistration() {
  const [form, setForm] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    dob: "",
    gender: "",
    photo: null,
    street: "",
    city: "",
    state: "",
    zip: "",
    country: "",
    emergencyName: "",
    emergencyRelationship: "",
    emergencyPhone: "",
    password: "",
    confirmPassword: "",
    terms: false,
  });
  const [photoPreview, setPhotoPreview] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [success, setSuccess] = useState(false);

  // Validation
  const validate = () => {
    const newErrors = {};
    if (!form.firstName) newErrors.firstName = "First name required";
    if (!form.lastName) newErrors.lastName = "Last name required";
    if (!form.email || !validateEmail(form.email))
      newErrors.email = "Valid email required";
    if (!form.phone || !validatePhone(form.phone))
      newErrors.phone = "Valid phone required";
    if (!form.dob) newErrors.dob = "Date of birth required";
    if (form.dob && calculateAge(form.dob) < 13)
      newErrors.dob = "You must be at least 13 years old";
    if (!form.gender) newErrors.gender = "Gender required";
    if (!form.street) newErrors.street = "Street address required";
    if (!form.city) newErrors.city = "City required";
    if (!form.state) newErrors.state = "State/Province required";
    if (!form.zip) newErrors.zip = "ZIP/Postal code required";
    if (!form.country) newErrors.country = "Country required";
    if (!form.emergencyName)
      newErrors.emergencyName = "Emergency contact name required";
    if (!form.emergencyRelationship)
      newErrors.emergencyRelationship = "Relationship required";
    if (!form.emergencyPhone || !validatePhone(form.emergencyPhone))
      newErrors.emergencyPhone = "Valid emergency phone required";
    if (
      form.emergencyPhone === form.phone ||
      form.emergencyName === `${form.firstName} ${form.lastName}`
    )
      newErrors.emergencyPhone =
        "Emergency contact must be different from patient";
    if (!form.password || !validatePassword(form.password))
      newErrors.password = "Min 8 chars, 1 number, 1 special char";
    if (form.password !== form.confirmPassword)
      newErrors.confirmPassword = "Passwords must match";
    if (!form.terms) newErrors.terms = "You must accept the terms";
    return newErrors;
  };

  const handleChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    if (type === "checkbox") {
      setForm((f) => ({ ...f, [name]: checked }));
    } else if (type === "file") {
      const file = files[0];
      setForm((f) => ({ ...f, photo: file }));
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => setPhotoPreview(e.target.result);
        reader.readAsDataURL(file);
      } else {
        setPhotoPreview(null);
      }
    } else {
      setForm((f) => ({ ...f, [name]: value }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError("");
    const newErrors = validate();
    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) return;

    setLoading(true);

    try {
      const registrationData = {
        first_name: form.firstName,
        last_name: form.lastName,
        email: form.email,
        phone_number: form.phone,
        date_of_birth: form.dob,
        gender: form.gender,
        address: {
          street: form.street,
          city: form.city,
          state: form.state,
          zip_code: form.zip,
          country: form.country,
        },
        emergency_contact: {
          name: form.emergencyName,
          relationship: form.emergencyRelationship,
          phone_number: form.emergencyPhone,
        },
        password: form.password,
        confirm_password: form.confirmPassword,
      };

      const result = await makeApiRequest(
        API_ENDPOINTS.PATIENT_REGISTER,
        registrationData,
        "POST"
      );

      setLoading(false);

      if (result.success) {
        setSuccess(true);
      } else {
        setFormError(result.error || "Registration failed. Please try again.");
      }
    } catch (err) {
      setLoading(false);
      setFormError("Network error. Please try again.");
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
            minWidth: 340,
            maxWidth: 420,
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
              Registration Successful!
            </Typography>
            <Typography align="center" sx={{ mb: 2 }}>
              Please check your email for verification and next steps.
              <br />
              You may now{" "}
              <Link
                href="/patient-login"
                sx={{ cursor: "pointer", color: "primary.main" }}
              >
                login
              </Link>{" "}
              or go to your dashboard.
            </Typography>
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
        <Avatar sx={{ bgcolor: "#10b981", width: 56, height: 56, mb: 1 }}>
          <Favorite sx={{ color: "#fff", fontSize: 32 }} />
        </Avatar>
        <Typography variant="h4" fontWeight="bold" color="#3b82f6" gutterBottom>
          Welcome to Healthcare Platform
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Create your account to access healthcare services
        </Typography>
      </Box>
      <Box sx={{ display: "flex", justifyContent: "center", mt: 2, mb: 4 }}>
        <Card
          sx={{
            minWidth: 340,
            maxWidth: 600,
            width: "100%",
            boxShadow: 3,
            borderRadius: 3,
          }}
        >
          <CardContent>
            <form onSubmit={handleSubmit} autoComplete="on">
              {/* Personal Info */}
              <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
                Personal Information
              </Typography>
              <Grid container columns={12} spacing={2}>
                <Grid item span={6}>
                  <TextField
                    label="First Name"
                    name="firstName"
                    value={form.firstName}
                    onChange={handleChange}
                    error={!!errors.firstName}
                    helperText={errors.firstName}
                    fullWidth
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Person />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid item span={6}>
                  <TextField
                    label="Last Name"
                    name="lastName"
                    value={form.lastName}
                    onChange={handleChange}
                    error={!!errors.lastName}
                    helperText={errors.lastName}
                    fullWidth
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Person />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid item span={6}>
                  <TextField
                    label="Email Address"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    error={!!errors.email}
                    helperText={errors.email}
                    fullWidth
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Email />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid item span={6}>
                  <TextField
                    label="Phone Number"
                    name="phone"
                    value={form.phone}
                    onChange={handleChange}
                    error={!!errors.phone}
                    helperText={errors.phone}
                    fullWidth
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Phone />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid item span={6}>
                  <TextField
                    label="Date of Birth"
                    name="dob"
                    type="date"
                    value={form.dob}
                    onChange={handleChange}
                    error={!!errors.dob}
                    helperText={errors.dob}
                    fullWidth
                    required
                    InputLabelProps={{ shrink: true }}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <CalendarToday />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid item span={6}>
                  <TextField
                    select
                    label="Gender"
                    name="gender"
                    value={form.gender}
                    onChange={handleChange}
                    error={!!errors.gender}
                    helperText={errors.gender}
                    fullWidth
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Wc />
                        </InputAdornment>
                      ),
                    }}
                  >
                    {GENDERS.map((opt) => (
                      <MenuItem key={opt} value={opt}>
                        {opt}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item span={6}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                    <Avatar
                      src={photoPreview}
                      sx={{ width: 48, height: 48, bgcolor: "secondary.main" }}
                    />
                    <Button
                      variant="outlined"
                      component="label"
                      startIcon={<PhotoCamera />}
                      sx={{ textTransform: "none" }}
                    >
                      Upload Photo
                      <input
                        type="file"
                        accept="image/*"
                        hidden
                        name="photo"
                        onChange={handleChange}
                        aria-label="Profile Photo Upload"
                      />
                    </Button>
                  </Box>
                </Grid>
              </Grid>
              <Divider sx={{ my: 3 }} />
              {/* Address Info */}
              <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
                Address Information
              </Typography>
              <Grid container columns={12} spacing={2}>
                <Grid item span={6}>
                  <TextField
                    label="Street Address"
                    name="street"
                    value={form.street}
                    onChange={handleChange}
                    error={!!errors.street}
                    helperText={errors.street}
                    fullWidth
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Home />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid item span={6}>
                  <TextField
                    label="City"
                    name="city"
                    value={form.city}
                    onChange={handleChange}
                    error={!!errors.city}
                    helperText={errors.city}
                    fullWidth
                    required
                  />
                </Grid>
                <Grid item span={6}>
                  <TextField
                    label="State/Province"
                    name="state"
                    value={form.state}
                    onChange={handleChange}
                    error={!!errors.state}
                    helperText={errors.state}
                    fullWidth
                    required
                  />
                </Grid>
                <Grid item span={6}>
                  <TextField
                    label="ZIP/Postal Code"
                    name="zip"
                    value={form.zip}
                    onChange={handleChange}
                    error={!!errors.zip}
                    helperText={errors.zip}
                    fullWidth
                    required
                  />
                </Grid>
                <Grid item span={6}>
                  <TextField
                    select
                    label="Country"
                    name="country"
                    value={form.country}
                    onChange={handleChange}
                    error={!!errors.country}
                    helperText={errors.country}
                    fullWidth
                    required
                  >
                    {COUNTRIES.map((opt) => (
                      <MenuItem key={opt} value={opt}>
                        {opt}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
              </Grid>
              <Divider sx={{ my: 3 }} />
              {/* Emergency Contact */}
              <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
                Emergency Contact
              </Typography>
              <Grid container columns={12} spacing={2}>
                <Grid item span={6}>
                  <TextField
                    label="Contact Name"
                    name="emergencyName"
                    value={form.emergencyName}
                    onChange={handleChange}
                    error={!!errors.emergencyName}
                    helperText={errors.emergencyName}
                    fullWidth
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <ContactPhone />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid item span={6}>
                  <TextField
                    select
                    label="Relationship"
                    name="emergencyRelationship"
                    value={form.emergencyRelationship}
                    onChange={handleChange}
                    error={!!errors.emergencyRelationship}
                    helperText={errors.emergencyRelationship}
                    fullWidth
                    required
                  >
                    {RELATIONSHIPS.map((opt) => (
                      <MenuItem key={opt} value={opt}>
                        {opt}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item span={6}>
                  <TextField
                    label="Emergency Phone Number"
                    name="emergencyPhone"
                    value={form.emergencyPhone}
                    onChange={handleChange}
                    error={!!errors.emergencyPhone}
                    helperText={errors.emergencyPhone}
                    fullWidth
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Phone />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
              </Grid>
              <Divider sx={{ my: 3 }} />
              {/* Account Security */}
              <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
                Account Security
              </Typography>
              <Grid container columns={12} spacing={2}>
                <Grid item span={6}>
                  <TextField
                    label="Password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    value={form.password}
                    onChange={handleChange}
                    error={!!errors.password}
                    helperText={
                      errors.password || "Min 8 chars, 1 number, 1 special char"
                    }
                    fullWidth
                    required
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
                            {showPassword ? <Lock /> : <Lock />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid item span={6}>
                  <TextField
                    label="Confirm Password"
                    name="confirmPassword"
                    type={showConfirm ? "text" : "password"}
                    value={form.confirmPassword}
                    onChange={handleChange}
                    error={!!errors.confirmPassword}
                    helperText={errors.confirmPassword}
                    fullWidth
                    required
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
                              showConfirm ? "Hide password" : "Show password"
                            }
                            onClick={() => setShowConfirm((s) => !s)}
                            edge="end"
                            tabIndex={-1}
                          >
                            {showConfirm ? <Lock /> : <Lock />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
              </Grid>
              <Box sx={{ mt: 1, mb: 2 }}>
                <Typography
                  variant="caption"
                  color={
                    validatePassword(form.password)
                      ? "success.main"
                      : "error.main"
                  }
                >
                  Password strength:{" "}
                  {validatePassword(form.password) ? "Strong" : "Weak"}
                </Typography>
              </Box>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={form.terms}
                    onChange={handleChange}
                    name="terms"
                    color="primary"
                    inputProps={{ "aria-label": "Accept Terms and Conditions" }}
                  />
                }
                label={
                  <span>
                    I accept the{" "}
                    <Link href="#" underline="hover">
                      Terms & Conditions
                    </Link>{" "}
                    and{" "}
                    <Link href="#" underline="hover">
                      Privacy Policy
                    </Link>
                  </span>
                }
              />
              {formError && (
                <Alert severity="error" sx={{ my: 2 }}>
                  {formError}
                </Alert>
              )}
              <Button
                type="submit"
                fullWidth
                variant="contained"
                color="primary"
                size="large"
                disabled={loading}
                sx={{
                  mt: 2,
                  mb: 1,
                  height: 48,
                  fontWeight: "bold",
                  fontSize: 16,
                }}
                aria-label="Register"
              >
                {loading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  "Register"
                )}
              </Button>
              <Box sx={{ textAlign: "center", mt: 1 }}>
                <Typography variant="body2">
                  Already have an account?{" "}
                  <Link
                    href="/patient-login"
                    sx={{ cursor: "pointer", color: "primary.main" }}
                  >
                    Login
                  </Link>
                </Typography>
              </Box>
            </form>
          </CardContent>
        </Card>
      </Box>
      <Box sx={{ textAlign: "center", color: "text.secondary", pb: 2 }}>
        <Typography variant="caption">
          Your privacy and security are our top priority.
          <br />
          &copy; {new Date().getFullYear()} Healthcare Platform
        </Typography>
      </Box>
    </Box>
  );
}
