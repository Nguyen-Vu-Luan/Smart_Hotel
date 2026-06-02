import React, { useState } from 'react';
import { View, ScrollView, Alert, Modal, StyleSheet } from 'react-native';
import { Text, Card, Title, Button, RadioButton, List } from 'react-native-paper';
import { WebView } from 'react-native-webview';
import API from '../../configs/Apis';
import AsyncStorage from '@react-native-async-storage/async-storage';

const Checkout = ({ route, navigation }) => {
    const { bookingId, room, checkIn, checkOut, totalPrice, services } = route.params;
    const [paymentMethod, setPaymentMethod] = useState('vnpay');
    const [loading, setLoading] = useState(false);
    const [vnpayUrl, setVnpayUrl] = useState(null);
    const [showWebView, setShowWebView] = useState(false);

    

    const handlePaymentProcess = async () => {
        setLoading(true);
        try {
            if (paymentMethod === 'cod') { 
                navigation.replace('PaymentResult', { 
                    bookingId, 
                    totalPrice, 
                    status:  'XÁC NHẬN GIỮ CHỖ', 
                    roomName: room.name,
                    roomTypeName: room.typeName,
                    basePrice: room.price,
                    checkIn,
                    checkOut,
                    paymentMethod: 'cod', 
                    services: services || [],
                    
                });
                return;
            }

            const paymentResponse = await API.post('/payments/create-vnpay/', { 
                booking_id: bookingId 
            });

            setVnpayUrl(paymentResponse.data.payment_url);
            setShowWebView(true);

        } catch (error) {
            console.error("Lỗi thanh toán:", error.response?.data || error);
            Alert.alert("Lỗi", "Không thể khởi tạo thanh toán. Vui lòng thử lại!");
        } finally {
            setLoading(false);
        }
    };

    return (
        <View style={{ flex: 1, backgroundColor: '#f5f5f5' }}>
            <ScrollView style={{ padding: 16 }}>
                <Title style={styles.header}>XÁC NHẬN THANH TOÁN</Title>
                
                <Card style={styles.card}>
                    <Card.Content>
                        <Title>{room.name}</Title>
                        <Text>📅 Nhận phòng: {checkIn}</Text>
                        <Text>📅 Trả phòng: {checkOut}</Text>
                        <Text style={{ fontWeight: 'bold', fontSize: 18, marginTop: 10, color: 'red' }}>
                            Tổng tiền: {totalPrice.toLocaleString('vi-VN')} VNĐ
                        </Text>
                    </Card.Content>
                </Card>

                <Card style={styles.card}>
                    <Card.Content>
                        <Title style={{ fontSize: 16 }}>Phương thức thanh toán</Title>
                        <RadioButton.Group onValueChange={setPaymentMethod} value={paymentMethod}>
                            <List.Item title="VNPAY" right={() => <RadioButton value="vnpay" />} />
                            <List.Item title="Tiền mặt tại quầy" right={() => <RadioButton value="cod" />} />
                        </RadioButton.Group>
                    </Card.Content>
                </Card>

                <Button mode="contained" loading={loading} onPress={handlePaymentProcess} style={styles.btn}>
                    {paymentMethod === 'vnpay' ? "THANH TOÁN QUA VNPAY" : "XÁC NHẬN ĐẶT PHÒNG"}
                </Button>
            </ScrollView>

            <Modal visible={showWebView} animationType="slide">
                <View style={{ flex: 1, marginTop: 50 }}>
                    <Button onPress={() => setShowWebView(false)}>Đóng</Button>
                    {vnpayUrl && (
                        <WebView 
                            source={{ uri: vnpayUrl }}
                            onNavigationStateChange={(navState) => {
                                // if (navState.url.includes('vnpay-callback')) {
                                //     setShowWebView(false);
                                //     navigation.replace('PaymentResult', {
                                //         bookingId: bookingId,
                                //         totalPrice: totalPrice,
                                //         status: 'Đã xác nhận',
                                //         roomName: room.name,      
                                //         checkIn: checkIn,         
                                //         checkOut: checkOut,
                                //         services: services      
                                //     });
                                // }
                                // Kiểm tra URL callback
                            if (navState.url.includes('vnpay-callback')) {
                                setShowWebView(false); // Đóng modal trước

                                // KIỂM TRA MÃ TRẠNG THÁI GIAO DỊCH
                                // VNPAY thường trả về vnpay_ResponseCode=00 khi thành công
                                if (navState.url.includes('vnpay_ResponseCode=00')) {
                                    navigation.replace('PaymentResult', {
                                        bookingId: bookingId,
                                        totalPrice: totalPrice,
                                        status: 'Thanh toán thành công',
                                        roomName: room.name,
                                        roomTypeName: room.typeName,
                                        basePrice: room.price,
                                        checkIn: checkIn,
                                        checkOut: checkOut,
                                        paymentMethod: 'vnpay',
                                        services: services
                                    });
                                } else {
                                    // Xử lý khi hủy hoặc thất bại
                                    Alert.alert(
                                        "Thông báo", 
                                        "Giao dịch đã bị hủy hoặc không thành công.",
                                        [{ text: "OK", onPress: () => navigation.goBack() }] // Quay lại trang trước
                                    );
                                }
                            }
                            }}
                        />
                    )}
                </View>
            </Modal>
        </View>
    );
};

const styles = StyleSheet.create({
    header: { textAlign: 'center', marginVertical: 20 },
    card: { marginBottom: 16, borderRadius: 12 },
    btn: { paddingVertical: 6 }
});

export default Checkout;