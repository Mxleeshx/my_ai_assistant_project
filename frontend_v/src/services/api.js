import axios from 'axios';

// Base URL points to the FastAPI backend
const API = axios.create({ baseURL: 'http://localhost:8000' });

export const sendMessage = async (message, sessionId = null, file = null) => {
    const formData = new FormData();
    formData.append('message', message);
    if (sessionId) {
        formData.append('session_id', sessionId);
    }
    if (file) {
        formData.append('file', file);
    }

    const response = await API.post('/api/chat', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
};

export const getSessions = async () => {
    const response = await API.get('/api/sessions');
    return response.data;
};

export const renameSession = async (sessionId, title) => {
    const response = await API.put(`/api/sessions/${sessionId}`, { title });
    return response.data;
};

export const getHistory = async (sessionId) => {
    const response = await API.get(`/api/history/${sessionId}`);
    return response.data;
};

export const deleteSession = async (sessionId) => {
    const response = await API.delete(`/api/sessions/${sessionId}`);
    return response.data;
};
