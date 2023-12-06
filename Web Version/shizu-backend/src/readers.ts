import path, { join, resolve, basename, parse } from "path";
import {
  readdirSync,
  Dirent,
  existsSync,
  readFileSync,
  writeFileSync,
  mkdirSync,
} from "fs";
import type { ILedger, ILineup, ISettings, ITheme } from "./types";
const dialog = require("node-file-dialog");

const SETTINGS_FILE = join(resolve("."), "settings.json");
const APP_THEMES_FILE = join(resolve("."), "themes.json");
const DEFAULT_SETTINGS: ISettings = {
  ledger_path: join(resolve("."), "ledger.json"),
  lineups_dir: join(resolve("."), "lineups"),
  theme_index: 0,
};

export const getLedger = () => {
  const path = JSON.parse(readFileSync(SETTINGS_FILE, "utf-8")).ledger_path;

  if (!existsSync(path)) {
    writeFileSync(
      path,
      JSON.stringify({
        djs: [],
        promos: [],
      }),
    );
  }

  const file_contents: ILedger = JSON.parse(readFileSync(path, "utf-8"));

  return file_contents;
};

export const getLineup = (data: { name: string }) => {
  const path = join(
    JSON.parse(readFileSync(SETTINGS_FILE, "utf-8")).lineups_dir,
    data.name + ".json",
  );
  // Err on this
  if (!existsSync(path)) {
    return {};
  }

  const file_contents: ILineup = JSON.parse(readFileSync(path, "utf-8"));

  return file_contents;
};

export const getAppThemes = () => {
  const themesPath = APP_THEMES_FILE;
  let styles: ITheme[] = [];
  if (existsSync(themesPath)) {
    styles = JSON.parse(readFileSync(themesPath, "utf-8"));
  } else {
    styles = [
      {
        title: "Default Theme",
        style: {
          primaryColor: "#add8e6",
          secondaryColor: "#d3d3d3",
          backgroundColor: "#ffffff",
          primaryTextColor: "#000000",
          secondaryTextColor: "#808080",
          highlightColor: "#ffc0cb",
          focusColor: "#ffffff",
          activeColor: "#d3d3d3",
          deleteColor: "#ff0000",
          cancelTextColor: "#ff0000",
          cancelBackgroundColor: "rgb(253, 229, 232)",
          submitTextColor: "#0000ff",
          submitBackgroundColor: "rgb(235, 246, 250)",
        },
      },
      {
        title: "Moe",
        style: {
          primaryColor: "#789922",
          secondaryColor: "#d3d3d3",
          backgroundColor: "#d9e6ff",
          primaryTextColor: "#000000",
          secondaryTextColor: "#789922",
          highlightColor: "#cc4a4a",
          focusColor: "#ffffff",
          activeColor: "#d9e6ff",
          deleteColor: "#5c3c82",
          cancelTextColor: "#5c3c82",
          cancelBackgroundColor: "#7149a24f",
          submitTextColor: "#789922",
          submitBackgroundColor: "#97c42252",
        },
      },
    ];
    writeFileSync(themesPath, JSON.stringify(styles));
  }
  return styles;
};

export const getLineups = () => {
  const path = JSON.parse(readFileSync(SETTINGS_FILE, "utf-8")).lineups_dir;

  if (path == null) {
    return [];
  }
  if (!existsSync(path)) {
    mkdirSync(path);
    return [];
  }

  const lineups: string[] = readdirSync(path, { withFileTypes: true })
    .filter((file: Dirent) => file.isFile())
    .map((file: Dirent) => parse(file.name).name);
  return lineups;
};

export const getSettings = () => {
  if (!existsSync(SETTINGS_FILE)) {
    writeFileSync(SETTINGS_FILE, JSON.stringify(DEFAULT_SETTINGS));
  }

  return JSON.parse(readFileSync(SETTINGS_FILE, "utf-8"));
};

export const getFilePath = () => {
  return dialog({type: "open-file"}).then((files: (string)[]) => [path.basename(files[0]), files[0]]);
}

export const getDirPath = () => {
  return dialog({type: "directory"}).then((files: (string)[]) => files[0]);
}
