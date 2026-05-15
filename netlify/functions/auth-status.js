const { jsonResponse, errorResponse } = require('./_shared/response');
const fs = require('fs');
const path = require('path');

exports.handler = async (event, context) => {
    if (event.httpMethod !== 'GET') {
        return errorResponse('Method Not Allowed', 405);
    }

    try {
        const modelPath = path.resolve(__dirname, './_shared/models/status_model.json');
        const data = fs.readFileSync(modelPath, 'utf-8');
        const model = JSON.parse(data);
        return jsonResponse(model);
    } catch (error) {
        console.error("Error reading auth status model:", error);
        return errorResponse('Failed to load auth status', 500);
    }
};