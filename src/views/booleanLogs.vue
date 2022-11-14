<template>
        <div class="container-xl">
                <button class="btn btn-outline-warning rounded" style="position:absolute;top:0;right:0;" @click="onLogout">Logout</button>
                <button class="btn btn-outline-danger rounded" style="position:absolute;top:0;left:0;" @click="onDashboard">Back to Dashboard</button>
                <br />
                <br />
                <h2> Logs for the Boolean Tracker </h2>
                <br />
                <button class="btn btn-outline-success rounded" @click="onAdd">Add New Log</button>
                <br />
                <br />
                <table class="table">
                    <tr>
                        <th style="border:2px solid black; border-collapse:collapse;">Tracker Value</th>
                        <th style="border:2px solid black; border-collapse:collapse;">Tracker Timestamp</th>
                        <th style="border:2px solid black; border-collapse:collapse;">Tracker Notes</th>
                        <th style="border:2px solid black; border-collapse:collapse;">Actions</th>
                    </tr>
                    <tr v-for="(log, index) in logs" :key="index">
                        <td style="border:2px solid black; border-collapse:collapse;">{{ log.value }}</td>
                        <td style="border:2px solid black; border-collapse:collapse;">{{ log.timestamp }}</td>
                        <td style="border:2px solid black; border-collapse:collapse;">{{ log.note }}</td>
                        <td style="border:2px solid black; border-collapse:collapse;"><span><button @click="onUpdate(`${log.logID}`)" class="btn btn-outline-primary rounded">Update</button>&nbsp;&nbsp;&nbsp;&nbsp;
                        <button @click="onDelete(`${log.logID}`)" class="btn btn-outline-danger rounded">Delete</button></span></td>
                    </tr>
                </table>
      <br />
      <br />
      <button @click="onDownload" class="btn btn-outline-dark rounded">Download Logs</button>
      <span>&nbsp;&nbsp;&nbsp;&nbsp;</span> <button class="btn btn-outline-info rounded" @click="makeChart"> View a Chart Based Summary </button>
      <div class="container-lg">
      <canvas id="myChart"></canvas>
      </div>
      <label class="btn btn-outline-primary rounded"> Please upload a CSV file if you wish to import data
            <input class="btn btn-outline-primary rounded" type="file" accept=".csv" v-on:change="onUpload($event)" />
        </label>
        <button class="btn btn-outline-success rounded" @click="fileSubmission">Submit</button>
    </div>
</template>                
<script>


import router from "../router" 
import {Chart} from "../main.js";
export default {
  name: "BooleanLogs",
  data() {
    return {
      logs: [],
      myChart:null
    };
  },
  methods: {
    getLogs() {
      let id = localStorage.getItem("viewTrackerID");
      const path = `http://localhost:5000/booleanLogs/${id}`;
      var authtoken = false;
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
        }).then( response => {return response.json();}) .then( item => {this.logs = item.data;}).catch( e => console.log(e));
    }
    },
    onUpdate(value){
      localStorage.setItem("updateLogID",value);
      router.push("/booleanUpdate");
    },
    onDelete(value) {
      let trackerID = this.logs[0].tracker_id;
      let authtoken = localStorage.getItem("secret_authtoken");
      let path = `http://localhost:5000/booleanLogs/${trackerID}/${value}`;
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
        router.push("/booleanAdd");
    },
    onDownload(){
      let trackerID = this.logs[0].tracker_id;
      let path = `http://localhost:5000/downloadBoolean/${trackerID}`;
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
        }).then( ()=> {alert("We have received your download request. We will notify you about its status via an email.");}).catch( e => console.log(e));
      
    },
    makeChart(){
        const labels = ['True','False'];
        let true_counts = 0;
        let false_counts = 0;
        for (let item of this.logs){
          if (item.value == true){
            true_counts+=1;
          }
          else{
            false_counts+=1;
          }
        }
        const data = {
          labels: labels,
          datasets: [{
            label: 'Boolean Tracker Log Values',
            backgroundColor: 'rgb(0, 100, 100)',
            borderColor: 'rgb(0, 100, 100)',
            data: [true_counts,false_counts],
          }]};
        
        const config = {type: 'bar',data: data,options: {responsive: true}};
        this.myChart = new Chart(document.getElementById('myChart'),config);

    },
     onUpload(){
            this.myFile = event.target.files[0];
     },
     fileSubmission(){
            let trackerID = this.logs[0].tracker_id
            let formData = new FormData();
            formData.append("UploadedFile",this.myFile);
            let uniqueresourcelocator = `http://127.0.0.1:5000/importJobBoolean/${trackerID}`;
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
          }).then ( () => {alert("We have received your import request. We will notify you about the same via an email.");location.reload()}).catch( e => console.log(e));
      },
    onLogout(){
      localStorage.clear();
      router.push("/login");
    },
    onDashboard(){
      router.push("/dashboard");
    }
  },
  created() {
    this.getLogs();
  },
};
</script>