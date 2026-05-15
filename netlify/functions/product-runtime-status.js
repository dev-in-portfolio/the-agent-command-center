const { jsonResponse, errorResponse } = require('./_shared/response');
const fs = require('fs');
const path = require('path');

exports.handler = async (event, context) => {
    if (event.httpMethod !== 'GET') {
        return errorResponse('Method Not Allowed', 405);
    }

    try {
        const modelPath = path.resolve(__dirname, './_shared/models/product_runtime_status.json');
        if (!fs.existsSync(modelPath)) {
            return jsonResponse({
                "product_track_active": true,
                "runtime_scaffold_ready": true,
                "real_auth_configured": false,
                "durable_persistence_configured": false,
                "dry_run_execution_enabled": false,
                "external_mutation_enabled": false,
                "real_automation_enabled": false,
                "current_status": "MVP_RUNTIME_SCAFFOLD_READY"
            });
        }
        const data = fs.readFileSync(modelPath, 'utf-8');
        const model = JSON.parse(data);
        return jsonResponse(model);
    } catch (error) {
        console.error("Error reading product runtime status model:", error);
        return errorResponse('Failed to load product runtime status', 500);
    }
};
