<template>
        <div class="container">
                    <b-card header="Password Revival" header-bg-variant="info" header-text-variant="black">
                            <b-form @submit="onSubmit">
                                <b-form-group description="Please enter your username" label="USERNAME">
                                    <b-form-input v-model="user_name" required></b-form-input>
                                </b-form-group>
                                <b-form-group description="Please enter your email" label="EMAIL">
                                    <b-form-input v-model="email" required type="email"></b-form-input>
                                </b-form-group>
                                <b-form-group>
                                    <b-button type="submit" @click="onSubmit" variant="dark">Submit</b-button>
                                </b-form-group>
                            </b-form>
                    </b-card>
        </div>
</template>

<script>
import router from "../router"
export default {
    name:"ForgotPassword",
    data:() =>(
        {
            user_name:"",
            email:""
    }),
    methods: {
        onSubmit(x){
            x.preventDefault();
            let path = "http://localhost:5000/forgotPassword";
            let data = {user_name:this.user_name,email:this.email};
            if (this.user_name.length == 0 || this.email.length ==0 ){
                alert("Please enter all fields!");
                location.reload();
            }
            fetch(path,{
                method: 'POST', 
                mode: 'cors', 
                cache: 'no-cache', 
                credentials: 'omit', 
                headers: {
                    'Content-Type': 'application/json',
                },
                redirect: 'follow', 
                referrerPolicy: 'no-referrer',
                body: JSON.stringify(data)  
            }).then( () => {alert("We have received your request. In case you are a registered user and the details you submitted are correct, you will receive an email with your password.");router.push("/login");}).catch( e => console.log(e));
            
        }
    },
}
</script>