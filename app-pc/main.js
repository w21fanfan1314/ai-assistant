const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let serverProcess = null;

function startServer() {
  // 获取 server.exe 的路径
  let serverPath;
  if (app.isPackaged) {
    // 打包后的路径
    serverPath = path.join(path.join(process.resourcesPath, 'app'), 'server.exe');
  } else {
    // 开发环境路径
    serverPath = path.join(app.getAppPath(), 'server.exe');
  }
  
  console.log('Server path:', serverPath);
  
  // 启动 server.exe
  serverProcess = spawn(serverPath, [], {
    windowsHide: true // 隐藏命令行窗口
  });

  // 监听服务器输出（可选）
  serverProcess.stdout.on('data', (data) => {
    console.log(`Server output: ${data}`);
  });

  serverProcess.stderr.on('data', (data) => {
    console.error(`Server error: ${data}`);
  });

  // 监听服务器退出
  serverProcess.on('close', (code) => {
    console.log(`Server process exited with code ${code}`);
    serverProcess = null;
  });
}

function stopServer() {
  if (serverProcess) {
    // Windows 上使用 taskkill 确保进程及其子进程都被终止
    if (process.platform === 'win32') {
      spawn('taskkill', ['/F', '/T', '/PID', serverProcess.pid]);
    } else {
      serverProcess.kill('SIGTERM');
    }
    serverProcess = null;
  }
}

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false,
      allowRunningInsecureContent: true
    }
  });

  mainWindow.loadFile('index.html');

  // 当窗口关闭时，不要立即关闭服务器
  mainWindow.on('closed', () => {
    // 如果没有其他窗口打开，才关闭服务器
    if (BrowserWindow.getAllWindows().length === 0) {
      stopServer();
    }
  });
}

app.whenReady().then(() => {
  // 启动服务器
  startServer();

  // 等待一小段时间确保服务器启动
  setTimeout(() => {
    createWindow();
  }, 1000);

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// 当所有窗口关闭时退出应用
app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    stopServer();
    app.quit();
  }
});

// 当应用退出前确保服务器被关闭
app.on('before-quit', () => {
  stopServer();
});

// 处理安全警告
app.commandLine.appendSwitch('ignore-certificate-errors');
app.commandLine.appendSwitch('disable-features', 'OutOfBlinkCors'); 