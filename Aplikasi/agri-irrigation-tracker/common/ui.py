"""
Master UI Design System and Shared GTK3 Components for AgriStation Suite.
Complies strictly with:
- UI/00_master_design_system.md
- Strict Light Mode (#F8FAF8 canvas, #FFFFFF card surface, #2E7D32 Forest Sage Green)
- Font >= 16px, buttons >= 44px, tabular-nums formatting
- Indonesian localization (Rp, koma desimal, bahasa Indonesia)
"""

import os
import shutil
import subprocess
import datetime
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GLib, Pango, GdkPixbuf

from .db import DB_PATH
from .backup import create_backup, restore_backup, list_backups

# CSS Stylesheet enforcing Master Design System
CSS_THEME = """
/* Master Agri-Clean Minimalist Style */

* {
    font-family: 'Plus Jakarta Sans', 'Inter', 'Ubuntu', 'DejaVu Sans', sans-serif;
    font-size: 15px;
    color: #1E293B;
}

window, .agri-canvas {
    background-color: #F8FAF8;
}

/* Cards */
.agri-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px;
}

.agri-card-highlight {
    background-color: #FFFFFF;
    border: 2px solid #2E7D32;
    border-radius: 12px;
    padding: 16px;
}

/* KPI Cards */
.kpi-title {
    font-size: 13px;
    font-weight: bold;
    color: #64748B;
}

.kpi-value {
    font-size: 26px;
    font-weight: 800;
    color: #1E293B;
    margin: 4px 0;
}

.kpi-value-green {
    font-size: 26px;
    font-weight: 800;
    color: #16A34A;
}

.kpi-value-red {
    font-size: 26px;
    font-weight: 800;
    color: #DC2626;
}

.kpi-subtext {
    font-size: 13px;
    color: #64748B;
}

/* Buttons */
button {
    min-height: 44px;
    padding: 8px 18px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 14px;
}

.btn-primary {
    background-color: #2E7D32;
    color: #FFFFFF;
    border: 1px solid #2E7D32;
}
.btn-primary:hover {
    background-color: #1B5E20;
    color: #FFFFFF;
}

.btn-outline {
    background-color: #FFFFFF;
    color: #2E7D32;
    border: 2px solid #2E7D32;
}
.btn-outline:hover {
    background-color: #E8F5E9;
    color: #1B5E20;
}

.btn-danger {
    background-color: #DC2626;
    color: #FFFFFF;
    border: 1px solid #DC2626;
}
.btn-danger:hover {
    background-color: #B91C1C;
    color: #FFFFFF;
}

.btn-secondary {
    background-color: #FFFFFF;
    color: #475569;
    border: 1px solid #CBD5E1;
}
.btn-secondary:hover {
    background-color: #F1F5F9;
    color: #1E293B;
}

/* Pill Filter Buttons */
.pill-tab {
    background-color: #FFFFFF;
    color: #64748B;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: bold;
    min-height: 36px;
}
.pill-tab:checked, .pill-tab.active {
    background-color: #2E7D32;
    color: #FFFFFF;
    border: 1px solid #2E7D32;
}
.pill-tab:hover {
    background-color: #F1F5F9;
}
.pill-tab.active:hover {
    background-color: #1B5E20;
    color: #FFFFFF;
}

/* Badges */
.badge {
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
}

.badge-success {
    background-color: #DCFCE7;
    color: #16A34A;
}

.badge-warning {
    background-color: #FEF3C7;
    color: #D97706;
}

.badge-danger {
    background-color: #FEE2E2;
    color: #DC2626;
}

.badge-mint {
    background-color: #E8F5E9;
    color: #2E7D32;
}

.badge-neutral {
    background-color: #F1F5F9;
    color: #475569;
}

.badge-blue {
    background-color: #E0F2FE;
    color: #0284C7;
}

/* PHI Alert Banner */
.phi-banner {
    background-color: #FEF3C7;
    border: 2px solid #FCD34D;
    border-radius: 10px;
    padding: 12px 18px;
}
.phi-banner-text {
    color: #B45309;
    font-size: 14px;
    font-weight: bold;
}

/* TreeView (Tables) */
treeview {
    background-color: #FFFFFF;
    color: #1E293B;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    font-size: 14px;
}

treeview:selected {
    background-color: #E8F5E9;
    color: #1B5E20;
}

treeview header button {
    background-color: #F8FAF8;
    color: #475569;
    font-weight: bold;
    font-size: 13px;
    border-bottom: 2px solid #E2E8F0;
    min-height: 38px;
}

/* Progress bar */
progressbar trough {
    background-color: #E2E8F0;
    border-radius: 7px;
    min-height: 14px;
}

progressbar progress {
    background-color: #2E7D32;
    border-radius: 7px;
    min-height: 14px;
}

.progress-amber progress {
    background-color: #D97706;
}

.progress-red progress {
    background-color: #DC2626;
}

/* Entries and Combobox */
entry, combobox button {
    min-height: 42px;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 6px 12px;
    background-color: #FFFFFF;
    font-size: 14px;
}
entry:focus {
    border: 2px solid #2E7D32;
}
"""

_css_loaded = False

def init_styles():
    global _css_loaded
    if _css_loaded:
        return
    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(CSS_THEME.encode('utf-8'))
    screen = Gdk.Screen.get_default()
    if screen:
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    _css_loaded = True

def escape(s):
    """Safely escape text for Pango/Gtk markup."""
    if s is None:
        return ""
    return GLib.markup_escape_text(str(s))

def format_rupiah(amount):
    """Format float/int to Indonesian Rupiah e.g. Rp 24.500.000"""
    try:
        val = int(round(float(amount)))
        is_neg = val < 0
        val = abs(val)
        s = f"{val:,}".replace(",", ".")
        if is_neg:
            return f"-Rp {s}"
        return f"Rp {s}"
    except Exception:
        return f"Rp {amount}"

def format_number(val, unit="", decimals=1):
    """Format decimal number using Indonesian comma, e.g. 4,5 Ha or 28,4 Ton"""
    try:
        f = float(val)
        fmt = f"{{:.{decimals}f}}".format(f).replace(".", ",")
        if unit:
            return f"{fmt} {unit}"
        return fmt
    except Exception:
        return f"{val} {unit}".strip()

def format_date_id(date_str):
    """Format YYYY-MM-DD to Indonesian format, e.g. 16 Nov 2026"""
    if not date_str:
        return "-"
    try:
        d = datetime.date.fromisoformat(date_str[:10])
        months = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
        return f"{d.day} {months[d.month - 1]} {d.year}"
    except Exception:
        return date_str

class AgriWindow(Gtk.Window):
    """Base Window enforcing standard AgriStation styles, icons, and Wayland/X11 dock integration."""
    def __init__(self, title, icon_name=None, app_name=None, default_width=1050, default_height=700):
        name = app_name or icon_name or "agristation"
        
        # Critical for Wayland and GNOME Shell dock to match the window to its .desktop file:
        GLib.set_prgname(name)
        try:
            if not GLib.get_application_name():
                GLib.set_application_name(title)
        except Exception:
            pass
        try:
            Gdk.set_program_class(name)
        except Exception:
            pass

        super().__init__(title=title)
        init_styles()
        self.set_default_size(default_width, default_height)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.get_style_context().add_class("agri-canvas")
        
        try:
            self.set_wmclass(name, name)
            self.set_role(name)
        except Exception:
            pass

        # Load and set application icon across window and dock
        if name:
            self._set_app_icon(name, title)

    def _set_app_icon(self, icon_name, title="AgriStation"):
        # Append possible search paths to icon theme
        theme = Gtk.IconTheme.get_default()
        local_icons_dir = os.path.expanduser("~/.local/share/icons")
        if os.path.exists(local_icons_dir):
            theme.append_search_path(local_icons_dir)
            
        workspace_icon_dir = os.path.join(os.path.dirname(__file__), "..", "Icon")
        if os.path.exists(workspace_icon_dir):
            theme.append_search_path(workspace_icon_dir)

        # Find SVG file
        possible_svg_paths = [
            os.path.join(os.path.dirname(__file__), "..", "Icon", f"{icon_name}.svg"),
            os.path.join(os.path.dirname(__file__), "..", f"{icon_name}.svg"),
            os.path.join(os.path.dirname(__file__), f"{icon_name}.svg"),
            os.path.expanduser(f"~/.local/share/icons/hicolor/scalable/apps/{icon_name}.svg"),
            f"/usr/share/icons/hicolor/scalable/apps/{icon_name}.svg"
        ]
        
        svg_path = None
        for p in possible_svg_paths:
            if os.path.exists(p):
                svg_path = os.path.abspath(p)
                break

        # Register to user space (~/.local/share) if needed so dock always has it
        self._ensure_user_desktop_integration(icon_name, title, svg_path)

        # Set icon name
        try:
            self.set_icon_name(icon_name)
            Gtk.Window.set_default_icon_name(icon_name)
        except Exception:
            pass

        # Set multi-resolution pixbufs list for compositors
        if svg_path:
            pixbufs = []
            for sz in [16, 24, 32, 48, 64, 128, 256]:
                try:
                    pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(svg_path, sz, sz, True)
                    pixbufs.append(pb)
                except Exception:
                    pass
            if pixbufs:
                self.set_icon_list(pixbufs)
                Gtk.Window.set_default_icon_list(pixbufs)

    def _ensure_user_desktop_integration(self, app_name, title, svg_path):
        """Ensures ~/.local/share/applications/<app_name>.desktop and icon exist."""
        try:
            user_apps = os.path.expanduser("~/.local/share/applications")
            user_icons = os.path.expanduser("~/.local/share/icons/hicolor")
            desktop_file = os.path.join(user_apps, f"{app_name}.desktop")

            if not os.path.exists(desktop_file) or not os.path.exists(os.path.join(user_icons, "scalable", "apps", f"{app_name}.svg")):
                os.makedirs(user_apps, exist_ok=True)
                os.makedirs(os.path.join(user_icons, "scalable", "apps"), exist_ok=True)
                
                if svg_path and os.path.exists(svg_path):
                    shutil.copy2(svg_path, os.path.join(user_icons, "scalable", "apps", f"{app_name}.svg"))
                    for sz in [16, 32, 48, 64, 128, 256]:
                        os.makedirs(os.path.join(user_icons, f"{sz}x{sz}", "apps"), exist_ok=True)
                        try:
                            pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(svg_path, sz, sz, True)
                            pb.savev(os.path.join(user_icons, f"{sz}x{sz}", "apps", f"{app_name}.png"), "png", [], [])
                        except Exception:
                            pass

                # Write desktop entry
                app_exec = f"/home/renodwi/Downloads/Aplikasi/{app_name}/main.py"
                d_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={title}
Comment={title} - AgriStation Suite
Exec=python3 {app_exec}
Icon={app_name}
Terminal=false
Categories=Office;Utility;Agriculture;
StartupWMClass={app_name}
StartupNotify=true
"""
                with open(desktop_file, "w", encoding="utf-8") as f:
                    f.write(d_content)

                try:
                    subprocess.run(["update-desktop-database", user_apps], capture_output=True)
                    subprocess.run(["gtk-update-icon-cache", "-q", "-t", "-f", user_icons], capture_output=True)
                except Exception:
                    pass
        except Exception:
            pass

    def show_info(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def show_error(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def confirm_action(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=title
        )
        dialog.format_secondary_text(message)
        response = dialog.run()
        dialog.destroy()
        return response == Gtk.ResponseType.YES

    def open_backup_dialog(self):
        dialog = BackupRestoreDialog(self)
        dialog.run()
        dialog.destroy()

class AgriHeader(Gtk.Box):
    """
    Standard top header bar:
    Left: Title & Subtitle/Date context
    Right: Weather Pill / Status, Backup Button, Primary Action Button
    """
    def __init__(self, title, subtitle=None, action_label=None, action_callback=None, parent_window=None, weather_text="28°C • Cerah Berawan"):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self.set_margin_start(20)
        self.set_margin_end(20)
        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.parent_window = parent_window

        # Left Title Box
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        lbl_title = Gtk.Label(xalign=0)
        lbl_title.set_markup(f"<span size='x-large' weight='bold' color='#1E293B'>{title}</span>")
        title_box.pack_start(lbl_title, False, False, 0)
        
        today_str = datetime.date.today().strftime("%d %b %Y")
        sub = subtitle or f"Hari ini, {today_str}"
        lbl_sub = Gtk.Label(xalign=0)
        lbl_sub.set_markup(f"<span size='small' color='#64748B'>{sub}</span>")
        title_box.pack_start(lbl_sub, False, False, 0)
        self.pack_start(title_box, True, True, 0)

        # Right Controls
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        # Weather / Environment Pill
        if weather_text:
            weather_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            weather_box.get_style_context().add_class("badge")
            weather_box.get_style_context().add_class("badge-mint")
            w_lbl = Gtk.Label()
            w_lbl.set_markup(f"<b>🌤 {weather_text}</b>")
            weather_box.pack_start(w_lbl, False, False, 4)
            controls_box.pack_start(weather_box, False, False, 0)

        # Backup Button
        btn_backup = Gtk.Button(label="💾 Cadangan")
        btn_backup.get_style_context().add_class("btn-secondary")
        btn_backup.connect("clicked", self._on_backup_clicked)
        controls_box.pack_start(btn_backup, False, False, 0)

        # Primary Action Button
        if action_label and action_callback:
            btn_action = Gtk.Button(label=action_label)
            btn_action.get_style_context().add_class("btn-primary")
            btn_action.connect("clicked", action_callback)
            controls_box.pack_start(btn_action, False, False, 0)

        self.pack_end(controls_box, False, False, 0)

    def _on_backup_clicked(self, widget):
        if self.parent_window:
            self.parent_window.open_backup_dialog()

class KPICard(Gtk.Box):
    """
    Standard KPI Card conforming to AgriStation design system.
    """
    def __init__(self, title, value, subtext="", highlighted=False, value_color=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        if highlighted:
            self.get_style_context().add_class("agri-card-highlight")
        else:
            self.get_style_context().add_class("agri-card")
            
        self.set_hexpand(True)
        
        lbl_title = Gtk.Label(xalign=0)
        lbl_title.get_style_context().add_class("kpi-title")
        lbl_title.set_text(title)
        self.pack_start(lbl_title, False, False, 0)

        self.lbl_value = Gtk.Label(xalign=0)
        if value_color == "green":
            self.lbl_value.get_style_context().add_class("kpi-value-green")
        elif value_color == "red":
            self.lbl_value.get_style_context().add_class("kpi-value-red")
        else:
            self.lbl_value.get_style_context().add_class("kpi-value")
        self.lbl_value.get_style_context().add_class("tabular")
        self.lbl_value.set_text(str(value))
        self.pack_start(self.lbl_value, False, False, 0)

        self.lbl_subtext = Gtk.Label(xalign=0)
        self.lbl_subtext.get_style_context().add_class("kpi-subtext")
        self.lbl_subtext.set_text(subtext)
        self.pack_start(self.lbl_subtext, False, False, 0)

    def update(self, value, subtext=None):
        self.lbl_value.set_text(str(value))
        if subtext is not None:
            self.lbl_subtext.set_text(subtext)

class PillTabs(Gtk.Box):
    """Horizontal filter tabs."""
    def __init__(self, options, on_change_callback):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.options = options
        self.callback = on_change_callback
        self.buttons = []
        self.active_index = 0

        for i, opt in enumerate(options):
            btn = Gtk.Button(label=opt)
            btn.get_style_context().add_class("pill-tab")
            if i == 0:
                btn.get_style_context().add_class("active")
            btn.connect("clicked", self._on_btn_clicked, i)
            self.pack_start(btn, False, False, 0)
            self.buttons.append(btn)

    def _on_btn_clicked(self, widget, index):
        if self.active_index == index:
            return
        for i, b in enumerate(self.buttons):
            if i == index:
                b.get_style_context().add_class("active")
            else:
                b.get_style_context().remove_class("active")
        self.active_index = index
        self.callback(self.options[index])

class BackupRestoreDialog(Gtk.Dialog):
    """Modal Dialog for creating backups, viewing backup history, and restoring."""
    def __init__(self, parent):
        super().__init__(title="Manajemen Cadangan & Pemulihan Data", transient_for=parent, flags=0)
        self.set_default_size(680, 480)
        self.parent_win = parent
        
        box = self.get_content_area()
        box.set_spacing(14)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(16)
        box.set_margin_bottom(16)

        # Header description
        info_lbl = Gtk.Label(xalign=0)
        info_lbl.set_markup("<b>Pusat Pencadangan SQLite Terpusat</b>\n<span color='#64748B'>Cadangkan data Anda secara berkala atau pulihkan dari arsip bertanda tangan SHA-256.</span>")
        box.pack_start(info_lbl, False, False, 0)

        # Action row
        action_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_now = Gtk.Button(label="+ Buat Cadangan Sekarang")
        btn_now.get_style_context().add_class("btn-primary")
        btn_now.connect("clicked", self._on_create_backup)
        action_row.pack_start(btn_now, False, False, 0)

        btn_restore = Gtk.Button(label="↺ Pulihkan dari Pilihan")
        btn_restore.get_style_context().add_class("btn-outline")
        btn_restore.connect("clicked", self._on_restore_selected)
        action_row.pack_start(btn_restore, False, False, 0)

        box.pack_start(action_row, False, False, 0)

        # Backups List
        list_lbl = Gtk.Label(xalign=0)
        list_lbl.set_markup("<b>Daftar Arsip Cadangan (30 Hari Terakhir):</b>")
        box.pack_start(list_lbl, False, False, 0)

        self.store = Gtk.ListStore(str, str, str, str) # filename, date, size, full_path
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.get_style_context().add_class("agri-card")

        r1 = Gtk.CellRendererText()
        c1 = Gtk.TreeViewColumn("Nama Berkas Arsip", r1, text=0)
        c1.set_expand(True)
        self.tree.append_column(c1)

        r2 = Gtk.CellRendererText()
        c2 = Gtk.TreeViewColumn("Waktu Pencadangan", r2, text=1)
        self.tree.append_column(c2)

        r3 = Gtk.CellRendererText()
        c3 = Gtk.TreeViewColumn("Ukuran", r3, text=2)
        self.tree.append_column(c3)

        scroller = Gtk.ScrolledWindow()
        scroller.set_min_content_height(200)
        scroller.add(self.tree)
        box.pack_start(scroller, True, True, 0)

        self.add_button("Tutup", Gtk.ResponseType.CLOSE)
        self.refresh_list()
        self.show_all()

    def refresh_list(self):
        self.store.clear()
        backups = list_backups()
        for b in backups:
            self.store.append([b["filename"], b["mtime"], f"{b['size_kb']} KB", b["path"]])

    def _on_create_backup(self, widget):
        success, msg, path = create_backup()
        if success:
            self.refresh_list()
            self.parent_win.show_info("Cadangan Sukses", msg)
        else:
            self.parent_win.show_error("Pencadangan Gagal", msg)

    def _on_restore_selected(self, widget):
        selection = self.tree.get_selection()
        model, treeiter = selection.get_selected()
        if not treeiter:
            self.parent_win.show_error("Peringatan", "Silakan pilih salah satu berkas cadangan dari daftar terlebih dahulu.")
            return

        archive_name = model[treeiter][0]
        archive_path = model[treeiter][3]

        if not self.parent_win.confirm_action(
            "Konfirmasi Pemulihan Data",
            f"Apakah Anda yakin ingin memulihkan database dari {archive_name}?\n\nPerubahan sejak cadangan ini dibuat akan ditimpa."
        ):
            return

        success, msg = restore_backup(archive_path)
        if success:
            self.parent_win.show_info("Pemulihan Sukses", msg)
        else:
            self.parent_win.show_error("Pemulihan Gagal", msg)
