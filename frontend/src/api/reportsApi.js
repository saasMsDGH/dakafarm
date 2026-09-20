import { api } from "./axios";

// Helper to remove empty parameters
const buildQuery = (params) => {
    if (!params) return '';
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
            query.append(key, value);
        }
    });
    const str = query.toString();
    return str ? '?' + str : '';
};

export const reportsApi = {
    getMasterSummary: (params) => api.get(`/api/v1/reports/operations/master-summary${buildQuery(params)}`),
};
