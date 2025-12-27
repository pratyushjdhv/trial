<script setup>
import { ref } from 'vue'
import { onMounted } from 'vue'
import Login from './components/Login.vue'
import Dashboard from './components/Dashboard.vue'
import Challenge from './components/Challenge.vue'
import Admin from './components/Admin.vue'
import GameOverModal from './components/GameOverModal.vue'
import api from '@/api'

// Global State
const username = ref('')
const userId = ref(null)
const view = ref('login') // 'login', 'dashboard', 'challenge', 'admin'
const questions = ref([])
const selectedQ = ref(null)
const showGameOver = ref(false)
const topWinners = ref([])
const gameOverDismissed = ref(false)

// Polling for event status
const checkEventStatus = async () => {
    if (view.value === 'admin' || view.value === 'login') return

    try {
        const res = await api.get(`/event/status?user_id=${userId.value}`)
        
        if (res.data.valid_user === false) {
            handleLogout()
            return
        }

        if (res.data.ended) {
            if (!gameOverDismissed.value) {
                topWinners.value = res.data.top5
                showGameOver.value = true
            }
        } else {
            showGameOver.value = false
            gameOverDismissed.value = false
        }
    } catch (err) {
        console.error("Polling error", err)
    }
}

onMounted(() => {
    setInterval(checkEventStatus, 5000)

    const savedUser = localStorage.getItem('user_data')
    if (savedUser) {
        const data = JSON.parse(savedUser)
        userId.value = data.id
        username.value = data.username
        loadDashboard()
    }
})
const handleJoin = async (credentials) => {
    const name = (credentials && typeof credentials === 'object') ? credentials.username : credentials
    const password = (credentials && typeof credentials === 'object') ? credentials.password : ''

    if (!name) return

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

// onMounted is already defined above with polling logic

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
            <h1>
                <svg version="1.1" id="_x32_" xmlns="http://www.w3.org/2000/svg"
                    xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 512 512" xml:space="preserve"
                    class="header-logo-svg">
                    <g>
                        <path class="st0"
                            d="M378.625,209.465c-6.531-38.344-13.672-80-15.844-91.844c-5.313-28.906-43.375-45.063-71.656-24.234 c-14.828,10.938-28.094,11.719-35.125,11.719s-14.828,1.563-35.125-11.719c-29.391-19.219-66.344-4.672-71.656,24.234 c-2.172,11.844-9.313,53.5-15.844,91.844C53.906,219.418,0,238.778,0,261.012c0,32.438,114.625,58.719,256,58.719 c141.391,0,256-26.281,256-58.719C512,238.778,458.094,219.418,378.625,209.465z"
                            fill="#f6f5f4"></path>
                        <path class="st0"
                            d="M109.125,330.45l7.547,86.515c39.563,6.719,79.734,10.219,119.703,11.078L256,401.278l19.625,26.765 c39.969-0.859,80.141-4.359,119.703-11.078l7.547-86.515c-48.375,9.359-97.906,13.5-146.875,13.5 C207.016,343.95,157.516,339.809,109.125,330.45z M186.688,401.997c-33.469-1.578-35.563-41.766-35.563-41.766l75.125,14.672 C226.25,374.903,220.156,403.59,186.688,401.997z M360.875,360.231c0,0-2.094,40.188-35.563,41.766 c-33.469,1.594-39.563-27.094-39.563-27.094L360.875,360.231z"
                            fill="#f6f5f4"></path>
                    </g>
                </svg>
                CRACK THE <span class="highlight">ENIGMA</span>
            </h1>

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

        <GameOverModal v-if="showGameOver && view !== 'login' && view !== 'admin'" :winners="topWinners"
            @close="showGameOver = false; gameOverDismissed = true" />

    </div>
</template>

<style>
/* Global Styles */
body {
    margin: 0;
    padding: 0;
    background: #000;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}

.app-container {
    font-family: 'Courier New', monospace;
    /* background: #1a1a1a;  Removed to show canvas */
    color: #0f0;
    min-height: 100vh;
    padding: 20px;
    position: relative; /* Ensure z-index context works if needed */
    z-index: 1; /* Ensure content is above background */
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

.header-logo-svg {
    height: 1.5em;
    width: 1.5em;
    vertical-align: middle;
    margin-right: 15px;
    fill: #f6f5f4;
    /* Ensure fill color works */
}

.highlight {
    color: #0f0;
    /* Bright Hacker Green */
    text-shadow: 0 0 5px #0f0;
    /* Glowing effect */
    font-weight: bold;
}
</style>