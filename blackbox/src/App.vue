<script setup>
import { ref } from 'vue'
import { onMounted } from 'vue'
import axios from 'axios'
import Login from './components/Login.vue'
import Dashboard from './components/Dashboard.vue'
import Challenge from './components/Challenge.vue'
import Admin from './components/Admin.vue'
import api from '@/api'

// Global State
const username = ref('')
const userId = ref(null)
const view = ref('login') // 'login', 'dashboard', 'challenge', 'admin'
const questions = ref([])
const selectedQ = ref(null)

// --- ACTIONS ---
const handleJoin = async (credentials) => {
    const name = credentials.username
    const password = credentials.password

    if (name.toLowerCase() === 'admin') {
        if (password === 'admin123') {
            view.value = 'admin'
            username.value = 'Admin'
            userId.value = 'admin'
            return
        } else {
            alert("Access Denied")
            return
        }
    }

    try {
        const res = await api.post('/register', { username: name })
        username.value = name
        userId.value = res.data.id
        
        localStorage.setItem('user_data', JSON.stringify({
            id: userId.value,
            username: username.value
        }))

        loadDashboard()
    } catch (err) {
        alert("Login Error: " + err.response?.data?.error)
    }
}

const loadDashboard = async () => {
    try {
        const res = await api.get('/questions')
        
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
        loadDashboard()
    }
})

const handleLogout = () => {
    localStorage.removeItem('user_data')
    userId.value = null
    username.value = ''
    view.value = 'login'
    questions.value = []
    selectedQ.value = null
}
</script>

<template>
    <div class="app-container">
        <header>
            <h1>🕵️ BLACK BOX OS</h1>
            <div v-if="userId" class="user-info">
                Agent: {{ username }}
                <button @click="handleLogout" class="logout-btn">Logout</button>
            </div>
        </header>

        <Login v-if="view === 'login'" @join="handleJoin" />

        <Dashboard v-else-if="view === 'dashboard'" :questions="questions" @select="handleSelectQuestion" />

        <Challenge v-else-if="view === 'challenge'" :key="selectedQ.id" :question="selectedQ" :userId="userId"
            @back="loadDashboard" />

        <Admin v-else-if="view === 'admin'" />

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
    align-items: center;
}

.logout-btn {
    background: #333;
    color: #fff;
    border: 1px solid #555;
    padding: 5px 10px;
    margin-left: 10px;
    cursor: pointer;
    font-family: inherit;
}

.logout-btn:hover {
    background: #555;
    border-color: #fff;
}
</style>