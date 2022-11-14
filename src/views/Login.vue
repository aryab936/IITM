<template>
        <div class="container">
                    <b-card header="Login" header-bg-variant="warning" header-text-variant="black">
                            <b-form @submit="onSubmit">
                                <b-form-group description="Please enter your username" label="USERNAME">
                                    <b-form-input v-model="Users.user_name" required></b-form-input>
                                </b-form-group>
                                <b-form-group description="Please enter your password" label="PASSWORD">
                                    <b-form-input v-model="Users.pass_word" required type="password"></b-form-input>
                                </b-form-group>
                                <b-form-group>
                                    <b-button type="submit" @click="onSubmit" variant="info">Submit</b-button>&nbsp;&nbsp;&nbsp;&nbsp;<b-button @click="onForgot" variant="danger">Forgot Password?</b-button>&nbsp;&nbsp;&nbsp;&nbsp;<b-button @click="onNew" variant="success">New User Registration</b-button>
                                </b-form-group>
                            </b-form>
                    </b-card>
        </div>
</template>


<script>
import {store} from "../main.js"; 
import router from "../router"
export default {
    name:"LoginView",
    data:() =>({
        Users: {
            user_name:"",
            pass_word:""
        }
    }),
    methods: {
        onSubmit(x){
            x.preventDefault()
            store.dispatch("Loginfunc",this.Users)
        },
        onForgot(){
            router.push("/forgotPassword");
        },
        onNew(){
            router.push("/newUser");
        }
    },
}
</script>