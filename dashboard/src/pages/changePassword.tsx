import { useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  Alert,
} from "@mui/material";
import { useNotify, useRedirect } from "react-admin";
import { API_BASE_URL } from "../utils/common";

export const ChangePassword = () => {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const notify = useNotify();
  const redirect = useRedirect();

  const isForced = localStorage.getItem("must_change_password") === "true";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    if (newPassword.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    const token = localStorage.getItem("token");
    const response = await fetch(`${API_BASE_URL}/auth/me/password`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      setError(data.detail || "Failed to change password");
      return;
    }

    localStorage.removeItem("must_change_password");
    notify("Password changed successfully");
    redirect("/");
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="80vh"
    >
      <Card sx={{ minWidth: 400, maxWidth: 500 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            {isForced ? "Change Your Password" : "Change Password"}
          </Typography>
          {isForced && (
            <Alert severity="info" sx={{ mb: 2 }}>
              You must change your password before continuing.
            </Alert>
          )}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <form onSubmit={handleSubmit}>
            <TextField
              label="Current Password"
              type="password"
              fullWidth
              margin="normal"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
            />
            <TextField
              label="New Password"
              type="password"
              fullWidth
              margin="normal"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
            <TextField
              label="Confirm New Password"
              type="password"
              fullWidth
              margin="normal"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
            <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }}>
              Change Password
            </Button>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
};
