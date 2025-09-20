"""
Exporter - Export calendar data to EPUB and Markdown formats
Provides modular export functionality for weekly plans and calendar data
"""

import os
import json
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Any

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("Warning: markdown not available. Markdown export will be disabled.")
    
from .event_manager import EventManager, Event

try:
    from ebooklib import epub
    EPUB_AVAILABLE = True
except ImportError:
    EPUB_AVAILABLE = False
    print("Warning: ebooklib not available. EPUB export will be disabled.")


class Exporter:
    """Export calendar data to various formats."""
    
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.export_dir = os.path.expanduser("~/Documents/FaithForwardPlanner/Exports")
        os.makedirs(self.export_dir, exist_ok=True)
        
    def export_to_markdown(self, start_date: datetime = None, 
                          end_date: datetime = None,
                          include_reflection: bool = True) -> str:
        """Export calendar events to Markdown format."""
        if not MARKDOWN_AVAILABLE:
            print("Warning: markdown package not available, creating plain text export")
            
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=7)
            
        events = self.event_manager.get_events(start_date, end_date)
        
        # Generate filename
        filename = f"faith_forward_planner_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.md"
        filepath = os.path.join(self.export_dir, filename)
        
        # Generate markdown content
        markdown_content = self._generate_markdown_content(
            events, start_date, end_date, include_reflection
        )
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        return filepath
        
    def export_to_epub(self, start_date: datetime = None, 
                      end_date: datetime = None,
                      include_reflection: bool = True) -> str:
        """Export calendar events to EPUB format."""
        if not EPUB_AVAILABLE:
            raise ImportError("ebooklib is required for EPUB export")
            
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=7)
            
        events = self.event_manager.get_events(start_date, end_date)
        
        # Generate filename
        filename = f"faith_forward_planner_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.epub"
        filepath = os.path.join(self.export_dir, filename)
        
        # Create EPUB book
        book = self._create_epub_book(events, start_date, end_date, include_reflection)
        
        # Write EPUB file
        epub.write_epub(filepath, book, {})
        
        return filepath
        
    def export_week_plan(self, week_start_date: datetime = None) -> Dict[str, str]:
        """Export a complete weekly plan in both Markdown and EPUB formats."""
        if week_start_date is None:
            # Get start of current week (Monday)
            today = datetime.now()
            days_from_monday = today.weekday()
            week_start_date = today - timedelta(days=days_from_monday)
            
        week_end_date = week_start_date + timedelta(days=6)
        
        results = {}
        
        # Export to Markdown
        try:
            markdown_file = self.export_to_markdown(week_start_date, week_end_date)
            results['markdown'] = markdown_file
        except Exception as e:
            results['markdown_error'] = str(e)
            
        # Export to EPUB
        try:
            epub_file = self.export_to_epub(week_start_date, week_end_date)
            results['epub'] = epub_file
        except Exception as e:
            results['epub_error'] = str(e)
            
        return results
        
    def _generate_markdown_content(self, events: List[Event], 
                                 start_date: datetime, end_date: datetime,
                                 include_reflection: bool) -> str:
        """Generate Markdown content for the calendar export."""
        content = []
        
        # Header
        content.append("# Faith Forward Planner")
        content.append("*Spiritus Invictus - The Unconquered Spirit*")
        content.append("")
        content.append(f"**Export Period:** {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}")
        content.append("")
        
        # Daily reflection section
        if include_reflection:
            content.append("## Daily Reflection")
            content.append("")
            content.append("> *Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go.*")
            content.append("> **— Joshua 1:9**")
            content.append("")
            content.append("---")
            content.append("")
            
        # Group events by date
        events_by_date = self._group_events_by_date(events)
        
        # Generate content for each day
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            day_events = events_by_date.get(current_date, [])
            
            # Day header
            day_name = current_date.strftime("%A")
            full_date = current_date.strftime("%B %d, %Y")
            content.append(f"## {day_name}, {full_date}")
            content.append("")
            
            if day_events:
                # Sort events by start time
                day_events.sort(key=lambda e: e.start_time if e.start_time else datetime.min)
                
                for event in day_events:
                    content.append(self._format_event_markdown(event))
                    content.append("")
            else:
                content.append("*No events scheduled*")
                content.append("")
                
            content.append("---")
            content.append("")
            
            current_date += timedelta(days=1)
            
        # Summary section
        content.append("## Weekly Summary")
        content.append("")
        content.append(f"**Total Events:** {len(events)}")
        
        # Event count by day
        content.append("")
        content.append("### Events by Day")
        for date_key, date_events in events_by_date.items():
            day_name = date_key.strftime("%A")
            content.append(f"- {day_name}: {len(date_events)} events")
            
        content.append("")
        
        # Event types
        event_types = self._analyze_event_types(events)
        if event_types:
            content.append("### Event Types")
            for event_type, count in event_types.items():
                content.append(f"- {event_type.title()}: {count}")
            content.append("")
            
        # Footer
        content.append("---")
        content.append("")
        content.append("*Generated by Faith Forward Planner*")
        content.append("*Faith Forward Community - Helping people realize unlimited possibilities*")
        content.append("")
        content.append("**Spiritus Invictus**")
        
        return "\n".join(content)
        
    def _create_epub_book(self, events: List[Event], 
                         start_date: datetime, end_date: datetime,
                         include_reflection: bool):
        """Create an EPUB book from calendar events."""
        if not EPUB_AVAILABLE:
            raise ImportError("ebooklib is required for EPUB export")
            
        book = epub.EpubBook()
        
        # Set metadata
        book.set_identifier('faith-forward-planner-' + start_date.strftime('%Y%m%d'))
        book.set_title(f'Faith Forward Planner - {start_date.strftime("%b %d")} to {end_date.strftime("%b %d, %Y")}')
        book.set_language('en')
        book.add_author('Faith Forward Community')
        
        # Create cover page
        cover_html = self._create_epub_cover(start_date, end_date)
        cover_chapter = epub.EpubHtml(title='Cover', file_name='cover.xhtml', lang='en')
        cover_chapter.content = cover_html
        book.add_item(cover_chapter)
        
        # Create daily reflection chapter
        if include_reflection:
            reflection_html = self._create_epub_reflection()
            reflection_chapter = epub.EpubHtml(title='Daily Reflection', file_name='reflection.xhtml', lang='en')
            reflection_chapter.content = reflection_html
            book.add_item(reflection_chapter)
            
        # Group events by date and create chapters
        events_by_date = self._group_events_by_date(events)
        chapters = [cover_chapter]
        if include_reflection:
            chapters.append(reflection_chapter)
            
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            day_events = events_by_date.get(current_date, [])
            
            # Create chapter for this day
            day_html = self._create_epub_day_chapter(current_date, day_events)
            day_name = current_date.strftime("%A")
            day_chapter = epub.EpubHtml(
                title=f'{day_name}, {current_date.strftime("%b %d")}',
                file_name=f'day_{current_date.strftime("%Y%m%d")}.xhtml',
                lang='en'
            )
            day_chapter.content = day_html
            book.add_item(day_chapter)
            chapters.append(day_chapter)
            
            current_date += timedelta(days=1)
            
        # Create summary chapter
        summary_html = self._create_epub_summary(events, events_by_date)
        summary_chapter = epub.EpubHtml(title='Weekly Summary', file_name='summary.xhtml', lang='en')
        summary_chapter.content = summary_html
        book.add_item(summary_chapter)
        chapters.append(summary_chapter)
        
        # Add default NCX and Nav files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Create spine
        book.spine = ['nav'] + chapters
        
        # Add CSS
        style = '''
            body { font-family: Georgia, serif; margin: 2em; }
            h1, h2, h3 { color: #4a90e2; }
            .reflection { background: #f8f9fa; padding: 1em; border-left: 4px solid #4a90e2; }
            .event { background: #f0f8ff; padding: 0.5em; margin: 0.5em 0; border-radius: 4px; }
            .event-time { font-weight: bold; color: #357abd; }
            .event-location { color: #666; }
            .faith-motto { text-align: center; font-style: italic; color: #4a90e2; }
        '''
        nav_css = epub.EpubItem(uid="nav_css", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)
        
        return book
        
    def _group_events_by_date(self, events: List[Event]) -> Dict[date, List[Event]]:
        """Group events by date."""
        events_by_date = {}
        
        for event in events:
            if event.start_time:
                event_date = event.start_time.date()
                if event_date not in events_by_date:
                    events_by_date[event_date] = []
                events_by_date[event_date].append(event)
                
        return events_by_date
        
    def _format_event_markdown(self, event: Event) -> str:
        """Format a single event for Markdown output."""
        lines = []
        
        # Event title
        lines.append(f"### {event.title}")
        
        # Time
        if event.start_time:
            if event.all_day:
                lines.append("**Time:** All Day")
            else:
                time_str = event.start_time.strftime("%I:%M %p")
                if event.end_time:
                    time_str += f" - {event.end_time.strftime('%I:%M %p')}"
                lines.append(f"**Time:** {time_str}")
                
        # Location
        if event.location:
            lines.append(f"**Location:** {event.location}")
            
        # Description
        if event.description:
            lines.append(f"**Description:** {event.description}")
            
        return "\n".join(lines)
        
    def _analyze_event_types(self, events: List[Event]) -> Dict[str, int]:
        """Analyze and categorize event types."""
        event_types = {}
        
        for event in events:
            # Simple categorization based on title keywords
            title_lower = event.title.lower()
            
            if any(word in title_lower for word in ['meeting', 'call', 'conference']):
                category = 'meetings'
            elif any(word in title_lower for word in ['lunch', 'dinner', 'meal']):
                category = 'meals'
            elif any(word in title_lower for word in ['appointment', 'medical', 'doctor']):
                category = 'appointments'
            elif any(word in title_lower for word in ['workout', 'gym', 'exercise']):
                category = 'fitness'
            elif any(word in title_lower for word in ['travel', 'trip', 'flight']):
                category = 'travel'
            else:
                category = 'other'
                
            event_types[category] = event_types.get(category, 0) + 1
            
        return event_types
        
    def _create_epub_cover(self, start_date: datetime, end_date: datetime) -> str:
        """Create HTML content for EPUB cover page."""
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Faith Forward Planner</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body>
            <div style="text-align: center; margin-top: 2em;">
                <h1 style="font-size: 2.5em; color: #4a90e2;">Faith Forward Planner</h1>
                <p class="faith-motto" style="font-size: 1.2em;">Spiritus Invictus - The Unconquered Spirit</p>
                
                <div style="margin: 2em 0;">
                    <h2>Weekly Plan</h2>
                    <p><strong>{start_date.strftime("%B %d, %Y")} - {end_date.strftime("%B %d, %Y")}</strong></p>
                </div>
                
                <div style="margin: 3em 0; padding: 1em; background: #f8f9fa; border-radius: 8px;">
                    <p><em>"Faith Forward is a sanctuary for combat veterans and believers seeking healing, purpose, and legacy."</em></p>
                </div>
                
                <p style="margin-top: 3em; color: #666;">Generated on {datetime.now().strftime("%B %d, %Y")}</p>
            </div>
        </body>
        </html>
        '''
        
    def _create_epub_reflection(self) -> str:
        """Create HTML content for daily reflection chapter."""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Daily Reflection</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body>
            <h1>Daily Reflection</h1>
            
            <div class="reflection">
                <p style="font-style: italic; font-size: 1.1em;">
                    "Be strong and courageous. Do not be afraid; do not be discouraged, 
                    for the Lord your God will be with you wherever you go."
                </p>
                <p style="text-align: right; font-weight: bold;">— Joshua 1:9</p>
            </div>
            
            <h2>Weekly Meditation</h2>
            <p>
                This week, let us remember that our strength comes not from our own might, 
                but from the One who goes before us. Whether facing challenges in our daily 
                schedule or navigating life's uncertainties, we are not alone.
            </p>
            
            <p>
                The Faith Forward community stands as a testament to the power of the 
                unconquered spirit - Spiritus Invictus. In our planning and our living, 
                may we carry this truth forward.
            </p>
            
            <div style="text-align: center; margin: 2em 0;">
                <p class="faith-motto">Spiritus Invictus</p>
            </div>
        </body>
        </html>
        '''
        
    def _create_epub_day_chapter(self, date_obj: date, events: List[Event]) -> str:
        """Create HTML content for a daily chapter."""
        day_name = date_obj.strftime("%A")
        full_date = date_obj.strftime("%B %d, %Y")
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{day_name}, {date_obj.strftime("%b %d")}</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body>
            <h1>{day_name}</h1>
            <h2>{full_date}</h2>
        '''
        
        if events:
            # Sort events by start time
            events.sort(key=lambda e: e.start_time if e.start_time else datetime.min)
            
            for event in events:
                html += f'''
                <div class="event">
                    <h3>{event.title}</h3>
                '''
                
                if event.start_time:
                    if event.all_day:
                        html += '<p class="event-time">All Day</p>'
                    else:
                        time_str = event.start_time.strftime("%I:%M %p")
                        if event.end_time:
                            time_str += f" - {event.end_time.strftime('%I:%M %p')}"
                        html += f'<p class="event-time">{time_str}</p>'
                        
                if event.location:
                    html += f'<p class="event-location">📍 {event.location}</p>'
                    
                if event.description:
                    html += f'<p>{event.description}</p>'
                    
                html += '</div>'
        else:
            html += '<p><em>No events scheduled for this day.</em></p>'
            
        html += '''
        </body>
        </html>
        '''
        
        return html
        
    def _create_epub_summary(self, events: List[Event], events_by_date: Dict[date, List[Event]]) -> str:
        """Create HTML content for weekly summary chapter."""
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Weekly Summary</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body>
            <h1>Weekly Summary</h1>
        '''
        
        html += f'<p><strong>Total Events:</strong> {len(events)}</p>'
        
        # Events by day
        html += '<h2>Events by Day</h2><ul>'
        for date_key, date_events in events_by_date.items():
            day_name = date_key.strftime("%A")
            html += f'<li>{day_name}: {len(date_events)} events</li>'
        html += '</ul>'
        
        # Event types
        event_types = self._analyze_event_types(events)
        if event_types:
            html += '<h2>Event Types</h2><ul>'
            for event_type, count in event_types.items():
                html += f'<li>{event_type.title()}: {count}</li>'
            html += '</ul>'
            
        html += '''
            <div style="margin-top: 3em; text-align: center;">
                <hr/>
                <p><em>Generated by Faith Forward Planner</em></p>
                <p class="faith-motto">Spiritus Invictus</p>
            </div>
        </body>
        </html>
        '''
        
        return html
        
    def export_ical(self, start_date: datetime = None, end_date: datetime = None) -> str:
        """Export events to iCal format."""
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=7)
            
        # Generate filename
        filename = f"faith_forward_calendar_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.ics"
        filepath = os.path.join(self.export_dir, filename)
        
        # Get iCal content from event manager
        ical_content = self.event_manager.export_to_ical()
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(ical_content)
            
        return filepath