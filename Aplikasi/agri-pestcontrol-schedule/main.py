#!/usr/bin/env python3
"""
Agri-PestControl Schedule
Jadwal Semprot, Pengendalian Hama & Batas Aman Panen (PHI)
Sesuai UI/07_agri_pestcontrol_schedule.md & PRD 7.7
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
        PillTabs, format_date_id, escape
    )
except ImportError:
    from common import (
        init_db, get_connection, AgriWindow, AgriHeader, KPICard,
        PillTabs, format_date_id, escape
    )

class PestControlScheduleApp(AgriWindow):
    def __init__(self):
        super().__init__(
            title="Agri-PestControl Schedule - Jadwal Semprot & PHI",
            icon_name="agri-pestcontrol-schedule",
            default_width=1120,
            default_height=750
        )
        init_db()

        self.current_filter = "Semua Lahan"
        self.search_text = ""

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        # 1. Header
        self.header = AgriHeader(
            title="Jadwal Semprot &amp; Pengendalian Hama",
            subtitle="Pengawalan Batas Waktu Aman Konsumsi Pangan (Pre-Harvest Interval / PHI)",
            action_label="+ Catat Penyemprotan",
            action_callback=self._on_add_spray_clicked,
            parent_window=self
        )
        main_box.pack_start(self.header, False, False, 0)

        # Scroller
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        content_box.set_margin_bottom(24)
        scroller.add(content_box)

        # 2. PHI Alert Banner (Container will show/hide dynamically)
        self.banner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.banner_box.get_style_context().add_class("phi-banner")
        self.lbl_banner = Gtk.Label(xalign=0)
        self.lbl_banner.get_style_context().add_class("phi-banner-text")
        self.banner_box.pack_start(self.lbl_banner, True, True, 0)
        content_box.pack_start(self.banner_box, False, False, 0)

        # 3. 3 KPI Cards
        kpi_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        content_box.pack_start(kpi_row, False, False, 0)

        self.kpi_phi = KPICard("Lahan Dalam Masa PHI", "0 Blok", "Dilarang Dipanen", highlighted=True)
        self.kpi_aman = KPICard("Lahan Aman Dipanen", "0 Blok", "Bebas Residu Kimia", value_color="green")
        self.kpi_terakhir = KPICard("Semprot Terakhir", "-", "Aplikasi Perlindungan")

        kpi_row.pack_start(self.kpi_phi, True, True, 0)
        kpi_row.pack_start(self.kpi_aman, True, True, 0)
        kpi_row.pack_start(self.kpi_terakhir, True, True, 0)

        # 4. Filter Bar (Pill Tabs & Search)
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        content_box.pack_start(filter_box, False, False, 0)

        pill_options = ["Semua Lahan", "Dalam Masa Tunggu PHI", "Aman Dipanen"]
        self.tabs = PillTabs(pill_options, self._on_filter_changed)
        filter_box.pack_start(self.tabs, False, False, 0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Cari hama sasaran, pestisida, atau blok lahan...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        filter_box.pack_start(self.search_entry, True, True, 0)

        # 5. Table Container
        table_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        table_card.get_style_context().add_class("agri-card")
        content_box.pack_start(table_card, True, True, 0)

        # TreeStore: id, spray_date, plot_name, pest_name, pesticide, dosage, safe_date, status_str
        self.store = Gtk.ListStore(int, str, str, str, str, str, str, str)
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.set_rules_hint(True)

        cols = [
            ("ID", 0, 50, 0.0),
            ("Tanggal Semprot", 1, 120, 0.0),
            ("Blok Lahan", 2, 200, 0.0),
            ("Hama Sasaran", 3, 160, 0.0),
            ("Pestisida & Bahan Aktif", 4, 180, 0.0),
            ("Dosis Takaran", 5, 120, 0.0),
            ("Tanggal Aman Panen", 6, 140, 0.0),
            ("Status Batas PHI", 7, 160, 0.5)
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

        today = datetime.date.today()
        today_str = today.strftime("%Y-%m-%d")

        # Automatically check and update status of logs whose safe_harvest_date has passed
        with conn:
            conn.execute("""
                UPDATE pest_control_logs
                SET status = 'Aman Dipanen'
                WHERE safe_harvest_date <= ? AND status = 'Masa Tunggu'
            """, (today_str,))

        # Query active PHI blocks
        cursor.execute("""
            SELECT p.plot_code, p.plot_name, pcl.pesticide_name, pcl.safe_harvest_date
            FROM pest_control_logs pcl
            JOIN plots p ON pcl.plot_id = p.id
            WHERE pcl.status = 'Masa Tunggu'
            ORDER BY pcl.safe_harvest_date ASC
        """)
        active_phi = cursor.fetchall()

        if active_phi:
            self.banner_box.set_visible(True)
            blocks_txt = ", ".join([f"{r[0]} (Aman: {format_date_id(r[3])})" for r in active_phi])
            self.lbl_banner.set_markup(
                f"<b>⚠️ PERINGATAN KETAT MASA TUNGGU PANEN (PHI):</b>\n"
                f"Lahan berikut baru disemprot dan dilarang dipanen sebelum tanggal aman: <b>{blocks_txt}</b>"
            )
        else:
            self.banner_box.set_visible(False)

        # Update KPIs
        cursor.execute("SELECT COUNT(DISTINCT plot_id) FROM pest_control_logs WHERE status = 'Masa Tunggu'")
        phi_plots = cursor.fetchone()[0]
        self.kpi_phi.update(f"{phi_plots} Blok Lahan", "Dilarang Tebas Panen")

        cursor.execute("SELECT COUNT(DISTINCT id) FROM plots WHERE status = 'Aktif' AND id NOT IN (SELECT plot_id FROM pest_control_logs WHERE status = 'Masa Tunggu')")
        safe_plots = cursor.fetchone()[0]
        self.kpi_aman.update(f"{safe_plots} Blok Lahan", "Bebas Residu Pestisida")

        cursor.execute("SELECT spray_date, pesticide_name FROM pest_control_logs ORDER BY spray_date DESC LIMIT 1")
        last_spray = cursor.fetchone()
        if last_spray:
            self.kpi_terakhir.update(format_date_id(last_spray[0]), last_spray[1])
        else:
            self.kpi_terakhir.update("-", "Belum ada riwayat")

        # Populate Table
        self.store.clear()
        query = """
            SELECT pcl.id, pcl.spray_date, p.plot_code || ' - ' || p.plot_name,
                   pcl.target_pest, pcl.pesticide_name, pcl.dosage, pcl.safe_harvest_date, pcl.status
            FROM pest_control_logs pcl
            JOIN plots p ON pcl.plot_id = p.id
            ORDER BY pcl.spray_date DESC, pcl.id DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        for r in rows:
            pcl_id, sp_date, p_name, target, pest, dose, safe_date, status = r
            try:
                d_safe = datetime.date.fromisoformat(safe_date[:10])
                diff_days = (d_safe - today).days
            except Exception:
                diff_days = 0

            if self.current_filter == "Dalam Masa Tunggu PHI" and status != "Masa Tunggu":
                continue
            if self.current_filter == "Aman Dipanen" and status != "Aman Dipanen":
                continue

            # Search text filter
            if self.search_text:
                searchable = f"{p_name} {target} {pest} {status} {sp_date} {safe_date}".lower()
                if self.search_text not in searchable:
                    continue

            if status == "Masa Tunggu" and diff_days > 0:
                status_txt = f"⏳ Sisa {diff_days} Hari"
            else:
                status_txt = "✓ Aman Dipanen"

            self.store.append([
                pcl_id,
                format_date_id(sp_date),
                p_name,
                target,
                pest,
                dose,
                format_date_id(safe_date),
                status_txt
            ])

        conn.close()

    def _on_add_spray_clicked(self, widget):
        dialog = AddSprayDialog(self)
        dialog.run()
        dialog.destroy()
        self.refresh_data()

class AddSprayDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Catat Aplikasi Penyemprotan & PHI", transient_for=parent, flags=0)
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

        # Plot & Crop
        grid.attach(Gtk.Label(label="Blok Lahan & Komoditas:", xalign=0), 0, 0, 1, 1)
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
            self.combo_crop.append_text(f"{p_code} - {p_name} ({c_type}) [{c_stat}]")
            self.crop_plot_pairs.append((c_id, p_id))
        conn.close()
        if self.crop_plot_pairs:
            self.combo_crop.set_active(0)
        grid.attach(self.combo_crop, 1, 0, 1, 1)

        # Spray Date
        grid.attach(Gtk.Label(label="Tanggal Semprot (YYYY-MM-DD):", xalign=0), 0, 1, 1, 1)
        self.entry_date = Gtk.Entry()
        self.entry_date.set_text(datetime.date.today().strftime("%Y-%m-%d"))
        grid.attach(self.entry_date, 1, 1, 1, 1)

        # Target Pest
        grid.attach(Gtk.Label(label="Hama / Penyakit Sasaran:", xalign=0), 0, 2, 1, 1)
        self.combo_pest = Gtk.ComboBoxText()
        for h in ["Wereng Batang Coklat", "Ulat Grayak (FAW)", "Penggerek Batang", "Jamur Blas Daun", "Kutu Kebul", "Walang Sangit"]:
            self.combo_pest.append_text(h)
        self.combo_pest.set_active(0)
        grid.attach(self.combo_pest, 1, 2, 1, 1)

        # Pesticide Name
        grid.attach(Gtk.Label(label="Nama & Merek Pestisida:", xalign=0), 0, 3, 1, 1)
        self.entry_pest = Gtk.Entry()
        self.entry_pest.set_placeholder_text("Contoh: Insektisida Virtako 300SC")
        grid.attach(self.entry_pest, 1, 3, 1, 1)

        # Dosage
        grid.attach(Gtk.Label(label="Dosis Aplikasi:", xalign=0), 0, 4, 1, 1)
        self.entry_dose = Gtk.Entry()
        self.entry_dose.set_text("1.5 ml / Liter Air")
        grid.attach(self.entry_dose, 1, 4, 1, 1)

        # PHI Days
        grid.attach(Gtk.Label(label="Masa Tunggu PHI (Hari):", xalign=0), 0, 5, 1, 1)
        self.entry_phi = Gtk.Entry()
        self.entry_phi.set_text("14")
        grid.attach(self.entry_phi, 1, 5, 1, 1)

        # Cost IDR
        grid.attach(Gtk.Label(label="Biaya Pestisida (Rp, Catat ke Kas):", xalign=0), 0, 6, 1, 1)
        self.entry_cost = Gtk.Entry()
        self.entry_cost.set_placeholder_text("Opsional. Contoh: 120000")
        grid.attach(self.entry_cost, 1, 6, 1, 1)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(12)
        btn_cancel = Gtk.Button(label="Batal")
        btn_cancel.get_style_context().add_class("btn-secondary")
        btn_cancel.connect("clicked", lambda w: self.response(Gtk.ResponseType.CANCEL))
        btn_box.pack_end(btn_cancel, False, False, 0)

        btn_save = Gtk.Button(label="Simpan Jadwal Semprot")
        btn_save.get_style_context().add_class("btn-primary")
        btn_save.connect("clicked", self._on_save)
        btn_box.pack_end(btn_save, False, False, 0)
        box.pack_start(btn_box, False, False, 0)

        self.show_all()

    def _on_save(self, widget):
        idx = self.combo_crop.get_active()
        if idx < 0 or not self.crop_plot_pairs:
            self.parent_win.show_error("Peringatan", "Pilih blok lahan sasaran.")
            return

        c_id, p_id = self.crop_plot_pairs[idx]
        spray_date = self.entry_date.get_text().strip()
        target_pest = self.combo_pest.get_active_text()
        pesticide = self.entry_pest.get_text().strip()
        dosage = self.entry_dose.get_text().strip()
        phi_str = self.entry_phi.get_text().strip()

        if not pesticide or not dosage or not phi_str or not spray_date:
            self.parent_win.show_error("Peringatan", "Semua kolom wajib diisi.")
            return

        try:
            phi_days = int(phi_str)
            if phi_days < 0:
                raise ValueError()
        except ValueError:
            self.parent_win.show_error("Peringatan", "Hari PHI harus berupa angka bulat positif atau 0.")
            return

        try:
            d_sp = datetime.date.fromisoformat(spray_date)
            safe_d = (d_sp + datetime.timedelta(days=phi_days)).strftime("%Y-%m-%d")
        except ValueError:
            self.parent_win.show_error("Peringatan", "Format tanggal harus YYYY-MM-DD.")
            return

        status = "Masa Tunggu" if datetime.date.today().strftime("%Y-%m-%d") < safe_d else "Aman Dipanen"
        cost_str = self.entry_cost.get_text().strip().replace(".", "").replace(",", ".")

        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO pest_control_logs (plot_id, crop_id, spray_date, target_pest, pesticide_name, dosage, phi_days, safe_harvest_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (p_id, c_id, spray_date, target_pest, pesticide, dosage, phi_days, safe_d, status))
                sp_id = cursor.lastrowid

                # If cost entered, record to finance_transactions
                if cost_str:
                    try:
                        cost = float(cost_str)
                        if cost > 0:
                            cursor.execute("""
                                INSERT INTO finance_transactions (transaction_date, category, transaction_type, description, amount_idr, source_module, ref_id)
                                VALUES (?, 'Pupuk & Obat', 'Pengeluaran', ?, ?, 'Agri-PestControl Schedule', ?)
                            """, (spray_date, f"Biaya Pestisida {pesticide} ({target_pest})", cost, sp_id))
                    except ValueError:
                        pass

            self.response(Gtk.ResponseType.OK)
        except Exception as e:
            self.parent_win.show_error("Gagal Menyimpan", f"Terjadi kesalahan saat menyimpan data:\n{e}")
        finally:
            conn.close()

def main():
    GLib.set_prgname("agri-pestcontrol-schedule")
    GLib.set_application_name("Agri-PestControl Schedule")
    try:
        Gdk.set_program_class("agri-pestcontrol-schedule")
    except Exception:
        pass
    app = PestControlScheduleApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
