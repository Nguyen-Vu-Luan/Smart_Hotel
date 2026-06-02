import { createContext } from "react";

// 1. Tạo Context để lưu thông tin User và hàm Dispatch (để cập nhật User)
export const MyUserContext = createContext();
export const MyDispatchContext = createContext();

// 2. Tạo Reducer xử lý các hành động (Đăng nhập / Đăng xuất)
export const myUserReducer = (currentState, action) => {
    switch (action.type) {
        case "login":
            return action.payload; 
        case "logout":
            return null; 
        default:
            return currentState;
    }
}