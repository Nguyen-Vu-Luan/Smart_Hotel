import { StyleSheet } from 'react-native';

export default StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    loader: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    headerTitle: {
        textAlign: 'center',
        fontSize: 20,
        fontWeight: 'bold',
        marginVertical: 15,
        color: '#333',
    },
    listContainer: {
        paddingHorizontal: 15,
        paddingBottom: 20,
    },
    card: {
        marginBottom: 20,
        borderRadius: 10,
        backgroundColor: '#fff',
        shadowColor: '#000', 
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3, 
    },
    title: {
        color: '#1e88e5',
        marginTop: 10,
        fontWeight: 'bold',
    },
    price: {
        fontWeight: 'bold',
        color: '#e53935',
        marginTop: 8,
        fontSize: 16,
    },
    capacity: {
        fontStyle: 'italic',
        color: '#666',
        marginTop: 4,
    }
});