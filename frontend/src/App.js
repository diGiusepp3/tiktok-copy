import React, { useState } from "react";
import "./App.css";
import VideoFeed from "./components/VideoFeed";
import BottomNav from "./components/BottomNav";
import Profile from "./components/Profile";

function App() {
  const [activeTab, setActiveTab] = useState('foryou');

  return (
    <div className="App">
      {activeTab === 'profile' ? (
        <Profile onBack={() => setActiveTab('foryou')} />
      ) : activeTab === 'following' ? (
        <div className="coming-soon">
          <h2>Following Feed</h2>
          <p>Coming Soon!</p>
          <button onClick={() => setActiveTab('foryou')} className="back-btn">
            Back to For You
          </button>
        </div>
      ) : activeTab === 'inbox' ? (
        <div className="coming-soon">
          <h2>Inbox</h2>
          <p>Coming Soon!</p>
          <button onClick={() => setActiveTab('foryou')} className="back-btn">
            Back to For You
          </button>
        </div>
      ) : (
        <VideoFeed />
      )}
      
      <BottomNav activeTab={activeTab} setActiveTab={setActiveTab} />
    </div>
  );
}

export default App;
