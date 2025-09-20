#!/usr/bin/env python3
"""
Faith Forward Planner - Main Application
A GTK-based calendar application with faith-focused features.
"""

import sys
import os
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib
import sqlite3
from datetime import datetime, date
import threading

# Import our modules
from .calendar_view import CalendarView
from .event_manager import EventManager
from .reflection_widget import ReflectionWidget
from .nlp_parser import NLPParser
from .time_blocker import TimeBlocker
from .exporter import Exporter


class FaithForwardPlanner(Adw.Application):
    """Main application class for Faith Forward Planner."""
    
    def __init__(self):
        super().__init__(application_id='org.faithforward.planner')
        self.window = None
        self.event_manager = None
        self.calendar_view = None
        self.reflection_widget = None
        self.nlp_parser = None
        self.time_blocker = None
        self.exporter = None
        
        # Connect startup signal
        self.connect('activate', self.on_activate)
        
    def on_activate(self, app):
        """Called when the application is activated."""
        if not self.window:
            self.create_window()
        self.window.present()
        
    def create_window(self):
        """Create the main application window."""
        # Initialize components
        self.initialize_components()
        
        # Create main window
        self.window = Adw.ApplicationWindow(application=self)
        self.window.set_title("Faith Forward Planner")
        self.window.set_default_size(1200, 800)
        
        # Create header bar
        header_bar = self.create_header_bar()
        self.window.set_titlebar(header_bar)
        
        # Create main content
        main_content = self.create_main_content()
        self.window.set_content(main_content)
        
        # Load CSS styling
        self.load_css()
        
    def initialize_components(self):
        """Initialize all application components."""
        # Initialize database
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'planner.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize components
        self.event_manager = EventManager(db_path)
        self.nlp_parser = NLPParser()
        self.time_blocker = TimeBlocker(self.event_manager)
        self.exporter = Exporter(self.event_manager)
        self.reflection_widget = ReflectionWidget()
        self.calendar_view = CalendarView(self.event_manager, self.nlp_parser, self.time_blocker)
        
    def create_header_bar(self):
        """Create the header bar with Faith Forward branding."""
        header_bar = Adw.HeaderBar()
        
        # Faith Forward title
        title_widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        title_label = Gtk.Label(label="Faith Forward Planner")
        title_label.add_css_class("faith-forward-logo")
        motto_label = Gtk.Label(label="Spiritus Invictus - The Unconquered Spirit")
        motto_label.add_css_class("faith-forward-motto")
        
        title_widget.append(title_label)
        title_widget.append(motto_label)
        header_bar.set_title_widget(title_widget)
        
        # Export menu button
        export_button = Gtk.MenuButton()
        export_button.set_icon_name("document-save-symbolic")
        export_button.set_tooltip_text("Export Calendar")
        
        export_menu = Gio.Menu()
        export_menu.append("Export to Markdown", "app.export_markdown")
        export_menu.append("Export to EPUB", "app.export_epub")
        export_button.set_menu_model(export_menu)
        
        header_bar.pack_end(export_button)
        
        # View selector
        view_selector = Gtk.ComboBoxText()
        view_selector.append("month", "Month View")
        view_selector.append("week", "Week View") 
        view_selector.append("day", "Day View")
        view_selector.set_active(0)
        view_selector.connect("changed", self.on_view_changed)
        
        header_bar.pack_start(view_selector)
        
        # Setup export actions
        self.setup_actions()
        
        return header_bar
        
    def setup_actions(self):
        """Setup application actions."""
        export_markdown_action = Gio.SimpleAction.new("export_markdown", None)
        export_markdown_action.connect("activate", self.on_export_markdown)
        self.add_action(export_markdown_action)
        
        export_epub_action = Gio.SimpleAction.new("export_epub", None)
        export_epub_action.connect("activate", self.on_export_epub)
        self.add_action(export_epub_action)
        
    def create_main_content(self):
        """Create the main content area."""
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        # Left sidebar with reflection widget
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar.set_size_request(300, -1)
        sidebar.add_css_class("sidebar")
        
        # Daily reflection widget
        reflection_frame = Gtk.Frame()
        reflection_frame.set_child(self.reflection_widget.get_widget())
        sidebar.append(reflection_frame)
        
        # Add some spacing
        sidebar.append(Gtk.Separator())
        
        # Quick add event section
        quick_add_frame = Gtk.Frame()
        quick_add_frame.set_label("Quick Add Event")
        quick_add_box = self.create_quick_add_widget()
        quick_add_frame.set_child(quick_add_box)
        sidebar.append(quick_add_frame)
        
        # Main calendar area
        calendar_frame = Gtk.Frame()
        calendar_frame.set_child(self.calendar_view.get_widget())
        
        # Add to main box
        main_box.append(sidebar)
        main_box.append(Gtk.Separator())
        main_box.append(calendar_frame)
        
        return main_box
        
    def create_quick_add_widget(self):
        """Create quick add event widget."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        
        # Natural language input
        self.quick_entry = Gtk.Entry()
        self.quick_entry.set_placeholder_text("e.g., 'Meeting tomorrow at 2pm' or 'Lunch next Friday'")
        self.quick_entry.connect("activate", self.on_quick_add)
        box.append(self.quick_entry)
        
        # Add button
        add_button = Gtk.Button(label="Add Event")
        add_button.add_css_class("suggested-action")
        add_button.connect("clicked", self.on_quick_add)
        box.append(add_button)
        
        return box
        
    def load_css(self):
        """Load CSS styling."""
        css_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'style.css')
        if os.path.exists(css_path):
            css_provider = Gtk.CssProvider()
            css_provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_display(
                self.window.get_display(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            
    def on_view_changed(self, combo):
        """Handle view change."""
        view_type = combo.get_active_id()
        if self.calendar_view:
            self.calendar_view.set_view_type(view_type)
            
    def on_quick_add(self, widget):
        """Handle quick add event."""
        text = self.quick_entry.get_text().strip()
        if text:
            try:
                # Parse natural language input
                event_data = self.nlp_parser.parse_event(text)
                if event_data:
                    # Create event
                    self.event_manager.create_event(**event_data)
                    self.calendar_view.refresh()
                    self.quick_entry.set_text("")
                    
                    # Show success message
                    self.show_toast("Event added successfully!")
                else:
                    self.show_toast("Could not parse event. Try a different format.")
            except Exception as e:
                self.show_toast(f"Error adding event: {str(e)}")
                
    def on_export_markdown(self, action, param):
        """Export calendar to Markdown."""
        threading.Thread(target=self._export_markdown_thread, daemon=True).start()
        
    def on_export_epub(self, action, param):
        """Export calendar to EPUB."""
        threading.Thread(target=self._export_epub_thread, daemon=True).start()
        
    def _export_markdown_thread(self):
        """Export to Markdown in background thread."""
        try:
            filename = self.exporter.export_to_markdown()
            GLib.idle_add(self.show_toast, f"Exported to {filename}")
        except Exception as e:
            GLib.idle_add(self.show_toast, f"Export failed: {str(e)}")
            
    def _export_epub_thread(self):
        """Export to EPUB in background thread."""
        try:
            filename = self.exporter.export_to_epub()
            GLib.idle_add(self.show_toast, f"Exported to {filename}")
        except Exception as e:
            GLib.idle_add(self.show_toast, f"Export failed: {str(e)}")
            
    def show_toast(self, message):
        """Show a toast notification."""
        if hasattr(self.window, 'add_toast'):
            toast = Adw.Toast()
            toast.set_title(message)
            self.window.add_toast(toast)
        else:
            print(f"Toast: {message}")


def main():
    """Main entry point."""
    app = FaithForwardPlanner()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())