import { useState, useEffect } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  Avatar,
  Alert,
} from "@mui/material";
import { useNotify, useRedirect } from "react-admin";
import { API_BASE_URL } from "../utils/common";

export const ProfileSettings = () => {
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [avatar, setAvatar] = useState("");
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");
  const notify = useNotify();
  const redirect = useRedirect();

  useEffect(() => {
    const user = localStorage.getItem("user");
    if (user) {
      const parsed = JSON.parse(user);
      setUsername(parsed.username || "");
      setFullName(parsed.fullName || "");
      setAvatar(parsed.avatar || "");
    }
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    const token = localStorage.getItem("token");
    const response = await fetch(`${API_BASE_URL}/auth/me/profile`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ username, full_name: fullName }),
    });

    if (!response.ok) {
      const data = await response.json();
      setError(data.detail || "Failed to update profile");
      return;
    }

    const updated = await response.json();
    const existingUser = JSON.parse(localStorage.getItem("user") || "{}");
    localStorage.setItem(
      "user",
      JSON.stringify({
        ...existingUser,
        id: updated.id,
        fullName: updated.full_name,
        avatar: updated.avatar,
        username: updated.username,
      }),
    );
    setSuccess("Profile updated successfully");
    notify("Profile updated");
  };

  return (
    <Box display="flex" justifyContent="center" alignItems="flex-start" mt={4}>
      <Card sx={{ minWidth: 400, maxWidth: 500 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2} mb={3}>
            <Avatar src={avatar} sx={{ width: 64, height: 64 }} />
            <Typography variant="h5">Profile Settings</Typography>
          </Box>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {success}
            </Alert>
          )}
          <form onSubmit={handleSave}>
            <TextField
              label="Username"
              fullWidth
              margin="normal"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <TextField
              label="Full Name"
              fullWidth
              margin="normal"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
            <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }}>
              Save Changes
            </Button>
          </form>
          <Button
            variant="outlined"
            fullWidth
            sx={{ mt: 2 }}
            onClick={() => redirect("/change-password")}
          >
            Change Password
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
};
