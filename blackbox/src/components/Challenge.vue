<script setup>
import { ref, onMounted, watch } from 'vue' // Added 'watch'
import api from '@/api'
import Swal from 'sweetalert2'

const props = defineProps(['question', 'userId'])
const emit = defineEmits(['back'])

// --- 1. LANGUAGE & TEMPLATES ---
const language = ref('python')

const TEMPLATES = {
    python: `def solve(n):
    # Write your logic here
    return n`,
    
    c: `int solve(int n) {
    // Write your logic here
    return n;
}`
}

// Initialize code with Python template
const userCode = ref(TEMPLATES.python)

// --- 2. THE WATCHER ---
// Whenever 'language' changes, this runs automatically
watch(language, (newLang) => {
    // Optional: Only change if code is empty or matches the OTHER template 
    // (to prevent overwriting user work), but for now, we force update.
    userCode.value = TEMPLATES[newLang]
})

// --- 3. EXISTING STATE ---
const probeInput = ref('')
const probeHistory = ref([])
const probesLeft = ref(props.question.max_probes)
const submitLogs = ref([])
const submitStatus = ref('')

// --- 4. LOAD HISTORY ---
const loadProgress = async () => {
    try {
        const res = await api.post('/get_progress', {
            user_id: props.userId,
            question_id: props.question.id
        })
        probeHistory.value = res.data.history
        probesLeft.value = props.question.max_probes - res.data.probes_used
    } catch (err) {
        console.error("Could not load progress")
    }
}

onMounted(() => { loadProgress() })

// --- 5. EDITOR UTILS ---
const handleTab = (event) => {
    const textarea = event.target
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    userCode.value = userCode.value.substring(0, start) + "    " + userCode.value.substring(end)
    setTimeout(() => textarea.selectionStart = textarea.selectionEnd = start + 4, 0)
}

// --- 6. ACTIONS ---
const sendProbe = async () => {
    if (!probeInput.value) return
    try {
        const res = await api.post('/probe', {
            user_id: props.userId,
            question_id: props.question.id,
            input: probeInput.value
        })
        probeHistory.value.unshift({ in: res.data.input, out: res.data.output })
        probesLeft.value = res.data.probes_left
        probeInput.value = ''
    } catch (err) {
        Swal.fire({
            icon: 'error',
            title: 'Probe Failed',
            text: err.response?.data?.error || "Unknown Error",
            background: '#222',
            color: '#fff'
        })
    }
}

const submitCode = async () => {
    submitStatus.value = 'loading'
    submitLogs.value = []
    
    try {
        const res = await api.post('/submit', {
            user_id: props.userId,
            question_id: props.question.id,
            code: userCode.value,
            language: language.value // Don't forget to send this!
        })

        submitLogs.value = res.data.details
        
        if (res.data.solved) {
            submitStatus.value = 'success'
            Swal.fire({
                icon: 'success',
                title: 'MISSION ACCOMPLISHED',
                html: `
                    <p>You passed <b>${res.data.total_tests}/${res.data.total_tests}</b> test cases.</p>
                    <p style="font-size: 1.2em; color: #0f0">Score Added: +${res.data.score_added}</p>
                `,
                background: '#1a1a1a',
                color: '#fff',
                confirmButtonColor: '#008000'
            })
        } else {
            submitStatus.value = 'fail'
            Swal.fire({
                icon: 'warning',
                title: 'Partial Success',
                html: `
                    <p>Passed: <b>${res.data.tests_passed}/${res.data.total_tests}</b> tests.</p>
                    <p>Keep hacking. You earned partial points.</p>
                `,
                background: '#1a1a1a',
                color: '#fff',
                confirmButtonColor: '#d33'
            })
        }

    } catch (err) {
        submitStatus.value = 'error'
        Swal.fire({
            icon: 'error',
            title: 'Execution Error',
            text: err.response?.data?.error || err.message,
            background: '#222',
            color: '#fff'
        })
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
                <div style="margin-bottom: 10px;">
                    <label style="color: #fff; margin-right: 10px;">Language:</label>
                    <select v-model="language"
                        style="padding: 5px; background: #000; color: #0f0; border: 1px solid #333;">
                        <option value="python">Python</option>
                        <option value="c">C</option>
                    </select>
                </div>
                <textarea v-model="userCode" class="code-editor" spellcheck="false"
                    @keydown.tab.prevent="handleTab"></textarea>
                <button @click="submitCode" class="submit-btn">
                    {{ submitStatus === 'loading' ? 'Compiling...' : '🚀 Submit Code' }}
                </button>

                <div v-if="submitLogs.length" class="logs-box">
                    <h4>Judge Results:</h4>
                    <div v-for="(log, i) in submitLogs" :key="i" :class="['log-item', log.status]">
                        <span v-if="log.status === 'Pass'">✅ Input {{ log.input }}: Passed</span>
                        <span v-else-if="log.status === 'Fail'">❌ Input {{ log.input }}: Expected Hidden, Got "{{ log.got }}"</span>
                        <span v-else-if="log.status === 'Bonus'">✨ {{ log.msg }}</span>
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

.log-item.Bonus {
    color: #ffd700;
    font-weight: bold;
    margin-top: 5px;
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