import React, { useState, useEffect } from 'react';
import { View, FlatList } from 'react-native';
import { Text, Card, Title, Paragraph, Button } from 'react-native-paper';
import Styles from '../../styles/Styles';
import Footer from '../../components/Footer';
import API, { endpoints } from '../../configs/Apis';
import ScreenWrapper from '../../components/ScreenWrapper';

const Home = ({ navigation }) => {
    const [roomTypes, setRoomTypes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [loadingMore, setLoadingMore] = useState(false); 
    const [page, setPage] = useState(1); 
    const [hasNextPage, setHasNextPage] = useState(true); 

    const loadRoomTypes = async () => {
        if (!hasNextPage) return;

        if (page === 1) setLoading(true);
        else setLoadingMore(true);

        try {
            let res = await API.get(`${endpoints['roomtypes']}?page=${page}`);
            
            const newData = res.data.results || res.data || [];

            if (page === 1) {
                setRoomTypes(newData);
            } else {
                setRoomTypes(currentTypes => [...currentTypes, ...newData]);
            }

            if (!res.data.next) {
                setHasNextPage(false);
            }
        } catch (error) {
            console.error("Lỗi khi tải danh sách loại phòng:", error);
        } finally {
            setLoading(false);
            setLoadingMore(false);
        }
    };

    useEffect(() => {
        loadRoomTypes();
    }, [page]);

    const handleLoadMore = () => {
        if (!loadingMore && hasNextPage) {
            setPage(page + 1);
        }
    };

    const renderItem = ({ item }) => (
        <Card style={Styles.card}>
            {item.image && <Card.Cover source={{ uri: item.image }} />}
            <Card.Content>
                <Title style={Styles.title}>{item.name}</Title>
                <Paragraph numberOfLines={2}>{item.description}</Paragraph>
                <Text style={Styles.price}>
                    Giá: {Number(item.base_price).toLocaleString('vi-VN')} VNĐ
                </Text>
                <Text style={Styles.capacity}>
                    Sức chứa: {item.capacity} người
                </Text>
            </Card.Content>
            <Card.Actions>
                <Button
                    mode="contained"
                    onPress={() => navigation.navigate('RoomDetail', {
                        roomTypeId: item.id,
                        roomTypeName: item.name,
                    })}
                >
                    Xem chi tiết
                </Button>
            </Card.Actions>
        </Card>
    );

    // Component hiển thị vòng xoay dưới đáy khi đang tải thêm
    const renderFooter = () => {
        if (!loadingMore) return null;
        return <ActivityIndicator size="small" color="#1e88e5" style={{ padding: 20 }} />;
    };

    return (
        // BỌC TOÀN BỘ GIAO DIỆN VÀO TRONG SCREEN WRAPPER
        // Truyền biến loading lần đầu của API vào prop isLoading
        <ScreenWrapper isLoading={loading && page === 1}>
            <View style={Styles.container}>
                <FlatList
                    data={roomTypes}
                    keyExtractor={item => item.id.toString()}
                    renderItem={renderItem}
                    contentContainerStyle={Styles.listContainer}
                    showsVerticalScrollIndicator={false}
                    onEndReached={handleLoadMore}
                    onEndReachedThreshold={0.5}
                    ListFooterComponent={renderFooter}
                />
                <Footer />
            </View>
        </ScreenWrapper>
    );
}

export default Home;