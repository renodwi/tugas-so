#!/usr/bin/env python3
"""
Agri-Yield Analytics
Analisis Hasil Panen, Produktivitas Lahan & Kualitas Mutu (Grade A/B/C)
Sesuai UI/09_agri_yield_analytics.md & PRD 7.9
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

class YieldAnalyticsApp(AgriWindow):
    def __init__(self):
        super().__init__(
            title="Agri-Yield Analytics - Analisis Hasil Panen",
            icon_name="agri-yield-analytics",
            default_width=1120,
            default_height=760
        )
        init_db()

        self.selected_crop_type = "Semua Komoditas"
        self.search_text = ""

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        # 1. Header
        self.header = AgriHeader(
            title="Analisis Hasil Panen &amp; Mutu",
            subtitle="Produktivitas Ton/Ha, Evaluasi Pencapaian Target &amp; Komposisi Mutu",
            action_label="+ Input Hasil Panen",
            action_callback=self._on_add_yield_clicked,
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

        # Filter bar
        filter_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        lbl_f = Gtk.Label(label="Filter Komoditas:")
        lbl_f.get_style_context().add_class("kpi-title")
        filter_bar.pack_start(lbl_f, False, False, 0)

        self.combo_crop_filter = Gtk.ComboBoxText()
        self.combo_crop_filter.append_text("Semua Komoditas")
        self.combo_crop_filter.append_text("Padi")
        self.combo_crop_filter.append_text("Jagung")
        self.combo_crop_filter.append_text("Kedelai")
        self.combo_crop_filter.set_active(0)
        self.combo_crop_filter.connect("changed", self._on_crop_filter_changed)
        filter_bar.pack_start(self.combo_crop_filter, False, False, 0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Cari riwayat panen, blok lahan, atau varietas...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        filter_bar.pack_end(self.search_entry, True, True, 0)

        content_box.pack_start(filter_bar, False, False, 0)

        # 2. 4 Top KPI Cards
        kpi_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        content_box.pack_start(kpi_row, False, False, 0)

        self.kpi_total = KPICard("Total Hasil Panen", "0 Ton", "Volume Panen Bersih", highlighted=True)
        self.kpi_prod = KPICard("Produktivitas Rata-rata", "0 Ton / Ha", "Rasio Hasil per Lahan", value_color="green")
        self.kpi_target = KPICard("Pencapaian Target", "0% Tercapai", "Terhadap Target Awal")
        self.kpi_mutu = KPICard("Kualitas Utama", "0% Grade A", "Hasil Kualitas Super")

        kpi_row.pack_start(self.kpi_total, True, True, 0)
        kpi_row.pack_start(self.kpi_prod, True, True, 0)
        kpi_row.pack_start(self.kpi_target, True, True, 0)
        kpi_row.pack_start(self.kpi_mutu, True, True, 0)

        # 3. Simple Visualizations (2 Columns)
        viz_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        content_box.pack_start(viz_row, False, False, 0)

        # Left: Target vs Actual comparison bars
        self.left_viz = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.left_viz.get_style_context().add_class("agri-card")
        lbl_v1 = Gtk.Label(xalign=0)
        lbl_v1.set_markup("<b>Target vs Realisasi Panen per Blok</b>\n<span size='small' color='#64748B'>Perbandingan tonase target (abu-abu) vs realisasi (hijau sage)</span>")
        self.left_viz.pack_start(lbl_v1, False, False, 0)
        self.bars_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.left_viz.pack_start(self.bars_container, True, True, 0)
        viz_row.pack_start(self.left_viz, True, True, 0)

        # Right: Grade A / B / C breakdown bars
        self.right_viz = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.right_viz.get_style_context().add_class("agri-card")
        self.right_viz.set_size_request(440, -1)
        lbl_v2 = Gtk.Label(xalign=0)
        lbl_v2.set_markup("<b>Rincian Komposisi Kualitas Mutu Panen</b>\n<span size='small' color='#64748B'>Distribusi mutu hasil panen bersih (Grade A / B / C)</span>")
        self.right_viz.pack_start(lbl_v2, False, False, 0)

        self.grade_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.right_viz.pack_start(self.grade_container, True, True, 0)
        viz_row.pack_start(self.right_viz, False, False, 0)

        # 4. Summary Table
        table_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        table_card.get_style_context().add_class("agri-card")
        content_box.pack_start(table_card, True, True, 0)

        lbl_tbl = Gtk.Label(xalign=0)
        lbl_tbl.set_markup("<b>Tabel Ringkasan Riwayat Panen per Petak Lahan</b>")
        table_card.pack_start(lbl_tbl, False, False, 0)

        # TreeStore: id, harvest_date, plot_name, crop_info, area, target, actual, prod, grades
        self.store = Gtk.ListStore(int, str, str, str, str, str, str, str, str)
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.set_rules_hint(True)

        cols = [
            ("ID", 0, 45, 0.0),
            ("Tanggal Panen", 1, 110, 0.0),
            ("Blok Lahan", 2, 170, 0.0),
            ("Komoditas / Varietas", 3, 160, 0.0),
            ("Luas (Ha)", 4, 90, 1.0),
            ("Target (Ton)", 5, 100, 1.0),
            ("Realisasi (Ton)", 6, 110, 1.0),
            ("Produktivitas", 7, 120, 1.0),
            ("Rincian Mutu (A/B/C)", 8, 150, 0.5)
        ]

        for title, col_idx, width, align in cols:
            renderer = Gtk.CellRendererText()
            renderer.set_alignment(align, 0.5)
            col = Gtk.TreeViewColumn(title, renderer, text=col_idx)
            col.set_min_width(width)
            col.set_resizable(True)
            self.tree.append_column(col)

        table_scroller = Gtk.ScrolledWindow()
        table_scroller.set_min_content_height(260)
        table_scroller.add(self.tree)
        table_card.pack_start(table_scroller, True, True, 0)

        self.refresh_data()

    def _on_crop_filter_changed(self, combo):
        self.selected_crop_type = combo.get_active_text()
        self.refresh_data()

    def _on_search_changed(self, entry):
        self.search_text = entry.get_text().strip().lower()
        self.refresh_data()

    def refresh_data(self):
        conn = get_connection()
        cursor = conn.cursor()

        query_agg = """
            SELECT
                COALESCE(SUM(hy.total_yield_ton), 0),
                COALESCE(SUM(hy.target_ton), 0),
                COALESCE(SUM(p.area_ha), 0),
                COALESCE(SUM(hy.grade_a_ton), 0),
                COALESCE(SUM(hy.grade_b_ton), 0),
                COALESCE(SUM(hy.grade_c_ton), 0)
            FROM harvest_yields hy
            JOIN plots p ON hy.plot_id = p.id
            JOIN crops c ON hy.crop_id = c.id
        """
        params = []
        if self.selected_crop_type != "Semua Komoditas":
            query_agg += " WHERE c.crop_type = ?"
            params.append(self.selected_crop_type)

        cursor.execute(query_agg, params)
        agg = cursor.fetchone()
        tot_yield, tot_target, tot_area, tot_ga, tot_gb, tot_gc = agg

        avg_prod = (tot_yield / tot_area) if tot_area > 0 else 0.0
        achieve_pct = int(round((tot_yield / tot_target * 100))) if tot_target > 0 else 0
        grade_a_pct = int(round((tot_ga / tot_yield * 100))) if tot_yield > 0 else 0

        self.kpi_total.update(format_number(tot_yield, "Ton"), f"Target: {format_number(tot_target, 'Ton')}")
        self.kpi_prod.update(f"{format_number(avg_prod, 'Ton / Ha')}", f"Dari {format_number(tot_area, 'Ha')} total luas panen")
        self.kpi_target.update(f"{achieve_pct}% Tercapai", "Rasio Hasil vs Target")
        self.kpi_mutu.update(f"{grade_a_pct}% Grade A", f"{format_number(tot_ga, 'Ton')} Mutu Super")

        # 2. Populate Target vs Actual Bars (Cairo / Box bars)
        for child in self.bars_container.get_children():
            self.bars_container.remove(child)

        query_bars = """
            SELECT p.plot_code, hy.target_ton, hy.total_yield_ton, c.crop_type
            FROM harvest_yields hy
            JOIN plots p ON hy.plot_id = p.id
            JOIN crops c ON hy.crop_id = c.id
        """
        if self.selected_crop_type != "Semua Komoditas":
            query_bars += " WHERE c.crop_type = ?"
        query_bars += " ORDER BY hy.harvest_date DESC LIMIT 4"
        cursor.execute(query_bars, params)
        bar_rows = cursor.fetchall()

        for b in bar_rows:
            p_code, target, actual, c_type = b
            b_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

            lbl_b = Gtk.Label(xalign=0)
            lbl_b.set_markup(f"<b>{escape(p_code)} ({escape(c_type)})</b> • Target: {format_number(target, 'Ton')} | Realisasi: <b>{format_number(actual, 'Ton')}</b>")
            b_box.pack_start(lbl_b, False, False, 0)

            # Two stacked mini progress bars or dual bar
            max_val = max(1.0, max(target, actual) * 1.1)

            # Actual Bar (Green)
            act_pbar = Gtk.ProgressBar()
            act_pbar.set_fraction(min(1.0, actual / max_val))
            b_box.pack_start(act_pbar, False, False, 0)

            self.bars_container.pack_start(b_box, False, False, 4)

        # 3. Populate Grade Breakdown Bars
        for child in self.grade_container.get_children():
            self.grade_container.remove(child)

        if tot_yield > 0:
            pct_a = int(round(tot_ga / tot_yield * 100))
            pct_b = int(round(tot_gb / tot_yield * 100))
            pct_c = max(0, 100 - pct_a - pct_b)
        else:
            pct_a, pct_b, pct_c = 0, 0, 0

        # Grade A
        ga_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        lbl_ga = Gtk.Label(xalign=0)
        lbl_ga.set_markup(f"<span weight='bold' color='#16A34A'>Grade A (Kualitas Super): {pct_a}% • {format_number(tot_ga, 'Ton')}</span>")
        ga_box.pack_start(lbl_ga, False, False, 0)
        p_ga = Gtk.ProgressBar()
        p_ga.set_fraction(pct_a / 100.0)
        ga_box.pack_start(p_ga, False, False, 0)
        self.grade_container.pack_start(ga_box, False, False, 4)

        # Grade B
        gb_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        lbl_gb = Gtk.Label(xalign=0)
        lbl_gb.set_markup(f"<span weight='bold' color='#D97706'>Grade B (Kualitas Standar): {pct_b}% • {format_number(tot_gb, 'Ton')}</span>")
        gb_box.pack_start(lbl_gb, False, False, 0)
        p_gb = Gtk.ProgressBar()
        p_gb.get_style_context().add_class("progress-amber")
        p_gb.set_fraction(pct_b / 100.0)
        gb_box.pack_start(p_gb, False, False, 0)
        self.grade_container.pack_start(gb_box, False, False, 4)

        # Grade C
        gc_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        lbl_gc = Gtk.Label(xalign=0)
        lbl_gc.set_markup(f"<span weight='bold' color='#DC2626'>Grade C (Sortiran / Afkir): {pct_c}% • {format_number(tot_gc, 'Ton')}</span>")
        gc_box.pack_start(lbl_gc, False, False, 0)
        p_gc = Gtk.ProgressBar()
        p_gc.get_style_context().add_class("progress-red")
        p_gc.set_fraction(pct_c / 100.0)
        gc_box.pack_start(p_gc, False, False, 0)
        self.grade_container.pack_start(gc_box, False, False, 4)

        # 4. Table data
        self.store.clear()
        query_tbl = """
            SELECT hy.id, hy.harvest_date, p.plot_code || ' - ' || p.plot_name,
                   c.crop_type || ' (' || c.variety || ')', p.area_ha, hy.target_ton,
                   hy.total_yield_ton, hy.productivity_ton_ha,
                   hy.grade_a_ton, hy.grade_b_ton, hy.grade_c_ton
            FROM harvest_yields hy
            JOIN plots p ON hy.plot_id = p.id
            JOIN crops c ON hy.crop_id = c.id
        """
        if self.selected_crop_type != "Semua Komoditas":
            query_tbl += " WHERE c.crop_type = ?"
        query_tbl += " ORDER BY hy.harvest_date DESC, hy.id DESC"
        cursor.execute(query_tbl, params)
        rows = cursor.fetchall()

        for r in rows:
            h_id, h_date, p_name, c_info, area, tgt, actual, prod, ga, gb, gc = r
            grade_str = f"A:{format_number(ga)} | B:{format_number(gb)} | C:{format_number(gc)}"

            if self.search_text:
                searchable = f"{p_name} {c_info} {grade_str} {h_date}".lower()
                if self.search_text not in searchable:
                    continue

            self.store.append([
                h_id,
                format_date_id(h_date),
                p_name,
                c_info,
                format_number(area, "Ha"),
                format_number(tgt, "Ton"),
                format_number(actual, "Ton"),
                format_number(prod, "Ton/Ha"),
                grade_str
            ])

        conn.close()
        self.bars_container.show_all()
        self.grade_container.show_all()

    def _on_add_yield_clicked(self, widget):
        dialog = AddYieldDialog(self)
        dialog.run()
        dialog.destroy()
        self.refresh_data()

class AddYieldDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Input Data Hasil Panen Bersih", transient_for=parent, flags=0)
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

        # Plot & Crop
        grid.attach(Gtk.Label(label="Petak Lahan & Tanaman:", xalign=0), 0, 0, 1, 1)
        self.combo_crop = Gtk.ComboBoxText()
        self.crop_plot_pairs = []

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.plot_id, p.plot_code, p.plot_name, c.crop_type, c.variety, p.area_ha, c.target_yield_ton
            FROM crops c
            JOIN plots p ON c.plot_id = p.id
        """)
        for c_id, p_id, p_code, p_name, c_type, c_var, area_ha, tgt_ton in cursor.fetchall():
            self.combo_crop.append_text(f"{p_code} - {p_name} ({c_type} {c_var})")
            self.crop_plot_pairs.append((c_id, p_id, area_ha, tgt_ton))
        conn.close()
        if self.crop_plot_pairs:
            self.combo_crop.set_active(0)
            self.combo_crop.connect("changed", self._on_crop_selection_changed)
        grid.attach(self.combo_crop, 1, 0, 1, 1)

        # Harvest Date
        grid.attach(Gtk.Label(label="Tanggal Panen:", xalign=0), 0, 1, 1, 1)
        self.entry_date = Gtk.Entry()
        self.entry_date.set_text(datetime.date.today().strftime("%Y-%m-%d"))
        grid.attach(self.entry_date, 1, 1, 1, 1)

        # Total Yield Ton
        grid.attach(Gtk.Label(label="Total Berat Panen (Ton):", xalign=0), 0, 2, 1, 1)
        self.entry_total = Gtk.Entry()
        self.entry_total.set_text("7.5")
        grid.attach(self.entry_total, 1, 2, 1, 1)

        # Grade A Ton
        grid.attach(Gtk.Label(label="Grade A - Super (Ton):", xalign=0), 0, 3, 1, 1)
        self.entry_ga = Gtk.Entry()
        self.entry_ga.set_text("5.5")
        grid.attach(self.entry_ga, 1, 3, 1, 1)

        # Grade B Ton
        grid.attach(Gtk.Label(label="Grade B - Standar (Ton):", xalign=0), 0, 4, 1, 1)
        self.entry_gb = Gtk.Entry()
        self.entry_gb.set_text("1.5")
        grid.attach(self.entry_gb, 1, 4, 1, 1)

        # Grade C Ton with Auto-Calc Button
        grid.attach(Gtk.Label(label="Grade C - Afkir (Ton):", xalign=0), 0, 5, 1, 1)
        gc_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.entry_gc = Gtk.Entry()
        self.entry_gc.set_text("0.5")
        gc_box.pack_start(self.entry_gc, True, True, 0)

        btn_auto_c = Gtk.Button(label="⚡ Hitung Sisa")
        btn_auto_c.get_style_context().add_class("btn-secondary")
        btn_auto_c.set_tooltip_text("Hitung otomatis Grade C = Total - (Grade A + Grade B)")
        btn_auto_c.connect("clicked", self._on_calc_grade_c)
        gc_box.pack_start(btn_auto_c, False, False, 0)
        grid.attach(gc_box, 1, 5, 1, 1)

        # Target Ton
        grid.attach(Gtk.Label(label="Target Awal (Ton):", xalign=0), 0, 6, 1, 1)
        self.entry_target = Gtk.Entry()
        self.entry_target.set_text("7.0")
        grid.attach(self.entry_target, 1, 6, 1, 1)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(12)
        btn_cancel = Gtk.Button(label="Batal")
        btn_cancel.get_style_context().add_class("btn-secondary")
        btn_cancel.connect("clicked", lambda w: self.response(Gtk.ResponseType.CANCEL))
        btn_box.pack_end(btn_cancel, False, False, 0)

        btn_save = Gtk.Button(label="Simpan Hasil Panen")
        btn_save.get_style_context().add_class("btn-primary")
        btn_save.connect("clicked", self._on_save)
        btn_box.pack_end(btn_save, False, False, 0)
        box.pack_start(btn_box, False, False, 0)

        self.show_all()

    def _on_calc_grade_c(self, widget):
        try:
            tot = float(self.entry_total.get_text().strip().replace(",", "."))
            ga = float(self.entry_ga.get_text().strip().replace(",", ".")) if self.entry_ga.get_text().strip() else 0.0
            gb = float(self.entry_gb.get_text().strip().replace(",", ".")) if self.entry_gb.get_text().strip() else 0.0
            gc = tot - (ga + gb)
            if gc < -0.001:
                self.parent_win.show_error("Perhitungan Keliru", f"Grade A ({ga}) + Grade B ({gb}) = {ga+gb:.2f} Ton sudah melebihi Total ({tot:.2f} Ton).")
                return
            self.entry_gc.set_text(f"{max(0.0, gc):.2f}".rstrip("0").rstrip("."))
        except ValueError:
            self.parent_win.show_error("Peringatan", "Pastikan kolom Total, Grade A, dan Grade B berisi angka valid.")

    def _on_crop_selection_changed(self, combo):
        idx = combo.get_active()
        if idx >= 0 and self.crop_plot_pairs:
            _, _, _, tgt_ton = self.crop_plot_pairs[idx]
            self.entry_target.set_text(str(tgt_ton))

    def _on_save(self, widget):
        idx = self.combo_crop.get_active()
        if idx < 0 or not self.crop_plot_pairs:
            self.parent_win.show_error("Peringatan", "Pilih blok tanaman.")
            return

        c_id, p_id, area_ha, _ = self.crop_plot_pairs[idx]
        h_date = self.entry_date.get_text().strip()
        tot_str = self.entry_total.get_text().strip().replace(",", ".")
        ga_str = self.entry_ga.get_text().strip().replace(",", ".")
        gb_str = self.entry_gb.get_text().strip().replace(",", ".")
        gc_str = self.entry_gc.get_text().strip().replace(",", ".")
        tgt_str = self.entry_target.get_text().strip().replace(",", ".")

        try:
            total_ton = float(tot_str)
            ga = float(ga_str) if ga_str else 0.0
            gb = float(gb_str) if gb_str else 0.0
            gc = float(gc_str) if gc_str else 0.0
            tgt = float(tgt_str) if tgt_str else total_ton
            if total_ton <= 0:
                raise ValueError()
        except ValueError:
            self.parent_win.show_error("Peringatan", "Total hasil panen harus berupa angka lebih besar dari 0.")
            return

        # REQ-APP09-001: grade sum check
        if abs((ga + gb + gc) - total_ton) > 0.01:
            self.parent_win.show_error("Peringatan", f"Penjumlahan Grade A ({ga}) + B ({gb}) + C ({gc}) = {ga+gb+gc:.2f} Ton harus sama dengan Total Panen ({total_ton} Ton).")
            return

        prod = (total_ton / area_ha) if area_ha > 0 else 0.0
        achieve = (total_ton / tgt * 100.0) if tgt > 0 else 100.0

        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO harvest_yields (crop_id, plot_id, harvest_date, total_yield_ton, productivity_ton_ha, grade_a_ton, grade_b_ton, grade_c_ton, target_ton, achievement_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (c_id, p_id, h_date, total_ton, prod, ga, gb, gc, tgt, achieve))
                conn.execute("UPDATE crops SET status = 'Selesai Panen', harvest_date = ? WHERE id = ?", (h_date, c_id))
                conn.execute("UPDATE plots SET status = 'Persiapan' WHERE id = ?", (p_id,))
            self.response(Gtk.ResponseType.OK)
        except Exception as e:
            self.parent_win.show_error("Gagal Menyimpan", f"Error:\n{e}")
        finally:
            conn.close()

def main():
    GLib.set_prgname("agri-yield-analytics")
    GLib.set_application_name("Agri-Yield Analytics")
    try:
        Gdk.set_program_class("agri-yield-analytics")
    except Exception:
        pass
    app = YieldAnalyticsApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
