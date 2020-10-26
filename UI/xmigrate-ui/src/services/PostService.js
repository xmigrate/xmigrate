import Axios from 'axios';
// import { LOGINURL } from './Services';

export default function PostService(API, data) {
    
    Axios.defaults.headers.common['Authorization'] = 'Bearer '+  localStorage.getItem('auth_token');
    let config = {
        withCredentials: false,
        headers: { "Content-Type": "application/json" }
    }
    let response = Axios.post(API, data, config).catch(error=>{
        console.log("Here");
        if(error.response.status === 401){
            return error.response.status
        }
        else{
            console.error(error);
        }
        
    });
    // response.then({}).catch(error => {
    //     console.log("Here");
    //     if(error.response.status === 401){
    //         return error.response.status
    //     }
    //     console.log(error.response.data);
    //     console.log(error.response.status);
    //     console.log(error.response.headers);
    //     // window.location.replace("/error");
    // })
    return response
}



