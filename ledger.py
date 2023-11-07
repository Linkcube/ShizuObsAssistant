from settings import DJ_KEY, PROMO_KEY
from ledger_dj import LedgerDJ
from ledger_promo import LedgerPromo

import json

class Ledger:
    # Interface for in memory database
    def __init__(self):
        self.djs = {}
        self.promos = {}

    def load_data(self, data):
        for dj_entry in data[DJ_KEY]:
            self.djs[dj_entry.get("name")] = LedgerDJ(
                dj_entry.get("name"),
                dj_entry.get("logo_path"),
                dj_entry.get("recording_path"),
                dj_entry.get("rtmp_server"),
                dj_entry.get("stream_key"),
                dj_entry.get("last_live_resolution"),
            )

        for promo in data[PROMO_KEY]:
            self.promos[promo.get("name")] = LedgerPromo(
                promo.get("name"), promo.get("path")
            )

    def get_dj_by_name(self, dj_name) -> "LedgerDJ":
        dj = self.djs.get(dj_name)
        if dj:
            return dj
        raise Exception(f"Could not find dj by name: {dj_name}")

    def get_promo_by_name(self, promo_name) -> "LedgerPromo":
        promo = self.promos.get(promo_name)
        if promo:
            return promo
        raise Exception(f"Could not find promo by name: {promo_name}")

    def create_dj_entry(self):
        dj_name = "new-dj"
        post_fix = 0
        while self.djs.get(dj_name):
            post_fix += 1
            dj_name = f"new-dj{post_fix}"

        self.djs[dj_name] = LedgerDJ(dj_name)
        return dj_name

    def create_promo_entry(self):
        promo_name = "new-dj"
        post_fix = 0
        while self.promos.get(promo_name):
            post_fix += 1
            promo_name = f"new-dj{post_fix}"

        self.promos[promo_name] = LedgerPromo(promo_name)
        return promo_name

    def update_dj(self, dj_name, name, logo_path, recording_path, rtmp, stream_key):
        dj = self.get_dj_by_name(dj_name)
        dj.logo_path = logo_path
        dj.recording_path = recording_path
        dj.rtmp_server = rtmp
        dj.stream_key = stream_key
        if dj_name != name:
            dj.name = name
            self.rename_dj(dj_name, name)

    def update_promo(self, promo_name, name, path):
        promo = self.get_promo_by_name(promo_name)
        promo.path = path
        if promo_name != name:
            promo.name = name
            self.rename_promo(promo_name, name)

    def rename_dj(self, old_name, new_name):
        self.djs[new_name] = self.djs.pop(old_name)

    def rename_promo(self, old_name, new_name):
        self.promos[new_name] = self.promos.pop(old_name)

    def delete_dj(self, dj_name):
        self.djs.pop(dj_name)

    def delete_promo(self, promo_name):
        self.promos.pop(promo_name)

    def save(self):
        return json.dumps(
            {
                "djs": [dj.save() for _, dj in self.djs.items()],
                "promos": [promo.save() for _, promo in self.promos.items()],
            }
        )

    def to_treeview_values(self):
        # Return values split up for treeview usage
        # DJs: "Name", "Has Logo", "RTMP", "Has Recording"
        # Promos: "Name", "Has Recording"
        dj_rows = []
        promo_rows = []
        for name, dj in self.djs.items():
            dj_rows.append(
                (name, dj.logo_path != "", dj.rtmp_server, dj.recording_path != "")
            )

        for name, promo in self.promos.items():
            promo_rows.append((name, promo.path != ""))

        return (dj_rows, promo_rows)