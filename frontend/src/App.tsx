import React, {useState, useEffect} from 'react';
// import logo from './logo.svg';
import './App.css';

const API_BASE = process.env.REACT_APP_API_BASE || "";

function MealEditor(props: {editing: boolean, onSave?: any, onDiscard?: any, onEdit?: any}) {
  const onSave = props.onSave || (() => {});
  const onDiscard = props.onDiscard || (() => {});
  const onEdit = props.onEdit || (() => {});
  if (props.editing) {
    return <>
      <button onClick={() => onSave()}>✓</button>
      <button onClick={() => onDiscard()}>✗</button>
    </>;
  } else {
    return <button onClick={() => onEdit()}>edit</button>;
  }
}

function Meal(props: {date: string, data: {source: any, meal: any}, sources: any, onUpdate: any}) {
  const today = (new Date()).toISOString().split("T")[0];
  const tomorrow = new Date((new Date().setDate(new Date().getDate() + 1))).toISOString().split("T")[0];
  const data = props.data;
  const [editing, setEditing] = useState(false);
  const [localData, setLocalData] = useState({source: data.source?.id, meal: data.meal});
  function onEdit() {
    setEditing(true);
  }
  function onDiscard() {
    setEditing(false);
    setLocalData({source: data?.source?.id, meal: data?.meal});
  }
  function onSave() {
    setEditing(false);
    props.onUpdate(localData);
  }
  function onKeyPress(event: any) {
    if (event.isComposing || event.keyCode === 229) {
      return;
    }
    if (event.key === "Enter") {
      onSave();
    }
  }
  const theDay = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][(new Date(props.date)).getDay()];
  const theDate = props.date === today ? <strong>Today, {theDay}:</strong> : props.date === tomorrow ? <>Tomorrow, {theDay}:</> : <>{props.date}, {theDay}:</>;
  function onUpdateSource(event: any) {
    setLocalData(prevData => ({...prevData, source: event.target.value}));
  }
  function onUpdateMeal(event: any) {
    setLocalData(prevData => ({...prevData, meal: event.target.value}));
  }
  if (editing) {
    return <tr><td className="align-right no-wrap">{theDate}</td><td><select value={localData.source || 0} onChange={onUpdateSource}><option key={0} value={0}>nobody</option>{props.sources.map((s: any) => <option key={s.id} value={s.id}>{s.name}</option>)}</select> <input type="text" value={localData.meal || ""} size={10} placeholder='"Food"' onChange={onUpdateMeal} onKeyPress={onKeyPress} /> <MealEditor editing={editing} onEdit={onEdit} onSave={onSave} onDiscard={onDiscard} /></td></tr>;
  } else {
    let theProvider = data?.source ? data.source.name : "nobody";
    if (props.date === today) {
      theProvider = <strong>{theProvider}</strong>;
    }
    return <tr><td className="align-right no-wrap">{theDate}</td><td>{theProvider} {data?.meal ? `(${data.meal})` : null} <MealEditor editing={editing} onEdit={onEdit} onSave={onSave} onDiscard={onDiscard} /></td></tr>
  }
}

function App() {
  const [data, setData] = useState<{[_: string]: {source: any, meal: any}}>();
  useEffect(() => {
    fetch(API_BASE + "/api/upcoming").then(response => response.json()).then(data => {console.log("data:", data); setData(data)});
  }, []);
  const [sources, setSources] = useState(null);
  useEffect(() => {
    fetch(API_BASE + "/api/p").then(response => response.json()).then(data => setSources(data));
  }, []);
  const now = new Date();
  return (
    <div className="App">
      <header className="App-header">
        {/* <img src={logo} className="App-logo" alt="logo" /> */}
        <h1>whomst food</h1>
      </header>
      <main>
        {data == null ? "Loading..." : <><table><tbody>
          {[...Array(7)].map((_, i) => {
            const theDate = new Date((new Date().setDate(now.getDate() + i))).toISOString().split("T")[0];
            return <Meal
              date={theDate}
              key={theDate}
              data={data[theDate] || {meal: undefined, source: undefined}}
              sources={sources}
              onUpdate={(data: any) => {
                fetch(API_BASE + "/api/d/" + theDate, {
                  method: "POST",
                  body: new URLSearchParams({
                    meal: data.meal || "",
                    source_id: data.source || "",
                  })
                }).then(response => response.json()).then(data => setData(prevData => ({
                  ...(prevData || {}), [theDate]: data,
                })))
              }}
            />;
          })}
        </tbody></table></>
        }
      </main>
    </div>
  );
}

export default App;
