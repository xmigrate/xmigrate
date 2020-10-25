import Axios from 'axios';
// import {  LOGINURL } from './Services';


export default function GetService(API) {
    Axios.defaults.headers.common['Authorization'] = 'Bearer '+localStorage.getItem('auth_token');
    let response = Axios.get(API, { withCredentials: false,headers: { "Content-Type": "application/json" }} )
    response.then({}).catch(error => {
        // window.location.replace(LOGINURL);
        console.log(error.response.data);
        console.log(error.response.status);
        console.log(error.response.headers);
    })
    return response
}

export function GetServiceWithData(API, dataGet) {
    Axios.defaults.headers.common['Authorization'] = 'Bearer '+localStorage.getItem('auth_token');
    let response = Axios.get(API,{
        withCredentials: false,
        headers: { "Content-Type": "application/json" },
        params: dataGet
    })
    response.then({}).catch(error => {
        console.log(error.response.data);
        console.log(error.response.status);
        console.log(error.response.headers);
        // window.location.replace("/error");
    })
    return response;

  
    
}