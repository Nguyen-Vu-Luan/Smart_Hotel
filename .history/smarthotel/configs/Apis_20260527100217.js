import axios from "axios";

export const endpoints = {
  roomtypes: "roomtypes/",
  rooms: "rooms/",
  login: "o/token/",
};

export default axios.create({
  baseURL: "http://192.168.10.108:8000/",
});
