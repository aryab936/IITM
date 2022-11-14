<template>
    <div class="container">
        <h1> Please try logging in again. Thanks </h1>
        <b-button variant="danger" @click="goBack"> Go Back to Login </b-button>
    </div>
</template>

<script>
import router from "../router"
export default {
    name:"FailedLogin",
    methods :{
        goBack(){
            router.push("/login");
        }
    }
}
</script>