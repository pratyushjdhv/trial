<script setup>
defineProps(['winners'])
defineEmits(['close'])
</script>

<template>
    <div class="modal-overlay">
        <div class="modal-content">
            <h1>🏁 EVENT ENDED 🏁</h1>
            <p>The simulation has concluded.</p>
            
            <div class="winners-list">
                <h3>🏆 TOP 5 AGENTS 🏆</h3>
                <ul>
                    <li v-for="(user, index) in winners" :key="user.id" :class="{'top-1': index === 0}">
                        <span class="rank">#{{ index + 1 }}</span>
                        <span class="name">{{ user.username }}</span>
                        <span class="score">{{ user.total_score }} pts</span>
                    </li>
                </ul>
            </div>
            <button class="dismiss-btn" @click="$emit('close')">Dismiss</button>
        </div>
    </div>
</template>

<style scoped>
.dismiss-btn {
    margin-top: 20px;
    padding: 10px 20px;
    background: #333;
    color: #fff;
    border: 1px solid #0f0;
    cursor: pointer;
    font-family: inherit;
    font-size: 1em;
    transition: all 0.3s;
}

.dismiss-btn:hover {
    background: #0f0;
    color: #000;
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: #111;
    border: 2px solid #0f0;
    padding: 40px;
    text-align: center;
    color: #0f0;
    max-width: 500px;
    width: 90%;
    box-shadow: 0 0 20px #0f0;
    animation: popIn 0.5s ease-out;
}

@keyframes popIn {
    0% { transform: scale(0.8); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}

h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    color: #ff0000;
    text-shadow: 0 0 10px #ff0000;
}

.winners-list {
    margin-top: 30px;
    text-align: left;
}

ul {
    list-style: none;
    padding: 0;
}

li {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    border-bottom: 1px solid #333;
    font-size: 1.2em;
}

li.top-1 {
    color: #ffd700;
    font-weight: bold;
    font-size: 1.4em;
    border-bottom: 2px solid #ffd700;
}

.rank {
    width: 40px;
}

.name {
    flex-grow: 1;
}
</style>
