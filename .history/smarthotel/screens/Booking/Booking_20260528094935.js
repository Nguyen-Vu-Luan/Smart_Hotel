import React, { useState, useEffect, useContext } from 'react';
import { View, ScrollView, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import { Text, Button, Card, Divider, Checkbox } from 'react-native-paper';
import DateTimePicker from '@react-native-community/datetimepicker';
import { MyUserContext } from '../../reducers/MyUserReducer';
import API, { endpoints } from '../../configs/Apis';
import styles from '../../styles/Styles';
import ScreenWrapper from '../../components/ScreenWrapper';

const Booking = ({ route, navigation }) => {
    // Nhận dữ liệu phòng từ trang trước
    const { roomId, roomNumber, basePrice } = route.params;
    const user = useContext(MyUserContext);

    // --- STATES ---
    const [services, setServices] = useState([]);
    const [selectedServices, setSelectedServices] = useState([]); // Chứa ID các dịch vụ được chọn
    const [loading, setLoading] = useState(true);
    const [bookingLoading, setBookingLoading] = useState(false);

    // State cho Date Picker
    const [checkIn, setCheckIn] = useState(new Date());
    const [checkOut, setCheckOut] = useState(new Date(new Date().getTime() + 24 * 60 * 60 * 1000)); // Mặc định ngày mai
    const [showCheckInPicker, setShowCheckInPicker] = useState(false);
    const [showCheckOutPicker, setShowCheckOutPicker] = useState(false);

    // Lấy danh sách dịch vụ từ API khi mở trang
    useEffect(() => {
        const loadServices = async () => {
            try {
                // Nhớ khai báo endpoints['services'] trong file Apis.js nhé
                let res = await API.get(endpoints['services']);
                setServices(res.data.results || res.data);
            } catch (error) {
                console.error("Lỗi tải dịch vụ:", error);
            } finally {
                setLoading(false);
            }
        };
        loadServices();
    }, []);

    // --- TÍNH TOÁN TIỀN ---
    // Tính số đêm (Chênh lệch giữa 2 ngày)
    const getNightCount = () => {
        const diffTime = Math.abs(checkOut - checkIn);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays > 0 ? diffDays : 1; // Ít nhất là 1 đêm
    };

    // Tính tổng tiền = (Giá phòng * số đêm) + Tổng tiền dịch vụ
    const getTotalPrice = () => {
        const roomTotal = basePrice * getNightCount();

        // Tính tổng tiền các dịch vụ đã tick chọn
        const servicesTotal = services
            .filter(s => selectedServices.includes(s.id))
            .reduce((sum, service) => sum + Number(service.price), 0);

        return roomTotal + servicesTotal;
    };

    // --- XỬ LÝ CHỌN DỊCH VỤ ---
    const toggleService = (serviceId) => {
        if (selectedServices.includes(serviceId)) {
            setSelectedServices(selectedServices.filter(id => id !== serviceId)); // Bỏ chọn
        } else {
            setSelectedServices([...selectedServices, serviceId]); // Chọn
        }
    };

    // --- XỬ LÝ ĐẶT PHÒNG ---
    // const handleConfirmBooking = async () => {
    //     if (checkOut <= checkIn) {
    //         Alert.alert("Lỗi", "Ngày trả phòng phải sau ngày nhận phòng!");
    //         return;
    //     }

    //     setBookingLoading(true);
    //     try {
    //         // Chuẩn bị dữ liệu gửi lên Backend
    //         const bookingData = {
    //             room: roomId,
    //             check_in_date: checkIn.toISOString().split('T')[0], // Format: YYYY-MM-DD
    //             check_out_date: checkOut.toISOString().split('T')[0],
    //             services: selectedServices, // Gửi mảng ID dịch vụ
    //             total_price: getTotalPrice()
    //         };

    //         // Gọi API tạo Booking (Lưu ý: Phải có Token xác thực)
    //         let res = await API.post(endpoints['bookings'], bookingData, {
    //             headers: {
    //                 'Authorization': `Bearer ${user.token}` // Tuỳ cách bạn lưu token, hoặc Axios tự gán
    //             }
    //         });

    //         Alert.alert("Thành công", "Chốt đơn đặt phòng thành công!", [
    //             { text: "Về Trang Chủ", onPress: () => navigation.navigate("Home") }
    //         ]);
    //     } catch (error) {
    //         console.error(error.response?.data || error);
    //         Alert.alert("Thất bại", "Có lỗi xảy ra khi đặt phòng.");
    //     } finally {
    //         setBookingLoading(false);
    //     }
    // };

    // TRONG Booking.js
    const handleConfirmBooking = async () => {
    if (checkOut <= checkIn) {
        Alert.alert("Lỗi", "Ngày trả phòng phải sau ngày nhận phòng!");
        return;
    }

    // Thay vì gọi API ở đây, sếp hãy đẩy dữ liệu sang trang Checkout
    navigation.navigate('Checkout', {
        room: { id: roomId, name: `Phòng ${roomNumber}`, price: basePrice },
        checkIn: checkIn.toISOString().split('T')[0],
        checkOut: checkOut.toISOString().split('T')[0],
        totalPrice: getTotalPrice(),
        services: selectedServices
    });
};

    if (loading) return <ActivityIndicator size="large" color="#1e88e5" style={styles.loader} />;

    return (
        <ScreenWrapper isLoading={loading && page === 1}>
            <View style={{ flex: 1, backgroundColor: '#f5f5f5' }}>
                <ScrollView contentContainerStyle={localStyles.container}>
                    <Text style={styles.headerTitle}>XÁC NHẬN ĐẶT PHÒNG</Text>

                    <Card style={styles.card}>
                        <Card.Content>
                            <Text style={localStyles.label}>Phòng: <Text style={localStyles.value}>{roomNumber}</Text></Text>
                            <Text style={localStyles.label}>Giá cơ bản: <Text style={localStyles.value}>{Number(basePrice).toLocaleString('vi-VN')} đ/đêm</Text></Text>
                        </Card.Content>
                    </Card>

                    {/* --- CHỌN NGÀY --- */}
                    <Card style={styles.card}>
                        <Card.Title title="Thời gian lưu trú" />
                        <Card.Content style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                            <View>
                                <Text>Nhận phòng:</Text>
                                <Button mode="text" onPress={() => setShowCheckInPicker(true)}>
                                    {checkIn.toLocaleDateString('vi-VN')}
                                </Button>
                            </View>
                            <View>
                                <Text>Trả phòng:</Text>
                                <Button mode="text" onPress={() => setShowCheckOutPicker(true)}>
                                    {checkOut.toLocaleDateString('vi-VN')}
                                </Button>
                            </View>
                        </Card.Content>
                    </Card>

                    {/* Các DatePicker ẩn, chỉ hiện lên khi bấm nút */}
                    {showCheckInPicker && (
                        <DateTimePicker
                            value={checkIn}
                            mode="date"
                            minimumDate={new Date()} // Không cho chọn ngày trong quá khứ
                            onChange={(event, date) => {
                                setShowCheckInPicker(false);
                                if (date) setCheckIn(date);
                            }}
                        />
                    )}
                    {showCheckOutPicker && (
                        <DateTimePicker
                            value={checkOut}
                            mode="date"
                            minimumDate={checkIn} // Ngày trả phải sau ngày nhận
                            onChange={(event, date) => {
                                setShowCheckOutPicker(false);
                                if (date) setCheckOut(date);
                            }}
                        />
                    )}

                    {/* --- DỊCH VỤ ĐI KÈM --- */}
                    <Card style={styles.card}>
                        <Card.Title title="Dịch vụ đi kèm" />
                        <Card.Content>
                            {services.length === 0 ? (
                                <Text style={{ fontStyle: 'italic', color: 'gray' }}>Không có dịch vụ nào.</Text>
                            ) : (
                                services.map(s => (
                                    <Checkbox.Item
                                        key={s.id}
                                        label={`${s.name} (+${Number(s.price).toLocaleString('vi-VN')} đ)`}
                                        status={selectedServices.includes(s.id) ? 'checked' : 'unchecked'}
                                        onPress={() => toggleService(s.id)}
                                        color="#1e88e5"
                                    />
                                ))
                            )}
                        </Card.Content>
                    </Card>

                </ScrollView>

                {/* THANH THANH TOÁN DƯỚI CÙNG */}
                <View style={localStyles.bottomBar}>
                    <View style={{ flex: 1 }}>
                        <Text style={{ fontSize: 13, color: '#666' }}>Tổng cộng ({getNightCount()} đêm):</Text>
                        <Text style={{ fontSize: 20, fontWeight: 'bold', color: '#e53935' }}>
                            {getTotalPrice().toLocaleString('vi-VN')} đ
                        </Text>
                    </View>
                    <Button
                        mode="contained"
                        onPress={handleConfirmBooking}
                        loading={bookingLoading}
                        disabled={bookingLoading}
                        style={{ justifyContent: 'center' }}
                    >
                        Chốt đơn
                    </Button>
                </View>
            </View>
        </ScreenWrapper>

    );
};

const localStyles = StyleSheet.create({
    container: { padding: 10, paddingBottom: 100 },
    label: { fontSize: 16, marginBottom: 5 },
    value: { fontWeight: 'bold', color: '#1e88e5' },
    bottomBar: {
        position: 'absolute', bottom: 0, left: 0, right: 0,
        backgroundColor: '#fff',
        flexDirection: 'row',
        padding: 15,
        borderTopWidth: 1, borderColor: '#ddd',
        elevation: 10,
    }
});

export default Booking;