import {
  Admin,
  Resource,
  ListGuesser,
  ShowGuesser,
  CustomRoutes,
} from "react-admin";
import { Route } from "react-router-dom";

import PersonIcon from "@mui/icons-material/Person";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import SportsScoreIcon from "@mui/icons-material/SportsScore";
import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import RouteIcon from "@mui/icons-material/Route";
import EmojiFlagsIcon from "@mui/icons-material/EmojiFlags";
import FormatListNumberedIcon from "@mui/icons-material/FormatListNumbered";
import Groups3Icon from "@mui/icons-material/Groups3";
import Filter1Icon from "@mui/icons-material/Filter1";
import CheckBoxIcon from "@mui/icons-material/CheckBox";
import PeopleIcon from "@mui/icons-material/People";
import { Dashboard } from "./pages/dashboard";
import { Layout } from "./Layout";

import { authProvider } from "./authProvider";
import { dataProvider } from "./dataProvider";

import { RaceList, RaceShow } from "./pages/races";
import { DriverList, DriverShow } from "./pages/drivers";
import { UserList, UserCreate, UserEdit } from "./pages/users";
import { ChangePassword } from "./pages/changePassword";
import { ProfileSettings } from "./pages/profile";

export const App = () => (
  <Admin
    layout={Layout}
    dashboard={Dashboard}
    dataProvider={dataProvider}
    authProvider={authProvider}
  >
    {(permissions) => (
      <>
        <CustomRoutes>
          <Route path="/change-password" element={<ChangePassword />} />
          <Route path="/profile" element={<ProfileSettings />} />
        </CustomRoutes>
        <Resource
          icon={EmojiFlagsIcon}
          name="races"
          list={RaceList}
          show={RaceShow}
        />
        <Resource
          icon={PersonIcon}
          name="drivers"
          list={DriverList}
          show={DriverShow}
        />
        <Resource
          icon={Filter1Icon}
          name="driver_standings"
          list={ListGuesser}
          show={ShowGuesser}
        />
        <Resource
          icon={RouteIcon}
          name="circuits"
          list={ListGuesser}
          show={ShowGuesser}
        />
        <Resource
          icon={EmojiEventsIcon}
          name="results"
          list={ListGuesser}
          show={ShowGuesser}
        />
        <Resource
          icon={SportsScoreIcon}
          name="qualifying"
          list={ListGuesser}
          show={ShowGuesser}
        />
        <Resource
          icon={DirectionsCarIcon}
          name="constructors"
          list={ListGuesser}
          show={ShowGuesser}
        />
        <Resource
          icon={FormatListNumberedIcon}
          name="constructor_standings"
          list={ListGuesser}
          show={ShowGuesser}
        />
        <Resource
          icon={Groups3Icon}
          name="constructor_results"
          list={ListGuesser}
          show={ShowGuesser}
        />
        <Resource
          icon={CheckBoxIcon}
          name="status"
          list={ListGuesser}
          show={ShowGuesser}
        />
        {permissions === "admin" && (
          <Resource
            icon={PeopleIcon}
            name="users"
            list={UserList}
            create={UserCreate}
            edit={UserEdit}
          />
        )}
      </>
    )}
  </Admin>
);
