import { useState } from "react";
import {
  List,
  Datagrid,
  TextField,
  BooleanField,
  ImageField,
  Edit,
  SimpleForm,
  TextInput,
  SelectInput,
  Create,
  useNotify,
  useRedirect,
  useDataProvider,
} from "react-admin";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
} from "@mui/material";

export const UserList = () => (
  <List>
    <Datagrid rowClick="edit">
      <ImageField source="avatar" label="" sortable={false} />
      <TextField source="username" />
      <TextField source="full_name" />
      <TextField source="role" />
      <BooleanField source="is_active" label="Active" />
    </Datagrid>
  </List>
);

const roleChoices = [
  { id: "admin", name: "Admin" },
  { id: "member", name: "Member" },
];

export const UserEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="username" />
      <TextInput source="full_name" />
      <SelectInput source="role" choices={roleChoices} />
    </SimpleForm>
  </Edit>
);

export const UserCreate = () => {
  const [open, setOpen] = useState(false);
  const [initialPassword, setInitialPassword] = useState("");
  const notify = useNotify();
  const redirect = useRedirect();
  const dataProvider = useDataProvider();

  const handleSubmit = async (data: {
    username: string;
    full_name: string;
  }) => {
    try {
      const result = await dataProvider.create("users", { data });
      setInitialPassword(result.data.initial_password);
      setOpen(true);
    } catch {
      notify("Failed to create user", { type: "error" });
    }
  };

  const handleClose = () => {
    setOpen(false);
    redirect("list", "users");
  };

  return (
    <>
      <Create>
        <SimpleForm onSubmit={handleSubmit}>
          <TextInput source="username" required />
          <TextInput source="full_name" label="Full Name" required />
          <SelectInput
            source="role"
            choices={roleChoices}
            defaultValue="member"
            required
          />
        </SimpleForm>
      </Create>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>User Created</DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            The user has been created. Share the initial password with them —
            they will be prompted to change it on first login.
          </Typography>
          <Typography
            variant="h6"
            sx={{
              fontFamily: "monospace",
              bgcolor: "action.hover",
              p: 1.5,
              borderRadius: 1,
              textAlign: "center",
            }}
          >
            {initialPassword}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} variant="contained">
            Done
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};
