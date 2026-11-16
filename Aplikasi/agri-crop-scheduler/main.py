#!/usr/bin/env python3
"""
Agri-Crop Scheduler
Jadwal dan Plot Tanam
Sesuai UI/02_agri_crop_scheduler.md & PRD 7.2
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

class CropSchedulerApp(AgriWindow):
    def __init__(self):
        super().__init__(
            title="Agri-Crop Scheduler - Jadwal & Plot Tanam",
            app_name="agri-crop-scheduler",
            icon_name="agri-crop-scheduler",
            default_width=1120,
            default_height=760
        )
        init_db()

        self.current_filter = "Semua Plot"
        self.search_query = ""

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        # 1. Header
        self.header = AgriHeader(
            title="Jadwal &amp; Plot Tanam",
            subtitle="Manajemen Blok Lahan, Varietas Tanaman &amp; Rotasi Musim",
            action_label="+ Tambah Plot / Tanam Baru",
            action_callback=self._on_add_plot_clicked,
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

        # 2. KPI Cards Row (3 Cards)
        kpi_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        content_box.pack_start(kpi_row, False, False, 0)

        self.kpi_aktif = KPICard("Total Plot Dikelola", "0", "Terdaftar di Sistem", highlighted=True)
        self.kpi_luas = KPICard("Total Luas Tertanam", "0 Ha", "Akumulasi Bervegetasi", value_color="green")
        self.kpi_komoditas = KPICard("Komoditas Utama", "-", "Dominan Musim Ini")

        kpi_row.pack_start(self.kpi_aktif, True, True, 0)
        kpi_row.pack_start(self.kpi_luas, True, True, 0)
        kpi_row.pack_start(self.kpi_komoditas, True, True, 0)

        # 3. Filter Bar (Pill Tabs + Search Entry)
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        content_box.pack_start(filter_box, False, False, 0)

        pill_options = ["Semua Plot", "Sedang Tumbuh", "Persiapan Lahan", "Selesai Panen"]
        self.tabs = PillTabs(pill_options, self._on_filter_changed)
        filter_box.pack_start(self.tabs, True, True, 0)

        # Search entry
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        search_box.pack_start(Gtk.Label(label="Cari:"), False, False, 0)
        self.entry_search = Gtk.SearchEntry()
        self.entry_search.set_placeholder_text("Nama blok / varietas...")
        self.entry_search.connect("search-changed", self._on_search_changed)
        search_box.pack_start(self.entry_search, False, False, 0)
        filter_box.pack_end(search_box, False, False, 0)

        # 4. Grid 2 Columns for Plot Cards
        self.grid_flow = Gtk.FlowBox()
        self.grid_flow.set_valign(Gtk.Align.START)
        self.grid_flow.set_max_children_per_line(2)
        self.grid_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.grid_flow.set_column_spacing(16)
        self.grid_flow.set_row_spacing(16)
        content_box.pack_start(self.grid_flow, True, True, 0)

        self.refresh_data()

    def _on_filter_changed(self, option):
        self.current_filter = option
        self.refresh_data()

    def _on_search_changed(self, entry):
        self.search_query = entry.get_text().strip().lower()
        self.refresh_data()

    def refresh_data(self):
        conn = get_connection()
        cursor = conn.cursor()

        # Update KPIs
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(area_ha), 0) FROM plots WHERE status != 'Nonaktif'")
        row = cursor.fetchone()
        plot_count, total_ha = row[0], row[1]
        self.kpi_aktif.update(f"{plot_count} Plot", f"{format_number(total_ha, 'Ha')} total luas garapan")

        cursor.execute("""
            SELECT COALESCE(SUM(p.area_ha), 0)
            FROM plots p
            JOIN crops c ON p.id = c.plot_id
            WHERE c.status = 'Sedang Tumbuh'
        """)
        tertanam_ha = cursor.fetchone()[0]
        self.kpi_luas.update(format_number(tertanam_ha, "Ha"), "Lahan Sedang Ditanami")

        cursor.execute("""
            SELECT crop_type, COUNT(*) as cnt
            FROM crops
            WHERE status = 'Sedang Tumbuh'
            GROUP BY crop_type
            ORDER BY cnt DESC
            LIMIT 1
        """)
        top_crop = cursor.fetchone()
        if top_crop:
            self.kpi_komoditas.update(top_crop[0], f"{top_crop[1]} Plot Aktif")
        else:
            self.kpi_komoditas.update("-", "Tidak ada tanaman aktif")

        # Clear grid
        for child in self.grid_flow.get_children():
            self.grid_flow.remove(child)

        # Query plots with filter
        query = """
            SELECT p.id, p.plot_code, p.plot_name, p.area_ha, p.status as plot_status, p.soil_type,
                   c.id as crop_id, c.crop_type, c.variety, c.planting_date, c.est_harvest_date,
                   c.current_stage, c.status as crop_status, c.target_yield_ton
            FROM plots p
            LEFT JOIN crops c ON p.id = c.plot_id AND c.status = 'Sedang Tumbuh'
            ORDER BY p.plot_code ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        for r in rows:
            p_id, p_code, p_name, p_area, p_status, soil = r[0], r[1], r[2], r[3], r[4], r[5]
            c_id, c_type, c_var, plant_d, est_d = r[6], r[7], r[8], r[9], r[10]
            stage, c_status, target_ton = r[11], r[12], r[13]

            # Filter logic
            if self.current_filter == "Sedang Tumbuh" and c_status != "Sedang Tumbuh":
                continue
            if self.current_filter == "Persiapan Lahan" and p_status != "Persiapan":
                continue
            if self.current_filter == "Selesai Panen" and (c_status == "Sedang Tumbuh" or p_status not in ("Istirahat", "Persiapan")):
                continue

            # Search query logic
            if self.search_query:
                combined = f"{p_code} {p_name} {c_type or ''} {c_var or ''}".lower()
                if self.search_query not in combined:
                    continue

            card = self._create_plot_card(
                p_id, p_code, p_name, p_area, p_status, soil,
                c_id, c_type, c_var, plant_d, est_d, stage, c_status, target_ton
            )
            self.grid_flow.add(card)

        conn.close()
        self.grid_flow.show_all()

    def _create_plot_card(self, p_id, p_code, p_name, p_area, p_status, soil,
                           c_id, c_type, c_var, plant_d, est_d, stage, c_status, target_ton):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        card.get_style_context().add_class("agri-card")
        card.set_size_request(480, -1)
        card.set_margin_bottom(6)

        # Header: Name, Area, Status badge
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        lbl_code = Gtk.Label(xalign=0)
        lbl_code.set_markup(f"<b>{escape(p_code)}</b> • <span color='#1E293B'>{escape(p_name)}</span>")
        title_box.pack_start(lbl_code, False, False, 0)

        lbl_area = Gtk.Label(xalign=0)
        lbl_area.set_markup(f"<span size='small' color='#64748B'>Luas: {format_number(p_area, 'Ha')} • Tanah: {escape(soil or 'Normal')}</span>")
        title_box.pack_start(lbl_area, False, False, 0)
        header.pack_start(title_box, True, True, 0)

        badge_status = Gtk.Label()
        badge_status.get_style_context().add_class("badge")
        if c_status == "Sedang Tumbuh":
            badge_status.get_style_context().add_class("badge-success")
            badge_status.set_text("Sedang Tumbuh")
        elif p_status == "Persiapan":
            badge_status.get_style_context().add_class("badge-warning")
            badge_status.set_text("Persiapan Lahan")
        else:
            badge_status.get_style_context().add_class("badge-neutral")
            badge_status.set_text(p_status)
        header.pack_end(badge_status, False, False, 0)
        card.pack_start(header, False, False, 0)

        # Separator line
        card.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 2)

        # Crop Info & Variety
        if c_type:
            crop_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            crop_badge = Gtk.Label()
            crop_badge.get_style_context().add_class("badge")
            crop_badge.get_style_context().add_class("badge-mint")
            crop_badge.set_markup(f"<b>🌾 {escape(c_type)} • Varietas {escape(c_var)}</b>")
            crop_box.pack_start(crop_badge, False, False, 0)

            stage_badge = Gtk.Label()
            stage_badge.get_style_context().add_class("badge")
            stage_badge.get_style_context().add_class("badge-blue")
            stage_badge.set_markup(f"Fase: <b>{escape(stage or 'Tanam')}</b>")
            crop_box.pack_start(stage_badge, False, False, 0)
            card.pack_start(crop_box, False, False, 0)

            # Dates 2 columns
            dates_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            d1_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            d1_lbl = Gtk.Label(xalign=0)
            d1_lbl.set_markup("<span size='small' color='#64748B'>Tanggal Tanam:</span>")
            d1_val = Gtk.Label(xalign=0)
            d1_val.set_markup(f"<b>{format_date_id(plant_d)}</b>")
            d1_box.pack_start(d1_lbl, False, False, 0)
            d1_box.pack_start(d1_val, False, False, 0)
            dates_box.pack_start(d1_box, True, True, 0)

            d2_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            d2_lbl = Gtk.Label(xalign=0)
            d2_lbl.set_markup("<span size='small' color='#64748B'>Perkiraan Panen:</span>")
            d2_val = Gtk.Label(xalign=0)
            d2_val.set_markup(f"<span weight='bold' color='#2E7D32'>{format_date_id(est_d)}</span>")
            d2_box.pack_start(d2_lbl, False, False, 0)
            d2_box.pack_start(d2_val, False, False, 0)
            dates_box.pack_start(d2_box, True, True, 0)

            d3_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            d3_lbl = Gtk.Label(xalign=0)
            d3_lbl.set_markup("<span size='small' color='#64748B'>Target Tonase:</span>")
            d3_val = Gtk.Label(xalign=0)
            d3_val.set_markup(f"<b>{format_number(target_ton or 0, 'Ton')}</b>")
            d3_box.pack_start(d3_lbl, False, False, 0)
            d3_box.pack_start(d3_val, False, False, 0)
            dates_box.pack_start(d3_box, True, True, 0)

            card.pack_start(dates_box, False, False, 4)
        else:
            empty_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            empty_c = Gtk.Label(xalign=0)
            empty_c.set_markup("<span color='#94A3B8'><i>Plot kosong / siap tanam musim baru.</i></span>")
            empty_box.pack_start(empty_c, True, True, 0)
            card.pack_start(empty_box, False, False, 6)

        # Card Actions
        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        actions.set_margin_top(4)

        if c_id:
            btn_stage = Gtk.Button(label="Perbarui Fase")
            btn_stage.get_style_context().add_class("btn-secondary")
            btn_stage.connect("clicked", self._on_change_stage, c_id, stage, p_id)
            actions.pack_start(btn_stage, False, False, 0)

            btn_finish = Gtk.Button(label="Selesai Panen")
            btn_finish.get_style_context().add_class("btn-outline")
            btn_finish.connect("clicked", self._on_finish_crop, c_id, p_id, p_name)
            actions.pack_start(btn_finish, False, False, 0)
        else:
            btn_new_season = Gtk.Button(label="+ Mulai Musim Tanam Baru")
            btn_new_season.get_style_context().add_class("btn-primary")
            btn_new_season.connect("clicked", self._on_plant_existing_plot, p_id, p_code, p_name)
            actions.pack_start(btn_new_season, False, False, 0)

        card.pack_start(actions, False, False, 0)
        return card

    def _on_change_stage(self, widget, crop_id, current_stage, plot_id):
        dialog = Gtk.Dialog(title="Perbarui Fase Tanaman", transient_for=self, flags=0)
        dialog.set_default_size(360, 200)
        box = dialog.get_content_area()
        box.set_spacing(10)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_margin_top(16)

        box.pack_start(Gtk.Label(label="Pilih Fase Pertumbuhan Baru:", xalign=0), False, False, 0)
        combo = Gtk.ComboBoxText()
        stages = ["Tanam", "Vegetatif", "Bunga", "Siap Panen"]
        for s in stages:
            combo.append_text(s)
        try:
            combo.set_active(stages.index(current_stage))
        except ValueError:
            combo.set_active(0)
        box.pack_start(combo, False, False, 0)

        dialog.add_button("Batal", Gtk.ResponseType.CANCEL)
        dialog.add_button("Simpan Perubahan", Gtk.ResponseType.OK)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            new_stage = combo.get_active_text()
            conn = get_connection()
            with conn:
                conn.execute("UPDATE crops SET current_stage = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_stage, crop_id))
            conn.close()
            self.refresh_data()
        dialog.destroy()

    def _on_finish_crop(self, widget, crop_id, plot_id, plot_name):
        if not self.confirm_action(
            "Konfirmasi Selesai Panen",
            f"Tandai musim tanam pada {plot_name} sebagai 'Selesai Panen'?\nPlot akan dipindahkan ke status persiapan/istirahat."
        ):
            return

        conn = get_connection()
        with conn:
            conn.execute("UPDATE crops SET status = 'Selesai Panen', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (crop_id,))
            conn.execute("UPDATE plots SET status = 'Persiapan', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (plot_id,))
        conn.close()
        self.show_info("Sukses", "Status berhasil diperbarui menjadi Selesai Panen.")
        self.refresh_data()

    def _on_plant_existing_plot(self, widget, plot_id, plot_code, plot_name):
        dialog = PlantSeasonDialog(self, plot_id, plot_code, plot_name)
        dialog.run()
        dialog.destroy()
        self.refresh_data()

    def _on_add_plot_clicked(self, widget):
        dialog = AddPlotDialog(self)
        dialog.run()
        dialog.destroy()
        self.refresh_data()

class PlantSeasonDialog(Gtk.Dialog):
    """Start a new crop season on an existing plot."""
    def __init__(self, parent, plot_id, plot_code, plot_name):
        super().__init__(title=f"Mulai Musim Tanam Baru - {plot_code}", transient_for=parent, flags=0)
        self.set_default_size(480, 420)
        self.parent_win = parent
        self.plot_id = plot_id

        box = self.get_content_area()
        box.set_spacing(10)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(16)
        box.set_margin_bottom(16)

        box.pack_start(Gtk.Label(label=f"Menanam pada plot: <b>{plot_code} - {plot_name}</b>", xalign=0, use_markup=True), False, False, 4)

        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(10)
        box.pack_start(grid, True, True, 0)

        # Crop Type
        grid.attach(Gtk.Label(label="Komoditas Tanaman:", xalign=0), 0, 0, 1, 1)
        self.combo_crop = Gtk.ComboBoxText()
        for c in ["Padi", "Jagung", "Kedelai", "Bawang Merah", "Cabai Merah"]:
            self.combo_crop.append_text(c)
        self.combo_crop.set_active(0)
        grid.attach(self.combo_crop, 1, 0, 1, 1)

        # Variety
        grid.attach(Gtk.Label(label="Varietas Benih:", xalign=0), 0, 1, 1, 1)
        self.entry_var = Gtk.Entry()
        self.entry_var.set_placeholder_text("Contoh: Ciherang / Inpari 32")
        grid.attach(self.entry_var, 1, 1, 1, 1)

        # Planting Date
        grid.attach(Gtk.Label(label="Tanggal Tanam (YYYY-MM-DD):", xalign=0), 0, 2, 1, 1)
        self.entry_plant = Gtk.Entry()
        self.entry_plant.set_text(datetime.date.today().strftime("%Y-%m-%d"))
        grid.attach(self.entry_plant, 1, 2, 1, 1)

        # Estimated Harvest Date
        grid.attach(Gtk.Label(label="Estimasi Panen (YYYY-MM-DD):", xalign=0), 0, 3, 1, 1)
        self.entry_est = Gtk.Entry()
        self.entry_est.set_text((datetime.date.today() + datetime.timedelta(days=100)).strftime("%Y-%m-%d"))
        grid.attach(self.entry_est, 1, 3, 1, 1)

        # Target Ton
        grid.attach(Gtk.Label(label="Target Tonase (Ton):", xalign=0), 0, 4, 1, 1)
        self.entry_target = Gtk.Entry()
        self.entry_target.set_text("7.0")
        grid.attach(self.entry_target, 1, 4, 1, 1)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(12)
        btn_cancel = Gtk.Button(label="Batal")
        btn_cancel.get_style_context().add_class("btn-secondary")
        btn_cancel.connect("clicked", lambda w: self.response(Gtk.ResponseType.CANCEL))
        btn_box.pack_end(btn_cancel, False, False, 0)

        btn_save = Gtk.Button(label="Mulai Tanam")
        btn_save.get_style_context().add_class("btn-primary")
        btn_save.connect("clicked", self._on_save)
        btn_box.pack_end(btn_save, False, False, 0)
        box.pack_start(btn_box, False, False, 0)

        self.show_all()

    def _on_save(self, widget):
        crop_type = self.combo_crop.get_active_text()
        variety = self.entry_var.get_text().strip()
        plant_d = self.entry_plant.get_text().strip()
        est_d = self.entry_est.get_text().strip()
        target_str = self.entry_target.get_text().strip().replace(",", ".")

        if not variety or not plant_d or not est_d:
            self.parent_win.show_error("Peringatan", "Varietas dan tanggal wajib diisi.")
            return

        try:
            target_ton = float(target_str) if target_str else 0.0
            d_p = datetime.date.fromisoformat(plant_d)
            d_e = datetime.date.fromisoformat(est_d)
            if d_e <= d_p:
                self.parent_win.show_error("Peringatan", "Estimasi panen harus setelah tanggal tanam.")
                return
        except ValueError:
            self.parent_win.show_error("Peringatan", "Format tanggal atau target ton tidak valid.")
            return

        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO crops (plot_id, crop_type, variety, planting_date, est_harvest_date, current_stage, target_yield_ton, status)
                    VALUES (?, ?, ?, ?, ?, 'Tanam', ?, 'Sedang Tumbuh')
                """, (self.plot_id, crop_type, variety, plant_d, est_d, target_ton))
                conn.execute("UPDATE plots SET status = 'Aktif' WHERE id = ?", (self.plot_id,))
            self.response(Gtk.ResponseType.OK)
        except Exception as e:
            self.parent_win.show_error("Gagal Menyimpan", f"Error:\n{e}")
        finally:
            conn.close()

class AddPlotDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Daftarkan Petak Lahan Baru", transient_for=parent, flags=0)
        self.set_default_size(520, 500)
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

        # Plot Code
        grid.attach(Gtk.Label(label="Kode Plot (unik):", xalign=0), 0, 0, 1, 1)
        self.entry_code = Gtk.Entry()
        self.entry_code.set_placeholder_text("Contoh: BLK-D1")
        grid.attach(self.entry_code, 1, 0, 1, 1)

        # Plot Name
        grid.attach(Gtk.Label(label="Nama Lahan / Blok:", xalign=0), 0, 1, 1, 1)
        self.entry_name = Gtk.Entry()
        self.entry_name.set_placeholder_text("Contoh: Blok D1 - Sawah Baru")
        grid.attach(self.entry_name, 1, 1, 1, 1)

        # Area Ha
        grid.attach(Gtk.Label(label="Luas Lahan (Ha):", xalign=0), 0, 2, 1, 1)
        self.entry_area = Gtk.Entry()
        self.entry_area.set_placeholder_text("Contoh: 1.25")
        grid.attach(self.entry_area, 1, 2, 1, 1)

        # Soil Type
        grid.attach(Gtk.Label(label="Jenis Tanah:", xalign=0), 0, 3, 1, 1)
        self.entry_soil = Gtk.Entry()
        self.entry_soil.set_text("Lempung Berliat")
        grid.attach(self.entry_soil, 1, 3, 1, 1)

        # Crop Type
        grid.attach(Gtk.Label(label="Komoditas Awal:", xalign=0), 0, 4, 1, 1)
        self.combo_crop = Gtk.ComboBoxText()
        for c in ["Padi", "Jagung", "Kedelai", "Bawang Merah", "Cabai Merah"]:
            self.combo_crop.append_text(c)
        self.combo_crop.set_active(0)
        grid.attach(self.combo_crop, 1, 4, 1, 1)

        # Variety
        grid.attach(Gtk.Label(label="Varietas Benih:", xalign=0), 0, 5, 1, 1)
        self.entry_var = Gtk.Entry()
        self.entry_var.set_placeholder_text("Contoh: Inpari 32 / Ciherang")
        grid.attach(self.entry_var, 1, 5, 1, 1)

        # Planting Date
        grid.attach(Gtk.Label(label="Tanggal Tanam (YYYY-MM-DD):", xalign=0), 0, 6, 1, 1)
        self.entry_plant = Gtk.Entry()
        today_s = datetime.date.today().strftime("%Y-%m-%d")
        self.entry_plant.set_text(today_s)
        grid.attach(self.entry_plant, 1, 6, 1, 1)

        # Estimated Harvest Date
        grid.attach(Gtk.Label(label="Estimasi Panen (YYYY-MM-DD):", xalign=0), 0, 7, 1, 1)
        self.entry_est = Gtk.Entry()
        est_default = (datetime.date.today() + datetime.timedelta(days=100)).strftime("%Y-%m-%d")
        self.entry_est.set_text(est_default)
        grid.attach(self.entry_est, 1, 7, 1, 1)

        # Target Ton
        grid.attach(Gtk.Label(label="Target Hasil (Ton):", xalign=0), 0, 8, 1, 1)
        self.entry_target = Gtk.Entry()
        self.entry_target.set_text("7.0")
        grid.attach(self.entry_target, 1, 8, 1, 1)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(12)
        btn_cancel = Gtk.Button(label="Batal")
        btn_cancel.get_style_context().add_class("btn-secondary")
        btn_cancel.connect("clicked", lambda w: self.response(Gtk.ResponseType.CANCEL))
        btn_box.pack_end(btn_cancel, False, False, 0)

        btn_save = Gtk.Button(label="Daftarkan Plot")
        btn_save.get_style_context().add_class("btn-primary")
        btn_save.connect("clicked", self._on_save)
        btn_box.pack_end(btn_save, False, False, 0)
        box.pack_start(btn_box, False, False, 0)

        self.show_all()

    def _on_save(self, widget):
        code = self.entry_code.get_text().strip().upper()
        name = self.entry_name.get_text().strip()
        area_str = self.entry_area.get_text().strip().replace(",", ".")
        soil = self.entry_soil.get_text().strip()
        crop_type = self.combo_crop.get_active_text()
        variety = self.entry_var.get_text().strip()
        plant_d = self.entry_plant.get_text().strip()
        est_d = self.entry_est.get_text().strip()
        target_str = self.entry_target.get_text().strip().replace(",", ".")

        if not code or not name or not area_str or not variety or not plant_d or not est_d:
            self.parent_win.show_error("Peringatan", "Seluruh kolom bertanda wajib harus diisi lengkap.")
            return

        try:
            area_ha = float(area_str)
            if area_ha <= 0:
                raise ValueError()
        except ValueError:
            self.parent_win.show_error("Peringatan", "Luas lahan harus berupa angka desimal positif lebih besar dari 0.")
            return

        try:
            target_ton = float(target_str) if target_str else 0.0
        except ValueError:
            target_ton = 0.0

        try:
            d_p = datetime.date.fromisoformat(plant_d)
            d_e = datetime.date.fromisoformat(est_d)
            if d_e <= d_p:
                self.parent_win.show_error("Peringatan", "Estimasi tanggal panen harus setelah tanggal tanam.")
                return
        except ValueError:
            self.parent_win.show_error("Peringatan", "Format tanggal harus YYYY-MM-DD.")
            return

        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO plots (plot_code, plot_name, area_ha, soil_type, status)
                    VALUES (?, ?, ?, ?, 'Aktif')
                """, (code, name, area_ha, soil))
                plot_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO crops (plot_id, crop_type, variety, planting_date, est_harvest_date, current_stage, target_yield_ton, status)
                    VALUES (?, ?, ?, ?, ?, 'Tanam', ?, 'Sedang Tumbuh')
                """, (plot_id, crop_type, variety, plant_d, est_d, target_ton))

            self.response(Gtk.ResponseType.OK)
        except Exception as e:
            self.parent_win.show_error("Gagal Menyimpan", f"Terjadi kesalahan atau kode plot sudah digunakan:\n{e}")
        finally:
            conn.close()

def main():
    GLib.set_prgname("agri-crop-scheduler")
    GLib.set_application_name("Agri-Crop Scheduler")
    try:
        Gdk.set_program_class("agri-crop-scheduler")
    except Exception:
        pass
    app = CropSchedulerApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
