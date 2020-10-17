class Auth{
    constructor(){
        this.authenticated = false;
    }

    login(cb){

        this.authenticated = true;

    cb();
    }

    logout(cb){
        this.authenticated =false;
        localStorage.removeItem('auth_token');
        cb();
    }

    isAuthenticated(){
        let token = localStorage.getItem('auth_token');
        if(token!= null){
            return true;
        }
        else{
            return false;
        }
        // return this.authenticated;
    }

}

export default new Auth();