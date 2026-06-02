import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, ActivityIndicator, StyleSheet, RefreshControl } from 'react-native';
import { BarChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';
import Apis, { endpoints } from '../../configs/Apis'; // Sếp đảm bảo import đúng đường dẫn nhé

const screenWidth = Dimensions.get('window').width;

const AdminDashboard = () => {
    const [loading, setLoading] = useState(false);
    const [revenueData, setRevenueData] = useState(null);

    // 1. MOCK DATA (Dùng để test giao diện trước khi API xong)
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

    const loadRevenue = async () => {
        setLoading(true);
        try {
            // 🚀 KHI CHƯA CÓ API THẬT: Dùng mockData
            setRevenueData(mockData); 

            // 🚀 KHI CÓ API THẬT: Sếp comment dòng trên và bỏ comment 2 dòng dưới:
            // let res = await Apis.get(endpoints['revenue-report']);
            // setRevenueData(res.data);
            
        } catch (err) {
            console.error("Lỗi lấy báo cáo:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadRevenue();
    }, []);

    return (
        <ScrollView 
            style={styles.container}
            refreshControl={<RefreshControl refreshing={loading} onRefresh={loadRevenue} />}
        >
            <Text style={styles.title}>Báo cáo Doanh thu (Năm 2026)</Text>

            {revenueData ? (
                <BarChart
                    data={{
                        labels: revenueData.revenue_by_months.map(item => `T${item.month}`),
                        datasets: [{
                            data: revenueData.revenue_by_months.map(item => item.total_revenue / 1000000) // Chia cho 1tr để số hiển thị gọn
                        }]
                    }}
                    width={screenWidth - 40}
                    height={250}
                    yAxisLabel="tr"
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
            ) : (
                <ActivityIndicator size="large" />
            )}
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, padding: 20, backgroundColor: '#f5f5f5' },
    title: { fontSize: 20, fontWeight: 'bold', marginBottom: 20, textAlign: 'center' },
    chart: { marginVertical: 8, borderRadius: 16 }
});

export default AdminDashboard;