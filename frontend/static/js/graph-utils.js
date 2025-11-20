/**
 * Utility functions for graph visualization
 */
class GraphUtils {
    /**
     * Determine the node type based on entity properties
     * @param {Object} entity - The entity object
     * @returns {string} The node type (user, company, transaction)
     */
    static getNodeType(entity) {
        // First, check for explicit type if it exists
        if (entity.type && Object.values(CONFIG.NODE_TYPES).includes(entity.type)) {
            return entity.type;
        }

        // Check for transaction-specific properties
        if (entity.amount !== undefined && (entity.sender_id !== undefined || entity.receiver_id !== undefined)) {
            return CONFIG.NODE_TYPES.TRANSACTION;
        }

        // Check for transaction IDs (they typically start with 'tx')
        if (entity.id && (entity.id.startsWith('tx') || entity.id.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i))) {
            // Check if it has transaction-like properties
            if (entity.amount !== undefined || entity.currency !== undefined || entity.metadata !== undefined) {
                return CONFIG.NODE_TYPES.TRANSACTION;
            }
        }

        // Check for company-specific properties
        if (entity.entity_type === 'company' || entity.company_name || entity.company_id || entity.incorporation_date) {
            return CONFIG.NODE_TYPES.COMPANY;
        }

        // Default to user if no other type is detected
        return CONFIG.NODE_TYPES.USER;
    }

    /**
     * Generate a label for a node based on its type and properties
     * @param {Object} entity - The entity object
     * @returns {string} The node label
     */
    static getNodeLabel(entity) {
        if (this.getNodeType(entity) === CONFIG.NODE_TYPES.TRANSACTION) {
            // Create a descriptive name for transactions
            let purpose = '';
            if (entity.metadata && entity.metadata.purpose) {
                purpose = entity.metadata.purpose;
            }

            // Format the transaction amount with commas for thousands
            const formattedAmount = new Intl.NumberFormat('en-US', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 2
            }).format(entity.amount);

            // If we have a purpose, use it in the label
            if (purpose) {
                // Capitalize the first letter of the purpose
                const capitalizedPurpose = purpose.charAt(0).toUpperCase() + purpose.slice(1);
                return `${capitalizedPurpose} (${formattedAmount} ${entity.currency || 'USD'})`;
            } else {
                // If no purpose, use a generic transaction label with ID
                return `Transaction ${entity.id.replace('tx', '#')} (${formattedAmount} ${entity.currency || 'USD'})`;
            }
        } else if (this.getNodeType(entity) === CONFIG.NODE_TYPES.COMPANY) {
            return entity.company_name || entity.name;
        } else {
            return entity.name;
        }
    }

    /**
     * Determine the node size based on its type and properties
     * @param {Object} entity - The entity object
     * @returns {number} The node size
     */
    static getNodeSize(entity) {
        const type = this.getNodeType(entity);

        if (type === CONFIG.NODE_TYPES.TRANSACTION) {
            // Scale transaction size based on amount
            const amount = entity.amount || 0;
            return Math.min(Math.max(30 + Math.log10(amount) * 10, 30), 80);
        } else if (type === CONFIG.NODE_TYPES.COMPANY) {
            return 60;
        } else {
            return 40;
        }
    }

    /**
     * Generate a unique ID for an edge
     * @param {string} sourceId - The source node ID
     * @param {string} targetId - The target node ID
     * @param {string} type - The relationship type
     * @returns {string} The edge ID
     */
    static getEdgeId(sourceId, targetId, type) {
        return `${sourceId}-${type}-${targetId}`;
    }

    /**
     * Format a value for display in the details panel
     * @param {*} value - The value to format
     * @param {string} key - The property key (optional)
     * @returns {string} The formatted value
     */
    static formatValue(value, key = '') {
        if (value === null || value === undefined) {
            return '-';
        } else if (typeof value === 'object') {
            // Special handling for shareholders array
            if (key === 'shareholders' && Array.isArray(value)) {
                return this.formatShareholders(value);
            }
            // Special handling for directors array
            else if (key === 'directors' && Array.isArray(value)) {
                return this.formatDirectors(value);
            }
            // General array handling
            else if (Array.isArray(value)) {
                return value.map(item => {
                    if (typeof item === 'object') {
                        return JSON.stringify(item);
                    } else {
                        return String(item);
                    }
                }).join(', ');
            }
            // Object handling
            else {
                return JSON.stringify(value, null, 2)
                    .replace(/[{}"]/g, '')
                    .replace(/,/g, ', ')
                    .trim();
            }
        } else if (typeof value === 'boolean') {
            return value ? 'Yes' : 'No';
        } else {
            return String(value);
        }
    }

    /**
     * Format shareholders data for display
     * @param {Array} shareholders - Array of shareholder objects
     * @returns {string} Formatted HTML for shareholders
     */
    static formatShareholders(shareholders) {
        if (!shareholders || !Array.isArray(shareholders) || shareholders.length === 0) {
            return '-';
        }

        let html = '<ul class="list-unstyled mb-0">';

        shareholders.forEach(shareholder => {
            if (shareholder && shareholder.id) {
                const percentage = shareholder.percentage ? shareholder.percentage : 0;
                const entityId = shareholder.id;

                html += `
                    <li class="shareholder-item">
                        <div class="d-flex justify-content-between align-items-center w-100">
                            <strong>${entityId}</strong>
                            <span class="percentage-badge">${percentage}%</span>
                        </div>
                    </li>
                `;
            }
        });

        html += '</ul>';
        return html;
    }

    /**
     * Format directors data for display
     * @param {Array} directors - Array of director IDs
     * @returns {string} Formatted HTML for directors
     */
    static formatDirectors(directors) {
        if (!directors || !Array.isArray(directors) || directors.length === 0) {
            return '-';
        }

        // If directors is a string, convert it to an array
        if (typeof directors === 'string') {
            directors = [directors];
        }

        let html = '<ul class="list-unstyled mb-0">';

        directors.forEach(director => {
            html += `
                <li>
                    <div class="d-flex align-items-center">
                        <i class="fas fa-user-tie me-2"></i>
                        <strong>${director}</strong>
                    </div>
                </li>
            `;
        });

        html += '</ul>';
        return html;
    }

    /**
     * Generate HTML for displaying node details
     * @param {Object} node - The node data
     * @returns {string} HTML content for the details panel
     */
    static generateNodeDetailsHTML(node) {
        const data = node.data();
        const type = data.type;

        // Customize title based on node type
        let title = '';
        let nodeTypeDisplay = '';

        if (type === CONFIG.NODE_TYPES.TRANSACTION) {
            nodeTypeDisplay = 'Transaction';
            title = 'Transaction Details';
            if (data.metadata && data.metadata.purpose) {
                title = data.metadata.purpose.charAt(0).toUpperCase() + data.metadata.purpose.slice(1);
            }
        } else if (type === CONFIG.NODE_TYPES.COMPANY) {
            nodeTypeDisplay = 'Company';
            title = data.company_name || data.name || 'Company Details';
        } else {
            nodeTypeDisplay = 'User';
            title = data.name || 'User Details';
        }

        // Add a badge with the node type
        const typeBadge = `<span class="badge ${type === CONFIG.NODE_TYPES.TRANSACTION ? 'bg-warning text-dark' :
                                              type === CONFIG.NODE_TYPES.COMPANY ? 'bg-success' :
                                              'bg-primary'} me-2">${nodeTypeDisplay}</span>`;


        let html = `<h6>${typeBadge}${title}</h6>`;
        html += '<table class="table table-sm">';
        html += '<tbody>';

        // Common properties to exclude from the details
        const excludeProps = ['id', 'label', 'type', 'size'];

        // For transactions, customize the display order and formatting
        if (type === CONFIG.NODE_TYPES.TRANSACTION) {
            // Format amount with commas
            const formattedAmount = new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: data.currency || 'USD',
                minimumFractionDigits: 2
            }).format(data.amount);

            html += `
                <tr>
                    <th>Metadata</th>
                    <td>${this.formatValue(data.metadata, 'metadata')}</td>
                </tr>
                <tr>
                    <th>Amount</th>
                    <td>${formattedAmount}</td>
                </tr>
                <tr>
                    <th>Device Id</th>
                    <td>${this.formatValue(data.device_id, 'device_id')}</td>
                </tr>
                <tr>
                    <th>Currency</th>
                    <td>${this.formatValue(data.currency, 'currency')}</td>
                </tr>
                <tr>
                    <th>Ip Address</th>
                    <td>${this.formatValue(data.ip_address, 'ip_address')}</td>
                </tr>
                <tr>
                    <th>Status</th>
                    <td>${this.formatValue(data.status || 'completed', 'status')}</td>
                </tr>
                <tr>
                    <th>Timestamp</th>
                    <td>${this.formatValue(data.timestamp || new Date().toISOString(), 'timestamp')}</td>
                </tr>
            `;
        } else {
            // For other node types, add all properties to the table
            for (const [key, value] of Object.entries(data)) {
                if (!excludeProps.includes(key)) {
                    const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    html += `
                        <tr>
                            <th>${formattedKey}</th>
                            <td>${this.formatValue(value, key)}</td>
                        </tr>
                    `;
                }
            }
        }

        html += '</tbody></table>';

        // Add related nodes section
        html += '<h6 class="mt-3">Connected Nodes</h6>';
        const connectedEdges = node.connectedEdges();

        if (connectedEdges.length === 0) {
            html += '<p>No connections found.</p>';
        } else {
            // For transactions, show SENT and RECEIVED_BY sections
            if (type === CONFIG.NODE_TYPES.TRANSACTION) {
                html += '<div class="transaction-connections">';

                // Find sender and receiver
                let sender = null;
                let receiver = null;

                connectedEdges.forEach(edge => {
                    const edgeType = edge.data('type');
                    const sourceId = edge.data('source');
                    const targetId = edge.data('target');
                    const otherNodeId = sourceId === data.id ? targetId : sourceId;
                    const otherNode = edge.cy().getElementById(otherNodeId);

                    if (otherNode.length > 0) {
                        if (edgeType === 'SENT' && sourceId !== data.id) {
                            sender = {
                                id: otherNodeId,
                                label: otherNode.data('label')
                            };
                        } else if (edgeType === 'RECEIVED_BY' && targetId !== data.id) {
                            receiver = {
                                id: otherNodeId,
                                label: otherNode.data('label')
                            };
                        }
                    }
                });

                // Display sender
                html += '<div class="mb-3"><strong>SENT</strong>';
                if (sender) {
                    html += `<ul class="list-unstyled ms-3">
                        <li>
                            <span class="badge bg-secondary me-1">From</span>
                            <a href="#" class="node-link" data-node-id="${sender.id}">
                                ${sender.label} ←
                            </a>
                        </li>
                    </ul>`;
                } else {
                    html += '<p class="ms-3 text-muted">No sender information</p>';
                }
                html += '</div>';

                // Display receiver
                html += '<div><strong>RECEIVED_BY</strong>';
                if (receiver) {
                    html += `<ul class="list-unstyled ms-3">
                        <li>
                            <span class="badge bg-secondary me-1">To</span>
                            <a href="#" class="node-link" data-node-id="${receiver.id}">
                                ${receiver.label} →
                            </a>
                        </li>
                    </ul>`;
                } else {
                    html += '<p class="ms-3 text-muted">No receiver information</p>';
                }
                html += '</div>';

                html += '</div>';
            } else {
                // For other node types, use the original grouping by relationship type
                html += '<ul class="list-group">';

                // Group edges by type
                const edgesByType = {};
                connectedEdges.forEach(edge => {
                    const edgeType = edge.data('type');
                    if (!edgesByType[edgeType]) {
                        edgesByType[edgeType] = [];
                    }

                    const sourceId = edge.data('source');
                    const targetId = edge.data('target');
                    const otherNodeId = sourceId === data.id ? targetId : sourceId;
                    const otherNode = edge.cy().getElementById(otherNodeId);

                    if (otherNode.length > 0) {
                        edgesByType[edgeType].push({
                            id: otherNodeId,
                            label: otherNode.data('label'),
                            direction: sourceId === data.id ? 'outgoing' : 'incoming'
                        });
                    }
                });

                // Display grouped connections
                for (const [type, connections] of Object.entries(edgesByType)) {
                    html += `<li class="list-group-item">
                        <strong>${type}</strong>
                        <ul class="mt-1">`;

                    connections.forEach(conn => {
                        const directionIcon = conn.direction === 'outgoing' ? '→' : '←';
                        html += `<li>
                            <a href="#" class="node-link" data-node-id="${conn.id}">
                                ${conn.label} ${directionIcon}
                            </a>
                        </li>`;
                    });

                    html += `</ul></li>`;
                }

                html += '</ul>';
            }
        }

        return html;
    }

    /**
     * Check if a relationship type belongs to a category
     * @param {string} type - The relationship type
     * @param {string} category - The category name
     * @returns {boolean} True if the type belongs to the category
     */
    static relationshipBelongsToCategory(type, category) {
        return CONFIG.RELATIONSHIP_CATEGORIES[category].includes(type);
    }
}
