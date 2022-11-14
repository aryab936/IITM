<template>
        <div class="container">
                    <b-card header="New User Registration" header-bg-variant="success" header-text-variant="black">
                            <b-form @submit="onSubmit">
                                <b-form-group description="Please enter your first name" label="FIRST NAME">
                                    <b-form-input v-model="first_name" required></b-form-input>
                                </b-form-group>
                                <b-form-group description="Please enter your last name" label="LAST NAME">
                                    <b-form-input v-model="last_name" required></b-form-input>
                                </b-form-group>
                                <b-form-group description="Please enter your username" label="USERNAME">
                                    <b-form-input v-model="user_name" required></b-form-input>
                                </b-form-group>
                                <b-form-group description="Please enter your email" label="EMAIL">
                                    <b-form-input v-model="email" required type="email"></b-form-input>
                                </b-form-group>
                                <b-form-group description="Please enter your chat space URL. You can leave it blank if you want to use the default space." label="CHAT SPACE URL">
                                    <b-form-input v-model="url"></b-form-input>
                                </b-form-group>
                                 <b-form-group description="Please enter your password" label="PASSWORD">
                                    <b-form-input v-model="password" required type="password"></b-form-input>
                                </b-form-group>
                                <b-form-group>
                                    <b-button type="submit" @click="onSubmit" variant="primary">Submit</b-button>
                                </b-form-group>
                            </b-form>
                    </b-card>
        </div>
</template>

<script>
import router from "../router"
export default {
    name:"NewUser",
    data:() =>(
        {
            first_name:"",
            user_name:"",
            last_name:"",
            email:"",
            url:"",
            password:""
    }),
    methods: {
        onSubmit(x){
            x.preventDefault();
            let path = "http://localhost:5000/newUser";
            let data = {user_name:this.user_name,email:this.email, first_name:this.first_name, last_name:this.last_name,url:this.url, password:this.password};
            if (this.first_name.length ==0 || this.user_name.length ==0 || this.last_name.length ==0 || this.email.length ==0 || this.password.length ==0){
                alert("Please enter all mandatory fields");
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
            }).then( (response) => {return response.json();} ).then( (abc) => {if (abc.status == "success"){alert("Your account is successfully created");router.push("/login");} else{ alert(abc.message());}}).catch( e => console.log(e));
            
        }
    },
}
</script>