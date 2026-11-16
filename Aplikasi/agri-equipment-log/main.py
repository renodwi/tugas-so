#!/usr/bin/env python3
"""
Agri-Equipment Log
Katalog dan Kondisi Alat dan Mesin Pertanian (Alsintan)
Sesuai UI/08_agri_equipment_log.md & PRD 7.8
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

class EquipmentLogApp(AgriWindow):
    def __init__(self):
        super().__init__(
            title="Agri-Equipment Log - Katalog & Kondisi Alsintan",
            icon_name="agri-equipment-log",
            default_width=1120,
            default_height=750
        )
        init_db()

        self.current_filter = "Semua Unit"
        self.search_text = ""

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        # 1. Header
        self.header = AgriHeader(
            title="Katalog &amp; Kondisi Alsintan",
            subtitle="Inventaris Alat Mesin Pertanian, Pelacakan Jam Kerja &amp; Jadwal Servis Rutin",
            action_label="+ Tambah Alsintan",
            action_callback=self._on_add_equipment_clicked,
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

        self.kpi_total = KPICard("Total Unit Alsintan", "0 Unit", "Seluruh Aset Mesin", highlighted=True)
        self.kpi_siap = KPICard("Kondisi Siap Pakai", "0 Unit", "Normal Operasional", value_color="green")
        self.kpi_servis = KPICard("Perlu Perawatan / Servis", "0 Unit", "Ganti Oli / Perbaikan", value_color="red")

        kpi_row.pack_start(self.kpi_total, True, True, 0)
        kpi_row.pack_start(self.kpi_siap, True, True, 0)
        kpi_row.pack_start(self.kpi_servis, True, True, 0)

        # 3. Filter Bar (Pill Tabs & Search)
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        content_box.pack_start(filter_box, False, False, 0)

        pill_options = ["Semua Unit", "Siap Pakai", "Perlu Servis", "Sedang Diperbaiki"]
        self.tabs = PillTabs(pill_options, self._on_filter_changed)
        filter_box.pack_start(self.tabs, False, False, 0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Cari nama alsintan, kode, atau kategori...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        filter_box.pack_start(self.search_entry, True, True, 0)

        # 4. Grid FlowBox 3 Columns
        self.flow = Gtk.FlowBox()
        self.flow.set_valign(Gtk.Align.START)
        self.flow.set_max_children_per_line(3)
        self.flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flow.set_column_spacing(16)
        self.flow.set_row_spacing(16)
        content_box.pack_start(self.flow, True, True, 0)

        self.refresh_data()

    def _on_filter_changed(self, option):
        self.current_filter = option
        self.refresh_data()

    def _on_search_changed(self, entry):
        self.search_text = entry.get_text().strip().lower()
        self.refresh_data()

    def _on_quick_change_status(self, widget, eq_id, cur_status):
        dialog = Gtk.Dialog(title="Ubah Status Alsintan", transient_for=self, flags=0)
        dialog.set_default_size(320, 160)
        box = dialog.get_content_area()
        box.set_spacing(10)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_margin_top(16)
        box.set_margin_bottom(16)

        lbl = Gtk.Label(label="Pilih Status Operasional Mesin:", xalign=0)
        box.pack_start(lbl, False, False, 0)
        combo = Gtk.ComboBoxText()
        statuses = ["Siap Pakai", "Perlu Servis", "Sedang Diperbaiki"]
        for s in statuses:
            combo.append_text(s)
        if cur_status in statuses:
            combo.set_active(statuses.index(cur_status))
        else:
            combo.set_active(0)
        box.pack_start(combo, False, False, 0)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_box.set_margin_top(8)
        btn_cancel = Gtk.Button(label="Batal")
        btn_cancel.get_style_context().add_class("btn-secondary")
        btn_cancel.connect("clicked", lambda w: dialog.response(Gtk.ResponseType.CANCEL))
        btn_box.pack_end(btn_cancel, False, False, 0)

        btn_ok = Gtk.Button(label="Simpan")
        btn_ok.get_style_context().add_class("btn-primary")
        def _save_st(w):
            new_s = combo.get_active_text()
            conn = get_connection()
            with conn:
                conn.execute("UPDATE equipment SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_s, eq_id))
            conn.close()
            dialog.response(Gtk.ResponseType.OK)
        btn_ok.connect("clicked", _save_st)
        btn_box.pack_end(btn_ok, False, False, 0)
        box.pack_start(btn_box, False, False, 0)

        dialog.show_all()
        dialog.run()
        dialog.destroy()
        self.refresh_data()

    def refresh_data(self):
        conn = get_connection()
        cursor = conn.cursor()

        # Update KPIs
        cursor.execute("SELECT COUNT(*) FROM equipment")
        tot = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM equipment WHERE status = 'Siap Pakai'")
        siap = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM equipment WHERE status IN ('Perlu Servis', 'Sedang Diperbaiki')")
        servis = cursor.fetchone()[0]

        self.kpi_total.update(f"{tot} Unit", "Inventaris Mesin Terdata")
        self.kpi_siap.update(f"{siap} Unit", "Kondisi Prima Siap Operasi")
        self.kpi_servis.update(f"{servis} Unit", "Mendekati / Lewat Jam Servis")

        # Clear grid
        for child in self.flow.get_children():
            self.flow.remove(child)

        query = """
            SELECT id, equipment_code, name, category, status, total_hours, next_service_hours, last_used_date
            FROM equipment
            ORDER BY equipment_code ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        for r in rows:
            eq_id, code, name, cat, status, hours, next_hrs, last_d = r

            if self.current_filter != "Semua Unit" and status != self.current_filter:
                continue

            if self.search_text:
                searchable = f"{code} {name} {cat} {status}".lower()
                if self.search_text not in searchable:
                    continue

            card = self._create_equipment_card(eq_id, code, name, cat, status, hours, next_hrs, last_d)
            self.flow.add(card)

        conn.close()
        self.flow.show_all()

    def _create_equipment_card(self, eq_id, code, name, cat, status, hours, next_hrs, last_d):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        card.get_style_context().add_class("agri-card")
        card.set_size_request(320, -1)

        # Header: Name, Code & Badge
        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        lbl_code = Gtk.Label(xalign=0)
        lbl_code.set_markup(f"<span size='small' weight='bold' color='#64748B'>{escape(code)} • {escape(cat)}</span>")
        title_box.pack_start(lbl_code, False, False, 0)

        lbl_name = Gtk.Label(xalign=0)
        lbl_name.set_markup(f"<span weight='bold' color='#1E293B'>{escape(name)}</span>")
        title_box.pack_start(lbl_name, False, False, 0)
        h_box.pack_start(title_box, True, True, 0)

        badge = Gtk.Label()
        badge.get_style_context().add_class("badge")
        if status == "Siap Pakai":
            badge.get_style_context().add_class("badge-success")
        elif status == "Perlu Servis":
            badge.get_style_context().add_class("badge-warning")
        else:
            badge.get_style_context().add_class("badge-danger")
        badge.set_text(status)
        h_box.pack_end(badge, False, False, 0)
        card.pack_start(h_box, False, False, 0)

        card.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 2)

        # Metrics: Total hours & last used
        metrics_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        lbl_hrs = Gtk.Label(xalign=0)
        lbl_hrs.set_markup(f"Total Operasi: <span size='large' weight='bold' color='#2E7D32'>{format_number(hours, 'Jam Kerja')}</span>")
        metrics_box.pack_start(lbl_hrs, False, False, 0)

        last_str = format_date_id(last_d) if last_d else "Belum tercatat"
        lbl_last = Gtk.Label(xalign=0)
        lbl_last.set_markup(f"<span size='small' color='#64748B'>Terakhir Dipakai: {last_str}</span>")
        metrics_box.pack_start(lbl_last, False, False, 0)
        card.pack_start(metrics_box, False, False, 0)

        # Service notice box
        rem_hrs = next_hrs - hours
        srv_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        srv_box.get_style_context().add_class("badge")
        if rem_hrs <= 0:
            srv_box.get_style_context().add_class("badge-danger")
            lbl_srv = Gtk.Label(label=f"⚠️ Jadwal Servis Terlewat! Segera ganti oli")
        elif rem_hrs <= 15:
            srv_box.get_style_context().add_class("badge-warning")
            lbl_srv = Gtk.Label(label=f"⏳ Servis Rutin: {format_number(rem_hrs, 'Jam')} lagi")
        else:
            srv_box.get_style_context().add_class("badge-neutral")
            lbl_srv = Gtk.Label(label=f"Jadwal Servis: {format_number(rem_hrs, 'Jam')} lagi ({format_number(next_hrs, 'Jam')})")
        srv_box.pack_start(lbl_srv, False, False, 4)
        card.pack_start(srv_box, False, False, 2)

        # Action Buttons: + Catat Pakai, Log Servis, and Ubah Status
        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        actions.set_margin_top(6)

        btn_usage = Gtk.Button(label="+ Pakai")
        btn_usage.get_style_context().add_class("btn-secondary")
        btn_usage.connect("clicked", self._on_log_usage, eq_id, name)
        actions.pack_start(btn_usage, True, True, 0)

        btn_service = Gtk.Button(label="Servis")
        btn_service.get_style_context().add_class("btn-outline")
        btn_service.connect("clicked", self._on_log_service, eq_id, name, hours)
        actions.pack_start(btn_service, True, True, 0)

        btn_status = Gtk.Button(label="⚙ Status")
        btn_status.get_style_context().add_class("btn-secondary")
        btn_status.connect("clicked", self._on_quick_change_status, eq_id, status)
        actions.pack_start(btn_status, True, True, 0)

        card.pack_start(actions, False, False, 0)
        return card

    def _on_log_usage(self, widget, eq_id, eq_name):
        dialog = LogUsageDialog(self, eq_id, eq_name)
        dialog.run()
        dialog.destroy()
        self.refresh_data()

    def _on_log_service(self, widget, eq_id, eq_name, cur_hours):
        dialog = LogServiceDialog(self, eq_id, eq_name, cur_hours)
        dialog.run()
        dialog.destroy()
        self.refresh_data()

    def _on_add_equipment_clicked(self, widget):
        dialog = AddEquipmentDialog(self)
        dialog.run()
        dialog.destroy()
        self.refresh_data()

class LogUsageDialog(Gtk.Dialog):
    def __init__(self, parent, eq_id, eq_name):
        super().__init__(title=f"Catat Pemakaian - {eq_name}", transient_for=parent, flags=0)
        self.set_default_size(460, 360)
        self.parent_win = parent
        self.eq_id = eq_id

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

        grid.attach(Gtk.Label(label="Blok Lahan Kerja:", xalign=0), 0, 0, 1, 1)
        self.combo_plot = Gtk.ComboBoxText()
        self.plot_ids = []
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, plot_code, plot_name FROM plots")
        for p_id, p_code, p_name in cursor.fetchall():
            self.combo_plot.append_text(f"{p_code} - {p_name}")
            self.plot_ids.append(p_id)
        conn.close()
        if self.plot_ids:
            self.combo_plot.set_active(0)
        grid.attach(self.combo_plot, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Tanggal Pemakaian:", xalign=0), 0, 1, 1, 1)
        self.entry_date = Gtk.Entry()
        self.entry_date.set_text(datetime.date.today().strftime("%Y-%m-%d"))
        grid.attach(self.entry_date, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label="Lama Pemakaian (Jam):", xalign=0), 0, 2, 1, 1)
        self.entry_hours = Gtk.Entry()
        self.entry_hours.set_text("4.5")
        grid.attach(self.entry_hours, 1, 2, 1, 1)

        grid.attach(Gtk.Label(label="Nama Operator Mesin:", xalign=0), 0, 3, 1, 1)
        self.entry_op = Gtk.Entry()
        self.entry_op.set_placeholder_text("Contoh: Bpk. Slamet")
        grid.attach(self.entry_op, 1, 3, 1, 1)

        grid.attach(Gtk.Label(label="Uraian Aktivitas:", xalign=0), 0, 4, 1, 1)
        self.entry_act = Gtk.Entry()
        self.entry_act.set_placeholder_text("Contoh: Olah tanah dan bajak singkal")
        grid.attach(self.entry_act, 1, 4, 1, 1)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(12)
        btn_cancel = Gtk.Button(label="Batal")
        btn_cancel.get_style_context().add_class("btn-secondary")
        btn_cancel.connect("clicked", lambda w: self.response(Gtk.ResponseType.CANCEL))
        btn_box.pack_end(btn_cancel, False, False, 0)

        btn_save = Gtk.Button(label="Simpan Pemakaian")
        btn_save.get_style_context().add_class("btn-primary")
        btn_save.connect("clicked", self._on_save)
        btn_box.pack_end(btn_save, False, False, 0)
        box.pack_start(btn_box, False, False, 0)

        self.show_all()

    def _on_save(self, widget):
        p_idx = self.combo_plot.get_active()
        plot_id = self.plot_ids[p_idx] if p_idx >= 0 and self.plot_ids else 1
        dt = self.entry_date.get_text().strip()
        h_str = self.entry_hours.get_text().strip().replace(",", ".")
        op = self.entry_op.get_text().strip()
        act = self.entry_act.get_text().strip()

        if not op or not act:
            self.parent_win.show_error("Peringatan", "Nama operator dan aktivitas wajib diisi.")
            return

        try:
            hrs = float(h_str)
            if hrs <= 0:
                raise ValueError()
        except ValueError:
            self.parent_win.show_error("Peringatan", "Jam pemakaian harus lebih besar dari 0.")
            return

        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO equipment_usage_logs (equipment_id, plot_id, usage_date, hours_used, operator_name, activity_desc)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (self.eq_id, plot_id, dt, hrs, op, act))
            self.response(Gtk.ResponseType.OK)
        except Exception as e:
            self.parent_win.show_error("Gagal Menyimpan", f"Error:\n{e}")
        finally:
            conn.close()

class LogServiceDialog(Gtk.Dialog):
    def __init__(self, parent, eq_id, eq_name, cur_hours):
        super().__init__(title=f"Catat Servis Alsintan - {eq_name}", transient_for=parent, flags=0)
        self.set_default_size(460, 360)
        self.parent_win = parent
        self.eq_id = eq_id

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

        grid.attach(Gtk.Label(label="Tanggal Pelaksanaan Servis:", xalign=0), 0, 0, 1, 1)
        self.entry_date = Gtk.Entry()
        self.entry_date.set_text(datetime.date.today().strftime("%Y-%m-%d"))
        grid.attach(self.entry_date, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Jenis Servis / Pemeliharaan:", xalign=0), 0, 1, 1, 1)
        self.combo_type = Gtk.ComboBoxText()
        for t in ["Ganti Oli & Filter", "Perbaikan Berat", "Ganti Suku Cadang", "Tune Up & Pembersihan"]:
            self.combo_type.append_text(t)
        self.combo_type.set_active(0)
        grid.attach(self.combo_type, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label="Biaya Jasa & Sparepart (Rp):", xalign=0), 0, 2, 1, 1)
        self.entry_cost = Gtk.Entry()
        self.entry_cost.set_text("250000")
        grid.attach(self.entry_cost, 1, 2, 1, 1)

        grid.attach(Gtk.Label(label="Bengkel Pelaksana / Teknisi:", xalign=0), 0, 3, 1, 1)
        self.entry_tech = Gtk.Entry()
        self.entry_tech.set_placeholder_text("Contoh: Bengkel Tani Makmur")
        grid.attach(self.entry_tech, 1, 3, 1, 1)

        grid.attach(Gtk.Label(label="Catatan Suku Cadang:", xalign=0), 0, 4, 1, 1)
        self.entry_notes = Gtk.Entry()
        self.entry_notes.set_placeholder_text("Oli mesin diesel 5 liter dan seal klep")
        grid.attach(self.entry_notes, 1, 4, 1, 1)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(12)
        btn_cancel = Gtk.Button(label="Batal")
        btn_cancel.get_style_context().add_class("btn-secondary")
        btn_cancel.connect("clicked", lambda w: self.response(Gtk.ResponseType.CANCEL))
        btn_box.pack_end(btn_cancel, False, False, 0)

        btn_save = Gtk.Button(label="Simpan & Reset Servis")
        btn_save.get_style_context().add_class("btn-primary")
        btn_save.connect("clicked", self._on_save)
        btn_box.pack_end(btn_save, False, False, 0)
        box.pack_start(btn_box, False, False, 0)

        self.show_all()

    def _on_save(self, widget):
        dt = self.entry_date.get_text().strip()
        stype = self.combo_type.get_active_text()
        cost_str = self.entry_cost.get_text().strip().replace(".", "").replace(",", ".")
        tech = self.entry_tech.get_text().strip()
        notes = self.entry_notes.get_text().strip()

        if not tech:
            self.parent_win.show_error("Peringatan", "Nama bengkel/teknisi wajib diisi.")
            return

        try:
            cost = float(cost_str) if cost_str else 0.0
            if cost < 0:
                raise ValueError()
        except ValueError:
            self.parent_win.show_error("Peringatan", "Biaya harus positif atau 0.")
            return

        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO equipment_maintenance_logs (equipment_id, service_date, service_type, cost_idr, workshop_technician, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (self.eq_id, dt, stype, cost, tech, notes))
            self.response(Gtk.ResponseType.OK)
        except Exception as e:
            self.parent_win.show_error("Gagal Menyimpan", f"Error:\n{e}")
        finally:
            conn.close()

class AddEquipmentDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Daftarkan Unit Alsintan Baru", transient_for=parent, flags=0)
        self.set_default_size(460, 360)
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

        grid.attach(Gtk.Label(label="Kode Aset Mesin (unik):", xalign=0), 0, 0, 1, 1)
        self.entry_code = Gtk.Entry()
        self.entry_code.set_placeholder_text("Contoh: TRK-03 / PMP-03")
        grid.attach(self.entry_code, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Nama & Seri Mesin:", xalign=0), 0, 1, 1, 1)
        self.entry_name = Gtk.Entry()
        self.entry_name.set_placeholder_text("Contoh: Traktor Kubota L3218")
        grid.attach(self.entry_name, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label="Kategori Alsintan:", xalign=0), 0, 2, 1, 1)
        self.combo_cat = Gtk.ComboBoxText()
        for c in ["Traktor", "Pompa Air", "Sprayer", "Combine Harvester", "Alat Tanam (Transplanter)"]:
            self.combo_cat.append_text(c)
        self.combo_cat.set_active(0)
        grid.attach(self.combo_cat, 1, 2, 1, 1)

        grid.attach(Gtk.Label(label="Jam Kerja Awal (Jam):", xalign=0), 0, 3, 1, 1)
        self.entry_hours = Gtk.Entry()
        self.entry_hours.set_text("0.0")
        grid.attach(self.entry_hours, 1, 3, 1, 1)

        grid.attach(Gtk.Label(label="Interval Servis Berikutnya (Jam):", xalign=0), 0, 4, 1, 1)
        self.entry_next = Gtk.Entry()
        self.entry_next.set_text("50.0")
        grid.attach(self.entry_next, 1, 4, 1, 1)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(12)
        btn_cancel = Gtk.Button(label="Batal")
        btn_cancel.get_style_context().add_class("btn-secondary")
        btn_cancel.connect("clicked", lambda w: self.response(Gtk.ResponseType.CANCEL))
        btn_box.pack_end(btn_cancel, False, False, 0)

        btn_save = Gtk.Button(label="Simpan Unit")
        btn_save.get_style_context().add_class("btn-primary")
        btn_save.connect("clicked", self._on_save)
        btn_box.pack_end(btn_save, False, False, 0)
        box.pack_start(btn_box, False, False, 0)

        self.show_all()

    def _on_save(self, widget):
        code = self.entry_code.get_text().strip().upper()
        name = self.entry_name.get_text().strip()
        cat = self.combo_cat.get_active_text()
        hrs_str = self.entry_hours.get_text().strip().replace(",", ".")
        next_str = self.entry_next.get_text().strip().replace(",", ".")

        if not code or not name:
            self.parent_win.show_error("Peringatan", "Kode dan nama mesin wajib diisi.")
            return

        try:
            hrs = float(hrs_str)
            next_hrs = float(next_str)
        except ValueError:
            self.parent_win.show_error("Peringatan", "Jam kerja harus berupa angka.")
            return

        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO equipment (equipment_code, name, category, status, total_hours, next_service_hours)
                    VALUES (?, ?, ?, 'Siap Pakai', ?, ?)
                """, (code, name, cat, hrs, next_hrs))
            self.response(Gtk.ResponseType.OK)
        except Exception as e:
            self.parent_win.show_error("Gagal Menyimpan", f"Error kode aset sudah ada:\n{e}")
        finally:
            conn.close()

def main():
    GLib.set_prgname("agri-equipment-log")
    GLib.set_application_name("Agri-Equipment Log")
    try:
        Gdk.set_program_class("agri-equipment-log")
    except Exception:
        pass
    app = EquipmentLogApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
