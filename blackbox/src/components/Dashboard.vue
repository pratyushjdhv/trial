<script setup>
    // Props: Data passed down from parent
    defineProps(['questions'])
    // Emits: Events sent up to parent
    defineEmits(['select'])
</script>

<template>
    <div class="dashboard">
        <h2>Select Target</h2>
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
    transition: 0.2s;
    color: #0f0;
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
</style>