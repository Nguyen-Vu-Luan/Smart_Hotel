import axios from "axios";



export default axios.create({
  baseURL: "http://192.168.10.108:8000/",
});


// API.defaults.headers.common['Authorization'] = `Bearer 19H3zK7Rkm0ILKdxRFeydnPtrnRaw7`;


export const endpoints = {
  roomtypes: "roomtypes/",
  rooms: "rooms/",
  login: "o/token/",
  revenue-report: '/reports/revenue/',
  'occupancy-report: '/reports/occupancy-rate/',
  'feedback-report: '/reports/customer-feedback/',
};