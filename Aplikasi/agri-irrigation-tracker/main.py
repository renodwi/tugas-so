#!/usr/bin/env python3
"""
Agri-Irrigation Tracker
Catatan Operasional Pompa dan Pasokan Air Lahan
Sesuai UI/06_agri_irrigation_tracker.md & PRD 7.6
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
        format_number, format_date_id, escape
    )
except ImportError:
    from common import (
        init_db, get_connection, AgriWindow, AgriHeader, KPICard,
        format_number, format_date_id, escape
    )

class IrrigationTrackerApp(AgriWindow):
    def __init__(self):
        super().__init__(
            title="Agri-Irrigation Tracker - Catatan Pengairan Lahan",
            icon_name="agri-irrigation-tracker",
            default_width=1100,
            default_height=740
        )
        init_db()

        self.selected_plot_id = None
        self.search_text = ""

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        # 1. Header
        self.header = AgriHeader(
            title="Catatan Pengairan Lahan",
            subtitle="Pemantauan Pasokan Air, Jam Kerja Pompa &amp; Efisiensi Bahan Bakar",
            action_label="+ Catat Pengairan",
            action_callback=self._on_add_irrigation_clicked,
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

        self.kpi_durasi = KPICard("Total Durasi Pengairan", "0 Jam", "Akumulasi Pompa", highlighted=True)
        self.kpi_bbm = KPICard("Penggunaan Bahan Bakar", "0 Liter", "Total Konsumsi Solar", value_color="green")
        self.kpi_terakhir = KPICard("Pengairan Terakhir", "-", "Belum ada catatan")

        kpi_row.pack_start(self.kpi_durasi, True, True, 0)
        kpi_row.pack_start(self.kpi_bbm, True, True, 0)
        kpi_row.pack_start(self.kpi_terakhir, True, True, 0)

        # 3. Filter Bar (Filter by Plot Dropdown)
        filter_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        content_box.pack_start(filter_bar, False, False, 0)

        lbl_f = Gtk.Label(label="Filter Berdasarkan Blok Lahan:")
        lbl_f.get_style_context().add_class("kpi-title")
        filter_bar.pack_start(lbl_f, False, False, 0)

        self.combo_filter_plot = Gtk.ComboBoxText()
        self.combo_filter_plot.append_text("Semua Blok Lahan")
        self.filter_plot_ids = [None]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, plot_code, plot_name FROM plots ORDER BY plot_code ASC")
        for p_id, p_code, p_name in cursor.fetchall():
            self.combo_filter_plot.append_text(f"{p_code} - {p_name}")
            self.filter_plot_ids.append(p_id)
        conn.close()

        self.combo_filter_plot.set_active(0)
        self.combo_filter_plot.connect("changed", self._on_plot_filter_changed)
        filter_bar.pack_start(self.combo_filter_plot, False, False, 0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Cari riwayat / pompa / sumber air...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        filter_bar.pack_end(self.search_entry, True, True, 0)

        # 4. Table Container
        table_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        table_card.get_style_context().add_class("agri-card")
        content_box.pack_start(table_card, True, True, 0)

        # TreeStore: id, datetime, plot_name, water_source, pump_type, duration_str, fuel_str
        self.store = Gtk.ListStore(int, str, str, str, str, str, str)
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.set_rules_hint(True)

        cols = [
            ("ID", 0, 50, 0.0),
            ("Tanggal & Waktu", 1, 140, 0.0),
            ("Lokasi Lahan", 2, 220, 0.0),
            ("Sumber Air", 3, 140, 0.5),
            ("Jenis Pompa", 4, 180, 0.0),
            ("Lama Pengairan", 5, 140, 1.0),
            ("Pemakaian BBM", 6, 130, 1.0)
        ]

        for title, col_idx, width, align in cols:
            renderer = Gtk.CellRendererText()
            renderer.set_alignment(align, 0.5)
            col = Gtk.TreeViewColumn(title, renderer, text=col_idx)
            col.set_min_width(width)
            col.set_resizable(True)
            self.tree.append_column(col)

        table_scroller = Gtk.ScrolledWindow()
        table_scroller.set_min_content_height(380)
        table_scroller.add(self.tree)
        table_card.pack_start(table_scroller, True, True, 0)

        self.refresh_data()

    def _on_plot_filter_changed(self, combo):
        idx = combo.get_active()
        self.selected_plot_id = self.filter_plot_ids[idx] if idx >= 0 else None
        self.refresh_data()

    def _on_search_changed(self, entry):
        self.search_text = entry.get_text().strip().lower()
        self.refresh_data()

    def refresh_data(self):
        conn = get_connection()
        cursor = conn.cursor()

        # Update KPIs
        cursor.execute("SELECT COALESCE(SUM(duration_minutes), 0), COALESCE(SUM(fuel_liters), 0) FROM irrigation_logs")
        row = cursor.fetchone()
        tot_min, tot_fuel = row[0], row[1]
        hours = tot_min // 60
        mins = tot_min % 60
        self.kpi_durasi.update(f"{hours} Jam {mins} Menit", "Total Operasional Pompa")
        self.kpi_bbm.update(format_number(tot_fuel, "Liter Solar"), "Konsumsi Mesin Diesel")

        cursor.execute("""
            SELECT i.irrigation_date, p.plot_code
            FROM irrigation_logs i
            JOIN plots p ON i.plot_id = p.id
            ORDER BY i.irrigation_date DESC
            LIMIT 1
        """)
        last_irr = cursor.fetchone()
        if last_irr:
            self.kpi_terakhir.update(last_irr[1], last_irr[0])
        else:
            self.kpi_terakhir.update("-", "Belum ada riwayat")

        # Table data
        self.store.clear()
        query = """
            SELECT i.id, i.irrigation_date, p.plot_code || ' - ' || p.plot_name,
                   i.water_source, i.pump_type, i.duration_minutes, i.fuel_liters
            FROM irrigation_logs i
            JOIN plots p ON i.plot_id = p.id
        """
        params = []
        if self.selected_plot_id:
            query += " WHERE i.plot_id = ?"
            params.append(self.selected_plot_id)

        query += " ORDER BY i.irrigation_date DESC, i.id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        for r in rows:
            i_id, i_dt, p_name, w_src, p_type, dur_min, fuel = r
            h = dur_min // 60
            m = dur_min % 60
            dur_str = f"{h} Jam {m} Menit" if h > 0 else f"{m} Menit"
            fuel_str = format_number(fuel, "Liter") if fuel > 0 else "-"

            # Search text filter
            if self.search_text:
                searchable = f"{p_name} {w_src} {p_type} {dur_str} {i_dt}".lower()
                if self.search_text not in searchable:
                    continue

            self.store.append([
                i_id,
                i_dt,
                p_name,
                w_src,
                p_type,
                dur_str,
                fuel_str
            ])

        conn.close()

    def _on_add_irrigation_clicked(self, widget):
        dialog = AddIrrigationDialog(self)
        dialog.run()
        dialog.destroy()
        self.refresh_data()

class AddIrrigationDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Catat Kegiatan Pengairan Lahan", transient_for=parent, flags=0)
        self.set_default_size(500, 480)
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

        # Plot
        grid.attach(Gtk.Label(label="Blok Lahan Sawah:", xalign=0), 0, 0, 1, 1)
        self.combo_plot = Gtk.ComboBoxText()
        self.plot_ids = []
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, plot_code, plot_name FROM plots WHERE status != 'Nonaktif' ORDER BY plot_code ASC")
        for p_id, p_code, p_name in cursor.fetchall():
            self.combo_plot.append_text(f"{p_code} - {p_name}")
            self.plot_ids.append(p_id)
        if self.plot_ids:
            self.combo_plot.set_active(0)
        grid.attach(self.combo_plot, 1, 0, 1, 1)

        # Equipment (Pump)
        grid.attach(Gtk.Label(label="Mesin Pompa Terpasang:", xalign=0), 0, 1, 1, 1)
        self.combo_eq = Gtk.ComboBoxText()
        self.combo_eq.append_text("Gravitasi / Tanpa Pompa")
        self.eq_ids = [None]
        cursor.execute("SELECT id, equipment_code, name FROM equipment WHERE category = 'Pompa Air'")
        for eq_id, eq_code, eq_name in cursor.fetchall():
            self.combo_eq.append_text(f"{eq_code} - {eq_name}")
            self.eq_ids.append(eq_id)
        conn.close()
        self.combo_eq.set_active(0)
        self.combo_eq.connect("changed", self._on_pump_changed)
        grid.attach(self.combo_eq, 1, 1, 1, 1)

        # Date & Time
        grid.attach(Gtk.Label(label="Waktu Mulai (YYYY-MM-DD HH:MM):", xalign=0), 0, 2, 1, 1)
        self.entry_datetime = Gtk.Entry()
        self.entry_datetime.set_text(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        grid.attach(self.entry_datetime, 1, 2, 1, 1)

        # Duration Minutes
        grid.attach(Gtk.Label(label="Durasi Pengairan (Menit):", xalign=0), 0, 3, 1, 1)
        self.entry_duration = Gtk.Entry()
        self.entry_duration.set_text("180")
        grid.attach(self.entry_duration, 1, 3, 1, 1)

        # Water Source
        grid.attach(Gtk.Label(label="Sumber Air:", xalign=0), 0, 4, 1, 1)
        self.combo_source = Gtk.ComboBoxText()
        for s in ["Irigasi Teknis", "Sumur Bor", "Sungai", "Embung"]:
            self.combo_source.append_text(s)
        self.combo_source.set_active(0)
        self.combo_source.connect("changed", self._on_source_changed)
        grid.attach(self.combo_source, 1, 4, 1, 1)

        # Fuel Liters
        grid.attach(Gtk.Label(label="Bahan Bakar Solar (Liter):", xalign=0), 0, 5, 1, 1)
        self.entry_fuel = Gtk.Entry()
        self.entry_fuel.set_text("4.0")
        grid.attach(self.entry_fuel, 1, 5, 1, 1)

        # Fuel Cost IDR
        grid.attach(Gtk.Label(label="Biaya Solar (Rp, Catat ke Kas):", xalign=0), 0, 6, 1, 1)
        self.entry_fuel_cost = Gtk.Entry()
        self.entry_fuel_cost.set_placeholder_text("Opsional. Contoh: 60000")
        grid.attach(self.entry_fuel_cost, 1, 6, 1, 1)

        # Notes
        grid.attach(Gtk.Label(label="Catatan Debit / Kondisi:", xalign=0), 0, 7, 1, 1)
        self.entry_notes = Gtk.Entry()
        self.entry_notes.set_placeholder_text("Debit air lancar, saluran sekunder normal")
        grid.attach(self.entry_notes, 1, 7, 1, 1)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(12)
        btn_cancel = Gtk.Button(label="Batal")
        btn_cancel.get_style_context().add_class("btn-secondary")
        btn_cancel.connect("clicked", lambda w: self.response(Gtk.ResponseType.CANCEL))
        btn_box.pack_end(btn_cancel, False, False, 0)

        btn_save = Gtk.Button(label="Simpan Pengairan")
        btn_save.get_style_context().add_class("btn-primary")
        btn_save.connect("clicked", self._on_save)
        btn_box.pack_end(btn_save, False, False, 0)
        box.pack_start(btn_box, False, False, 0)

        self.show_all()

    def _on_source_changed(self, combo):
        # REQ-APP06-001: If gravity chosen, fuel is automatically 0
        if combo.get_active_text() == "Gravitasi":
            self.entry_fuel.set_text("0.0")
            self.entry_fuel.set_sensitive(False)
        else:
            self.entry_fuel.set_sensitive(True)

    def _on_pump_changed(self, combo):
        txt = combo.get_active_text()
        if "Gravitasi" in txt or "Listrik" in txt:
            self.entry_fuel.set_text("0.0")
            self.entry_fuel.set_sensitive(False)
        else:
            self.entry_fuel.set_sensitive(True)

    def _on_save(self, widget):
        p_idx = self.combo_plot.get_active()
        if p_idx < 0 or not self.plot_ids:
            self.parent_win.show_error("Peringatan", "Pilih blok lahan.")
            return

        plot_id = self.plot_ids[p_idx]
        eq_idx = self.combo_eq.get_active()
        eq_id = self.eq_ids[eq_idx] if eq_idx >= 0 else None
        pump_type = self.combo_eq.get_active_text()

        dt_str = self.entry_datetime.get_text().strip()
        dur_str = self.entry_duration.get_text().strip()
        source = self.combo_source.get_active_text()
        fuel_str = self.entry_fuel.get_text().strip().replace(",", ".")
        notes = self.entry_notes.get_text().strip()

        try:
            dur = int(dur_str)
            if dur <= 0:
                raise ValueError()
        except ValueError:
            self.parent_win.show_error("Peringatan", "Durasi pengairan wajib bernilai minimal 1 menit.")
            return

        try:
            fuel = float(fuel_str) if fuel_str else 0.0
            if fuel < 0:
                raise ValueError()
        except ValueError:
            self.parent_win.show_error("Peringatan", "Volume bahan bakar tidak boleh bernilai negatif.")
            return

        cost_str = self.entry_fuel_cost.get_text().strip().replace(".", "").replace(",", ".")

        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO irrigation_logs (plot_id, equipment_id, irrigation_date, duration_minutes, water_source, pump_type, fuel_liters, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (plot_id, eq_id, dt_str, dur, source, pump_type, fuel, notes))
                irr_id = cursor.lastrowid

                # If fuel cost provided, auto-record into finance ledger
                if cost_str:
                    try:
                        fuel_cost = float(cost_str)
                        if fuel_cost > 0:
                            cursor.execute("""
                                INSERT INTO finance_transactions (transaction_date, category, transaction_type, description, amount_idr, source_module, ref_id)
                                VALUES (?, 'BBM & Perawatan', 'Pengeluaran', ?, ?, 'Agri-Irrigation Tracker', ?)
                            """, (dt_str[:10], f"Biaya Bahan Bakar Pompa Irigasi ({source})", fuel_cost, irr_id))
                    except ValueError:
                        pass
            self.response(Gtk.ResponseType.OK)
        except Exception as e:
            self.parent_win.show_error("Gagal Menyimpan", f"Terjadi kesalahan saat menyimpan data:\n{e}")
        finally:
            conn.close()

def main():
    GLib.set_prgname("agri-irrigation-tracker")
    GLib.set_application_name("Agri-Irrigation Tracker")
    try:
        Gdk.set_program_class("agri-irrigation-tracker")
    except Exception:
        pass
    app = IrrigationTrackerApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
