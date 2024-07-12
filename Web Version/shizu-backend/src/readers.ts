import path, { join, resolve, basename, parse } from "path";
import {
  readdirSync,
  Dirent,
  existsSync,
  readFileSync,
  writeFileSync,
  mkdirSync,
} from "fs";
import type { IFileObject, ILedger, ILineup, IPermissions, ISettings, ITheme, IStaticFolderPermission, IStaticPermissions } from "./types";
const dialog = require("node-file-dialog");
import { LineupNotFoundError } from "./errors";

const SETTINGS_FILE = join(resolve("."), "settings.json");
const APP_THEMES_FILE = join(resolve("."), "themes.json");
const DEFAULT_SETTINGS: ISettings = {
  ledger_path: join(resolve("."), "ledger.json"),
  lineups_dir: join(resolve("."), "lineups"),
  theme_index: 0,
};

const PERMISSIONS_FILE = join(resolve("."), "permissions.json")
const DEFAULT_PERMISSIONS: IPermissions = {
  logo_dirs: [join(resolve(".", "logos"))],
  recording_dirs: [join(resolve(".", "recordings"))],
  export_dirs: [join(resolve(".", "export"))]
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

  if (!existsSync(path)) {
    return new LineupNotFoundError(`Could not find lineup ${data.name}.`);
  }

  const file_contents: ILineup = JSON.parse(readFileSync(path, "utf-8"));

  // Python lineups value conversion
  file_contents.djs = file_contents.djs.map(dj => {
    if (dj.url) dj.is_live = true;
    if (dj.recording_path) dj.is_live = false;
    if (dj.is_live == null) dj.is_live = false;
    return dj;
  })

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

function getPermissions(permission: string) {
  if (!existsSync(PERMISSIONS_FILE)) {
    writeFileSync(PERMISSIONS_FILE, JSON.stringify(DEFAULT_PERMISSIONS));
    if (!existsSync(DEFAULT_PERMISSIONS.logo_dirs[0])) mkdirSync(DEFAULT_PERMISSIONS.logo_dirs[0]);
    if (!existsSync(DEFAULT_PERMISSIONS.recording_dirs[0])) mkdirSync(DEFAULT_PERMISSIONS.recording_dirs[0]);
    if (!existsSync(DEFAULT_PERMISSIONS.export_dirs[0])) mkdirSync(DEFAULT_PERMISSIONS.export_dirs[0]);
  }

  let permissions: IPermissions = JSON.parse(readFileSync(PERMISSIONS_FILE, "utf-8"));

  switch(permission) {
    case "logos":
      return permissions.logo_dirs
    case "recordings":
      return permissions.recording_dirs
    case "export":
      return permissions.export_dirs
    default:
      return [];
  }
};

function getFilesForPermission(top_dirs: string[], dirs_list: string[], dirs_only: boolean) {
  let top_dirs_map = new Map(top_dirs.map(directory => {
    return [path.basename(directory), directory]
  }));
  let top_dirs_names = [...top_dirs_map.keys()]
  
  let top_dir: string | undefined = top_dirs_names[0];
  let top_level_path: string | undefined = "";
  let sub_dirs: string[] = [];

  if (dirs_list && dirs_list.at(0)) {
    top_dir = dirs_list.at(0);
    if (!top_dir) throw Error("panic")
    sub_dirs = dirs_list.slice(1);
  } else {
    dirs_list = [top_dir];
  }

  top_level_path = top_dirs_map.get(top_dir);
  if (!top_level_path) throw Error("panic")

  let new_path = top_level_path;

  if (sub_dirs) {
    new_path = path.join(top_level_path, ...sub_dirs);
  }

  const new_items: IFileObject[] = readdirSync(new_path, { withFileTypes: true })
  .filter((file: Dirent) => {
    if (dirs_only) {
      return file.isDirectory();
    }
    return true;
  })
  .map((file: Dirent) => {
    return {
      name: file.name,
      is_dir: file.isDirectory()
    }
  });

  return {
    files: new_items,
    path: dirs_list,
    top_dirs: top_dirs_names
  };
}

export const getLogoPermissions = (data: { sub_dirs: string[]}) => {
  const permissions = getPermissions("logos");
  let retval = getFilesForPermission(permissions, data.sub_dirs, false);
  retval.files = retval.files.filter(file => {
    return [".png", ".jpg", ".jpeg", ".apng", ".gif", ".webp", ".svg", ".avif"].includes(path.extname(file.name)) || file.is_dir
  });

  return retval;
}

export const getRecordingPermissions = (data: { sub_dirs: string[]}) => {
  const permissions = getPermissions("recordings");
  let retval =  getFilesForPermission(permissions, data.sub_dirs, false);
  retval.files = retval.files.filter(file => {
    return [".mkv", ".webm", ".avi", ".mov", ".mp4", ".mp3", ".wav", ".flac"].includes(path.extname(file.name)) || file.is_dir
  });

  return retval;
}

export const getExportPermissions = (data: { sub_dirs: string[]}) => {
  const permissions = getPermissions("export");
  return getFilesForPermission(permissions, data.sub_dirs, true);
}

export function getStaticPathPermissions() {
  if (!existsSync(PERMISSIONS_FILE)) {
    writeFileSync(PERMISSIONS_FILE, JSON.stringify(DEFAULT_PERMISSIONS));
    if (!existsSync(DEFAULT_PERMISSIONS.logo_dirs[0])) mkdirSync(DEFAULT_PERMISSIONS.logo_dirs[0]);
    if (!existsSync(DEFAULT_PERMISSIONS.recording_dirs[0])) mkdirSync(DEFAULT_PERMISSIONS.recording_dirs[0]);
    if (!existsSync(DEFAULT_PERMISSIONS.export_dirs[0])) mkdirSync(DEFAULT_PERMISSIONS.export_dirs[0]);
  }

  let permissions: IPermissions = JSON.parse(readFileSync(PERMISSIONS_FILE, "utf-8"));

  let logo_dirs = permissions.logo_dirs.map(dir => {
    let perm: IStaticFolderPermission = {
      id: path.basename(dir),
      path: resolve(dir)
    }
    
    return perm;
  });
  let recording_dirs = permissions.recording_dirs.map(dir => {
    let perm: IStaticFolderPermission = {
      id: path.basename(dir),
      path: resolve(dir)
    }

    return perm;
  });
  let export_dirs = permissions.export_dirs.map(dir => {
    let perm: IStaticFolderPermission = {
      id: path.basename(dir),
      path: resolve(dir)
    }

    return perm;
  });

  let static_permissions: IStaticPermissions = {
    logos: logo_dirs,
    recordings: recording_dirs,
    exports: export_dirs
  }

  return static_permissions
}

function reconstructFilePath(top_dirs: string[], segments: string[]) {
  let top_dirs_map = new Map(top_dirs.map(directory => {
    return [path.basename(directory), directory]
  }));

  let top_dir = top_dirs_map.get(segments[0]);
  if (!top_dir) throw Error("Invalid top directory")
  let full_path = top_dir
  if (segments.length > 1) {
    full_path = path.join(top_dir, ...segments.slice(1));
  }

  return full_path;
}

export const reconstructLogoPath = (data: { dirs: string[]}) => {
  const permissions = getPermissions("logos");
  return reconstructFilePath(permissions, data.dirs);
}

export const reconstructRecordingPath = (data: { dirs: string[]}) => {
  const permissions = getPermissions("recordings");
  return reconstructFilePath(permissions, data.dirs);
}

export const reconstructExportPath = (data: { dirs: string[]}) => {
  const permissions = getPermissions("export");
  return reconstructFilePath(permissions, data.dirs);
}