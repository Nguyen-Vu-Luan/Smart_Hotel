
import React, { useReducer } from "react";
import { SafeAreaView, StyleSheet } from "react-native";
import Styles from "./styles/Styles";
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { MyUserContext, MyDispatchContext, myUserReducer } from "./reducers/MyUserReducer";
import Header from "./components/Header";
import Home from "./screens/Home/Home";
import RoomDetail from "./screens/RoomDetail/RoomDetail";
import Login from "./screens/User/Login";
import Register from "./screens/User/Register";
import Booking from "./screens/Booking/Booking";
import { PaperProvider } from "react-native-paper";
import Checkout from "./screens/Checkout/Checkout";

const Stack = createNativeStackNavigator();

const App = () => {
    const [user, dispatch] = useReducer(myUserReducer, null);

    return (
        <PaperProvider>
            <MyUserContext.Provider value={user}>
                <MyDispatchContext.Provider value={dispatch}>
                    <NavigationContainer>
                        <Stack.Navigator initialRouteName="Home">
                            <Stack.Screen name="Home" component={Home} options={{ title: 'Trang chủ' }} />
                            <Stack.Screen name="RoomDetail" component={RoomDetail} options={{ title: 'Chi tiết phòng' }} />
                            <Stack.Screen name="Login" component={Login} options={{ title: 'Đăng nhập' }} />
                            <Stack.Screen name="Register" component={Register} options={{ title: 'Đăng ký' }} />
                            <Stack.Screen name="Booking" component={Booking} options={{ title: 'Đặt phòng' }} />
                            <Stack.Screen name="Checkout" component={Checkout} options={{ title: 'Thanh toán' }} />
                        </Stack.Navigator>
                    </NavigationContainer>
                </MyDispatchContext.Provider>
            </MyUserContext.Provider>
        </PaperProvider>

    );
}

export default App;