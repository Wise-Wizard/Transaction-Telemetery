/**
 * Configuration settings for the graph visualization
 */
const CONFIG = {
    // API endpoints
    API: {
        BASE_URL: 'http://localhost:8000/api',
        USERS: '/users',
        TRANSACTIONS: '/transactions',
        USER_RELATIONSHIPS: '/relationships/user/',
        TRANSACTION_RELATIONSHIPS: '/relationships/transaction/',
        BUSINESS_RELATIONSHIPS: '/business-relationships/user/',
        DETECT_RELATIONSHIPS: '/detect-relationships',

        // Analytics endpoints
        SHORTEST_PATH: '/analytics/shortest-path',
        TRANSACTION_CLUSTERS: '/analytics/transaction-clusters',
        GRAPH_METRICS: '/analytics/graph-metrics',

        // Export endpoints
        EXPORT_JSON: '/export/json',
        EXPORT_CSV: '/export/csv'
    },

    // Node types
    NODE_TYPES: {
        USER: 'user',
        COMPANY: 'company',
        TRANSACTION: 'transaction'
    },

    // Relationship types
    RELATIONSHIP_TYPES: {
        // Business relationships
        PARENT_OF: 'PARENT_OF',
        SUBSIDIARY_OF: 'SUBSIDIARY_OF',
        DIRECTOR_OF: 'DIRECTOR_OF',
        SHAREHOLDER_OF: 'SHAREHOLDER_OF',
        LEGAL_ENTITY_OF: 'LEGAL_ENTITY_OF',
        COMPOSITE: 'COMPOSITE',

        // User-to-user relationships
        SHARED_EMAIL: 'SHARED_EMAIL',
        SHARED_PHONE: 'SHARED_PHONE',
        SHARED_ADDRESS: 'SHARED_ADDRESS',
        SHARED_PAYMENT_METHOD: 'SHARED_PAYMENT_METHOD',

        // Transaction relationships
        SENT: 'SENT',
        RECEIVED_BY: 'RECEIVED_BY',
        LINKED_TO: 'LINKED_TO'
    },

    // Relationship categories for filtering
    RELATIONSHIP_CATEGORIES: {
        PARENT_CHILD: ['PARENT_OF', 'SUBSIDIARY_OF'],
        DIRECTOR: ['DIRECTOR_OF'],
        SHAREHOLDER: ['SHAREHOLDER_OF'],
        LEGAL_ENTITY: ['LEGAL_ENTITY_OF'],
        COMPOSITE: ['COMPOSITE'],
        SHARED_ATTRIBUTES: ['SHARED_EMAIL', 'SHARED_PHONE', 'SHARED_ADDRESS', 'SHARED_PAYMENT_METHOD'],
        TRANSACTION: ['SENT', 'RECEIVED_BY', 'LINKED_TO']
    },

    // Graph layout options
    LAYOUTS: {
        'cola': {
            name: 'cola',
            nodeDimensionsIncludeLabels: true,
            refresh: 30,
            fit: true,
            padding: 50,
            randomize: true,
            nodeSpacing: 100,
            edgeLength: 150,
            animate: true,
            animationDuration: 500,
            avoidOverlap: true,
            maxSimulationTime: 4000
        },
        'circle': {
            name: 'circle',
            fit: true,
            padding: 50,
            animate: true,
            animationDuration: 500,
            radius: 500
        },
        'concentric': {
            name: 'concentric',
            fit: true,
            padding: 50,
            startAngle: 3 / 2 * Math.PI,
            sweep: undefined,
            clockwise: true,
            equidistant: false,
            minNodeSpacing: 50,
            animate: true,
            animationDuration: 500,
            concentric: function(node) {
                return node.degree();
            },
            levelWidth: function(nodes) {
                return nodes.maxDegree() / 4;
            }
        },
        'grid': {
            name: 'grid',
            fit: true,
            padding: 50,
            rows: undefined,
            columns: undefined,
            animate: true,
            animationDuration: 500
        },
        'breadthfirst': {
            name: 'breadthfirst',
            fit: true,
            padding: 50,
            directed: false,
            circle: false,
            grid: false,
            spacingFactor: 1.5,
            animate: true,
            animationDuration: 500
        }
    }
};
