const { jsonResponse, errorResponse } = require('./_shared/response');
const fs = require('fs');
const path = require('path');

exports.handler = async (event, context) => {
    if (event.httpMethod !== 'GET') {
        return errorResponse('Method Not Allowed', 405);
    }

    try {
        const modelPath = path.resolve(__dirname, './_shared/models/audit_log_status.json');
        if (!fs.existsSync(modelPath)) {
            return jsonResponse({
                "audit_foundation_status": "READY_FOR_FOUNDATION_REVIEW_ONLY",
                "durable_audit_storage_configured": false,
                "append_endpoint_enabled": false,
                "immutable_chain_verified": false,
                "persistence_verified": false,
                "hash_algorithm": "SHA256",
                "current_mode": "AUDIT_FOUNDATION_ONLY"
            });
        }
        const data = fs.readFileSync(modelPath, 'utf-8');
        const model = JSON.parse(data);
        return jsonResponse(model);
    } catch (error) {
        console.error("Error reading audit log status model:", error);
        return errorResponse('Failed to load audit status', 500);
    }
};