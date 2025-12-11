// Global variables
let cy; // Cytoscape instance
let allNodes = []; // All nodes from the API
let allEdges = []; // All edges from the API
let relationshipTypes = new Set(); // Set of all relationship types
let currentLayout = 'cose-bilkent'; // Default layout
let selectedUserIds = []; // Track selected user IDs

// Initialize the application when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Make sure the required libraries are loaded
    if (typeof cytoscape === 'undefined') {
        console.error('Cytoscape.js is not loaded!');
        alert('Error: Cytoscape.js library is missing. Please check your internet connection and refresh the page.');
        return;
    }

    // Register the Cytoscape extensions
    try {
        // Register cose-bilkent layout if available
        if (typeof cytoscapeCoseBilkent !== 'undefined') {
            cytoscape.use(cytoscapeCoseBilkent);
            console.log('cose-bilkent layout registered');
        } else {
            console.warn('cose-bilkent layout not available, falling back to cose layout');
            currentLayout = 'cose'; // Fallback to built-in cose layout
        }

        // Register popper extension if available
        if (typeof cytoscapePopper !== 'undefined') {
            cytoscape.use(cytoscapePopper);
            console.log('popper extension registered');
        } else {
            console.warn('popper extension not available');
        }

        // Register navigator extension if available
        if (typeof cytoscapeNavigator !== 'undefined') {
            cytoscape.use(cytoscapeNavigator);
            console.log('navigator extension registered');
        } else {
            console.warn('navigator extension not available');
        }
    } catch (error) {
        console.error('Error registering Cytoscape extensions:', error);
    }

    // Initialize Cytoscape
    initCytoscape();

    // Show initial blank state message
    showBlankState();
    
    // Load user list for selection
    loadUsersList();
    
    // Initialize table
    loadTransactionsTable();
    
    // Set up event listeners
    setupEventListeners();
});

// Initialize Cytoscape with default settings
function initCytoscape() {
    console.log('Initializing Cytoscape with layout:', currentLayout);

    // Define layout options based on the available layout
    let layoutOptions;

    if (currentLayout === 'cose-bilkent') {
        layoutOptions = {
            name: currentLayout,
            animate: true,
            padding: 30,
            nodeDimensionsIncludeLabels: true,
            randomize: false,
            nodeRepulsion: 4500,
            idealEdgeLength: 100,
            edgeElasticity: 0.45,
            nestingFactor: 0.1,
            gravity: 0.25
        };
    } else {
        // Fallback to standard cose layout
        layoutOptions = {
            name: 'cose',
            animate: true,
            padding: 30,
            nodeDimensionsIncludeLabels: true,
            componentSpacing: 40,
            nodeRepulsion: 4500,
            nodeOverlap: 10,
            idealEdgeLength: 100,
            edgeElasticity: 100,
            nestingFactor: 5,
            gravity: 80
        };
    }

    cy = cytoscape({
        container: document.getElementById('cy'),
        style: [
            // Node styles
            {
                selector: 'node',
                style: {
                    'background-color': '#666',
                    'label': 'data(label)',
                    'color': '#fff',
                    'text-outline-color': '#555',
                    'text-outline-width': 2,
                    'font-size': 12,
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'text-wrap': 'wrap',
                    'text-max-width': 100
                }
            },
            {
                selector: 'node[type="User"]',
                style: {
                    'background-color': '#4e73df',
                    'shape': 'ellipse'
                }
            },
            {
                selector: 'node[type="Transaction"]',
                style: {
                    'background-color': '#1cc88a',
                    'shape': 'diamond'
                }
            },
            // Edge styles - will be extended dynamically
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#999',
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'target-arrow-color': '#999',
                    'label': 'data(label)',
                    'font-size': 10,
                    'text-rotation': 'autorotate',
                    'text-background-color': '#fff',
                    'text-background-opacity': 0.7,
                    'text-background-padding': 2
                }
            }
        ],
        layout: layoutOptions,
        wheelSensitivity: 0.2
    });

    // Add node click event
    cy.on('tap', 'node', function(evt) {
        const node = evt.target;
        showNodeDetails(node);
    });

    // Add edge click event
    cy.on('tap', 'edge', function(evt) {
        const edge = evt.target;
        showEdgeDetails(edge);
    });

    // Add background click event to clear selection
    cy.on('tap', function(evt) {
        if (evt.target === cy) {
            hideNodeDetails();
        }
    });
}

// Show blank state message
function showBlankState() {
    const cyContainer = cy.container();
    const existingMessage = cyContainer.querySelector('.blank-state-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    const message = document.createElement('div');
    message.className = 'blank-state-message';
    message.style.cssText = `
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        color: #6c757d;
        pointer-events: none;
        z-index: 1000;
    `;
    message.innerHTML = `
        <i class="fas fa-project-diagram" style="font-size: 4rem; opacity: 0.3; margin-bottom: 1rem;"></i>
        <h4>Select Users to Visualize</h4>
        <p>Choose one or more users from the sidebar and click "Load Graph"</p>
    `;
    cyContainer.appendChild(message);
}

// Hide blank state message
function hideBlankState() {
    const cyContainer = cy.container();
    const message = cyContainer.querySelector('.blank-state-message');
    if (message) {
        message.remove();
    }
}

// Load users list for selection (replaces loadGraphData)
async function loadUsersList() {
    try {
        console.log('Fetching users list...');
        const response = await fetch('/api/users?limit=100');
        const users = await response.json();
        console.log('Users received:', users.length);
        
        populateUsersList(users);
    } catch (error) {
        console.error('Error loading users list:', error);
        alert('Failed to load users list. Please try again later.');
    }
}

// Load graph data for selected users
async function loadSelectedUsersGraph() {
    if (selectedUserIds.length === 0) {
        alert('Please select at least one user');
        return;
    }
    
    try {
        // Show loading indicator
        showLoading();
        hideBlankState();

        // Fetch graph data for selected users
        console.log('Fetching graph data for users:', selectedUserIds);
        const userIdsParam = selectedUserIds.join(',');
        const response = await fetch(`/api/graph-data/users?user_ids=${encodeURIComponent(userIdsParam)}`);
        const data = await response.json();
        console.log('Graph data received:', data);

        // Store data globally
        allNodes = data.nodes || [];
        allEdges = data.edges || [];

        console.log(`Loaded ${allNodes.length} nodes and ${allEdges.length} edges`);

        // Clear existing graph
        cy.elements().remove();
        
        // Extract relationship types
        relationshipTypes.clear();
        allEdges.forEach(edge => {
            relationshipTypes.add(edge.data.relationship);
        });

        console.log('Relationship types:', Array.from(relationshipTypes));

        // Populate relationship filters
        populateRelationshipFilters();

        // Populate transaction list (from loaded data)
        populateTransactionsList();

        // Add data to Cytoscape
        console.log('Adding nodes to Cytoscape...');
        cy.add(allNodes);
        console.log('Adding edges to Cytoscape...');
        cy.add(allEdges);

        // Apply layout
        console.log('Applying layout...');
        applyLayout();

        // Add edge styles based on relationship types
        console.log('Adding edge styles...');
        addEdgeStyles();

        // Hide loading indicator
        hideLoading();

        // Fit the graph to the viewport
        cy.fit();

        console.log('Graph visualization complete!');
    } catch (error) {
        console.error('Error loading graph data:', error);
        hideLoading();
        showBlankState();
        alert('Failed to load graph data. Please try again later.');
    }
}

// Add edge styles based on relationship types
function addEdgeStyles() {
    relationshipTypes.forEach(type => {
        let color;
        switch (type) {
            case 'SENT': color = '#f6c23e'; break;
            case 'RECEIVED_BY': color = '#36b9cc'; break;
            case 'SHARED_EMAIL': color = '#e74a3b'; break;
            case 'SHARED_PHONE': color = '#fd7e14'; break;
            case 'SHARED_ADDRESS': color = '#6f42c1'; break;
            case 'SHARED_PAYMENT_METHOD': color = '#20c997'; break;
            case 'LINKED_TO': color = '#6c757d'; break;
            case 'PARENT_OF': color = '#0d6efd'; break;
            case 'SUBSIDIARY_OF': color = '#6610f2'; break;
            case 'DIRECTOR_OF': color = '#d63384'; break;
            case 'SHAREHOLDER_OF': color = '#dc3545'; break;
            case 'LEGAL_ENTITY_OF': color = '#198754'; break;
            case 'COMPOSITE': color = '#0dcaf0'; break;
            default: color = '#999';
        }

        cy.style().selector(`edge[relationship="${type}"]`).style({
            'line-color': color,
            'target-arrow-color': color
        }).update();
    });
}

// Populate relationship filters
function populateRelationshipFilters() {
    const container = document.getElementById('relationshipFilters');
    container.innerHTML = '';

    relationshipTypes.forEach(type => {
        const div = document.createElement('div');
        div.className = 'form-check';

        const input = document.createElement('input');
        input.className = 'form-check-input';
        input.type = 'checkbox';
        input.id = `rel-${type}`;
        input.checked = true;
        input.addEventListener('change', filterGraph);

        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `rel-${type}`;
        label.textContent = type.replace(/_/g, ' ');

        div.appendChild(input);
        div.appendChild(label);
        container.appendChild(div);
    });
}

// Populate users list with checkboxes
function populateUsersList(users) {
    const container = document.getElementById('usersList');
    container.innerHTML = '';

    if (!users || users.length === 0) {
        container.innerHTML = '<div class="text-muted p-2 text-center">No users found</div>';
        return;
    }

    users.forEach(user => {
        const item = document.createElement('div');
        item.className = 'form-check p-2';
        
        const checkbox = document.createElement('input');
        checkbox.className = 'form-check-input';
        checkbox.type = 'checkbox';
        checkbox.id = `user-${user.id}`;
        checkbox.value = user.id;
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                if (!selectedUserIds.includes(user.id)) {
                    selectedUserIds.push(user.id);
                }
            } else {
                selectedUserIds = selectedUserIds.filter(id => id !== user.id);
            }
            console.log('Selected users:', selectedUserIds);
        });
        
        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `user-${user.id}`;
        label.textContent = user.name || user.id;
        label.style.cursor = 'pointer';
        
        item.appendChild(checkbox);
        item.appendChild(label);
        container.appendChild(item);
    });
}

// Populate transactions list
function populateTransactionsList() {
    const container = document.getElementById('transactionsList');
    container.innerHTML = '';

    const transactions = allNodes.filter(node => node.data.type === 'Transaction');

    transactions.forEach(transaction => {
        const item = document.createElement('a');
        item.className = 'list-group-item list-group-item-action';
        item.setAttribute('data-id', transaction.data.id);
        item.textContent = transaction.data.label;

        item.addEventListener('click', function() {
            const nodeId = this.getAttribute('data-id');
            const node = cy.getElementById(nodeId);
            selectNode(node);
        });

        container.appendChild(item);
    });
}

// Select a node
function selectNode(node) {
    // Clear previous selection
    cy.elements().removeClass('selected');

    // Add selected class
    node.addClass('selected');

    // Center view on node
    cy.animate({
        fit: {
            eles: node,
            padding: 50
        },
        duration: 500
    });

    // Show node details
    showNodeDetails(node);
}

// Show node details
function showNodeDetails(node) {
    const detailsPanel = document.getElementById('nodeDetails');
    const detailsTitle = document.getElementById('nodeDetailsTitle');
    const detailsContent = document.getElementById('nodeDetailsContent');

    // Set title
    detailsTitle.textContent = node.data('label');

    // Build content based on node type
    let content = '';

    if (node.data('type') === 'User') {
        content = `
            <p><strong>ID:</strong> ${node.data('id')}</p>
            <p><strong>Type:</strong> ${node.data('type')}</p>
            <p><strong>Email:</strong> ${node.data('email') || 'N/A'}</p>
            <p><strong>Phone:</strong> ${node.data('phone') || 'N/A'}</p>
            <p><strong>Address:</strong> ${node.data('address') || 'N/A'}</p>
            <p><strong>Entity Type:</strong> ${node.data('entity_type') || 'N/A'}</p>
            <p><strong>Company:</strong> ${node.data('company_name') || 'N/A'}</p>
        `;
    } else if (node.data('type') === 'Transaction') {
        content = `
            <p><strong>ID:</strong> ${node.data('id')}</p>
            <p><strong>Type:</strong> ${node.data('type')}</p>
            <p><strong>Amount:</strong> ${node.data('amount')} ${node.data('currency')}</p>
            <p><strong>Date:</strong> ${formatDate(node.data('timestamp'))}</p>
            <p><strong>Status:</strong> ${node.data('status')}</p>
            <p><strong>IP Address:</strong> ${node.data('ip_address') || 'N/A'}</p>
            <p><strong>Device ID:</strong> ${node.data('device_id') || 'N/A'}</p>
        `;
    }

    detailsContent.innerHTML = content;

    // Show panel
    detailsPanel.style.display = 'block';
}

// Show edge details
function showEdgeDetails(edge) {
    const detailsPanel = document.getElementById('nodeDetails');
    const detailsTitle = document.getElementById('nodeDetailsTitle');
    const detailsContent = document.getElementById('nodeDetailsContent');

    // Set title
    detailsTitle.textContent = `Relationship: ${edge.data('relationship')}`;

    // Build content
    let content = `
        <p><strong>Type:</strong> ${edge.data('relationship')}</p>
        <p><strong>Source:</strong> ${edge.source().data('label')}</p>
        <p><strong>Target:</strong> ${edge.target().data('label')}</p>
    `;

    // Add additional properties if available
    if (edge.data('properties')) {
        const props = edge.data('properties');
        for (const key in props) {
            if (props.hasOwnProperty(key)) {
                content += `<p><strong>${key}:</strong> ${props[key]}</p>`;
            }
        }
    }

    detailsContent.innerHTML = content;

    // Show panel
    detailsPanel.style.display = 'block';
}

// Hide node details
function hideNodeDetails() {
    const detailsPanel = document.getElementById('nodeDetails');
    detailsPanel.style.display = 'none';
}

// Filter graph based on user selections
function filterGraph() {
    // Get filter values
    const showUsers = document.getElementById('showUsers').checked;
    const showTransactions = document.getElementById('showTransactions').checked;
    const searchText = document.getElementById('searchInput').value.toLowerCase();

    // Get selected relationship types
    const selectedRelationships = [];
    relationshipTypes.forEach(type => {
        const checkbox = document.getElementById(`rel-${type}`);
        if (checkbox && checkbox.checked) {
            selectedRelationships.push(type);
        }
    });

    // Filter nodes
    cy.nodes().forEach(node => {
        const nodeType = node.data('type');
        const nodeLabel = node.data('label').toLowerCase();
        const nodeId = node.data('id').toLowerCase();

        // Check node type
        let visible = (nodeType === 'User' && showUsers) ||
                     (nodeType === 'Transaction' && showTransactions);

        // Check search text
        if (visible && searchText) {
            visible = nodeLabel.includes(searchText) || nodeId.includes(searchText);
        }

        node.style('display', visible ? 'element' : 'none');
    });

    // Filter edges
    cy.edges().forEach(edge => {
        const relType = edge.data('relationship');
        const sourceVisible = edge.source().style('display') !== 'none';
        const targetVisible = edge.target().style('display') !== 'none';

        // Check if relationship type is selected and both nodes are visible
        const visible = selectedRelationships.includes(relType) &&
                       sourceVisible && targetVisible;

        edge.style('display', visible ? 'element' : 'none');
    });
}

// Apply layout
function applyLayout() {
    console.log('Applying layout:', currentLayout);

    // Define layout options based on the available layout
    let layoutOptions;

    if (currentLayout === 'cose-bilkent') {
        layoutOptions = {
            name: currentLayout,
            animate: true,
            padding: 30,
            nodeDimensionsIncludeLabels: true,
            randomize: false,
            nodeRepulsion: 4500,
            idealEdgeLength: 100,
            edgeElasticity: 0.45,
            nestingFactor: 0.1,
            gravity: 0.25
        };
    } else if (currentLayout === 'concentric') {
        layoutOptions = {
            name: 'concentric',
            animate: true,
            padding: 30,
            nodeDimensionsIncludeLabels: true,
            minNodeSpacing: 50,
            concentric: function(node) {
                // Place users in the center
                return node.data('type') === 'User' ? 10 : 1;
            },
            levelWidth: function() { return 1; }
        };
    } else {
        // Fallback to standard cose layout
        layoutOptions = {
            name: 'cose',
            animate: true,
            padding: 30,
            nodeDimensionsIncludeLabels: true,
            componentSpacing: 40,
            nodeRepulsion: 4500,
            nodeOverlap: 10,
            idealEdgeLength: 100,
            edgeElasticity: 100,
            nestingFactor: 5,
            gravity: 80
        };
    }

    try {
        const layout = cy.layout(layoutOptions);
        layout.run();
    } catch (error) {
        console.error('Error applying layout:', error);
        // Fallback to grid layout if all else fails
        try {
            cy.layout({ name: 'grid' }).run();
        } catch (e) {
            console.error('Even grid layout failed:', e);
        }
    }
}

// Toggle layout
function toggleLayout() {
    // Cycle through available layouts
    if (currentLayout === 'cose-bilkent') {
        currentLayout = 'concentric';
    } else if (currentLayout === 'concentric') {
        currentLayout = 'cose';
    } else {
        // If cose-bilkent is available, use it, otherwise use concentric
        currentLayout = typeof cytoscapeCoseBilkent !== 'undefined' ? 'cose-bilkent' : 'concentric';
    }

    console.log('Switched to layout:', currentLayout);
    applyLayout();
}

// Reset view
function resetView() {
    cy.fit(undefined, 50);
}

// Export image
function exportImage() {
    const png64 = cy.png({scale: 2, full: true});
    const link = document.createElement('a');
    link.href = png64;
    link.download = 'graph-visualization.png';
    link.click();
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Show loading indicator
function showLoading() {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.id = 'loadingOverlay';

    const spinner = document.createElement('div');
    spinner.className = 'spinner-border text-primary';
    spinner.setAttribute('role', 'status');

    const span = document.createElement('span');
    span.className = 'visually-hidden';
    span.textContent = 'Loading...';

    spinner.appendChild(span);
    loadingOverlay.appendChild(spinner);
    document.body.appendChild(loadingOverlay);
}

// Hide loading indicator
function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

// Search users via API
async function searchUsers(query) {
    const container = document.getElementById('usersList');
    container.innerHTML = '<div class="text-center p-2"><div class="spinner-border spinner-border-sm text-primary" role="status"></div></div>';
    
    try {
        let url = '/api/users?limit=50';
        if (query) {
            url += `&search=${encodeURIComponent(query)}`;
        }
        
        const response = await fetch(url);
        const users = await response.json();
        
        container.innerHTML = '';
        
        if (users.length === 0) {
            container.innerHTML = '<div class="text-muted p-2 text-center">No users found</div>';
            return;
        }

        users.forEach(user => {
            const item = document.createElement('a');
            item.className = 'list-group-item list-group-item-action';
            item.setAttribute('data-id', user.id);
            item.textContent = user.name || user.id;

            item.addEventListener('click', async function() {
                const nodeId = this.getAttribute('data-id');
                await addNodeToGraph(nodeId, 'User');
            });

            container.appendChild(item);
        });
    } catch (error) {
        console.error('Error searching users:', error);
        container.innerHTML = '<div class="text-danger p-2 text-center">Error searching users</div>';
    }
}

// Search transactions via API
async function searchTransactions(query) {
    const container = document.getElementById('transactionsList');
    container.innerHTML = '<div class="text-center p-2"><div class="spinner-border spinner-border-sm text-primary" role="status"></div></div>';
    
    try {
        let url = '/api/transactions?limit=50';
        if (query) {
            url += `&search=${encodeURIComponent(query)}`;
        }
        
        const response = await fetch(url);
        const transactions = await response.json();
        
        container.innerHTML = '';
        
        if (transactions.length === 0) {
            container.innerHTML = '<div class="text-muted p-2 text-center">No transactions found</div>';
            return;
        }

        transactions.forEach(tx => {
            const item = document.createElement('a');
            item.className = 'list-group-item list-group-item-action';
            item.setAttribute('data-id', tx.id);
            item.textContent = `Transaction: ${tx.amount} ${tx.currency}`;

            item.addEventListener('click', async function() {
                const nodeId = this.getAttribute('data-id');
                await addNodeToGraph(nodeId, 'Transaction');
            });

            container.appendChild(item);
        });
    } catch (error) {
        console.error('Error searching transactions:', error);
        container.innerHTML = '<div class="text-danger p-2 text-center">Error searching transactions</div>';
    }
}

// Table state
let currentPage = 1;
let currentSort = 'timestamp';
let currentOrder = 'desc';
const itemsPerPage = 10;

// Load transactions table
async function loadTransactionsTable() {
    const tbody = document.getElementById('transactionsTableBody');
    tbody.innerHTML = '<tr><td colspan="6" class="text-center"><div class="spinner-border spinner-border-sm text-primary" role="status"></div> Loading...</td></tr>';
    
    try {
        const skip = (currentPage - 1) * itemsPerPage;
        let url = `/api/transactions?skip=${skip}&limit=${itemsPerPage}&sort_by=${currentSort}&order=${currentOrder}`;
        
        // Add search if exists
        const searchInput = document.getElementById('transactionSearchInput');
        if (searchInput && searchInput.value) {
            url += `&search=${encodeURIComponent(searchInput.value)}`;
        }
        
        const response = await fetch(url);
        const transactions = await response.json();
        
        renderTable(transactions);
        updatePagination(transactions.length);
    } catch (error) {
        console.error('Error loading table:', error);
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error loading data</td></tr>';
    }
}

// Render table rows
function renderTable(transactions) {
    const tbody = document.getElementById('transactionsTableBody');
    tbody.innerHTML = '';
    
    if (transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No transactions found</td></tr>';
        return;
    }
    
    transactions.forEach(tx => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><small>${tx.id}</small></td>
            <td>${tx.amount}</td>
            <td>${tx.currency}</td>
            <td><small>${new Date(tx.timestamp).toLocaleString()}</small></td>
            <td><span class="badge bg-${getStatusColor(tx.status)}">${tx.status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary view-btn" data-id="${tx.id}">
                    <i class="fas fa-project-diagram"></i> View
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
    
    // Add event listeners to buttons
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            addNodeToGraph(id, 'Transaction');
            // Scroll to graph
            document.getElementById('cy').scrollIntoView({ behavior: 'smooth' });
        });
    });
}

// Get status color
function getStatusColor(status) {
    switch(status.toLowerCase()) {
        case 'completed': return 'success';
        case 'pending': return 'warning';
        case 'failed': return 'danger';
        default: return 'secondary';
    }
}

// Update pagination controls
function updatePagination(count) {
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    const pageInfo = document.getElementById('pageInfo');
    
    pageInfo.textContent = `Page ${currentPage}`;
    
    if (currentPage <= 1) {
        prevBtn.classList.add('disabled');
    } else {
        prevBtn.classList.remove('disabled');
    }
    
    // Simple check: if we got fewer items than requested, we're at the end
    if (count < itemsPerPage) {
        nextBtn.classList.add('disabled');
    } else {
        nextBtn.classList.remove('disabled');
    }
    
    // Re-attach listeners
    prevBtn.onclick = () => changePage(-1);
    nextBtn.onclick = () => changePage(1);
}

// Change page
function changePage(delta) {
    if ((delta < 0 && currentPage === 1)) return;
    currentPage += delta;
    loadTransactionsTable();
}

// Sort table
window.sortTable = function(column) {
    if (currentSort === column) {
        currentOrder = currentOrder === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort = column;
        currentOrder = 'desc';
    }
    currentPage = 1; // Reset to first page
    loadTransactionsTable();
}

// Add node to graph dynamically
async function addNodeToGraph(nodeId, type) {
    // Check if node already exists
    let node = cy.getElementById(nodeId);
    
    if (node.length === 0) {
        // Show loading
        showLoading();
        try {
            // Fetch relationships (which includes the node itself)
            const url = type === 'User' 
                ? `/api/relationships/user/${nodeId}`
                : `/api/relationships/transaction/${nodeId}`;
                
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to fetch node details');
            
            const data = await response.json();
            
            // Add the main node
            const mainNodeData = type === 'User' ? data.user : data.transaction;
            
            // Format node for Cytoscape
            const cyNode = {
                group: 'nodes',
                data: {
                    id: mainNodeData.id,
                    type: type,
                    label: type === 'User' ? (mainNodeData.name || 'Unknown') : `Transaction: ${mainNodeData.amount} ${mainNodeData.currency}`,
                    ...mainNodeData
                }
            };
            
            cy.add(cyNode);
            node = cy.getElementById(nodeId);
            
            // Add related nodes and edges if they don't exist
            // This part simplifies adding neighbors - a full implementation would parse the relationships object
            // For now, we just ensure the main node is added and selected
            
            console.log(`Added ${type} ${nodeId} to graph`);
            
        } catch (error) {
            console.error(`Error adding ${type} to graph:`, error);
            alert(`Failed to load ${type} details`);
        } finally {
            hideLoading();
        }
    }
    
    if (node.length > 0) {
        selectNode(node);
    }
}

// Setup event listeners
function setupEventListeners() {
    // User selection buttons
    document.getElementById('loadSelectedUsers').addEventListener('click', loadSelectedUsersGraph);
    
    document.getElementById('selectAllUsers').addEventListener('click', function() {
        const checkboxes = document.querySelectorAll('#usersList input[type="checkbox"]');
        selectedUserIds = [];
        checkboxes.forEach(cb => {
            cb.checked = true;
            selectedUserIds.push(cb.value);
        });
        console.log('All users selected:', selectedUserIds);
    });
    
    document.getElementById('clearAllUsers').addEventListener('click', function() {
        const checkboxes = document.querySelectorAll('#usersList input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = false);
        selectedUserIds = [];
        console.log('All users deselected');
    });
    
    // Search input
    document.getElementById('searchInput').addEventListener('input', filterGraph);

    // Node type checkboxes
    document.getElementById('showUsers').addEventListener('change', filterGraph);
    document.getElementById('showTransactions').addEventListener('change', filterGraph);

    // User search (now just filters the checkbox list)
    let userSearchTimeout;
    document.getElementById('userSearchInput').addEventListener('input', function() {
        clearTimeout(userSearchTimeout);
        userSearchTimeout = setTimeout(() => filterList('usersList', this.value), 300);
    });

    // Transaction search (Server-side)
    let txSearchTimeout;
    document.getElementById('transactionSearchInput').addEventListener('input', function() {
        clearTimeout(txSearchTimeout);
        txSearchTimeout = setTimeout(() => searchTransactions(this.value), 300);
    });

    // Clear search buttons
    document.getElementById('clearUserSearch').addEventListener('click', function() {
        document.getElementById('userSearchInput').value = '';
        filterList('usersList', '');
    });

    document.getElementById('clearTransactionSearch').addEventListener('click', function() {
        document.getElementById('transactionSearchInput').value = '';
        searchTransactions('');
    });

    // Toolbar buttons
    document.getElementById('resetViewBtn').addEventListener('click', resetView);
    document.getElementById('toggleLayoutBtn').addEventListener('click', toggleLayout);
    document.getElementById('exportImageBtn').addEventListener('click', exportImage);
    document.getElementById('zoomInBtn').addEventListener('click', function() {
        cy.zoom(cy.zoom() * 1.2);
    });
    document.getElementById('zoomOutBtn').addEventListener('click', function() {
        cy.zoom(cy.zoom() / 1.2);
    });

    // Close node details
    document.getElementById('closeNodeDetails').addEventListener('click', hideNodeDetails);

    // Collapse buttons
    document.getElementById('collapseUsersBtn').addEventListener('click', function() {
        toggleCollapse('usersListContainer', this);
    });

    document.getElementById('collapseTransactionsBtn').addEventListener('click', function() {
        toggleCollapse('transactionsListContainer', this);
    });
    
    // Initial load of lists
    searchUsers('');
    searchTransactions('');
}

// Toggle collapse
function toggleCollapse(containerId, button) {
    const container = document.getElementById(containerId);
    const icon = button.querySelector('i');

    if (container.style.display === 'none') {
        container.style.display = '';
        icon.className = 'fas fa-chevron-down';
    } else {
        container.style.display = 'none';
        icon.className = 'fas fa-chevron-right';
    }
}
