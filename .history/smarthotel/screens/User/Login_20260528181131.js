import React, { useState, useContext } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { Text, TextInput, Button } from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';
import API, { endpoints } from '../../configs/Apis';
import { MyDispatchContext } from '../../reducers/MyUserReducer';
import styles from '../../styles/Styles';

const Login = ({ navigation }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const dispatch = useContext(MyDispatchContext);

    const handleLogin = async () => {
        if (!username || !password) {
            Alert.alert("Lỗi", "Vui lòng nhập đầy đủ tài khoản và mật khẩu!");
            return;
        }

        setLoading(true);
        try {
            
            let res = await API.post(endpoints['login'], {
                'grant_type': 'password',
                'username': username,
                'password': password,
                // THAY BẰNG CLIENT_ID VÀ CLIENT_SECRET CỦA BẠN (Lấy từ Django Admin)
                'client_id': 'q0QxIoaHENINPcS4iPs7k4fts0c8v0vN0axY5Qmt',
                'client_secret': 'Tg4MXjuYDjBSiFFNnnGBK9fIhVehKGzIA4Dy6H7BLuppoPMtcJkAp2BS78PH0tFbLvdYiwZcI8ax9hd729lY86j40injERxi0b3j22rO3SglPzMEEbIpF44mlWSWJdVs'
            }, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });

            // 2. Lưu Token vào bộ nhớ điện thoại
            await AsyncStorage.setItem('access_token', res.data.access_token);

            // 3. (Tùy chọn) Gọi thêm API /api/users/current-user/ để lấy thông tin chi tiết của User (Tên, Avatar) bằng Token vừa nhận.
            // Tạm thời ở đây chúng ta giả lập lưu username vào state:
            dispatch({
                type: "login",
                payload: { username: username }
            });

            // 4. Chuyển hướng về Trang chủ
            navigation.reset({
                index: 0,
                routes: [{ name: 'Home' }],
            });

        } catch (error) {
            console.error(error);
            Alert.alert("Đăng nhập thất bại", "Tài khoản hoặc mật khẩu không chính xác!");
        } finally {
            setLoading(false);
        }
    };

    return (
        <View style={[styles.container, localStyles.container]}>
            <Text style={styles.headerTitle}>ĐĂNG NHẬP HỆ THỐNG</Text>

            <TextInput
                label="Tên đăng nhập"
                value={username}
                onChangeText={text => setUsername(text)}
                style={localStyles.input}
                mode="outlined"
                autoCapitalize="none"
                autoCorrect={false}
                spellCheck={false}
            />

            <TextInput
                label="Mật khẩu"
                value={password}
                onChangeText={text => setPassword(text)}
                secureTextEntry={true}
                style={localStyles.input}
                mode="outlined"
                autoCapitalize="none"
            />

            <Button
                mode="contained"
                onPress={handleLogin}
                loading={loading}
                disabled={loading}
                style={localStyles.button}
            >
                Đăng nhập
            </Button>
        </View>
    );
}

const localStyles = StyleSheet.create({
    container: {
        padding: 20,
        justifyContent: 'center'
    },
    input: {
        marginBottom: 15,
        backgroundColor: '#fff'
    },
    button: {
        marginTop: 10,
        paddingVertical: 5
    }
});

export default Login;