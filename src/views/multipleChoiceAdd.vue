<template>
        <div class="container">
                    <b-card header="Add Multi Choice Tracker Log" header-bg-variant="warning" header-text-variant="black">
                            <b-form @submit="onSubmit">
                                <b-form-group description="Please enter the value of the tracker." label="VALUE">
                                    <b-form-select v-model="value" :options="options" required></b-form-select>
                                </b-form-group>
                                <b-form-group description="Please enter a note for the tracker" label="NOTE">
                                    <b-form-input v-model="note" required></b-form-input>
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
    name:"multiChoiceAdd",
    data : () => ({
        note:"",
        value:null,
        options:[]   
    }),
    methods:{
        populateOptions(){
            let id = localStorage.getItem("viewTrackerID");
            let uniqueresourcelocator = `http://127.0.0.1:5000/optionsMulti/${id}`;
            let authtoken = localStorage.getItem("secret_authtoken");
            fetch(uniqueresourcelocator, {
            method: 'GET', 
            mode: 'cors', 
            cache: 'no-cache', 
            credentials: 'omit', 
            headers: {
              'Content-Type': 'application/json',
              'secret-authtoken' : authtoken
              
            },
            redirect: 'follow', 
            referrerPolicy: 'no-referrer', 
          }).then( response => { return response.json()}).then ( (item) => {let data = item.data; for(let i =0;i<data.length;i++){this.options.push(data[i].option);}}).catch( e => console.log(e));
        },

        onSubmit(x) {
            x.preventDefault();
            let id = localStorage.getItem("viewTrackerID");
            let uniqueresourcelocator = `http://127.0.0.1:5000/multiChoiceLogs/${id}`;
            let authtoken = localStorage.getItem("secret_authtoken");
            let data = {note:this.note,value:this.value};
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
          }).then( response => { return response.json()}).then ( (thing) => { if(thing.status!="failure"){alert("The addition operation was successful");router.push("/multiChoiceLogs")} else{alert(thing.message);location.reload();}}).catch( e => console.log(e));
        }
    },
    mounted(){
        this.populateOptions();
    }
}

</script>
