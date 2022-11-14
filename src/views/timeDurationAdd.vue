<template>
        <div class="container">
                    <b-card header="Add Time Duration Tracker Log" header-bg-variant="warning" header-text-variant="black">
                            <b-form @submit="onSubmit">
                                <b-form-group description="Please enter the hours for the tracker." label="HOURS">
                                    <b-form-select v-model="hours" :options="options_hours" required></b-form-select>
                                </b-form-group>
                                <b-form-group description="Please enter the minutes for the tracker." label="MINUTES">
                                    <b-form-select v-model="minutes" :options="options_minutes" required></b-form-select>
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
    name:"timeDurationAdd",
    data : () => ({
        note:"",
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

        onSubmit(x) {
            x.preventDefault();
            let id = localStorage.getItem("viewTrackerID");
            let uniqueresourcelocator = `http://127.0.0.1:5000/timeDurationLogs/${id}`;
            if (this.hours == null || this.minutes == null){
                alert("Please fill the fields of hours/minutes depending on what has been skipped.");
                location.reload();
            }
            let authtoken = localStorage.getItem("secret_authtoken");
            let data = {note:this.note,hours:this.hours,minutes:this.minutes};
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
          }).then( response => { return response.json()}).then ( () => {alert("The addition operation was successful");router.push("/timeDurationLogs");}).catch( e => console.log(e));
        }
    },
    created(){
        this.populateOptions();
    }
}

</script>
