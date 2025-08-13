import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: { main: "#2563eb" }, // Blue
    secondary: { main: "#059669" }, // Green
    background: { default: "#f4f8fb" },
  },
  typography: {
    fontFamily: "Roboto, Arial, sans-serif",
  },
});

export default theme;
