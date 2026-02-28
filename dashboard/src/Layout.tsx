import { forwardRef, type ReactNode } from "react";
import {
  Layout as RALayout,
  AppBar,
  CheckForApplicationUpdate,
  UserMenu,
  Logout,
} from "react-admin";
import { useUserMenu } from "ra-ui-materialui";
import { MenuItem, ListItemIcon, ListItemText } from "@mui/material";
import SettingsIcon from "@mui/icons-material/Settings";
import { useNavigate, useLocation, Navigate } from "react-router-dom";

const ProfileMenuItem = forwardRef<HTMLLIElement>(
  function ProfileMenuItem(props, ref) {
    const navigate = useNavigate();
    const { onClose } = useUserMenu();
    return (
      <MenuItem
        {...props}
        ref={ref}
        onClick={() => {
          navigate("/profile");
          onClose();
        }}
      >
        <ListItemIcon>
          <SettingsIcon fontSize="small" />
        </ListItemIcon>
        <ListItemText>Profile Settings</ListItemText>
      </MenuItem>
    );
  },
);

const MyUserMenu = () => (
  <UserMenu>
    <ProfileMenuItem />
    <Logout />
  </UserMenu>
);

const MyAppBar = () => <AppBar userMenu={<MyUserMenu />} />;

const ForcePasswordChange = ({ children }: { children: ReactNode }) => {
  const location = useLocation();
  if (
    localStorage.getItem("must_change_password") === "true" &&
    location.pathname !== "/change-password"
  ) {
    return <Navigate to="/change-password" replace />;
  }
  return <>{children}</>;
};

export const Layout = ({ children }: { children: ReactNode }) => (
  <RALayout appBar={MyAppBar}>
    <ForcePasswordChange>{children}</ForcePasswordChange>
    <CheckForApplicationUpdate />
  </RALayout>
);
