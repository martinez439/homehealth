import { useMemo, useState } from 'react';

const addDays = (date, days) => { const next = new Date(date); next.setDate(next.getDate() + days); return next; };
const startOfWeek = (date) => { const next = new Date(date); const day = (next.getDay() + 6) % 7; next.setDate(next.getDate() - day); next.setHours(0, 0, 0, 0); return next; };
const sameDay = (a, b) => a.toDateString() === b.toDateString();
const fmtTime = (start, end) => `${start.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}${end ? `–${end.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}` : ''}`;

function buildEvent(raw) {
  return {
    id: raw.id,
    title: raw.title,
    start: new Date(raw.start),
    end: raw.end ? new Date(raw.end) : new Date(raw.start),
    extendedProps: raw.extendedProps || {},
  };
}

export default function FullCalendar({ events = [], eventClick, eventDrop, eventResize, eventContent, initialView = 'timeGridWeek' }) {
  const [view, setView] = useState(initialView);
  const [anchor, setAnchor] = useState(new Date());
  const parsed = useMemo(() => events.map(buildEvent), [events]);
  const days = useMemo(() => {
    if (view === 'timeGridDay') return [new Date(anchor)];
    const start = view === 'dayGridMonth' ? new Date(anchor.getFullYear(), anchor.getMonth(), 1) : startOfWeek(anchor);
    const count = view === 'dayGridMonth' ? new Date(anchor.getFullYear(), anchor.getMonth() + 1, 0).getDate() : 7;
    return Array.from({ length: count }, (_, i) => addDays(start, i));
  }, [anchor, view]);

  const move = (daysDelta) => setAnchor((current) => view === 'dayGridMonth' ? new Date(current.getFullYear(), current.getMonth() + daysDelta, 1) : addDays(current, daysDelta * (view === 'timeGridDay' ? 1 : 7)));
  const handleDrop = (dropDay, e) => {
    if (!eventDrop) return;
    const id = e.dataTransfer.getData('text/plain');
    const found = parsed.find((event) => event.id === id);
    if (!found) return;
    const oldStart = new Date(found.start);
    const oldEnd = new Date(found.end);
    const nextStart = new Date(dropDay);
    nextStart.setHours(oldStart.getHours(), oldStart.getMinutes(), 0, 0);
    const nextEnd = new Date(dropDay);
    nextEnd.setHours(oldEnd.getHours(), oldEnd.getMinutes(), 0, 0);
    eventDrop({ event: { ...found, start: nextStart, end: nextEnd }, revert: () => {} });
  };

  return <div className="fc-lite">
    <div className="fc fc-toolbar fc-header-toolbar">
      <div className="fc-toolbar-chunk"><button className="fc-button-primary" onClick={() => move(-1)}>prev</button><button className="fc-button-primary" onClick={() => setAnchor(new Date())}>today</button><button className="fc-button-primary" onClick={() => move(1)}>next</button></div>
      <div className="fc-toolbar-chunk"><h2 className="fc-toolbar-title">{anchor.toLocaleDateString([], { month: 'long', year: 'numeric' })}</h2></div>
      <div className="fc-toolbar-chunk"><button className="fc-button-primary" onClick={() => setView('dayGridMonth')}>month</button><button className="fc-button-primary" onClick={() => setView('timeGridWeek')}>week</button><button className="fc-button-primary" onClick={() => setView('timeGridDay')}>day</button></div>
    </div>
    <div className={`fc-lite-grid ${view === 'dayGridMonth' ? 'month' : ''}`}>
      {days.map((day) => <div className="fc-lite-day" key={day.toISOString()} onDragOver={(e) => e.preventDefault()} onDrop={(e) => handleDrop(day, e)}>
        <div className="fc-lite-day-head">{day.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' })}</div>
        <div className="fc-lite-events">
          {parsed.filter((event) => sameDay(event.start, day)).map((event) => <button key={event.id} draggable className={`fc-lite-event ${(events.find((e) => e.id === event.id)?.classNames || []).join(' ')}`} style={{ background: events.find((e) => e.id === event.id)?.backgroundColor, borderColor: events.find((e) => e.id === event.id)?.borderColor }} onDragStart={(e) => e.dataTransfer.setData('text/plain', event.id)} onClick={() => eventClick?.({ event })}>
            {eventContent ? eventContent({ event, timeText: fmtTime(event.start, event.end) }) : <span>{fmtTime(event.start, event.end)} {event.title}</span>}
            {eventResize && <span className="fc-lite-resize" title="Resize duration in the edit form">↕</span>}
          </button>)}
        </div>
      </div>)}
    </div>
  </div>;
}
