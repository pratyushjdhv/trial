<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const emit = defineEmits(['join'])
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

watch(username, (newVal) => {
    if (newVal.trim().toLowerCase() === 'admin') {
        showPassword.value = true
    } else {
        showPassword.value = false
        password.value = ''
    }
})

const handleLogin = () => {
    if (username.value.trim()) {
        emit('join', { username: username.value, password: password.value }) 
    }
}
</script>

<template>
    <div>
        <canvas ref="canvasRef" class="grid-canvas"></canvas>
        <div class="center-box">
            <h2>Identify Yourself</h2>
            <input v-model="username" placeholder="Enter Codename" @keyup.enter="handleLogin" />
            <div v-if="showPassword">
                <br>
                <input  v-model="password" type="password" placeholder="Admin Password" @keyup.enter="handleLogin" />
                <br><br>
            </div>
            
            <button @click="handleLogin">Connect</button>
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

.center-box {
    max-width: 400px;
    background: #0F0E0E;
    margin: 100px auto;
    text-align: center;
    padding-top: 1rem;
    padding-bottom: 1rem;
    border-radius: 1.5rem;
    
}

input {
    background: #000;
    color: #0f0;
    border: 1px solid #333;
    padding: 10px;
    font-family: inherit;
    margin-right: 10px;
}

button {
    cursor: pointer;
    border: none;
    font-weight: bold;
    padding: 10px 20px;
    background: #333;
    color: white;
}

button:hover {
    background: #555;
}
</style>