import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Button, Card, Title } from 'react-native-paper';

const PaymentResult = ({ route, navigation }) => {
    // Nhận thông tin từ trang Checkout truyền sang
    const { bookingId, totalPrice, status } = route.params;

    return (
        <View style={styles.container}>
            <Card style={styles.card}>
                <Card.Content style={{ alignItems: 'center' }}>
                    <Title style={{ color: 'green', marginBottom: 20 }}>THANH TOÁN THÀNH CÔNG 🎉</Title>
                    <Text style={styles.text}>Mã đơn hàng: {bookingId}</Text>
                    <Text style={styles.text}>Số tiền: {totalPrice.toLocaleString('vi-VN')} VNĐ</Text>
                    <Text style={styles.text}>Trạng thái: {status}</Text>
                </Card.Content>
            </Card>

            <Button mode="contained" onPress={() => navigation.navigate('Home')} style={styles.button}>
                Về trang chủ
            </Button>
            <Button mode="outlined" onPress={() => navigation.navigate('Home')} style={styles.button}>
                Xem chi tiết đơn hàng
            </Button>
        </View>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, justifyContent: 'center', padding: 20, backgroundColor: '#f5f5f5' },
    card: { padding: 20, marginBottom: 20 },
    text: { fontSize: 16, marginBottom: 10 },
    button: { marginTop: 10 }
});

export default PaymentResult;