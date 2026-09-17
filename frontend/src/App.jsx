import React, { useMemo, useState } from "react";
import {
  ArrowUp,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Hotel,
  Loader2,
  MessageCircle,
  Minus,
  Plus,
  RotateCcw,
  Send,
  Sparkles,
  Users,
  Wifi,
  X
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const suggestions = [
  "What time is check-in?",
  "Does the hotel have a swimming pool?",
  "Is breakfast included?",
  "Which room is suitable for 3 guests?"
];

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(value);
}

function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`message-row ${isUser ? "user-row" : "assistant-row"}`}>
      {!isUser && (
        <div className="avatar assistant-avatar">
          <Sparkles size={16} />
        </div>
      )}
      <div className={`message-bubble ${isUser ? "user-bubble" : "assistant-bubble"}`}>
        <div className="message-text">{message.content}</div>
        {message.source && !isUser && (
          <div className="source-label">
            {message.source === "gemini" ? "AI assistant" : "Hotel information"}
          </div>
        )}
      </div>
      {isUser && <div className="avatar user-avatar">You</div>}
    </div>
  );
}

function AvailabilityCard({ result }) {
  return (
    <div className="availability-result">
      <div className="result-heading">
        <div>
          <span className="eyebrow">Availability</span>
          <h3>{result.available ? "Rooms available" : "No rooms available"}</h3>
        </div>
        <CheckCircle2 className={result.available ? "success-icon" : "muted-icon"} size={24} />
      </div>

      <div className="stay-summary">
        <div>
          <span>Check-in</span>
          <strong>{result.check_in}</strong>
        </div>
        <div>
          <span>Check-out</span>
          <strong>{result.check_out}</strong>
        </div>
        <div>
          <span>Guests</span>
          <strong>{result.adults} adults</strong>
        </div>
      </div>

      {result.rooms?.length > 0 && (
        <div className="room-results">
          {result.rooms.map((room) => (
            <div className="room-card" key={room.room_id}>
              <div>
                <h4>{room.room_name}</h4>
                <p>Up to {room.max_guests} guests</p>
                <span>{formatCurrency(room.price_per_night)} / night</span>
              </div>
              <div className="room-total">
                <strong>{formatCurrency(room.total_price)}</strong>
                <small>{room.nights} nights</small>
              </div>
            </div>
          ))}
        </div>
      )}

      {!result.available && (
        <p className="empty-result">
          No suitable rooms were found for the requested number of guests.
        </p>
      )}
    </div>
  );
}

function AvailabilityPanel({ onClose, onResult }) {
  const [checkIn, setCheckIn] = useState("");
  const [checkOut, setCheckOut] = useState("");
  const [adults, setAdults] = useState(2);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError("");

    if (!checkIn || !checkOut) {
      setError("Please select both check-in and check-out dates.");
      return;
    }

    if (checkOut <= checkIn) {
      setError("Check-out must be after check-in.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/availability`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          check_in: checkIn,
          check_out: checkOut,
          adults
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to check availability.");
      }

      onResult(data);
      onClose();
    } catch (err) {
      setError(
        err.message?.includes("Failed to fetch")
          ? "Unable to reach the hotel server. Make sure the FastAPI backend is running."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel-overlay" onMouseDown={onClose}>
      <div className="availability-panel" onMouseDown={(e) => e.stopPropagation()}>
        <div className="panel-header">
          <div>
            <span className="eyebrow">Stay details</span>
            <h2>Check room availability</h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={submit}>
          <label>
            <span>Check-in</span>
            <div className="input-with-icon">
              <CalendarDays size={18} />
              <input
                type="date"
                value={checkIn}
                min={new Date().toISOString().split("T")[0]}
                onChange={(e) => setCheckIn(e.target.value)}
              />
            </div>
          </label>

          <label>
            <span>Check-out</span>
            <div className="input-with-icon">
              <CalendarDays size={18} />
              <input
                type="date"
                value={checkOut}
                min={checkIn || new Date().toISOString().split("T")[0]}
                onChange={(e) => setCheckOut(e.target.value)}
              />
            </div>
          </label>

          <div className="guest-control">
            <div>
              <span>Adults</span>
              <small>How many adults?</small>
            </div>
            <div className="counter">
              <button
                type="button"
                onClick={() => setAdults((n) => Math.max(1, n - 1))}
                aria-label="Decrease adults"
              >
                <Minus size={16} />
              </button>
              <strong>{adults}</strong>
              <button
                type="button"
                onClick={() => setAdults((n) => Math.min(10, n + 1))}
                aria-label="Increase adults"
              >
                <Plus size={16} />
              </button>
            </div>
          </div>

          {error && <div className="form-error">{error}</div>}

          <button className="primary-button full-width" disabled={loading}>
            {loading ? <Loader2 className="spin" size={18} /> : <SearchIcon />}
            {loading ? "Checking..." : "Check availability"}
          </button>
        </form>
      </div>
    </div>
  );
}

function SearchIcon() {
  return <CalendarDays size={18} />;
}

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      content:
        "Welcome to Grand Horizon Hotel. I’m your AI guest assistant. I can help with rooms, amenities, policies, and availability.",
      source: "gemini"
    }
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showAvailability, setShowAvailability] = useState(false);
  const [availability, setAvailability] = useState(null);

  const conversation = useMemo(
    () =>
      messages.map((m) => ({
        role: m.role,
        content: m.content
      })),
    [messages]
  );

  async function sendMessage(text = input) {
  const message = text.trim();
  if (!message || loading) return;

  setError("");
  setInput("");

  // Clear previous availability results when starting a new question
  setAvailability(null);

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: message
    };

    setMessages((current) => [...current, userMessage]);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          conversation
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "The assistant could not respond.");
      }

      setMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "assistant",
          content: data.message,
          source: data.source
        }
      ]);

      if (data.needs_availability) {
        setShowAvailability(true);
      }
    } catch (err) {
      setError(
        err.message?.includes("Failed to fetch")
          ? "I can't reach the hotel assistant right now. Please make sure the backend is running."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  function handleAvailabilityResult(result) {
    setAvailability(result);
    const summary = result.available
      ? `I found ${result.rooms.length} suitable room option${result.rooms.length === 1 ? "" : "s"} for your stay.`
      : "I couldn't find a suitable room for the requested number of guests.";

    setMessages((current) => [
      ...current,
      {
        id: Date.now(),
        role: "assistant",
        content: summary,
        source: "availability"
      }
    ]);
  }

  function resetChat() {
    setMessages([
      {
        id: Date.now(),
        role: "assistant",
        content:
          "Welcome to Grand Horizon Hotel. I’m your AI guest assistant. How can I help with your stay?",
        source: "gemini"
      }
    ]);
    setAvailability(null);
    setError("");
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <Hotel size={22} />
          </div>
          <div>
            <strong>Grand Horizon</strong>
            <span>Hotel & Guest Assistant</span>
          </div>
        </div>

        <div className="top-actions">
          <div className="status">
            <span className="status-dot" />
            Assistant online
          </div>
          <button className="reset-button" onClick={resetChat} title="Start a new conversation">
            <RotateCcw size={17} />
            <span>New chat</span>
          </button>
        </div>
      </header>

      <main className="main-content">
        <section className="hero">
          <div className="hero-copy">
            <span className="eyebrow">Guest services</span>
            <h1>Your stay, made simpler.</h1>
            <p>
              Ask about the hotel or check room availability. The assistant uses
              the hotel's verified information to answer your questions.
            </p>
          </div>

          <div className="quick-actions">
            <button onClick={() => setShowAvailability(true)} className="availability-button">
              <CalendarDays size={18} />
              Check availability
              <ArrowUp size={15} className="rotate-45" />
            </button>
          </div>
        </section>

        <section className="workspace">
          <div className="chat-card">
            <div className="chat-header">
              <div className="chat-title">
                <div className="avatar assistant-avatar large">
                  <Sparkles size={18} />
                </div>
                <div>
                  <strong>Hotel Assistant</strong>
                  <span>Typically replies instantly</span>
                </div>
              </div>
              <div className="chat-header-icons">
                <button className="icon-button" title="Help">
                  <CircleHelp size={19} />
                </button>
              </div>
            </div>

            <div className="messages">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}

              {loading && (
                <div className="message-row assistant-row">
                  <div className="avatar assistant-avatar">
                    <Sparkles size={16} />
                  </div>
                  <div className="message-bubble assistant-bubble typing">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              )}

              {availability && <AvailabilityCard result={availability} />}
            </div>

            <div className="composer-area">
              {error && (
                <div className="api-error">
                  <span>{error}</span>
                  <button onClick={() => setError("")} aria-label="Dismiss error">
                    <X size={15} />
                  </button>
                </div>
              )}

              <div className="suggestion-row">
                {suggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    className="suggestion"
                    onClick={() => sendMessage(suggestion)}
                    disabled={loading}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>

              <form
                className="composer"
                onSubmit={(e) => {
                  e.preventDefault();
                  sendMessage();
                }}
              >
                <MessageCircle size={19} />
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask anything about your stay..."
                  disabled={loading}
                />
                <button type="submit" className="send-button" disabled={!input.trim() || loading}>
                  {loading ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
                </button>
              </form>
              <p className="privacy-note">
                <Wifi size={12} /> Responses are based on the hotel's available information.
              </p>
            </div>
          </div>

          <aside className="info-card">
            <div className="info-icon"><Users size={20} /></div>
            <h3>Need a room?</h3>
            <p>
              Tell us your dates and party size and we'll check the available
              room options for you.
            </p>
            <button onClick={() => setShowAvailability(true)} className="secondary-button">
              Check rooms
            </button>

            <div className="info-divider" />

            <div className="help-row">
              <div className="mini-icon"><Sparkles size={15} /></div>
              <div>
                <strong>AI-powered assistance</strong>
                <span>Hotel information is grounded in our knowledge base.</span>
              </div>
            </div>
          </aside>
        </section>
      </main>

      <footer>
        <span>Grand Horizon Hotel</span>
        <span>•</span>
        <span>Guest Assistant</span>
      </footer>

      {showAvailability && (
        <AvailabilityPanel
          onClose={() => setShowAvailability(false)}
          onResult={handleAvailabilityResult}
        />
      )}
    </div>
  );
}
