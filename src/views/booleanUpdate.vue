<template>
        <div class="container">
                    <b-card header="Update Boolean Tracker Log" header-bg-variant="danger" header-text-variant="white">
                            <b-form @submit="onSubmit">
                                <b-form-group description="Please enter the timestamp if you wish to modify" label="TIMESTAMP">
                                    <b-form-input v-model="timestamp"></b-form-input>
                                </b-form-group>
                                 <b-form-group description="Please enter the value for the tracker if you wish to change." label="VALUE">
                                    <b-form-select v-model="selected" :options="options"></b-form-select>
                                </b-form-group>
                                <b-form-group description="Please enter the new note if you wish to change." label="NOTE">
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
    name:"booleanUpdate",
    data: () =>({
        timestamp:"",
        note:"",
        selected : null,
        options:[
            {value : true, text:"True"},
            {value : false, text: "False" }
        ]
    }),
    methods: {
        onSubmit(x){
            x.preventDefault();
            let id = localStorage.getItem("viewTrackerID");
            let uniqueresourcelocator = `http://127.0.0.1:5000/booleanLogs/${id}`
            let logsID = localStorage.getItem("updateLogID");
            let authtoken = localStorage.getItem("secret_authtoken");
            localStorage.removeItem("updateLogID");
            let data = {logID:logsID,timestamp:this.timestamp,note:this.note,value:this.selected};
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
          }).then( response => { return response.json()}).then ( () => {alert("The update operation was successful");router.push("/booleanLogs");}).catch( e => console.log(e));
        }
    }
    
}


</script>