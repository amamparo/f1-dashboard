import React, { useState, useEffect } from "react";
import Card from "@mui/material/Card";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import Plot from "react-plotly.js";
import { Title, useList, ListContextProvider, DataTable } from "react-admin";

import { get } from "../utils/api";
import { ChampionshipProgression } from "./championshipProgression";
import { ConstructorDominance } from "./constructorDominance";

const TopDriversByWins = () => {
  const [data, setData] = useState(null);
  useEffect(() => {
    get("/dashboard/top_drivers_by_wins", { range: "[0, 9]" }).then(setData);
  }, []);
  const listContext = useList({ data });
  if (data) {
    return (
      <ListContextProvider value={listContext}>
        <DataTable resource="drivers" sx={{ boxShadow: 1 }}>
          <DataTable.Col source="id" />
          <DataTable.Col source="full_name" />
          <DataTable.Col source="nationality" />
          <DataTable.Col source="number_of_wins" />
        </DataTable>
      </ListContextProvider>
    );
  }
  return null;
};

const BasicChart = () => {
  return (
    <Plot
      data={[
        {
          x: [1, 2, 3],
          y: [2, 6, 3],
          type: "scatter",
          mode: "lines+markers",
          marker: { color: "red" },
        },
        { type: "bar", x: [1, 2, 3], y: [2, 5, 3] },
      ]}
      layout={{ title: { text: "A Fancy Plot" } }}
    />
  );
};

export const Dashboard = () => (
  <Card sx={{ m: 2, p: 2 }}>
    <Title title="F1 Dashboard" />
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid size={6}>
          <Typography variant="h4" gutterBottom sx={{ textAlign: "left" }}>
            Top Drivers by Wins
          </Typography>
          <TopDriversByWins />
        </Grid>
        <Grid size={6}>
          <BasicChart />
        </Grid>
        <Grid size={12} sx={{ my: 2 }}>
          <Divider />
        </Grid>
        <Grid size={12}>
          <ChampionshipProgression />
        </Grid>
        <Grid size={12} sx={{ my: 2 }}>
          <Divider />
        </Grid>
        <Grid size={12}>
          <ConstructorDominance />
        </Grid>
      </Grid>
    </Box>
  </Card>
);
