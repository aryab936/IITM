<template>
        <div class="container">
                    <b-card header="Add Options for Multi Choice" header-bg-variant="warning" header-text-variant="black">
                            <b-form @submit="onSubmit">
                                <b-form-group description="Please enter the options for the tracker in a comma separated way." label="OPTIONS">
                                    <b-form-input v-model="options" required></b-form-input>
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
    name:"addOptions",
    data : () => ({
            options:null 
    }),
    methods:{
        onSubmit(x) {
            x.preventDefault();
            let tid = localStorage.getItem("optionAddID");
            let uniqueresourcelocator = `http://127.0.0.1:5000/optionsMulti/${tid}`;
            let authtoken = localStorage.getItem("secret_authtoken");
            let data = {options:this.options};
            
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
                }).then( response => { return response.json()}).then ( (thing) => { if(thing.status!="failure" && thing.status!=null){alert("The addition operation was successful");localStorage.removeItem("optionAddID");router.push("/dashboard")} else{alert(thing.message);location.reload();}}).catch( e => console.log(e));
            
        }
    },
}

</script>