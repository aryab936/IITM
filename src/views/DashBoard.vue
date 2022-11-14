<template>
        <div class="container-xl">
                <button class="btn btn-outline-warning rounded " style="position:absolute;top:0;right:0;" @click="onLogout">Logout</button>
                <br />
                <br />
                <h2> Dashboard</h2>
                <button class="btn btn-outline-success rounded" @click="onAdd">Add New Tracker</button>
                <br />
                <br />
                <table>
                    <tr>
                        <th style="border:2px solid purple; border-collapse:collapse;">Tracker ID</th>
                        <th style="border:2px solid purple; border-collapse:collapse;">Tracker Type</th>
                        <th style="border:2px solid purple; border-collapse:collapse;">Tracker Name</th>
                        <th style="border:2px solid purple; border-collapse:collapse;"> Tracker Description</th>
                        <th style="border:2px solid purple; border-collapse:collapse;"> Tracker Last Reviewed Timestamp</th>
                        <th style="border:2px solid purple; border-collapse:collapse;"> Tracker Last Logged Timestamp</th> 
                        <th style="border:2px solid purple; border-collapse:collapse;">Actions</th>
                    </tr>
                    <tr v-for="(tracker, index) in trackers" :key="index">
                        <td style="border:2px solid purple; border-collapse:collapse;">{{ tracker.tracker_id }}</td>
                        <td style="border:2px solid purple; border-collapse:collapse;">{{ tracker.tracker_name}}</td>
                        <td style="border:2px solid purple; border-collapse:collapse;">{{ tracker.tracker_type }}</td>
                        <td style="border:2px solid purple; border-collapse:collapse;">{{ tracker.description }}</td>
                        <td style="border:2px solid purple; border-collapse:collapse;">{{ tracker.tracker_last_logged }}</td>
                        <td style="border:2px solid purple; border-collapse:collapse;">{{ tracker.tracker_last_logged }}</td>
                        <td style="border:2px solid purple; border-collapse:collapse;"><span><button type="button" @click="onUpdate(`${tracker.tracker_id}`,`${tracker.tracker_type}`)" class="btn btn-outline-primary rounded">Update</button></span>
                        <span><button @click="onDelete(`${tracker.tracker_id}`)" class="btn btn-outline-danger rounded">Delete</button></span><br /><br />
                        <span><button @click="onViewLogs(`${tracker.tracker_id}`,`${tracker.tracker_type}`)" class="btn btn-outline-info rounded">View Logs</button></span>
                        <br />
                        <br />
                        <span><button v-if="checkEquality(`${tracker.tracker_type}`)" @click="onAddOptions(`${tracker.tracker_id}`)" class="btn btn-outline-warning rounded">Add Options</button></span>
                        </td>
                    </tr>
                </table>
      <br />
      <br />
      <button @click="onDownload" class="btn btn-outline-dark rounded">Download Trackers</button>&nbsp;&nbsp;&nbsp;&nbsp;
      <label class="btn btn-outline-primary rounded"> Please upload a CSV file if you wish to import data
            <input class="btn btn-outline-primary rounded" type="file" accept=".csv" v-on:change="onUpload($event)" />
        </label>
        <button class="btn btn-outline-success rounded" @click="fileSubmission">Submit</button>
    </div>
</template>
                
<script>


import router from "../router" 
export default {
  name: "DashBoard",
  data() {
    return {
      trackers: [],
    };
  },
  methods: {
    checkEquality(value){
        if(value == "Multi Choice"){
            return true;
        }
        return false;
    },
    onAddOptions(value){
        localStorage.setItem("optionAddID",value);
        router.push("/addOptions");
    },
    getTrackers() {
      let path = "http://localhost:5000/dashboard";
      var authtoken = "";
      try {
        authtoken = localStorage.getItem("secret_authtoken");
      } catch (error) {
        console.log(error);
      }
      if (!authtoken){
        router.push("/failedLogin");
      }
      else{
        fetch(path,{
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
        }).then( response => {return response.json();}) .then( item => {this.trackers = item.data;}).catch( e => console.log(e));
    }
    },
    onUpdate(value1,value2){
      localStorage.setItem("updateTrackerID",value1);
      if (value2 != "Multi Choice"){
          router.push("/dashboardUpdate");
      }
      else{
        router.push("/dashboardMultiUpdate");
      }
    },
    onDelete(value) {
      let authtoken = localStorage.getItem("secret_authtoken");
      let path = `http://localhost:5000/dashboard/${value}`;
      fetch(path,{
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
        }).then( response => {return response.json();}) .then( () => {alert("The Delete Operation was successful");location.reload();}).catch( e => console.log(e));
      
    },
    onAdd() {
        router.push("/dashboardAdd");
    },
    onViewLogs(value1,value2){
        localStorage.setItem("viewTrackerID",value1);
        if (value2 == "Numerical"){
            router.push("/numericalLogs");
        }
        else if (value2 == "Boolean"){
            router.push("/booleanLogs");
        }
        else if (value2 == "Multi Choice"){
            router.push("/multiChoiceLogs");
        }
        else{
            router.push("/timeDurationLogs");
        }
    },
    onDownload(){
      let path = "http://localhost:5000/downloadDashboard";
      let authtoken = localStorage.getItem("secret_authtoken");
      fetch(path,{
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
        }).then( () => {alert("We have received your download request. We will notify you about its status via an email.");}).catch( e => console.log(e));
      
    },
    onUpload(){
            this.myFile = event.target.files[0];
    },
    fileSubmission(){
            let formData = new FormData();
            formData.append("UploadedFile",this.myFile);
            let uniqueresourcelocator = "http://127.0.0.1:5000/importJobTracker";
            let authtoken = localStorage.getItem("secret_authtoken");
            fetch(uniqueresourcelocator, {
            method: 'POST',
            mode: 'cors', 
            cache: 'no-cache', 
            credentials: 'omit',
            headers: {
              'secret-authtoken' : authtoken
              
            },
            redirect: 'follow', 
            referrerPolicy: 'no-referrer', 
            body: formData 
          }).then ( () => {alert("We have received your import request. We will notify you about the same via an email.");location.reload();}).catch( e => console.log(e));
    },
    onLogout(){
      localStorage.clear();
      router.push("/login");
    }


  },
  created() {
    this.getTrackers();
  },
};
</script>