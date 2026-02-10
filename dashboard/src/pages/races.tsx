import {
  DataTable,
  DateField,
  List,
  NumberField,
  ReferenceField,
  Show,
  TabbedShowLayout,
  TextField,
  UrlField,
} from "react-admin";

export const RaceList = () => (
  <List>
    <DataTable>
      <DataTable.Col source="id" />
      <DataTable.NumberCol source="year" />
      <DataTable.NumberCol source="round" />
      <DataTable.Col source="circuit_id">
        <ReferenceField source="circuit_id" reference="circuits" />
      </DataTable.Col>
      <DataTable.Col source="name" />
      <DataTable.Col source="date">
        <DateField source="date" />
      </DataTable.Col>
      <DataTable.Col source="time" />
      <DataTable.Col source="url">
        <UrlField source="url" />
      </DataTable.Col>
      <DataTable.Col source="fp1_date" />
      <DataTable.Col source="fp1_time" />
      <DataTable.Col source="fp2_date" />
      <DataTable.Col source="fp2_time" />
      <DataTable.Col source="fp3_date" />
      <DataTable.Col source="fp3_time" />
      <DataTable.Col source="quali_date" />
      <DataTable.Col source="quali_time" />
      <DataTable.Col source="sprint_date" />
      <DataTable.Col source="sprint_time" />
    </DataTable>
  </List>
);

export const RaceShow = () => (
  <Show>
    <TabbedShowLayout>
      <TabbedShowLayout.Tab label="summary">
        <TextField source="id" />
        <NumberField source="year" />
        <NumberField source="round" />
        <ReferenceField source="circuit_id" reference="circuits" />
        <TextField source="name" />
        <DateField source="date" />
        <TextField source="time" />
        <UrlField source="url" />
        <TextField source="fp1_date" />
        <TextField source="fp1_time" />
        <TextField source="fp2_date" />
        <TextField source="fp2_time" />
        <TextField source="fp3_date" />
        <TextField source="fp3_time" />
        <TextField source="quali_date" />
        <TextField source="quali_time" />
        <TextField source="sprint_date" />
        <TextField source="sprint_time" />
      </TabbedShowLayout.Tab>
      <TabbedShowLayout.Tab label="circuit" path="circuit">
        <div>Please add information about the circuit used in this race!</div>
      </TabbedShowLayout.Tab>
      <TabbedShowLayout.Tab label="drivers" path="drivers">
        <div>Please add information about the drivers in this race!</div>
      </TabbedShowLayout.Tab>
      <TabbedShowLayout.Tab label="contructors" path="contructors">
        <div>Please add information about the contructors in this race!</div>
      </TabbedShowLayout.Tab>
    </TabbedShowLayout>
  </Show>
);
