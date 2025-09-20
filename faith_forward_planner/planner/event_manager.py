"""
Event Manager - Handles CRUD operations for calendar events
Supports SQLite database backend with iCal compatibility
"""

import sqlite3
import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
try:
    from icalendar import Calendar, Event as iCalEvent, vDDDTypes
    ICAL_AVAILABLE = True
except ImportError:
    ICAL_AVAILABLE = False
    print("Warning: icalendar not available. iCal export will be disabled.")
import os


class Event:
    """Represents a calendar event."""
    
    def __init__(self, id=None, title="", description="", start_time=None, 
                 end_time=None, all_day=False, location="", recurrence=None,
                 reminder_minutes=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.all_day = all_day
        self.location = location
        self.recurrence = recurrence  # JSON string for recurrence rules
        self.reminder_minutes = reminder_minutes
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        
    def to_dict(self):
        """Convert event to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'all_day': self.all_day,
            'location': self.location,
            'recurrence': self.recurrence,
            'reminder_minutes': self.reminder_minutes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create event from dictionary."""
        event = cls()
        event.id = data.get('id')
        event.title = data.get('title', '')
        event.description = data.get('description', '')
        
        if data.get('start_time'):
            event.start_time = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            event.end_time = datetime.fromisoformat(data['end_time'])
            
        event.all_day = data.get('all_day', False)
        event.location = data.get('location', '')
        event.recurrence = data.get('recurrence')
        event.reminder_minutes = data.get('reminder_minutes')
        
        if data.get('created_at'):
            event.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            event.updated_at = datetime.fromisoformat(data['updated_at'])
            
        return event


class EventManager:
    """Manages calendar events with SQLite backend."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    all_day BOOLEAN DEFAULT FALSE,
                    location TEXT,
                    recurrence TEXT,
                    reminder_minutes INTEGER,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id TEXT PRIMARY KEY,
                    event_id TEXT,
                    reminder_time TEXT,
                    sent BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (event_id) REFERENCES events (id)
                )
            ''')
            
            conn.commit()
            
    def create_event(self, title: str, description: str = "", start_time: datetime = None,
                    end_time: datetime = None, all_day: bool = False, location: str = "",
                    recurrence: dict = None, reminder_minutes: int = None) -> str:
        """Create a new event."""
        event = Event(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            all_day=all_day,
            location=location,
            recurrence=json.dumps(recurrence) if recurrence else None,
            reminder_minutes=reminder_minutes
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO events (id, title, description, start_time, end_time,
                                  all_day, location, recurrence, reminder_minutes,
                                  created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.id, event.title, event.description,
                event.start_time.isoformat() if event.start_time else None,
                event.end_time.isoformat() if event.end_time else None,
                event.all_day, event.location, event.recurrence,
                event.reminder_minutes,
                event.created_at.isoformat(),
                event.updated_at.isoformat()
            ))
            
            # Create reminders if specified
            if reminder_minutes and start_time:
                self._create_reminder(conn, event.id, start_time - timedelta(minutes=reminder_minutes))
                
            conn.commit()
            
        return event.id
        
    def get_event(self, event_id: str) -> Optional[Event]:
        """Get a single event by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,))
            row = cursor.fetchone()
            
            if row:
                return Event.from_dict(dict(row))
                
        return None
        
    def get_events(self, start_date: datetime = None, end_date: datetime = None) -> List[Event]:
        """Get events within a date range."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if start_date and end_date:
                cursor = conn.execute('''
                    SELECT * FROM events 
                    WHERE (start_time >= ? AND start_time <= ?) 
                       OR (end_time >= ? AND end_time <= ?)
                       OR (start_time <= ? AND end_time >= ?)
                    ORDER BY start_time
                ''', (
                    start_date.isoformat(), end_date.isoformat(),
                    start_date.isoformat(), end_date.isoformat(),
                    start_date.isoformat(), end_date.isoformat()
                ))
            else:
                cursor = conn.execute('SELECT * FROM events ORDER BY start_time')
                
            return [Event.from_dict(dict(row)) for row in cursor.fetchall()]
            
    def update_event(self, event_id: str, **kwargs) -> bool:
        """Update an existing event."""
        event = self.get_event(event_id)
        if not event:
            return False
            
        # Update fields
        for key, value in kwargs.items():
            if hasattr(event, key):
                setattr(event, key, value)
                
        event.updated_at = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE events SET title=?, description=?, start_time=?, end_time=?,
                                all_day=?, location=?, recurrence=?, reminder_minutes=?,
                                updated_at=?
                WHERE id=?
            ''', (
                event.title, event.description,
                event.start_time.isoformat() if event.start_time else None,
                event.end_time.isoformat() if event.end_time else None,
                event.all_day, event.location, event.recurrence,
                event.reminder_minutes, event.updated_at.isoformat(),
                event_id
            ))
            conn.commit()
            
        return True
        
    def delete_event(self, event_id: str) -> bool:
        """Delete an event."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
            conn.execute('DELETE FROM reminders WHERE event_id = ?', (event_id,))
            conn.commit()
            return cursor.rowcount > 0
            
    def search_events(self, query: str) -> List[Event]:
        """Search events by title, description, or location."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM events 
                WHERE title LIKE ? OR description LIKE ? OR location LIKE ?
                ORDER BY start_time
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            
            return [Event.from_dict(dict(row)) for row in cursor.fetchall()]
            
    def get_events_for_date(self, date_obj: datetime) -> List[Event]:
        """Get all events for a specific date."""
        start_of_day = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        return self.get_events(start_of_day, end_of_day)
        
    def reschedule_event(self, event_id: str, new_start: datetime, new_end: datetime = None) -> bool:
        """Reschedule an event (for drag-and-drop functionality)."""
        event = self.get_event(event_id)
        if not event:
            return False
            
        # Calculate duration if end time not specified
        if new_end is None and event.start_time and event.end_time:
            duration = event.end_time - event.start_time
            new_end = new_start + duration
            
        return self.update_event(event_id, start_time=new_start, end_time=new_end)
        
    def generate_recurring_events(self, event_id: str, until_date: datetime = None) -> List[str]:
        """Generate recurring events based on recurrence rules."""
        event = self.get_event(event_id)
        if not event or not event.recurrence:
            return []
            
        try:
            recurrence = json.loads(event.recurrence)
        except (json.JSONDecodeError, TypeError):
            return []
            
        created_events = []
        frequency = recurrence.get('frequency', 'daily')
        interval = recurrence.get('interval', 1)
        count = recurrence.get('count', 10)
        
        if not event.start_time:
            return []
            
        current_start = event.start_time
        current_end = event.end_time
        
        for i in range(1, count + 1):
            if frequency == 'daily':
                next_start = current_start + timedelta(days=interval)
                next_end = current_end + timedelta(days=interval) if current_end else None
            elif frequency == 'weekly':
                next_start = current_start + timedelta(weeks=interval)
                next_end = current_end + timedelta(weeks=interval) if current_end else None
            elif frequency == 'monthly':
                # Simple monthly recurrence (same day of month)
                if current_start.month == 12:
                    next_month = 1
                    next_year = current_start.year + 1
                else:
                    next_month = current_start.month + interval
                    next_year = current_start.year
                    
                try:
                    next_start = current_start.replace(month=next_month, year=next_year)
                    next_end = current_end.replace(month=next_month, year=next_year) if current_end else None
                except ValueError:
                    break  # Invalid date (e.g., Feb 31)
            else:
                break
                
            if until_date and next_start > until_date:
                break
                
            new_event_id = self.create_event(
                title=event.title,
                description=event.description,
                start_time=next_start,
                end_time=next_end,
                all_day=event.all_day,
                location=event.location,
                reminder_minutes=event.reminder_minutes
            )
            created_events.append(new_event_id)
            
            current_start = next_start
            current_end = next_end
            
        return created_events
        
    def export_to_ical(self) -> str:
        """Export all events to iCal format."""
        if not ICAL_AVAILABLE:
            raise ImportError("icalendar package is required for iCal export")
            
        cal = Calendar()
        cal.add('prodid', '-//Faith Forward Planner//mxm.dk//')
        cal.add('version', '2.0')
        
        events = self.get_events()
        
        for event in events:
            ical_event = iCalEvent()
            ical_event.add('uid', event.id)
            ical_event.add('summary', event.title)
            ical_event.add('description', event.description)
            
            if event.start_time:
                ical_event.add('dtstart', event.start_time)
            if event.end_time:
                ical_event.add('dtend', event.end_time)
            if event.location:
                ical_event.add('location', event.location)
                
            ical_event.add('created', event.created_at)
            ical_event.add('last-modified', event.updated_at)
            
            cal.add_component(ical_event)
            
        return cal.to_ical().decode('utf-8')
        
    def _create_reminder(self, conn, event_id: str, reminder_time: datetime):
        """Create a reminder for an event."""
        reminder_id = str(uuid.uuid4())
        conn.execute('''
            INSERT INTO reminders (id, event_id, reminder_time, sent)
            VALUES (?, ?, ?, ?)
        ''', (reminder_id, event_id, reminder_time.isoformat(), False))
        
    def get_pending_reminders(self) -> List[Dict[str, Any]]:
        """Get all pending reminders that should be triggered."""
        now = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT r.id, r.event_id, r.reminder_time, e.title, e.description
                FROM reminders r
                JOIN events e ON r.event_id = e.id
                WHERE r.sent = FALSE AND r.reminder_time <= ?
                ORDER BY r.reminder_time
            ''', (now.isoformat(),))
            
            return [dict(row) for row in cursor.fetchall()]
            
    def mark_reminder_sent(self, reminder_id: str):
        """Mark a reminder as sent."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('UPDATE reminders SET sent = TRUE WHERE id = ?', (reminder_id,))
            conn.commit()