#!/usr/bin/env python3
"""
Faith Forward Planner - Demo Script
Demonstrates core functionality without requiring GTK
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from planner.event_manager import EventManager
from planner.nlp_parser import NLPParser
from planner.time_blocker import TimeBlocker
from planner.exporter import Exporter

def main():
    print("=" * 60)
    print("🌟 FAITH FORWARD PLANNER DEMO 🌟")
    print("Spiritus Invictus - The Unconquered Spirit")
    print("=" * 60)
    print()
    
    # Initialize components
    print("📦 Initializing components...")
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'demo.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    event_manager = EventManager(db_path)
    nlp_parser = NLPParser()
    time_blocker = TimeBlocker(event_manager)
    exporter = Exporter(event_manager)
    
    # Create reflection widget without GTK components
    class SimpleReflectionWidget:
        def __init__(self):
            self.current_date = datetime.now().date()
            self.verses_database = self._load_verses_database()
            self.verse_of_day = None
            self._load_daily_verse()
            
        def _load_verses_database(self):
            return {
                "daily_verses": [
                    {
                        "verse": "Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go.",
                        "reference": "Joshua 1:9",
                        "theme": "courage"
                    },
                    {
                        "verse": "Trust in the Lord with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight.",
                        "reference": "Proverbs 3:5-6",
                        "theme": "trust"
                    }
                ],
                "healing_focused": [
                    {
                        "verse": "He heals the brokenhearted and binds up their wounds.",
                        "reference": "Psalm 147:3",
                        "theme": "healing"
                    }
                ]
            }
            
        def _load_daily_verse(self):
            import random
            random.seed(self.current_date.toordinal())
            all_verses = []
            for collection in self.verses_database.values():
                all_verses.extend(collection)
            self.verse_of_day = random.choice(all_verses) if all_verses else None
            
        def get_verses_by_theme(self, theme):
            matching_verses = []
            for collection in self.verses_database.values():
                for verse in collection:
                    if verse.get("theme") == theme:
                        matching_verses.append(verse)
            return matching_verses
    
    reflection = SimpleReflectionWidget()
    print("✅ Components initialized successfully!")
    print()
    
    # Demo 1: Natural Language Parsing
    print("🗣️  DEMO 1: Natural Language Event Parsing")
    print("-" * 40)
    test_phrases = [
        "Meeting with John tomorrow at 2pm",
        "Lunch next Friday at noon",
        "Weekly standup every Monday at 9am",
        "Doctor appointment in 2 weeks",
        "Birthday party on Saturday evening"
    ]
    
    for phrase in test_phrases:
        result = nlp_parser.parse_event(phrase)
        if result:
            print(f"✅ '{phrase}' → {result['title']}")
            # Create the event
            event_manager.create_event(**result)
        else:
            print(f"❌ Failed to parse: '{phrase}'")
    print()
    
    # Demo 2: Event Management
    print("📅 DEMO 2: Event Management")
    print("-" * 40)
    
    # Create some sample events
    now = datetime.now()
    sample_events = [
        {
            'title': 'Morning Prayer',
            'description': 'Daily morning devotion',
            'start_time': now.replace(hour=7, minute=0),
            'end_time': now.replace(hour=7, minute=30),
            'recurrence': {'frequency': 'daily', 'interval': 1}
        },
        {
            'title': 'Team Meeting',
            'description': 'Weekly team sync',
            'start_time': now.replace(hour=10, minute=0),
            'end_time': now.replace(hour=11, minute=0),
            'location': 'Conference Room A'
        },
        {
            'title': 'Faith Forward Community Gathering',
            'description': 'Monthly community meeting',
            'start_time': now.replace(hour=19, minute=0),
            'end_time': now.replace(hour=21, minute=0),
            'location': 'Community Center'
        }
    ]
    
    for event_data in sample_events:
        event_id = event_manager.create_event(**event_data)
        print(f"✅ Created: {event_data['title']}")
    
    # Show all events
    all_events = event_manager.get_events()
    print(f"\n📊 Total events in calendar: {len(all_events)}")
    print()
    
    # Demo 3: Smart Time Blocking
    print("⚡ DEMO 3: Smart Time Blocking")
    print("-" * 40)
    
    suggestions = time_blocker.suggest_time_blocks(60, 'meeting')  # 60-minute meeting
    print(f"🎯 Found {len(suggestions)} optimal time slots for a 1-hour meeting:")
    
    for i, suggestion in enumerate(suggestions[:3], 1):
        print(f"  {i}. {suggestion.start_time.strftime('%A %I:%M %p')} - "
              f"{suggestion.end_time.strftime('%I:%M %p')} "
              f"(Score: {suggestion.score:.1f}/100)")
        print(f"     Reason: {suggestion.reason}")
    print()
    
    # Demo 4: Daily Reflection
    print("✝️  DEMO 4: Daily Reflection")
    print("-" * 40)
    
    verse = reflection.verse_of_day
    if verse:
        print(f"📖 Today's Verse:")
        print(f"   \"{verse['verse']}\"")
        print(f"   — {verse['reference']}")
        print()
        
        # Show themed verses
        healing_verses = reflection.get_verses_by_theme('healing')
        print(f"🏥 Found {len(healing_verses)} healing-focused verses")
        
        veteran_verses = reflection.get_verses_by_theme('courage')
        print(f"🎖️  Found {len(veteran_verses)} courage-focused verses")
    print()
    
    # Demo 5: Export Functionality
    print("📤 DEMO 5: Export Functionality")
    print("-" * 40)
    
    try:
        # Export to Markdown
        md_file = exporter.export_to_markdown()
        print(f"✅ Exported to Markdown: {os.path.basename(md_file)}")
        
        # Show sample of markdown content
        with open(md_file, 'r') as f:
            content = f.read()[:500] + "..." if len(f.read()) > 500 else f.read()
        print(f"📄 Sample content preview:")
        print("   " + content.replace('\n', '\n   ')[:200] + "...")
        
    except Exception as e:
        print(f"❌ Export error: {e}")
    
    try:
        # Try EPUB export
        epub_file = exporter.export_to_epub()
        print(f"✅ Exported to EPUB: {os.path.basename(epub_file)}")
    except Exception as e:
        print(f"⚠️  EPUB export not available: {e}")
    print()
    
    # Demo 6: Schedule Analysis
    print("📊 DEMO 6: Schedule Analysis")
    print("-" * 40)
    
    analysis = time_blocker.analyze_schedule_conflicts()
    print(f"📈 Schedule Analysis Results:")
    print(f"   Total events: {analysis['total_events']}")
    print(f"   Conflicts detected: {len(analysis['conflicts'])}")
    print(f"   Large gaps found: {len(analysis['gaps'])}")
    print(f"   Overloaded days: {len(analysis['overloaded_days'])}")
    
    if analysis['optimization_suggestions']:
        print(f"💡 Optimization suggestions:")
        for suggestion in analysis['optimization_suggestions']:
            print(f"   • {suggestion}")
    print()
    
    # Final summary
    print("=" * 60)
    print("🎉 DEMO COMPLETE!")
    print()
    print("Faith Forward Planner features demonstrated:")
    print("✅ Natural language event parsing")
    print("✅ Smart event management with SQLite backend")
    print("✅ Intelligent time blocking suggestions")
    print("✅ Daily faith-based reflections")
    print("✅ Export to Markdown and EPUB formats")
    print("✅ Schedule analysis and optimization")
    print()
    print("To run the full GTK application:")
    print("  python3 run_planner.py")
    print()
    print("Spiritus Invictus - The Unconquered Spirit!")
    print("=" * 60)

if __name__ == "__main__":
    main()