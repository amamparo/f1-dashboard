import React, { useState, useEffect } from "react";
import Card from "@mui/material/Card";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import Plot from "react-plotly.js";
import { stringify } from "query-string";

import {
  Title,
  useList,
  ListContextProvider,
  DataTable,
  fetchUtils,
} from "react-admin";

import { API_BASE_URL } from "../utils/common";

const httpClient = async (url, options = {}) => {
  const { status, headers, body, json } = await fetchUtils.fetchJson(
    url,
    options,
  );
  return { status, headers, body, json };
};

const TopDriversByWins = () => {
  const query = {
    range: "[0, 9]",
  };
  const url = `${API_BASE_URL}/dashboard/top_drivers_by_wins?${stringify(query)}`;
  const options = {
    method: "GET",
    headers: new Headers({
      Accept: "application/json",
    }),
  };
  const [data, setData] = useState(null);
  useEffect(() => {
    httpClient(url, options).then(({ json }) => {
      setData(json);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
      </Grid>
    </Box>
  </Card>
);
