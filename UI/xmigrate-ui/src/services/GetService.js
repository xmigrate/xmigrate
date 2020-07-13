import Axios from 'axios';
import {  LOGINURL } from './Services';


export default function GetService(API) {
    let response = Axios.get(API, { withCredentials: true,headers: { "Content-Type": "application/x-www-form-urlencoded" }} )
    response.then({}).catch(err => {
        window.location.replace(LOGINURL);
    })
    return response
}

export function GetServiceWithData(API, data) {
    let config = {
        withCredentials: true,
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        params: data
    }
    let response = Axios.get(API, config)
    response.then({}).catch(err => {
        window.location.replace(LOGINURL);
    })
    return response;
}