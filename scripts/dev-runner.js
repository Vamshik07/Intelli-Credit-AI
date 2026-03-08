const { spawn } = require("child_process");
const net = require("net");
const path = require("path");

const root = process.cwd();
const isWindows = process.platform === "win32";
let shuttingDown = false;

const pythonPath = isWindows
  ? path.join(root, ".venv", "Scripts", "python.exe")
  : path.join(root, ".venv", "bin", "python");

const npmCommand = "npm";

function getFreePort(preferredPort) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.unref();
    server.on("error", () => resolve(null));
    server.listen(preferredPort, "127.0.0.1", () => {
      const { port } = server.address();
      server.close(() => resolve(port));
    });
  });
}

async function pickBackendPort() {
  const preferred = await getFreePort(8000);
  if (preferred) {
    return preferred;
  }

  const fallback = await getFreePort(0);
  return fallback || 8000;
}

async function start() {
  const backendPort = await pickBackendPort();
  const backendUrl = `http://127.0.0.1:${backendPort}`;

  console.log(`Using backend URL: ${backendUrl}`);

  const backend = spawn(
    pythonPath,
    [
      "-m",
      "uvicorn",
      "backend.main:app",
      "--reload",
      "--host",
      "127.0.0.1",
      "--port",
      String(backendPort),
    ],
    { stdio: "inherit", cwd: root }
  );

  const frontend = spawn(
    npmCommand,
    ["run", "dev", "--", "--host", "127.0.0.1", "--port", "3000"],
    {
      shell: isWindows,
      stdio: "inherit",
      cwd: path.join(root, "frontend"),
      env: {
        ...process.env,
        BROWSER: "none",
        VITE_API_BASE_URL: backendUrl,
      },
    }
  );

  function shutdown(signal) {
    shuttingDown = true;

    if (!backend.killed) {
      backend.kill(signal);
    }
    if (!frontend.killed) {
      frontend.kill(signal);
    }
  }

  process.on("SIGINT", () => shutdown("SIGINT"));
  process.on("SIGTERM", () => shutdown("SIGTERM"));

  function handleChildExit(name, code, signal) {
    if (shuttingDown) {
      process.exit(0);
      return;
    }

    if (code === 0) {
      process.exit(0);
      return;
    }

    const reason = code !== null ? `code ${code}` : `signal ${signal}`;
    console.error(`${name} exited with ${reason}`);
    shutdown("SIGTERM");
    process.exit(code ?? 1);
  }

  backend.on("error", (err) => {
    console.error(`Failed to start backend: ${err.message}`);
    shutdown("SIGTERM");
    process.exit(1);
  });

  frontend.on("error", (err) => {
    console.error(`Failed to start frontend: ${err.message}`);
    shutdown("SIGTERM");
    process.exit(1);
  });

  backend.on("exit", (code, signal) => {
    handleChildExit("Backend", code, signal);
  });

  frontend.on("exit", (code, signal) => {
    handleChildExit("Frontend", code, signal);
  });
}

start().catch((err) => {
  console.error(`Failed to initialize dev runner: ${err.message}`);
  process.exit(1);
});
