import { SafeAreaView, StyleSheet } from "react-native";
import Header from "./components/Header";
import Home from "./screens/Home/Home";
import Checkout from './screens/Checkout/Checkout';
import Styles from "./styles/Styles";

const App = () => {
    return (
        <SafeAreaView style={Styles.container}>
            <Header />
            <Home />
        </SafeAreaView>
    );
}

export default App;