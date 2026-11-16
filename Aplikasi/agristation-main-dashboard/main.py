#!/usr/bin/env python3
"""
AgriStation Main Dashboard
Pusat Kendali Operasional Harian Petani
Sesuai UI/01_agristation_main_dashboard.md & PRD 7.1
"""

import sys
import os
import datetime
import subprocess

# Add common to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "common"))

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango

try:
    from agristation_common import (
        init_db, get_connection, AgriWindow, AgriHeader, KPICard,
        format_rupiah, format_number, format_date_id, escape
    )
except ImportError:
    from common import (
        init_db, get_connection, AgriWindow, AgriHeader, KPICard,
        format_rupiah, format_number, format_date_id, escape
    )

OTHER_APPS = [
    ("agri-crop-scheduler", "🌾 Jadwal Tanam"),
    ("agri-harvest-countdown", "⏱️ Hitung Mundur"),
    ("agri-fertilizer-planner", "🌱 Pemupukan"),
    ("agri-finance-ledger", "💰 Buku Kas"),
    ("agri-irrigation-tracker", "💧 Pengairan"),
    ("agri-pestcontrol-schedule", "🛡️ Hama & PHI"),
    ("agri-equipment-log", "🚜 Alsintan"),
    ("agri-yield-analytics", "📊 Analisis Panen"),
    ("agri-storage-manager", "🏬 Gudang & Silo"),
]

def launch_submodule(app_name):
    bin_path = f"/usr/bin/{app_name}"
    local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), app_name, "main.py")
    if os.path.exists(bin_path):
        subprocess.Popen([bin_path])
    elif os.path.exists(local_path):
        subprocess.Popen([sys.executable, local_path])
    else:
        print(f"Could not locate {app_name}")

class MainDashboardApp(AgriWindow):
    def __init__(self):
        super().__init__(
            title="AgriStation - Pusat Kendali Pertanian",
            app_name="agristation-main-dashboard",
            icon_name="agristation-main-dashboard",
            default_width=1150,
            default_height=780
        )
        init_db()

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        # 1. Top Header
        self.header = AgriHeader(
            title="Selamat Datang di AgriStation",
            subtitle="Pusat Kendali Kebun • Musim Tanam Terpadu 2026",
            action_label="+ Catat Aktivitas",
            action_callback=self._on_add_activity_clicked,
            parent_window=self,
            weather_text="28°C • Cerah Berawan"
        )
        main_box.pack_start(self.header, False, False, 0)

        # Scrollable content area
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        content_box.set_margin_bottom(24)
        scroller.add(content_box)

        # 2. 4 Top KPI Cards
        kpi_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        content_box.pack_start(kpi_row, False, False, 0)

        self.kpi_lahan = KPICard("Total Lahan Aktif", "0 Ha", "0 Plot Terdaftar")
        self.kpi_gudang = KPICard("Kapasitas Gudang", "0%", "0 Ton Terisi")
        self.kpi_panen = KPICard("Panen Terdekat", "-", "- Hari Lagi", highlighted=True)
        self.kpi_kas = KPICard("Saldo Kas Bulan Ini", "Rp 0", "+Rp 0 bln ini", value_color="green")

        kpi_row.pack_start(self.kpi_lahan, True, True, 0)
        kpi_row.pack_start(self.kpi_gudang, True, True, 0)
        kpi_row.pack_start(self.kpi_panen, True, True, 0)
        kpi_row.pack_start(self.kpi_kas, True, True, 0)

        # 3. Quick Launcher Ribbon (Modul AgriStation)
        launcher_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        launcher_card.get_style_context().add_class("agri-card")

        lbl_ribbon = Gtk.Label(xalign=0)
        lbl_ribbon.set_markup("<b>Akses Cepat Modul Mandiri AgriStation:</b>")
        launcher_card.pack_start(lbl_ribbon, False, False, 0)

        ribbon_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for sub_name, sub_label in OTHER_APPS:
            btn = Gtk.Button(label=sub_label)
            btn.get_style_context().add_class("pill-tab")
            btn.connect("clicked", lambda w, s=sub_name: launch_submodule(s))
            ribbon_box.pack_start(btn, False, False, 0)

        launcher_card.pack_start(ribbon_box, False, False, 0)
        content_box.pack_start(launcher_card, False, False, 0)

        # 4. Asymmetric 2-Column Content (60% Left, 40% Right)
        columns_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        content_box.pack_start(columns_box, True, True, 0)

        # LEFT COLUMN (60%): Today's Tasks Checklist
        left_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        left_col.get_style_context().add_class("agri-card")
        columns_box.pack_start(left_col, True, True, 0)

        left_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        left_title = Gtk.Label(xalign=0)
        left_title.set_markup("<b>Daftar Tugas Mandor Hari Ini</b>")
        left_header.pack_start(left_title, True, True, 0)

        btn_clear_done = Gtk.Button(label="Bersihkan Selesai")
        btn_clear_done.get_style_context().add_class("btn-secondary")
        btn_clear_done.connect("clicked", self._on_clear_completed_tasks)
        left_header.pack_end(btn_clear_done, False, False, 0)

        btn_refresh_tasks = Gtk.Button(label="Segarkan")
        btn_refresh_tasks.get_style_context().add_class("btn-secondary")
        btn_refresh_tasks.connect("clicked", lambda w: self.refresh_data())
        left_header.pack_end(btn_refresh_tasks, False, False, 0)
        left_col.pack_start(left_header, False, False, 4)

        self.tasks_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        left_col.pack_start(self.tasks_container, True, True, 0)

        # RIGHT COLUMN (40%): Active Plots Condition & Alerts
        right_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        right_col.get_style_context().add_class("agri-card")
        right_col.set_size_request(380, -1)
        columns_box.pack_end(right_col, False, False, 0)

        right_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        right_title = Gtk.Label(xalign=0)
        right_title.set_markup("<b>Kondisi Lahan &amp; Peringatan</b>")
        right_header.pack_start(right_title, True, True, 0)
        right_col.pack_start(right_header, False, False, 4)

        self.plots_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        right_col.pack_start(self.plots_container, True, True, 0)

        self.refresh_data()

    def refresh_data(self):
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Total Lahan Dikelola (Aktif & Persiapan)
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(area_ha), 0) FROM plots WHERE status != 'Nonaktif'")
        row = cursor.fetchone()
        plot_count, total_ha = row[0], row[1]
        self.kpi_lahan.update(
            format_number(total_ha, "Ha"),
            f"{plot_count} Plot Dikelola"
        )

        # 2. Kapasitas Gudang
        cursor.execute("SELECT COALESCE(SUM(capacity_ton), 0), COALESCE(SUM(used_ton), 0) FROM storage_locations")
        row = cursor.fetchone()
        cap_ton, used_ton = row[0], row[1]
        pct = int(round((used_ton / cap_ton * 100))) if cap_ton > 0 else 0
        self.kpi_gudang.update(
            f"{pct}% Terisi",
            f"{format_number(used_ton, 'Ton')} / {format_number(cap_ton, 'Ton')}"
        )

        # 3. Panen Terdekat
        cursor.execute("""
            SELECT c.crop_type, c.variety, c.est_harvest_date, p.plot_code
            FROM crops c
            JOIN plots p ON c.plot_id = p.id
            WHERE c.status = 'Sedang Tumbuh'
            ORDER BY c.est_harvest_date ASC
            LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            c_type, c_var, est_date, p_code = row[0], row[1], row[2], row[3]
            try:
                d_est = datetime.date.fromisoformat(est_date[:10])
                d_today = datetime.date.today()
                diff_days = (d_est - d_today).days
                days_txt = "Hari Ini!" if diff_days == 0 else (f"{diff_days} Hari Lagi" if diff_days > 0 else f"Terlambat {-diff_days} Hari")
            except Exception:
                days_txt = est_date
            self.kpi_panen.update(f"{c_type} {c_var}", f"{days_txt} ({p_code})")
        else:
            self.kpi_panen.update("Tidak ada", "Belum ada jadwal panen")

        # 4. Saldo Kas Bulan Ini
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN transaction_type = 'Pemasukan' THEN amount_idr ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN transaction_type = 'Pengeluaran' THEN amount_idr ELSE 0 END), 0)
            FROM finance_transactions
        """)
        saldo = cursor.fetchone()[0]
        self.kpi_kas.update(format_rupiah(saldo), "Saldo Pembukuan Aktif")

        # 5. Populate Daily Tasks
        for child in self.tasks_container.get_children():
            self.tasks_container.remove(child)

        cursor.execute("""
            SELECT t.id, t.task_title, t.category, t.is_completed, p.plot_code, p.plot_name
            FROM daily_tasks t
            JOIN plots p ON t.plot_id = p.id
            ORDER BY t.is_completed ASC, t.id DESC
        """)
        tasks = cursor.fetchall()
        if not tasks:
            empty_lbl = Gtk.Label(label="Tidak ada tugas harian untuk hari ini.", xalign=0)
            empty_lbl.get_style_context().add_class("kpi-subtext")
            self.tasks_container.pack_start(empty_lbl, False, False, 10)
        else:
            for task_id, title, cat, is_comp, p_code, p_name in tasks:
                t_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                t_row.set_margin_top(4)
                t_row.set_margin_bottom(4)

                chk = Gtk.CheckButton()
                chk.set_active(bool(is_comp))
                chk.connect("toggled", self._on_task_toggled, task_id)
                t_row.pack_start(chk, False, False, 0)

                t_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                t_title = Gtk.Label(xalign=0)
                if is_comp:
                    t_title.set_markup(f"<span strikethrough='true' color='#94A3B8'>{escape(title)}</span>")
                else:
                    t_title.set_markup(f"<span weight='600' color='#1E293B'>{escape(title)}</span>")
                t_info.pack_start(t_title, False, False, 0)

                t_loc = Gtk.Label(xalign=0)
                t_loc.set_markup(f"<span size='small' color='#64748B'>Lokasi: {escape(p_name)} ({escape(p_code)})</span>")
                t_info.pack_start(t_loc, False, False, 0)
                t_row.pack_start(t_info, True, True, 0)

                # Badge
                badge = Gtk.Label()
                badge.get_style_context().add_class("badge")
                if cat in ("Pemupukan", "Pupuk"):
                    badge.get_style_context().add_class("badge-mint")
                elif cat in ("Pengairan", "Irigasi"):
                    badge.get_style_context().add_class("badge-blue")
                elif cat in ("Semprot", "Penyemprotan"):
                    badge.get_style_context().add_class("badge-warning")
                else:
                    badge.get_style_context().add_class("badge-neutral")
                badge.set_text(cat)
                t_row.pack_end(badge, False, False, 0)

                self.tasks_container.pack_start(t_row, False, False, 0)

        # 6. Populate Plots Condition & Alerts (include all plots)
        for child in self.plots_container.get_children():
            self.plots_container.remove(child)

        cursor.execute("""
            SELECT p.id, p.plot_code, p.plot_name, p.status, c.crop_type, c.variety, c.current_stage, c.est_harvest_date,
                   (SELECT COUNT(*) FROM pest_control_logs pcl WHERE pcl.plot_id = p.id AND pcl.status = 'Masa Tunggu') AS phi_active
            FROM plots p
            LEFT JOIN crops c ON p.id = c.plot_id AND c.status = 'Sedang Tumbuh'
            ORDER BY p.plot_code ASC
        """)
        plots = cursor.fetchall()
        for p_id, p_code, p_name, p_stat, c_type, c_var, stage, est_h, phi_cnt in plots:
            p_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            p_box.get_style_context().add_class("agri-card")
            p_box.set_margin_bottom(6)

            h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            lbl_pname = Gtk.Label(xalign=0)
            lbl_pname.set_markup(f"<b>{escape(p_code)}</b> • <span color='#475569'>{escape(p_name)}</span>")
            h_box.pack_start(lbl_pname, True, True, 0)

            if phi_cnt > 0:
                phi_badge = Gtk.Label()
                phi_badge.get_style_context().add_class("badge")
                phi_badge.get_style_context().add_class("badge-warning")
                phi_badge.set_markup("<b>Masa Tunggu PHI</b>")
                h_box.pack_end(phi_badge, False, False, 0)
            elif p_stat == "Persiapan":
                p_badge = Gtk.Label()
                p_badge.get_style_context().add_class("badge")
                p_badge.get_style_context().add_class("badge-neutral")
                p_badge.set_text("Persiapan Lahan")
                h_box.pack_end(p_badge, False, False, 0)

            p_box.pack_start(h_box, False, False, 0)

            c_text = f"{escape(c_type)} ({escape(c_var)}) • Fase: <b>{escape(stage or 'Tanam')}</b>" if c_type else f"<i>Status lahan: {escape(p_stat)}</i>"
            lbl_c = Gtk.Label(xalign=0)
            lbl_c.set_markup(f"<span size='small' color='#64748B'>{c_text}</span>")
            p_box.pack_start(lbl_c, False, False, 0)

            if est_h:
                lbl_est = Gtk.Label(xalign=0)
                lbl_est.set_markup(f"<span size='small' color='#2E7D32'>Estimasi Panen: {format_date_id(est_h)}</span>")
                p_box.pack_start(lbl_est, False, False, 0)

            self.plots_container.pack_start(p_box, False, False, 0)

        conn.close()
        self.tasks_container.show_all()
        self.plots_container.show_all()

    def _on_task_toggled(self, button, task_id):
        new_val = 1 if button.get_active() else 0
        conn = get_connection()
        with conn:
            conn.execute("UPDATE daily_tasks SET is_completed = ? WHERE id = ?", (new_val, task_id))
        conn.close()
        self.refresh_data()

    def _on_clear_completed_tasks(self, widget):
        if not self.confirm_action("Bersihkan Tugas Selesai", "Hapus seluruh tugas harian yang telah dicentang selesai?"):
            return
        conn = get_connection()
        with conn:
            conn.execute("DELETE FROM daily_tasks WHERE is_completed = 1")
        conn.close()
        self.refresh_data()

    def _on_add_activity_clicked(self, widget):
        dialog = AddTaskDialog(self)
        dialog.run()
        dialog.destroy()
        self.refresh_data()

class AddTaskDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Catat Tugas Aktivitas Harian", transient_for=parent, flags=0)
        self.set_default_size(480, 360)
        self.parent_win = parent

        box = self.get_content_area()
        box.set_spacing(12)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(16)
        box.set_margin_bottom(16)

        # Title
        box.pack_start(Gtk.Label(label="Deskripsi Tugas / Aktivitas:", xalign=0), False, False, 0)
        self.entry_title = Gtk.Entry()
        self.entry_title.set_placeholder_text("Contoh: Semprot fungisida pencegah blas daun")
        box.pack_start(self.entry_title, False, False, 0)

        # Category
        box.pack_start(Gtk.Label(label="Kategori Aktivitas:", xalign=0), False, False, 0)
        self.combo_cat = Gtk.ComboBoxText()
        for c in ["Pemupukan", "Pengairan", "Semprot", "Panen", "Olah Tanah", "Perawatan Mesin"]:
            self.combo_cat.append_text(c)
        self.combo_cat.set_active(0)
        box.pack_start(self.combo_cat, False, False, 0)

        # Plot (load all managed plots)
        box.pack_start(Gtk.Label(label="Lokasi Blok Lahan:", xalign=0), False, False, 0)
        self.combo_plot = Gtk.ComboBoxText()
        self.plot_ids = []
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, plot_code, plot_name, status FROM plots ORDER BY plot_code ASC")
        for p_id, p_code, p_name, p_stat in cursor.fetchall():
            self.combo_plot.append_text(f"{p_code} - {p_name} ({p_stat})")
            self.plot_ids.append(p_id)
        conn.close()
        if self.plot_ids:
            self.combo_plot.set_active(0)
        box.pack_start(self.combo_plot, False, False, 0)

        # Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(10)
        btn_cancel = Gtk.Button(label="Batal")
        btn_cancel.get_style_context().add_class("btn-secondary")
        btn_cancel.connect("clicked", lambda w: self.response(Gtk.ResponseType.CANCEL))
        btn_box.pack_end(btn_cancel, False, False, 0)

        btn_save = Gtk.Button(label="Simpan Tugas")
        btn_save.get_style_context().add_class("btn-primary")
        btn_save.connect("clicked", self._on_save)
        btn_box.pack_end(btn_save, False, False, 0)
        box.pack_start(btn_box, False, False, 0)

        self.show_all()

    def _on_save(self, widget):
        title = self.entry_title.get_text().strip()
        if not title:
            self.parent_win.show_error("Peringatan", "Deskripsi tugas tidak boleh kosong.")
            return

        cat = self.combo_cat.get_active_text()
        plot_idx = self.combo_plot.get_active()
        if plot_idx < 0 or not self.plot_ids:
            self.parent_win.show_error("Peringatan", "Silakan pilih blok lahan.")
            return

        plot_id = self.plot_ids[plot_idx]
        today_str = datetime.date.today().strftime("%Y-%m-%d")

        conn = get_connection()
        with conn:
            conn.execute("""
                INSERT INTO daily_tasks (task_date, task_title, category, plot_id, is_completed)
                VALUES (?, ?, ?, ?, 0)
            """, (today_str, title, cat, plot_id))
        conn.close()

        self.response(Gtk.ResponseType.OK)

def main():
    GLib.set_prgname("agristation-main-dashboard")
    GLib.set_application_name("AgriStation Main Dashboard")
    try:
        Gdk.set_program_class("agristation-main-dashboard")
    except Exception:
        pass
    app = MainDashboardApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
