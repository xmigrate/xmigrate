import Axios from 'axios';
// import { LOGINURL } from './Services';

export default function PostService(API, data) {
    
    Axios.defaults.headers.common['Authorization'] = 'Bearer '+  localStorage.getItem('auth_token');
    let config = {
        withCredentials: false,
        headers: { "Content-Type": "application/json" },
        params: data
    }
    let response = Axios.post(API, data, config);
    response.then({}).catch(err => {
        console.error(err)
        // window.location.replace(LOGINURL);
    })
    return response
}



