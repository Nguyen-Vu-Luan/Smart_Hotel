import axios from "axios";

export const endpoints = {
  roomtypes: "roomtypes/",
  rooms: "rooms/",
  login: "o/token/",
};

export default axios.create({
  baseURL: "http://192.168.10.108:8000/",
});


API.defaults.headers.common['Authorization'] = `Bearer CHUỖI_TOKEN_JWT_CỦA_BẠN_Ở_ĐÂY`;
