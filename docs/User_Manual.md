# Data Annotation Swiss Knife - User Manual

## Introduction

Welcome to the Data Annotation Swiss Knife! This application is designed to help you with various data annotation tasks. This user manual will guide you through the basics of getting started with the application and provide detailed instructions for using each tool.

## Getting Started

### Extracting the Application

1. Locate the zip file you received (e.g., `annotation_toolkit.zip`)
2. Extract/uncompress the zip file:
   - On Windows: Right-click the zip file and select "Extract All"
   - On Mac: Double-click the zip file to extract its contents

### Running the Application

#### On Windows:
1. Open the extracted folder
2. Find and double-click on `AnnotationToolkit.exe`
3. If you see a security warning, click "More info" and then "Run anyway"

#### On Mac:
1. Open the extracted folder
2. Find and double-click on `AnnotationToolkit.app`
3. If you see a security warning stating the app is from an unidentified developer:
   - Right-click (or Control-click) on `AnnotationToolkit.app`
   - Select "Open" from the menu
   - Click "Open" in the dialog box that appears

## Using the Application

### Main Interface

When you open the application, you'll see the main interface with different tools available in the sidebar. Select a tool by clicking on its name in the sidebar.

### Dictionary to Bullet List Tool

This tool converts dictionaries with URLs to formatted bullet lists with hyperlinks.

To use this tool:
1. Click on "Dictionary to Bullet List" in the sidebar
2. Load your dictionary file by clicking "Open File" or paste your content directly
3. Choose your preferred output format
4. Click "Convert" to generate the bullet list
5. Save the result by clicking "Save Output"

#### Input Format

The tool expects a JSON dictionary with string keys and values. For example:

```json
{
  "Example 1": "https://www.example.com/page1",
  "Example 2": "https://www.example.com/page2",
  "Example 3": "This is not a URL but still works"
}
```

#### Output Formats

- **Markdown**: Creates markdown-formatted links for URLs
- **Text**: Creates plain text with URLs

### JSON Visualizer Tool

This tool helps you visualize and format JSON data, with special handling for conversation data and XML tags.

To use this tool:
1. Click on "JSON Visualizer" in the sidebar
2. Load your JSON file by clicking "Load from File" or paste your content directly in the input area
3. Choose your preferred output format (Text or Markdown)
4. Click "Generate Visualization" to format the JSON data
5. The formatted result will appear in the display area below
6. Save the result by clicking "Save Conversation" or copy it to clipboard with "Copy Formatted JSON"

#### Supported JSON Formats

The JSON Visualizer supports multiple data formats:

1. **Standard JSON objects and arrays**:
   ```json
   {
     "name": "John Doe",
     "age": 30,
     "isActive": true,
     "address": {
       "street": "123 Main St",
       "city": "Anytown"
     }
   }
   ```

2. **Conversation data in various formats**:
   - Standard format:
     ```json
     [
       {"role": "user", "content": "Hello!"},
       {"role": "ai", "content": "Hi there!"}
     ]
     ```
   - Chat history format:
     ```json
     {
       "chat_history": [
         {"role": "user", "content": "Hello!"},
         {"role": "ai", "content": "Hi there!"}
       ]
     }
     ```
   - Message_v2 format:
     ```json
     [
       {"source": "user", "version": "message_v2", "body": "Hello", ...},
       {"source": "assistant", "version": "message_v2", "body": "Hi there", ...}
     ]
     ```

3. **XML tags in JSON strings**:
   The tool provides special formatting for XML tags in JSON strings, making them more readable:
   ```json
   {
     "message": "<response>\n    This is a response\n</response>"
   }
   ```
   Will be displayed with proper formatting for the XML tags.

#### Advanced Features

- **Search Functionality**: Use the search box at the top to find specific text within the JSON data. You can toggle case sensitivity with the "Case Sensitive" checkbox.
- **Debug Logging**: Enable debug logging to help troubleshoot issues with malformed JSON.
- **JSON Repair**: The tool automatically attempts to repair common JSON formatting issues, such as missing quotes, trailing commas, and unescaped characters.

### Conversation Visualizer Tool

This tool helps you visualize and format conversation data.

To use this tool:
1. Click on "Conversation Visualizer" in the sidebar
2. Load your conversation file by clicking "Open File" or paste your content directly
3. Choose your preferred output format
4. Click "Visualize" to format the conversation
5. Save the result by clicking "Save Output"

### Saving Your Work

To save your work:
1. Click the "Save" button in the toolbar
2. Choose a location on your computer
3. Enter a filename
4. Click "Save"

## Command Line Usage

The toolkit also provides a command-line interface for each tool:

### Dictionary to Bullet List

```bash
annotation-toolkit dict2bullet input.json --output output.md --format markdown
```

### JSON Visualizer

```bash
annotation-toolkit jsonvis data.json --output formatted.txt --format text
```

To search for specific content in JSON data:

```bash
annotation-toolkit jsonvis data.json --search "query" --case-sensitive
```

### Conversation Visualizer

```bash
annotation-toolkit convvis conversation.json --output formatted.txt --format text
```

To search for specific text in a conversation:

```bash
annotation-toolkit convvis conversation.json --search "hello" --case-sensitive
```

### Text Cleaner

```bash
annotation-toolkit textclean input.txt --output cleaned.txt
```

To transform cleaned text back to code format:

```bash
annotation-toolkit textclean --transform-back cleaned.txt --output code_format.txt --format code
```

## Troubleshooting

### Application Won't Open on Mac

If the application won't open on Mac:
1. Right-click (or Control-click) on `AnnotationToolkit.app`
2. Select "Open" from the context menu
3. Click "Open" in the dialog that appears

### Application Won't Open on Windows

If the application won't open on Windows:
1. Make sure you're running the application from the extracted folder
2. If Windows SmartScreen prevents the app from running, click "More info" and then "Run anyway"

### JSON Parsing Issues

If you encounter issues with JSON parsing:
1. Enable debug logging by checking the "Debug Logging" checkbox
2. Check the log file in the `~/annotation_toolkit_data/logs/json_parser.log` directory
3. Common issues include:
   - Missing quotes around string values
   - Trailing commas in arrays or objects
   - Unescaped special characters in strings
   - Malformed XML tags

### General Issues

If the application crashes or behaves unexpectedly:
1. Check the log files in the `~/annotation_toolkit_data/logs/` directory
2. Try restarting the application
3. If the issue persists, try reinstalling the application

## Need Help?

If you encounter any issues not covered in this manual, please contact your system administrator or the person who provided you with this application.
