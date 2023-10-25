# Simple local GUI equiped python assistant to manage JSON files for Hijack events.
# Provided as is, use at your own risk.
# Contact linkcube @ Anison Hijack for assistance.


import json
from functools import partial
import importlib.util
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import time

spec = importlib.util.find_spec("cv2")
if spec is None:
    raise Exception(
        "opencv is not installed, this package is required to run the program!"
    )
import cv2

SOFTWARE_VERSION = "Alpha-0.0.1"
RTMP_US_EAST = "us-east"
RTMP_US_WEST = "us-west"
RTMP_JAPAN = "japan"
RTMP_VALUES = [RTMP_US_EAST, RTMP_US_WEST, RTMP_JAPAN]
DJ_KEY = "djs"
PROMO_KEY = "promos"
LEDGERS_BACKUP = "ledgers_backup"
LINEUP_BACKUP = "lineup_backup"


def load_ledger(ledger_path):
    if not os.path.exists(ledger_path):
        raise Exception("Ledger file does not exist at: " + ledger_path)
    with open(ledger_path, "r") as f:
        data = json.load(f)
    ledger = Ledger()
    ledger.load_data(data)
    return ledger

def load_lineup(lineup_path, ledger):
    if not os.path.exists(lineup_path):
        raise Exception("Lineup file does not exist at: " + lineup_path)
    with open(lineup_path, "r") as f:
        data = json.load(f)
    lineup = Lineup([], [], ledger)
    lineup.load_data(data)
    return lineup


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


class LedgerDJ:
    # Handle DJ information and live or pre-rec data
    def __init__(
        self,
        name,
        logo_path="",
        recording_path="",
        rtmp_server="",
        stream_key="",
        last_live_resolution="",
    ):
        self.name = name
        self.logo_path = logo_path
        self.recording_path = recording_path
        self.rtmp_server = rtmp_server
        self.stream_key = stream_key
        self.last_live_resolution = last_live_resolution

    def get_stream_url(self):
        if self.rtmp_server and self.stream_key:
            return (
                " rtmp://rtmp-"
                + self.rtmp_server
                + ".anisonhijack.moe/live/"
                + self.stream_key
            )
        return None

    def export(self, is_live):
        data = {
            "name": self.name,
            "logo_path": self.logo_path,
        }

        if is_live:
            data["resolution"] = self.last_live_resolution
            data["url"] = self.get_stream_url()
        else:
            vcap = cv2.VideoCapture(self.recording_path)
            if vcap.isOpened():
                width = vcap.get(3)
                height = vcap.get(4)
                data["resolution"] = [width, height]
            data["recording_path"] = self.recording_path

        return data

    def save(self):
        return {
            "name": self.name,
            "logo_path": self.logo_path,
            "recording_path": self.recording_path,
            "rtmp_server": self.rtmp_server,
            "stream_key": self.stream_key,
            "last_live_resolution": self.last_live_resolution,
        }


class LedgerPromo:
    # Handle promotional video data
    def __init__(self, name, path=""):
        self.name = name
        self.path = path

    def export(self):
        data = {"name": self.name, "path": self.path}
        vcap = cv2.VideoCapture(self.path)
        if vcap.isOpened():
            width = vcap.get(3)
            height = vcap.get(4)
            data["resolution"] = [width, height]
        return data

    def save(self):
        return {"name": self.name, "path": self.path}


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


# tkinter GUI


class ShizuApp(Tk):
    def __init__(self):
        Tk.__init__(self)

        self.geometry("800x920")
        self.title("Shizu Assistance")
        style = ttk.Style()
        style.configure("Treeview", rowheight=40)
        self.resizable(0, 0)

        self.ledger = Ledger()
        self.lineup = Lineup([], [], self.ledger)

        # Setup page frames
        self.container_frame = Frame(self)
        self.container_frame.pack(side="top", fill="both", expand=True)
        self.container_frame.grid_rowconfigure(0, weight=1)
        self.container_frame.grid_columnconfigure(0, weight=1)

        bottom_label_frame = Frame(self, background="Black")
        info_label = Label(bottom_label_frame, fg="yellow", bg="black")
        self.info_stringvar = StringVar(value="...")
        info_label["textvariable"] = self.info_stringvar
        info_label.pack(side="left")

        self.frames = {}
        for FrameClass in (HomePage, LedgerPage, LineupPage):
            page_name = FrameClass.__name__
            frame = FrameClass(parent=self.container_frame, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        bottom_label_frame.pack(fill=X)
        self.navigate_to_page("HomePage")

        # Setup menu and navigation
        self.option_add("*tearOff", FALSE)
        menubar = Menu(self)
        menu_file = Menu(menubar)
        menu_edit = Menu(menubar)
        menu_add = Menu(menubar)
        menu_help = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label="Program")
        menu_file.add_command(label="Open Ledger", command=self.open_ledger)
        menu_file.add_command(label="Save Ledger", command=self.save_ledger)
        menu_file.add_command(label="Open Lineup", command=self.open_lineup)
        menu_file.add_command(label="Export Lineup", command=self.export_lineup)
        menu_file.add_separator()
        menu_file.add_command(label="Reset Data", command=self.create_ledger)
        menu_file.add_command(label="Close", command=self.close_app)
        menubar.add_cascade(menu=menu_edit, label="Navigate")
        menu_edit.add_command(
            label="Home", command=partial(self.navigate_to_page, "HomePage")
        )
        menu_edit.add_command(
            label="Ledger", command=partial(self.navigate_to_page, "LedgerPage")
        )
        menu_edit.add_command(
            label="Lineup", command=partial(self.navigate_to_page, "LineupPage")
        )
        menubar.add_cascade(menu=menu_add, label="Add")
        menu_add.add_command(label="New DJ Entry", command=self.create_dj_entry)
        menu_add.add_command(label="New Promo Entry", command=self.create_promo_entry)
        menubar.add_cascade(menu=menu_help, label="Help")
        menu_help.add_command(label="About", command=self.open_about)
        menu_help.add_command(label="There is no more help")
        self["menu"] = menubar
    
    def open_about(self):
        from tkinter import messagebox
        messagebox.showinfo(message=f"Version: {SOFTWARE_VERSION}")

    def navigate_to_page(self, page_name):
        frame = self.frames[page_name]
        frame.navigate()
        self.info_stringvar.set(frame.info)
        frame.tkraise()
        self.current_frame = page_name

    def create_ledger(self):
        self.ledger = Ledger()
        self.lineup = Lineup([], [], self.ledger)

    def open_ledger(self):
        self.ledger = load_ledger(filedialog.askopenfilename())
        self.lineup.ledger = self.ledger
        for _, frame in self.frames.items():
            frame.reload()
    
    def open_lineup(self):
        self.lineup = load_lineup(filedialog.askopenfilename(), self.ledger)
        for _, frame in self.frames.items():
            frame.reload()

    def save_ledger(self):
        target_file = filedialog.askopenfilename()
        if target_file:
            data = self.ledger.save()
            with open(target_file, "w") as f:
                f.write(data)
            backup_path = os.path.join(os.getcwd(), LEDGERS_BACKUP)
            if not os.path.isdir(backup_path):
                os.mkdir(backup_path)
            with open(os.path.join(backup_path, f"{time.strftime('%Y%m%d-%H%M%S')}-{os.path.split(target_file)[1]}"), 'w') as f:
                f.write(data)

    def export_lineup(self):
        target_file = filedialog.askopenfilename()
        if target_file:
            data = self.lineup.export()
            with open(target_file, "w") as f:
                f.write(data)
            backup_path = os.path.join(os.getcwd(), LINEUP_BACKUP)
            if not os.path.isdir(backup_path):
                os.mkdir(backup_path)
            with open(os.path.join(backup_path, f"{time.strftime('%Y%m%d-%H%M%S')}-{os.path.split(target_file)[1]}"), 'w') as f:
                f.write(data)

    def create_dj_entry(self):
        new_dj_name = self.ledger.create_dj_entry()
        ledger_frame = self.frames["LedgerPage"]
        if self.current_frame == "LedgerPage":
            ledger_frame.reload()
        else:
            self.navigate_to_page("LedgerPage")
        ledger_frame.open_dj_edit_window(new_dj_name)

    def create_promo_entry(self):
        new_promo_name = self.ledger.create_promo_entry()
        ledger_frame = self.frames["LedgerPage"]
        if self.current_frame == "LedgerPage":
            ledger_frame.reload()
        else:
            self.navigate_to_page("LedgerPage")
        ledger_frame.open_promo_edit_window(new_promo_name)

    def get_ledger_treeview_values(self):
        if self.ledger:
            return self.ledger.to_treeview_values()

    def get_lineup_treeview_values(self):
        if self.lineup:
            return self.lineup.to_treeview_values()
        return [], []

    def close_app(self):
        self.destroy()


class PageFrame(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

    def navigate(self):
        self.controller.title(self.title)
        self.reload()

    def reload(self):
        pass
        # raise Exception("Not implemented")


def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children("")]
    l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, "", index)

    # reverse sort next time
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


class PopupWindow(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.controller = parent.controller
        self.grab_set()
        self.display_length = 40

    def select_file(self, raw_stringvar, display_stringvar):
        new_file = filedialog.askopenfilename()
        if new_file:
            raw_stringvar.set(new_file)
            self.update_display_var(display_stringvar, new_file)

    def update_display_var(self, stringvar, new_data):
        stringvar.set(self.limit_string(new_data))

    def limit_string(self, string):
        if len(string) > self.display_length:
            return "..." + string[-1 * (self.display_length - 3) :]
        return string

    def exit(self):
        self.parent.close_edit_window()


class TreeManagingPageFrame(PageFrame):
    def __init__(self, parent, controller, dj_columns, promo_columns, sortable=False):
        super().__init__(parent, controller)
        self.dj_tree = ttk.Treeview(self, column=dj_columns, show="headings")
        self.promo_tree = ttk.Treeview(self, column=promo_columns, show="headings")

        for col in dj_columns:
            self.dj_tree.heading(
                col,
                text=col,
                command=lambda _col=col: treeview_sort_column(
                    self.dj_tree, _col, False
                )
                if sortable
                else None,
            )
            self.dj_tree.column(col, anchor=CENTER)

        for col in promo_columns:
            self.promo_tree.heading(
                col,
                text=col,
                command=lambda _col=col: treeview_sort_column(
                    self.promo_tree, _col, False
                )
                if sortable
                else None,
            )
            self.promo_tree.column(col, anchor=CENTER)

        Label(self, text="DJ Entries").pack(fill=X, expand=True)
        self.dj_tree.pack(fill=BOTH, expand=True)
        Label(self, text="Promotional Videos").pack(fill=X, expand=True)
        self.promo_tree.pack(fill=BOTH, expand=True)

        self.dj_tree.bind("<Double-1>", self.double_click_dj_tree)
        self.promo_tree.bind("<Double-1>", self.double_click_promo_tree)
        self.edit_window = None

    def close_edit_window(self):
        self.edit_window.destroy()
        self.edit_window = None

    def open_dj_edit_window(self, dj_tree_item):
        pass

    def open_promo_edit_window(self, promo_tree_item):
        pass

    def double_click_dj_tree(self, event):
        item = self.dj_tree.identify("item", event.x, event.y)
        if item == "":
            return
        if self.edit_window:
            self.edit_window.grab_set()
        else:
            self.open_dj_edit_window(item)

    def double_click_promo_tree(self, event):
        item = self.promo_tree.identify("item", event.x, event.y)
        if item == "":
            return
        if self.edit_window:
            self.edit_window.grab_set()
        else:
            self.open_promo_edit_window(item)

    def reload(self):
        for i in self.dj_tree.get_children():
            self.dj_tree.delete(i)
        for i in self.promo_tree.get_children():
            self.promo_tree.delete(i)


class LedgerDjEditWindow(PopupWindow):
    def __init__(self, parent, dj):
        super().__init__(parent)
        self.ledger_page = parent
        self.geometry("560x220")
        self.title("Edit DJ Entry")
        self.resizable(0, 0)

        # Setup stringvars
        self.dj_name = StringVar(value=dj.name)
        self.logo_path = StringVar()
        self.logo_path_display = StringVar(value="No Logo Set")
        if dj.logo_path:
            self.logo_path.set(dj.logo_path)
            self.update_display_var(self.logo_path_display, dj.logo_path)
        self.recording_path = StringVar()
        self.recording_path_display = StringVar(value="No Recording Set")
        if dj.recording_path:
            self.recording_path.set(dj.recording_path)
            self.update_display_var(self.recording_path_display, dj.recording_path)
        self.original_data = dj
        self.rtmp_stringvar = StringVar()
        if dj.rtmp_server:
            self.rtmp_stringvar.set(dj.rtmp_server)
        self.stream_key = StringVar()
        if dj.stream_key:
            self.stream_key.set(dj.stream_key)

        # Element inits
        content = ttk.Frame(self)
        name_label = Label(content, text="Name")
        logo_label = Label(content, text="Logo")
        recording_label = Label(content, text="Recording")
        rtmp_label = Label(content, text="RTMP Server")
        stream_key_label = Label(content, text="Stream Key")

        name_entry = ttk.Entry(content, textvariable=self.dj_name, width=30)
        logo_value_label = Label(content, textvariable=self.logo_path_display)
        logo_button = ttk.Button(
            content,
            text="Select Logo",
            command=partial(self.select_file, self.logo_path, self.logo_path_display),
        )
        recording_value_label = Label(content, textvariable=self.recording_path_display)
        recording_button = ttk.Button(
            content,
            text="Select Recording",
            command=partial(
                self.select_file, self.recording_path, self.recording_path_display
            ),
        )
        rtmp_box = ttk.Combobox(
            content, textvariable=self.rtmp_stringvar, values=RTMP_VALUES
        )
        stream_key_entry = ttk.Entry(content, textvariable=self.stream_key, width=30)
        save_button = ttk.Button(content, text="Save", command=self.save)
        cancel_button = ttk.Button(content, text="Cancel", command=self.exit)
        delete_button = ttk.Button(content, text="Delete", command=self.delete)
        self.add_to_lineup_button = ttk.Button(
            content, text="Add to Lineup", command=self.add_to_lineup
        )
        if self.controller.lineup.has_dj(dj.name):
            self.add_to_lineup_button.state(["disabled"])

        # Grid definitions
        content.grid(column=0, row=0)
        name_label.grid(column=0, row=0, sticky="w", pady=2)
        logo_label.grid(column=0, row=1, sticky="w", pady=2)
        recording_label.grid(column=0, row=2, sticky="w", pady=2)
        rtmp_label.grid(column=0, row=3, sticky="w", pady=2)
        stream_key_label.grid(column=0, row=4, sticky="w", pady=2)

        name_entry.grid(column=1, row=0, columnspan=1, sticky="w", pady=2)
        logo_button.grid(column=1, row=1, pady=2)
        logo_value_label.grid(column=2, row=1, sticky="w", pady=2)
        recording_button.grid(column=1, row=2, pady=2)
        recording_value_label.grid(column=2, row=2, sticky="w", pady=2)
        rtmp_box.grid(column=1, row=3, columnspan=2, sticky="w", pady=2)
        stream_key_entry.grid(column=1, row=4, columnspan=2, sticky="w", pady=2)

        save_button.grid(column=1, row=5, pady=10)
        cancel_button.grid(column=2, row=5, pady=10, padx=10)
        delete_button.grid(column=2, row=0, pady=2)
        self.add_to_lineup_button.grid(column=0, row=5, pady=10)

        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.columnconfigure(2, weight=1)
        content.pack(fill="both", expand=True, padx=20, pady=20)

    def add_to_lineup(self):
        self.controller.lineup.add_dj(self.original_data.name)
        self.add_to_lineup_button.state(["disabled"])

    def save(self):
        self.controller.ledger.update_dj(
            self.original_data.name,
            self.dj_name.get(),
            self.logo_path.get(),
            self.recording_path.get(),
            self.rtmp_stringvar.get(),
            self.stream_key.get(),
        )
        self.parent.reload()
        self.exit()

    def delete(self):
        self.ledger_page.controller.ledger.delete_dj(self.original_data.name)
        try:
            self.ledger_page.controller.lineup.remove_dj(self.original_data.name)
        finally:
            self.ledger_page.reload()
            self.exit()


class LedgerPromoEditWindow(PopupWindow):
    def __init__(self, parent, promo):
        super().__init__(parent)
        self.geometry("540x140")
        self.title("Edit Promo Entry")
        self.resizable(0, 0)

        # Setup stringvars
        self.promo_name = StringVar(value=promo.name)
        self.recording_path = StringVar()
        self.recording_path_display = StringVar(value="No Recording Set")
        if promo.path:
            self.recording_path.set(promo.path)
            self.update_display_var(self.recording_path_display, promo.path)
        self.original_data = promo

        # Element inits
        content = ttk.Frame(self)
        name_label = Label(content, text="Name")
        recording_label = Label(content, text="Recording")

        name_entry = ttk.Entry(content, textvariable=self.promo_name, width=30)
        recording_value_label = Label(content, textvariable=self.recording_path_display)
        recording_button = ttk.Button(
            content,
            text="Select Recording",
            command=partial(
                self.select_file, self.recording_path, self.recording_path_display
            ),
        )
        save_button = ttk.Button(content, text="Save", command=self.save)
        cancel_button = ttk.Button(content, text="Cancel", command=self.exit)
        delete_button = ttk.Button(content, text="Delete", command=self.delete)
        self.add_to_lineup_button = ttk.Button(
            content, text="Add to Lineup", command=self.add_to_lineup
        )
        if self.controller.lineup.has_promo(promo.name):
            self.add_to_lineup_button.state(["disabled"])

        # Grid definitions
        content.grid(column=0, row=0)
        name_label.grid(column=0, row=0, sticky="w", pady=2)
        recording_label.grid(column=0, row=2, sticky="w", pady=2)

        name_entry.grid(column=1, row=0, columnspan=1, sticky="w", pady=2)
        recording_button.grid(column=1, row=2, pady=2)
        recording_value_label.grid(column=2, row=2, sticky="w", pady=2)

        save_button.grid(column=1, row=5, pady=10)
        cancel_button.grid(column=2, row=5, pady=10, padx=10)
        delete_button.grid(column=2, row=0, pady=2)
        self.add_to_lineup_button.grid(column=0, row=5, pady=10)

        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.columnconfigure(2, weight=1)
        content.pack(fill="both", expand=True, padx=20, pady=20)

    def add_to_lineup(self):
        self.controller.lineup.add_promo(self.original_data.name)
        self.add_to_lineup_button.state(["disabled"])

    def save(self):
        self.controller.ledger.update_promo(
            self.original_data.name, self.promo_name.get(), self.recording_path.get()
        )
        self.parent.reload()
        self.exit()

    def delete(self):
        self.controller.ledger.delete_promo(self.original_data.name)
        try:
            self.controller.lineup.remove_promo(self.original_data.name)
        finally:
            self.parent.reload()
            self.exit()


class LedgerPage(TreeManagingPageFrame):
    def __init__(self, parent, controller):
        dj_columns = ["Name", "Has Logo", "RTMP", "Has Recording"]
        promo_columns = ["Name", "Has Recording"]
        super().__init__(parent, controller, dj_columns, promo_columns, sortable=True)
        self.title = "Shizu Assistance - Ledger"
        self.info = "Manage DJ and promotional video data"

    def reload(self):
        super().reload()

        dj_rows, promo_rows = self.controller.get_ledger_treeview_values()
        for dj_values in dj_rows:
            self.dj_tree.insert(
                "", "end", dj_values[0], text=dj_values[0], values=dj_values
            )
        for promo_values in promo_rows:
            self.promo_tree.insert(
                "", "end", promo_values[0], text=promo_values[0], values=promo_values
            )

    def open_dj_edit_window(self, dj_name):
        self.edit_window = LedgerDjEditWindow(
            self, self.controller.ledger.get_dj_by_name(dj_name)
        )
        self.edit_window.protocol("WM_DELETE_WINDOW", self.close_edit_window)

    def open_promo_edit_window(self, promo_name):
        self.edit_window = LedgerPromoEditWindow(
            self, self.controller.ledger.get_promo_by_name(promo_name)
        )
        self.edit_window.protocol("WM_DELETE_WINDOW", self.close_edit_window)


class LineupDjEditWindow(PopupWindow):
    def __init__(self, parent, dj, is_live):
        super().__init__(parent)
        self.display_length = 80
        self.geometry("420x190")
        self.title("Edit DJ Entry")
        self.grab_set()
        self.resizable(0, 0)
        self.dj_name = dj.name
        # TODO: fill in rest of rec/live info as labels?

        # Setup vars
        self.is_live = BooleanVar(value=is_live)
        not_set = "Not Set"

        # Element inits
        content = ttk.Frame(self)
        name_label = Label(content, text=f"Name: {self.dj_name}")
        recording_label = Label(
            content,
            text=f"Recording: {self.limit_string(dj.recording_path) if dj.recording_path else not_set}",
        )
        rtmp_label = Label(
            content, text=f"RTMP Server: {dj.rtmp_server if dj.rtmp_server else not_set}"
        )
        stream_key_label = Label(
            content, text=f"Stream Key: {dj.stream_key if dj.stream_key else not_set}"
        )
        is_live_label = Label(content, text="Is Live:")
        true_radio = Radiobutton(content, text="True", variable=self.is_live, value=True)
        false_radio = Radiobutton(
            content, text="False", variable=self.is_live, value=False
        )
        save_button = ttk.Button(content, text="Save", command=self.save)
        cancel_button = ttk.Button(content, text="Cancel", command=self.exit)
        delete_button = ttk.Button(content, text="Remove", command=self.delete)

        # Grid definitions
        content.grid(column=0, row=0)
        name_label.grid(column=0, row=0, sticky="w", pady=2, columnspan=3)
        recording_label.grid(column=0, row=1, sticky="w", pady=2, columnspan=3)
        rtmp_label.grid(column=0, row=2, sticky="w", pady=2, columnspan=3)
        stream_key_label.grid(column=0, row=3, sticky="w", pady=2, columnspan=3)
        is_live_label.grid(column=0, row=4, sticky="w", pady=2)

        true_radio.grid(column=1, row=4, pady=2)
        false_radio.grid(column=2, row=4, sticky="w", pady=2)

        save_button.grid(column=0, row=5, pady=2)
        cancel_button.grid(column=1, row=5, pady=2, padx=2)
        delete_button.grid(column=2, row=5, pady=2)

        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.columnconfigure(2, weight=1)
        content.pack(fill="both", expand=True, padx=20, pady=20)

    def save(self):
        self.controller.lineup.update_dj(self.dj_name, self.is_live.get())
        self.parent.reload()
        self.exit()

    def delete(self):
        self.controller.lineup.remove_dj(self.dj_name)
        self.parent.reload()
        self.exit()


class LineupPromoEditWindow(PopupWindow):
    def __init__(self, parent, promo):
        super().__init__(parent)
        self.geometry("420x110")
        self.title("Edit Promo Entry")
        self.resizable(0, 0)
        self.promo_name = promo.name
        self.display_length = 80
        not_set = "Not Set"

        # Element inits
        content = ttk.Frame(self)
        name_label = Label(content, text=f"Name: {self.promo_name}")
        path_label = Label(
            content,
            text=f"Path: {self.limit_string(promo.path) if promo.path else not_set}",
        )
        cancel_button = ttk.Button(content, text="Cancel", command=self.exit)
        delete_button = ttk.Button(content, text="Remove", command=self.delete)

        # Grid definitions
        content.grid(column=0, row=0)
        name_label.grid(column=0, row=0, sticky="w", pady=2, columnspan=2)
        path_label.grid(column=0, row=1, sticky="w", pady=2, columnspan=2)

        cancel_button.grid(column=0, row=2, pady=2, padx=2)
        delete_button.grid(column=1, row=2, pady=2)

        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.pack(fill="both", expand=True, padx=20, pady=20)

    def delete(self):
        self.controller.lineup.remove_promo(self.promo_name)
        self.parent.reload()
        self.exit()


class LineupPage(TreeManagingPageFrame):
    def __init__(self, parent, controller):
        dj_columns = ["Name", "Is Live"]
        promo_columns = ["Name"]
        super().__init__(parent, controller, dj_columns, promo_columns)
        self.title = "Shizu Assistance - Lineup"
        self.info = "Create a lineup for an event"
        self.controller.bind("<Button-1>", self.on_click)

    # Logic to allow drag and drop
    def changeOrder(self, swapped, held, initial, tree):
        children = tree.get_children()
        swapped_index = tree.index(swapped)
        tree.move(swapped, "", initial)
        if swapped_index == len(children) - 1:
            tree.move(held, "", "end")
        else:
            tree.move(held, "", swapped_index)
        if tree is self.dj_tree:
            self.controller.lineup.swap_djs(swapped_index, initial)
        else:
            self.controller.lineup.swap_promos(swapped_index, initial)

    def open_dj_edit_window(self, dj_tree_item):
        dj_info = self.controller.lineup.get_dj_by_name(dj_tree_item)
        self.edit_window = LineupDjEditWindow(
            self, self.controller.ledger.get_dj_by_name(dj_tree_item), dj_info[1]
        )
        self.edit_window.protocol("WM_DELETE_WINDOW", self.close_edit_window)

    def open_promo_edit_window(self, promo_tree_item):
        self.edit_window = LineupPromoEditWindow(
            self, self.controller.ledger.get_promo_by_name(promo_tree_item)
        )
        self.edit_window.protocol("WM_DELETE_WINDOW", self.close_edit_window)

    def on_click(self, event):
        if self.controller.current_frame != "LineupPage":
            return
        widget = event.widget
        dj_item = self.dj_tree.identify("item", event.x, event.y)
        promo_item = self.promo_tree.identify("item", event.x, event.y)
        if dj_item:
            tree_index = self.dj_tree.index(dj_item)
            widget.bind(
                "<ButtonRelease-1>",
                lambda event: self.drag_release(
                    event, dj_item, tree_index, self.dj_tree
                ),
            )
            self.config(cursor="exchange")
        elif promo_item:
            tree_index = self.promo_tree.index(promo_item)
            widget.bind(
                "<ButtonRelease-1>",
                lambda event: self.drag_release(
                    event, promo_item, tree_index, self.promo_tree
                ),
            )
            self.config(cursor="exchange")
        else:
            self.unbind("<ButtonRelease-1>")
            self.config(cursor="arrow")

    def drag_release(self, event, widget, tree_index, tree):
        target_widget = tree.identify("item", event.x, event.y)
        if target_widget:
            self.changeOrder(target_widget, widget, tree_index, tree)
        self.config(cursor="arrow")

    def reload(self):
        super().reload()

        dj_rows, promo_rows = self.controller.get_lineup_treeview_values()
        for dj_values in dj_rows:
            self.dj_tree.insert(
                "", "end", dj_values[0], text=dj_values[0], values=dj_values
            )
        for promo_values in promo_rows:
            self.promo_tree.insert(
                "", "end", promo_values, text=promo_values, values=promo_values
            )


class HomePage(PageFrame):
    readme_text = [
        "",
        "This program manages a 'ledger' of DJs and Promotional videos used for stream, that can be selectively added to a 'lineup'. Once the lineup is complete, it can be exported to a json file for use in the accompanying OBS plugin to generate scenes for each of the selected DJs and promos.",
        "If you are using an existing ledger and lineup, make sure to load the ledger then lineup, either through the menu or home buttons, before continuing.",
        "To add a new DJ entry, click on the Add menu > New DJ Entry, which will bring up the new entry edit window to be filled in. Adding to lineup will not save or exit the current entry, make sure to save once you're done! " +
        "Likewise, the process is similar for adding promotional videos, which only have a name and recording path to manage.",
        "",
        "On the ledger page, you can edit/delete entries for DJs or Promotional videos by double cicking a row, once you are done making any changes make sure to save though the Program menu > Save Ledger button.",
        "",
        "The lineup page will let you set the order to DJs and Promotional videos after adding them, you can edit DJ entries to either be live or pre-recorded, but otherwise you can only delete these entries after double clicking. " +
        "Once you are done setting up your lineup, make sure to export using Program menu > Export Lineup. This will save the file either for later loading/edits or for use in the OBS plugin.",
        "",
        "When saving or exporting data, a backup will be made in a subdirectory of where this file is, along with the date+time it was saved. Resetting the data will only clear the ledger/lineup in memory, files are not changed.",
        "",
        "Thanks for using the program, make sure to report any issues with the software."
    ]

    checklist_text = [
        "",
        "0. Load .json files",
        "    - Ledger should be the latest",
        "    - Load a lineup if working on an existing one",
        "",
        "1. Fill out entries in the DJ ledger",
        "    - Name and logo are set",
        "    - Set RTMP server + stream key, or recording path",
        "",
        "2. Enter Promotional videos",
        "    - Set recording path"
        "3. Add entries to the lineup for the event",
        "",
        "    - In the lineup page, set the order",
        "    - And set whether DJs are live or not",
        "4. Save the ledger, export the lineup",
        "",
        "5. (In OBS), Load the exported lineup",
        "    - [TEMPORARY] Delete the existing DJ and Promotional scenes, keep opening/ending/problems/etc scenes",
        "    - Run the script, and verify each of the scenes",
        "    - Live DJs will need their sources to be fitted to the overlay",
        "",
        "6. Everything should be setup, or something went horribly wrong!"
    ]
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.title = "Shizu Assistance - Home"
        self.info = (
            "Welcome! Be sure to check the readme and checklist before starting."
        
        )
        self.content_title = StringVar()
        self.context_stringvar = StringVar()

        # Elements
        content = ttk.Frame(self)
        open_ledger_button = ttk.Button(content, text="Open Ledger", command=self.controller.open_ledger)
        open_lineup_button = ttk.Button(content, text="Open Lineup", command=self.controller.open_lineup)
        ledger_button = ttk.Button(content, text="Go to Ledger", command=partial(self.controller.navigate_to_page, "LedgerPage"))
        lineup_button = ttk.Button(content, text="Go to Lineup", command=partial(self.controller.navigate_to_page, "LineupPage"))
        readme_button = ttk.Button(content, text="Read Me", command=self.open_readme)
        checklist_button = ttk.Button(content, text="Checklist", command=self.open_checklist)
        content_title_label = Label(content, textvariable=self.content_title, font=("Arial", 25))
        content_text_label = Label(content, textvariable=self.context_stringvar, wraplength=740, justify=LEFT, font=("Arial", 15))

        # Grid
        content.grid(column=0, row=0)
        open_ledger_button.grid(column=0, row=0, pady=10, padx=10)
        open_lineup_button.grid(column=1, row=0, pady=10, padx=10)
        ledger_button.grid(column=2, row=0, pady=10, padx=10)
        lineup_button.grid(column=3, row=0, pady=10, padx=10)
        readme_button.grid(column=0, row=1, pady=10, padx=10, columnspan=2)
        checklist_button.grid(column=2, row=1, pady=10, padx=10, columnspan=2)
        content_title_label.grid(column=0, row=2, columnspan=4, padx=10, pady=10)
        content_text_label.grid(column=0, row=3, columnspan=4, pady=10, padx=10, sticky="nw")

        content.rowconfigure(0, weight=0)
        content.rowconfigure(1, weight=0)
        content.rowconfigure(2, weight=0)
        content.rowconfigure(3, weight=1)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.columnconfigure(2, weight=1)
        content.columnconfigure(3, weight=1)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        self.open_readme()
    
    def open_readme(self):
        self.content_title.set("Readme")
        self.context_stringvar.set("\n".join(self.readme_text))
    
    def open_checklist(self):
        self.content_title.set("Checklist")
        self.context_stringvar.set("\n".join(self.checklist_text))



if __name__ == "__main__":
    app = ShizuApp()
    app.mainloop()
