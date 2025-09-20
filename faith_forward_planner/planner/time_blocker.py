"""
Time Blocker - Smart time blocking suggestions for optimal scheduling
Analyzes existing events and suggests optimal time slots for new events
"""

from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Tuple, Any
from .event_manager import EventManager, Event
import math


class TimeBlock:
    """Represents a suggested time block for scheduling."""
    
    def __init__(self, start_time: datetime, end_time: datetime, 
                 score: float, reason: str):
        self.start_time = start_time
        self.end_time = end_time
        self.score = score  # 0-100, higher is better
        self.reason = reason
        
    def duration(self) -> timedelta:
        """Get the duration of this time block."""
        return self.end_time - self.start_time
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'score': self.score,
            'reason': self.reason,
            'duration_minutes': int(self.duration().total_seconds() / 60)
        }


class TimeBlocker:
    """Smart time blocking engine for optimal scheduling."""
    
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        
        # Work hours configuration
        self.work_start = time(9, 0)  # 9 AM
        self.work_end = time(17, 0)   # 5 PM
        
        # Preferred time slots for different event types
        self.event_type_preferences = {
            'meeting': {
                'preferred_times': [(10, 0), (14, 0), (15, 0)],
                'avoid_times': [(12, 0), (17, 0)],
                'min_duration': 30,
                'max_duration': 120
            },
            'call': {
                'preferred_times': [(10, 0), (14, 0), (15, 30)],
                'avoid_times': [(12, 0), (17, 0)],
                'min_duration': 15,
                'max_duration': 60
            },
            'focus': {
                'preferred_times': [(9, 0), (10, 0), (14, 0)],
                'avoid_times': [(12, 0), (16, 0)],
                'min_duration': 60,
                'max_duration': 240
            },
            'lunch': {
                'preferred_times': [(12, 0), (12, 30), (13, 0)],
                'avoid_times': [(9, 0), (16, 0)],
                'min_duration': 30,
                'max_duration': 90
            },
            'break': {
                'preferred_times': [(10, 30), (15, 0), (15, 30)],
                'avoid_times': [(12, 0), (17, 0)],
                'min_duration': 15,
                'max_duration': 30
            }
        }
        
    def suggest_time_blocks(self, duration_minutes: int, 
                          event_type: str = 'meeting',
                          start_date: datetime = None,
                          end_date: datetime = None,
                          max_suggestions: int = 5) -> List[TimeBlock]:
        """Suggest optimal time blocks for a new event."""
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=7)  # Look ahead 1 week
            
        duration = timedelta(minutes=duration_minutes)
        suggestions = []
        
        # Get existing events in the date range
        existing_events = self.event_manager.get_events(start_date, end_date)
        
        # Analyze each day in the range
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            if self._is_workday(current_date):
                day_suggestions = self._analyze_day(
                    current_date, duration, event_type, existing_events
                )
                suggestions.extend(day_suggestions)
                
            current_date += timedelta(days=1)
            
        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x.score, reverse=True)
        return suggestions[:max_suggestions]
        
    def _analyze_day(self, date_obj, duration: timedelta, 
                    event_type: str, existing_events: List[Event]) -> List[TimeBlock]:
        """Analyze a single day for available time blocks."""
        suggestions = []
        
        # Get events for this specific day
        day_start = datetime.combine(date_obj, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        day_events = [e for e in existing_events 
                     if e.start_time and day_start <= e.start_time < day_end]
        
        # Create work hours for this day
        work_start = datetime.combine(date_obj, self.work_start)
        work_end = datetime.combine(date_obj, self.work_end)
        
        # Find free slots
        free_slots = self._find_free_slots(work_start, work_end, day_events, duration)
        
        # Score each free slot
        for start_time, end_time in free_slots:
            score = self._score_time_slot(start_time, end_time, event_type, day_events)
            reason = self._generate_reason(start_time, end_time, event_type, day_events)
            
            suggestion = TimeBlock(start_time, end_time, score, reason)
            suggestions.append(suggestion)
            
        return suggestions
        
    def _find_free_slots(self, work_start: datetime, work_end: datetime,
                        day_events: List[Event], duration: timedelta) -> List[Tuple[datetime, datetime]]:
        """Find free time slots in a day."""
        free_slots = []
        
        # Sort events by start time
        sorted_events = sorted([e for e in day_events if e.start_time and e.end_time], 
                              key=lambda x: x.start_time)
        
        # Check slot before first event
        if not sorted_events or sorted_events[0].start_time > work_start:
            slot_end = sorted_events[0].start_time if sorted_events else work_end
            if slot_end - work_start >= duration:
                free_slots.append((work_start, work_start + duration))
                
        # Check slots between events
        for i in range(len(sorted_events) - 1):
            current_event = sorted_events[i]
            next_event = sorted_events[i + 1]
            
            gap_start = current_event.end_time
            gap_end = next_event.start_time
            
            if gap_end - gap_start >= duration:
                # Find optimal position within the gap
                slot_start = gap_start
                slot_end = slot_start + duration
                
                # Ensure we don't go beyond the gap
                if slot_end <= gap_end:
                    free_slots.append((slot_start, slot_end))
                    
        # Check slot after last event
        if sorted_events:
            last_event = sorted_events[-1]
            if work_end - last_event.end_time >= duration:
                slot_start = last_event.end_time
                slot_end = slot_start + duration
                
                if slot_end <= work_end:
                    free_slots.append((slot_start, slot_end))
        elif work_end - work_start >= duration:
            # No events, entire work day is available
            free_slots.append((work_start, work_start + duration))
            
        return free_slots
        
    def _score_time_slot(self, start_time: datetime, end_time: datetime,
                        event_type: str, day_events: List[Event]) -> float:
        """Score a time slot based on various factors."""
        score = 50.0  # Base score
        
        # Get event type preferences
        prefs = self.event_type_preferences.get(event_type, {})
        
        # Time of day preference
        hour = start_time.hour
        minute = start_time.minute
        
        preferred_times = prefs.get('preferred_times', [])
        avoid_times = prefs.get('avoid_times', [])
        
        # Bonus for preferred times
        for pref_hour, pref_minute in preferred_times:
            time_diff = abs((hour * 60 + minute) - (pref_hour * 60 + pref_minute))
            if time_diff <= 30:  # Within 30 minutes
                score += 20 - (time_diff / 30 * 20)
                
        # Penalty for avoided times
        for avoid_hour, avoid_minute in avoid_times:
            time_diff = abs((hour * 60 + minute) - (avoid_hour * 60 + avoid_minute))
            if time_diff <= 60:  # Within 1 hour
                score -= 15 - (time_diff / 60 * 15)
                
        # Buffer time bonus (events with space around them)
        buffer_before = self._get_buffer_time(start_time, day_events, before=True)
        buffer_after = self._get_buffer_time(end_time, day_events, before=False)
        
        if buffer_before >= 15:  # 15+ minutes before
            score += 10
        if buffer_after >= 15:  # 15+ minutes after
            score += 10
            
        # Day of week adjustments
        weekday = start_time.weekday()
        if weekday == 0:  # Monday
            score += 5  # Fresh start of week
        elif weekday == 4:  # Friday
            score -= 5  # End of week fatigue
        elif weekday >= 5:  # Weekend
            score -= 20  # Avoid weekends for work events
            
        # Time of day general preferences
        if 9 <= hour <= 11:  # Morning focus time
            if event_type in ['focus', 'meeting']:
                score += 15
        elif 14 <= hour <= 16:  # Afternoon productive time
            if event_type in ['meeting', 'call']:
                score += 10
        elif hour >= 17:  # After hours
            score -= 20
            
        # Lunch time penalty
        if 12 <= hour <= 13 and event_type != 'lunch':
            score -= 25
            
        # Event clustering (prefer to group similar events)
        similar_events_nearby = self._count_similar_events_nearby(
            start_time, end_time, event_type, day_events
        )
        if similar_events_nearby > 0:
            score += 5 * similar_events_nearby
            
        # Ensure score is within bounds
        return max(0, min(100, score))
        
    def _get_buffer_time(self, target_time: datetime, day_events: List[Event], 
                        before: bool = True) -> int:
        """Get buffer time before or after a target time."""
        relevant_events = []
        
        for event in day_events:
            if not event.start_time or not event.end_time:
                continue
                
            if before:
                # Look for events ending before target time
                if event.end_time <= target_time:
                    relevant_events.append(event)
            else:
                # Look for events starting after target time
                if event.start_time >= target_time:
                    relevant_events.append(event)
                    
        if not relevant_events:
            return 60  # Assume 1 hour buffer if no adjacent events
            
        if before:
            # Find the closest event ending before target
            closest_event = max(relevant_events, key=lambda x: x.end_time)
            buffer = (target_time - closest_event.end_time).total_seconds() / 60
        else:
            # Find the closest event starting after target
            closest_event = min(relevant_events, key=lambda x: x.start_time)
            buffer = (closest_event.start_time - target_time).total_seconds() / 60
            
        return int(buffer)
        
    def _count_similar_events_nearby(self, start_time: datetime, end_time: datetime,
                                   event_type: str, day_events: List[Event]) -> int:
        """Count similar events within 2 hours of the proposed time."""
        count = 0
        window_start = start_time - timedelta(hours=2)
        window_end = end_time + timedelta(hours=2)
        
        for event in day_events:
            if not event.start_time:
                continue
                
            # Check if event is within time window
            if window_start <= event.start_time <= window_end:
                # Check if event type is similar
                if self._are_event_types_similar(event_type, event.title):
                    count += 1
                    
        return count
        
    def _are_event_types_similar(self, type1: str, event_title: str) -> bool:
        """Check if event types are similar based on title keywords."""
        title_lower = event_title.lower()
        
        type_keywords = {
            'meeting': ['meeting', 'standup', 'sync', 'review', 'discussion'],
            'call': ['call', 'phone', 'interview', 'chat'],
            'focus': ['focus', 'work', 'coding', 'development', 'analysis'],
            'lunch': ['lunch', 'meal', 'eat', 'food'],
            'break': ['break', 'rest', 'coffee', 'tea']
        }
        
        keywords = type_keywords.get(type1, [])
        return any(keyword in title_lower for keyword in keywords)
        
    def _generate_reason(self, start_time: datetime, end_time: datetime,
                        event_type: str, day_events: List[Event]) -> str:
        """Generate a human-readable reason for the suggestion."""
        reasons = []
        
        hour = start_time.hour
        
        # Time-based reasons
        if 9 <= hour <= 11:
            reasons.append("optimal morning focus time")
        elif 14 <= hour <= 16:
            reasons.append("productive afternoon slot")
        elif hour == 12:
            reasons.append("lunch time")
        elif hour >= 17:
            reasons.append("after-hours slot")
            
        # Buffer reasons
        buffer_before = self._get_buffer_time(start_time, day_events, before=True)
        buffer_after = self._get_buffer_time(end_time, day_events, before=False)
        
        if buffer_before >= 30 and buffer_after >= 30:
            reasons.append("well-spaced with buffer time")
        elif buffer_before >= 15 or buffer_after >= 15:
            reasons.append("has buffer time")
            
        # Event clustering
        similar_count = self._count_similar_events_nearby(
            start_time, end_time, event_type, day_events
        )
        if similar_count > 0:
            reasons.append(f"groups with {similar_count} similar events")
            
        # Weekday reasons
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday = weekday_names[start_time.weekday()]
        
        if start_time.weekday() == 0:
            reasons.append("fresh start of week")
        elif start_time.weekday() == 4:
            reasons.append("end of week wrap-up")
            
        if not reasons:
            reasons.append("available time slot")
            
        return f"{weekday} - {', '.join(reasons)}"
        
    def _is_workday(self, date_obj) -> bool:
        """Check if a date is a workday (Monday-Friday)."""
        return date_obj.weekday() < 5
        
    def analyze_schedule_conflicts(self, start_date: datetime = None,
                                 end_date: datetime = None) -> Dict[str, Any]:
        """Analyze schedule for potential conflicts and optimization opportunities."""
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=7)
            
        events = self.event_manager.get_events(start_date, end_date)
        
        analysis = {
            'total_events': len(events),
            'conflicts': [],
            'gaps': [],
            'overloaded_days': [],
            'optimization_suggestions': []
        }
        
        # Find overlapping events (conflicts)
        for i, event1 in enumerate(events):
            for event2 in events[i+1:]:
                if self._events_overlap(event1, event2):
                    analysis['conflicts'].append({
                        'event1': event1.title,
                        'event2': event2.title,
                        'overlap_start': max(event1.start_time, event2.start_time),
                        'overlap_end': min(event1.end_time, event2.end_time)
                    })
                    
        # Find large gaps in schedule
        sorted_events = sorted([e for e in events if e.start_time and e.end_time], 
                              key=lambda x: x.start_time)
        
        for i in range(len(sorted_events) - 1):
            current_event = sorted_events[i]
            next_event = sorted_events[i + 1]
            
            # Check if events are on the same day
            if current_event.end_time.date() == next_event.start_time.date():
                gap_duration = next_event.start_time - current_event.end_time
                if gap_duration > timedelta(hours=2):
                    analysis['gaps'].append({
                        'after_event': current_event.title,
                        'before_event': next_event.title,
                        'gap_duration_hours': gap_duration.total_seconds() / 3600,
                        'start_time': current_event.end_time,
                        'end_time': next_event.start_time
                    })
                    
        # Find overloaded days (too many events)
        daily_event_counts = {}
        for event in events:
            if event.start_time:
                day = event.start_time.date()
                daily_event_counts[day] = daily_event_counts.get(day, 0) + 1
                
        for day, count in daily_event_counts.items():
            if count >= 8:  # More than 8 events per day
                analysis['overloaded_days'].append({
                    'date': day,
                    'event_count': count
                })
                
        # Generate optimization suggestions
        if analysis['conflicts']:
            analysis['optimization_suggestions'].append(
                "Consider rescheduling conflicting events for better time management"
            )
            
        if analysis['gaps']:
            analysis['optimization_suggestions'].append(
                "Large gaps in schedule could be used for focused work or meetings"
            )
            
        if analysis['overloaded_days']:
            analysis['optimization_suggestions'].append(
                "Some days are overloaded - consider redistributing events"
            )
            
        return analysis
        
    def _events_overlap(self, event1: Event, event2: Event) -> bool:
        """Check if two events overlap in time."""
        if not all([event1.start_time, event1.end_time, event2.start_time, event2.end_time]):
            return False
            
        return (event1.start_time < event2.end_time and 
                event2.start_time < event1.end_time)
                
    def suggest_optimal_meeting_times(self, participants: List[str], 
                                    duration_minutes: int,
                                    date_range_days: int = 7) -> List[TimeBlock]:
        """Suggest optimal meeting times considering multiple participants."""
        # For now, this is a simplified version that doesn't check participant calendars
        # In a real implementation, this would integrate with external calendar APIs
        
        return self.suggest_time_blocks(
            duration_minutes=duration_minutes,
            event_type='meeting',
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=date_range_days)
        )