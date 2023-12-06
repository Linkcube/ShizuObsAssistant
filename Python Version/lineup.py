from settings import DJ_KEY, PROMO_KEY
from ledger import Ledger

import json

class Lineup:
    def __init__(self, djs: list["str"], promos: list["str"], ledger: "Ledger"):
        self.dj_entries = []
        for dj_name in djs:
            dj = ledger.get_dj_by_name(dj_name)
            if dj.recording_path is None:
                self.dj_entries.append([dj_name, True])
            else:
                self.dj_entries.append([dj_name, False])
        self.promo_entries = promos
        self.ledger = ledger
    
    def load_data(self, json_data):
        for dj_entry in json_data[DJ_KEY]:
            self.dj_entries.append([dj_entry.get("name"), "url" in dj_entry])
        for promo_entry in json_data[PROMO_KEY]:
            self.promo_entries.append(promo_entry.get("name"))

    def has_dj(self, dj_name):
        for dj_entry in self.dj_entries:
            if dj_name == dj_entry[0]:
                return dj_entry

    def has_promo(self, promo_name):
        for promo_entry in self.promo_entries:
            if promo_name == promo_entry:
                return promo_entry

    def get_dj_by_name(self, dj_name):
        return self.has_dj(dj_name)

    def add_dj(self, dj_name, is_live=False):
        if self.has_dj(dj_name):
            raise Exception("DJ entry already in lineup")
        self.dj_entries.append([dj_name, is_live])

    def add_promo(self, promo_name):
        if self.has_promo(promo_name):
            raise Exception("Promo entry already in lineup")
        self.promo_entries.append(promo_name)

    def remove_dj(self, dj_name):
        found_dj = self.has_dj(dj_name)

        if found_dj:
            self.dj_entries.remove(found_dj)
        else:
            raise Exception(f"No dj found in lineup for {dj_name}")

    def remove_promo(self, promo_name):
        found_promo = self.has_promo(promo_name)

        if found_promo:
            self.promo_entries.remove(found_promo)
        else:
            raise Exception(f"No promo found in lineup for {found_promo}")

    def swap_djs(self, first_index, second_index):
        temp = self.dj_entries[first_index]
        self.dj_entries[first_index] = self.dj_entries[second_index]
        self.dj_entries[second_index] = temp

    def swap_promos(self, first_index, second_index):
        temp = self.promo_entries[first_index]
        self.promo_entries[first_index] = self.promo_entries[second_index]
        self.promo_entries[second_index] = temp

    def update_dj(self, dj_name, is_live):
        found_dj = self.has_dj(dj_name)
        if found_dj:
            index = self.dj_entries.index(found_dj)
            self.dj_entries[index][1] = is_live
        else:
            raise Exception("No dj found in lineup")

    def export(self):
        data = {"djs": [], "promos": []}
        for dj_name, is_live in self.dj_entries:
            dj = self.ledger.get_dj_by_name(dj_name)
            data["djs"].append(dj.export(is_live))
        for promo_name in self.promo_entries:
            data["promos"].append(self.ledger.get_promo_by_name(promo_name).export())

        return json.dumps(data)

    def to_treeview_values(self):
        return self.dj_entries, self.promo_entries