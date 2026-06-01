import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Button, Card, Title, Divider, Icon } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';

const PaymentResult = ({ route, navigation }) => {
    // Nhận thêm dữ liệu truyền sang
    const { bookingId, totalPrice, status, roomName, checkIn, checkOut } = route.params;

    return (
        <ScrollView contentContainerStyle={styles.container}>
            {/* Icon Thành công */}
            <View style={styles.iconContainer}>
                <MaterialCommunityIcons name="check-circle-outline" color="#4caf50" size={80} />
                <Title style={styles.title}>Thanh toán thành công!</Title>
            </View>

            <Card style={styles.card}>
                <Card.Content>
                    <Title style={styles.sectionTitle}>Thông tin đặt phòng</Title>
                    <Divider style={styles.divider} />
                    
                    <InfoRow label="Mã đơn hàng" value={`#${bookingId}`} />
                    <InfoRow label="Phòng" value={roomName} />
                    <InfoRow label="Nhận phòng" value={checkIn} />
                    <InfoRow label="Trả phòng" value={checkOut} />
                    
                    <Divider style={styles.divider} />
                    
                    <View style={styles.totalRow}>
                        <Text style={styles.totalLabel}>Tổng thanh toán</Text>
                        <Text style={styles.totalValue}>{totalPrice.toLocaleString('vi-VN')} VNĐ</Text>
                    </View>
                </Card.Content>
            </Card>

            <Button mode="contained" onPress={() => navigation.navigate('Home')} style={styles.button}>
                Về trang chủ
            </Button>
            <Button mode="outlined" onPress={() => { /* Logic xem chi tiết */ }} style={styles.outlineButton}>
                Xem chi tiết đặt phòng
            </Button>
        </ScrollView>
    );
};

// Component con để hiển thị từng dòng thông tin cho cân đối
const InfoRow = ({ label, value }) => (
    <View style={styles.row}>
        <Text style={styles.label}>{label}</Text>
        <Text style={styles.value}>{value}</Text>
    </View>
);

const styles = StyleSheet.create({
    container: { flexGrow: 1, padding: 20, backgroundColor: '#f9f9f9' },
    iconContainer: { alignItems: 'center', marginVertical: 30 },
    title: { color: '#2e7d32', marginTop: 10, fontSize: 22 },
    card: { borderRadius: 15, elevation: 4, backgroundColor: '#fff' },
    sectionTitle: { fontSize: 18, marginBottom: 10, fontWeight: 'bold' },
    divider: { marginVertical: 10 },
    row: { flexDirection: 'row', justifyContent: 'space-between', marginVertical: 6 },
    label: { color: '#666', fontSize: 15 },
    value: { fontWeight: '600', fontSize: 15 },
    totalRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 10 },
    totalLabel: { fontSize: 16, fontWeight: 'bold' },
    totalValue: { fontSize: 18, fontWeight: 'bold', color: '#d32f2f' },
    button: { marginTop: 25, paddingVertical: 5 },
    outlineButton: { marginTop: 15, paddingVertical: 5 }
});

export default PaymentResult;