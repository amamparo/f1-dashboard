import React, { useState, useEffect } from "react";
import Box from "@mui/material/Box";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Typography from "@mui/material/Typography";
import { useTheme } from "@mui/material/styles";
import Plot from "react-plotly.js";
import { fetchUtils } from "react-admin";

import { API_BASE_URL } from "../utils/common";

const httpClient = async (url: string, options = {}) => {
  const { status, headers, body, json } = await fetchUtils.fetchJson(
    url,
    options,
  );
  return { status, headers, body, json };
};

export const ChampionshipProgression = () => {
  const theme = useTheme();
  const [season, setSeason] = useState<number | null>(null);
  const [data, setData] = useState<Record<string, unknown>[] | null>(null);

  useEffect(() => {
    const params = season ? `?season=${season}` : "";
    const url = `${API_BASE_URL}/dashboard/championship_progression${params}`;
    setData(null);
    httpClient(url).then(({ json }) => setData(json));
  }, [season]);

  if (!data || data.length === 0) return null;

  const drivers = [...new Set(data.map((d) => d.driver_name as string))];
  const rounds = [...new Set(data.map((d) => d.round as number))].sort(
    (a, b) => a - b,
  );
  const currentSeason = season ?? (data[0].season as number);

  // Find top 10 drivers by final round points
  const finalRound = rounds[rounds.length - 1];
  const finalStandings = data
    .filter((d) => d.round === finalRound)
    .sort((a, b) => (b.points as number) - (a.points as number))
    .slice(0, 10)
    .map((d) => d.driver_name as string);

  const topDrivers = drivers.filter((name) => finalStandings.includes(name));

  const fontColor = theme.palette.mode === "dark" ? "#fff" : "#333";

  const traces = topDrivers.map((driver) => {
    const driverData = data
      .filter((d) => d.driver_name === driver)
      .sort((a, b) => (a.round as number) - (b.round as number));
    return {
      x: driverData.map((d) => d.round),
      y: driverData.map((d) => d.points),
      name: driver,
      type: "scatter" as const,
      mode: "lines+markers" as const,
    };
  });

  const seasons = Array.from(
    { length: currentSeason - 1950 + 1 },
    (_, i) => currentSeason - i,
  );

  return (
    <Box sx={{ position: "relative" }}>
      <Box
        sx={{
          position: "absolute",
          top: -8,
          left: 0,
          right: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1,
          pointerEvents: "none",
        }}
      >
        <Select
          value={currentSeason}
          onChange={(e) => setSeason(e.target.value as number)}
          size="small"
          sx={{ mr: 1, pointerEvents: "auto" }}
        >
          {seasons.map((y) => (
            <MenuItem key={y} value={y}>
              {y}
            </MenuItem>
          ))}
        </Select>
        <Typography variant="h6">Championship Points Progression</Typography>
      </Box>
      <Plot
        data={traces}
        layout={{
          xaxis: { title: { text: "Round" }, dtick: 1 },
          yaxis: { title: { text: "Points" } },
          autosize: true,
          font: { color: fontColor },
          legend: { orientation: "h", y: -0.3 },
          margin: { t: 40, b: 100 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
        }}
        useResizeHandler={true}
        style={{ width: "100%", height: "450px" }}
      />
    </Box>
  );
};
