<template>
        <div class="container">
                    <b-card header="Update Tracker" header-bg-variant="danger" header-text-variant="white">
                            <b-form @submit="onSubmit">
                                <b-form-group description="Please enter the name if you wish to modify" label="NAME">
                                    <b-form-input v-model="name"></b-form-input>
                                </b-form-group>
                                <b-form-group description="Please enter the description if you wish to change" label="DESCRIPTION">
                                    <b-form-input v-model="description"></b-form-input>
                                </b-form-group>
                                <b-form-group description="Please enter any options (in a comma separated manner) you wish to be deleted." label="OPTIONS TO BE DELETED">
                                    <b-form-input v-model="options"></b-form-input>
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

export default {
    name:"dashboardMultiUpdate",
    data: () =>({
            name:null,
            description:null,
            options:null
    }),
    methods: {
        removeOptions(){
            if (this.options.length > 0){
                let x = this.options.split(",");  
                let trackersID = localStorage.getItem("updateTrackerID");
                let authtoken = localStorage.getItem("secret_authtoken");              
                for (let item of x){
                    let path = `http://127.0.0.1:5000/deleteOptions/${trackersID}/${item}`;
                    fetch(path, {
                    method: 'DELETE', 
                    mode: 'cors', 
                    cache: 'no-cache', 
                    credentials: 'omit', 
                    headers: {
                        'Content-Type': 'application/json',
                        'secret-authtoken' : authtoken
                       
                    },
                    redirect: 'follow', 
                    referrerPolicy: 'no-referrer', 
                    })
                }
            }
        },
        onSubmit(x){
            x.preventDefault();
            this.removeOptions();
            let uniqueresourcelocator = "http://127.0.0.1:5000/dashboard";
            let trackersID = localStorage.getItem("updateTrackerID");
            let authtoken = localStorage.getItem("secret_authtoken");
            let data = {tracker_id:trackersID,name:this.name,description:this.description};
            fetch(uniqueresourcelocator, {
            method: 'PATCH', 
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
          }).then( response => { return response.json()}).then ( (data) => {if(data.status !="failed"){alert("The updation operation was successfully processed");router.push("/dashboard");localStorage.removeItem("updateLogID");} else{alert("Please enter a number only");location.reload();}}).catch( e => console.log(e));
        }
    }
    
}


</script>