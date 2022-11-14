<template>
        <div class="container">
                    <b-card header="Add Tracker" header-bg-variant="warning" header-text-variant="black">
                            <b-form @submit="onSubmit">
                                <b-form-group description="Please enter a name for the tracker" label="NAME">
                                    <b-form-input v-model="name" required></b-form-input>
                                </b-form-group>
                                <b-form-group description="Please enter the type of the tracker." label="TYPE">
                                    <b-form-select v-model="type" :options="options" required></b-form-select>
                                </b-form-group>
                                <b-form-group description="Please enter a description for the tracker" label="DESCRIPTION">
                                    <b-form-input v-model="description" required></b-form-input>
                                </b-form-group>
                                <b-form-group>
                                    <b-button type="submit" @click="onSubmit" variant="success">Submit</b-button>
                                </b-form-group>
                            </b-form>
                    </b-card>
        </div>
</template>

<script>
import router from "../router"

export default{
    name:"dashboardAdd",
    data : () => ({
        name:"",
        type:null,
        description:"",
        options:["Numerical", "Multi Choice", "Time Duration", "Boolean"]
        
    }),
    methods:{
        onSubmit(x) {
            x.preventDefault();
            let uniqueresourcelocator = "http://127.0.0.1:5000/dashboard";
            let authtoken = localStorage.getItem("secret_authtoken");
            let data = {tracker_name:this.name,tracker_type:this.type,description:this.description};
            if (this.description.length == 0){
                alert("Please enter a description");
                location.reload();
            }
            fetch(uniqueresourcelocator, {
                method: 'POST', 
                mode: 'cors', 
                cache: 'no-cache',
                credentials: 'omit', 
                headers: {
                'Content-Type': 'application/json',
                'secret-authtoken' : authtoken
                
                },
                redirect: 'follow',
                referrerPolicy: 'no-referrer', 
                body: JSON.stringify(data) 
            }).then( response => { return response.json()}).then ( (thing) => { if(thing.status!="failure"){alert("The addition operation was successful");router.push("/dashboard")} else{alert(thing.message);location.reload();}}).catch( e => console.log(e));
        }
        
    },
}

</script>