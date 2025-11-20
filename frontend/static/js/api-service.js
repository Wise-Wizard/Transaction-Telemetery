/**
 * API Service for interacting with the backend
 */
class ApiService {
    constructor(config) {
        this.config = config;
    }

    /**
     * Fetch all users from the API
     * @returns {Promise<Array>} Array of user objects
     */
    async getUsers() {
        try {
            const response = await fetch(`${this.config.BASE_URL}${this.config.USERS}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching users:', error);
            throw error;
        }
    }

    /**
     * Fetch all transactions from the API
     * @returns {Promise<Array>} Array of transaction objects
     */
    async getTransactions() {
        try {
            const response = await fetch(`${this.config.BASE_URL}${this.config.TRANSACTIONS}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching transactions:', error);
            throw error;
        }
    }

    /**
     * Fetch relationships for a specific user
     * @param {string} userId - The ID of the user
     * @returns {Promise<Object>} User relationship data
     */
    async getUserRelationships(userId) {
        try {
            const response = await fetch(`${this.config.BASE_URL}${this.config.USER_RELATIONSHIPS}${userId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error fetching relationships for user ${userId}:`, error);
            throw error;
        }
    }

    /**
     * Fetch business relationships for a specific user
     * @param {string} userId - The ID of the user
     * @returns {Promise<Object>} Business relationship data
     */
    async getBusinessRelationships(userId) {
        try {
            const response = await fetch(`${this.config.BASE_URL}${this.config.BUSINESS_RELATIONSHIPS}${userId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error fetching business relationships for user ${userId}:`, error);
            throw error;
        }
    }

    /**
     * Fetch relationships for a specific transaction
     * @param {string} transactionId - The ID of the transaction
     * @returns {Promise<Object>} Transaction relationship data
     */
    async getTransactionRelationships(transactionId) {
        try {
            const response = await fetch(`${this.config.BASE_URL}${this.config.TRANSACTION_RELATIONSHIPS}${transactionId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error fetching relationships for transaction ${transactionId}:`, error);
            throw error;
        }
    }

    /**
     * Trigger relationship detection on the server
     * @returns {Promise<Object>} Response from the server
     */
    async detectRelationships() {
        try {
            const response = await fetch(`${this.config.BASE_URL}${this.config.DETECT_RELATIONSHIPS}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error detecting relationships:', error);
            throw error;
        }
    }

    /**
     * Find the shortest path between two nodes
     * @param {string} sourceId - The ID of the source node
     * @param {string} targetId - The ID of the target node
     * @param {Array<string>} relationshipTypes - Optional array of relationship types to consider
     * @returns {Promise<Object>} Shortest path data
     */
    async findShortestPath(sourceId, targetId, relationshipTypes = null) {
        try {
            let url = `${this.config.BASE_URL}${this.config.SHORTEST_PATH}?source_id=${sourceId}&target_id=${targetId}`;

            // Add relationship types if provided
            if (relationshipTypes && relationshipTypes.length > 0) {
                relationshipTypes.forEach(type => {
                    url += `&relationship_types=${encodeURIComponent(type)}`;
                });
            }

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error finding shortest path:', error);
            throw error;
        }
    }

    /**
     * Get transaction clusters
     * @param {number} minClusterSize - Minimum number of transactions in a cluster
     * @param {number} maxDistance - Maximum distance between transactions
     * @returns {Promise<Array>} Array of transaction clusters
     */
    async getTransactionClusters(minClusterSize = 2, maxDistance = 2) {
        try {
            const url = `${this.config.BASE_URL}${this.config.TRANSACTION_CLUSTERS}?min_cluster_size=${minClusterSize}&max_distance=${maxDistance}`;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error getting transaction clusters:', error);
            throw error;
        }
    }

    /**
     * Get graph metrics
     * @returns {Promise<Object>} Graph metrics data
     */
    async getGraphMetrics() {
        try {
            const response = await fetch(`${this.config.BASE_URL}${this.config.GRAPH_METRICS}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error getting graph metrics:', error);
            throw error;
        }
    }

    /**
     * Export graph data as JSON
     * Triggers a file download
     */
    exportAsJson() {
        window.open(`${this.config.BASE_URL}${this.config.EXPORT_JSON}`);
    }

    /**
     * Export graph data as CSV
     * Triggers a file download
     */
    exportAsCsv() {
        window.open(`${this.config.BASE_URL}${this.config.EXPORT_CSV}`);
    }
}

// Create an instance of the API service
const apiService = new ApiService(CONFIG.API);
