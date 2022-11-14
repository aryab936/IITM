<template>
        <div class="container"> 
                    <b-card header="Update Multi Choice Tracker Log" header-bg-variant="danger" header-text-variant="white">
                            <b-form @submit="onSubmit">
                                <b-form-group description="Please enter the timestamp if you wish to modify" label="TIMESTAMP">
                                    <b-form-input v-model="timestamp"></b-form-input>
                                </b-form-group>
                                  <b-form-group description="Please enter the value of the tracker." label="VALUE">
                                    <b-form-select v-model="value" :options="options"></b-form-select>
                                </b-form-group>
                                <b-form-group description="Please enter a note for the tracker" label="NOTE">
                                    <b-form-input v-model="note"></b-form-input>
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
    name:"multiChoiceUpdate",
    data : () => ({
            note:"",
            value:"",
            timestamp:"",
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
        onSubmit(x){
            x.preventDefault();
            let id = localStorage.getItem("viewTrackerID");
            let uniqueresourcelocator = `http://127.0.0.1:5000/multiChoiceLogs/${id}`
            let logsID = localStorage.getItem("updateLogID");
            let authtoken = localStorage.getItem("secret_authtoken");
            let data = {logID:logsID,note:this.note,timestamp:this.timestamp,value:this.value};
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
          }).then( response => { return response.json()}).then ( () => {alert("The update operation was successful");localStorage.removeItem("updateLogID");router.push("/multiChoiceLogs");}).catch( e => console.log(e));
        }
    },
    mounted(){
        this.populateOptions();
    }
    
}


</script>