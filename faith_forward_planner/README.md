# Faith Forward Planner

> **Spiritus Invictus** - *The Unconquered Spirit*

A comprehensive GTK-based calendar application designed for Ubuntu/Debian systems, featuring faith-focused elements and advanced productivity tools.

## 🌟 About Faith Forward

Faith Forward is a sanctuary for combat veterans and believers seeking healing, purpose, and legacy. Founded on *Spiritus Invictus* — "The Unconquered Spirit", we blend theology, testimony, and community to restore what war tried to take.

## ✨ Features

### Core Calendar Functionality
- 📅 **Multiple Views**: Monthly, weekly, and daily calendar views
- ➕ **Event Management**: Create, edit, delete events with full CRUD operations
- 🔄 **Recurring Events**: Support for daily, weekly, and monthly recurring events
- ⏰ **Reminders**: Customizable event reminders
- 🖱️ **Drag & Drop**: Reschedule events by dragging between dates
- 🔍 **Search & Filter**: Find events by title, description, or location

### Enhanced Productivity Features
- 🗣️ **Natural Language Parsing**: Create events using natural language (e.g., "Meeting tomorrow at 2pm")
- ⚡ **Smart Time Blocking**: AI-powered suggestions for optimal time slots
- ✝️ **Daily Reflection Widget**: Faith-based daily verses and inspirational content
- 📤 **Export Options**: Export weekly plans to EPUB and Markdown formats

### Faith-Focused Elements
- 🙏 **Daily Bible Verses**: Rotating collection of inspirational verses
- ⭐ **Veteran-Focused Content**: Special verses and reflections for combat veterans
- 💙 **Healing-Centered**: Content focused on healing and restoration
- 🏛️ **Faith Forward Branding**: Complete branding with Faith Forward colors and motto

## 🚀 Installation

### Prerequisites

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 sqlite3 python3-pip

# Install Python dependencies
pip install -r requirements.txt
```

### Quick Start

1. **Clone or download the Faith Forward Planner**
   ```bash
   cd faith_forward_planner/
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python3 run_planner.py
   ```

## 📁 Directory Structure

```
faith_forward_planner/
├── assets/
│   ├── logo.png.placeholder          # Faith Forward logo placeholder
│   └── style.css                     # GTK CSS styling
├── planner/
│   ├── __init__.py                   # Package initialization
│   ├── main.py                       # Main GTK application
│   ├── calendar_view.py              # Calendar display logic
│   ├── event_manager.py              # Event CRUD operations
│   ├── nlp_parser.py                 # Natural language processing
│   ├── time_blocker.py               # Smart time blocking
│   ├── reflection_widget.py          # Daily reflection widget
│   └── exporter.py                   # EPUB/Markdown export
├── data/
│   └── planner.db                    # SQLite database
├── README.md                         # This file
├── requirements.txt                  # Python dependencies
└── run_planner.py                    # Application launcher
```

## 🎯 Usage Guide

### Creating Events

1. **Quick Add**: Use the natural language input in the sidebar
   - Examples: "Lunch tomorrow at 12pm", "Meeting next Friday at 2pm"
   
2. **Calendar Click**: Double-click any date to create an event

3. **Drag & Drop**: Reschedule events by dragging them to new dates

### Calendar Views

- **Month View**: Overview of the entire month with event summaries
- **Week View**: Detailed weekly view with hourly time slots
- **Day View**: Focused daily view for detailed planning

### Daily Reflections

The reflection widget provides:
- Daily Bible verses from KJV and inspirational sources
- Veteran-focused content for combat veterans
- Healing-centered verses for those in recovery
- Faith Forward community quotes and motto

### Export Features

Export your weekly plans:
- **Markdown**: Perfect for documentation and sharing
- **EPUB**: Create e-books of your weekly plans
- **iCal**: Standard calendar format for importing into other applications

### Smart Time Blocking

The time blocker analyzes your schedule and suggests:
- Optimal meeting times based on your preferences
- Buffer time around important events
- Event clustering for better productivity
- Conflict detection and resolution suggestions

## 🔧 Configuration

### Database

The application uses SQLite for data storage. The database is automatically created at:
- `data/planner.db`

### Styling

Customize the appearance by editing:
- `assets/style.css`

### Reflections

Add custom verses or modify the reflection content in:
- `planner/reflection_widget.py`

## 📊 Technical Details

### Dependencies

- **GTK 4.0**: Modern GTK framework for the user interface
- **libadwaita**: Provides modern GNOME styling
- **dateparser**: Natural language date parsing
- **icalendar**: iCal format support
- **markdown**: Markdown export functionality
- **ebooklib**: EPUB generation (optional)
- **sqlite3**: Database backend

### Database Schema

The application uses two main tables:
- **events**: Stores calendar events with full metadata
- **reminders**: Manages event reminders and notifications

### Natural Language Processing

Supports various input formats:
- "Meeting tomorrow at 2pm"
- "Lunch with John next Friday"
- "Weekly standup every Monday at 9am"
- "Doctor appointment in 2 weeks"

## 🚀 Deployment

### Building a Distributable Package

1. **Create a desktop entry** (optional):
   ```bash
   cat > ~/.local/share/applications/faith-forward-planner.desktop << EOF
   [Desktop Entry]
   Name=Faith Forward Planner
   Comment=Faith-focused calendar and planner
   Exec=/path/to/faith_forward_planner/run_planner.py
   Icon=/path/to/faith_forward_planner/assets/logo.png
   Terminal=false
   Type=Application
   Categories=Office;Calendar;
   EOF
   ```

2. **Create a launch script**:
   ```bash
   #!/bin/bash
   cd /path/to/faith_forward_planner
   python3 run_planner.py
   ```

### System-wide Installation

For system-wide installation:
```bash
sudo cp -r faith_forward_planner /opt/
sudo ln -s /opt/faith_forward_planner/run_planner.py /usr/local/bin/faith-forward-planner
```

## 🤝 Contributing

We welcome contributions to improve the Faith Forward Planner:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Credits

- **Faith Forward Community**: Spiritual guidance and mission
- **Combat Veterans**: Inspiration and feedback
- **Open Source Community**: Technical foundation

## 🆘 Support

For support, issues, or feature requests:
- Create an issue in the repository
- Contact the Faith Forward Community
- Check the documentation in the `docs/` directory

## 🌈 Mission Statement

*Faith Forward Community exists to help people realize the unlimited possibilities God has available. We believe in sharing encouragement, hope, and love from diverse faith traditions, inspiring everyone to move their faith forward every day.*

---

> **Spiritus Invictus** - *The Unconquered Spirit*  
> Faith Forward Community