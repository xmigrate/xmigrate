import Axios from 'axios';
// import {  LOGINURL } from './Services';


export default function GetService(API) {
    Axios.defaults.headers.common['Authorization'] = 'Bearer '+localStorage.getItem('auth_token');
    let response = Axios.get(API, { withCredentials: false,headers: { "Content-Type": "application/json" }} )
    response.then({}).catch(err => {
        // window.location.replace(LOGINURL);
        console.error(err)
    })
    return response
}

export function GetServiceWithData(API, dataGet) {
    let response = Axios.get(API,{
        withCredentials: false,
        headers: { "Content-Type": "application/json" },
        params: dataGet
    })
    response.then({}).catch(err => {
        console.error(err);
        window.location.replace("/error");
    })
    return response;

  
    
}