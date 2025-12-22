<script setup>
import { ref, watch } from 'vue'

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const emit = defineEmits(['join'])

watch(username, (newVal) => {
    if (newVal.trim().toLowerCase() === 'admin') {
        showPassword.value = true
    } else {
        showPassword.value = false
        password.value = ''
    }
})

const handleLogin = () => {
    if (username.value.trim()) {
        emit('join', { username: username.value, password: password.value }) 
    }
}
</script>

<template>
    <div class="center-box">
        <h2>Identify Yourself</h2>
        <input v-model="username" placeholder="Enter Codename" @keyup.enter="handleLogin" />
        <div v-if="showPassword">
            <br>
            <input  v-model="password" type="password" placeholder="Admin Password" @keyup.enter="handleLogin" />
            <br><br>
        </div>
        
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