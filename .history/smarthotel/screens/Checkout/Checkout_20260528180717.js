
import React, { useState } from 'react';
import { View, ScrollView, Alert, Modal, StyleSheet } from 'react-native';
import { Text, Card, Title, Button, RadioButton, List } from 'react-native-paper';
import { WebView } from 'react-native-webview';
import API from '../../configs/Apis';
import AsyncStorage from '@react-native-async-storage/async-storage';

const Checkout = ({ route, navigation }) => {
    // const [bookingId, setBookingId] = useState(null);
    const { bookingId, room, checkIn, checkOut, totalPrice, services } = route.params;

    const [paymentMethod, setPaymentMethod] = useState('vnpay');
    const [loading, setLoading] = useState(false);
    const [vnpayUrl, setVnpayUrl] = useState(null);
    const [showWebView, setShowWebView] = useState(false);

    // const handlePaymentProcess = async () => {
    //     setLoading(true);
    //     try {
    //         // 1. Kiểm tra Token từ AsyncStorage (Nguồn tin cậy nhất)
    //         const token = await AsyncStorage.getItem('access_token');
    //         if (!token) {
    //             Alert.alert("Thông báo", "Phiên đăng nhập hết hạn hoặc chưa đăng nhập. Vui lòng đăng nhập lại!");
    //             navigation.navigate("Login");
    //             return;
    //         }

    //         // 2. Gọi API tạo đơn đặt phòng
    //         // Lưu ý: Nhờ có Interceptor ở file Apis.js, token đã tự động được đính kèm
    //         const bookingResponse = await API.post('/bookings/', {
    //             check_in_date: checkIn,
    //             check_out_date: checkOut,
    //             total_price: totalPrice,
    //             details: [{ room: room.id }],
    //             services: services
    //         });

    //         const createdBookingId = bookingResponse.data.id;

    //         // 2. LƯU VÀO STATE ĐỂ DÙNG SAU NÀY
    //         setBookingId(createdBookingId);

    //         // 3. Xử lý phương thức thanh toán
    //         if (paymentMethod === 'cod') {
    //             Alert.alert("Thành công 🎉", "Đặt phòng thành công. Vui lòng thanh toán tại quầy.");
    //             navigation.navigate('Home');
    //             return;
    //         }

    //         // 4. Gọi API tạo link VNPAY
    //         const paymentResponse = await API.post('/payments/create-vnpay/', { 
    //             booking_id: createdBookingId 
    //         });

    //         setVnpayUrl(paymentResponse.data.payment_url);
    //         setShowWebView(true);

    //     } catch (error) {
    //         // Nếu server trả về 401 Unauthorized -> Token hết hạn
    //         if (error.response?.status === 401) {
    //             Alert.alert("Lỗi", "Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại!");
    //             navigation.navigate("Login");
    //         } else {
    //             console.log("Lỗi chi tiết:", error.response?.data);
    //             Alert.alert("Lỗi", "Không thể đặt phòng. Vui lòng thử lại!");
    //         }
    //     } finally {
    //         setLoading(false);
    //     }
    // };

    const handlePaymentProcess = async () => {
        setLoading(true);
        try {
            // 1. Nếu chọn thanh toán tại quầy (COD)
            // if (paymentMethod === 'cod') {
            //     Alert.alert("Thành công 🎉", "Đặt phòng thành công. Vui lòng thanh toán tại quầy.");
            //     navigation.replace('PaymentResult', { 
            //         bookingId, 
            //         totalPrice, 
            //         status: 'Thành công (COD)',
            //         roomName: room.name,
            //         checkIn,
            //         checkOut
            //     });
            //     return;
            // }
            // 1. Nếu chọn thanh toán tại quầy (COD)
            if (paymentMethod === 'cod') {
                // Sếp gọi API xác nhận đặt phòng ở đây (nếu có API confirm)
                // await API.post(`/bookings/${bookingId}/confirm-cod/`); 
                
                navigation.replace('PaymentResult', { 
                    bookingId, 
                    totalPrice, 
                    status: 'XÁC NHẬN GIỮ CHỖ', // Thay đổi status ở đây
                    roomName: room.name,
                    checkIn,
                    checkOut,
                    paymentMethod: 'cod', 
                    services: services || []
                });
                return;
            }

            // 2. Nếu chọn thanh toán qua VNPay
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

            {/* <Modal visible={showWebView} animationType="slide">
                <View style={{ flex: 1, marginTop: 50 }}>
                    <Button onPress={() => setShowWebView(false)}>Đóng WebView</Button>
                    {vnpayUrl && <WebView source={{ uri: vnpayUrl }} />}
                </View>
            </Modal> */}

            <Modal visible={showWebView} animationType="slide">
                <View style={{ flex: 1, marginTop: 50 }}>
                    <Button onPress={() => setShowWebView(false)}>Đóng</Button>
                    {vnpayUrl && (
                        <WebView 
                            source={{ uri: vnpayUrl }}
                            onNavigationStateChange={(navState) => {
                                // Thay 'vnpay-callback' bằng đường dẫn thực tế server của bạn trả về sau khi thanh toán
                                if (navState.url.includes('vnpay-callback')) {
                                    setShowWebView(false);
                                    navigation.replace('PaymentResult', {
                                        bookingId: bookingId,
                                        totalPrice: totalPrice,
                                        status: 'Đã xác nhận',
                                        roomName: room.name,      // Mới thêm
                                        checkIn: checkIn,         // Mới thêm
                                        checkOut: checkOut,
                                        services: services      // Mới thêm
                                    });
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