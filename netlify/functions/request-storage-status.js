const { jsonResponse, errorResponse } = require('./_shared/response');
const fs = require('fs');
const path = require('path');

exports.handler = async (event, context) => {
    if (event.httpMethod !== 'GET') {
        return errorResponse('Method Not Allowed', 405);
    }

    try {
        const modelPath = path.resolve(__dirname, './_shared/models/request_storage_status.json');
        if (!fs.existsSync(modelPath)) {
            // Fallback for local build process before deployment
            return jsonResponse({
                "storage_foundation_status": "READY_FOR_FOUNDATION_REVIEW_ONLY",
                "durable_storage_configured": false,
                "write_endpoint_enabled": false,
                "persistence_verified": false,
                "current_mode": "STORAGE_FOUNDATION_ONLY"
            });
        }
        const data = fs.readFileSync(modelPath, 'utf-8');
        const model = JSON.parse(data);
        return jsonResponse(model);
    } catch (error) {
        console.error("Error reading request storage status model:", error);
        return errorResponse('Failed to load storage status', 500);
    }
};