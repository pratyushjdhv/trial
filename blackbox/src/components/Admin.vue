<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import api from '@/api'

const leaderboard = ref([])
const top3 = ref([])
const eventEnded = ref(false)
const canvasRef = ref(null)

// --- GRID EFFECT ---
onMounted(() => {
    const canvas = canvasRef.value
    if (!canvas) return
    const ctx = canvas.getContext("2d");

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    let mouse = { x: -9999, y: -9999 };
    const squareSize = 80;
    const grid = [];

    function initGrid() {
      grid.length = 0;
      for (let x = 0; x < width; x += squareSize) {
        for (let y = 0; y < height; y += squareSize) {
          grid.push({
            x,
            y,
            alpha: 0,
            fading: false,
            lastTouched: 0,
          });
        }
      }
    }

    function getCellAt(x, y) {
      return grid.find(cell =>
        x >= cell.x && x < cell.x + squareSize &&
        y >= cell.y && y < cell.y + squareSize
      );
    }

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      initGrid();
    };

    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;

      const cell = getCellAt(mouse.x, mouse.y);
      if (cell && cell.alpha === 0) {
        cell.alpha = 1;
        cell.lastTouched = Date.now();
        cell.fading = false;
      }
    };

    window.addEventListener("resize", handleResize);
    window.addEventListener("mousemove", handleMouseMove);

    let animationFrameId;

    function drawGrid() {
      ctx.clearRect(0, 0, width, height);
      const now = Date.now();

      for (let i = 0; i < grid.length; i++) {
        const cell = grid[i];

        // Start fading after 500ms
        if (cell.alpha > 0 && !cell.fading && now - cell.lastTouched > 500) {
          cell.fading = true;
        }

        if (cell.fading) {
          cell.alpha -= 0.02;
          if (cell.alpha <= 0) {
            cell.alpha = 0;
            cell.fading = false;
          }
        }

        if (cell.alpha > 0) {
          const centerX = cell.x + squareSize / 2;
          const centerY = cell.y + squareSize / 2;

          const gradient = ctx.createRadialGradient(
            centerX, centerY, 5,
            centerX, centerY, squareSize
          );
          gradient.addColorStop(0, `rgba(0, 255, 204, ${cell.alpha})`);
          gradient.addColorStop(1, `rgba(0, 255, 204, 0)`);

          ctx.strokeStyle = gradient;
          ctx.lineWidth = 1.3;
          ctx.strokeRect(cell.x + 0.5, cell.y + 0.5, squareSize - 1, squareSize - 1);
        }
      }

      animationFrameId = requestAnimationFrame(drawGrid);
    }

    initGrid();
    drawGrid();

    onUnmounted(() => {
        window.removeEventListener("resize", handleResize);
        window.removeEventListener("mousemove", handleMouseMove);
        cancelAnimationFrame(animationFrameId);
    })
})

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

const startNewEvent = async () => {
    if (!confirm("Are you sure? This will clear all user data and start a new event.")) return
    
    try {
        await api.post('/admin/reset_event')
        eventEnded.value = false
        leaderboard.value = []
        top3.value = []
        alert("New event started!")
    } catch (err) {
        alert("Error starting new event: " + (err.response?.data?.error || err.message))
    }
}
</script>

<template>
    <div>
        <canvas ref="canvasRef" class="grid-canvas"></canvas>
        <div class="admin-panel">
            <h2>Admin Control</h2>
            
            <div v-if="!eventEnded">
                <button @click="endEvent" class="danger-btn">END EVENT</button>
            </div>

            <div v-else class="results">
                <div class="actions">
                    <button @click="startNewEvent" class="primary-btn">START NEW EVENT</button>
                </div>

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
    </div>
</template>

<style scoped>
.grid-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    background: #000;
}

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

.primary-btn {
    background: #0f0;
    color: #000;
    padding: 15px 30px;
    font-size: 1.2em;
    border: none;
    cursor: pointer;
    font-weight: bold;
    margin-bottom: 20px;
}

.primary-btn:hover {
    background: #00cc00;
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
