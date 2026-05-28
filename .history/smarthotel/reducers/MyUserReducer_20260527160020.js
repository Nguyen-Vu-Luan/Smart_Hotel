const MyUserReducer = (currentState, action) => {
    switch (action.type) {
        case "login":
            return action.payload; // payload này là thông tin user (có chứa role)
        case "logout":
            return null;
    }
    return currentState;
};

export default MyUserReducer;