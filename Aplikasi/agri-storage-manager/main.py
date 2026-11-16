#!/usr/bin/env python3
"""
Agri-Storage Manager
Pusat Manajemen Stok Komoditas, Inventaris Saprotan & Fasilitas Silo/Gudang
Sesuai UI/10_agri_storage_manager.md & PRD 7.10
"""

import sys
import os
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "common"))

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib

try:
    from agristation_common import (
        init_db, get_connection, AgriWindow, AgriHeader, KPICard,
        PillTabs, format_number, format_date_id, escape
    )
except ImportError:
    from common import (
        init_db, get_connection, AgriWindow, AgriHeader, KPICard,
        PillTabs, format_number, format_date_id, escape
    )

class StorageManagerApp(AgriWindow):
    def __init__(self):
        super().__init__(
            title="Agri-Storage Manager - Stok Komoditas & Gudang",
            icon_name="agri-storage-manager",
            default_width=1120,
            default_height=760
        )
        init_db()

        self.current_filter = "Semua Stok"
        self.search_text = ""

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        # 1. Header with Dual Action Buttons
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        header_box.set_margin_start(20)
        header_box.set_margin_end(20)
        header_box.set_margin_top(16)
        header_box.set_margin_bottom(16)

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        lbl_title = Gtk.Label(xalign=0)
        lbl_title.set_markup("<span size='x-large' weight='bold' color='#1E293B'>Stok Komoditas &amp; Gudang</span>")
        title_box.pack_start(lbl_title, False, False, 0)
        lbl_sub = Gtk.Label(xalign=0)
        lbl_sub.set_markup("<span size='small' color='#64748B'>Pengawasan Kapasitas Silo Pengering, Gudang Komoditas &amp; Mutasi Stok</span>")
        title_box.pack_start(lbl_sub, False, False, 0)
        header_box.pack_start(title_box, True, True, 0)

        # Right buttons
        ctrl_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        btn_backup = Gtk.Button(label="💾 Cadangan")
        btn_backup.get_style_context().add_class("btn-secondary")
        btn_backup.connect("clicked", lambda w: self.open_backup_dialog())
        ctrl_box.pack_start(btn_backup, False, False, 0)

        btn_in = Gtk.Button(label="+ Stok Masuk")
        btn_in.get_style_context().add_class("btn-primary")
        btn_in.connect("clicked", self._on_stock_in_clicked)
        ctrl_box.pack_start(btn_in, False, False, 0)

        btn_out = Gtk.Button(label="- Stok Keluar / Jual")
        btn_out.get_style_context().add_class("btn-outline")
        btn_out.connect("clicked", self._on_stock_out_clicked)
        ctrl_box.pack_start(btn_out, False, False, 0)

        header_box.pack_end(ctrl_box, False, False, 0)
        main_box.pack_start(header_box, False, False, 0)

        # Scroller
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        content_box.set_margin_bottom(24)
        scroller.add(content_box)

        # 2. 3 Facility Capacity Cards
        self.capacity_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        content_box.pack_start(self.capacity_row, False, False, 0)

        # 3. Filter Bar (Pill Tabs & Search)
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        content_box.pack_start(filter_box, False, False, 0)

        pill_options = ["Semua Stok", "Hasil Panen", "Benih", "Pupuk & Obat"]
        self.tabs = PillTabs(pill_options, self._on_filter_changed)
        filter_box.pack_start(self.tabs, False, False, 0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Cari nama komoditas, kategori, atau gudang...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        filter_box.pack_start(self.search_entry, True, True, 0)

        # 4. Inventory Table
        table_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        table_card.get_style_context().add_class("agri-card")
        content_box.pack_start(table_card, True, True, 0)

        lbl_tbl = Gtk.Label(xalign=0)
        lbl_tbl.set_markup("<b>Daftar Inventaris Barang &amp; Komoditas Terdata</b>")
        table_card.pack_start(lbl_tbl, False, False, 0)

        # TreeStore: id, item_name, category, location, qty_str, last_date, condition_str
        self.store = Gtk.ListStore(int, str, str, str, str, str, str)
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.set_rules_hint(True)

        cols = [
            ("ID", 0, 45, 0.0),
            ("Nama Komoditas / Barang", 1, 240, 0.0),
            ("Kategori", 2, 130, 0.5),
            ("Lokasi Fasilitas", 3, 190, 0.0),
            ("Jumlah Stok Saat Ini", 4, 160, 1.0),
            ("Tanggal Masuk Terakhir", 5, 140, 0.0),
            ("Kondisi Fisik / Kadar Air", 6, 180, 0.0)
        ]

        for title, col_idx, width, align in cols:
            renderer = Gtk.CellRendererText()
            renderer.set_alignment(align, 0.5)
            col = Gtk.TreeViewColumn(title, renderer, text=col_idx)
            col.set_min_width(width)
            col.set_resizable(True)
            self.tree.append_column(col)

        table_scroller = Gtk.ScrolledWindow()
        table_scroller.set_min_content_height(350)
        table_scroller.add(self.tree)
        table_card.pack_start(table_scroller, True, True, 0)

        self.refresh_data()

    def _on_filter_changed(self, option):
        self.current_filter = option
        self.refresh_data()

    def _on_search_changed(self, entry):
        self.search_text = entry.get_text().strip().lower()
        self.refresh_data()

    def refresh_data(self):
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Update Capacity Cards
        for child in self.capacity_row.get_children():
            self.capacity_row.remove(child)

        cursor.execute("SELECT id, code, name, facility_type, capacity_ton, used_ton FROM storage_locations ORDER BY id ASC")
        locations = cursor.fetchall()

        for loc in locations:
            l_id, code, name, f_type, cap, used = loc
            card = self._create_facility_card(code, name, f_type, cap, used)
            self.capacity_row.pack_start(card, True, True, 0)

        # 2. Update Table
        self.store.clear()
        query = """
            SELECT inv.id, inv.item_name, inv.category, loc.name,
                   inv.quantity_kg, inv.package_count, inv.last_in_date,
                   inv.moisture_pct, inv.condition_status
            FROM storage_inventory inv
            JOIN storage_locations loc ON inv.storage_location_id = loc.id
            ORDER BY inv.id ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        for r in rows:
            i_id, item_name, cat, loc_name, qty_kg, pkg_cnt, last_d, moist, cond = r

            # Category filter
            if self.current_filter != "Semua Stok":
                if self.current_filter == "Pupuk & Obat" and cat not in ("Pupuk", "Obat"):
                    continue
                elif self.current_filter != "Pupuk & Obat" and cat != self.current_filter:
                    continue

            qty_str = f"{format_number(qty_kg, 'Kg')} ({pkg_cnt} Sak)"

            # REQ-APP10-003: Moisture check (>14% warning)
            if moist is not None and moist > 14.0:
                cond_str = f"⚠️ KA {format_number(moist)}% • {cond} (Lembab)"
            elif moist is not None and moist > 0:
                cond_str = f"KA {format_number(moist)}% • {cond}"
            else:
                cond_str = f"{cond} • Baik"

            # Search text filter
            if self.search_text:
                searchable = f"{item_name} {cat} {loc_name} {cond_str} {qty_str}".lower()
                if self.search_text not in searchable:
                    continue

            self.store.append([
                i_id,
                item_name,
                cat,
                loc_name,
                qty_str,
                format_date_id(last_d),
                cond_str
            ])

        conn.close()
        self.capacity_row.show_all()

    def _create_facility_card(self, code, name, f_type, cap_ton, used_ton):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.get_style_context().add_class("agri-card")

        pct = int(round(used_ton / cap_ton * 100)) if cap_ton > 0 else 0
        frac = min(1.0, max(0.0, used_ton / cap_ton)) if cap_ton > 0 else 0.0

        # Header
        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lbl_code = Gtk.Label(xalign=0)
        lbl_code.set_markup(f"<span size='small' weight='bold' color='#64748B'>{escape(code)} • {escape(f_type)}</span>")
        h_box.pack_start(lbl_code, True, True, 0)

        badge = Gtk.Label()
        badge.get_style_context().add_class("badge")
        if pct >= 95:
            badge.get_style_context().add_class("badge-danger")
            badge.set_text("HAMPIR PENUH")
        elif pct >= 85:
            badge.get_style_context().add_class("badge-warning")
            badge.set_text("WASPADA")
        else:
            badge.get_style_context().add_class("badge-mint")
            badge.set_text("KAPASITAS AMAN")
        h_box.pack_end(badge, False, False, 0)
        card.pack_start(h_box, False, False, 0)

        # Name
        lbl_name = Gtk.Label(xalign=0)
        lbl_name.set_markup(f"<span weight='bold' color='#1E293B'>{escape(name)}</span>")
        card.pack_start(lbl_name, False, False, 0)

        # Capacity numbers
        nums_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lbl_nums = Gtk.Label(xalign=0)
        lbl_nums.set_markup(f"<span size='large' weight='bold' color='#1E293B'>{format_number(used_ton, 'Ton')}</span> / <span color='#64748B'>{format_number(cap_ton, 'Ton')}</span>")
        nums_box.pack_start(lbl_nums, True, True, 0)

        lbl_pct = Gtk.Label(xalign=1)
        lbl_pct.set_markup(f"<span weight='bold' color='#2E7D32'>{pct}% Terisi</span>")
        nums_box.pack_end(lbl_pct, False, False, 0)
        card.pack_start(nums_box, False, False, 0)

        # Progress bar (turns red when >= 95%, amber when >= 85%) (REQ-APP10-004)
        pbar = Gtk.ProgressBar()
        pbar.set_fraction(frac)
        if pct >= 95:
            pbar.get_style_context().add_class("progress-red")
        elif pct >= 85:
            pbar.get_style_context().add_class("progress-amber")
        card.pack_start(pbar, False, False, 0)

        return card

    def _on_stock_in_clicked(self, widget):
        dialog = StockInDialog(self)
        dialog.run()
        dialog.destroy()
        self.refresh_data()

    def _on_stock_out_clicked(self, widget):
        dialog = StockOutDialog(self)
        dialog.run()
        dialog.destroy()
        self.refresh_data()

class StockInDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Catat Mutasi Stok Masuk", transient_for=parent, flags=0)
        self.set_default_size(500, 460)
        self.parent_win = parent

        box = self.get_content_area()
        box.set_spacing(10)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(16)
        box.set_margin_bottom(16)

        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(10)
        box.pack_start(grid, True, True, 0)

        # Location
        grid.attach(Gtk.Label(label="Fasilitas Penyimpanan:", xalign=0), 0, 0, 1, 1)
        self.combo_loc = Gtk.ComboBoxText()
        self.loc_info = []

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, code, name, capacity_ton, used_ton FROM storage_locations")
        for l_id, code, name, cap, used in cursor.fetchall():
            sisa = max(0.0, cap - used)
            self.combo_loc.append_text(f"{code} - {name} (Sisa: {format_number(sisa, 'Ton')})")
            self.loc_info.append((l_id, sisa))
        conn.close()
        if self.loc_info:
            self.combo_loc.set_active(0)
        grid.attach(self.combo_loc, 1, 0, 1, 1)

        # Item Name
        grid.attach(Gtk.Label(label="Nama Komoditas / Barang:", xalign=0), 0, 1, 1, 1)
        self.entry_item = Gtk.Entry()
        self.entry_item.set_placeholder_text("Contoh: Gabah Kering Giling (GKG) Ciherang")
        grid.attach(self.entry_item, 1, 1, 1, 1)

        # Category
        grid.attach(Gtk.Label(label="Kategori Barang:", xalign=0), 0, 2, 1, 1)
        self.combo_cat = Gtk.ComboBoxText()
        for c in ["Hasil Panen", "Benih", "Pupuk", "Obat"]:
            self.combo_cat.append_text(c)
        self.combo_cat.set_active(0)
        grid.attach(self.combo_cat, 1, 2, 1, 1)

        # Quantity Kg
        grid.attach(Gtk.Label(label="Bobot Masuk (Kg):", xalign=0), 0, 3, 1, 1)
        self.entry_qty = Gtk.Entry()
        self.entry_qty.set_text("2000.0")
        grid.attach(self.entry_qty, 1, 3, 1, 1)

        # Moisture pct
        grid.attach(Gtk.Label(label="Kadar Air (%) (jika biji):", xalign=0), 0, 4, 1, 1)
        self.entry_moist = Gtk.Entry()
        self.entry_moist.set_text("13.0")
        grid.attach(self.entry_moist, 1, 4, 1, 1)

        # Source / Origin
        grid.attach(Gtk.Label(label="Asal Sumber / Blok Panen:", xalign=0), 0, 5, 1, 1)
        self.entry_source = Gtk.Entry()
        self.entry_source.set_placeholder_text("Contoh: Panen Blok A1")
        grid.attach(self.entry_source, 1, 5, 1, 1)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(12)
        btn_cancel = Gtk.Button(label="Batal")
        btn_cancel.get_style_context().add_class("btn-secondary")
        btn_cancel.connect("clicked", lambda w: self.response(Gtk.ResponseType.CANCEL))
        btn_box.pack_end(btn_cancel, False, False, 0)

        btn_save = Gtk.Button(label="Simpan Stok Masuk")
        btn_save.get_style_context().add_class("btn-primary")
        btn_save.connect("clicked", self._on_save)
        btn_box.pack_end(btn_save, False, False, 0)
        box.pack_start(btn_box, False, False, 0)

        self.show_all()

    def _on_save(self, widget):
        idx = self.combo_loc.get_active()
        if idx < 0 or not self.loc_info:
            self.parent_win.show_error("Peringatan", "Pilih lokasi fasilitas gudang.")
            return

        loc_id, sisa_ton = self.loc_info[idx]
        item_name = self.entry_item.get_text().strip()
        cat = self.combo_cat.get_active_text()
        qty_str = self.entry_qty.get_text().strip().replace(",", ".")
        moist_str = self.entry_moist.get_text().strip().replace(",", ".")
        source = self.entry_source.get_text().strip()

        if not item_name or not qty_str or not source:
            self.parent_win.show_error("Peringatan", "Nama barang, jumlah kg, dan asal sumber wajib diisi.")
            return

        try:
            qty_kg = float(qty_str)
            if qty_kg <= 0:
                raise ValueError()
        except ValueError:
            self.parent_win.show_error("Peringatan", "Bobot masuk harus berupa angka lebih besar dari 0.")
            return

        # REQ-APP10-001: Cannot exceed remaining capacity
        if (qty_kg / 1000.0) > (sisa_ton + 0.001):
            self.parent_win.show_error(
                "Kapasitas Penuh",
                f"Jumlah masuk ({qty_kg/1000.0:.2f} Ton) melebihi sisa kapasitas gudang ({sisa_ton:.2f} Ton)."
            )
            return

        try:
            moist = float(moist_str) if moist_str else None
        except ValueError:
            moist = None

        today_s = datetime.date.today().strftime("%Y-%m-%d")
        pkg_cnt = int(round(qty_kg / 50.0))
        cond = "Baik" if (moist is None or moist <= 14.0) else "Lembab"

        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                # Check if item exists in location
                cursor.execute("""
                    SELECT id FROM storage_inventory
                    WHERE storage_location_id = ? AND item_name = ?
                """, (loc_id, item_name))
                existing = cursor.fetchone()

                if existing:
                    inv_id = existing[0]
                else:
                    cursor.execute("""
                        INSERT INTO storage_inventory (storage_location_id, item_name, category, quantity_kg, package_count, moisture_pct, condition_status, last_in_date)
                        VALUES (?, ?, ?, 0, 0, ?, ?, ?)
                    """, (loc_id, item_name, cat, moist, cond, today_s))
                    inv_id = cursor.lastrowid

                # Insert storage movement (which triggers auto updates!)
                cursor.execute("""
                    INSERT INTO storage_movements (storage_inventory_id, movement_type, quantity_kg, movement_date, destination_or_source, notes)
                    VALUES (?, 'Masuk', ?, ?, ?, ?)
                """, (inv_id, qty_kg, today_s, source, f"Penerimaan {cat}"))

            self.response(Gtk.ResponseType.OK)
        except Exception as e:
            self.parent_win.show_error("Gagal Menyimpan", f"Error:\n{e}")
        finally:
            conn.close()

class StockOutDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Catat Mutasi Stok Keluar / Penjualan", transient_for=parent, flags=0)
        self.set_default_size(500, 420)
        self.parent_win = parent

        box = self.get_content_area()
        box.set_spacing(10)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(16)
        box.set_margin_bottom(16)

        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(10)
        box.pack_start(grid, True, True, 0)

        # Inventory item
        grid.attach(Gtk.Label(label="Pilih Barang dari Gudang:", xalign=0), 0, 0, 1, 1)
        self.combo_item = Gtk.ComboBoxText()
        self.item_info = []

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT inv.id, inv.item_name, loc.name, inv.quantity_kg
            FROM storage_inventory inv
            JOIN storage_locations loc ON inv.storage_location_id = loc.id
            WHERE inv.quantity_kg > 0
        """)
        for i_id, i_name, l_name, qty in cursor.fetchall():
            self.combo_item.append_text(f"{i_name} ({l_name}) - Stok: {format_number(qty, 'Kg')}")
            self.item_info.append((i_id, qty, i_name))
        conn.close()
        if self.item_info:
            self.combo_item.set_active(0)
        grid.attach(self.combo_item, 1, 0, 1, 1)

        # Qty Out
        grid.attach(Gtk.Label(label="Jumlah Dikeluarkan (Kg):", xalign=0), 0, 1, 1, 1)
        self.entry_qty = Gtk.Entry()
        self.entry_qty.set_text("500.0")
        grid.attach(self.entry_qty, 1, 1, 1, 1)

        # Destination / Buyer
        grid.attach(Gtk.Label(label="Tujuan / Pembeli / Penggunaan:", xalign=0), 0, 2, 1, 1)
        self.entry_dest = Gtk.Entry()
        self.entry_dest.set_placeholder_text("Contoh: Pembeli CV Beras Sejahtera / Pemakaian Blok B1")
        grid.attach(self.entry_dest, 1, 2, 1, 1)

        # Auto Sales Revenue IDR (Optional)
        grid.attach(Gtk.Label(label="Total Nilai Penjualan (Rp):", xalign=0), 0, 3, 1, 1)
        self.entry_revenue = Gtk.Entry()
        self.entry_revenue.set_placeholder_text("Kosongkan jika bukan penjualan")
        grid.attach(self.entry_revenue, 1, 3, 1, 1)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(12)
        btn_cancel = Gtk.Button(label="Batal")
        btn_cancel.get_style_context().add_class("btn-secondary")
        btn_cancel.connect("clicked", lambda w: self.response(Gtk.ResponseType.CANCEL))
        btn_box.pack_end(btn_cancel, False, False, 0)

        btn_save = Gtk.Button(label="Proses Stok Keluar")
        btn_save.get_style_context().add_class("btn-outline")
        btn_save.connect("clicked", self._on_save)
        btn_box.pack_end(btn_save, False, False, 0)
        box.pack_start(btn_box, False, False, 0)

        self.show_all()

    def _on_save(self, widget):
        idx = self.combo_item.get_active()
        if idx < 0 or not self.item_info:
            self.parent_win.show_error("Peringatan", "Pilih barang yang tersedia di gudang.")
            return

        inv_id, cur_qty, item_name = self.item_info[idx]
        qty_str = self.entry_qty.get_text().strip().replace(",", ".")
        dest = self.entry_dest.get_text().strip()
        rev_str = self.entry_revenue.get_text().strip().replace(".", "").replace(",", ".")

        if not qty_str or not dest:
            self.parent_win.show_error("Peringatan", "Jumlah kg dan tujuan pengeluaran wajib diisi.")
            return

        try:
            qty_kg = float(qty_str)
            if qty_kg <= 0:
                raise ValueError()
        except ValueError:
            self.parent_win.show_error("Peringatan", "Jumlah keluar harus angka lebih besar dari 0.")
            return

        # REQ-APP10-002: Cannot exceed current available stock
        if qty_kg > cur_qty:
            self.parent_win.show_error(
                "Stok Kurang",
                f"Jumlah keluar ({qty_kg} Kg) melebihi saldo stok yang tersedia ({cur_qty} Kg)."
            )
            return

        today_s = datetime.date.today().strftime("%Y-%m-%d")

        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO storage_movements (storage_inventory_id, movement_type, quantity_kg, movement_date, destination_or_source, notes)
                    VALUES (?, 'Keluar', ?, ?, ?, ?)
                """, (inv_id, qty_kg, today_s, dest, f"Pengeluaran stok {item_name}"))

                # If revenue entered, record to finance_transactions
                if rev_str:
                    try:
                        rev = float(rev_str)
                        if rev > 0:
                            cursor.execute("""
                                INSERT INTO finance_transactions (transaction_date, category, transaction_type, description, amount_idr, source_module)
                                VALUES (?, 'Penjualan Panen', 'Pemasukan', ?, ?, 'Agri-Storage Manager')
                            """, (today_s, f"Penjualan {item_name} ({format_number(qty_kg, 'Kg')}) ke {dest}", rev))
                    except ValueError:
                        pass

            self.response(Gtk.ResponseType.OK)
        except Exception as e:
            self.parent_win.show_error("Gagal Menyimpan", f"Error:\n{e}")
        finally:
            conn.close()

def main():
    GLib.set_prgname("agri-storage-manager")
    GLib.set_application_name("Agri-Storage Manager")
    try:
        Gdk.set_program_class("agri-storage-manager")
    except Exception:
        pass
    app = StorageManagerApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
