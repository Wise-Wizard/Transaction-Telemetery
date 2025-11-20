/**
 * Cytoscape graph styles
 */
const GRAPH_STYLES = [
    // Node Styles
    {
        selector: 'node',
        style: {
            'background-color': '#4a6fdc',
            'label': 'data(label)',
            'color': '#fff',
            'text-outline-color': '#4a6fdc',
            'text-outline-width': '2px',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',
            'font-weight': 'bold',
            'text-max-width': '100px',
            'text-wrap': 'ellipsis',
            'width': 'data(size)',
            'height': 'data(size)',
            'border-width': '2px',
            'border-color': '#fff',
            'text-background-opacity': 0,
            'text-background-color': '#fff',
            'text-background-padding': '3px',
            'text-background-shape': 'roundrectangle',
            'text-border-opacity': 0,
            'text-border-width': '1px',
            'text-border-color': '#888'
        }
    },

    // User Node Style
    {
        selector: 'node[type="user"]',
        style: {
            'background-color': '#4a6fdc',
            'text-outline-color': '#4a6fdc',
            'shape': 'ellipse'
        }
    },

    // Company Node Style
    {
        selector: 'node[type="company"]',
        style: {
            'background-color': '#28a745',
            'text-outline-color': '#28a745',
            'shape': 'roundrectangle'
        }
    },

    // Transaction Node Style
    {
        selector: 'node[type="transaction"]',
        style: {
            'background-color': '#ffc107',
            'text-outline-color': '#ffc107',
            'shape': 'diamond',
            'color': '#000',
            'text-outline-width': '0px',
            'text-background-color': 'rgba(255, 255, 255, 0.8)',
            'text-background-opacity': 1,
            'text-background-padding': '3px',
            'text-background-shape': 'roundrectangle',
            'text-border-opacity': 1,
            'text-border-width': '1px',
            'text-border-color': '#ffc107',
            'text-max-width': '150px',
            'font-size': '10px'
        }
    },

    // Highlighted Node Style
    {
        selector: 'node.highlighted',
        style: {
            'border-width': '4px',
            'border-color': '#ff0000',
            'text-outline-color': '#ff0000',
            'text-outline-width': '3px',
            'z-index': 999
        }
    },

    // Selected Node Style
    {
        selector: 'node:selected',
        style: {
            'border-width': '4px',
            'border-color': '#ff0000',
            'text-outline-color': '#ff0000',
            'text-outline-width': '3px',
            'z-index': 999
        }
    },

    // Edge Styles
    {
        selector: 'edge',
        style: {
            'width': 2,
            'line-color': '#ccc',
            'target-arrow-color': '#ccc',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'color': '#777',
            'text-rotation': 'autorotate',
            'text-margin-y': '-10px',
            'text-background-color': '#fff',
            'text-background-opacity': 0.7,
            'text-background-padding': '2px',
            'edge-text-rotation': 'autorotate'
        }
    },

    // Business Relationship Styles
    {
        selector: 'edge[type="PARENT_OF"]',
        style: {
            'line-color': '#28a745',
            'target-arrow-color': '#28a745',
            'width': 3
        }
    },
    {
        selector: 'edge[type="SUBSIDIARY_OF"]',
        style: {
            'line-color': '#28a745',
            'target-arrow-color': '#28a745',
            'line-style': 'dashed',
            'width': 3
        }
    },
    {
        selector: 'edge[type="DIRECTOR_OF"]',
        style: {
            'line-color': '#9c27b0',
            'target-arrow-color': '#9c27b0',
            'width': 3
        }
    },
    {
        selector: 'edge[type="SHAREHOLDER_OF"]',
        style: {
            'line-color': '#ff9800',
            'target-arrow-color': '#ff9800',
            'width': 3
        }
    },
    {
        selector: 'edge[type="LEGAL_ENTITY_OF"]',
        style: {
            'line-color': '#795548',
            'target-arrow-color': '#795548',
            'width': 3
        }
    },
    {
        selector: 'edge[type="COMPOSITE"]',
        style: {
            'line-color': '#e91e63',
            'target-arrow-color': '#e91e63',
            'width': 4,
            'line-style': 'solid'
        }
    },

    // Shared Attribute Relationship Styles
    {
        selector: 'edge[type="SHARED_EMAIL"], edge[type="SHARED_PHONE"], edge[type="SHARED_ADDRESS"], edge[type="SHARED_PAYMENT_METHOD"]',
        style: {
            'line-color': '#03a9f4',
            'target-arrow-color': '#03a9f4',
            'line-style': 'dotted',
            'width': 2
        }
    },

    // Transaction Relationship Styles
    {
        selector: 'edge[type="SENT"]',
        style: {
            'line-color': '#ff5722',
            'target-arrow-color': '#ff5722',
            'width': 3,
            'line-style': 'solid',
            'text-background-color': '#fff',
            'text-background-opacity': 1,
            'text-background-padding': '2px',
            'text-border-opacity': 1,
            'text-border-width': '1px',
            'text-border-color': '#ff5722'
        }
    },
    {
        selector: 'edge[type="RECEIVED_BY"]',
        style: {
            'line-color': '#ff5722',
            'target-arrow-color': '#ff5722',
            'width': 3,
            'line-style': 'solid',
            'text-background-color': '#fff',
            'text-background-opacity': 1,
            'text-background-padding': '2px',
            'text-border-opacity': 1,
            'text-border-width': '1px',
            'text-border-color': '#ff5722'
        }
    },
    {
        selector: 'edge[type="LINKED_TO"]',
        style: {
            'line-color': '#607d8b',
            'target-arrow-color': '#607d8b',
            'line-style': 'dashed',
            'width': 2,
            'target-arrow-shape': 'none',
            'source-arrow-shape': 'none'
        }
    },

    // Highlighted Edge Style
    {
        selector: 'edge.highlighted',
        style: {
            'width': 4,
            'line-color': '#ff0000',
            'target-arrow-color': '#ff0000',
            'z-index': 999
        }
    },

    // Selected Edge Style
    {
        selector: 'edge:selected',
        style: {
            'width': 4,
            'line-color': '#ff0000',
            'target-arrow-color': '#ff0000',
            'z-index': 999
        }
    }
];
