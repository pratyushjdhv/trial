<script setup>
import { ref } from 'vue'

const username = ref('')
const emit = defineEmits(['join']) // Define custom event

const handleLogin = () => {
    if (username.value.trim()) {
        emit('join', username.value) // Send data to parent
    }
}
</script>

<template>
    <div class="center-box">
        <h2>Identify Yourself</h2>
        <input v-model="username" placeholder="Enter Codename" @keyup.enter="handleLogin" />
        <button @click="handleLogin">Connect</button>
    </div>
</template>

<style scoped>
.center-box {
    max-width: 400px;
    margin: 100px auto;
    text-align: center;
}

input {
    background: #000;
    color: #0f0;
    border: 1px solid #333;
    padding: 10px;
    font-family: inherit;
    margin-right: 10px;
}

button {
    cursor: pointer;
    border: none;
    font-weight: bold;
    padding: 10px 20px;
    background: #333;
    color: white;
}

button:hover {
    background: #555;
}
</style>