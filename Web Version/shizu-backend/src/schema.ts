import { buildSchema } from "graphql";

export const SCHEMA = buildSchema(`
type Query {
    test(mandatory: String!, optional: String): String
    getLedger: ledgerObject
    getLineup(name: String!): lineupObject
    getAppThemes: [themeObject]
    getLineups: [String]
    getSettings: settingsObject
    getFilePath: [String]
    getDirPath: String
    getLogoPermissions(sub_dirs: [String]): fileDialogBlob
    getRecordingPermissions(sub_dirs: [String]): fileDialogBlob
    getExportPermissions(sub_dirs: [String]): fileDialogBlob
    reconstructLogoPath(dirs: [String]): String
    reconstructRecordingPath(dirs: [String]): String
    reconstructExportPath(dirs: [String]): String
},
type Mutation {
    addDj(name: String!, logo_path: String, recording_path: String, rtmp_server: String, stream_key: String): ledgerObject
    addPromo(name: String!, path: String): ledgerObject
    updateDj(index: Int!, name: String, logo_path: String, recording_path: String, rtmp_server: String, stream_key: String): ledgerObject
    updatePromo(index: Int!, name: String, path: String): ledgerObject
    createLineup(name: String!): String
    updateLineup(name: String!, djs: [lineupDjObjectInput], promos: [String]): String
    setLineupDjLive(lineup_name: String!, dj_name: String!, is_live: Boolean, vj: String): String
    swapLineupDJs(lineup_name: String!, index_a: Int!, index_b: Int!): String
    swapLineupPromos(lineup_name: String!, index_a: Int!, index_b: Int!): String
    addDjToLineup(lineup_name: String!, dj_name: String!): String
    addPromoToLineup(lineup_name: String!, promo_name: String!): String
    removeDjFromLineup(lineup_name: String!, dj_name: String!): String
    removePromoFromLineup(lineup_name: String!, promo_name: String!): String
    addAppTheme: [themeObject]
    editAppTheme(themeIndex: Int!, newThemeTitle: String!, newThemeStyle: themeStyleInput!): [themeObject]
    deleteAppTheme(themeIndex: Int!): [themeObject]
    setLastThemeIndex(index: Int!): String
    deleteDj(index: Int!): ledgerObject
    deletePromo(index: Int!): ledgerObject
    deleteLineup(name: String!): String
    updateSettings(ledger_path: String, lineups_dir: String, theme_index: Int): String
    exportLineup(lineup_name: String, export_dir: String): String
},
type ledgerObject {
    djs: [djObject],
    promos: [promoObject]
},
type lineupObject {
    djs: [lineupDjObject],
    promos: [String]
},
type djObject {
    name: String,
    recording_path: String,
    logo_path: String,
    rtmp_server: String,
    stream_key: String
},
type promoObject {
    name: String,
    path: String
},
type lineupDjObject {
    name: String,
    is_live: Boolean,
    vj: String
},
type themeObject {
    title: String,
    style: themeStyle
},
type themeStyle {
    primaryColor: String,
    secondaryColor: String,
    backgroundColor: String,
    primaryTextColor: String,
    secondaryTextColor: String,
    highlightColor: String,
    focusColor: String,
    activeColor: String,
    deleteColor: String,
    cancelTextColor: String,
    cancelBackgroundColor: String,
    submitTextColor: String,
    submitBackgroundColor: String
}
type settingsObject {
    ledger_path: String,
    lineups_dir: String,
    theme_index: Int
}
type fileDialogBlob {
    files: [fileBlob],
    path: [String],
    top_dirs: [String]
}
type fileBlob {
    name: String,
    is_dir: Boolean
}
input lineupDjObjectInput {
    name: String,
    is_live: Boolean
}
input themeStyleInput {
    primaryColor: String,
    secondaryColor: String,
    backgroundColor: String,
    primaryTextColor: String,
    secondaryTextColor: String,
    highlightColor: String,
    focusColor: String,
    activeColor: String,
    deleteColor: String,
    cancelTextColor: String,
    cancelBackgroundColor: String,
    submitTextColor: String,
    submitBackgroundColor: String
}
`);
