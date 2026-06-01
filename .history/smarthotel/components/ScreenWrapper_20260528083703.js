import React, { useState, useCallback } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { Text } from 'react-native-paper';
import { useFocusEffect } from '@react-navigation/native';

// Nhận 2 tham số: 
// 1. children: Nội dung của trang muốn hiển thị
// 2. isLoading: Cờ báo hiệu API của trang đó đang tải (tùy chọn)
const ScreenWrapper = ({ children, isLoading = false }) => {
    const [isScreenTransitioning, setIsScreenTransitioning] = useState(false);

    useFocusEffect(
        useCallback(() => {
            setIsScreenTransitioning(true);
            const timer = setTimeout(() => {
                setIsScreenTransitioning(false);
            }, 300);

            return () => clearTimeout(timer);
        }, [])
    );

    // Nếu đang chuyển trang HOẶC api đang tải -> Hiện vòng xoay
    if (isScreenTransitioning || isLoading) {
        return (
            <View style={styles.center}>
                <ActivityIndicator size="large" color="#1e88e5" />
                <Text style={{ marginTop: 10, color: '#666' }}>Đang tải giao diện...</Text>
            </View>
        );
    }

    // Nếu tải xong -> Trả về giao diện thật của trang
    return <View style={styles.container}>{children}</View>;
};

const styles = StyleSheet.create({
    center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f5f5f5' },
    container: { flex: 1 }
});

export default ScreenWrapper;