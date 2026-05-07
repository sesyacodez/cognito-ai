"use client";

import React, { useState } from "react";

export default function SocraticTutorPanel({ isOpen, onClose, currentQuestionPrompt }:{isOpen:boolean; onClose:() => void; currentQuestionPrompt?: string}){
  const [messages, setMessages] = useState<Array<{from: 'ai'|'user'; text: string}>>([
    { from: 'ai', text: currentQuestionPrompt ? `Бачу: "${currentQuestionPrompt}" — з якого боку підійдемо до цього?` : 'Привіт! Я ваш Socratic Mentor. Розкажіть, що саме викликає складнощі.' },
  ]);
  const [input, setInput] = useState("");

  function send() {
    if (!input.trim()) return;
    setMessages((m) => [...m, { from: 'user', text: input }]);
    // simple echo placeholder reply
    setTimeout(() => {
      setMessages((m) => [...m, { from: 'ai', text: `Добре. Спробуйте розбити проблему на підзадачі. (Автовідповідь)` }]);
    }, 600);
    setInput("");
  }

  // close on Escape
  React.useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape' && isOpen) onClose();
    }
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  return (
    <div className={`fixed top-0 right-0 h-full w-full max-w-md z-50 transform bg-[#070918]/95 backdrop-blur-lg transition-transform ${isOpen ? 'translate-x-0' : 'translate-x-full'}`} aria-hidden={!isOpen}>
      <div className="flex h-full flex-col">
        <div className="flex items-center justify-between border-b border-white/6 p-4">
          <div className="text-lg font-semibold text-white">AI Mentor</div>
          <button onClick={onClose} aria-label="Close" className="text-white/70 hover:text-white">✕</button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.map((m, i) => (
            <div key={i} className={`max-w-[90%] ${m.from === 'ai' ? 'text-left' : 'text-right'} `}>
              <div className={`inline-block rounded-lg p-3 ${m.from === 'ai' ? 'bg-[#0d1730] text-white' : 'bg-[#11324d] text-white/90'}`}>
                {m.text}
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-white/6">
          <div className="flex gap-2">
            <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Напишіть повідомлення..." className="flex-1 rounded-md bg-[#061022] border border-white/6 px-3 py-2 text-white" />
            <button onClick={send} className="rounded-md bg-emerald-500 px-4 py-2 text-black font-semibold">Send</button>
          </div>
        </div>
      </div>
    </div>
  );
}
