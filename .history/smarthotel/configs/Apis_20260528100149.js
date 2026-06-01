import axios from "axios";

API.interceptors.request.use(async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const endpoints = {
    'roomtypes': '/roomtypes/', 
    'rooms': '/rooms/',
    'login': '/o/token/',
    'users': '/users/',
    'bookings': '/bookings/',
    'services': '/services/',
    'revenue-report': '/reports/revenue/',
    'occupancy-report': '/reports/occupancy-rate/',
    'feedback-report': '/reports/customer-feedback/',
}


export default axios.create({
  baseURL: "http://192.168.120.239:8000/",
});

