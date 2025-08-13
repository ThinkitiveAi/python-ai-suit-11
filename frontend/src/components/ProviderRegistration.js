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
  LocalHospital,
  PhotoCamera,
  Business,
  LocationOn,
  Work,
  Visibility,
  VisibilityOff,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { API_ENDPOINTS, makeApiRequest } from "../config/api";

const SPECIALIZATIONS = [
  "Cardiology",
  "Dermatology",
  "Pediatrics",
  "General Medicine",
  "Orthopedics",
  "Neurology",
  "Psychiatry",
  "Radiology",
  "Surgery",
  "Other",
];
const PRACTICE_TYPES = [
  "Private Practice",
  "Hospital",
  "Clinic",
  "Group Practice",
  "Other",
];

function validateEmail(email) {
  return /\S+@\S+\.\S+/.test(email);
}
function validatePhone(phone) {
  return /^\+?\d{10,15}$/.test(phone);
}
function validatePassword(password) {
  // At least 8 chars, 1 number, 1 special char
  return /^(?=.*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{8,}$/.test(password);
}

export default function ProviderRegistration() {
  const [form, setForm] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    photo: null,
    license: "",
    specialization: "",
    experience: "",
    degree: "",
    clinic: "",
    address: "",
    practiceType: "",
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
  const navigate = useNavigate();

  // Validation
  const validate = () => {
    const newErrors = {};
    if (!form.firstName) newErrors.firstName = "First name required";
    if (!form.lastName) newErrors.lastName = "Last name required";
    if (!form.email || !validateEmail(form.email))
      newErrors.email = "Valid email required";
    if (!form.phone || !validatePhone(form.phone))
      newErrors.phone = "Valid phone required";
    if (!form.license) newErrors.license = "Medical license required";
    if (!form.specialization)
      newErrors.specialization = "Specialization required";
    if (!form.experience || isNaN(form.experience) || form.experience < 0)
      newErrors.experience = "Valid years required";
    if (!form.degree) newErrors.degree = "Degree required";
    if (!form.clinic) newErrors.clinic = "Clinic/Hospital name required";
    if (!form.street) newErrors.street = "Street address required";
    if (!form.city) newErrors.city = "City required";
    if (!form.state) newErrors.state = "State required";
    if (!form.zip) newErrors.zip = "ZIP code required";
    if (!form.practiceType) newErrors.practiceType = "Practice type required";
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
      const payload = {
        first_name: form.firstName,
        last_name: form.lastName,
        email: form.email,
        phone_number: form.phone,
        password: form.password,
        confirm_password: form.confirmPassword,
        specialization: form.specialization,
        license_number: form.license,
        years_of_experience: Number(form.experience),
        clinic_address: {
          street: form.street,
          city: form.city,
          state: form.state,
          zip: form.zip,
        },
      };
      const result = await makeApiRequest(
        API_ENDPOINTS.PROVIDER_REGISTER,
        payload,
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
      setFormError("Network or server error. Please try again.");
    }
  };

  if (success) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          background: "#f4f8fb",
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
                onClick={() => navigate("/")}
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
    <Box sx={{ minHeight: "100vh", background: "#f4f8fb" }}>
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          pt: 4,
        }}
      >
        <LocalHospital sx={{ fontSize: 48, color: "primary.main", mb: 1 }} />
        <Typography
          variant="h4"
          fontWeight="bold"
          color="primary.main"
          gutterBottom
        >
          Provider Registration
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Create your professional profile
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
              {/* Professional Info */}
              <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
                Professional Information
              </Typography>
              <Grid container columns={12} spacing={2}>
                <Grid item span={6}>
                  <TextField
                    label="Medical License Number"
                    name="license"
                    value={form.license}
                    onChange={handleChange}
                    error={!!errors.license}
                    helperText={errors.license}
                    fullWidth
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <LocalHospital />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid item span={6}>
                  <TextField
                    select
                    label="Specialization"
                    name="specialization"
                    value={form.specialization}
                    onChange={handleChange}
                    error={!!errors.specialization}
                    helperText={errors.specialization}
                    fullWidth
                    required
                  >
                    {SPECIALIZATIONS.map((opt) => (
                      <MenuItem key={opt} value={opt}>
                        {opt}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item span={6}>
                  <TextField
                    label="Years of Experience"
                    name="experience"
                    type="number"
                    value={form.experience}
                    onChange={handleChange}
                    error={!!errors.experience}
                    helperText={errors.experience}
                    fullWidth
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Work />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid item span={6}>
                  <TextField
                    label="Medical Degree/Qualifications"
                    name="degree"
                    value={form.degree}
                    onChange={handleChange}
                    error={!!errors.degree}
                    helperText={errors.degree}
                    fullWidth
                    required
                  />
                </Grid>
              </Grid>
              <Divider sx={{ my: 3 }} />
              {/* Practice Info */}
              <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
                Practice Information
              </Typography>
              <Grid container columns={12} spacing={2}>
                <Grid item span={6}>
                  <TextField
                    label="Clinic/Hospital Name"
                    name="clinic"
                    value={form.clinic}
                    onChange={handleChange}
                    error={!!errors.clinic}
                    helperText={errors.clinic}
                    fullWidth
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Business />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid item span={12}>
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
                          <LocationOn />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid item span={4}>
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
                <Grid item span={4}>
                  <TextField
                    label="State"
                    name="state"
                    value={form.state}
                    onChange={handleChange}
                    error={!!errors.state}
                    helperText={errors.state}
                    fullWidth
                    required
                  />
                </Grid>
                <Grid item span={4}>
                  <TextField
                    label="ZIP Code"
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
                    label="Practice Type"
                    name="practiceType"
                    value={form.practiceType}
                    onChange={handleChange}
                    error={!!errors.practiceType}
                    helperText={errors.practiceType}
                    fullWidth
                    required
                  >
                    {PRACTICE_TYPES.map((opt) => (
                      <MenuItem key={opt} value={opt}>
                        {opt}
                      </MenuItem>
                    ))}
                  </TextField>
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
                            {showPassword ? <VisibilityOff /> : <Visibility />}
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
                            {showConfirm ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
              </Grid>
              {/* Password Strength Indicator */}
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
                    onClick={() => navigate("/")}
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
          Need help? <Link href="#">Contact Support</Link>
        </Typography>
      </Box>
    </Box>
  );
}
