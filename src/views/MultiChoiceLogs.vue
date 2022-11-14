<template>
        <div class="container-xl">
                <button class="btn btn-outline-warning rounded" style="position:absolute;top:0;right:0;" @click="onLogout">Logout</button>
                <button class="btn btn-outline-danger rounded" style="position:absolute;top:0;left:0;" @click="onDashboard">Back to Dashboard</button>
                <br />
                <br />
                <h2> Logs for the Multiple Choice Tracker </h2>
                <br />
                <button class="btn btn-outline-success rounded" @click="onAdd">Add New Log</button>
                <table class="table">
                <br />
                <br />
                    <tr>
                        <th style="border:2px solid darkorange; border-collapse:collapse;">Tracker Value</th>
                        <th style="border:2px solid darkorange; border-collapse:collapse;">Tracker Timestamp</th>
                        <th style="border:2px solid darkorange; border-collapse:collapse;">Tracker Notes</th>
                        <th style="border:2px solid darkorange; border-collapse:collapse;">Actions</th>
                    </tr>
                    <tr v-for="(log, index) in logs" :key="index">
                        <td style="border:2px solid darkorange; border-collapse:collapse;">{{ log.value }}</td>
                        <td style="border:2px solid darkorange; border-collapse:collapse;">{{ log.timestamp }}</td>
                        <td style="border:2px solid darkorange; border-collapse:collapse;">{{ log.note }}</td>
                        <td style="border:2px solid darkorange; border-collapse:collapse;"><div><button @click="onUpdate(`${log.logID}`)" class="btn btn-outline-primary rounded">Update</button></div><br />
                        <div><button @click="onDelete(`${log.logID}`)" class="btn btn-outline-danger rounded">Delete</button></div></td>
                    </tr>
                </table>    
      <br />
      <br />
      <button @click="onDownload" class="btn btn-outline-dark rounded">Download Logs</button>
      <span>&nbsp;&nbsp;&nbsp;&nbsp;</span> <button   class="btn btn-outline-info rounded" @click="makeChart"> View a Chart Based Summary </button>
      <div class="container-sm">
      <canvas id="myChart"></canvas>
      </div>
      <label class="btn btn-outline-primary rounded"> Please upload a CSV file if you wish to import data
            <input class="btn btn-outline-primary rounded" type="file" accept=".csv" v-on:change="onUpload($event)" />
        </label>
        <button class="btn btn-outline-success rounded" @click="fileSubmission">Submit</button>
    </div>
</template>
                
<script>


import {Chart} from "../main.js";
import router from "../router";
export default {
  name: "MultipleChoiceLogs",
  data() {
    return {
      logs: [],
      labels:[]
    };
  },
  methods: {
    getLogs() {
      let id = localStorage.getItem("viewTrackerID");
      const path = `http://localhost:5000/multiChoiceLogs/${id}`;
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
        }).then( response => {return response.json();}) .then( item => {this.logs = item.data;}).catch( e => console.log(e));
    }
    },
    onUpdate(value){
      localStorage.setItem("updateLogID",value);
      router.push("/multiChoiceUpdate");
    },
    onDelete(value) {
      let trackerID = this.logs[0].tracker_id;
      let authtoken = localStorage.getItem("secret_authtoken");
      let path = `http://localhost:5000/multiChoiceLogs/${trackerID}/${value}`;
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
        router.push("/multiChoiceAdd");
    },
    onDownload(){
      let trackerID = this.logs[0].tracker_id;
      let path = `http://localhost:5000/downloadMultiChoice/${trackerID}`;
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
        }).then( () => {alert("Your request has been submitted. You will be notified via email.");}).catch( e => console.log(e));
      
    },
    makeChart(){
        let data_1={};
        //console.log(this.labels);
        for (let item of this.labels){
          data_1[item] =0;
        }
        //console.log(data_1);
        for (let item of this.logs){
          for (let thing of this.labels){
            if (item.value == thing){
              data_1[thing]+=1;
              break;
            }
          }
        }
        //console.log(data_1)
        const data = {
          labels: this.labels,
          datasets: [{
            label: 'Multiple Choice Tracker Log Values',
            backgroundColor: 'rgb(255,128,170)',
            borderColor: 'rgb(0, 100, 100)',
            data: data_1,
          }]};
        
        const config = {type: 'bar',data: data,options: {responsive: true}};
        this.myChart = new Chart(document.getElementById('myChart'),config);

    },
    populateLabels(){
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
        }).then( response => { return response.json()}).then ( (item) => {let data = item.data; for(let i =0;i<data.length;i++){this.labels.push(data[i].option);}}).catch( e => console.log(e));
    },
    onUpload(){
            this.myFile = event.target.files[0];
    },
    fileSubmission(){
            let trackerID = this.logs[0].tracker_id
            let formData = new FormData();
            formData.append("UploadedFile",this.myFile);
            let uniqueresourcelocator = `http://127.0.0.1:5000/importJobMultiChoice/${trackerID}`;
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
    this.populateLabels();
  },
};
</script>

