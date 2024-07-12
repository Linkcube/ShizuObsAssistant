import path, { join, resolve, basename } from "path";
import {
  readdirSync,
  Dirent,
  existsSync,
  readFileSync,
  writeFileSync,
  mkdirSync,
  rm,
  rmSync,
} from "fs";
import type {
  IDj,
  ILedger,
  ILineup,
  ILineupDj,
  IPromo,
  ISettings,
  ITheme,
  IThemeStyle,
  IPermissions,
  IExportDjineupData,
  IExportPromoLineupData
} from "./types";
import { FfprobeData, ffprobe } from "fluent-ffmpeg";
import { 
  InvalidFileError,
  InvalidDjError,
  InvalidPromoError,
  InvalidLineupError,
  DjNotFoundError,
  PromoNotFoundError,
  LineupNotFoundError
} from "./errors";
import {
  getLineup
} from "./readers";

const SETTINGS_FILE = join(resolve("."), "settings.json");
const APP_THEMES_FILE = join(resolve("."), "themes.json");
const PERMISSIONS_FILE = join(resolve("."), "permissions.json")

function validate_file_path(file_path: string, root_dirs: string[]) {
  var valid_path = false;

  root_dirs.forEach((root) => {
    const relative = path.relative(root, file_path);
    const isSubdir = relative && !relative.startsWith('..') && !path.isAbsolute(relative);
    if (isSubdir) {
      console.log("Valid path found!");
      valid_path = true;
    }
  });

  return valid_path;
}

function validate_logo(logo_path: string) {
  const permissions: IPermissions = JSON.parse(readFileSync(PERMISSIONS_FILE, "utf-8"));

  if (!validate_file_path(logo_path, permissions.logo_dirs)) {
    throw new InvalidFileError("Supplied logo path is not permitted.")
  }
}

function validate_recording(recording_path: string) {
  const permissions: IPermissions = JSON.parse(readFileSync(PERMISSIONS_FILE, "utf-8"));

  if (!validate_file_path(recording_path, permissions.recording_dirs)) {
    throw new InvalidFileError("Supplied recording path is not permitted.")
  }
}

function validate_export(export_path: string) {
  const permissions: IPermissions = JSON.parse(readFileSync(PERMISSIONS_FILE, "utf-8"));

  if (!validate_file_path(export_path, permissions.export_dirs)) {
    throw new InvalidFileError("Supplied export path is not permitted.")
  }
}

export const addDj = (data: {
  name: string;
  logo_path: string;
  recording_path: string;
  rtmp_server: string;
  stream_key: string;
}) => {
  const ledger_path = JSON.parse(
    readFileSync(SETTINGS_FILE, "utf-8"),
  ).ledger_path;
  const ledger_data: ILedger = JSON.parse(readFileSync(ledger_path, "utf-8"));

  if (
    ledger_data.djs.find((dj) => {
      return dj.name === data.name;
    })
  ) {
    return new InvalidDjError(`DJ ${data.name} already exists`);
  }

  try {
    if (data.logo_path) validate_logo(data.logo_path);
    if (data.recording_path) validate_recording(data.recording_path);
  } catch (error) {
    return error;
  }

  const new_dj: IDj = {
    name: data.name,
    logo_path: data.logo_path,
    recording_path: data.recording_path,
    rtmp_server: data.rtmp_server,
    stream_key: data.stream_key,
  };
  ledger_data.djs.push(new_dj);
  writeFileSync(ledger_path, JSON.stringify(ledger_data));
  return ledger_data;
};

export const addPromo = (data: { name: string; path: string }) => {
  const ledger_path = JSON.parse(
    readFileSync(SETTINGS_FILE, "utf-8"),
  ).ledger_path;
  const ledger_data: ILedger = JSON.parse(readFileSync(ledger_path, "utf-8"));

  if (
    ledger_data.promos.find((promo) => {
      return promo.name === data.name;
    })
  ) {
    return new InvalidPromoError(`Promo ${data.name} already exists`);
  }

  try {
    if (data.path) validate_recording(data.path);
  } catch (error) {
    return error;
  }

  const new_promo: IPromo = {
    name: data.name,
    path: data.path,
  };
  ledger_data.promos.push(new_promo);
  writeFileSync(ledger_path, JSON.stringify(ledger_data));
  return ledger_data;
};

export const updateDj = (data: {
  index: number;
  name: string;
  logo_path: string;
  recording_path: string;
  rtmp_server: string;
  stream_key: string;
}) => {
  const ledger_path = JSON.parse(
    readFileSync(SETTINGS_FILE, "utf-8"),
  ).ledger_path;
  const ledger_data: ILedger = JSON.parse(readFileSync(ledger_path, "utf-8"));

  if (data.index < 1 || data.index >= ledger_data.djs.length) {
    return new DjNotFoundError(`No entry exists for DJ ${data.name} at index ${data.index}.`);
  }

  const dj: IDj = ledger_data.djs[data.index];

  try {
    if (data.logo_path) validate_logo(data.logo_path);
    if (data.recording_path) validate_recording(data.recording_path);
  } catch (error) {
    return error;
  }

  if (data.name) dj.name = data.name;
  if (data.logo_path) dj.logo_path = data.logo_path;
  if (data.recording_path) dj.recording_path = data.recording_path;
  if (data.rtmp_server) dj.rtmp_server = data.rtmp_server;
  if (data.stream_key) dj.stream_key = data.stream_key;

  ledger_data.djs[data.index] = dj;
  writeFileSync(ledger_path, JSON.stringify(ledger_data));
  return ledger_data;
};

export const updatePromo = (data: {
  index: number;
  name: string;
  path: string;
}) => {
  const ledger_path = JSON.parse(
    readFileSync(SETTINGS_FILE, "utf-8"),
  ).ledger_path;
  const ledger_data: ILedger = JSON.parse(readFileSync(ledger_path, "utf-8"));

  if (data.index < 1 || data.index >= ledger_data.promos.length) {
    return new PromoNotFoundError(`No entry exists for Promo ${data.name} at index ${data.index}.`);
  }

  try {
    if (data.path) validate_recording(data.path);
  } catch (error) {
    return error;
  }

  const promo: IPromo = ledger_data.promos[data.index];

  if (data.name) promo.name = data.name;
  if (data.path) promo.path = data.path;

  ledger_data.promos[data.index] = promo;
  writeFileSync(ledger_path, JSON.stringify(ledger_data));
  return ledger_data;
};

export const createLineup = (data: { name: string }) => {
  const lineup_path = join(
    JSON.parse(readFileSync(SETTINGS_FILE, "utf-8")).lineups_dir,
    data.name + ".json",
  );
  if (existsSync(lineup_path)) {
    return new InvalidLineupError("Lineup already exists");
  }

  writeFileSync(
    lineup_path,
    JSON.stringify({
      djs: [],
      promos: [],
    }),
  );

  return "Done";
};

export const addDjToLineup = (data: {
  lineup_name: string,
  dj_name: string
}) => {
  // Validation requires a DB overhaul
  const lineup = getLineup({name: data.lineup_name});
  if (lineup instanceof Error) return lineup;

  if (lineup.djs.map(dj => dj.name).includes(data.dj_name)) {
    return new InvalidDjError(`Lineup ${data.lineup_name} already contains DJ ${data.dj_name}.`);
  }

  lineup.djs.push({
    name: data.dj_name,
    is_live: false
  })

  const lineup_path = join(
    JSON.parse(readFileSync(SETTINGS_FILE, "utf-8")).lineups_dir,
    data.lineup_name + ".json",
  );
  writeFileSync(
    lineup_path,
    JSON.stringify({
      djs: lineup.djs,
      promos: lineup.promos,
    }),
  );

  return "Done";
}

export const addPromoToLineup = (data: {
  lineup_name: string,
  promo_name: string
}) => {
  // Validation requires a DB overhaul
  const lineup = getLineup({name: data.lineup_name});
  if (lineup instanceof Error) return lineup;

  if (lineup.promos.includes(data.promo_name)) {
    return new InvalidPromoError(`Lineup ${data.lineup_name} already contains Promo ${data.promo_name}.`);
  }

  lineup.promos.push(data.promo_name);

  const lineup_path = join(
    JSON.parse(readFileSync(SETTINGS_FILE, "utf-8")).lineups_dir,
    data.lineup_name + ".json",
  );
  writeFileSync(
    lineup_path,
    JSON.stringify({
      djs: lineup.djs,
      promos: lineup.promos,
    }),
  );

  return "Done";
}

export const updateLineup = (data: {
  name: string;
  djs: ILineupDj[];
  promos: string[];
}) => {
  const lineup_path = join(
    JSON.parse(readFileSync(SETTINGS_FILE, "utf-8")).lineups_dir,
    data.name + ".json",
  );
  if (!existsSync(lineup_path)) {
    return new LineupNotFoundError(`Could not find Lineup: ${data.name}.`);
  }

  // TODO: validate djs and promos

  writeFileSync(
    lineup_path,
    JSON.stringify({
      djs: data.djs,
      promos: data.promos,
    }),
  );

  return "Done";
};

export const addAppTheme = () => {
  let themes: ITheme[] = [];
  if (existsSync(APP_THEMES_FILE)) {
    themes = JSON.parse(readFileSync(APP_THEMES_FILE, "utf-8"));
  }
  themes.push({
    title: "New Theme",
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
  });
  writeFileSync(APP_THEMES_FILE, JSON.stringify(themes));
  return themes;
};

export const editAppTheme = (data: {
  themeIndex: number;
  newThemeTitle: string;
  newThemeStyle: IThemeStyle;
}) => {
  let themes: ITheme[] = [];
  if (existsSync(APP_THEMES_FILE)) {
    themes = JSON.parse(readFileSync(APP_THEMES_FILE, "utf-8"));
  }
  themes[data.themeIndex] = {
    title: data.newThemeTitle,
    style: data.newThemeStyle,
  };
  writeFileSync(APP_THEMES_FILE, JSON.stringify(themes));
  return themes;
};

export const deleteAppTheme = (data: { themeIndex: number }) => {
  let themes: ITheme[] = [];
  if (existsSync(APP_THEMES_FILE)) {
    themes = JSON.parse(readFileSync(APP_THEMES_FILE, "utf-8"));
  }
  themes.splice(data.themeIndex, 1);
  writeFileSync(APP_THEMES_FILE, JSON.stringify(themes));
  return themes;
};

export const setLastThemeIndex = (data: { index: number }) => {
  const settings_data: ISettings = JSON.parse(
    readFileSync(SETTINGS_FILE, "utf-8"),
  );
  settings_data.theme_index = data.index;
  writeFileSync(SETTINGS_FILE, JSON.stringify(settings_data));
  return "done";
};

export const deleteDj = (data: { index: number }) => {
  const settings_data: ISettings = JSON.parse(
    readFileSync(SETTINGS_FILE, "utf-8"),
  );
  const ledger_data: ILedger = JSON.parse(
    readFileSync(settings_data.ledger_path, "utf-8"),
  );

  const dj_name = ledger_data.djs[data.index].name;

  const lineups: string[] = readdirSync(settings_data.lineups_dir, {
    withFileTypes: true,
  })
    .filter((file: Dirent) => file.isFile())
    .map((file: Dirent) => file.name);

  lineups.map((lineup) => {
    const lineup_path = join(settings_data.lineups_dir, lineup);
    const lineup_data: ILineup = JSON.parse(readFileSync(lineup_path, "utf-8"));
    lineup_data.djs = lineup_data.djs.filter((dj) => dj.name !== dj_name);
    writeFileSync(lineup_path, JSON.stringify(lineup_data));
  });

  ledger_data.djs.splice(data.index, 1);
  writeFileSync(settings_data.ledger_path, JSON.stringify(ledger_data));
  return ledger_data;
};

export const deletePromo = (data: { index: number }) => {
  const settings_data: ISettings = JSON.parse(
    readFileSync(SETTINGS_FILE, "utf-8"),
  );
  const ledger_data: ILedger = JSON.parse(
    readFileSync(settings_data.ledger_path, "utf-8"),
  );

  const promo_name = ledger_data.promos[data.index].name;

  const lineups: string[] = readdirSync(settings_data.lineups_dir, {
    withFileTypes: true,
  })
    .filter((file: Dirent) => file.isFile())
    .map((file: Dirent) => file.name);

  lineups.map((lineup) => {
    const lineup_path = join(settings_data.lineups_dir, lineup);
    const lineup_data: ILineup = JSON.parse(readFileSync(lineup_path, "utf-8"));
    lineup_data.promos = lineup_data.promos.filter(
      (promo) => promo !== promo_name,
    );
    writeFileSync(lineup_path, JSON.stringify(lineup_data));
  });

  ledger_data.promos.splice(data.index, 1);
  writeFileSync(settings_data.ledger_path, JSON.stringify(ledger_data));
  return ledger_data;
};

export const deleteLineup = (data: { name: string }) => {
  const settings_data: ISettings = JSON.parse(
    readFileSync(SETTINGS_FILE, "utf-8"),
  );
  const lineup_path = join(settings_data.lineups_dir, data.name + ".json");

  if (!existsSync(lineup_path)) {
    return "No lineup found";
  }

  rmSync(lineup_path);
  return "Deleted";
};

export const updateSettings = (data: {
  ledger_path: string;
  lineups_dir: string;
  theme_index: number;
}) => {
  const settings_data: ISettings = JSON.parse(
    readFileSync(SETTINGS_FILE, "utf-8"),
  );

  if (data.ledger_path) settings_data.ledger_path = data.ledger_path;
  if (data.lineups_dir) settings_data.lineups_dir = data.lineups_dir;
  if (data.theme_index) settings_data.theme_index = data.theme_index;

  writeFileSync(
    SETTINGS_FILE,
    JSON.stringify(settings_data),
  );

  return "Updated";
};

export const exportLineup = async (data: { lineup_name: string, export_dir: string }) => {
  let settings = JSON.parse(readFileSync(SETTINGS_FILE, "utf-8"));
  let ledger_path = settings.ledger_path;

  if (!existsSync(ledger_path)) {
    writeFileSync(
      ledger_path,
      JSON.stringify({
        djs: [],
        promos: [],
      }),
    );
  }

  const ledger_contents: ILedger = JSON.parse(readFileSync(ledger_path, "utf-8"));

  let lineup_path = join(
    settings.lineups_dir,
    data.lineup_name + ".json",
  );

  const export_path = join(path.normalize(data.export_dir), data.lineup_name + ".json");

  try {
    validate_export(export_path);
  } catch (error) {
    return error;
  }

  if (!existsSync(lineup_path)) {
    return new LineupNotFoundError(`Could not find Lineup: ${data.lineup_name}.`);
  }

  const lineup_contents: ILineup = JSON.parse(readFileSync(lineup_path, "utf-8"));

  const ledger_dj_map = new Map(ledger_contents.djs.map(dj => [dj.name, dj]));
  const ledger_promo_map = new Map(ledger_contents.promos.map(promo => [promo.name, promo]));

  const missing_djs: string[] = [];
  lineup_contents.djs.forEach((dj) => {
    if (ledger_dj_map.get(dj.name) === undefined) {
      missing_djs.push(dj.name);
    }
  });
  if (missing_djs.length > 0) {
    return new DjNotFoundError(`Could not find DJs: ${missing_djs.toString()}.`);
  }

  const dj_promises = lineup_contents.djs.map(dj => {
    let dj_data = ledger_dj_map.get(dj.name);
    if (!dj_data) {
      throw Error();
    }
    let export_data: IExportDjineupData = {
      name: dj.name,
      logo_path: "",
      recording_path: "",
      resolution: Promise.resolve([]),
      url: ""
    };
    export_data.logo_path = dj_data.logo_path ? dj_data.logo_path : "";
    if (dj.is_live) {
      export_data.url = `rtmp://rtmp-${dj_data.rtmp_server}.anisonhijack.com/live/${dj_data.stream_key}`;
    } else {
      if (dj_data.recording_path !== undefined) {
        export_data.recording_path = dj_data.recording_path;
        export_data.resolution = getResolution(dj_data.recording_path);
      }
    }
    return export_data;
  });

  const missing_promos: string[] = [];
  lineup_contents.promos.forEach((promo) => {
    if (ledger_promo_map.get(promo) === undefined) {
      missing_promos.push(promo);
    }
  });
  if (missing_promos.length > 0) {
    return new PromoNotFoundError(`Could not find Promos: ${missing_promos.toString()}.`);
  }
  
  const promo_promises = lineup_contents.promos.map(promo => {
    let promo_data = ledger_promo_map.get(promo);
    if (!promo_data) {
      throw Error();
    }
    let export_data: IExportPromoLineupData = {
      name: promo,
      path: "",
      resolution: Promise.resolve([])
    }
    if (promo_data.path) {
      export_data.path = promo_data.path;
      export_data.resolution = getResolution(promo_data.path);
    }

    return export_data;
  });

  const djs_data = await Promise.all(dj_promises.map(async dj => {
      return {
        name: dj.name,
        logo_path: resolvePath(dj.logo_path),
        recording_path: resolvePath(dj.recording_path),
        resolution: await dj.resolution,
        url: dj.url
      }
  }));
  const promos_data = await Promise.all(promo_promises.map(async promo => {
    return {
      name: promo.name,
      path: resolvePath(promo.path),
      resolution: await promo.resolution
    }
  }));

  const ffmpeg_errors: string[] = [];
  djs_data.forEach((dj) => {
    if (dj.resolution instanceof Error) {
      ffmpeg_errors.push(`DJ ${dj.name}, ${dj.resolution.message}`);
    }
  });
  promos_data.forEach((promo) => {
    if (promo.resolution instanceof Error) {
      ffmpeg_errors.push(`Promo ${promo.name}, ${promo.resolution.message}`);
    }
  });
  if (ffmpeg_errors.length > 0) return new InvalidFileError(ffmpeg_errors.toString());

  console.log(`Exporting to ${export_path}`);

  writeFileSync(
    export_path,
    JSON.stringify({
      djs: djs_data,
      promos: promos_data,
    }),
  );

  return "Done";
}

function getResolution(file_path: string): Promise<number[] | Error> {
  if (!file_path) return new Promise((resolve, _) => resolve([]));
  file_path = resolvePath(file_path);
  return new Promise((resolve, reject) => {
    ffprobe(file_path, (err, metadata) => {
      if (err) {
        console.log(err);
        resolve(new Error(`Invalid file selected for ${file_path}.`));
      }
      if (metadata && metadata.streams) {
        const video_stream = metadata.streams.filter(stream => stream.codec_type === "video");
        if (video_stream) {
          resolve(video_stream.map(stream => [stream.width!, stream.height!])[0]);
        }
      }
      resolve([]);
    });
  });
}

function resolvePath(file_path: string | undefined) {
  if (!file_path) return "";
  return path.normalize(file_path);
}