import React, { useState, useEffect, useContext } from 'react';
import { View, Text, ScrollView, ActivityIndicator, StyleSheet, RefreshControl, Alert } from 'react-native';
import { BarChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import Apis, { endpoints } from '../../configs/Apis';
import styles from ''; // Import file Styles.js vừa tạo

import { MyUserContext } from '../../../App'; // Kiểm tra đường dẫn tới file chứa Context User

const screenWidth = Dimensions.get('window').width;

const AdminDashboard = () => {
    const [user] = useContext(MyUserContext); // Lấy thông tin user
    const navigation = useNavigation();
    const [loading, setLoading] = useState(false);
    const [isAuthorized, setIsAuthorized] = useState(false);
    const [revenueData, setRevenueData] = useState(null);

    // 1. MOCK DATA (Dùng để test giao diện)
    const mockData = {
        "revenue_by_months": [
            { "month": 1, "total_revenue": 5000000 },
            { "month": 2, "total_revenue": 8000000 },
            { "month": 3, "total_revenue": 12000000 },
            { "month": 4, "total_revenue": 7000000 },
            { "month": 5, "total_revenue": 15000000 },
            { "month": 6, "total_revenue": 10000000 }
        ]
    };

    // 2. Kiểm tra quyền khi component được load
    useEffect(() => {
        if (user && user.role === 'MANAGER') {
            setIsAuthorized(true);
            loadRevenue();
        } else {
            Alert.alert("Thông báo", "Bạn không có quyền truy cập trang này!");
            navigation.navigate('Home');
        }
    }, [user]);

    // 3. Hàm tải dữ liệu
    const loadRevenue = async () => {
        setLoading(true);
        try {
            // 🚀 CHƯA CÓ API THẬT: Dùng mockData
            setRevenueData(mockData); 

            // 🚀 CÓ API THẬT: Comment dòng trên, bỏ comment 2 dòng dưới
            // let res = await Apis.get(endpoints['revenue-report']);
            // setRevenueData(res.data);
        } catch (err) {
            console.error("Lỗi:", err);
        } finally {
            setLoading(false);
        }
    };

    // Nếu chưa kiểm tra xong quyền hoặc không có quyền, hiển thị loading
    if (!isAuthorized) {
        return <View style={styles.center}><ActivityIndicator size="large" /></View>;
    }

    return (
        <ScrollView 
            style={styles.container}
            refreshControl={<RefreshControl refreshing={loading} onRefresh={loadRevenue} />}
        >
            <Text style={styles.title}>Dashboard Quản lý</Text>

            {revenueData ? (
                <View>
                    <Text style={styles.subTitle}>Doanh thu theo tháng (triệu VNĐ)</Text>
                    <BarChart
                        data={{
                            labels: revenueData.revenue_by_months.map(item => `T${item.month}`),
                            datasets: [{
                                data: revenueData.revenue_by_months.map(item => item.total_revenue / 1000000)
                            }]
                        }}
                        width={screenWidth - 40}
                        height={250}
                        chartConfig={{
                            backgroundColor: '#ffffff',
                            backgroundGradientFrom: '#fb8c00',
                            backgroundGradientTo: '#ffa726',
                            decimalPlaces: 0,
                            color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
                            labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
                        }}
                        style={styles.chart}
                    />
                </View>
            ) : (
                <ActivityIndicator size="large" />
            )}
        </ScrollView>
    );
};


export default AdminDashboard;