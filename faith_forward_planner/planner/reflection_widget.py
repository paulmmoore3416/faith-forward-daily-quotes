"""
Reflection Widget - Daily faith-based reflections and Bible verses
Provides inspirational content aligned with Faith Forward's mission
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from datetime import datetime, date
import random
import json
import os
from typing import Dict, List, Optional


class ReflectionWidget:
    """Widget providing daily faith-based reflections and Bible verses."""
    
    def __init__(self):
        self.current_date = date.today()
        self.verses_database = self._load_verses_database()
        self.main_widget = self._create_widget()
        self.verse_of_day = None
        self._load_daily_verse()
        
    def _load_verses_database(self) -> Dict:
        """Load Bible verses and inspirational quotes database."""
        # In a real implementation, this would load from a database or API
        # For now, we'll use a hardcoded collection of verses
        
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
                },
                {
                    "verse": "I can do all this through him who gives me strength.",
                    "reference": "Philippians 4:13",
                    "theme": "strength"
                },
                {
                    "verse": "And we know that in all things God works for the good of those who love him, who have been called according to his purpose.",
                    "reference": "Romans 8:28",
                    "theme": "purpose"
                },
                {
                    "verse": "The Lord is my shepherd, I lack nothing.",
                    "reference": "Psalm 23:1",
                    "theme": "provision"
                },
                {
                    "verse": "For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, to give you hope and a future.",
                    "reference": "Jeremiah 29:11",
                    "theme": "hope"
                },
                {
                    "verse": "Have I not commanded you? Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go.",
                    "reference": "Joshua 1:9",
                    "theme": "courage"
                },
                {
                    "verse": "The Lord your God is with you, the Mighty Warrior who saves. He will take great delight in you; in his love he will no longer rebuke you, but will rejoice over you with singing.",
                    "reference": "Zephaniah 3:17",
                    "theme": "love"
                },
                {
                    "verse": "Cast all your anxiety on him because he cares for you.",
                    "reference": "1 Peter 5:7",
                    "theme": "peace"
                },
                {
                    "verse": "But those who hope in the Lord will renew their strength. They will soar on wings like eagles; they will run and not grow weary, they will walk and not be faint.",
                    "reference": "Isaiah 40:31",
                    "theme": "renewal"
                },
                {
                    "verse": "The Lord is close to the brokenhearted and saves those who are crushed in spirit.",
                    "reference": "Psalm 34:18",
                    "theme": "healing"
                },
                {
                    "verse": "Therefore, if anyone is in Christ, the new creation has come: The old has gone, the new is here!",
                    "reference": "2 Corinthians 5:17",
                    "theme": "new_beginning"
                },
                {
                    "verse": "He heals the brokenhearted and binds up their wounds.",
                    "reference": "Psalm 147:3",
                    "theme": "healing"
                },
                {
                    "verse": "Come to me, all you who are weary and burdened, and I will give you rest.",
                    "reference": "Matthew 11:28",
                    "theme": "rest"
                },
                {
                    "verse": "The name of the Lord is a fortified tower; the righteous run to it and are safe.",
                    "reference": "Proverbs 18:10",
                    "theme": "protection"
                }
            ],
            "veteran_focused": [
                {
                    "verse": "No weapon forged against you will prevail, and you will refute every tongue that accuses you.",
                    "reference": "Isaiah 54:17",
                    "theme": "protection"
                },
                {
                    "verse": "Greater love has no one than this: to lay down one's life for one's friends.",
                    "reference": "John 15:13",
                    "theme": "sacrifice"
                },
                {
                    "verse": "Put on the full armor of God, so that you can take your stand against the devil's schemes.",
                    "reference": "Ephesians 6:11",
                    "theme": "spiritual_warfare"
                },
                {
                    "verse": "The Lord is a warrior; the Lord is his name.",
                    "reference": "Exodus 15:3",
                    "theme": "divine_warrior"
                }
            ],
            "healing_focused": [
                {
                    "verse": "He sent out his word and healed them; he rescued them from the grave.",
                    "reference": "Psalm 107:20",
                    "theme": "healing"
                },
                {
                    "verse": "Praise the Lord, my soul, and forget not all his benefits—who forgives all your sins and heals all your diseases.",
                    "reference": "Psalm 103:2-3",
                    "theme": "healing"
                },
                {
                    "verse": "But he was pierced for our transgressions, he was crushed for our iniquities; the punishment that brought us peace was on him, and by his wounds we are healed.",
                    "reference": "Isaiah 53:5",
                    "theme": "healing"
                }
            ],
            "faith_forward_quotes": [
                {
                    "verse": "Spiritus Invictus - The Unconquered Spirit lives within each of us.",
                    "reference": "Faith Forward Motto",
                    "theme": "spirit"
                },
                {
                    "verse": "Faith Forward is a sanctuary for those seeking healing, purpose, and legacy.",
                    "reference": "Faith Forward Mission",
                    "theme": "purpose"
                },
                {
                    "verse": "We restore what war tried to take through faith, community, and unconquered spirit.",
                    "reference": "Faith Forward Vision",
                    "theme": "restoration"
                }
            ]
        }
        
    def _create_widget(self) -> Gtk.Widget:
        """Create the reflection widget UI."""
        # Main container
        main_frame = Gtk.Frame()
        main_frame.add_css_class("reflection-widget")
        
        # Content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_box.set_margin_top(15)
        content_box.set_margin_bottom(15)
        content_box.set_margin_start(15)
        content_box.set_margin_end(15)
        
        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header_box.set_halign(Gtk.Align.CENTER)
        
        # Faith Forward icon/symbol
        faith_symbol = Gtk.Label(label="✝")
        faith_symbol.add_css_class("faith-symbol")
        faith_symbol.set_markup('<span size="x-large">✝</span>')
        header_box.append(faith_symbol)
        
        # Title
        title_label = Gtk.Label(label="Daily Reflection")
        title_label.add_css_class("reflection-title")
        title_label.set_markup('<span weight="bold">Daily Reflection</span>')
        header_box.append(title_label)
        
        content_box.append(header_box)
        
        # Date label
        self.date_label = Gtk.Label()
        self.date_label.add_css_class("reflection-date")
        self._update_date_label()
        content_box.append(self.date_label)
        
        # Verse text
        self.verse_label = Gtk.Label()
        self.verse_label.set_wrap(True)
        self.verse_label.set_wrap_mode(Pango.WrapMode.WORD)
        self.verse_label.set_justify(Gtk.Justification.CENTER)
        self.verse_label.add_css_class("reflection-verse")
        content_box.append(self.verse_label)
        
        # Reference
        self.reference_label = Gtk.Label()
        self.reference_label.add_css_class("reflection-reference")
        self.reference_label.set_halign(Gtk.Align.END)
        content_box.append(self.reference_label)
        
        # Separator
        separator = Gtk.Separator()
        content_box.append(separator)
        
        # Action buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        button_box.set_halign(Gtk.Align.CENTER)
        
        # New verse button
        new_verse_button = Gtk.Button(label="New Verse")
        new_verse_button.add_css_class("btn-secondary")
        new_verse_button.connect("clicked", self._on_new_verse_clicked)
        button_box.append(new_verse_button)
        
        # Share button
        share_button = Gtk.Button(label="Share")
        share_button.add_css_class("btn-secondary")
        share_button.connect("clicked", self._on_share_clicked)
        button_box.append(share_button)
        
        content_box.append(button_box)
        
        # Motto at bottom
        motto_label = Gtk.Label(label="Spiritus Invictus")
        motto_label.add_css_class("faith-forward-motto")
        motto_label.set_markup('<span style="italic" size="small">Spiritus Invictus</span>')
        content_box.append(motto_label)
        
        main_frame.set_child(content_box)
        
        # Schedule daily updates
        self._schedule_daily_update()
        
        return main_frame
        
    def get_widget(self) -> Gtk.Widget:
        """Get the reflection widget."""
        return self.main_widget
        
    def _load_daily_verse(self):
        """Load the verse for today."""
        # Use date as seed for reproducible daily verses
        random.seed(self.current_date.toordinal())
        
        # Determine which collection to use based on day of week or special considerations
        collection_weights = {
            "daily_verses": 60,
            "veteran_focused": 15,
            "healing_focused": 15,
            "faith_forward_quotes": 10
        }
        
        # Select collection based on weights
        collections = list(collection_weights.keys())
        weights = list(collection_weights.values())
        
        selected_collection = random.choices(collections, weights=weights)[0]
        verses = self.verses_database[selected_collection]
        
        # Select random verse from collection
        self.verse_of_day = random.choice(verses)
        
        # Update UI
        self._update_verse_display()
        
    def _update_verse_display(self):
        """Update the verse display in the UI."""
        if self.verse_of_day:
            self.verse_label.set_text(self.verse_of_day["verse"])
            self.reference_label.set_markup(f'<span weight="bold">— {self.verse_of_day["reference"]}</span>')
            
    def _update_date_label(self):
        """Update the date label."""
        formatted_date = self.current_date.strftime("%A, %B %d, %Y")
        self.date_label.set_markup(f'<span size="small">{formatted_date}</span>')
        
    def _schedule_daily_update(self):
        """Schedule daily verse updates at midnight."""
        def check_date_change():
            current_date = date.today()
            if current_date != self.current_date:
                self.current_date = current_date
                self._update_date_label()
                self._load_daily_verse()
            return True  # Continue the timeout
            
        # Check every hour for date changes
        GLib.timeout_add_seconds(3600, check_date_change)
        
    def _on_new_verse_clicked(self, button):
        """Handle new verse button click."""
        # Get a random verse from any collection
        all_verses = []
        for collection in self.verses_database.values():
            all_verses.extend(collection)
            
        self.verse_of_day = random.choice(all_verses)
        self._update_verse_display()
        
    def _on_share_clicked(self, button):
        """Handle share button click."""
        if self.verse_of_day:
            share_text = f'"{self.verse_of_day["verse"]}" - {self.verse_of_day["reference"]}\n\nShared from Faith Forward Planner\nSpiritus Invictus'
            
            # Copy to clipboard
            clipboard = self.main_widget.get_clipboard()
            clipboard.set_text(share_text, -1)
            
            # Show notification (in a real app, this would be a toast)
            print(f"Verse copied to clipboard: {share_text}")
            
    def get_verse_for_date(self, target_date: date) -> Dict:
        """Get the verse for a specific date."""
        # Use date as seed for reproducible verses
        random.seed(target_date.toordinal())
        
        # Same logic as _load_daily_verse but for specific date
        collection_weights = {
            "daily_verses": 60,
            "veteran_focused": 15,
            "healing_focused": 15,
            "faith_forward_quotes": 10
        }
        
        collections = list(collection_weights.keys())
        weights = list(collection_weights.values())
        
        selected_collection = random.choices(collections, weights=weights)[0]
        verses = self.verses_database[selected_collection]
        
        return random.choice(verses)
        
    def get_verses_by_theme(self, theme: str) -> List[Dict]:
        """Get all verses matching a specific theme."""
        matching_verses = []
        
        for collection in self.verses_database.values():
            for verse in collection:
                if verse.get("theme") == theme:
                    matching_verses.append(verse)
                    
        return matching_verses
        
    def add_custom_verse(self, verse: str, reference: str, theme: str = "custom"):
        """Add a custom verse to the database."""
        custom_verse = {
            "verse": verse,
            "reference": reference,
            "theme": theme
        }
        
        # Add to daily_verses collection
        if "custom_verses" not in self.verses_database:
            self.verses_database["custom_verses"] = []
            
        self.verses_database["custom_verses"].append(custom_verse)
        
    def get_reflection_for_event(self, event_title: str) -> Optional[Dict]:
        """Get a relevant verse based on event context."""
        title_lower = event_title.lower()
        
        # Map event keywords to themes
        theme_mapping = {
            "meeting": "wisdom",
            "interview": "courage",
            "presentation": "confidence",
            "travel": "protection",
            "medical": "healing",
            "appointment": "peace",
            "workout": "strength",
            "gym": "strength",
            "lunch": "provision",
            "dinner": "fellowship",
            "family": "love",
            "work": "purpose",
            "project": "purpose"
        }
        
        # Find matching theme
        for keyword, theme in theme_mapping.items():
            if keyword in title_lower:
                verses = self.get_verses_by_theme(theme)
                if verses:
                    return random.choice(verses)
                    
        # Default to random verse
        all_verses = []
        for collection in self.verses_database.values():
            all_verses.extend(collection)
            
        return random.choice(all_verses) if all_verses else None
        
    def export_verses_collection(self) -> str:
        """Export the verses collection as JSON."""
        return json.dumps(self.verses_database, indent=2)
        
    def import_verses_collection(self, json_data: str) -> bool:
        """Import verses from JSON data."""
        try:
            imported_data = json.loads(json_data)
            # Merge with existing database
            for collection_name, verses in imported_data.items():
                if collection_name in self.verses_database:
                    # Extend existing collection
                    self.verses_database[collection_name].extend(verses)
                else:
                    # Create new collection
                    self.verses_database[collection_name] = verses
            return True
        except (json.JSONDecodeError, KeyError):
            return False