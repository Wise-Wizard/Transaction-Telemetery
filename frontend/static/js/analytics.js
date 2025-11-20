/**
 * Graph Analytics functionality
 */
class GraphAnalytics {
    constructor(cy, apiService) {
        this.cy = cy;
        this.apiService = apiService;
        this.highlightedElements = [];
    }

    // Helper functions for loading indicator
    showLoading() {
        document.getElementById('loading-overlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loading-overlay').style.display = 'none';
    }

    /**
     * Find and highlight the shortest path between two nodes
     * @param {string} sourceId - ID of the source node
     * @param {string} targetId - ID of the target node
     * @param {Array<string>} relationshipTypes - Optional array of relationship types to consider
     */
    async findShortestPath(sourceId, targetId, relationshipTypes = null) {
        try {
            // Clear any previous highlights
            this.clearHighlights();

            // Show loading indicator
            this.showLoading();

            // Call the API to find the shortest path
            const result = await this.apiService.findShortestPath(sourceId, targetId, relationshipTypes);

            // Hide loading indicator
            this.hideLoading();

            if (!result.found) {
                alert(`No path found between ${sourceId} and ${targetId}`);
                return;
            }

            // Highlight the path in the graph
            this.highlightPath(result);

            // Show path information
            this.showPathInfo(result);

            return result;
        } catch (error) {
            this.hideLoading();
            console.error('Error finding shortest path:', error);
            alert(`Error finding shortest path: ${error.message}`);
        }
    }

    /**
     * Highlight a path in the graph
     * @param {Object} pathData - Path data from the API
     */
    highlightPath(pathData) {
        // First, make all elements transparent
        this.cy.elements().addClass('faded');

        // Collect elements to highlight
        const nodesToHighlight = [];
        const edgesToHighlight = [];

        // Add nodes to highlight
        pathData.nodes.forEach(node => {
            const cyNode = this.cy.getElementById(node.id);
            if (cyNode.length > 0) {
                nodesToHighlight.push(cyNode);
            }
        });

        // Add edges to highlight
        pathData.relationships.forEach(rel => {
            const sourceNode = this.cy.getElementById(rel.source_id);
            const targetNode = this.cy.getElementById(rel.target_id);

            if (sourceNode.length > 0 && targetNode.length > 0) {
                const edges = sourceNode.edgesTo(targetNode);
                if (edges.length > 0) {
                    edgesToHighlight.push(edges);
                }
            }
        });

        // Highlight the elements
        const elementsToHighlight = this.cy.collection();
        nodesToHighlight.forEach(node => elementsToHighlight.merge(node));
        edgesToHighlight.forEach(edge => elementsToHighlight.merge(edge));

        elementsToHighlight.removeClass('faded').addClass('highlighted');

        // Store highlighted elements for later cleanup
        this.highlightedElements = elementsToHighlight;

        // Fit the view to the highlighted elements
        this.cy.fit(elementsToHighlight, 50);
    }

    /**
     * Show path information in a modal or panel
     * @param {Object} pathData - Path data from the API
     */
    showPathInfo(pathData) {
        // Create HTML content for the path information
        let content = `
            <div class="path-info">
                <h5>Shortest Path</h5>
                <p><strong>Path Length:</strong> ${pathData.path_length}</p>
                <p><strong>Nodes:</strong> ${pathData.nodes.length}</p>
                <p><strong>Path:</strong></p>
                <ol class="path-nodes">
        `;

        // Add nodes to the path
        pathData.nodes.forEach((node, index) => {
            const nodeType = node.labels ? node.labels[0] : 'Unknown';
            const nodeName = node.name || node.id;

            content += `<li>${nodeName} (${nodeType})</li>`;

            // Add relationship if not the last node
            if (index < pathData.relationships.length) {
                const rel = pathData.relationships[index];
                content += `<li class="path-relationship">${rel.type}</li>`;
            }
        });

        content += `
                </ol>
            </div>
        `;

        // Show the content in the node details panel
        document.getElementById('node-details-title').textContent = 'Shortest Path';
        document.getElementById('node-details-content').innerHTML = content;
        document.getElementById('node-details').classList.add('visible');
    }

    /**
     * Find and highlight transaction clusters
     * @param {number} minClusterSize - Minimum number of transactions in a cluster
     * @param {number} maxDistance - Maximum distance between transactions
     */
    async findTransactionClusters(minClusterSize = 2, maxDistance = 2) {
        try {
            // Clear any previous highlights
            this.clearHighlights();

            // Show loading indicator
            this.showLoading();

            // Call the API to find transaction clusters
            const clusters = await this.apiService.getTransactionClusters(minClusterSize, maxDistance);

            // Hide loading indicator
            this.hideLoading();

            if (clusters.length === 0) {
                alert('No transaction clusters found with the specified parameters.');
                return;
            }

            // Show clusters information
            this.showClustersInfo(clusters);

            return clusters;
        } catch (error) {
            this.hideLoading();
            console.error('Error finding transaction clusters:', error);
            alert(`Error finding transaction clusters: ${error.message}`);
        }
    }

    /**
     * Show clusters information in a modal or panel
     * @param {Array} clusters - Array of cluster data from the API
     */
    showClustersInfo(clusters) {
        // Create HTML content for the clusters information
        let content = `
            <div class="clusters-info">
                <h5>Transaction Clusters</h5>
                <p><strong>Number of Clusters:</strong> ${clusters.length}</p>
                <div class="clusters-list">
        `;

        // Add clusters to the list
        clusters.forEach((cluster, index) => {
            content += `
                <div class="cluster-item">
                    <h6>Cluster ${index + 1} (${cluster.size} transactions)</h6>
                    <p><strong>Center:</strong> ${cluster.center_transaction.id}</p>
                    <p><strong>Transactions:</strong></p>
                    <ul>
            `;

            cluster.transactions.forEach(tx => {
                const amount = tx.amount || 0;
                const currency = tx.currency || 'USD';
                content += `<li>${tx.id} (${amount} ${currency})</li>`;
            });

            content += `
                    </ul>
                    <button class="btn btn-sm btn-outline-primary highlight-cluster" data-cluster-index="${index}">
                        Highlight Cluster
                    </button>
                </div>
            `;
        });

        content += `
                </div>
            </div>
        `;

        // Show the content in the node details panel
        document.getElementById('node-details-title').textContent = 'Transaction Clusters';
        document.getElementById('node-details-content').innerHTML = content;
        document.getElementById('node-details').classList.add('visible');

        // Add event listeners to highlight cluster buttons
        document.querySelectorAll('.highlight-cluster').forEach(button => {
            button.addEventListener('click', (event) => {
                const clusterIndex = parseInt(event.target.getAttribute('data-cluster-index'));
                this.highlightCluster(clusters[clusterIndex]);
            });
        });
    }

    /**
     * Highlight a transaction cluster in the graph
     * @param {Object} cluster - Cluster data from the API
     */
    highlightCluster(cluster) {
        // First, make all elements transparent
        this.cy.elements().addClass('faded');

        // Collect elements to highlight
        const elementsToHighlight = this.cy.collection();

        // Add transactions to highlight
        cluster.transactions.forEach(tx => {
            const cyNode = this.cy.getElementById(tx.id);
            if (cyNode.length > 0) {
                elementsToHighlight.merge(cyNode);

                // Also highlight connected edges
                elementsToHighlight.merge(cyNode.connectedEdges());
            }
        });

        // Highlight the elements
        elementsToHighlight.removeClass('faded').addClass('highlighted');

        // Store highlighted elements for later cleanup
        this.highlightedElements = elementsToHighlight;

        // Fit the view to the highlighted elements
        this.cy.fit(elementsToHighlight, 50);
    }

    /**
     * Show graph metrics in a modal or panel
     */
    async showGraphMetrics() {
        try {
            // Show loading indicator
            this.showLoading();

            // Call the API to get graph metrics
            const metrics = await this.apiService.getGraphMetrics();

            // Hide loading indicator
            this.hideLoading();

            // Create HTML content for the metrics
            let content = `
                <div class="metrics-info">
                    <h5>Graph Metrics</h5>
                    <div class="metrics-summary">
                        <div class="metric-item">
                            <span class="metric-value">${metrics.total_nodes}</span>
                            <span class="metric-label">Total Nodes</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-value">${metrics.relationship_count}</span>
                            <span class="metric-label">Relationships</span>
                        </div>
                    </div>

                    <div class="metrics-detail">
                        <h6>Node Types</h6>
                        <ul>
                            <li><strong>Users:</strong> ${metrics.user_count}</li>
                            <li><strong>Companies:</strong> ${metrics.company_count}</li>
                            <li><strong>Transactions:</strong> ${metrics.transaction_count}</li>
                        </ul>

                        <h6>Relationship Types</h6>
                        <ul>
            `;

            // Add relationship type counts
            Object.entries(metrics.relationship_type_counts).forEach(([type, count]) => {
                content += `<li><strong>${type}:</strong> ${count}</li>`;
            });

            content += `
                        </ul>

                        <h6>Most Connected Nodes</h6>
                        <ul>
            `;

            // Add most connected nodes
            metrics.most_connected_nodes.forEach(node => {
                content += `<li><strong>${node.name || node.id}:</strong> ${node.connection_count} connections</li>`;
            });

            content += `
                        </ul>
                    </div>
                </div>
            `;

            // Show the content in the node details panel
            document.getElementById('node-details-title').textContent = 'Graph Metrics';
            document.getElementById('node-details-content').innerHTML = content;
            document.getElementById('node-details').classList.add('visible');
        } catch (error) {
            this.hideLoading();
            console.error('Error getting graph metrics:', error);
            alert(`Error getting graph metrics: ${error.message}`);
        }
    }

    /**
     * Clear all highlights from the graph
     */
    clearHighlights() {
        this.cy.elements().removeClass('faded').removeClass('highlighted');
        this.highlightedElements = [];
    }
}
