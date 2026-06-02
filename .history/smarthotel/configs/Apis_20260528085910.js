import axios from "axios";


export const endpoints = {
    'roomtypes': '/roomtypes/', 
    'rooms': '/rooms/',
    'login': '/o/token/',
    'users': '/users/',
    'bookings': '/bookings/',
    'services': '/services/'
}


export default axios.create({
  baseURL: "http://192.168.10.108:8000/",
});



export const endpoints = {
  roomtypes: "roomtypes/",
  rooms: "rooms/",
  login: "o/token/",
  "revenue-report": "/reports/revenue/",
  "occupancy-report": "/reports/occupancy-rate/",
  "feedback-report": "/reports/customer-feedback/",
};