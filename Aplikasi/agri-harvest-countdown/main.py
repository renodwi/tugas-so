#!/usr/bin/env python3
"""
Agri-Harvest Countdown
Hitung Mundur Panen & Pemantau Progres Pertumbuhan Tanaman
Sesuai UI/03_agri_harvest_countdown.md & PRD 7.3
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

class HarvestCountdownApp(AgriWindow):
    def __init__(self):
        super().__init__(
            title="Agri-Harvest Countdown - Hitung Mundur Panen",
            app_name="agri-harvest-countdown",
            icon_name="agri-harvest-countdown",
            default_width=1120,
            default_height=760
        )
        init_db()

        self.sort_mode = "panen_terdekat"

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        # 1. Header
        self.header = AgriHeader(
            title="Hitung Mundur Panen",
            subtitle="Pemantau Umur Tanaman (HST), Fase Pertumbuhan &amp; Kesiapan Panen",
            action_label="Segarkan Data",
            action_callback=lambda w: self.refresh_data(),
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

        # 2. Controls & Filter Bar
        ctrl_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        content_box.pack_start(ctrl_bar, False, False, 0)

        self.lbl_summary = Gtk.Label(xalign=0)
        self.lbl_summary.get_style_context().add_class("kpi-title")
        ctrl_bar.pack_start(self.lbl_summary, True, True, 0)

        ctrl_bar.pack_end(Gtk.Label(label="Urutan:"), False, False, 0)
        self.combo_sort = Gtk.ComboBoxText()
        self.combo_sort.append_text("Panen Terdekat")
        self.combo_sort.append_text("Baru Ditanam")
        self.combo_sort.set_active(0)
        self.combo_sort.connect("changed", self._on_sort_changed)
        ctrl_bar.pack_end(self.combo_sort, False, False, 0)

        # 3. Cards Container (Flow / Vertical)
        self.cards_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content_box.pack_start(self.cards_container, True, True, 0)

        self.refresh_data()

    def _on_sort_changed(self, combo):
        txt = combo.get_active_text()
        self.sort_mode = "baru_ditanam" if txt == "Baru Ditanam" else "panen_terdekat"
        self.refresh_data()

    def refresh_data(self):
        for child in self.cards_container.get_children():
            self.cards_container.remove(child)

        conn = get_connection()
        cursor = conn.cursor()

        order_by = "c.est_harvest_date ASC" if self.sort_mode == "panen_terdekat" else "c.planting_date DESC"

        query = f"""
            SELECT c.id, c.plot_id, c.crop_type, c.variety, c.planting_date, c.est_harvest_date,
                   c.current_stage, c.target_yield_ton, p.plot_code, p.plot_name, p.area_ha,
                   (SELECT COUNT(*) FROM pest_control_logs pcl WHERE pcl.plot_id = p.id AND pcl.status = 'Masa Tunggu') as phi_count
            FROM crops c
            JOIN plots p ON c.plot_id = p.id
            WHERE c.status = 'Sedang Tumbuh'
            ORDER BY {order_by}
        """
        cursor.execute(query)
        crops = cursor.fetchall()

        today = datetime.date.today()
        ready_count = 0

        for row in crops:
            c_id, p_id, c_type, c_var, plant_d, est_d = row[0], row[1], row[2], row[3], row[4], row[5]
            stage, target_ton, p_code, p_name, area_ha, phi_cnt = row[6], row[7], row[8], row[9], row[10], row[11]

            # Calculate HST & countdown days
            try:
                d_plant = datetime.date.fromisoformat(plant_d[:10])
                d_est = datetime.date.fromisoformat(est_d[:10])
            except Exception:
                d_plant = today
                d_est = today + datetime.timedelta(days=90)

            hst = max(0, (today - d_plant).days)
            total_duration = max(1, (d_est - d_plant).days)
            remaining_days = (d_est - today).days

            # Progress percentage
            pct = min(1.0, max(0.0, hst / total_duration))
            pct_int = int(round(pct * 100))

            if remaining_days <= 7:
                ready_count += 1

            card = self._create_countdown_card(
                c_id, p_id, c_type, c_var, plant_d, est_d, stage, target_ton,
                p_code, p_name, area_ha, phi_cnt, hst, remaining_days, pct, pct_int
            )
            self.cards_container.pack_start(card, False, False, 0)

        conn.close()

        self.lbl_summary.set_markup(
            f"<span size='medium' weight='bold' color='#2E7D32'>{ready_count} Plot Siap Panen dalam Waktu Dekat (≤ 7 Hari)</span>"
        )
        self.cards_container.show_all()

    def _create_countdown_card(self, c_id, p_id, c_type, c_var, plant_d, est_d, stage,
                               target_ton, p_code, p_name, area_ha, phi_cnt, hst, remaining_days, pct, pct_int):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.get_style_context().add_class("agri-card")

        # Top Header: Plot + Crop left, Countdown right
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)

        left_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        lbl_p = Gtk.Label(xalign=0)
        lbl_p.set_markup(f"<span size='large' weight='bold' color='#1E293B'>{escape(p_code)} • {escape(p_name)}</span>")
        left_info.pack_start(lbl_p, False, False, 0)

        lbl_c = Gtk.Label(xalign=0)
        lbl_c.set_markup(f"<span color='#2E7D32' weight='bold'>🌾 {escape(c_type)} ({escape(c_var)})</span> • Luas: {format_number(area_ha, 'Ha')} • Umur: <b>{hst} HST</b>")
        left_info.pack_start(lbl_c, False, False, 0)
        top_row.pack_start(left_info, True, True, 0)

        # Right countdown badge/text
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        if phi_cnt > 0:
            phi_b = Gtk.Label()
            phi_b.get_style_context().add_class("badge")
            phi_b.get_style_context().add_class("badge-warning")
            phi_b.set_markup("<b>Masa Tunggu PHI Aktif!</b>")
            right_box.pack_start(phi_b, False, False, 0)

        if remaining_days <= 0:
            cd_badge = Gtk.Label()
            cd_badge.get_style_context().add_class("badge")
            cd_badge.get_style_context().add_class("badge-success")
            cd_badge.set_markup("<span size='large'><b>✓ SIAP PANEN</b></span>")
            right_box.pack_start(cd_badge, False, False, 0)
        elif remaining_days <= 7:
            cd_lbl = Gtk.Label(xalign=1)
            cd_lbl.set_markup(f"<span size='x-large' weight='bold' color='#D97706'>{remaining_days} Hari Lagi</span>")
            right_box.pack_start(cd_lbl, False, False, 0)
        else:
            cd_lbl = Gtk.Label(xalign=1)
            cd_lbl.set_markup(f"<span size='x-large' weight='bold' color='#2E7D32'>{remaining_days} Hari Lagi</span>")
            right_box.pack_start(cd_lbl, False, False, 0)

        top_row.pack_end(right_box, False, False, 0)
        card.pack_start(top_row, False, False, 0)

        # Progress Bar (14px thickness)
        pb_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        pbar = Gtk.ProgressBar()
        pbar.set_fraction(pct)
        if remaining_days <= 0:
            pbar.get_style_context().add_class("progress-amber")
        pb_box.pack_start(pbar, False, False, 0)

        pb_sub = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        pb_l = Gtk.Label(xalign=0)
        pb_l.set_markup(f"<span size='small' color='#64748B'>Tanam: <b>{format_date_id(plant_d)}</b></span>")
        pb_sub.pack_start(pb_l, True, True, 0)

        pb_m = Gtk.Label()
        pb_m.set_markup(f"<span size='small' weight='bold' color='#1E293B'>Kemajuan Pertumbuhan: {pct_int}%</span>")
        pb_sub.pack_start(pb_m, False, False, 0)

        pb_r = Gtk.Label(xalign=1)
        pb_r.set_markup(f"<span size='small' color='#64748B'>Perkiraan Panen: <b>{format_date_id(est_d)}</b></span>")
        pb_sub.pack_end(pb_r, True, True, 0)
        pb_box.pack_start(pb_sub, False, False, 0)

        card.pack_start(pb_box, False, False, 0)

        # Stage markers row: Tanam -> Vegetatif -> Bunga -> Siap Panen
        stages = ["Tanam", "Vegetatif", "Bunga", "Siap Panen"]
        stage_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        stage_row.set_margin_top(4)

        for s in stages:
            s_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            s_box.get_style_context().add_class("badge")
            if s == stage:
                s_box.get_style_context().add_class("badge-mint")
                s_lbl = Gtk.Label()
                s_lbl.set_markup(f"<b>● {s} (Aktif)</b>")
            else:
                s_box.get_style_context().add_class("badge-neutral")
                s_lbl = Gtk.Label()
                s_lbl.set_markup(f"<span color='#94A3B8'>○ {s}</span>")
            s_box.pack_start(s_lbl, False, False, 0)
            stage_row.pack_start(s_box, False, False, 0)

        # Action buttons
        btn_stage = Gtk.Button(label="Perbarui Fase")
        btn_stage.get_style_context().add_class("btn-secondary")
        btn_stage.connect("clicked", self._on_update_stage, c_id, stage)
        stage_row.pack_end(btn_stage, False, False, 0)

        # Harvest Yield button if ready
        if remaining_days <= 5 or stage == "Siap Panen":
            btn_harvest = Gtk.Button(label="🌾 Input Panen")
            btn_harvest.get_style_context().add_class("btn-primary")
            btn_harvest.connect("clicked", self._on_harvest_clicked, c_id, p_id, p_name, target_ton, area_ha)
            stage_row.pack_end(btn_harvest, False, False, 0)

        card.pack_start(stage_row, False, False, 0)
        return card

    def _on_update_stage(self, widget, crop_id, current_stage):
        dialog = Gtk.Dialog(title="Pilih Fase Tanaman", transient_for=self, flags=0)
        dialog.set_default_size(360, 180)
        box = dialog.get_content_area()
        box.set_spacing(10)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_margin_top(16)

        box.pack_start(Gtk.Label(label="Perbarui status fase tanaman saat ini:", xalign=0), False, False, 0)
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
        dialog.add_button("Simpan", Gtk.ResponseType.OK)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            new_stage = combo.get_active_text()
            conn = get_connection()
            with conn:
                conn.execute("UPDATE crops SET current_stage = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_stage, crop_id))
            conn.close()
            self.refresh_data()
        dialog.destroy()

    def _on_harvest_clicked(self, widget, crop_id, plot_id, plot_name, target_ton, area_ha):
        dialog = Gtk.Dialog(title=f"Catat Panen - {plot_name}", transient_for=self, flags=0)
        dialog.set_default_size(460, 360)
        box = dialog.get_content_area()
        box.set_spacing(10)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(16)
        box.set_margin_bottom(16)

        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(10)
        box.pack_start(grid, True, True, 0)

        grid.attach(Gtk.Label(label="Tanggal Panen:", xalign=0), 0, 0, 1, 1)
        entry_hdate = Gtk.Entry()
        entry_hdate.set_text(datetime.date.today().strftime("%Y-%m-%d"))
        grid.attach(entry_hdate, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Total Berat Panen (Ton):", xalign=0), 0, 1, 1, 1)
        entry_total = Gtk.Entry()
        entry_total.set_text(str(target_ton or "6.5"))
        grid.attach(entry_total, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label="Grade A - Super (Ton):", xalign=0), 0, 2, 1, 1)
        entry_ga = Gtk.Entry()
        entry_ga.set_text(str(round((target_ton or 6.5) * 0.75, 2)))
        grid.attach(entry_ga, 1, 2, 1, 1)

        grid.attach(Gtk.Label(label="Grade B - Standar (Ton):", xalign=0), 0, 3, 1, 1)
        entry_gb = Gtk.Entry()
        entry_gb.set_text(str(round((target_ton or 6.5) * 0.20, 2)))
        grid.attach(entry_gb, 1, 3, 1, 1)

        grid.attach(Gtk.Label(label="Grade C - Afkir (Ton):", xalign=0), 0, 4, 1, 1)
        entry_gc = Gtk.Entry()
        entry_gc.set_text(str(round((target_ton or 6.5) * 0.05, 2)))
        grid.attach(entry_gc, 1, 4, 1, 1)

        dialog.add_button("Batal", Gtk.ResponseType.CANCEL)
        dialog.add_button("Simpan Panen", Gtk.ResponseType.OK)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            try:
                tot_ton = float(entry_total.get_text().strip().replace(",", "."))
                ga = float(entry_ga.get_text().strip().replace(",", "."))
                gb = float(entry_gb.get_text().strip().replace(",", "."))
                gc = float(entry_gc.get_text().strip().replace(",", "."))
                h_d = entry_hdate.get_text().strip()

                prod = (tot_ton / area_ha) if area_ha > 0 else 0.0
                achieve = (tot_ton / target_ton * 100.0) if target_ton > 0 else 100.0

                conn = get_connection()
                with conn:
                    conn.execute("""
                        INSERT INTO harvest_yields (crop_id, plot_id, harvest_date, total_yield_ton, productivity_ton_ha, grade_a_ton, grade_b_ton, grade_c_ton, target_ton, achievement_pct)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (crop_id, plot_id, h_d, tot_ton, prod, ga, gb, gc, target_ton, achieve))
                    conn.execute("UPDATE crops SET status = 'Selesai Panen', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (crop_id,))
                    conn.execute("UPDATE plots SET status = 'Persiapan', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (plot_id,))
                conn.close()
                self.show_info("Sukses", "Data panen berhasil disimpan dan plot dialihkan ke status persiapan.")
                self.refresh_data()
            except Exception as e:
                self.show_error("Gagal", f"Error: {e}")
        dialog.destroy()

def main():
    GLib.set_prgname("agri-harvest-countdown")
    GLib.set_application_name("Agri-Harvest Countdown")
    try:
        Gdk.set_program_class("agri-harvest-countdown")
    except Exception:
        pass
    app = HarvestCountdownApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
