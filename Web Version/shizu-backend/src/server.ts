import { createHandler } from "graphql-http/lib/use/express";
import { SCHEMA } from "./schema";
import {
  getLedger,
  getLineup,
  getAppThemes,
  getLineups,
  getSettings,
  getFilePath,
  getDirPath,
  getLogoPermissions,
  getRecordingPermissions,
  getExportPermissions,
  getStaticPathPermissions,
  reconstructLogoPath,
  reconstructRecordingPath,
  reconstructExportPath,
} from "./readers";
import {
  addDj,
  addPromo,
  updateDj,
  updatePromo,
  createLineup,
  updateLineup,
  setLineupDjLive,
  swapLineupDJs,
  swapLineupPromos,
  addDjToLineup,
  addPromoToLineup,
  removeDjFromLineup,
  removePromoFromLineup,
  addAppTheme,
  editAppTheme,
  deleteAppTheme,
  setLastThemeIndex,
  deleteDj,
  deletePromo,
  deleteLineup,
  updateSettings,
  exportLineup,
} from "./writers";
import express from "express";
import cors from "cors";

const root = {
  getLedger,
  getLineup,
  getAppThemes,
  getLineups,
  getSettings,
  getFilePath,
  getDirPath,
  getLogoPermissions,
  getRecordingPermissions,
  getExportPermissions,
  reconstructLogoPath,
  reconstructRecordingPath,
  reconstructExportPath,
  addDj,
  addPromo,
  updateDj,
  updatePromo,
  createLineup,
  updateLineup,
  addDjToLineup,
  setLineupDjLive,
  swapLineupDJs,
  swapLineupPromos,
  addPromoToLineup,
  removeDjFromLineup,
  removePromoFromLineup,
  addAppTheme,
  editAppTheme,
  deleteAppTheme,
  setLastThemeIndex,
  deleteDj,
  deletePromo,
  deleteLineup,
  updateSettings,
  exportLineup,
};

const app = express();
app.use(cors()); // For graphql over http
app.use(
  "/graphql",
  createHandler({
    rootValue: root,
    schema: SCHEMA,
  }),
);

// Static permissions dirs
const static_permissions = getStaticPathPermissions();
static_permissions.logos.map((permission) => {
  app.use(
    `/logos/${encodeURIComponent(permission.id)}`,
    express.static(permission.path),
  );
});
static_permissions.recordings.map((permission) => {
  app.use(
    `/recordings/${encodeURIComponent(permission.id)}`,
    express.static(permission.path),
  );
});
static_permissions.exports.map((permission) => {
  app.use(
    `/exports/${encodeURIComponent(permission.id)}`,
    express.static(permission.path),
  );
});

// Listen for graphql
app.listen(4004, () => {
  console.log("Express GraphQL Server Now Running On localhost:4004/graphql");
});
