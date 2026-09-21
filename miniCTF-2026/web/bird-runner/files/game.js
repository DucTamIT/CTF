const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const scoreText = document.getElementById("scoreText");
const stateText = document.getElementById("stateText");
const result = document.getElementById("result");
const startBtn = document.getElementById("startBtn");
const jumpBtn = document.getElementById("jumpBtn");
const submitBtn = document.getElementById("submitBtn");
const scoreboardEl = document.getElementById("scoreboard");

const M32 = 0xffffffff;
const K1 = 0x9e3779b9;
const K2 = 0x165667b1;
const K3 = 0x85ebca6b;
const K4 = 0x2545f491;
const K5 = 0x27d4eb2f;

let session = null;
let running = false;
let over = false;
let lastTime = 0;
let spawnTimer = 0;
let score = 0;
let speed = 255;
let bird;
let obstacles;

function u32(x) {
  return x >>> 0;
}

function rotl(x, n) {
  x = u32(x);
  return u32((x << n) | (x >>> (32 - n)));
}

function zx(token, value, nonce) {
  const msg = `${token}|${value}|${nonce}`;
  let a = 0x1505;
  let b = K1;
  for (let i = 0; i < msg.length; i += 1) {
    const c = msg.charCodeAt(i);
    a = rotl(u32(Math.imul(a, 33) ^ c), 13);
    b = rotl(u32(Math.imul(u32(b ^ u32(c + K2)), K3)), 25);
    a = u32(a + b);
  }
  a = u32(a ^ (a >>> 15));
  a = u32(Math.imul(a, K4));
  a = u32(a ^ (a >>> 13));
  b = u32(b ^ (b >>> 16));
  b = u32(Math.imul(b, K5));
  b = u32(b ^ (b >>> 11));
  return a.toString(16).padStart(8, "0") + b.toString(16).padStart(8, "0");
}

function resetWorld() {
  bird = { x: 132, y: 210, r: 18, vy: 0 };
  obstacles = [];
  spawnTimer = 0;
  score = 0;
  speed = 255;
  over = false;
  submitBtn.disabled = true;
  result.textContent = "";
  updateScore();
}

function updateScore() {
  scoreText.textContent = Math.floor(score).toLocaleString("en-US");
}

function jump() {
  if (!running || over) return;
  bird.vy = -390;
}

function hitRect(circle, rect) {
  const nx = Math.max(rect.x, Math.min(circle.x, rect.x + rect.w));
  const ny = Math.max(rect.y, Math.min(circle.y, rect.y + rect.h));
  const dx = circle.x - nx;
  const dy = circle.y - ny;
  return dx * dx + dy * dy < circle.r * circle.r;
}

function spawnObstacle() {
  const gap = 130 + Math.random() * 34;
  const top = 58 + Math.random() * (canvas.height - gap - 128);
  obstacles.push({
    x: canvas.width + 20,
    w: 62,
    top,
    gap,
    passed: false,
  });
}

function update(dt) {
  if (!running || over) return;
  spawnTimer -= dt;
  if (spawnTimer <= 0) {
    spawnObstacle();
    spawnTimer = 1.22;
  }

  bird.vy += 910 * dt;
  bird.y += bird.vy * dt;
  speed += dt * 3.5;
  score += dt * 14;

  for (const pipe of obstacles) {
    pipe.x -= speed * dt;
    const topRect = { x: pipe.x, y: 0, w: pipe.w, h: pipe.top };
    const bottomRect = {
      x: pipe.x,
      y: pipe.top + pipe.gap,
      w: pipe.w,
      h: canvas.height - pipe.top - pipe.gap - 44,
    };
    if (hitRect(bird, topRect) || hitRect(bird, bottomRect)) {
      endGame("Game over");
    }
    if (!pipe.passed && pipe.x + pipe.w < bird.x) {
      pipe.passed = true;
      score += 100;
    }
  }

  obstacles = obstacles.filter((pipe) => pipe.x > -90);
  if (bird.y - bird.r < 0 || bird.y + bird.r > canvas.height - 44) {
    endGame("Game over");
  }
  updateScore();
}

function drawPipe(pipe) {
  ctx.fillStyle = "#2f8f4e";
  ctx.strokeStyle = "#155d32";
  ctx.lineWidth = 3;
  ctx.fillRect(pipe.x, 0, pipe.w, pipe.top);
  ctx.strokeRect(pipe.x, 0, pipe.w, pipe.top);
  const by = pipe.top + pipe.gap;
  const bh = canvas.height - by - 44;
  ctx.fillRect(pipe.x, by, pipe.w, bh);
  ctx.strokeRect(pipe.x, by, pipe.w, bh);
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const sky = ctx.createLinearGradient(0, 0, 0, canvas.height);
  sky.addColorStop(0, "#b7e4f9");
  sky.addColorStop(1, "#e9f6fb");
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
  for (let i = 0; i < 4; i += 1) {
    const x = (i * 260 + (Date.now() / 45) % 260) % (canvas.width + 140) - 80;
    ctx.beginPath();
    ctx.ellipse(x, 74 + i * 22, 48, 16, 0, 0, Math.PI * 2);
    ctx.ellipse(x + 34, 68 + i * 22, 34, 14, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  for (const pipe of obstacles) drawPipe(pipe);

  ctx.fillStyle = "#6aa84f";
  ctx.fillRect(0, canvas.height - 44, canvas.width, 44);
  ctx.fillStyle = "#4d7f38";
  ctx.fillRect(0, canvas.height - 44, canvas.width, 5);

  ctx.save();
  ctx.translate(bird.x, bird.y);
  ctx.rotate(Math.max(-0.35, Math.min(0.65, bird.vy / 620)));
  ctx.fillStyle = "#f4b400";
  ctx.beginPath();
  ctx.ellipse(0, 0, 23, 17, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#f26f21";
  ctx.beginPath();
  ctx.moveTo(18, -4);
  ctx.lineTo(38, 2);
  ctx.lineTo(18, 9);
  ctx.closePath();
  ctx.fill();
  ctx.fillStyle = "#ffffff";
  ctx.beginPath();
  ctx.arc(8, -7, 5, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#1f2933";
  ctx.beginPath();
  ctx.arc(10, -7, 2, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  if (!running) {
    overlay("Bird Runner");
  } else if (over) {
    overlay("Run ended");
  }
}

function overlay(text) {
  ctx.fillStyle = "rgba(255, 255, 255, 0.72)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#17202a";
  ctx.font = "700 34px system-ui";
  ctx.textAlign = "center";
  ctx.fillText(text, canvas.width / 2, canvas.height / 2 - 8);
}

function frame(ts) {
  const dt = Math.min(0.033, (ts - lastTime) / 1000 || 0);
  lastTime = ts;
  update(dt);
  draw();
  requestAnimationFrame(frame);
}

async function startGame() {
  resetWorld();
  stateText.textContent = "Starting session";
  const res = await fetch("/api/game/start", { method: "POST" });
  const data = await res.json();
  if (!data.ok) {
    stateText.textContent = "Session error";
    result.textContent = data.error || "Could not start session";
    return;
  }
  session = data;
  running = true;
  over = false;
  stateText.textContent = "Running";
}

function endGame(message) {
  if (over) return;
  over = true;
  running = false;
  stateText.textContent = message;
  submitBtn.disabled = !session;
}

async function submitScore() {
  if (!session) return;
  const finalScore = Math.max(0, Math.floor(score));
  submitBtn.disabled = true;
  const checksum = zx(session.token, finalScore, session.nonce);
  const res = await fetch("/api/game/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: session.session_id,
      score: finalScore,
      checksum,
    }),
  });
  const data = await res.json();
  result.textContent = JSON.stringify(data, null, 2);
  session = null;
  await loadScoreboard();
}

async function loadScoreboard() {
  const res = await fetch("/api/scoreboard");
  const data = await res.json();
  scoreboardEl.innerHTML = "";
  for (const entry of data.top || []) {
    const li = document.createElement("li");
    li.textContent = `${entry.score.toLocaleString("en-US")}  ${entry.tag}`;
    scoreboardEl.appendChild(li);
  }
}

startBtn.addEventListener("click", startGame);
jumpBtn.addEventListener("click", jump);
submitBtn.addEventListener("click", submitScore);
canvas.addEventListener("pointerdown", jump);
window.addEventListener("keydown", (event) => {
  if (event.code === "Space" || event.code === "ArrowUp" || event.code === "KeyW") {
    event.preventDefault();
    if (!running && !over) startGame();
    else jump();
  }
});

resetWorld();
draw();
loadScoreboard();
requestAnimationFrame(frame);
