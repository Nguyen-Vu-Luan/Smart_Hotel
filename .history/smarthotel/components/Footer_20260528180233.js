import React, { useContext } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { Button } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';


import { MyUserContext, MyDispatchContext } from '../reducers/MyUserReducer';

const Footer = () => {
    const navigation = useNavigation();
    
  
    const user = useContext(MyUserContext);
    const dispatch = useContext(MyDispatchContext);

   
    const handleLogout = () => {
        Alert.alert("Xác nhận", "Bạn có chắc chắn muốn đăng xuất?", [
            {
                text: "Hủy",
                style: "cancel"
            },
            {
                text: "Đăng xuất",
                onPress: async () => {
                  
                    await AsyncStorage.removeItem('access_token');
                    
                    // Báo cho toàn bộ App biết là user đã logout (trở về null)
                    dispatch({ type: "logout" });
                    
                    // Tự động đẩy người dùng về Trang chủ
                    navigation.navigate('Home');
                }
            }
        ]);
    };

    return (
        <View style={styles.footerContainer}>
            
            {/* 4. Logic ẩn hiện thông minh */}
            {user === null ? (
                <>
                    <Button 
                        icon="login" 
                        mode="text" 
                        onPress={() => navigation.navigate('Login')}
                    >
                        Đăng nhập
                    </Button>

                    <Button 
                        icon="account-plus" 
                        mode="text" 
                        onPress={() => navigation.navigate('Register')}
                    >
                        Đăng ký
                    </Button>
                </>
            ) : (
                <Button 
                    icon="logout" 
                    mode="text" 
                    textColor="#e53935" // Nút Đăng xuất màu đỏ cho nổi bật
                    onPress={handleLogout}
                >
                    Đăng xuất
                </Button>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    footerContainer: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        alignItems: 'center',
        paddingVertical: 10,
        backgroundColor: '#fff',
        borderTopWidth: 1,
        borderTopColor: '#e0e0e0',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: -2 },
        shadowOpacity: 0.1,
        shadowRadius: 3,
        elevation: 10,
    }
});

export default Footer;