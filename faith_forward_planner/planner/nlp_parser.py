"""
Natural Language Parser - Converts natural language to calendar events
Uses dateparser library for robust date/time parsing
"""

try:
    import dateparser
    DATEPARSER_AVAILABLE = True
except ImportError:
    DATEPARSER_AVAILABLE = False
    print("Warning: dateparser not available. Natural language parsing will be limited.")

import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import calendar


class NLPParser:
    """Natural language parser for calendar events."""
    
    def __init__(self):
        # Common time patterns
        self.time_patterns = {
            'morning': (9, 0),
            'afternoon': (14, 0),
            'evening': (18, 0),
            'night': (20, 0),
            'noon': (12, 0),
            'midnight': (0, 0)
        }
        
        # Duration patterns
        self.duration_patterns = {
            r'(\d+)\s*(?:hour|hr|h)s?': lambda m: timedelta(hours=int(m.group(1))),
            r'(\d+)\s*(?:minute|min|m)s?': lambda m: timedelta(minutes=int(m.group(1))),
            r'(\d+)\s*(?:day|d)s?': lambda m: timedelta(days=int(m.group(1))),
            r'(\d+)\s*(?:week|w)s?': lambda m: timedelta(weeks=int(m.group(1)))
        }
        
        # Recurrence patterns
        self.recurrence_patterns = {
            r'every\s+day|daily': {'frequency': 'daily', 'interval': 1},
            r'every\s+week|weekly': {'frequency': 'weekly', 'interval': 1},
            r'every\s+month|monthly': {'frequency': 'monthly', 'interval': 1},
            r'every\s+(\d+)\s+days?': lambda m: {'frequency': 'daily', 'interval': int(m.group(1))},
            r'every\s+(\d+)\s+weeks?': lambda m: {'frequency': 'weekly', 'interval': int(m.group(1))},
            r'every\s+(\d+)\s+months?': lambda m: {'frequency': 'monthly', 'interval': int(m.group(1))}
        }
        
        # Reminder patterns
        self.reminder_patterns = {
            r'remind\s+me\s+(\d+)\s*(?:minute|min)s?\s+before': lambda m: int(m.group(1)),
            r'remind\s+me\s+(\d+)\s*(?:hour|hr)s?\s+before': lambda m: int(m.group(1)) * 60,
            r'remind\s+me\s+(\d+)\s*(?:day|d)s?\s+before': lambda m: int(m.group(1)) * 24 * 60,
            r'(\d+)\s*(?:minute|min)s?\s+reminder': lambda m: int(m.group(1)),
            r'(\d+)\s*(?:hour|hr)s?\s+reminder': lambda m: int(m.group(1)) * 60
        }
        
    def parse_event(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse natural language text into event data."""
        if not text.strip():
            return None
            
        # Clean up the text
        text = text.strip().lower()
        original_text = text
        
        # Extract title (everything before time indicators)
        title = self._extract_title(text)
        
        # Extract location
        location = self._extract_location(text)
        
        # Extract recurrence
        recurrence = self._extract_recurrence(text)
        
        # Extract reminder
        reminder_minutes = self._extract_reminder(text)
        
        # Extract duration
        duration = self._extract_duration(text)
        
        # Parse date and time
        start_time, end_time = self._parse_datetime(text, duration)
        
        # Check if it's an all-day event
        all_day = self._is_all_day_event(text, start_time)
        
        if not title:
            title = "Untitled Event"
            
        event_data = {
            'title': title.title(),
            'description': f"Created from: '{original_text}'",
            'start_time': start_time,
            'end_time': end_time,
            'all_day': all_day,
            'location': location,
            'recurrence': recurrence,
            'reminder_minutes': reminder_minutes
        }
        
        return event_data
        
    def _extract_title(self, text: str) -> str:
        """Extract event title from text."""
        # Remove common prefixes
        text = re.sub(r'^(create|add|schedule|plan|book)\s+', '', text)
        text = re.sub(r'^(an?|the)\s+', '', text)
        
        # Find the main subject (before time/date indicators)
        time_indicators = [
            r'\b(?:at|on|in|for|during|from|until|to)\s+\d',
            r'\b(?:tomorrow|today|yesterday|next|last)\b',
            r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'\b(?:morning|afternoon|evening|night|noon|midnight)\b',
            r'\d{1,2}:\d{2}',
            r'\d{1,2}\s*(?:am|pm)'
        ]
        
        for pattern in time_indicators:
            match = re.search(pattern, text)
            if match:
                title = text[:match.start()].strip()
                if title:
                    return title
                    
        # If no time indicators found, use first few words
        words = text.split()
        if len(words) >= 3:
            return ' '.join(words[:3])
        elif words:
            return ' '.join(words)
            
        return ""
        
    def _extract_location(self, text: str) -> str:
        """Extract location from text."""
        location_patterns = [
            r'at\s+([^,\n]+?)(?:\s+(?:on|in|for|at|from|until|to)\s+\d|\s*$)',
            r'in\s+([^,\n]+?)(?:\s+(?:on|at|for|from|until|to)\s+\d|\s*$)',
            r'@\s*([^,\n]+?)(?:\s+(?:on|at|for|from|until|to)\s+\d|\s*$)',
            r'location:?\s*([^,\n]+?)(?:\s+(?:on|at|for|from|until|to)\s+\d|\s*$)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Filter out time-related words
                if not re.search(r'\b(?:morning|afternoon|evening|night|noon|midnight|\d+:\d+|\d+\s*(?:am|pm))\b', location, re.IGNORECASE):
                    return location.title()
                    
        return ""
        
    def _extract_recurrence(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract recurrence pattern from text."""
        for pattern, rule in self.recurrence_patterns.items():
            if callable(rule):
                match = re.search(pattern, text)
                if match:
                    return rule(match)
            else:
                if re.search(pattern, text):
                    return rule
                    
        return None
        
    def _extract_reminder(self, text: str) -> Optional[int]:
        """Extract reminder time in minutes."""
        for pattern, extractor in self.reminder_patterns.items():
            match = re.search(pattern, text)
            if match:
                return extractor(match)
                
        # Default reminder for certain keywords
        if re.search(r'\bremind|reminder|alert|notification\b', text):
            return 15  # 15 minutes default
            
        return None
        
    def _extract_duration(self, text: str) -> Optional[timedelta]:
        """Extract event duration."""
        for pattern, extractor in self.duration_patterns.items():
            match = re.search(pattern, text)
            if match:
                return extractor(match)
                
        # Look for "for X" patterns
        for_match = re.search(r'for\s+(\d+)\s*(?:hour|hr|h)s?', text)
        if for_match:
            return timedelta(hours=int(for_match.group(1)))
            
        for_match = re.search(r'for\s+(\d+)\s*(?:minute|min|m)s?', text)
        if for_match:
            return timedelta(minutes=int(for_match.group(1)))
            
        return None
        
    def _parse_datetime(self, text: str, duration: Optional[timedelta] = None) -> tuple[Optional[datetime], Optional[datetime]]:
        """Parse date and time from text."""
        # First try dateparser for full datetime parsing
        if DATEPARSER_AVAILABLE:
            parsed_dt = dateparser.parse(text, settings={
                'PREFER_DATES_FROM': 'future',
                'RETURN_AS_TIMEZONE_AWARE': False
            })
            
            if parsed_dt:
                start_time = parsed_dt
                
                # Calculate end time
                if duration:
                    end_time = start_time + duration
                else:
                    # Default duration based on event type
                    default_duration = self._get_default_duration(text)
                    end_time = start_time + default_duration
                    
                return start_time, end_time
        
        # Fallback: try to parse relative dates
        return self._parse_relative_datetime(text, duration)
        
    def _parse_relative_datetime(self, text: str, duration: Optional[timedelta] = None) -> tuple[Optional[datetime], Optional[datetime]]:
        """Parse relative dates like 'tomorrow', 'next week', etc."""
        now = datetime.now()
        start_time = None
        
        # Today
        if 'today' in text:
            start_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
            
        # Tomorrow
        elif 'tomorrow' in text:
            start_time = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
            
        # Next week
        elif 'next week' in text:
            days_ahead = 7 - now.weekday()
            start_time = (now + timedelta(days=days_ahead)).replace(hour=9, minute=0, second=0, microsecond=0)
            
        # Day names
        for i, day_name in enumerate(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
            if day_name in text:
                days_ahead = (i - now.weekday()) % 7
                if days_ahead == 0:  # Today is the day, assume next week
                    days_ahead = 7
                start_time = (now + timedelta(days=days_ahead)).replace(hour=9, minute=0, second=0, microsecond=0)
                break
                
        if start_time:
            # Try to extract specific time
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                ampm = time_match.group(3)
                
                if ampm:
                    if ampm == 'pm' and hour != 12:
                        hour += 12
                    elif ampm == 'am' and hour == 12:
                        hour = 0
                        
                start_time = start_time.replace(hour=hour, minute=minute)
                
            # Check for time of day indicators
            for time_word, (hour, minute) in self.time_patterns.items():
                if time_word in text:
                    start_time = start_time.replace(hour=hour, minute=minute)
                    break
                    
            # Calculate end time
            if duration:
                end_time = start_time + duration
            else:
                default_duration = self._get_default_duration(text)
                end_time = start_time + default_duration
                
            return start_time, end_time
            
        return None, None
        
    def _get_default_duration(self, text: str) -> timedelta:
        """Get default duration based on event type."""
        # Meeting patterns
        if re.search(r'\b(?:meeting|call|conference|session)\b', text):
            return timedelta(hours=1)
            
        # Meal patterns
        if re.search(r'\b(?:lunch|dinner|breakfast|meal)\b', text):
            return timedelta(hours=1)
            
        # Appointment patterns
        if re.search(r'\b(?:appointment|visit|consultation)\b', text):
            return timedelta(minutes=30)
            
        # Exercise patterns
        if re.search(r'\b(?:workout|exercise|gym|run|jog)\b', text):
            return timedelta(hours=1)
            
        # Travel patterns
        if re.search(r'\b(?:flight|travel|trip|journey)\b', text):
            return timedelta(hours=2)
            
        # Default
        return timedelta(hours=1)
        
    def _is_all_day_event(self, text: str, start_time: Optional[datetime]) -> bool:
        """Determine if this is an all-day event."""
        all_day_indicators = [
            'all day', 'whole day', 'entire day', 'full day',
            'birthday', 'anniversary', 'holiday', 'vacation'
        ]
        
        for indicator in all_day_indicators:
            if indicator in text:
                return True
                
        # If no specific time was parsed, it might be all-day
        if start_time and start_time.hour == 9 and start_time.minute == 0:
            # Check if there are any time indicators in the text
            if not re.search(r'\d{1,2}(?::\d{2})?\s*(?:am|pm)?|\b(?:morning|afternoon|evening|night|noon|midnight)\b', text):
                return True
                
        return False
        
    def suggest_completions(self, partial_text: str) -> list[str]:
        """Suggest completions for partial natural language input."""
        suggestions = []
        
        # Common event templates
        templates = [
            "Meeting with {person} tomorrow at 2pm",
            "Lunch at {location} on Friday",
            "Dentist appointment next week",
            "Birthday party on Saturday",
            "Weekly team meeting every Monday at 9am",
            "Gym workout today at 6pm for 1 hour",
            "Conference call tomorrow morning",
            "Dinner with family on Sunday evening"
        ]
        
        # Filter templates that match the partial text
        for template in templates:
            if partial_text.lower() in template.lower():
                suggestions.append(template)
                
        return suggestions[:5]  # Return top 5 suggestions