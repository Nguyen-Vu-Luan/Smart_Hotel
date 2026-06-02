import { SafeAreaView, StyleSheet } from "react-native";
import Header from "./components/Header";
import Home from "./screens/Home/Home";
import Checkout from './screens/Checkout/Checkout';
import Styles from "./styles/Styles";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from '@react-navigation/stack';

const Stack = createStackNavigator();

const App = () => {
    return (
        <SafeAreaView style={Styles.container}>
            <Header />
            {/* <Home /> */}

     
            <NavigationContainer>
                <Stack.Navigator 
                    initialRouteName="Home"
                    screenOptions={{
                        headerShown: false 
                    }}
                >
                    {/* Đăng ký màn hình Trang chủ */}
                    <Stack.Screen name="Home" component={Home} />
                    
                    {/* Đăng ký màn hình Thanh toán */}
                    <Stack.Screen name="Checkout" component={Checkout} />
                </Stack.Navigator>
            </NavigationContainer>
        </SafeAreaView>
    );
}

export default App;