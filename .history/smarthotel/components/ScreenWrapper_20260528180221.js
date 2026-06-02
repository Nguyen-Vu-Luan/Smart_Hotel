import React, { useState, useCallback } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { Text } from 'react-native-paper';
import { useFocusEffect } from '@react-navigation/native';


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

    
    if (isScreenTransitioning || isLoading) {
        return (
            <View style={styles.center}>
                <ActivityIndicator size="large" color="#1e88e5" />
                <Text style={{ marginTop: 10, color: '#666' }}>Đang tải giao diện...</Text>
            </View>
        );
    }

    
    return <View style={styles.container}>{children}</View>;
};

const styles = StyleSheet.create({
    center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f5f5f5' },
    container: { flex: 1 }
});

export default ScreenWrapper;