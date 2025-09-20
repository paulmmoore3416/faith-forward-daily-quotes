"""
Calendar View - GTK-based calendar interface with multiple view modes
Supports monthly, weekly, and daily views with drag-and-drop functionality
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GObject, Gdk, Pango
from datetime import datetime, timedelta, date
import calendar
from typing import List, Optional, Dict, Any
from .event_manager import EventManager, Event
from .nlp_parser import NLPParser
from .time_blocker import TimeBlocker


class CalendarView:
    """Main calendar view widget with multiple display modes."""
    
    def __init__(self, event_manager: EventManager, nlp_parser: NLPParser, time_blocker: TimeBlocker):
        self.event_manager = event_manager
        self.nlp_parser = nlp_parser
        self.time_blocker = time_blocker
        self.current_date = datetime.now()
        self.view_type = "month"  # month, week, day
        self.selected_date = None
        
        self.main_widget = self._create_widget()
        self.drag_source_event = None
        
    def get_widget(self) -> Gtk.Widget:
        """Get the main calendar widget."""
        return self.main_widget
        
    def _create_widget(self) -> Gtk.Widget:
        """Create the main calendar widget."""
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Create calendar header with navigation
        self.header = self._create_header()
        self.main_box.append(self.header)
        
        # Create scrolled window for calendar content
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled.set_vexpand(True)
        
        # Create calendar content
        self.calendar_content = self._create_calendar_content()
        self.scrolled.set_child(self.calendar_content)
        
        self.main_box.append(self.scrolled)
        
        return self.main_box
        
    def _create_header(self) -> Gtk.Widget:
        """Create calendar header with navigation and controls."""
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.add_css_class("calendar-header")
        header_box.set_margin_top(5)
        header_box.set_margin_bottom(5)
        header_box.set_margin_start(10)
        header_box.set_margin_end(10)
        
        # Previous button
        prev_button = Gtk.Button()
        prev_button.set_icon_name("go-previous-symbolic")
        prev_button.connect("clicked", self._on_prev_clicked)
        header_box.append(prev_button)
        
        # Current date/period label
        self.date_label = Gtk.Label()
        self.date_label.set_hexpand(True)
        self.date_label.set_halign(Gtk.Align.CENTER)
        self.date_label.add_css_class("calendar-header-label")
        self._update_date_label()
        header_box.append(self.date_label)
        
        # Next button
        next_button = Gtk.Button()
        next_button.set_icon_name("go-next-symbolic")
        next_button.connect("clicked", self._on_next_clicked)
        header_box.append(next_button)
        
        # Today button
        today_button = Gtk.Button(label="Today")
        today_button.connect("clicked", self._on_today_clicked)
        header_box.append(today_button)
        
        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search events...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        header_box.append(self.search_entry)
        
        return header_box
        
    def _create_calendar_content(self) -> Gtk.Widget:
        """Create calendar content based on current view type."""
        if self.view_type == "month":
            return self._create_month_view()
        elif self.view_type == "week":
            return self._create_week_view()
        elif self.view_type == "day":
            return self._create_day_view()
        else:
            return self._create_month_view()
            
    def _create_month_view(self) -> Gtk.Widget:
        """Create monthly calendar view."""
        grid = Gtk.Grid()
        grid.set_row_homogeneous(True)
        grid.set_column_homogeneous(True)
        grid.set_row_spacing(1)
        grid.set_column_spacing(1)
        
        # Add day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            header = Gtk.Label(label=day)
            header.add_css_class("calendar-day-header")
            header.set_size_request(-1, 30)
            grid.attach(header, i, 0, 1, 1)
            
        # Get calendar data
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Add calendar days
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell for days from other months
                    empty_cell = Gtk.Frame()
                    empty_cell.add_css_class("calendar-empty-day")
                    grid.attach(empty_cell, day_num, week_num + 1, 1, 1)
                else:
                    day_widget = self._create_day_widget(day, week_num + 1, day_num)
                    grid.attach(day_widget, day_num, week_num + 1, 1, 1)
                    
        return grid
        
    def _create_week_view(self) -> Gtk.Widget:
        """Create weekly calendar view."""
        grid = Gtk.Grid()
        grid.set_row_spacing(1)
        grid.set_column_spacing(1)
        
        # Get week start (Monday)
        days_from_monday = self.current_date.weekday()
        week_start = self.current_date - timedelta(days=days_from_monday)
        
        # Time column
        time_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        time_column.set_size_request(60, -1)
        
        # Add time labels
        for hour in range(24):
            time_label = Gtk.Label(label=f"{hour:02d}:00")
            time_label.set_size_request(-1, 60)
            time_label.add_css_class("time-label")
            time_column.append(time_label)
            
        grid.attach(time_column, 0, 1, 1, 1)
        
        # Day columns
        for i in range(7):
            day_date = week_start + timedelta(days=i)
            day_column = self._create_week_day_column(day_date)
            
            # Day header
            day_header = Gtk.Label(label=f"{day_date.strftime('%a %d')}")
            day_header.add_css_class("calendar-day-header")
            day_header.set_size_request(150, 30)
            grid.attach(day_header, i + 1, 0, 1, 1)
            
            # Day column
            grid.attach(day_column, i + 1, 1, 1, 1)
            
        return grid
        
    def _create_day_view(self) -> Gtk.Widget:
        """Create daily calendar view."""
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        # Time column
        time_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        time_column.set_size_request(80, -1)
        
        for hour in range(24):
            time_label = Gtk.Label(label=f"{hour:02d}:00")
            time_label.set_size_request(-1, 60)
            time_label.add_css_class("time-label")
            time_column.append(time_label)
            
        main_box.append(time_column)
        
        # Day content
        day_content = self._create_day_content(self.current_date)
        main_box.append(day_content)
        
        return main_box
        
    def _create_day_widget(self, day: int, row: int, col: int) -> Gtk.Widget:
        """Create a widget for a single day in month view."""
        day_date = date(self.current_date.year, self.current_date.month, day)
        today = date.today()
        
        frame = Gtk.Frame()
        frame.set_size_request(150, 120)
        
        # Add CSS classes
        if day_date == today:
            frame.add_css_class("calendar-day-today")
        else:
            frame.add_css_class("calendar-day")
            
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_margin_top(5)
        box.set_margin_bottom(5)
        box.set_margin_start(5)
        box.set_margin_end(5)
        
        # Day number
        day_label = Gtk.Label(label=str(day))
        day_label.set_halign(Gtk.Align.START)
        day_label.add_css_class("calendar-day-number")
        box.append(day_label)
        
        # Events for this day
        events = self.event_manager.get_events_for_date(
            datetime.combine(day_date, datetime.min.time())
        )
        
        for event in events[:3]:  # Show up to 3 events
            event_widget = self._create_event_widget(event, compact=True)
            box.append(event_widget)
            
        if len(events) > 3:
            more_label = Gtk.Label(label=f"+{len(events) - 3} more")
            more_label.add_css_class("calendar-more-events")
            box.append(more_label)
            
        frame.set_child(box)
        
        # Add click handler
        click_gesture = Gtk.GestureClick()
        click_gesture.connect("pressed", self._on_day_clicked, day_date)
        frame.add_controller(click_gesture)
        
        # Add drop target for drag-and-drop
        drop_target = Gtk.DropTarget()
        drop_target.set_gtypes([str])  # Accept text data
        drop_target.connect("drop", self._on_event_dropped, day_date)
        frame.add_controller(drop_target)
        
        return frame
        
    def _create_week_day_column(self, day_date: datetime) -> Gtk.Widget:
        """Create a day column for week view."""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_size_request(150, 1440)  # 24 hours * 60 pixels
        
        overlay = Gtk.Overlay()
        
        # Background grid for hours
        grid = Gtk.Grid()
        grid.set_row_spacing(0)
        
        for hour in range(24):
            hour_frame = Gtk.Frame()
            hour_frame.set_size_request(-1, 60)
            hour_frame.add_css_class("calendar-hour-slot")
            grid.attach(hour_frame, 0, hour, 1, 1)
            
        overlay.set_child(grid)
        
        # Events overlay
        events = self.event_manager.get_events_for_date(day_date)
        for event in events:
            if event.start_time:
                event_widget = self._create_timed_event_widget(event)
                overlay.add_overlay(event_widget)
                
        scrolled.set_child(overlay)
        return scrolled
        
    def _create_day_content(self, day_date: datetime) -> Gtk.Widget:
        """Create content for day view."""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_hexpand(True)
        
        overlay = Gtk.Overlay()
        
        # Background grid for hours
        grid = Gtk.Grid()
        grid.set_row_spacing(0)
        
        for hour in range(24):
            hour_frame = Gtk.Frame()
            hour_frame.set_size_request(-1, 60)
            hour_frame.add_css_class("calendar-hour-slot")
            
            # Add hour label
            hour_label = Gtk.Label(label=f"{hour:02d}:00")
            hour_label.set_halign(Gtk.Align.START)
            hour_label.set_valign(Gtk.Align.START)
            hour_label.add_css_class("hour-label-inline")
            hour_frame.set_child(hour_label)
            
            grid.attach(hour_frame, 0, hour, 1, 1)
            
        overlay.set_child(grid)
        
        # Events overlay
        events = self.event_manager.get_events_for_date(day_date)
        for event in events:
            if event.start_time:
                event_widget = self._create_timed_event_widget(event)
                overlay.add_overlay(event_widget)
                
        scrolled.set_child(overlay)
        return scrolled
        
    def _create_event_widget(self, event: Event, compact: bool = False) -> Gtk.Widget:
        """Create a widget for displaying an event."""
        if compact:
            # Compact view for month view
            button = Gtk.Button()
            button.set_label(event.title[:20] + "..." if len(event.title) > 20 else event.title)
            button.add_css_class("calendar-event-compact")
            button.set_size_request(-1, 20)
            button.connect("clicked", self._on_event_clicked, event)
            
            # Add drag source
            drag_source = Gtk.DragSource()
            drag_source.set_content(Gdk.ContentProvider.new_for_value(event.id))
            drag_source.connect("prepare", self._on_drag_prepare, event)
            button.add_controller(drag_source)
            
            return button
        else:
            # Full view for week/day views
            frame = Gtk.Frame()
            frame.add_css_class("calendar-event-full")
            
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            box.set_margin_top(2)
            box.set_margin_bottom(2)
            box.set_margin_start(4)
            box.set_margin_end(4)
            
            # Title
            title_label = Gtk.Label(label=event.title)
            title_label.set_halign(Gtk.Align.START)
            title_label.add_css_class("event-title")
            box.append(title_label)
            
            # Time
            if event.start_time and not event.all_day:
                time_text = event.start_time.strftime("%H:%M")
                if event.end_time:
                    time_text += f" - {event.end_time.strftime('%H:%M')}"
                time_label = Gtk.Label(label=time_text)
                time_label.set_halign(Gtk.Align.START)
                time_label.add_css_class("event-time")
                box.append(time_label)
                
            # Location
            if event.location:
                location_label = Gtk.Label(label=f"📍 {event.location}")
                location_label.set_halign(Gtk.Align.START)
                location_label.add_css_class("event-location")
                box.append(location_label)
                
            frame.set_child(box)
            
            # Add click handler
            click_gesture = Gtk.GestureClick()
            click_gesture.connect("pressed", self._on_event_clicked, event)
            frame.add_controller(click_gesture)
            
            # Add drag source
            drag_source = Gtk.DragSource()
            drag_source.set_content(Gdk.ContentProvider.new_for_value(event.id))
            drag_source.connect("prepare", self._on_drag_prepare, event)
            frame.add_controller(drag_source)
            
            return frame
            
    def _create_timed_event_widget(self, event: Event) -> Gtk.Widget:
        """Create a positioned event widget for timed views."""
        widget = self._create_event_widget(event, compact=False)
        
        if event.start_time and not event.all_day:
            # Calculate position and size
            start_hour = event.start_time.hour
            start_minute = event.start_time.minute
            y_position = start_hour * 60 + start_minute
            
            if event.end_time:
                end_hour = event.end_time.hour
                end_minute = event.end_time.minute
                height = (end_hour * 60 + end_minute) - y_position
            else:
                height = 60  # Default 1 hour
                
            widget.set_size_request(-1, height)
            widget.set_margin_top(y_position)
            
        return widget
        
    def _update_date_label(self):
        """Update the date label in the header."""
        if self.view_type == "month":
            text = self.current_date.strftime("%B %Y")
        elif self.view_type == "week":
            # Show week range
            days_from_monday = self.current_date.weekday()
            week_start = self.current_date - timedelta(days=days_from_monday)
            week_end = week_start + timedelta(days=6)
            text = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
        elif self.view_type == "day":
            text = self.current_date.strftime("%A, %B %d, %Y")
        else:
            text = self.current_date.strftime("%B %Y")
            
        self.date_label.set_text(text)
        
    def _on_prev_clicked(self, button):
        """Navigate to previous period."""
        if self.view_type == "month":
            # Previous month
            if self.current_date.month == 1:
                self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        elif self.view_type == "week":
            self.current_date -= timedelta(weeks=1)
        elif self.view_type == "day":
            self.current_date -= timedelta(days=1)
            
        self.refresh()
        
    def _on_next_clicked(self, button):
        """Navigate to next period."""
        if self.view_type == "month":
            # Next month
            if self.current_date.month == 12:
                self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        elif self.view_type == "week":
            self.current_date += timedelta(weeks=1)
        elif self.view_type == "day":
            self.current_date += timedelta(days=1)
            
        self.refresh()
        
    def _on_today_clicked(self, button):
        """Navigate to today."""
        self.current_date = datetime.now()
        self.refresh()
        
    def _on_search_changed(self, entry):
        """Handle search text changes."""
        search_text = entry.get_text().strip()
        if search_text:
            # Perform search and highlight results
            # For now, just refresh the view
            self.refresh()
            
    def _on_day_clicked(self, gesture, n_press, x, y, day_date):
        """Handle day click."""
        self.selected_date = day_date
        
        if n_press == 2:  # Double click
            # Switch to day view for this date
            self.current_date = datetime.combine(day_date, datetime.min.time())
            self.set_view_type("day")
        else:
            # Show day events or create new event dialog
            self._show_day_events_dialog(day_date)
            
    def _on_event_clicked(self, gesture_or_button, event_or_none=None, event=None):
        """Handle event click."""
        if event is None:
            event = event_or_none
        self._show_event_details_dialog(event)
        
    def _on_drag_prepare(self, drag_source, x, y, event):
        """Prepare drag operation."""
        self.drag_source_event = event
        return Gdk.ContentProvider.new_for_value(event.id)
        
    def _on_event_dropped(self, drop_target, value, x, y, target_date):
        """Handle event drop."""
        if self.drag_source_event:
            # Reschedule event to target date
            new_start = datetime.combine(target_date, self.drag_source_event.start_time.time()) if self.drag_source_event.start_time else datetime.combine(target_date, datetime.min.time())
            
            if self.event_manager.reschedule_event(self.drag_source_event.id, new_start):
                self.refresh()
                return True
                
        return False
        
    def _show_day_events_dialog(self, day_date):
        """Show events for a specific day."""
        # This would open a dialog showing all events for the day
        # For now, we'll just print the events
        events = self.event_manager.get_events_for_date(
            datetime.combine(day_date, datetime.min.time())
        )
        print(f"Events for {day_date}: {[e.title for e in events]}")
        
    def _show_event_details_dialog(self, event):
        """Show event details dialog."""
        # This would open a dialog for editing event details
        # For now, we'll just print the event
        print(f"Event details: {event.title}")
        
    def set_view_type(self, view_type: str):
        """Change the calendar view type."""
        if view_type in ["month", "week", "day"]:
            self.view_type = view_type
            self.refresh()
            
    def refresh(self):
        """Refresh the calendar view."""
        # Remove old content
        old_content = self.scrolled.get_child()
        if old_content:
            self.scrolled.set_child(None)
            
        # Create new content
        new_content = self._create_calendar_content()
        self.scrolled.set_child(new_content)
        
        # Update header
        self._update_date_label()
        
    def get_selected_date(self) -> Optional[date]:
        """Get the currently selected date."""
        return self.selected_date