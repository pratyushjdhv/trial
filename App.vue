<script setup>
import { ref } from "vue";
import axios from "axios";

// --- STATE ---
// These variables hold our data. 'ref' makes them reactive so the UI updates when they change.
const username = ref("");
const message = ref("");
const errorMessage = ref("");
const registered = ref(false);

const register_user = async () => {
    message.value = "";
    errorMessage.value = "";

    try {
        const response = await axios.post('http://127.0.0.1:5000/register', {
            username: username.value
        })

        message.value = response.data.message;
        registered.value = true;
    }
    catch (error) {
        if (error.response) {
            errorMessage.value = error.response.data.error;
        }
        else {
            errorMessage.value = "server not available";
        }
    }

}
</script>

<template>
    <div class="container">
        <h1>🕵️ Black Box Event</h1>

        <div v-if="!registered" class="card">
            <h2>Join the Competition</h2>

            <div class="form-group">
                <input v-model="username" placeholder="Enter your Codename" @keyup.enter="register_user" />
                <button @click="register_user">Enter Event</button>
            </div>

            <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
        </div>

        <div v-else class="card success">
            <h2>{{ message }}</h2>
            <p>Waiting for the event to start...</p>
            <p class="status">🟢 Connected to Server</p>
        </div>

    </div>
</template>

<style scoped>
.container {
    max-width: 500px;
    margin: 50px auto;
    font-family: 'Courier New', Courier, monospace;
    text-align: center;
    color: #333;
}

.card {
    border: 2px solid #333;
    padding: 2rem;
    border-radius: 8px;
    background: #f9f9f9;
}

input {
    padding: 10px;
    font-size: 16px;
    margin-right: 10px;
    border: 1px solid #ccc;
}

button {
    padding: 10px 20px;
    background-color: #333;
    color: white;
    border: none;
    cursor: pointer;
    font-weight: bold;
}

button:hover {
    background-color: #555;
}

.error {
    color: red;
    font-weight: bold;
    margin-top: 10px;
}

.success {
    border-color: green;
    background-color: #e8f5e9;
}
</style>
