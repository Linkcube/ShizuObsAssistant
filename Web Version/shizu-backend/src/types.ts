export interface IDj {
  name: string;
  logo_path?: string;
  recording_path?: string;
  rtmp_server?: string;
  stream_key?: string;
  last_live_resolution?: number[];
}
export interface ILineupDj {
  name: string;
  is_live: boolean;
  url?: string;
  recording_path?: string
}
export interface IPromo {
  name: string;
  path: string;
}

export interface ILedger {
  djs: IDj[];
  promos: IPromo[];
}

export interface ILineup {
  djs: ILineupDj[];
  promos: string[];
}

export interface ISettings {
  ledger_path: string;
  lineups_dir: string;
  theme_index: number;
}

export interface ITheme {
  title: string;
  style: IThemeStyle;
}

export interface IThemeStyle {
  primaryColor: string;
  secondaryColor: string;
  backgroundColor: string;
  primaryTextColor: string;
  secondaryTextColor: string;
  highlightColor: string;
  focusColor: string;
  activeColor: string;
  deleteColor: string;
  cancelTextColor: string;
  cancelBackgroundColor: string;
  submitTextColor: string;
  submitBackgroundColor: string;
}
