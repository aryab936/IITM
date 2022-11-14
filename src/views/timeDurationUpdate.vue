<template>
        <div class="container">
                    <b-card header="Update Time Duration Tracker Log" header-bg-variant="danger" header-text-variant="white">
                            <b-form @submit="onSubmit">
                                <b-form-group description="Please enter the timestamp if you wish to modify" label="TIMESTAMP">
                                    <b-form-input v-model="timestamp"></b-form-input>
                                </b-form-group>
                                  <b-form-group description="Please enter the hours for the tracker if you wish to modify them." label="HOURS">
                                    <b-form-select v-model="hours" :options="options_hours"></b-form-select>
                                </b-form-group>
                                <b-form-group description="Please enter the minutes for the tracker if you wish to modify them." label="MINUTES">
                                    <b-form-select v-model="minutes" :options="options_minutes"></b-form-select>
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
    name:"timeDurationUpdate",
    data : () => ({
        note:"",
        timestamp:"",
        hours : null,
        options_hours:[],
        minutes :null,
        options_minutes:[]     
    }),
    methods:{
        populateOptions(){
            for (let a=0; a<24;a++){
                this.options_hours.push(a);
            }
            for (let b = 0; b<60;b++){
                this.options_minutes.push(b);
            }
        },
        onSubmit(x){
            x.preventDefault();
            let id = localStorage.getItem("viewTrackerID");
            let uniqueresourcelocator = `http://127.0.0.1:5000/timeDurationLogs/${id}`;
            let logsID = localStorage.getItem("updateLogID");
            let authtoken = localStorage.getItem("secret_authtoken");
            localStorage.removeItem("updateLogID");
            let data = {logID:logsID,note:this.note,hours:this.hours,minutes:this.minutes,timestamp:this.timestamp};
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
          }).then( response => { return response.json()}).then ( () => {alert("The update operation was successful");router.push("/timeDurationLogs");}).catch( e => console.log(e));
        }
    },
    created(){
        this.populateOptions();
    }
    
}


</script>