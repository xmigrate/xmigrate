import Axios from 'axios';
import {  LOGINURL } from './Services';


export default function GetService(API) {
    let response = Axios.get(API, { withCredentials: false,headers: { "Content-Type": "application/json" }} )
    response.then({}).catch(err => {
        // window.location.replace(LOGINURL);
        console.error(err)
    })
    return response
}

export function GetServiceWithData(API, data) {
    let config = {
        withCredentials: false,
        headers: { "Content-Type": "application/json" },
        params: data
    }
    let response = Axios.get(API, config)
    response.then({}).catch(err => {
        console.error(err);
        // window.location.replace(LOGINURL);
    })
    return response;
}