<script setup>
import { ref } from 'vue'
import { onMounted } from 'vue'
import axios from 'axios'
import Login from './components/Login.vue'
import Dashboard from './components/Dashboard.vue'
import Challenge from './components/Challenge.vue'

// Global State
const username = ref('')
const userId = ref(null)
const view = ref('login') // 'login', 'dashboard', 'challenge'
const questions = ref([])
const selectedQ = ref(null)

// --- ACTIONS ---
const handleJoin = async (name) => {
    try {
        const res = await axios.post('http://127.0.0.1:5000/register', { username: name })
        username.value = name
        userId.value = res.data.id
        loadDashboard()
    } catch (err) {
        alert("Login Error: " + err.response?.data?.error)
    }
}

const loadDashboard = async () => {
    try {
        const res = await axios.get('http://127.0.0.1:5000/questions')
        questions.value = res.data
        view.value = 'dashboard'
    } catch (err) {
        console.error("Failed to load questions")
    }
}

const handleSelectQuestion = (q) => {
    selectedQ.value = q
    view.value = 'challenge'
}

onMounted(() => {
    // Could check for existing session here
    const savedUser = localStorage.getItem('user_data')
    if (savedUser) {
        const data = JSON.parse(savedUser)
        userId.value = data.id
        username.value = data.username
        loggedIn.value = true
        loadDashboard()
    }
})

// 2. Save session after login
const registerUser = async () => {
    try {
        const res = await axios.post('http://127.0.0.1:5000/register', { username: username.value }) // Remember to change IP!

        userId.value = res.data.id
        username.value = res.data.username // Ensure backend sends this
        loggedIn.value = true

        // SAVE TO BROWSER MEMORY
        localStorage.setItem('user_data', JSON.stringify({
            id: userId.value,
            username: username.value
        }))

        loadDashboard()
    } catch (err) {
        alert(err.response?.data?.error || "Server Error")
    }
}

// 3. Optional: Add a Logout function
const logout = () => {
    localStorage.removeItem('user_data')
    location.reload()
}
</script>

<template>
    <div class="app-container">
        <header>
            <h1>🕵️ BLACK BOX OS</h1>
            <div v-if="userId" class="user-info">Agent: {{ username }}</div>
        </header>

        <Login v-if="view === 'login'" @join="handleJoin" />

        <Dashboard v-else-if="view === 'dashboard'" :questions="questions" @select="handleSelectQuestion" />

        <Challenge v-else-if="view === 'challenge'" :key="selectedQ.id" :question="selectedQ" :userId="userId"
            @back="loadDashboard" />

    </div>
</template>

<style>
/* Global Styles */
.app-container {
    font-family: 'Courier New', monospace;
    background: #1a1a1a;
    color: #0f0;
    min-height: 100vh;
    padding: 20px;
}

header {
    display: flex;
    justify-content: space-between;
    border-bottom: 2px solid #333;
    padding-bottom: 10px;
    margin-bottom: 30px;
}
</style>