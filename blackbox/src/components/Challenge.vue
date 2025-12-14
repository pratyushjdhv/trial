<script setup>
import { ref } from 'vue'
import axios from 'axios'

// We need the User ID and Question Data to make API calls
const props = defineProps(['question', 'userId'])
const emit = defineEmits(['back'])

// Local State (Specific to this game session)
const userCode = ref('import sys\n\n# Read input from arguments\nn = int(input())\n\n# Write function logic here:\nprint(n)')
const probeInput = ref('')
const probeHistory = ref([])
const probesLeft = ref(props.question.max_probes) // Start with max probes
const submitLogs = ref([])
const submitStatus = ref('')

// --- LOGIC MOVED HERE ---
const sendProbe = async () => {
    if (!probeInput.value) return
    try {
        const res = await axios.post('http://127.0.0.1:5000/probe', {
            user_id: props.userId,
            question_id: props.question.id,
            input: probeInput.value
        })
        probeHistory.value.unshift({ in: res.data.input, out: res.data.output })
        probesLeft.value = res.data.probes_left
        probeInput.value = ''
    } catch (err) {
        alert(err.response?.data?.error || "Probe Failed")
    }
}

const submitCode = async () => {
    submitStatus.value = 'loading'
    submitLogs.value = []
    try {
        const res = await axios.post('http://127.0.0.1:5000/submit', {
            user_id: props.userId,
            question_id: props.question.id,
            code: userCode.value
        })
        submitLogs.value = res.data.details
        if (res.data.solved) {
            submitStatus.value = 'success'
            alert(`🎉 CORRECT! You earned ${res.data.score_added} points!`)
        } else {
            submitStatus.value = 'fail'
        }
    } catch (err) {
        submitStatus.value = 'error'
        alert("Error: " + (err.response?.data?.error || err.message))
    }
}
</script>

<template>
    <div class="challenge-ui">
        <button class="back-btn" @click="$emit('back')">← Back to Targets</button>

        <div class="panels">
            <div class="panel left">
                <div class="panel-header">
                    <h3>📝 Mission: Level {{ question.id }}</h3>
                    <span class="desc">{{ question.description }}</span>
                </div>
                <textarea v-model="userCode" class="code-editor" spellcheck="false"></textarea>
                <button @click="submitCode" class="submit-btn">
                    {{ submitStatus === 'loading' ? 'Compiling...' : '🚀 Submit Code' }}
                </button>

                <div v-if="submitLogs.length" class="logs-box">
                    <h4>Judge Results:</h4>
                    <div v-for="(log, i) in submitLogs" :key="i" :class="['log-item', log.status]">
                        <span v-if="log.status === 'Pass'">✅ Input {{ log.input }}: Passed</span>
                        <span v-else>❌ Input {{ log.input }}: Expected Hidden, Got {{ log.got }}</span>
                    </div>
                </div>
            </div>

            <div class="panel right">
                <h3>🧪 Black Box Probe</h3>
                <div class="probe-box">
                    <input type="number" v-model="probeInput" placeholder="Enter number..." />
                    <button @click="sendProbe" :disabled="probesLeft <= 0">TEST</button>
                </div>
                <p class="status">Probes Remaining: {{ probesLeft }}</p>
                <div class="history">
                    <div v-for="(h, i) in probeHistory" :key="i" class="history-item">
                        <span class="mono">In: {{ h.in }}</span> → <span class="mono bold">{{ h.out }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Copied styles from before, simplified */
.panels {
    display: flex;
    gap: 20px;
    margin-top: 20px;
    height: 70vh;
}

.panel {
    background: #222;
    border: 1px solid #333;
    padding: 20px;
    display: flex;
    flex-direction: column;
}

.left {
    flex: 2;
}

.right {
    flex: 1;
}

.code-editor {
    flex: 1;
    background: #111;
    border: 1px solid #444;
    color: #fff;
    margin: 10px 0;
    font-family: monospace;
}

.submit-btn {
    background: #008000;
    color: white;
    width: 100%;
    font-size: 1.2em;
    border: none;
    cursor: pointer;
}

.probe-box {
    display: flex;
    gap: 10px;
    margin: 15px 0;
}

.probe-box input {
    flex: 1;
    background: #000;
    color: #0f0;
    border: 1px solid #333;
}

.history-item {
    border-bottom: 1px solid #333;
    padding: 8px 0;
    font-size: 0.9em;
}

.log-item.Pass {
    color: #0f0;
}

.log-item.Fail {
    color: #f00;
}

.back-btn {
    background: #333;
    color: #fff;
    border: none;
    padding: 10px;
    cursor: pointer;
}

.mono {
    font-family: monospace;
}

.bold {
    font-weight: bold;
    color: #fff;
}
</style>