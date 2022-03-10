import Axios from 'axios';
// import {  LOGINURL } from './Services';
import {APPURL} from './Services';


export default function GetService(API) {
    Axios.defaults.headers.common['Authorization'] = 'Bearer '+localStorage.getItem('auth_token');
    let response = Axios.get(API, { withCredentials: false,headers: { "Content-Type": "application/json" }} )
    response.then({}).catch(error => {
        // window.location.replace(LOGINURL);
        console.log(error.response.data);
        console.log(error.response.status);
        console.log(error.response.headers);
        if(error.message === "Network Error"){
            window.location.replace("/404");
        }
        else if(error.response.status === 401 ){
            if(window.location.href === APPURL  ){
                console.log("401");
                return error.response.status;
            }else{
              window.location.replace("/401");
            }
           
      
        }
        else if(error.response.status === 404){
            window.location.replace("/404");
     } else if(error.response.status === 500){
         console.log(error.response);
          window.location.replace("/500");
        }
        else if(error.response.status === 400 ){
            window.location.replace("/400");
        }
        else if(error.response === undefined){
            console.log(error.response);
         window.location.replace("/500");
        }
        else{
            console.error(error);
        }
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
        if(error.message === "Network Error"){
            window.location.replace("/404");
        }
        else if(error.response.status === 401 ){
            if(window.location.href === APPURL  ){
                console.log("401");
                return error.response.status;
            }else{
              window.location.replace("/401");
            }
           
      
        }
        else if(error.response.status === 404){
            window.location.replace("/404");
     } else if(error.response.status === 500){
         console.log(error.response);
          window.location.replace("/500");
        }
        else if(error.response.status === 400 ){
            window.location.replace("/400");
        }
        else if(error.response === undefined){
            console.log(error.response);
         window.location.replace("/500");
        }
        else{
            console.error(error);
        }
        // window.location.replace("/error");
    })
    return response;

  
    
}