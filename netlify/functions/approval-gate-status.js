const { jsonResponse, errorResponse } = require('./_shared/response');
const fs = require('fs');
const path = require('path');

exports.handler = async (event, context) => {
    if (event.httpMethod !== 'GET') {
        return errorResponse('Method Not Allowed', 405);
    }

    try {
        const modelPath = path.resolve(__dirname, './_shared/models/approval_gate_status.json');
        if (!fs.existsSync(modelPath)) {
            return jsonResponse({
                "approval_foundation_status": "READY_FOR_FOUNDATION_REVIEW_ONLY",
                "durable_approval_storage_configured": false,
                "approval_write_endpoint_enabled": false,
                "approval_record_persistence_verified": false,
                "approval_identity_binding_ready": false,
                "audit_dependency_ready": true,
                "request_storage_dependency_ready": true,
                "current_mode": "APPROVAL_FOUNDATION_ONLY"
            });
        }
        const data = fs.readFileSync(modelPath, 'utf-8');
        const model = JSON.parse(data);
        return jsonResponse(model);
    } catch (error) {
        console.error("Error reading approval gate status model:", error);
        return errorResponse('Failed to load approval status', 500);
    }
};