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
        if(error.message === "Network Error"){
            window.location.replace("/404");
        }
        else if(error.response.status === 401 ){
            console.log("401");
            return error.response.status;
            //  window.alert("Unauthorised login!!!");
            //  window.location.replace("/");
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



