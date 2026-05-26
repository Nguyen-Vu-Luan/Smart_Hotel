import { useEffect, useState } from "react";
import { Text } from "react-native-paper";
import Apis, { endpoints } from "../configs/Apis";

const Header= () => {
    // const [roomtypes, setRoomtypes] = useState([]);
    
    // const loadRoomtypes = async () => {
    //     let res = await Apis.get(endpoints['roomtypes']);
    //     setRoomtypes(res.data);
    // }

    // useEffect(() => {
    //     loadRoomtypes();
    // }, [])

    return (
        <Text>HEADER</Text>
    );
}

export default Header;