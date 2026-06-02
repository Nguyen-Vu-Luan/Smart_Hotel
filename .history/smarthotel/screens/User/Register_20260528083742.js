import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Image, Alert } from 'react-native';
import { Text, TextInput, Button, Avatar } from 'react-native-paper';
import * as ImagePicker from 'expo-image-picker'; // Thư viện chọn ảnh
import API, { endpoints } from '../../configs/Apis';
import styles from '../../styles/Styles';
import Footer from '../../components/Footer';

const Register = ({ navigation }) => {
    const [user, setUser] = useState({
        username: "",
        password: "",
        email: "",
        first_name: "",
        last_name: ""
    });

    // State lưu trữ ảnh avatar được chọn
    const [avatar, setAvatar] = useState(null);
    const [loading, setLoading] = useState(false);

    const updateState = (field, value) => {
        setUser(current => ({ ...current, [field]: value }));
    }

    // Hàm mở thư viện ảnh trên điện thoại
    const pickImage = async () => {
        let result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ['images'],
            allowsEditing: true,
            aspect: [1, 1], // Cắt ảnh hình vuông
            quality: 1,
        });

        if (!result.canceled) {
            setAvatar(result.assets[0]);
        }
    };

    // Hàm gọi API Đăng ký
    const handleRegister = async () => {
        // Kiểm tra dữ liệu cơ bản
        if (!user.username || !user.password) {
            Alert.alert("Lỗi", "Vui lòng nhập tên đăng nhập và mật khẩu!");
            return;
        }

        setLoading(true);
        try {
            const form = new FormData();

            for (let key in user) {
                form.append(key, user[key]);
            }

            if (avatar) {
                let localUri = avatar.uri;
                let filename = localUri.split('/').pop();
                let match = /\.(\w+)$/.exec(filename);
                let type = match ? `image/${match[1]}` : `image`;

                form.append('avatar', {
                    uri: localUri,
                    name: filename,
                    type: type
                });
            }

            // Gọi API tạo tài khoản
            let res = await API.post(endpoints['users'], form, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            // THÊM DÒNG NÀY: Chuyển hướng ngay lập tức sang trang Login
            Alert.alert("Thành công", "Đăng ký tài khoản thành công!", [
                {
                    text: "Đăng nhập ngay",
                    // THAY TỪ navigate THÀNH replace Ở ĐÂY:
                    onPress: () => navigation.replace("Login")
                }
            ]);

        } catch (error) {
            console.error(error.response?.data || error);
            Alert.alert("Lỗi", "Đăng ký thất bại. Vui lòng kiểm tra lại thông tin!");
        } finally {
            setLoading(false);
        }
    }

    return (
        <View style={{ flex: 1, backgroundColor: '#f5f5f5' }}>
            <ScrollView contentContainerStyle={localStyles.container}>
                <Text style={styles.headerTitle}>ĐĂNG KÝ TÀI KHOẢN</Text>

                {/* KHU VỰC CHỌN AVATAR */}
                <View style={localStyles.avatarContainer}>
                    {avatar ? (
                        <Avatar.Image size={100} source={{ uri: avatar.uri }} />
                    ) : (
                        <Avatar.Icon size={100} icon="account" />
                    )}
                    <Button mode="text" onPress={pickImage}>
                        Chọn ảnh đại diện
                    </Button>
                </View>

                {/* KHU VỰC NHẬP LIỆU */}
                <TextInput value={user.first_name} onChangeText={t => updateState('first_name', t)} label="Họ" style={localStyles.input} mode="outlined" />
                <TextInput value={user.last_name} onChangeText={t => updateState('last_name', t)} label="Tên" style={localStyles.input} mode="outlined" />
                <TextInput value={user.email} onChangeText={t => updateState('email', t)} label="Email" style={localStyles.input} mode="outlined" autoCapitalize="none" autoCorrect={false} spellCheck={false}/>
                <TextInput value={user.username} onChangeText={t => updateState('username', t)} label="Tên đăng nhập" style={localStyles.input} mode="outlined" />
                <TextInput value={user.password} onChangeText={t => updateState('password', t)} label="Mật khẩu" secureTextEntry style={localStyles.input} mode="outlined" />

                <Button mode="contained" onPress={handleRegister} loading={loading} disabled={loading} style={localStyles.button}>
                    Tạo tài khoản
                </Button>
            </ScrollView>

            <Footer />
        </View>
    );
}

const localStyles = StyleSheet.create({
    container: { padding: 20, justifyContent: 'center' },
    avatarContainer: { alignItems: 'center', marginBottom: 15 },
    input: { marginBottom: 10, backgroundColor: '#fff' },
    button: { marginTop: 15, paddingVertical: 5 }
});

export default Register;