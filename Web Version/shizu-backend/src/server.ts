import * as express_graphql from "express-graphql";
import { SCHEMA } from "./schema";
import {
  getLedger,
  getLineup,
  getAppThemes,
  getLineups,
  getSettings,
  getFilePath,
  getDirPath
} from "./readers";
import {
  addDj,
  addPromo,
  updateDj,
  updatePromo,
  createLineup,
  updateLineup,
  addAppTheme,
  editAppTheme,
  deleteAppTheme,
  setLastThemeIndex,
  deleteDj,
  deletePromo,
  deleteLineup,
  updateSettings,
  exportLineup
} from "./writers";
const express = require("express");
import cors from "cors";

const root = {
  getLedger,
  getLineup,
  getAppThemes,
  getLineups,
  getSettings,
  getFilePath,
  getDirPath,
  addDj,
  addPromo,
  updateDj,
  updatePromo,
  createLineup,
  updateLineup,
  addAppTheme,
  editAppTheme,
  deleteAppTheme,
  setLastThemeIndex,
  deleteDj,
  deletePromo,
  deleteLineup,
  updateSettings,
  exportLineup
};

const app = express();
app.use(cors()); // For graphql over http
app.use(
  "/graphql",
  express_graphql.graphqlHTTP({
    graphiql: true,
    rootValue: root,
    schema: SCHEMA,
  }),
);

app.listen(4000, () => {
  console.log("Express GraphQL Server Now Running On localhost:4000/graphql");
});
