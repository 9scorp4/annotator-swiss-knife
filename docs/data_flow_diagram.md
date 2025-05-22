# Data Flow Diagram for Annotation Swiss Knife

## Overview

This document provides a comprehensive data flow diagram for the Annotation Swiss Knife repository, illustrating how data moves through the system from input to output across different components.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ENTRY POINTS                                  │
│                                                                         │
│  ┌───────────────┐                              ┌───────────────┐       │
│  │ Command Line  │                              │ GUI           │       │
│  │ Interface     │                              │ Application   │       │
│  │ (cli.py)      │                              │ (app.py)      │       │
│  └───────┬───────┘                              └───────┬───────┘       │
│          │                                              │               │
└──────────┼──────────────────────────────────────────────┼───────────────┘
           │                                              │
           ▼                                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           CONFIGURATION                                 │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ Config (config.py)                                                │  │
│  │                                                                   │  │
│  │ - Loads settings from YAML files                                  │  │
│  │ - Loads settings from environment variables                       │  │
│  │ - Provides configuration to all components                        │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────┬───────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           CORE TOOLS                                    │
│                                                                         │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────────┐        │
│  │ DictToBullet  │    │ JsonVisualizer│    │ TextCleaner       │        │
│  │ List          │    │               │    │                   │        │
│  │ (dict_to_     │    │ (visualizer.  │    │ (text_cleaner.py) │        │
│  │  bullet.py)   │    │  py)          │    │                   │        │
│  └───────┬───────┘    └───────┬───────┘    └─────────┬─────────┘        │
│          │                    │                      │                  │
└──────────┼────────────────────┼──────────────────────┼──────────────────┘
           │                    │                      │
           ▼                    ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA PROCESSING                               │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ Input Data                                                        │  │
│  │                                                                   │  │
│  │ - JSON files                                                      │  │
│  │ - Text files                                                      │  │
│  │ - User input (via GUI or CLI)                                     │  │
│  └───────────────────────────────────┬───────────────────────────────┘  │
│                                      │                                  │
│                                      ▼                                  │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ Processing                                                        │  │
│  │                                                                   │  │
│  │ - Parse input data                                                │  │
│  │ - Apply transformations based on tool                             │  │
│  │ - Format output according to user preferences                     │  │
│  └───────────────────────────────────┬───────────────────────────────┘  │
│                                      │                                  │
│                                      ▼                                  │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ Output Data                                                       │  │
│  │                                                                   │  │
│  │ - Formatted text                                                  │  │
│  │ - Markdown                                                        │  │
│  │ - JSON                                                            │  │
│  │ - Display in GUI or write to file                                 │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Detailed Data Flow

### 1. Entry Points

The application has two main entry points:

- **Command Line Interface (CLI)**: Defined in `cli.py`, allows users to run tools with specific arguments.
- **Graphical User Interface (GUI)**: Defined in `app.py`, provides an interactive interface for using the tools.

### 2. Configuration

The `Config` class in `config.py` manages application settings:

- Loads default configuration
- Overrides with settings from YAML files if provided
- Further overrides with environment variables
- Provides configuration values to all components

### 3. Core Tools

The application includes several annotation tools, each inheriting from base classes defined in `base.py`:

- **DictToBulletList**: Converts dictionary data to formatted bullet lists with hyperlinks
- **JsonVisualizer**: Visualizes and formats JSON data, with special handling for conversation data
- **TextCleaner**: Cleans text from markdown/JSON/code artifacts

### 4. Data Processing Flow

#### Input Data Sources:
- JSON files
- Text files
- Direct user input (via GUI or CLI)
- Configuration settings

#### Processing:
1. **Data Loading**:
   - Files are read using file utilities
   - JSON is parsed and validated
   - Text is processed according to the selected tool

2. **Tool-Specific Processing**:
   - **DictToBulletList**:
     - Parses dictionary data
     - Formats entries as bullet points
     - Converts URLs to hyperlinks if markdown output is selected

   - **JsonVisualizer**:
     - Parses JSON data
     - Detects conversation formats
     - Formats JSON with proper indentation and highlighting
     - Handles special cases like XML tags in strings

   - **TextCleaner**:
     - Removes markdown/code artifacts
     - Cleans up formatting issues
     - Can transform cleaned text back to various formats

#### Output:
- Formatted text (plain text or markdown)
- JSON data
- Output can be:
  - Displayed in the GUI
  - Written to a file
  - Printed to the console

### 5. User Interface Components

#### CLI Commands:
- `dict2bullet`: Convert dictionary to bullet list
- `jsonvis`: Visualize JSON data
- `textclean`: Clean text from artifacts
- `gui`: Launch the graphical interface

#### GUI Components:
- Main menu for tool selection
- Tool-specific widgets for each annotation tool
- Input/output areas
- Configuration options

## Tool-Specific Data Flows

### Dictionary to Bullet List

```
Input JSON → Parse JSON → Validate Dictionary → Format as Bullet List → Output (Text/Markdown)
```

### JSON Visualizer

```
Input JSON → Parse JSON → Detect Format → Apply Formatting → Output (Text/Markdown)
                            │
                            ├─→ Conversation Format → Format Messages
                            │
                            └─→ Generic JSON → Format with Indentation/Highlighting
```

### Text Cleaner

```
Input Text → Remove Artifacts → Clean Formatting → Output Clean Text
                                                      │
                                                      └─→ Transform Back → Code/JSON/Markdown
```

## File Storage and Persistence

- Configuration is stored in YAML files
- Processed data can be saved to files
- Default save directory is configured in the Config class
