const { jsonResponse, errorResponse } = require('./_shared/response');
const fs = require('fs');
const path = require('path');

exports.handler = async (event, context) => {
    if (event.httpMethod !== 'GET') {
        return errorResponse('Method Not Allowed', 405);
    }

    try {
        const modelPath = path.resolve(__dirname, './_shared/models/dry_run_status.json');
        if (!fs.existsSync(modelPath)) {
            return jsonResponse({
                "dry_run_foundation_status": "READY_FOR_FOUNDATION_REVIEW_ONLY",
                "dry_run_execution_enabled": false,
                "durable_dry_run_storage_configured": false,
                "command_execution_enabled": false,
                "external_api_simulation_enabled": false,
                "evidence_persistence_verified": false,
                "current_mode": "DRY_RUN_FOUNDATION_ONLY"
            });
        }
        const data = fs.readFileSync(modelPath, 'utf-8');
        const model = JSON.parse(data);
        return jsonResponse(model);
    } catch (error) {
        console.error("Error reading dry-run engine status model:", error);
        return errorResponse('Failed to load dry-run status', 500);
    }
};