import AsyncStorage from "@react-native-async-storage/async-storage";
import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000/",
});

API.interceptors.request.use(async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    } else {
        console.warn("CẢNH BÁO: Không tìm thấy Token trong AsyncStorage!");
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
}


export default API;

