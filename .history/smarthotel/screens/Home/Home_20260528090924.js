import React, { useState, useEffect } from 'react';
import { View, FlatList } from 'react-native';
import { Text, Card, Title, Paragraph, Button } from 'react-native-paper';
import Styles from '../../styles/Styles';
import Footer from '../../components/Footer';
import API, { endpoints } from '../../configs/Apis';
import ScreenWrapper from '../../components/ScreenWrapper';


const Home = ({ navigation }) => {
>>>>>>> 3ab3b3fcae8db40b5a12df7722edf6df058752ec
    const [roomTypes, setRoomTypes] = useState([]);

    // States cho Lazy Loading
    const [loading, setLoading] = useState(true); // Loading lần đầu
    const [loadingMore, setLoadingMore] = useState(false); // Loading khi cuộn
    const [page, setPage] = useState(1); // Trang hiện tại
    const [hasNextPage, setHasNextPage] = useState(true); // Kiểm tra còn dữ liệu không

    const loadRoomTypes = async () => {
        if (!hasNextPage) return;

        if (page === 1) setLoading(true);
        else setLoadingMore(true);

        try {
            let res = await API.get(`${endpoints['roomtypes']}?page=${page}`);
            
            // 1. Rút trích dữ liệu an toàn (Nếu có results thì lấy, không thì lấy data trực tiếp)
            const newData = res.data.results || res.data || [];

            // 2. Gán dữ liệu
            if (page === 1) {
                setRoomTypes(newData);
            } else {
                setRoomTypes(currentTypes => [...currentTypes, ...newData]);
            }

            // 3. Kiểm tra trang tiếp theo an toàn
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

    // Gọi API mỗi khi biến page thay đổi
    useEffect(() => {
        loadRoomTypes();
    }, [page]);

    // Hàm xử lý khi cuộn đến cuối danh sách
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
<<<<<<< HEAD
            {/* <Card.Actions>
                <Button 
                    mode="contained" 
                    onPress={() => console.log('Sẽ chuyển sang chi tiết phòng:', item.id)}
=======
            <Card.Actions>
                <Button
                    mode="contained"
                    onPress={() => navigation.navigate('RoomDetail', {
                        roomTypeId: item.id,
                        roomTypeName: item.name,
                    })}
>>>>>>> 3ab3b3fcae8db40b5a12df7722edf6df058752ec
                >
                    Xem chi tiết
                </Button>
            </Card.Actions> */}
            <Button 
                    mode="contained" 
                    // Chuyển hướng sang màn hình 'Checkout' và gửi kèm thông tin loại phòng
                    onPress={() => {
                        console.log('Chuyển sang trang thanh toán cho loại phòng:', item.name);
                        navigation.navigate('Checkout', { 
                            roomTypeId: item.id,
                            roomTypeName: item.name,
                            roomPrice: item.base_price
                        });
                    }}
                >
                    Đặt & Thanh toán
                </Button>
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