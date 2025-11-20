# Graph Visualization Frontend

This is a web-based visualization interface for the User & Transaction Graph Environment. It provides an interactive way to explore the relationships between users, companies, and transactions.

## Features

- Interactive graph visualization using Cytoscape.js
- Filter nodes and relationships by type
- Search for specific nodes
- View detailed information about nodes and their connections
- Multiple layout options for better visualization
- Export graph as an image
- Responsive design for different screen sizes

## Setup

1. Install the required dependencies:
   ```bash
   pip install flask
   ```

2. Run the Flask server:
   ```bash
   cd frontend
   python server.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### Navigation

- **Zoom**: Use the mouse wheel or the zoom buttons in the toolbar
- **Pan**: Click and drag on the background
- **Select Node**: Click on a node to view its details
- **Reset View**: Click the "Reset View" button to fit the graph to the screen

### Filtering

Use the checkboxes in the sidebar to filter:
- Node types (Users, Companies, Transactions)
- Relationship types (Parent-Child, Director, Shareholder, etc.)

### Searching

Enter a search term in the search box and click the search button to find nodes by name or label.

### Layout

Select a layout from the dropdown menu and click "Apply Layout" to change the arrangement of nodes.

### Actions

- **Refresh Data**: Reload all data from the API
- **Detect Relationships**: Trigger the relationship detection on the server
- **Export as Image**: Save the current graph view as a PNG image

## Architecture

The frontend is built with:
- **HTML/CSS/JavaScript**: Core web technologies
- **Bootstrap 5**: For responsive UI components
- **Cytoscape.js**: For graph visualization
- **Flask**: Simple web server to serve the static files

## Customization

You can customize the appearance of the graph by modifying:
- `static/css/styles.css`: For general UI styling
- `static/js/graph-styles.js`: For node and edge styling in the graph
- `static/js/config.js`: For configuration settings
