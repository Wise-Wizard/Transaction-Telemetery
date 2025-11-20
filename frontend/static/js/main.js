/**
 * Main application script
 */
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const graphContainer = document.getElementById('graph-container');
    const loadingOverlay = document.getElementById('loading-overlay');
    const nodeDetails = document.getElementById('node-details');
    const nodeDetailsTitle = document.getElementById('node-details-title');
    const nodeDetailsContent = document.getElementById('node-details-content');
    const closeDetails = document.getElementById('close-details');
    // Sidebar toggle removed
    const sidebar = document.querySelector('.sidebar');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const layoutSelect = document.getElementById('layout-select');
    const applyLayout = document.getElementById('apply-layout');
    const refreshData = document.getElementById('refresh-data');
    const detectRelationships = document.getElementById('detect-relationships');
    const exportImage = document.getElementById('export-image');
    const exportJson = document.getElementById('export-json');
    const exportCsv = document.getElementById('export-csv');
    const resetView = document.getElementById('reset-view');
    const zoomIn = document.getElementById('zoom-in');
    const zoomOut = document.getElementById('zoom-out');
    const fitGraph = document.getElementById('fit-graph');
    const nodeCount = document.getElementById('node-count');
    const edgeCount = document.getElementById('edge-count');

    // Analytics elements
    const shortestPathSource = document.getElementById('shortest-path-source');
    const shortestPathTarget = document.getElementById('shortest-path-target');
    const findShortestPath = document.getElementById('find-shortest-path');
    const clusterMinSize = document.getElementById('cluster-min-size');
    const clusterMaxDistance = document.getElementById('cluster-max-distance');
    const findTransactionClusters = document.getElementById('find-transaction-clusters');
    const showGraphMetrics = document.getElementById('show-graph-metrics');

    // Filter checkboxes
    const filterUsers = document.getElementById('filter-users');
    const filterCompanies = document.getElementById('filter-companies');
    const filterTransactions = document.getElementById('filter-transactions');
    const filterParentChild = document.getElementById('filter-parent-child');
    const filterDirector = document.getElementById('filter-director');
    const filterShareholder = document.getElementById('filter-shareholder');
    const filterLegalEntity = document.getElementById('filter-legal-entity');
    const filterComposite = document.getElementById('filter-composite');
    const filterSharedAttributes = document.getElementById('filter-shared-attributes');
    const filterTransaction = document.getElementById('filter-transaction');

    // Cytoscape instance
    let cy = null;

    // Graph data
    let graphData = {
        nodes: [],
        edges: []
    };

    /**
     * Initialize the Cytoscape graph
     */
    function initGraph() {
        cy = cytoscape({
            container: graphContainer,
            elements: [],
            style: GRAPH_STYLES,
            layout: CONFIG.LAYOUTS['cola'],
            minZoom: 0.1,
            maxZoom: 3,
            wheelSensitivity: 0.2
        });

        // Add event listeners
        cy.on('tap', 'node', function(evt) {
            const node = evt.target;
            showNodeDetails(node);
        });

        cy.on('tap', function(evt) {
            if (evt.target === cy) {
                hideNodeDetails();
            }
        });
    }

    /**
     * Load all data from the API
     */
    async function loadData() {
        showLoading();

        try {
            // Reset graph data
            graphData = {
                nodes: [],
                edges: []
            };

            // Fetch users and transactions
            const [users, transactions] = await Promise.all([
                apiService.getUsers(),
                apiService.getTransactions()
            ]);

            // Process users
            for (const user of users) {
                const nodeType = GraphUtils.getNodeType(user);

                graphData.nodes.push({
                    data: {
                        id: user.id,
                        label: GraphUtils.getNodeLabel(user),
                        type: nodeType,
                        size: GraphUtils.getNodeSize(user),
                        ...user
                    }
                });

                // Fetch relationships for each user
                try {
                    const userRelationships = await apiService.getUserRelationships(user.id);
                    processUserRelationships(userRelationships);

                    // Fetch business relationships if it's a user or company
                    if (nodeType !== CONFIG.NODE_TYPES.TRANSACTION) {
                        try {
                            const businessRelationships = await apiService.getBusinessRelationships(user.id);
                            processBusinessRelationships(businessRelationships);
                        } catch (error) {
                            console.warn(`Could not fetch business relationships for ${user.id}:`, error);
                        }
                    }
                } catch (error) {
                    console.warn(`Could not fetch relationships for ${user.id}:`, error);
                }
            }

            // Process transactions
            for (const transaction of transactions) {
                graphData.nodes.push({
                    data: {
                        id: transaction.id,
                        label: GraphUtils.getNodeLabel(transaction),
                        type: CONFIG.NODE_TYPES.TRANSACTION,
                        size: GraphUtils.getNodeSize(transaction),
                        ...transaction
                    }
                });

                // Fetch relationships for each transaction
                try {
                    const transactionRelationships = await apiService.getTransactionRelationships(transaction.id);
                    processTransactionRelationships(transactionRelationships);
                } catch (error) {
                    console.warn(`Could not fetch relationships for transaction ${transaction.id}:`, error);
                }
            }

            // Remove duplicate edges
            const uniqueEdges = {};
            graphData.edges.forEach(edge => {
                const edgeId = edge.data.id;
                uniqueEdges[edgeId] = edge;
            });
            graphData.edges = Object.values(uniqueEdges);

            // Update the graph
            updateGraph();
        } catch (error) {
            console.error('Error loading data:', error);
            alert('Error loading data. Please check the console for details.');
        } finally {
            hideLoading();
        }
    }

    /**
     * Process user relationships
     * @param {Object} relationshipData - The relationship data from the API
     */
    function processUserRelationships(relationshipData) {
        if (!relationshipData || !relationshipData.relationships) return;

        const { user, relationships } = relationshipData;
        const userId = user.id;

        // Process outgoing relationships
        if (relationships.outgoing) {
            relationships.outgoing.forEach(rel => {
                if (!rel.node || !rel.type) return;

                const targetId = rel.node.id;
                if (!targetId) return;

                // Add the target node if it doesn't exist
                if (!graphData.nodes.some(n => n.data.id === targetId)) {
                    const nodeType = GraphUtils.getNodeType(rel.node);
                    graphData.nodes.push({
                        data: {
                            id: targetId,
                            label: GraphUtils.getNodeLabel(rel.node),
                            type: nodeType,
                            size: GraphUtils.getNodeSize(rel.node),
                            ...rel.node
                        }
                    });
                }

                // Add the edge
                const edgeId = GraphUtils.getEdgeId(userId, targetId, rel.type);
                graphData.edges.push({
                    data: {
                        id: edgeId,
                        source: userId,
                        target: targetId,
                        type: rel.type,
                        label: rel.type
                    }
                });
            });
        }

        // Process incoming relationships
        if (relationships.incoming) {
            relationships.incoming.forEach(rel => {
                if (!rel.node || !rel.type) return;

                const sourceId = rel.node.id;
                if (!sourceId) return;

                // Add the source node if it doesn't exist
                if (!graphData.nodes.some(n => n.data.id === sourceId)) {
                    const nodeType = GraphUtils.getNodeType(rel.node);
                    graphData.nodes.push({
                        data: {
                            id: sourceId,
                            label: GraphUtils.getNodeLabel(rel.node),
                            type: nodeType,
                            size: GraphUtils.getNodeSize(rel.node),
                            ...rel.node
                        }
                    });
                }

                // Add the edge
                const edgeId = GraphUtils.getEdgeId(sourceId, userId, rel.type);
                graphData.edges.push({
                    data: {
                        id: edgeId,
                        source: sourceId,
                        target: userId,
                        type: rel.type,
                        label: rel.type
                    }
                });
            });
        }
    }

    /**
     * Process business relationships
     * @param {Object} relationshipData - The business relationship data from the API
     */
    function processBusinessRelationships(relationshipData) {
        if (!relationshipData || !relationshipData.business_relationships) return;

        const { user, business_relationships } = relationshipData;
        const userId = user.id;

        // Process outgoing business relationships
        if (business_relationships.outgoing) {
            business_relationships.outgoing.forEach(rel => {
                if (!rel.node || !rel.type) return;

                const targetId = rel.node.id;
                if (!targetId) return;

                // Add the target node if it doesn't exist
                if (!graphData.nodes.some(n => n.data.id === targetId)) {
                    const nodeType = GraphUtils.getNodeType(rel.node);
                    graphData.nodes.push({
                        data: {
                            id: targetId,
                            label: GraphUtils.getNodeLabel(rel.node),
                            type: nodeType,
                            size: GraphUtils.getNodeSize(rel.node),
                            ...rel.node
                        }
                    });
                }

                // Add the edge
                const edgeId = GraphUtils.getEdgeId(userId, targetId, rel.type);
                graphData.edges.push({
                    data: {
                        id: edgeId,
                        source: userId,
                        target: targetId,
                        type: rel.type,
                        label: rel.type,
                        properties: rel.properties
                    }
                });
            });
        }

        // Process incoming business relationships
        if (business_relationships.incoming) {
            business_relationships.incoming.forEach(rel => {
                if (!rel.node || !rel.type) return;

                const sourceId = rel.node.id;
                if (!sourceId) return;

                // Add the source node if it doesn't exist
                if (!graphData.nodes.some(n => n.data.id === sourceId)) {
                    const nodeType = GraphUtils.getNodeType(rel.node);
                    graphData.nodes.push({
                        data: {
                            id: sourceId,
                            label: GraphUtils.getNodeLabel(rel.node),
                            type: nodeType,
                            size: GraphUtils.getNodeSize(rel.node),
                            ...rel.node
                        }
                    });
                }

                // Add the edge
                const edgeId = GraphUtils.getEdgeId(sourceId, userId, rel.type);
                graphData.edges.push({
                    data: {
                        id: edgeId,
                        source: sourceId,
                        target: userId,
                        type: rel.type,
                        label: rel.type,
                        properties: rel.properties
                    }
                });
            });
        }
    }

    /**
     * Process transaction relationships
     * @param {Object} relationshipData - The transaction relationship data from the API
     */
    function processTransactionRelationships(relationshipData) {
        if (!relationshipData) return;

        const { transaction, relationships } = relationshipData;
        const transactionId = transaction.id;

        // Process incoming users (senders)
        if (relationships.incoming_users) {
            relationships.incoming_users.forEach(rel => {
                if (!rel.node || !rel.type) return;

                const sourceId = rel.node.id;
                if (!sourceId) return;

                // Add the source node if it doesn't exist
                if (!graphData.nodes.some(n => n.data.id === sourceId)) {
                    const nodeType = GraphUtils.getNodeType(rel.node);
                    graphData.nodes.push({
                        data: {
                            id: sourceId,
                            label: GraphUtils.getNodeLabel(rel.node),
                            type: nodeType,
                            size: GraphUtils.getNodeSize(rel.node),
                            ...rel.node
                        }
                    });
                }

                // Add the edge
                const edgeId = GraphUtils.getEdgeId(sourceId, transactionId, rel.type);
                graphData.edges.push({
                    data: {
                        id: edgeId,
                        source: sourceId,
                        target: transactionId,
                        type: rel.type,
                        label: rel.type
                    }
                });
            });
        }

        // Process outgoing users (receivers)
        if (relationships.outgoing_users) {
            relationships.outgoing_users.forEach(rel => {
                if (!rel.node || !rel.type) return;

                const targetId = rel.node.id;
                if (!targetId) return;

                // Add the target node if it doesn't exist
                if (!graphData.nodes.some(n => n.data.id === targetId)) {
                    const nodeType = GraphUtils.getNodeType(rel.node);
                    graphData.nodes.push({
                        data: {
                            id: targetId,
                            label: GraphUtils.getNodeLabel(rel.node),
                            type: nodeType,
                            size: GraphUtils.getNodeSize(rel.node),
                            ...rel.node
                        }
                    });
                }

                // Add the edge
                const edgeId = GraphUtils.getEdgeId(transactionId, targetId, rel.type);
                graphData.edges.push({
                    data: {
                        id: edgeId,
                        source: transactionId,
                        target: targetId,
                        type: rel.type,
                        label: rel.type
                    }
                });
            });
        }

        // Process linked transactions
        if (relationships.linked_transactions) {
            relationships.linked_transactions.forEach(rel => {
                if (!rel.node || !rel.type) return;

                const linkedId = rel.node.id;
                if (!linkedId) return;

                // Add the linked transaction node if it doesn't exist
                if (!graphData.nodes.some(n => n.data.id === linkedId)) {
                    graphData.nodes.push({
                        data: {
                            id: linkedId,
                            label: GraphUtils.getNodeLabel(rel.node),
                            type: CONFIG.NODE_TYPES.TRANSACTION,
                            size: GraphUtils.getNodeSize(rel.node),
                            ...rel.node
                        }
                    });
                }

                // Add the edge (undirected)
                const edgeId = GraphUtils.getEdgeId(transactionId, linkedId, rel.type);
                graphData.edges.push({
                    data: {
                        id: edgeId,
                        source: transactionId,
                        target: linkedId,
                        type: rel.type,
                        label: rel.type
                    }
                });
            });
        }
    }

    /**
     * Update the graph with the current data and filters
     */
    function updateGraph() {
        // Apply filters
        const filteredNodes = graphData.nodes.filter(node => {
            const nodeType = node.data.type;

            if (nodeType === CONFIG.NODE_TYPES.USER && !filterUsers.checked) {
                return false;
            }

            if (nodeType === CONFIG.NODE_TYPES.COMPANY && !filterCompanies.checked) {
                return false;
            }

            if (nodeType === CONFIG.NODE_TYPES.TRANSACTION && !filterTransactions.checked) {
                return false;
            }

            return true;
        });

        const filteredNodeIds = filteredNodes.map(node => node.data.id);

        const filteredEdges = graphData.edges.filter(edge => {
            const edgeType = edge.data.type;
            const sourceId = edge.data.source;
            const targetId = edge.data.target;

            // Filter out edges connected to filtered-out nodes
            if (!filteredNodeIds.includes(sourceId) || !filteredNodeIds.includes(targetId)) {
                return false;
            }

            // Apply relationship type filters
            if (GraphUtils.relationshipBelongsToCategory(edgeType, 'PARENT_CHILD') && !filterParentChild.checked) {
                return false;
            }

            if (GraphUtils.relationshipBelongsToCategory(edgeType, 'DIRECTOR') && !filterDirector.checked) {
                return false;
            }

            if (GraphUtils.relationshipBelongsToCategory(edgeType, 'SHAREHOLDER') && !filterShareholder.checked) {
                return false;
            }

            if (GraphUtils.relationshipBelongsToCategory(edgeType, 'LEGAL_ENTITY') && !filterLegalEntity.checked) {
                return false;
            }

            if (GraphUtils.relationshipBelongsToCategory(edgeType, 'COMPOSITE') && !filterComposite.checked) {
                return false;
            }

            if (GraphUtils.relationshipBelongsToCategory(edgeType, 'SHARED_ATTRIBUTES') && !filterSharedAttributes.checked) {
                return false;
            }

            if (GraphUtils.relationshipBelongsToCategory(edgeType, 'TRANSACTION') && !filterTransaction.checked) {
                return false;
            }

            return true;
        });

        // Update the graph
        cy.elements().remove();
        cy.add([...filteredNodes, ...filteredEdges]);

        // Apply layout
        applyCurrentLayout();

        // Update counts
        updateCounts();
    }

    /**
     * Apply the currently selected layout
     */
    function applyCurrentLayout() {
        const layoutName = layoutSelect.value;
        const layout = cy.layout(CONFIG.LAYOUTS[layoutName]);
        layout.run();
    }

    /**
     * Update the node and edge counts
     */
    function updateCounts() {
        nodeCount.textContent = `Nodes: ${cy.nodes().length}`;
        edgeCount.textContent = `Edges: ${cy.edges().length}`;
    }

    /**
     * Show node details in the panel
     * @param {Object} node - The Cytoscape node
     */
    function showNodeDetails(node) {
        // Set the title based on node type
        const data = node.data();
        const type = data.type;
        let title = '';

        if (type === CONFIG.NODE_TYPES.TRANSACTION) {
            if (data.metadata && data.metadata.purpose) {
                title = data.metadata.purpose.charAt(0).toUpperCase() + data.metadata.purpose.slice(1);
            } else {
                title = `Transaction ${data.id.replace('tx', '#')}`;
            }
        } else if (type === CONFIG.NODE_TYPES.COMPANY) {
            title = data.company_name || data.name;
        } else {
            title = data.name;
        }

        nodeDetailsTitle.textContent = title;
        nodeDetailsContent.innerHTML = GraphUtils.generateNodeDetailsHTML(node);
        nodeDetails.classList.add('visible');

        // Add event listeners to node links
        document.querySelectorAll('.node-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const nodeId = this.getAttribute('data-node-id');
                const targetNode = cy.getElementById(nodeId);
                if (targetNode.length > 0) {
                    cy.fit(targetNode, 100);
                    cy.center(targetNode);
                    showNodeDetails(targetNode);
                }
            });
        });
    }

    /**
     * Hide the node details panel
     */
    function hideNodeDetails() {
        nodeDetails.classList.remove('visible');
    }

    /**
     * Show the loading overlay
     */
    function showLoading() {
        loadingOverlay.style.display = 'flex';
    }

    /**
     * Hide the loading overlay
     */
    function hideLoading() {
        loadingOverlay.style.display = 'none';
    }

    /**
     * Search for nodes by label
     * @param {string} query - The search query
     */
    function searchNodes(query) {
        if (!query) return;

        const lowerQuery = query.toLowerCase();
        const matchingNodes = cy.nodes().filter(node => {
            const label = node.data('label').toLowerCase();
            return label.includes(lowerQuery);
        });

        if (matchingNodes.length > 0) {
            cy.fit(matchingNodes, 100);

            // Highlight matching nodes
            cy.nodes().removeClass('highlighted');
            matchingNodes.addClass('highlighted');

            // If only one node matches, show its details
            if (matchingNodes.length === 1) {
                showNodeDetails(matchingNodes[0]);
            }
        } else {
            alert('No matching nodes found.');
        }
    }

    /**
     * Export the graph as an image
     */
    function exportGraphImage() {
        const png64 = cy.png({
            output: 'blob',
            bg: 'white',
            full: true,
            scale: 2
        });

        const link = document.createElement('a');
        link.href = URL.createObjectURL(png64);
        link.download = 'graph-export.png';
        link.click();
    }

    /**
     * Initialize the application
     */
    function init() {
        // Initialize the graph
        initGraph();

        // Initialize analytics
        const analytics = new GraphAnalytics(cy, apiService);

        // Load data
        loadData();

        // Event listeners

        closeDetails.addEventListener('click', hideNodeDetails);

        searchBtn.addEventListener('click', function() {
            searchNodes(searchInput.value);
        });

        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchNodes(searchInput.value);
            }
        });

        applyLayout.addEventListener('click', applyCurrentLayout);

        refreshData.addEventListener('click', loadData);

        detectRelationships.addEventListener('click', async function() {
            showLoading();
            try {
                await apiService.detectRelationships();
                await loadData();
                alert('Relationships detected and created successfully.');
            } catch (error) {
                console.error('Error detecting relationships:', error);
                alert('Error detecting relationships. Please check the console for details.');
            } finally {
                hideLoading();
            }
        });

        exportImage.addEventListener('click', exportGraphImage);

        exportJson.addEventListener('click', function() {
            apiService.exportAsJson();
        });

        exportCsv.addEventListener('click', function() {
            apiService.exportAsCsv();
        });

        resetView.addEventListener('click', function() {
            cy.fit();
            cy.center();
            cy.nodes().removeClass('highlighted');
            analytics.clearHighlights();
            hideNodeDetails();
        });

        zoomIn.addEventListener('click', function() {
            cy.zoom(cy.zoom() * 1.2);
        });

        zoomOut.addEventListener('click', function() {
            cy.zoom(cy.zoom() / 1.2);
        });

        fitGraph.addEventListener('click', function() {
            cy.fit();
        });

        // Analytics event listeners
        findShortestPath.addEventListener('click', function() {
            const sourceId = shortestPathSource.value.trim();
            const targetId = shortestPathTarget.value.trim();

            if (!sourceId || !targetId) {
                alert('Please enter both source and target IDs.');
                return;
            }

            analytics.findShortestPath(sourceId, targetId);
        });

        findTransactionClusters.addEventListener('click', function() {
            const minSize = parseInt(clusterMinSize.value) || 2;
            const maxDistance = parseInt(clusterMaxDistance.value) || 2;

            analytics.findTransactionClusters(minSize, maxDistance);
        });

        showGraphMetrics.addEventListener('click', function() {
            analytics.showGraphMetrics();
        });

        // Filter change events
        const filterElements = [
            filterUsers, filterCompanies, filterTransactions,
            filterParentChild, filterDirector, filterShareholder,
            filterLegalEntity, filterComposite, filterSharedAttributes,
            filterTransaction
        ];

        filterElements.forEach(filter => {
            filter.addEventListener('change', updateGraph);
        });
    }

    // Initialize the application
    init();
});
