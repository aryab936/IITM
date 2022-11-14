<template>
        <div class="container-xl">
                <button class="btn btn-outline-warning rounded" style="position:absolute;top:0;right:0;" @click="onLogout">Logout</button>
                <button class="btn btn-outline-danger rounded" style="position:absolute;top:0;left:0;" @click="onDashboard">Back to Dashboard</button>
                <br />
                <br />
                <h2>Logs for the Time Duration Tracker</h2>
                <br />
                <button class="btn btn-outline-success rounded" @click="onAdd">Add New Log</button>
                <br />
                <br />
                <table class="table">
                    <tr>
                        <th style="border:2px solid brown; border-collapse:collapse;">Tracker Hours</th>
                        <th style="border:2px solid brown; border-collapse:collapse;">Tracker Minutes</th>
                        <th style="border:2px solid brown; border-collapse:collapse;">Tracker Timestamp</th>
                        <th style="border:2px solid brown; border-collapse:collapse;">Tracker Notes</th>
                        <th style="border:2px solid brown; border-collapse:collapse;">Actions</th>
                    </tr>
                    <tr v-for="(log, index) in logs" :key="index">
                        <td style="border:2px solid brown; border-collapse:collapse;">{{ log.hours }}</td>
                        <td style="border:2px solid brown; border-collapse:collapse;">{{ log.minutes }}</td>
                        <td style="border:2px solid brown; border-collapse:collapse;">{{ log.timestamp }}</td>
                        <td style="border:2px solid brown; border-collapse:collapse;">{{ log.note }}</td>
                        <td style="border:2px solid brown; border-collapse:collapse;"><div><button @click="onUpdate(`${log.logID}`)" class="btn btn-outline-primary rounded">Update</button></div><br />
                        <div><button @click="onDelete(`${log.logID}`)" class="btn btn-outline-danger rounded">Delete</button></div></td>
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
import router from "../router";
import {Chart} from "../main.js"; 
export default {
  name: "TimeDurationLogs",
  data() {
    return {
      logs: [],
      myChart:null
    };
  },
  methods: {
    getLogs() {
      let id = localStorage.getItem("viewTrackerID");
      const path = `http://localhost:5000/timeDurationLogs/${id}`;
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
          method: 'GET', // *GET, POST, PUT, DELETE, etc.
          mode: 'cors', // no-cors, *cors, same-origin
          cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
          credentials: 'omit', // include, *same-origin, omit
          headers: {
      'Content-Type': 'application/json',
      'secret-authtoken' : authtoken
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
        }).then( response => {return response.json();}) .then( item => {this.logs = item.data;}).catch( e => console.log(e));
    }
    },
    onUpdate(value){
      localStorage.setItem("updateLogID",value);
      router.push("/timeDurationUpdate");
    },
    onDelete(value) {
      let trackerID = this.logs[0].tracker_id;
      let authtoken = localStorage.getItem("secret_authtoken");
      let path = `http://localhost:5000/timeDurationLogs/${trackerID}/${value}`;
      fetch(path,{
          method: 'DELETE', // *GET, POST, PUT, DELETE, etc.
          mode: 'cors', // no-cors, *cors, same-origin
          cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
          credentials: 'omit', // include, *same-origin, omit
          headers: {
      'Content-Type': 'application/json',
      'secret-authtoken' : authtoken
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
        }).then( response => {return response.json();}) .then( () => {alert("The Delete Operation was successful");location.reload();}).catch( e => console.log(e));
      
    },
    onAdd() {
        router.push("/timeDurationAdd");
    },
    onDownload(){
      let trackerID = this.logs[0].tracker_id;
      let path = `http://localhost:5000/downloadTimeDuration/${trackerID}`;
      let authtoken = localStorage.getItem("secret_authtoken");
      fetch(path,{
          method: 'GET', // *GET, POST, PUT, DELETE, etc.
          mode: 'cors', // no-cors, *cors, same-origin
          cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
          credentials: 'omit', // include, *same-origin, omit
          headers: {
      'Content-Type': 'application/json',
      'secret-authtoken' : authtoken
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
        }).then( () => {alert("We have received your download request. You will be notified via an email on the status of the same..");}).catch( e => console.log(e));
      
    },
    makeChart(){
        const labels = [];
        const data_1 = [];
        for (let item of this.logs){
          labels.push(item.timestamp);
          data_1.push((item.hours*60+item.minutes));
        }
        const data = {
          labels: labels,
          datasets: [{
            label: 'Numerical Tracker Log Values',
            backgroundColor: 'rgb(255,0,0)',
            borderColor: 'rgb(255, 179, 26)',
            data: data_1,
          }]};
        
        const config = {type: 'line',data: data,options: {responsive: true}};
        this.myChart = new Chart(document.getElementById('myChart'),config);

    },
    onUpload(){
            this.file = event.target.files[0];
    },
    fileSubmission(){
            let trackerID = this.logs[0].tracker_id
            let formData = new FormData();
            formData.append("file",this.file);
            let uniqueresourcelocator = `http://127.0.0.1:5000/importTimeDuration/${trackerID}`;
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
          }).then ( () => {alert('We have received your import request. We will notify you about the same via an email.');location.reload()}).catch( e => console.log(e));
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