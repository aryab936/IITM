import router from '../router';

const state = {
    user:{},
    loggedIn:{status:false}
};
const getters = {};
const mutations = {};
const actions = {
     Loginfunc(_,user) {
        const uniqueresourcelocator="http://127.0.0.1:5000/login";
        let creds  = {"username":user.user_name,"password":user.pass_word}
        
        fetch(uniqueresourcelocator, {
            method: 'POST',
            mode: 'cors', 
            cache: 'no-cache', 
            credentials: 'omit', 
            headers: {
              'Content-Type': 'application/json'
              
            },
            redirect: 'follow', 
            referrerPolicy: 'no-referrer', 
            body: JSON.stringify(creds) 
          }).then( response => {return response.json();}) .then ( data => {if (data["authtoken"]){ state.user.authtoken = data["authtoken"]; localStorage.setItem("secret_authtoken",state.user.authtoken);state.user.loggedIn =true; router.push("/dashboard");} else{ router.push("/failedLogin");localStorage.removeItem("secret_authtoken");}})
    },
};
export default {
    state,
    getters,
    actions,
    mutations
}