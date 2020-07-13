import Axios from 'axios';
import { LOGINURL } from './Services';

export default function PostService(API, data) {
    let config = {
        withCredentials: true,
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        params: data
    }
    let response = Axios.post(API, data, config);
    response.then({}).catch(err => {
        console.error(err)
        // window.location.replace(LOGINURL);
    })
    return response
}



