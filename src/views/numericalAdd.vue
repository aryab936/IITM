<template>
        <div class="container">
                    <b-card header="Add Numerical Tracker Log" header-bg-variant="warning" header-text-variant="black">
                            <b-form @submit="onSubmit">
                                <b-form-group description="Please enter the value for the tracker." label="VALUE">
                                    <b-form-input v-model="value" required type="number"></b-form-input>
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
    name:"numericalAdd",
    data : () => ({
            value:"",
            note:"",
    }),
    methods:{
        onSubmit(x) {
            x.preventDefault();
            let id = localStorage.getItem("viewTrackerID");
            let uniqueresourcelocator = `http://127.0.0.1:5000/numericLogs/${id}`;
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
          }).then( response => { return response.json()}).then ( (data) => {if(data.status !="failed"){alert("The addition operation was successful");router.push("/numericalLogs");localStorage.removeItem("updateLogID");} else{alert("Please enter a number only");location.reload();}}).catch( e => console.log(e));
        }
    }
}

</script>


