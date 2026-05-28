import React, { useState, useEffect, useContext } from 'react';
import { View, FlatList, ActivityIndicator, Alert } from 'react-native';
import { Text, Card, Title, Paragraph, Button } from 'react-native-paper';

import { MyUserContext } from '../../reducers/MyUserReducer';
import API, { endpoints } from '../../configs/Apis';
import styles from '../../styles/Styles';
import Footer from '../../components/Footer';
import ScreenWrapper from '../../components/ScreenWrapper';

const RoomDetail = ({ route, navigation }) => {
    const { roomTypeId, roomTypeName } = route.params;
    const user = useContext(MyUserContext);

    const [rooms, setRooms] = useState([]);

    // States cho Lazy Loading
    const [loading, setLoading] = useState(true);
    const [loadingMore, setLoadingMore] = useState(false);
    const [page, setPage] = useState(1);
    const [hasNextPage, setHasNextPage] = useState(true);

    const loadRooms = async () => {
        if (!hasNextPage) return;

        if (page === 1) setLoading(true);
        else setLoadingMore(true);

        try {
            let res = await API.get(`${endpoints['rooms']}?room_type=${roomTypeId}&page=${page}`);
            
            // Rút trích dữ liệu an toàn
            const newData = res.data.results || res.data || [];
            
            if (page === 1) {
                setRooms(newData);
            } else {
                setRooms(currentRooms => [...currentRooms, ...newData]);
            }

            if (!res.data.next) {
                setHasNextPage(false);
            }
        } catch (error) {
            console.error("Lỗi khi tải danh sách phòng:", error);
        } finally {
            setLoading(false);
            setLoadingMore(false);
        }
    };

    // Lắng nghe sự thay đổi của page
    useEffect(() => {
        loadRooms();
    }, [page, roomTypeId]);

    const handleLoadMore = () => {
        if (!loadingMore && hasNextPage) {
            setPage(page + 1);
        }
    };

    const renderRoomItem = ({ item }) => {
        let statusText = 'Trống';
        let statusColor = 'green';

        if (item.status === 'OCCUPIED') {
            statusText = 'Đang có khách';
            statusColor = 'red';
        } else if (item.status === 'CLEANING') {
            statusText = 'Đang dọn dẹp';
            statusColor = 'orange';
        } else if (item.status === 'MAINTENANCE') {
            statusText = 'Bảo trì';
            statusColor = 'gray';
        }

        return (
            <Card style={styles.card}>
                {item.image && <Card.Cover source={{ uri: item.image }} />}

                <Card.Content>
                    <Title style={styles.title}>Phòng {item.room_number}</Title>
                    <Paragraph>
                        Trạng thái:
                        <Text style={{ color: statusColor, fontWeight: 'bold' }}> {statusText}</Text>
                    </Paragraph>
                </Card.Content>

                <Card.Actions>
                    <Button
                        mode="contained"
                        disabled={item.status !== 'AVAILABLE'}
                        onPress={() => {
                            if (user === null) {
                                Alert.alert("Thông báo", "Vui lòng đăng nhập để thực hiện đặt phòng!");
                            } else {
                                navigation.navigate('Booking', {
                                    roomId: item.id,
                                    roomNumber: item.room_number,
                                    basePrice: item.room_type_info ? item.room_type_info.base_price : route.params.roomTypePrice
                                });
                            }
                        }}
                    >
                        {item.status === 'AVAILABLE' ? 'Đặt phòng ngay' : 'Không khả dụng'}
                    </Button>
                </Card.Actions>
            </Card>
        );
    };

    const renderFooter = () => {
        if (!loadingMore) return null;
        return <ActivityIndicator size="small" color="#1e88e5" style={{ padding: 20 }} />;
    };

    return (
        <ScreenWrapper isLoading={loading && page === 1}>
            <View style={styles.container}>
                <Text style={styles.headerTitle}>LOẠI: {roomTypeName.toUpperCase()}</Text>

                {loading && page === 1 ? (
                    <ActivityIndicator size="large" color="#1e88e5" style={styles.loader} />
                ) : rooms.length === 0 ? (
                    <Text style={{ textAlign: 'center', marginTop: 20, fontStyle: 'italic', color: '#666' }}>
                        Hiện tại không có phòng nào thuộc loại này.
                    </Text>
                ) : (
                    <FlatList
                        data={rooms}
                        keyExtractor={item => item.id.toString()}
                        renderItem={renderRoomItem}
                        contentContainerStyle={styles.listContainer}
                        showsVerticalScrollIndicator={false}

                        // Lazy Loading Props
                        onEndReached={handleLoadMore}
                        onEndReachedThreshold={0.5}
                        ListFooterComponent={renderFooter}
                    />
                )}
                <Footer />
            </View>
        </ScreenWrapper>

    );
}

export default RoomDetail;