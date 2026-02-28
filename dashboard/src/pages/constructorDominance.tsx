import React, { useState, useEffect } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { useTheme } from "@mui/material/styles";
import Plot from "react-plotly.js";

import { get } from "../utils/api";

export const ConstructorDominance = () => {
  const theme = useTheme();
  const [data, setData] = useState<Record<string, unknown>[] | null>(null);

  useEffect(() => {
    get("/dashboard/constructor_wins_by_era").then(setData);
  }, []);

  if (!data || data.length === 0) return null;

  const seasons = [...new Set(data.map((d) => d.season as number))].sort(
    (a, b) => a - b,
  );
  const constructors = [
    ...new Set(data.map((d) => d.constructor_name as string)),
  ];

  const fontColor = theme.palette.mode === "dark" ? "#fff" : "#333";

  const traces = constructors.map((name) => {
    const byName = data.filter((d) => d.constructor_name === name);
    const winsMap = new Map(
      byName.map((d) => [d.season as number, d.wins as number]),
    );
    return {
      x: seasons,
      y: seasons.map((s) => winsMap.get(s) ?? 0),
      name,
      type: "bar" as const,
    };
  });

  return (
    <Box>
      <Typography variant="h6" sx={{ textAlign: "center" }}>
        Constructor Wins by Season
      </Typography>
      <Plot
        data={traces}
        layout={{
          barmode: "stack",
          xaxis: { title: { text: "Season" }, dtick: 1 },
          yaxis: { title: { text: "Wins" } },
          autosize: true,
          font: { color: fontColor },
          legend: { orientation: "h", y: -0.3 },
          margin: { t: 10, b: 100 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
        }}
        useResizeHandler={true}
        style={{ width: "100%", height: "450px" }}
      />
    </Box>
  );
};
