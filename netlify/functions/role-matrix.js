const { respondJson, respondError } = require('./_shared/response');
const fs = require('fs');
const path = require('path');

exports.handler = async (event, context) => {
    if (event.httpMethod !== 'GET') {
        return respondError(405, 'Method Not Allowed');
    }

    try {
        const modelPath = path.resolve(__dirname, '../../14_backend/auth/role_matrix.json');
        const data = fs.readFileSync(modelPath, 'utf-8');
        const model = JSON.parse(data);
        return respondJson(model);
    } catch (error) {
        console.error("Error reading role matrix model:", error);
        return respondError(500, 'Failed to load role matrix');
    }
};