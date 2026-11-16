#!/usr/bin/env python3
"""
Agri-Fertilizer Planner
Jadwal dan Catatan Pemupukan Nutrisi Tanaman
Sesuai UI/04_agri_fertilizer_planner.md & PRD 7.4
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
        PillTabs, format_rupiah, format_number, format_date_id, escape
    )
except ImportError:
    from common import (
        init_db, get_connection, AgriWindow, AgriHeader, KPICard,
        PillTabs, format_rupiah, format_number, format_date_id, escape
    )

class FertilizerPlannerApp(AgriWindow):
    def __init__(self):
        super().__init__(
            title="Agri-Fertilizer Planner - Jadwal & Catatan Pemupukan",
            icon_name="agri-fertilizer-planner",
            default_width=1100,
            default_height=740
        )
        init_db()

        self.current_filter = "Semua Catatan"
        self.search_text = ""

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        # 1. Header
        self.header = AgriHeader(
            title="Jadwal &amp; Catatan Pemupukan",
            subtitle="Manajemen Nutrisi Tanaman, Takaran Dosis &amp; Pengendalian Biaya Pupuk",
            action_label="+ Catat Pemupukan",
            action_callback=self._on_add_fertilizer_clicked,
            parent_window=self
        )
        main_box.pack_start(self.header, False, False, 0)

        # Scroller
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        content_box.set_margin_bottom(24)
        scroller.add(content_box)

        # 2. 3 KPI Cards
        kpi_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        content_box.pack_start(kpi_row, False, False, 0)

        self.kpi_biaya = KPICard("Total Biaya Pupuk", "Rp 0", "Akumulasi Pembelian", highlighted=True)
        self.kpi_jumlah = KPICard("Total Pupuk Digunakan", "0 Kg", "0 Karung", value_color="green")
        self.kpi_jadwal = KPICard("Jadwal Berikutnya", "-", "Belum ada jadwal")

        kpi_row.pack_start(self.kpi_biaya, True, True, 0)
        kpi_row.pack_start(self.kpi_jumlah, True, True, 0)
        kpi_row.pack_start(self.kpi_jadwal, True, True, 0)

        # 3. Filter Bar (Pill Tabs & Search)
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        content_box.pack_start(filter_box, False, False, 0)

        pill_options = ["Semua Catatan", "Jadwal Mendatang", "Sudah Selesai"]
        self.tabs = PillTabs(pill_options, self._on_filter_changed)
        filter_box.pack_start(self.tabs, False, False, 0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Cari pupuk, blok, atau metode...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        filter_box.pack_start(self.search_entry, True, True, 0)

        btn_finish_selected = Gtk.Button(label="✓ Tandai Selesai")
        btn_finish_selected.get_style_context().add_class("btn-outline")
        btn_finish_selected.connect("clicked", self._on_mark_selected_done)
        filter_box.pack_end(btn_finish_selected, False, False, 0)

        # 4. Table Container
        table_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        table_card.get_style_context().add_class("agri-card")
        content_box.pack_start(table_card, True, True, 0)

        # TreeStore: id, date, plot_name, fert_name, qty, method, cost, status
        self.store = Gtk.ListStore(int, str, str, str, str, str, str, str)
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.set_rules_hint(True)

        cols = [
            ("ID", 0, 50, 0.0),
            ("Tanggal", 1, 120, 0.0),
            ("Lokasi Lahan / Blok", 2, 200, 0.0),
            ("Jenis Pupuk", 3, 160, 0.0),
            ("Jumlah / Dosis", 4, 120, 1.0),
            ("Cara Pemberian", 5, 140, 0.5),
            ("Biaya Pupuk", 6, 150, 1.0),
            ("Status", 7, 120, 0.5)
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

        # Update KPIs
        cursor.execute("SELECT COALESCE(SUM(cost_idr), 0), COALESCE(SUM(quantity_kg), 0) FROM fertilizer_logs WHERE status = 'Selesai'")
        row = cursor.fetchone()
        tot_cost, tot_kg = row[0], row[1]
        karung = int(round(tot_kg / 50.0))
        self.kpi_biaya.update(format_rupiah(tot_cost), "Realisasi Biaya Musim Ini")
        self.kpi_jumlah.update(f"{format_number(tot_kg, 'Kg')}", f"± {karung} Karung (50 Kg)")

        today_str = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT f.application_date, p.plot_code, f.fertilizer_name
            FROM fertilizer_logs f
            JOIN plots p ON f.plot_id = p.id
            WHERE f.status = 'Terjadwal' AND f.application_date >= ?
            ORDER BY f.application_date ASC
            LIMIT 1
        """, (today_str,))
        next_f = cursor.fetchone()
        if next_f:
            self.kpi_jadwal.update(format_date_id(next_f[0]), f"{next_f[1]} • {next_f[2]}")
        else:
            self.kpi_jadwal.update("Tidak Ada", "Semua jadwal telah selesai")

        # Table data
        self.store.clear()
        query = """
            SELECT f.id, f.application_date, p.plot_code || ' - ' || p.plot_name,
                   f.fertilizer_name, f.quantity_kg, f.method, f.cost_idr, f.status
            FROM fertilizer_logs f
            JOIN plots p ON f.plot_id = p.id
            ORDER BY f.application_date DESC, f.id DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        for r in rows:
            f_id, app_date, plot_str, f_name, qty, method, cost, status = r
            if self.current_filter == "Jadwal Mendatang" and status != "Terjadwal":
                continue
            if self.current_filter == "Sudah Selesai" and status != "Selesai":
                continue

            # Search text filter
            if self.search_text:
                searchable = f"{plot_str} {f_name} {method} {status} {app_date}".lower()
                if self.search_text not in searchable:
                    continue

            self.store.append([
                f_id,
                format_date_id(app_date),
                plot_str,
                f_name,
                format_number(qty, "Kg"),
                method,
                format_rupiah(cost),
                f"✓ {status}" if status == "Selesai" else f"⏳ {status}"
            ])

        conn.close()

    def _on_mark_selected_done(self, widget):
        selection = self.tree.get_selection()
        model, treeiter = selection.get_selected()
        if not treeiter:
            self.show_error("Peringatan", "Pilih salah satu baris jadwal pemupukan yang ingin ditandai selesai.")
            return

        f_id = model[treeiter][0]
        f_status = model[treeiter][7]

        if "Selesai" in f_status:
            self.show_info("Informasi", "Jadwal pemupukan ini sudah berstatus Selesai.")
            return

        conn = get_connection()
        with conn:
            conn.execute("UPDATE fertilizer_logs SET status = 'Selesai' WHERE id = ?", (f_id,))
        conn.close()

        self.show_info("Sukses", "Jadwal berhasil ditandai Selesai dan transaksi otomatis dicatat ke Buku Kas.")
        self.refresh_data()

    def _on_add_fertilizer_clicked(self, widget):
        dialog = AddFertilizerDialog(self)
        dialog.run()
        dialog.destroy()
        self.refresh_data()

class AddFertilizerDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Catat Kegiatan Pemupukan", transient_for=parent, flags=0)
        self.set_default_size(480, 460)
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

        # Plot & Crop
        grid.attach(Gtk.Label(label="Lokasi Blok & Tanaman:", xalign=0), 0, 0, 1, 1)
        self.combo_crop = Gtk.ComboBoxText()
        self.crop_plot_pairs = []

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.plot_id, p.plot_code, p.plot_name, c.crop_type, c.variety, c.status
            FROM crops c
            JOIN plots p ON c.plot_id = p.id
            WHERE c.status IN ('Sedang Tumbuh', 'Panen Sebagian')
            ORDER BY p.plot_code ASC
        """)
        crops_list = cursor.fetchall()
        if not crops_list:
            cursor.execute("""
                SELECT c.id, c.plot_id, p.plot_code, p.plot_name, c.crop_type, c.variety, c.status
                FROM crops c
                JOIN plots p ON c.plot_id = p.id
                ORDER BY c.id DESC
            """)
            crops_list = cursor.fetchall()

        for c_id, p_id, p_code, p_name, c_type, c_var, c_stat in crops_list:
            self.combo_crop.append_text(f"{p_code} - {p_name} ({c_type} {c_var}) [{c_stat}]")
            self.crop_plot_pairs.append((c_id, p_id))
        conn.close()
        if self.crop_plot_pairs:
            self.combo_crop.set_active(0)
        grid.attach(self.combo_crop, 1, 0, 1, 1)

        # Date
        grid.attach(Gtk.Label(label="Tanggal Aplikasi (YYYY-MM-DD):", xalign=0), 0, 1, 1, 1)
        self.entry_date = Gtk.Entry()
        self.entry_date.set_text(datetime.date.today().strftime("%Y-%m-%d"))
        grid.attach(self.entry_date, 1, 1, 1, 1)

        # Fertilizer Name
        grid.attach(Gtk.Label(label="Jenis / Merek Pupuk:", xalign=0), 0, 2, 1, 1)
        self.combo_name = Gtk.ComboBoxText()
        for f in ["Urea Pusri", "NPK Phonska 15-15-15", "NPK Mutiara 16-16-16", "SP-36", "Pupuk Organik Kandang", "Gandasil B (Daun)"]:
            self.combo_name.append_text(f)
        self.combo_name.set_active(0)
        grid.attach(self.combo_name, 1, 2, 1, 1)

        # Quantity Kg
        grid.attach(Gtk.Label(label="Dosis / Jumlah (Kg):", xalign=0), 0, 3, 1, 1)
        self.entry_qty = Gtk.Entry()
        self.entry_qty.set_text("50.0")
        grid.attach(self.entry_qty, 1, 3, 1, 1)

        # Method: Tabur, Kocor, Semprot Daun
        grid.attach(Gtk.Label(label="Metode Aplikasi:", xalign=0), 0, 4, 1, 1)
        self.combo_method = Gtk.ComboBoxText()
        for m in ["Tabur", "Kocor", "Semprot Daun"]:
            self.combo_method.append_text(m)
        self.combo_method.set_active(0)
        grid.attach(self.combo_method, 1, 4, 1, 1)

        # Cost Rupiah
        grid.attach(Gtk.Label(label="Total Biaya Pupuk (Rp):", xalign=0), 0, 5, 1, 1)
        self.entry_cost = Gtk.Entry()
        self.entry_cost.set_text("325000")
        grid.attach(self.entry_cost, 1, 5, 1, 1)

        # Status: Terjadwal / Selesai
        grid.attach(Gtk.Label(label="Status Pelaksanaan:", xalign=0), 0, 6, 1, 1)
        self.combo_status = Gtk.ComboBoxText()
        self.combo_status.append_text("Selesai")
        self.combo_status.append_text("Terjadwal")
        self.combo_status.set_active(0)
        grid.attach(self.combo_status, 1, 6, 1, 1)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(12)
        btn_cancel = Gtk.Button(label="Batal")
        btn_cancel.get_style_context().add_class("btn-secondary")
        btn_cancel.connect("clicked", lambda w: self.response(Gtk.ResponseType.CANCEL))
        btn_box.pack_end(btn_cancel, False, False, 0)

        btn_save = Gtk.Button(label="Simpan Catatan")
        btn_save.get_style_context().add_class("btn-primary")
        btn_save.connect("clicked", self._on_save)
        btn_box.pack_end(btn_save, False, False, 0)
        box.pack_start(btn_box, False, False, 0)

        self.show_all()

    def _on_save(self, widget):
        idx = self.combo_crop.get_active()
        if idx < 0 or not self.crop_plot_pairs:
            self.parent_win.show_error("Peringatan", "Pilih blok lahan dan tanaman aktif.")
            return

        c_id, p_id = self.crop_plot_pairs[idx]
        app_date = self.entry_date.get_text().strip()
        fert_name = self.combo_name.get_active_text()
        qty_str = self.entry_qty.get_text().strip().replace(",", ".")
        method = self.combo_method.get_active_text()
        cost_str = self.entry_cost.get_text().strip().replace(".", "").replace(",", ".")
        status = self.combo_status.get_active_text()

        try:
            qty = float(qty_str)
            if qty <= 0:
                raise ValueError()
        except ValueError:
            self.parent_win.show_error("Peringatan", "Dosis pupuk harus berupa angka desimal lebih besar dari 0.")
            return

        try:
            cost = float(cost_str)
            if cost < 0:
                raise ValueError()
        except ValueError:
            self.parent_win.show_error("Peringatan", "Biaya pupuk harus berupa angka positif atau 0.")
            return

        try:
            datetime.date.fromisoformat(app_date)
        except ValueError:
            self.parent_win.show_error("Peringatan", "Format tanggal harus YYYY-MM-DD.")
            return

        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO fertilizer_logs (plot_id, crop_id, application_date, fertilizer_name, quantity_kg, method, cost_idr, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (p_id, c_id, app_date, fert_name, qty, method, cost, status))
            self.response(Gtk.ResponseType.OK)
        except Exception as e:
            self.parent_win.show_error("Gagal Menyimpan", f"Terjadi kesalahan saat menyimpan ke database:\n{e}")
        finally:
            conn.close()

def main():
    GLib.set_prgname("agri-fertilizer-planner")
    GLib.set_application_name("Agri-Fertilizer Planner")
    try:
        Gdk.set_program_class("agri-fertilizer-planner")
    except Exception:
        pass
    app = FertilizerPlannerApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
