import { useState, useEffect } from 'react'
import './App.css'

// ログの型定義
/**
 * @typedef {Object} MoodLog
 * @property {string} date
 * @property {string} mood
 * @property {string} event
 */

function getTodayString() {
  const today = new Date();
  return today.toISOString().slice(0, 10);
}

/** @returns {MoodLog[]} */
function loadLogs() {
  const logs = localStorage.getItem('moodlog-logs');
  return logs ? JSON.parse(logs) : [];
}

/** @param {MoodLog[]} logs */
function saveLogs(logs) {
  localStorage.setItem('moodlog-logs', JSON.stringify(logs));
}

function App() {
  /** @type {[string, Function]} */
  const [mood, setMood] = useState('');
  /** @type {[string, Function]} */
  const [event, setEvent] = useState('');
  /** @type {[MoodLog[], Function]} */
  const [logs, setLogs] = useState([]);
  /** @type {[MoodLog|null, Function]} */
  const [todayLog, setTodayLog] = useState(/** @type {MoodLog|null} */(null));
  const today = getTodayString();

  useEffect(() => {
    const loadedLogs = loadLogs();
    setLogs(loadedLogs);
    const found = loadedLogs.find(log => log.date === today);
    setTodayLog(found || null);
  }, [today]);

  const handleSave = () => {
    if (!mood && !event) return;
    const newLog = { date: today, mood, event };
    const updatedLogs = logs.filter(log => log.date !== today).concat(newLog);
    setLogs(updatedLogs);
    setTodayLog(newLog);
    saveLogs(updatedLogs);
  };

  return (
    <div className="moodlog-container">
      <h1>ムードログ</h1>
      <p>今日は {today} です</p>
      {todayLog ? (
        <div className="today-log">
          <h2>本日の記録</h2>
          <p>気分: {todayLog && todayLog.mood ? todayLog.mood : '（未記入）'}</p>
          <p>出来事: {todayLog && todayLog.event ? todayLog.event : '（未記入）'}</p>
          <p>※本日の記録は1回のみ保存できます</p>
        </div>
      ) : (
        <div className="log-form">
          <h2>本日の気分・出来事を記録</h2>
          <div>
            <label>気分：</label>
            <input
              type="text"
              value={mood}
              onChange={e => setMood(e.target.value)}
              placeholder="例：嬉しい、普通、悲しい..."
            />
          </div>
          <div>
            <label>出来事：</label>
            <textarea
              value={event}
              onChange={e => setEvent(e.target.value)}
              placeholder="今日あったことを自由に書いてください"
            />
          </div>
          <button onClick={handleSave}>記録する</button>
        </div>
      )}
      <hr />
      <div className="logs-list">
        <h2>過去のログ</h2>
        {logs.length === 0 ? (
          <p>まだ記録がありません</p>
        ) : (
          <ul>
            {logs
              .filter(log => log.date !== today)
              .sort((a, b) => b.date.localeCompare(a.date))
              .map(log => (
                <li key={log.date}>
                  <strong>{log.date}</strong>：気分「{log.mood || '（未記入）'}」／出来事「{log.event || '（未記入）'}」
                </li>
              ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default App
