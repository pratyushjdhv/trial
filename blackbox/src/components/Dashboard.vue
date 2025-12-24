<script setup>
    import { onMounted, onUnmounted } from 'vue';
    defineProps(['questions'])
    defineEmits(['select'])

    const updateCursor = (e) => {
        const cards = document.querySelectorAll('.level-card');
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty('--x', `${x}px`);
            card.style.setProperty('--y', `${y}px`);
        });
    }

    onMounted(() => window.addEventListener('pointermove', updateCursor));
    onUnmounted(() => window.removeEventListener('pointermove', updateCursor));
</script>

<template>
    <div class="dashboard">
        <h2>
            <img src="/target.svg" alt="" class="target-icon">
            Select Target</h2>
        <div class="grid">
            <div v-for="q in questions" :key="q.id" class="card level-card" @click="$emit('select', q)">
                <div class="badge">{{ q.difficulty }}</div>
                <h3>Level {{ q.id }}</h3>
                <p>{{ q.base_points }} Points</p>
            </div>
        </div>
    </div>
</template>

<style scoped>
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
}

.level-card {
    background: #222;
    border: 1px solid #444;
    padding: 20px;
    cursor: pointer;
    transition: border-color 0.2s;
    color: #0f0;
    position: relative;
    overflow: hidden;
}

.level-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(800px circle at var(--x) var(--y), rgba(0, 255, 0, 0.15), transparent 40%);
    opacity: 0;
    transition: opacity 0.5s;
    pointer-events: none;
    z-index: 1;
}

.level-card:hover::before {
    opacity: 1;
}

.level-card > * {
    position: relative;
    z-index: 2;
}

.level-card:hover {
    border-color: #0f0;
    background: #2a2a2a;
}

.badge {
    background: #444;
    color: #fff;
    padding: 2px 8px;
    font-size: 0.8em;
    display: inline-block;
    margin-bottom: 10px;
}

.target-icon {
    height: 1.5em;
    vertical-align: middle;
}
</style>