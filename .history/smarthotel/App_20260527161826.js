// import { SafeAreaView, StyleSheet } from "react-native";
// import Header from "./components/Header";
// import Home from "./screens/Home/Home";
// import Checkout from './screens/Checkout/Checkout';
// import Styles from "./styles/Styles";
// import { NavigationContainer } from "@react-navigation/native";
// import { createStackNavigator } from '@react-navigation/stack';

// const Stack = createStackNavigator();

// const App = () => {
//     return (
//         <SafeAreaView style={Styles.container}>
//             <Header />
//             {/* <Home /> */}

     
//             <NavigationContainer>
//                 <Stack.Navigator 
//                     initialRouteName="Home"
//                     screenOptions={{
//                         headerShown: false 
//                     }}
//                 >
//                     {/* Đăng ký màn hình Trang chủ */}
//                     <Stack.Screen name="Home" component={Home} />
                    
//                     {/* Đăng ký màn hình Thanh toán */}
//                     <Stack.Screen name="Checkout" component={Checkout} />
//                 </Stack.Navigator>
//             </NavigationContainer>
//         </SafeAreaView>
//     );
// }

// export default App;




import React, { createContext, useReducer } from 'react'; 
import { SafeAreaView } from "react-native";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from '@react-navigation/stack';

import Header from "./components/Header";
import Home from "./screens/Home/Home";
import Checkout from './screens/Checkout/Checkout';
import AdminDashboard from './screens/Admin/AdminDashboard'; 
import Styles from "./styles/Styles";
import MyUserReducer from './reducers/MyUserReducer'; 


export const MyUserContext = createContext();

const Stack = createStackNavigator();

const App = () => {
    // 5. Khởi tạo State user
    // const [user, dispatch] = useReducer(MyUserReducer, null);

    return (
        <MyUserContext.Provider value={[user, dispatch]}>
            <SafeAreaView style={Styles.container}>
                <Header />
                <NavigationContainer>
                    <Stack.Navigator 
                        initialRouteName="Home"
                        screenOptions={{ headerShown: false }}
                    >
                        {/* <Stack.Screen name="Home" component={Home} />
                        <Stack.Screen name="Checkout" component={Checkout} /> */}
                        {/* 6. Đăng ký thêm màn hình Admin ở đây */}
                        <Stack.Screen name="AdminDashboard" component={AdminDashboard} />
                    </Stack.Navigator>
                </NavigationContainer>
            </SafeAreaView>
        </MyUserContext.Provider>
    );
}

export default App;