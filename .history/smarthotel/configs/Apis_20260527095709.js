import axios from "axios";

export const endpoints = {
  roomtypes: "roomtypes/",
  rooms: "rooms/",
  login: "o/token/",
};

export default axios.create({
  baseURL: "http://127:8000/",
});
