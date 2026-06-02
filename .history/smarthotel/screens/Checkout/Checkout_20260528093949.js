import React, { useState } from 'react';
import { View, ScrollView, Alert, Modal, StyleSheet } from 'react-native';
import { Text, Card, Title, Button, RadioButton, List } from 'react-native-paper';
import { WebView } from 'react-native-webview';
import API from '../../configs/Apis'; // Đường dẫn cấu hình Axios của nhóm bạn

const Checkout = ({ route, navigation }) => {
    
    // const { roomTypeId, roomTypeName, roomPrice } = route.params || { 
    //     roomTypeId: 1, 
    //     roomTypeName: "Phòng Phổ Thông", 
    //     roomPrice: 5000000 
    // };

    
    // const mockOrderData = {
    //     roomTypeName: roomTypeName,
    //     totalPrice: Number(roomPrice) * 1, 
    //     check_in_date: "2026-05-27",       
    //     check_out_date: "2026-05-29",      
    //     special_requests: "Phòng hướng biển, sạch sẽ",
    //     details: [
    //         { room: 1 } 
    //     ]
    // };
    const { room, checkIn, checkOut } = route.params;

    const [paymentMethod, setPaymentMethod] = useState('vnpay');
    const [loading, setLoading] = useState(false);
    const [vnpayUrl, setVnpayUrl] = useState(null);
    const [showWebView, setShowWebView] = useState(false);

    // const [paymentMethod, setPaymentMethod] = useState('vnpay');
    // const [loading, setLoading] = useState(false);
    
    // // States quản lý WebView VNPAY
    // const [vnpayUrl, setVnpayUrl] = useState(null);
    // const [showWebView, setShowWebView] = useState(false);

    // // 🚀 LUỒNG XỬ LÝ THANH TOÁN CHÍNH
    // const handlePaymentProcess = async () => {
    //     setLoading(true);
    //     try {
    //         // BƯỚC 1: Gọi API tạo đơn đặt phòng (Yêu cầu bạn phải ĐĂNG NHẬP trên app trước)
    //         console.log("Đang gọi API tạo đơn đặt phòng...");
    //         const bookingResponse = await API.post('/bookings/', {
    //             check_in_date: mockOrderData.check_in_date,
    //             check_out_date: mockOrderData.check_out_date,
    //             special_requests: mockOrderData.special_requests,
    //             details: mockOrderData.details
    //         });

    //         const createdBookingId = bookingResponse.data.id;
    //         console.log("Tạo đơn hàng thành công, ID:", createdBookingId);

    //         // Nếu người dùng chọn thanh toán trực tiếp tại quầy (Tiền mặt)
    //         if (paymentMethod === 'cod') {
    //             Alert.alert("Thành công 🎉", `Đã ghi nhận đơn đặt phòng #${createdBookingId}. Vui lòng thanh toán tại quầy khi check-in.`);
    //             setLoading(false);
    //             return;
    //         }

    //         // BƯỚC 2: Gọi API sinh link thanh toán VNPAY từ booking_id vừa tạo
    //         console.log("Đang lấy link thanh toán từ cổng VNPAY...");
    //         const paymentResponse = await API.post('/payments/create-vnpay/', {
    //             booking_id: createdBookingId
    //         });

    //         const url = paymentResponse.data.payment_url;

    //         if (url) {
    //             setVnpayUrl(url);
    //             setShowWebView(true); // Mở Modal chứa WebView cổng thanh toán
    //         } else {
    //             Alert.alert("Lỗi", "Không phản hồi link thanh toán từ hệ thống.");
    //         }

    //     } catch (error) {
    //         console.error("Lỗi xử lý đặt phòng:", error.response?.data || error.message);
    //         const errorMsg = error.response?.data?.error || "Đặt phòng thất bại. Đảm bảo bạn đã đăng nhập và ID phòng tồn tại!";
    //         Alert.alert("Thông báo lỗi", errorMsg);
    //     } finally {
    //         setLoading(false);
    //     }
    // };

    // // 🔄 THEO DÕI SỰ KIỆN ĐIỀU HƯỚNG CỦA WEBVIEW VNPAY
    // const handleNavigationStateChange = async (navState) => {
    //     // Nhận diện khi URL chuyển hướng về endpoint callback của Backend
    //     if (navState.url.includes('/payments/vnpay-callback/')) {
    //         setShowWebView(false); // Tắt màn hình WebView
    //         setVnpayUrl(null);

    //         // Kiểm tra mã thành công phản hồi từ VNPAY (vnp_ResponseCode=00)
    //         if (navState.url.includes('vnp_ResponseCode=00')) {
    //             Alert.alert(
    //                 "Thành Công 🎉", 
    //                 "Thanh toán hóa đơn phòng qua VNPAY thành công! Kiểm tra email để nhận hóa đơn."
    //             );
    //             navigation.navigate('Home'); // Thanh toán xong chuyển về trang chủ
    //         } else {
    //             // Trích xuất mã lỗi phản hồi
    //             const urlParams = new URLSearchParams(navState.url.split('?')[1]);
    //             const errorCode = urlParams.get('vnp_ResponseCode') || 'Unknown';
    //             Alert.alert("Thất Bại ❌", `Giao dịch đã bị hủy hoặc lỗi xảy ra. (Mã lỗi VNPAY: ${errorCode})`);
    //         }
    //     }
    // };

    return (
        <View style={{ flex: 1, backgroundColor: '#f5f5f5' }}>
            <ScrollView style={{ padding: 16 }}>
                <Text style={styles.header}>THÔNG TIN HÓA ĐƠN</Text>

                {/* Card thông tin chi tiết phòng đặt */}
                <Card style={styles.card}>
                    <Card.Content>
                        <Title style={{ fontWeight: 'bold', color: '#005baa' }}>{mockOrderData.roomTypeName}</Title>
                        <View style={{ marginVertical: 8 }}>
                            <Text>📅 Nhận phòng: {mockOrderData.check_in_date}</Text>
                            <Text>📅 Trả phòng: {mockOrderData.check_out_date}</Text>
                            <Text>📝 Ghi chú: {mockOrderData.special_requests}</Text>
                        </View>
                        <View style={{ borderTopWidth: 0.5, borderColor: '#ccc', paddingTop: 8, marginTop: 8 }}>
                            <Text style={{ fontSize: 18, fontWeight: 'bold', color: 'red' }}>
                                Tổng tiền: {mockOrderData.totalPrice.toLocaleString('vi-VN')} VNĐ
                            </Text>
                        </View>
                    </Card.Content>
                </Card>

                {/* Chọn phương thức thanh toán */}
                <Card style={styles.card}>
                    <Card.Content>
                        <Title style={{ fontSize: 18, marginBottom: 8 }}>💳 Chọn phương thức thanh toán</Title>
                        <RadioButton.Group onValueChange={value => setPaymentMethod(value)} value={paymentMethod}>
                            
                            <List.Item
                                title="Cổng trực tuyến VNPAY"
                                left={props => <List.Icon {...props} icon="credit-card-outline" color="#005baa" />}
                                right={() => <RadioButton value="vnpay" />}
                                style={{ borderBottomWidth: 0.3, borderColor: '#eee' }}
                            />
                            
                            <List.Item
                                title="Thanh toán trực tiếp tại quầy"
                                left={props => <List.Icon {...props} icon="cash" color="#4caf50" />}
                                right={() => <RadioButton value="cod" />}
                            />

                        </RadioButton.Group>
                    </Card.Content>
                </Card>

                <Button 
                    mode="contained" 
                    buttonColor="#005baa" 
                    textColor="white"
                    loading={loading}
                    disabled={loading}
                    style={styles.btn}
                    onPress={handlePaymentProcess}
                >
                    {paymentMethod === 'vnpay' ? "THANH TOÁN QUA VNPAY" : "XÁC NHẬN ĐẶT PHÒNG"}
                </Button>
            </ScrollView>

            {/* Màn hình Modal chứa WebView VNPAY */}
            <Modal visible={showWebView} animationType="slide" onRequestClose={() => setShowWebView(false)}>
                <View style={{ flex: 1 }}>
                    <Button 
                        mode="contained-tonal" 
                        buttonColor="#ffcdd2"
                        textColor="#b71c1c"
                        onPress={() => setShowWebView(false)} 
                        style={{ marginTop: 50, marginHorizontal: 16, marginBottom: 10 }}
                    >
                        ❌ Hủy giao dịch / Quay lại App
                    </Button>
                    
                    {vnpayUrl && (
                        <WebView 
                            source={{ uri: vnpayUrl }}
                            onNavigationStateChange={handleNavigationStateChange}
                            javaScriptEnabled={true}
                            domStorageEnabled={true}
                            startInLoadingState={true}
                        />
                    )}
                </View>
            </Modal>
        </View>
    );
};

const styles = StyleSheet.create({
    header: { fontSize: 22, fontWeight: 'bold', textAlign: 'center', marginVertical: 24, color: '#333' },
    card: { marginBottom: 16, borderRadius: 12, backgroundColor: '#fff', elevation: 2 },
    btn: { paddingVertical: 8, borderRadius: 8, marginTop: 10, fontSize: 16 }
});

export default Checkout;