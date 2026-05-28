import React, { useState, useEffect } from 'react';
import { View, FlatList, ActivityIndicator } from 'react-native';
import { Text, Card, Title, Paragraph, Button } from 'react-native-paper';
import Styles from '../../styles/Styles';

import API, { endpoints } from '../../configs/Apis';

const Home = ({navi}) => {
    const [roomTypes, setRoomTypes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadRoomTypes = async () => {
            try {
                let res = await API.get(endpoints['roomtypes']);
                setRoomTypes(res.data.results || res.data); 
            } catch (error) {
                console.error("Lỗi khi tải danh sách loại phòng:", error);
            } finally {
                setLoading(false);
            }
        };

        loadRoomTypes();
    }, []);

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
            {/* <Card.Actions>
                <Button 
                    mode="contained" 
                    onPress={() => console.log('Sẽ chuyển sang chi tiết phòng:', item.id)}
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

    return (
        <View style={Styles.container}>
            <Text style={Styles.headerTitle}>DANH SÁCH LOẠI PHÒNG</Text>

            {loading ? (
                <ActivityIndicator size="large" color="#1e88e5" style={Styles.loader} />
            ) : (
                <FlatList
                    data={roomTypes}
                    keyExtractor={item => item.id.toString()}
                    renderItem={renderItem}
                    contentContainerStyle={Styles.listContainer}
                    showsVerticalScrollIndicator={false}
                />
            )}
        </View>
    );
}

export default Home;