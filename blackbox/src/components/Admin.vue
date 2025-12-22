<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const leaderboard = ref([])
const top3 = ref([])
const eventEnded = ref(false)

const endEvent = async () => {
    try {
        const res = await api.post('/admin/end_event')
        leaderboard.value = res.data.leaderboard
        top3.value = res.data.top3
        eventEnded.value = true
    } catch (err) {
        alert("Error ending event: " + (err.response?.data?.error || err.message))
    }
}
</script>

<template>
    <div class="admin-panel">
        <h2>Admin Control</h2>
        
        <div v-if="!eventEnded">
            <button @click="endEvent" class="danger-btn">END EVENT</button>
        </div>

        <div v-else class="results">
            <h3>🏆 Event Results</h3>
            
            <div class="top-3">
                <h4>Overall Top 3</h4>
                <div v-for="(user, index) in top3" :key="user.id" class="winner-card">
                    <span class="rank">#{{ index + 1 }}</span>
                    <span class="name">{{ user.username }}</span>
                    <span class="score">{{ user.total_score }} pts</span>
                </div>
            </div>

            <div class="leaderboard">
                <h4>Full Leaderboard</h4>
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Agent</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(user, index) in leaderboard" :key="user.id">
                            <td>{{ index + 1 }}</td>
                            <td>{{ user.username }}</td>
                            <td>{{ user.total_score }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<style scoped>
.admin-panel {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    color: #0f0;
}

.danger-btn {
    background: #ff0000;
    color: white;
    padding: 15px 30px;
    font-size: 1.2em;
    border: none;
    cursor: pointer;
    font-weight: bold;
}

.danger-btn:hover {
    background: #cc0000;
}

.results {
    margin-top: 30px;
}

.top-3 {
    display: flex;
    gap: 20px;
    justify-content: center;
    margin-bottom: 40px;
}

.winner-card {
    background: #222;
    border: 2px solid #ffd700;
    padding: 20px;
    text-align: center;
    min-width: 150px;
}

.rank {
    display: block;
    font-size: 2em;
    font-weight: bold;
    color: #ffd700;
}

.name {
    display: block;
    font-size: 1.2em;
    margin: 10px 0;
}

.score {
    color: #aaa;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

th, td {
    border: 1px solid #333;
    padding: 10px;
    text-align: left;
}

th {
    background: #222;
}
</style>
